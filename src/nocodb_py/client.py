"""
Filename: src/nocodb_py/client.py

NocoDB Client for Python
This module provides a client class to interact with NocoDB API
"""

import time
import threading
from typing import Dict, Any, Optional
from typing import TYPE_CHECKING
import requests
from .utils import parse_utc_datetime
if TYPE_CHECKING:
    from .project import NocoDBProject


# pylint: disable=too-many-instance-attributes
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
        "user_me": 300,       # 用户信息: 5分钟
        "projects": 300,     # 项目列表: 5分钟
    }

    def __init__(self, base_url: str, xc_token: str,
                cache_ttl: Optional[int] = None,
                cache_ttl_policies: Optional[Dict[str, int]] = None,
                timeout = 10
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
        self._timeout = timeout

        self._default_cache_ttl = cache_ttl or self._DEFAULT_CACHE_TTL
        if self._default_cache_ttl <= 0:
            raise ValueError("default_cache_ttl must be positive integer")
        self._cache_ttl_policies = self._DEFAULT_CACHE_TTL_POLICIES.copy()
        if cache_ttl_policies:
            self._cache_ttl_policies.update(cache_ttl_policies)
        for key, ttl in self._cache_ttl_policies.items():
            if not isinstance(ttl, int) or ttl <= 0:
                raise ValueError(f"Cache ttl for '{key}' must be positive integer")
        self._nocodb_info_cache = None
        self._nocodb_info_timestamp = 0
        self._user_me_cache = None
        self._user_me_timestamp = 0
        self._projects_cache = None
        self._projects_timeout = 0

        self._cache_lock = threading.RLock()

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

    def __eq__(self, other) -> bool:
        if not isinstance(other, NocoDBClient):
            return NotImplemented
        return (self._base_url == other._base_url and 
                self._xc_token == other._xc_token)

    def __hash__(self) -> int:
        """
        Hash implementation for NocoDBClient.
        
        Returns:
            int: Hash value based on immutable attributes
        """
        # 只对用于相等性比较的不可变属性进行哈希
        return hash((self._base_url, self._xc_token))

    def get_base_url(self) -> str:
        """
        Get the base URL of the NocoDB instance
        
        Returns:
            str: The base URL
        """
        return self._base_url

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

    def _get(self, path: str, **kwargs) -> dict:
        url = f"{self._base_url}{path}"
        headers = {"xc-token": self._xc_token}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']
        response = requests.get(url, headers=headers, timeout=self._timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    def _get_nocodb_info(self, force_refresh: bool = False) -> dict:
        """
        Get NocoDB instance information from /api/v1/db/meta/nocodb/info
        
        Returns:
            dict: JSON response from the NocoDB API
       
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        with self._cache_lock:
            current_time = time.time()

            if (not force_refresh and 
                self._nocodb_info_cache is not None and 
                current_time - self._nocodb_info_timestamp < self._get_cache_ttl("nocodb_info")):
                return self._nocodb_info_cache

            self._nocodb_info_cache = self._get("/api/v1/db/meta/nocodb/info")
            self._nocodb_info_timestamp = current_time

            return self._get("/api/v1/db/meta/nocodb/info")

    def clear_nocodb_info_cache(self):
        """Clear cached server information"""
        with self._cache_lock:
            self._nocodb_info_cache = None
            self._nocodb_info_timestamp = 0

    def server_version(self, force_refresh: bool = False) -> str:
        """
        Get NocoDB server version
        
        Returns:
            str: Server version string
        """
        info = self._get_nocodb_info(force_refresh=force_refresh)
        return info.get("version", "Unknown")

    def _get_me(self, force_refresh: bool = False) -> dict:
        """
        Get current user information
        
        Returns:
            dict: User information
        """
        with self._cache_lock:
            current_time = time.time()

            if(not force_refresh and self._user_me_cache is not None and
               current_time - self._user_me_timestamp < self._get_cache_ttl("user_me")):
                return self._user_me_cache

            self._user_me_cache = self._get("/api/v1/auth/user/me")
            self._user_me_timestamp = current_time
            return self._user_me_cache

    def clear_user_me_cache(self):
        """Clear cached user information"""
        with self._cache_lock:
            self._user_me_cache = None
            self._user_me_timestamp = 0

    def user_id(self, force_refresh: bool = False) -> str:
        """
        Get current user ID
        
        Returns:
            str: User ID
        """
        me = self._get_me(force_refresh=force_refresh)
        return me.get("id", "Unknown") if me else "Unknown"

    def user_email(self, force_refresh: bool = False) -> str:
        """
        Get current user email
        
        Returns:
            str: User email
        """
        me = self._get_me(force_refresh=force_refresh)
        return me.get("email", "Unknown") if me else "Unknown"

    def user_display_name(self, force_refresh: bool = False) -> str:
        """
        Get current user display name
        
        Returns:
            str: User display name
        """
        me = self._get_me(force_refresh=force_refresh)
        return me.get("display_name", "Unknown") if me else "Unknown"

    def _get_projects_data(self, force_refresh: bool = False) -> dict:
        """
        Get projects data
        
        Returns:
            dict: Projects data
        """
        with self._cache_lock:
            current_time = time.time()

            if(not force_refresh and self._projects_cache is not None and
               current_time - self._projects_timeout < self._get_cache_ttl("projects")):
                return self._projects_cache

            self._projects_cache = self._get("/api/v1/db/meta/projects")
            self._projects_timeout = current_time
            return self._projects_cache

    def list_projects(self, force_refresh: bool = False, 
                      full_info: bool = False, convert_time: bool = False) -> list:
        """
        List projects
        
        Returns:
            dict: Projects list
        """
        projects_data = self._get_projects_data(force_refresh= force_refresh)
        projects_list: list[dict[str, Any]] = projects_data.get("list", [])

        if convert_time:
            projects_list =[
                {
                    **project,
                    'created_at': parse_utc_datetime(project.get('created_at', None)),
                    'updated_at': parse_utc_datetime(project.get('updated_at', None))
                }
                for project in projects_list
            ]

        if not full_info:
            projects_list = [
                {
                    "id": project.get("id", ""),
                    "title": project.get("title", ""),
                    "prefix": project.get("prefix", ""),
                    "description": project.get("description", None),
                    "created_at": project.get("created_at", None),
                    "updated_at": project.get("updated_at", None),
                }
                for project in projects_list
                ]
        return projects_list

    def get_project(self, project_id: str, **kwargs) -> 'NocoDBProject':
        """
        Get a NocoDBProject instance for the specified project ID
        
        Args:
            project_id (str): The project ID
            
        Returns:
            NocoDBProject: The project instance
        """
        # pylint: disable=import-outside-toplevel
        # Reason: Avoid circular imports
        from .project import NocoDBProject
        return NocoDBProject(self, project_id, xc_token=self._xc_token, **kwargs)

    def create_project_instance(self, project_id: str) -> 'NocoDBProject':
        """
        Create a NocoDBProject instance for the specified project ID
        (Alias for get_project)
        
        Args:
            project_id (str): The project ID
            
        Returns:
            NocoDBProject: The project instance
        """
        return self.get_project(project_id)
