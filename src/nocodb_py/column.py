"""
Filename: src/nocodb_py/column.py

NocoDB Column for Python
This module provides a column class to interact with NocoDB column-specific API
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
import requests
from .utils import parse_utc_datetime, count_of_nocodb_data
from .table import NocoDBTable

# pylint: disable=too-many-instance-attributes
class NocoDBColumn:
    """
    A class representing a NocoDB column with column-specific operations
    
    Attributes:
        _table (NocoDBTable): The NocoDB table instance
        _column_id (str): The unique column identifier
    """

    def __init__(self, table: NocoDBTable, column_id: str, xc_token: str, timeout: int = 30, cache_ttl: Optional[int] = 300):
        """
        Initialize the NocoDBColumn with table and column ID
        
        Args:
            table (NocoDBTable): The NocoDB table instance
            column_id (str): The unique column identifier
            xc_token (str): The NocoDB token for authentication
            timeout (int): Request timeout in seconds
            cache_ttl (Optional[int]): Cache time-to-live in seconds
        """
        self._table = table
        self._column_id = column_id
        self._xc_token = xc_token
        self._timeout = timeout
        self._cache_ttl = cache_ttl

        # Column-specific cache
        self._column_info_cache = None
        self._column_info_timestamp = 0
        self._cache_lock = threading.RLock()

    def __str__(self) -> str:
        """
        String representation of the NocoDBColumn
        
        Returns:
            str: String representation of the column
        """
        return f"NocoDBColumn(id='{self._column_id}', table={self._table})"

    def __repr__(self) -> str:
        """
        Official string representation of the NocoDBColumn
        
        Returns:
            str: Official representation of the column
        """
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another NocoDBColumn
        
        Args:
            other (object): The other object to compare with
            
        Returns:
            bool: True if equal, False otherwise
        """
        if not isinstance(other, NocoDBColumn):
            return False
        return self._column_id == other._column_id and self._table == other._table

    def __hash__(self) -> int:
        """
        Hash implementation for NocoDBColumn.
        
        Returns:
            int: Hash value based on immutable attributes that define identity
        """
        return hash((self._table, self._column_id))

    def get_column_id(self) -> str:
        """
        Get the column ID
        
        Returns:
            str: The column ID
        """
        return self._column_id
    
    get_id = get_column_id

    def get_table(self) -> NocoDBTable:
        """
        Get the table instance
        
        Returns:
            NocoDBTable: The table instance
        """
        return self._table

