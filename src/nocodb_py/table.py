"""
Filename: src/nocodb_py/table.py

NocoDB Table for Python
"""

import time
import threading
from typing import Dict, List, Any, Optional, Union
import requests
from .utils import parse_utc_datetime, count_of_nocodb_data
from .client import NocoDBClient
from .project import NocoDBProject

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

    def get_project(self) -> NocoDBProject:
        """
        Get the project instance
        
        Returns:
            NocoDBProject: The project instance
        """
        return self._project

