"""
Filename: src/nocodb_py/project.py

NocoDB Project for Python
This module provides a project class to interact with NocoDB project-specific API
"""

import time
import threading
from typing import Dict, List, Any, Optional, Callable
from typing import TYPE_CHECKING
import requests
from .utils import parse_utc_datetime, count_of_nocodb_data
from .client import NocoDBClient
if TYPE_CHECKING:
    from .table import NocoDBTable

# pylint: disable=too-many-instance-attributes
# pylint: disable=trailing-whitespace
# pylint: disable=line-too-long
class NocoDBProject:
    """
    A class representing a NocoDB project with project-specific operations
    
    Attributes:
        _client (NocoDBClient): The NocoDB client instance
        _project_id (str): The unique project identifier
    """
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, client: NocoDBClient, project_id: str, xc_token: str,
                 timeout: int = 30, cache_ttl: Optional[int] = 300):
        """
        Initialize the NocoDBProject with client and project ID
        
        Args:
            client (NocoDBClient): The NocoDB client instance
            project_id (str): The unique project identifier
            xc_token (str): The NocoDB token for authentication
        """
        self._client = client
        self._project_id = project_id
        self._xc_token = xc_token
        self._timeout = timeout
        self._cache_ttl = cache_ttl
        # Project-specific cache
        self._project_info_cache = None
        self._project_info_timestamp = 0
        self._tables_cache = None
        self._tables_timestamp = 0

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
        return hash((self._client, self._project_id, self._xc_token))

    def get_project_id(self) -> str:
        """
        Get the project ID
        
        Returns:
            str: The project ID
        """
        return self._project_id

    def get_client(self) -> NocoDBClient:
        """
        Get the client instance
        
        Returns:
            NocoDBClient: The client instance
        """
        return self._client

    def _get(self, path: str, **kwargs) -> Dict:
        url = f"{self._client.get_base_url()}{path}"
        headers = {"xc-token": self._xc_token}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']

        response = requests.get(url, headers=headers, timeout=self._timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_full_info(self, force_refresh: bool = False) -> Dict:
        """
        Get the full information of the NocoDB instance
        
        Returns:
            Dict[str, Any]: The information of the NocoDB instance
        """
        with self._cache_lock:
            current_time = time.time()
            cache_ttl = self._cache_ttl
            if(not force_refresh and
               self._project_info_cache is not None and
               (cache_ttl is None or current_time - self._project_info_timestamp < cache_ttl)
               ):
                return self._project_info_cache

            self._project_info_cache = self._get(
                f"{self._client.get_meta_v2_prefix()}/bases/{self._project_id}"
                )
            self._project_info_timestamp = current_time
            return self._project_info_cache

    def get_tables_full_info(self, force_refresh: bool = False, include_m2m: bool = False) -> Dict:
        """
        Get the full information of all tables in the project
        
        Returns:
            Dict[str, Any]: The information of all tables in the project
        """
        with self._cache_lock:
            current_time = time.time()
            cache_ttl = self._cache_ttl
            if(not force_refresh and
              self._tables_cache is not None and
              (cache_ttl is None or current_time - self._tables_timestamp < cache_ttl)
              ):
                return self._tables_cache
            params = {
                "includeM2M": include_m2m
            }
            self._tables_cache = self._get(f"{self.get_meta_v2_prefix()}/tables",
                                           params=params)
            self._tables_timestamp = current_time
            return self._tables_cache

    def list_tables(self, force_refresh: bool = False, include_m2m: bool = False,
                      full_info: bool = False, convert_time: bool = False) -> List:
        """
        List all tables in the project
        
        Args:
            force_refresh (bool): Force refresh the cache
            full_info (bool): Get full information of the tables
            convert_time (bool): Convert time fields to datetime objects
            
        """
        tables_data = self.get_tables_full_info(force_refresh=force_refresh, include_m2m=include_m2m)
        tables_list: list[dict[str, Any]] = tables_data.get("list", [])

        if convert_time:
            tables_list = [
                {
                    **table,
                    'created_at': parse_utc_datetime(table.get('created_at', None)),
                    'updated_at': parse_utc_datetime(table.get('updated_at', None))
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
        return tables_list

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
            NocoDBTable: The table object
        """
        # pylint: disable=import-outside-toplevel
        # Reason: Avoid circular imports
        from .table import NocoDBTable
        return NocoDBTable(self,
                           table_id=table_id,
                           xc_token=self._xc_token,
                           **kwargs)

    def get_meta_v2_prefix(self) -> str:
        """
        Get the meta v2 prefix for the project
        Returns:
            str: The meta v2 prefix for the project
        """
        return f"/api/v2/meta/bases/{self._project_id}"

    def find_tables_by_title(self, title: str, match_func :Optional[Callable[[str, str], bool]] =None, force_refresh: bool = False) -> list:
        """
        通过title查找匹配的table_id列表
        
        Args:
            title (str): 搜索的title字符串
            match_func (Callable): 匹配函数，接受两个字符串参数返回bool，默认使用精确匹配
            force_refresh (bool): 是否强制刷新缓存
            
        Returns:
            List[str]: 匹配的table_id列表
        """
        # pylint: disable=import-outside-toplevel
        from .utils import exact_match  # 避免循环导入
        
        if match_func is None:
            match_func = exact_match
        
        tables: Optional[List[Dict[str, Any]]] = self.list_tables(force_refresh=force_refresh)
        if tables is None:
            return []
        
        return [
            table["id"] for table in tables
            if match_func(title, table.get("title", ""))
        ]
