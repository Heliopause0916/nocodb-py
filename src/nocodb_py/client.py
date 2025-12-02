"""
NocoDB Client for Python
This module provides a client class to interact with NocoDB API
"""

import time
import threading
from typing import Dict, Callable, Any, Optional, Union
import requests

class NocoDBClient:
    """
    A client class for interacting with NocoDB API
    
    Attributes:
        _base_url (str): The base URL of the NocoDB instance
        _xc_token (str): The authentication token for NocoDB API
    """
    
    _DEFAULT_CACHE_TTL = 300
    _DEFAULT_CACHE_TTL_POLICIES = {
        "nocodb_info": 3600,  # 服务器信息: 1小时
        "user_me": 300         # 用户信息: 5分钟
    }

    def __init__(self, base_url: str, xc_token: str,
                cache_ttl: Optional[int] = None,
                cache_ttl_policies: Optional[Dict[str, int]] = None,
                ):
        """
        Initialize the NocoDBClient with base_url and xc_token
        
        Args:
            base_url (str): The base URL of the NocoDB instance
            xc_token (str): The authentication token for NocoDB API
            cache_ttl (Optional[int]): Default cache TTL in seconds
            cache_ttl_policies (Optional[Dict[str, int]]): Cache TTL policies for specific endpoints
        """
        self._base_url = base_url
        self._xc_token = xc_token

        self._default_cache_ttl = cache_ttl or self._DEFAULT_CACHE_TTL
        if self._default_cache_ttl <= 0:
            raise ValueError("default_cache_ttl must be positive integer")
        self._cache_ttl_policies = self._DEFAULT_CACHE_TTL_POLICIES.copy()
        if cache_ttl_policies:
            self._cache_ttl_policies.update(cache_ttl_policies)
        for key, ttl in self._cache_ttl_policies.items():
            if not isinstance(ttl, int) or ttl <= 0:
                raise ValueError(f"Cache ttl for '{key}' must be positive integer")
            
        
    def __str__(self) -> str:
        """
        String representation of the NocoDBClient
        
        Returns:
            str: String representation of the client
        """
        return f"NocoDBClient(base_url='{self._base_url}', xc_token='***')"
    
    def __repr__(self) -> str:
        """
        Official string representation of the NocoDBClient
        
        Returns:
            str: Official representation of the client
        """
        return self.__str__()
    
    def _get_cache_ttl(self, cache_key: str) -> int:
        """
        Get cache TTL for a specific cache key
        为特定缓存键获取缓存TTL，优先使用注册表，否则使用默认值
        
        Args:
            cache_key (str): The cache key to get TTL for
            
        Returns:
            int: The TTL in seconds
        """
        return self._cache_ttl_policies.get(cache_key, self._default_cache_ttl)

    def _get(self, path: str) -> dict:
        url = f"{self._base_url}{path}"
        headers = {"xc-token": self._xc_token}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def _get_nocodb_info(self):
        """
        Get NocoDB instance information from /api/v1/db/meta/nocodb/info
        
        Returns:
            dict: JSON response from the NocoDB API
       
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        return self._get("/api/v1/db/meta/nocodb/info")

    def server_version(self) -> str:
        """
        Get NocoDB server version
        
        Returns:
            str: Server version string
        """
        info = self._get_nocodb_info()
        return info.get("version", "Unknown")

    def _get_me(self) -> dict:
        """
        Get current user information
        
        Returns:
            dict: User information
        """
        return self._get("/api/v1/auth/user/me")
    
    def user_id(self) -> str:
        """
        Get current user ID
        
        Returns:
            str: User ID
        """
        me = self._get_me()
        return me.get("id", "Unknown") if me else "Unknown"
    
    def user_email(self) -> str:
        """
        Get current user email
        
        Returns:
            str: User email
        """
        me = self._get_me()
        return me.get("email", "Unknown") if me else "Unknown"
    
    def user_display_name(self) -> str:
        """
        Get current user display name
        
        Returns:
            str: User display name
        """
        me = self._get_me()
        return me.get("display_name", "Unknown") if me else "Unknown"
