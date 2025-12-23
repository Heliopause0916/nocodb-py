"""
Filename: src/nocodb_py/table.py

NocoDB Table for Python
"""

# pylint: disable=unused-import
# pylint: disable=too-many-instance-attributes
# pylint: disable=trailing-whitespace
# pylint: disable=too-many-public-methods
# pylint: disable=line-too-long
# pylint: disable=import-outside-toplevel

import time
import threading
from typing import Dict, List, Any, Optional, Union
from typing import TYPE_CHECKING
import requests
from .utils import parse_utc_datetime, count_of_nocodb_data
from .client import NocoDBClient
from .project import NocoDBProject
if TYPE_CHECKING:
    from .column import NocoDBColumn

class RecordNotFoundError(Exception):
    """Exception raised when a record is not found in the table."""
    
    def __init__(self, table_id: str, record_id: int, original_error: Exception):
        self.table_id = table_id
        self.record_id = record_id
        self.original_error = original_error
        super().__init__(f"Record with ID {record_id} not found in table {table_id}")

# pylint: disable=too-many-instance-attributes
class NocoDBTable:
    """
    A class representing a NocoDB table with table-specific operations
    
    Attributes:
        _project (NocoDBProject): The NocoDB project instance
        _table_id (str): The unique table identifier
    """

    def __init__(self, project: NocoDBProject, table_id: str, xc_token: str, timeout: int = 30, cache_ttl: Optional[int] = 300):
        """
        Initialize the NocoDBTable with project and table ID
        
        Args:
            project (NocoDBProject): The NocoDB project instance
            table_id (str): The unique table identifier
            timeout (int): Request timeout in seconds
            cache_ttl (Optional[int]): Cache time-to-live in seconds
        """
        self._project = project
        self._table_id = table_id
        self._xc_token = xc_token
        self._timeout = timeout
        self._cache_ttl = cache_ttl

        # Table-specific cache
        self._table_info_cache = None
        self._table_info_timestamp = 0
        self._columns_cache = None
        self._columns_timestamp = 0
        self._cache_lock = threading.RLock()

    def __str__(self) -> str:
        """
        String representation of the NocoDBTable
        
        Returns:
            str: String representation of the table
        """
        return f"NocoDBTable(id='{self._table_id}', project={self._project})"

    def __repr__(self) -> str:
        """
        Official string representation of the NocoDBTable
        
        Returns:
            str: Official representation of the table
        """
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another NocoDBTable
        
        Args:
            other (object): The other object to compare with
            
        Returns:
            bool: True if equal, False otherwise
        """
        if not isinstance(other, NocoDBTable):
            return False
        return self._table_id == other._table_id and self._project == other._project

    def __hash__(self) -> int:
        """
        Hash implementation for NocoDBTable.
        
        Returns:
            int: Hash value based on immutable attributes that define identity
        """
        return hash((self._project, self._table_id))

    def get_table_id(self) -> str:
        """
        Get the table ID
        
        Returns:
            str: The table ID
        """
        return self._table_id
    
    get_id = get_table_id

    def get_project(self) -> NocoDBProject:
        """
        Get the project instance
        
        Returns:
            NocoDBProject: The project instance
        """
        return self._project

    def get_meta_v2_prefix(self) -> str:
        """
        Get the meta v2 prefix
        
        Returns:
            str: The meta v2 prefix
        """
        return f"/api/v2/meta/tables/{self._table_id}"

    def get_data_v2_prefix(self) -> str:
        """
        Get the data v2 prefix
        
        Returns:
            str: The data v2 prefix
        """
        return f"/api/v2/tables/{self._table_id}"

    def _get(self, path: str, **kwargs) -> Dict:
        url = f"{self._project.get_client().get_base_url()}{path}"
        headers = {"xc-token": self._xc_token}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']

        response = requests.get(url, headers=headers, timeout=self._timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    def _delete(self, path: str, **kwargs) -> Dict:
        """
        Send a DELETE request to the NocoDB API
        
        Args:
            path (str): The API endpoint path
            **kwargs: Additional arguments to pass to requests.delete
            
        Returns:
            Dict: The JSON response from the API
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self._project.get_client().get_base_url()}{path}"
        headers = {"xc-token": self._xc_token}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']

        response = requests.delete(url, headers=headers, timeout=self._timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    def _patch(self, path: str, data: Optional[Dict] = None, **kwargs) -> Dict:
        """
        Send a PATCH request to the NocoDB API
        
        Args:
            path (str): The API endpoint path
            data (Optional[Dict]): The data to send in the request body
            **kwargs: Additional arguments to pass to requests.patch
            
        Returns:
            Dict: The JSON response from the API
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self._project.get_client().get_base_url()}{path}"
        headers = {"xc-token": self._xc_token}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']

        response = requests.patch(url, headers=headers, json=data, timeout=self._timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, data: Optional[Dict] = None, **kwargs) -> Dict:
        """
        Send a POST request to the NocoDB API
        
        Args:
            path (str): The API endpoint path
            data (Optional[Dict]): The data to send in the request body
            **kwargs: Additional arguments to pass to requests.post
            
        Returns:
            Dict: The JSON response from the API
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self._project.get_client().get_base_url()}{path}"
        headers = {"xc-token": self._xc_token}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']

        response = requests.post(url, headers=headers, json=data, timeout=self._timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_full_info(self, force_refresh: bool = False) -> Dict:
        """
        Get the full info for the table
        
        Args:
            force_refresh (bool): Whether to force a refresh of the table info
            
        Returns:
            Dict: The full table info
        """
        with self._cache_lock:
            current_time = time.time()
            cache_ttl = self._cache_ttl
            if(not force_refresh and
               self._table_info_cache is not None and
               (cache_ttl is None or current_time - self._table_info_timestamp < cache_ttl)
               ):
                return self._table_info_cache

            self._table_info_cache = self._get(
                f"{self.get_meta_v2_prefix()}"
            )
            self._table_info_timestamp = current_time
            return self._table_info_cache

    def get_columns_full_info(self, force_refresh: bool = False) -> List:
        """
        Get the full column info for the table
        
        Args:
            force_refresh (bool): Force refresh the cache
            
        Returns:
            Dict: The full column info
        """
        full_info = self.get_full_info(force_refresh=force_refresh)
        return full_info.get("columns", [])

    def list_columns(self, force_refresh: bool = False,
                    full_info: bool = False, convert_time: bool = False) -> List:
        """
        List the column names for the table
        
        Args:
            force_refresh (bool): Force refresh the cache
            
        Returns:
            List[str]: The column names
        """
        columns_data = self.get_columns_full_info(force_refresh=force_refresh)
        columns_list = columns_data

        if convert_time:
            columns_list = [
                {
                    **col,
                    'created_at': parse_utc_datetime(col.get('created_at', None)),
                    'updated_at': parse_utc_datetime(col.get('updated_at', None)),
                }
                for col in columns_list
            ]

        if not full_info:
            columns_list = [
                {
                    "id": col.get("id", ""),
                    "title": col.get("title", ""),
                    "uidt": col.get("uidt", ""),
                }
                for col in columns_list
            ]
        return columns_list

    def count_columns(self) -> int:
        """Count columns in a table."""
        column_info = self.get_columns_full_info()
        column_list = column_info
        if isinstance(column_list, List):
            return len(column_list)
        return 0

    def get_column(self, column_id: str) -> 'NocoDBColumn':
        """
        Get a column object by column ID
        
        Args:
            column_id (str): The column ID to get
            
        Returns:
            NocoDBColumn: The column object
            
        Note:
            This method does not validate if the column exists and does not use cache.
            It directly creates a NocoDBColumn instance with the provided column ID.
        """
        from .column import NocoDBColumn
        return NocoDBColumn(
            table=self,
            column_id=column_id,
            xc_token=self._xc_token,
            timeout=self._timeout,
            cache_ttl=self._cache_ttl
        )

    def clear_table_info_cache(self):
        """
        Clear table info cache
        """
        with self._cache_lock:
            self._table_info_cache = None
            self._table_info_timestamp = 0

    def clear_columns_cache(self):
        """
        Clear columns cache
        """
        with self._cache_lock:
            self._columns_cache = None
            self._columns_timestamp = 0

    def get_records(self) -> List[Dict]:
        """
        Get all records from the table.
        
        Returns:
            List[Dict]: A list of records, each record is a dictionary.
        """
        path = f"{self.get_data_v2_prefix()}/records"
        response = self._get(path)
        return response.get("list", [])
    
    def count_records(self) -> int:
        """
        Count the number of records in the table.
        
        Returns:
            int: The number of records in the table.
            
        Raises:
            requests.exceptions.RequestException: If the API request fails.
            ValueError: If the API response format is invalid.
            
        Example:
            >>> table.count_records()
            42
            
        Note:
            API response format: {"count": 1}
        """
        path = f"{self.get_data_v2_prefix()}/records/count"
        response = self._get(path)
        
        # Validate response format
        if not isinstance(response, dict):
            raise ValueError(f"Invalid API response format: expected dict, got {type(response)}")
            
        count = response.get("count")
        if count is None:
            raise ValueError("Missing 'count' field in API response")
            
        if not isinstance(count, (int, float)):
            raise ValueError(f"Invalid count type: expected number, got {type(count)}")
            
        return int(count)

    def get_record(self, record_id:int) -> Optional[Dict]:
        """
        Get a single record from the table by its ID.
        
        Args:
            record_id (int): The record ID to retrieve
            
        Returns:
            Optional[Dict]: The record data as a dictionary if found
            
        Raises:
            RecordNotFoundError: If the record with the specified ID does not exist
            requests.exceptions.HTTPError: For other HTTP errors (e.g., 500 Internal Server Error)
            
        Example:
            >>> record = table.get_record(123)
            >>> print(record)
            {'Id': 123, 'title': 'Sample Record', 'created_at': '2023-01-01T00:00:00Z'}
        """
        try:
            path = f"{self.get_data_v2_prefix()}/records/{record_id}"
            response = self._get(path)
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise RecordNotFoundError(self._table_id, record_id, e) from e
            raise
