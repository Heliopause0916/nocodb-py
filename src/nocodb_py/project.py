"""
Filename: src/nocodb_py/project.py

NocoDB Project for Python
This module provides a project class to interact with NocoDB project-specific API
"""

# pylint: disable=unused-import
# pylint: disable=too-many-instance-attributes
# pylint: disable=trailing-whitespace
# pylint: disable=too-many-public-methods
# pylint: disable=line-too-long
# pylint: disable=import-outside-toplevel

import time
import threading
import copy
from typing import Dict, List, Any, Optional, Callable
from typing import TYPE_CHECKING
import requests
from .exceptions import ListRetrievalError
from .utils import parse_metadata_datetime, count_of_nocodb_data
from .client import NocoDBClient
if TYPE_CHECKING:
    from .table import NocoDBTable

class NocoDBProject:
    """
    A class representing a NocoDB project with project-specific operations
    
    Attributes:
        _client (NocoDBClient): The NocoDB client instance
        _project_id (str): The unique project identifier
    """
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, client: NocoDBClient, project_id: str,
                 timeout: int = 30, cache_ttl: Optional[int] = 300):
        """
        Initialize the NocoDBProject with client and project ID
        
        Args:
            client (NocoDBClient): The NocoDB client instance
            project_id (str): The unique project identifier
        """
        self._client = client
        self._project_id = project_id
        self._timeout = timeout
        self._cache_ttl = cache_ttl
        # Project-specific cache
        self._project_info_cache = None
        self._project_info_timestamp = 0
        self._tables_cache = None
        self._tables_timestamp = 0
        self._last_include_m2m = None  # Track last include_m2m parameter value

        self._cache_lock = threading.RLock()

    def __str__(self) -> str:
        """
        String representation of the NocoDBProject
        
        Returns:
            str: String representation of the project
        """
        return f"NocoDBProject(id='{self._project_id}', client={self._client})"

    def __repr__(self) -> str:
        """
        Official string representation of the NocoDBProject
        
        Returns:
            str: Official representation of the project
        """
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another NocoDBProject
        
        Args:
            other (object): The other object to compare with
            
        Returns:
            bool: True if equal, False otherwise
        """
        if not isinstance(other, NocoDBProject):
            return False
        return self._project_id == other._project_id and self._client == other._client

    def __hash__(self) -> int:
        """
        Hash implementation for NocoDBProject.
        
        Returns:
            int: Hash value based on immutable attributes that define identity
        """
        return hash((self._client, self._project_id))

    def __copy__(self):
        """
        Shallow copy implementation for NocoDBProject.
        
        Returns:
            NocoDBProject: A new project instance with same configuration but fresh cache
        """
        new_project = NocoDBProject(self._client, self._project_id,
                                  self._timeout, self._cache_ttl)
        # Reset cache state
        new_project._project_info_cache = None
        new_project._project_info_timestamp = 0
        new_project._tables_cache = None
        new_project._tables_timestamp = 0
        new_project._last_include_m2m = None
        return new_project

    def __deepcopy__(self, memo):
        """
        Deep copy implementation for NocoDBProject.
        
        Args:
            memo: Memo dictionary for deepcopy
            
        Returns:
            NocoDBProject: A new project instance with same configuration but fresh cache
        """
        # For NocoDBProject, deepcopy is the same as shallow copy
        # since we don't want to copy cache state and client is shared
        return self.__copy__()

    def __getstate__(self):
        """
        Get state for pickling.
        
        Returns:
            dict: State dictionary without non-serializable objects
        """
        state = self.__dict__.copy()
        # Remove non-serializable objects
        state.pop('_cache_lock', None)
        state.pop('_project_info_cache', None)
        state.pop('_project_info_timestamp', None)
        state.pop('_tables_cache', None)
        state.pop('_tables_timestamp', None)
        state.pop('_last_include_m2m', None)
        return state

    def __setstate__(self, state):
        """
        Set state from pickling.
        
        Args:
            state: State dictionary
        """
        self.__dict__.update(state)
        # Reinitialize non-serializable objects
        self._cache_lock = threading.RLock()
        self._project_info_cache = None
        self._project_info_timestamp = 0
        self._tables_cache = None
        self._tables_timestamp = 0
        self._last_include_m2m = None

    @property
    def project_id(self) -> str:
        """
        Get the project ID
        
        Returns:
            str: The project ID
        """
        return self._project_id
    
    def get_project_id(self) -> str:
        """
        Get the project ID (compatibility method)
        
        Returns:
            str: The project ID
        """
        return self.project_id
    
    get_id = get_project_id

    @property
    def client(self) -> NocoDBClient:
        """
        Get the client instance
        
        Returns:
            NocoDBClient: The client instance
        """
        return self._client
    
    def get_client(self) -> NocoDBClient:
        """
        Get the client instance (compatibility method)
        
        Returns:
            NocoDBClient: The client instance
        """
        return self.client


    def get_full_info(self, force_refresh: bool = False) -> Dict:
        """
        Get the full information of the NocoDB instance
        
        Returns:
            Dict[str, Any]: The information of the NocoDB instance (deep copy for safety)
        """
        with self._cache_lock:
            current_time = time.time()
            cache_ttl = self._cache_ttl
            if(not force_refresh and
               self._project_info_cache is not None and
               (cache_ttl is None or current_time - self._project_info_timestamp < cache_ttl)
               ):
                return copy.deepcopy(self._project_info_cache)

            # pylint: disable=protected-access
            # Reason: NocoDBClient._get is intentionally accessible to NocoDB-related classes
            self._project_info_cache = self._client._get(
                f"{self._client.get_meta_v2_prefix()}/bases/{self._project_id}"
                )
            self._project_info_timestamp = current_time
            return copy.deepcopy(self._project_info_cache)

    def get_tables_full_info(self, force_refresh: bool = False, include_m2m: bool = False) -> Dict:
        """
        Get the full information of all tables in the project
        
        Args:
            force_refresh (bool): Whether to force refresh the cache
            include_m2m (bool): Whether to include many-to-many relationship tables
            
        Returns:
            Dict[str, Any]: The information of all tables in the project (deep copy for safety)
        """
        with self._cache_lock:
            current_time = time.time()
            cache_ttl = self._cache_ttl
            
            # Check if include_m2m parameter has changed since last cache
            include_m2m_changed = (self._last_include_m2m is not None and
                                  self._last_include_m2m != include_m2m)
            
            # Force refresh if parameter changed or explicitly requested
            effective_force_refresh = force_refresh or include_m2m_changed
            
            if(not effective_force_refresh and
              self._tables_cache is not None and
              (cache_ttl is None or current_time - self._tables_timestamp < cache_ttl)
              ):
                return copy.deepcopy(self._tables_cache)
            
            params = {
                "includeM2M": "true" if include_m2m else "false"
            }
            # pylint: disable=protected-access
            # Reason: NocoDBClient._get is intentionally accessible to NocoDB-related classes
            self._tables_cache = self._client._get(f"{self.get_meta_v2_prefix()}/tables",
                                                   params=params)
            self._tables_timestamp = current_time
            self._last_include_m2m = include_m2m  # Store the parameter value
            return copy.deepcopy(self._tables_cache)

    def list_tables(self, force_refresh: bool = False, include_m2m: bool = False,
                      full_info: bool = False, convert_time: bool = False) -> List:
        """
        List all tables in the project
        
        Args:
            force_refresh (bool): Force refresh the cache
            full_info (bool): Get full information of the tables
            convert_time (bool): Convert time fields to datetime objects
            
        Returns:
            List: Tables list (deep copy for safety)
        """
        tables_data = self.get_tables_full_info(force_refresh=force_refresh, include_m2m=include_m2m)
        tables_list: list[dict[str, Any]] = tables_data.get("list", [])

        if convert_time:
            tables_list = [
                {
                    **table,
                    'created_at': parse_metadata_datetime(table.get('created_at', None)),
                    'updated_at': parse_metadata_datetime(table.get('updated_at', None))
                }
                for table in tables_list
            ]

        if not full_info:
            tables_list = [
                {
                    "id": table.get("id", ""),
                    "title": table.get("title", ""),
                }
                for table in tables_list
                ]
        return copy.deepcopy(tables_list)

    def get_table_title(self, table_id: str, force_refresh: bool = False) -> str:
        """
        Get table title by table ID

        Args:
            table_id (str): Table ID
            force_refresh (bool): Whether to force refresh cache
            
        Returns:
            str: Table title
            
        Raises:
            ValueError: When table is not found or title is empty
        """
        tables = self.list_tables(force_refresh=force_refresh)
        if not tables:
            raise ListRetrievalError(
                "Failed to get table list",
                api_endpoint=f"/api/v2/meta/bases/{self._project_id}/tables",
                expected_format="List of table objects"
            )
            
        for table in tables:
            if table.get("id") == table_id:
                title = table.get("title")
                if title is not None:
                    return title
                raise ValueError(f"Table {table_id} has empty title")
                
        raise ValueError(f"Table with ID {table_id} not found")

    def get_title(self, force_refresh: bool = False) -> str:
        """
        Get the title of the project
        
        Args:
            force_refresh (bool): Whether to force refresh the cache
            
        Returns:
            str: The title of the project
            
        Raises:
            ValueError: When title is not found in project info
        """
        project_info = self.get_full_info(force_refresh=force_refresh)
        title = project_info.get("title")
        if title is None:
            raise ValueError("Title not found in project info")
        return title

    def get_description(self, force_refresh: bool = False) -> Optional[str]:
        """
        Get the description of the project
        
        Args:
            force_refresh (bool): Whether to force refresh the cache
            
        Returns:
            Optional[str]: The description of the project, or None if not set
        """
        project_info = self.get_full_info(force_refresh=force_refresh)
        return project_info.get("description")

    def count_tables(self, force_refresh: bool = False) -> Optional[int]:
        """
        Count the number of tables in the project
        
        Returns:
            int: The number of tables in the project
        """
        tables_data = self.get_tables_full_info(force_refresh=force_refresh)
        return count_of_nocodb_data(tables_data)

    def get_table(self, table_id: str, **kwargs) -> 'NocoDBTable':
        """
        Get a NocoDBTable object from the project by its ID
        
        Args:
            table_id (str): The ID of the table to get
            
        Returns:
            'NocoDBTable': The table object
        """
        # pylint: disable=import-outside-toplevel
        # Reason: Avoid circular imports
        from .table import NocoDBTable
        return NocoDBTable(self,
                           table_id=table_id,
                           **kwargs)

    def get_meta_v2_prefix(self) -> str:
        """
        Get the meta v2 prefix for the project
        Returns:
            str: The meta v2 prefix for the project
        """
        return f"/api/v2/meta/bases/{self._project_id}"

    def find_tables_by_title(self, title: str, match_func :Optional[Callable[[str, str], bool]] =None,
                            force_refresh: bool = False, include_m2m: bool = False) -> list:
        """
        Find list of matching table_ids by title
        
        Args:
            title (str): The title string to search for
            match_func (Callable): Matching function, accepts two string arguments and returns bool, defaults to exact match
            force_refresh (bool): Whether to force refresh the cache
            include_m2m (bool): Whether to include many-to-many relationship tables
            
        Returns:
            List[str]: List of matching table_ids
        """
        # pylint: disable=import-outside-toplevel
        from .utils import exact_match  # Avoid circular import
        
        if match_func is None:
            match_func = exact_match
        
        tables: Optional[List[Dict[str, Any]]] = self.list_tables(force_refresh=force_refresh, include_m2m=include_m2m)
        if tables is None:
            return []
        
        return [
            table["id"] for table in tables
            if match_func(title, table.get("title", ""))
        ]

    def clear_project_info_cache(self):
        """
        Clear project info cache
        """
        with self._cache_lock:
            self._project_info_cache = None
            self._project_info_timestamp = 0

    def clear_tables_cache(self):
        """
        Clear tables cache
        """
        with self._cache_lock:
            self._tables_cache = None
            self._tables_timestamp = 0
            self._last_include_m2m = None

NocoDBBase = NocoDBProject
