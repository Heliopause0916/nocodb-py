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
from enum import Enum
import requests
from .utils import parse_utc_datetime, count_of_nocodb_data
from .table import NocoDBTable

class NocoDBColumnType(Enum):
    """
    Enumeration of all NocoDB column types.
    
    This enum provides type-safe references to NocoDB column type identifiers.
    Used for column validation, type checking, and API interactions.
    """
    # Basic types
    SINGLE_LINE_TEXT = "SingleLineText"
    LONG_TEXT = "LongText"
    NUMBER = "Number"
    DATE = "Date"
    TIME = "Time"
    DATETIME = "DateTime"
    CHECKBOX = "Checkbox"
    YEAR = "Year"
    DECIMAL = "Decimal"
    PERCENT = "Percent"
    DURATION = "Duration"
    RATING = "Rating"
    
    # Selection types
    SINGLE_SELECT = "SingleSelect"
    MULTI_SELECT = "MultiSelect"
    
    # Validation types
    EMAIL = "Email"
    URL = "URL"
    PHONE_NUMBER = "PhoneNumber"
    CURRENCY = "Currency"
    
    # Special types
    JSON = "JSON"
    GEOMETRY = "Geometry"
    GEO_DATA = "GeoData"
    QR_CODE = "QrCode"
    BARCODE = "Barcode"
    USER = "User"
    BUTTON = "Button"
    FORMULA = "Formula"
    ATTACHMENT = "Attachment"
    LINK = "Link"
    
    @classmethod
    def from_string(cls, type_str: str) -> 'NocoDBColumnType':
        """
        Convert a string to NocoDBColumnType enum.
        
        Args:
            type_str: The column type string from NocoDB API
            
        Returns:
            NocoDBColumnType: The corresponding enum value
            
        Raises:
            ValueError: If the string doesn't match any enum value
        """
        for column_type in cls:
            if column_type.value == type_str:
                return column_type
        raise ValueError(f"Unknown column type: {type_str}")


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

    def get_meta_v2_prefix(self) -> str:
        """
        Get the meta v2 prefix
        
        Returns:
            str: The meta v2 prefix
        """
        return f"/api/v2/meta/columns/{self._column_id}"

    def _get(self, path: str, **kwargs) -> Dict:
        """
        Send a GET request to the NocoDB API
        
        Args:
            path (str): The API endpoint path
            **kwargs: Additional arguments to pass to requests.get
            
        Returns:
            Dict: The JSON response from the API
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self._table.get_project().get_client().get_base_url()}{path}"
        headers = {"xc-token": self._xc_token}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']

        response = requests.get(url, headers=headers, timeout=self._timeout, **kwargs)
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
        url = f"{self._table.get_project().get_client().get_base_url()}{path}"
        headers = {"xc-token": self._xc_token}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']

        response = requests.post(url, headers=headers, json=data, timeout=self._timeout, **kwargs)
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
        url = f"{self._table.get_project().get_client().get_base_url()}{path}"
        headers = {"xc-token": self._xc_token}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']

        response = requests.patch(url, headers=headers, json=data, timeout=self._timeout, **kwargs)
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
        url = f"{self._table.get_project().get_client().get_base_url()}{path}"
        headers = {"xc-token": self._xc_token}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']

        response = requests.delete(url, headers=headers, timeout=self._timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_full_info(self, force_refresh: bool = False) -> Dict:
        """
        Get the full info for the column
        
        Args:
            force_refresh (bool): Whether to force a refresh of the column info
            
        Returns:
            Dict: The full column info
        """
        with self._cache_lock:
            current_time = time.time()
            cache_ttl = self._cache_ttl
            if(not force_refresh and
               self._column_info_cache is not None and
               (cache_ttl is None or current_time - self._column_info_timestamp < cache_ttl)
               ):
                return self._column_info_cache

            self._column_info_cache = self._get(
                f"{self.get_meta_v2_prefix()}"
            )
            self._column_info_timestamp = current_time
            return self._column_info_cache

    def clear_column_info_cache(self):
        """
        Clear column info cache
        """
        with self._cache_lock:
            self._column_info_cache = None
            self._column_info_timestamp = 0
