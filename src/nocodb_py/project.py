"""
Filename: src/nocodb_py/project.py

NocoDB Project for Python
This module provides a project class to interact with NocoDB project-specific API
"""

import time
import threading
from typing import Dict, List, Any, Optional, Union
import requests
from .client import NocoDBClient
# from .utils import parse_utc_datetime

# pylint: disable=too-many-instance-attributes
class NocoDBProject:
    """
    A class representing a NocoDB project with project-specific operations
    
    Attributes:
        _client (NocoDBClient): The NocoDB client instance
        _project_id (str): The unique project identifier
    """

    def __init__(self, client: NocoDBClient, project_id: str, xc_token: str, timeout: int = 30):
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

    def _get(self, path: str, **kwargs) -> dict:
        url = f"{self._client.get_base_url()}{path}"
        headers = {"xc-token": self._xc_token}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']
        
        response = requests.get(url, headers=headers, timeout=self._timeout, **kwargs)
        response.raise_for_status()
        return response.json()
    
    # def _get_info(self) -> dict:
    #     """
    #     Get the information of the NocoDB instance
        
    #     Returns:
    #         Dict[str, Any]: The information of the NocoDB instance
    #     """
    #     return self._client.get_info()