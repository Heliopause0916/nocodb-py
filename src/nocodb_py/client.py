"""
Filename: src/nocodb_py/client.py

NocoDB Client for Python
This module provides a client class to interact with NocoDB API
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
from typing import Dict, List, Any, Optional, Callable, Union, Literal, Tuple
from typing import TYPE_CHECKING
import requests
from .utils import parse_metadata_datetime, count_of_nocodb_data
from .exceptions import MissingFieldError, ListRetrievalError
from .variable import max_workspace_num, max_project_num
if TYPE_CHECKING:
    from .project import NocoDBProject
    from .workspace import NocoDBWorkspace

class NocoDBClient:
    """
    A client class for interacting with NocoDB API
    
    Attributes:
        _base_url (str): The base URL of the NocoDB instance
        _xc_token (str): The authentication token for NocoDB API
    """

    CACHE_FOREVER = None

    def __init__(self, base_url: str, xc_token: str,
                cache_ttl: Optional[int] = 300,
                timeout = 10
                ):
        """
        Initialize the NocoDBClient with base_url and xc_token
        
        Args:
            base_url (str): The base URL of the NocoDB instance
            xc_token (str): The authentication token for NocoDB API
            cache_ttl (Optional[int]): Default cache TTL in seconds, None for forever
        """
        self._base_url = base_url
        self._xc_token = xc_token
        self._timeout = timeout

        self._cache_ttl = cache_ttl
        self._nocodb_info_cache = None
        self._nocodb_info_timestamp = 0
        self._user_me_cache = None
        self._user_me_timestamp = 0
        self._projects_cache = None
        self._projects_timeout = 0
        self._workspaces_cache = None
        self._workspaces_timeout = 0

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
                self._xc_token == other._xc_token
                )

    def __hash__(self) -> int:
        """
        Hash implementation for NocoDBClient.
        
        Returns:
            int: Hash value based on immutable attributes
        """
        # Only hash immutable attributes used for equality comparison
        return hash((self._base_url, self._xc_token))

    def __copy__(self):
        """
        Shallow copy implementation for NocoDBClient.
        
        Returns:
            NocoDBClient: A new client instance with same configuration but fresh cache
        """
        new_client = NocoDBClient(self._base_url, self._xc_token,
                                self._cache_ttl, self._timeout)
        # Do not copy cache state - new object should have fresh cache
        return new_client

    def __deepcopy__(self, memo):
        """
        Deep copy implementation for NocoDBClient.
        
        Args:
            memo: Memo dictionary for deepcopy
            
        Returns:
            NocoDBClient: A new client instance with same configuration but fresh cache
        """
        # For NocoDBClient, deepcopy is the same as shallow copy
        # since we don't want to copy cache state
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
        state.pop('_nocodb_info_cache', None)
        state.pop('_nocodb_info_timestamp', None)
        state.pop('_user_me_cache', None)
        state.pop('_user_me_timestamp', None)
        state.pop('_projects_cache', None)
        state.pop('_projects_timeout', None)
        state.pop('_workspaces_cache', None)
        state.pop('_workspaces_timeout', None)
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
        self._nocodb_info_cache = None
        self._nocodb_info_timestamp = 0
        self._user_me_cache = None
        self._user_me_timestamp = 0
        self._projects_cache = None
        self._projects_timeout = 0
        self._workspaces_cache = None
        self._workspaces_timeout = 0

    def get_workspaces_full_info(self, force_refresh: bool = False) -> Optional[Dict]:
        """
        Get all workspaces with full information
        
        Returns:
            dict: The workspaces information (deep copy for safety)
        """
        if not self.is_cloud():
            return None
        with self._cache_lock:
            current_time = time.time()
            cache_ttl = self._get_cache_ttl()
            if(not force_refresh and
               self._workspaces_cache is not None and
               (cache_ttl is None or current_time - self._workspaces_timeout < cache_ttl)
               ):
                return copy.deepcopy(self._workspaces_cache)

            self._workspaces_cache = self._get("/api/v1/workspaces")
            self._workspaces_timeout = current_time
            return copy.deepcopy(self._workspaces_cache)

    def count_workspaces(self, force_refresh: bool = False) -> Optional[int]:
        """
        Count all workspaces
        
        Returns:
            int: The number of workspaces
        """
        workspaces = self.get_workspaces_full_info(force_refresh=force_refresh)
        if workspaces is None:
            return None
        
        return count_of_nocodb_data(workspaces)

    def list_workspaces(self, force_refresh: bool = False,
                        full_info: bool = False) -> Optional[List]:
        """
        List all workspaces
        
        Returns:
            dict: The workspaces information (deep copy for safety)
        """

        workspaces_data = self.get_workspaces_full_info(force_refresh=force_refresh)
        if workspaces_data is None:
            return None
        workspaces_list = workspaces_data.get("list",[])

        if not full_info:
            workspaces_list = [
                {
                    "id": workspace.get("id", ""),
                    "title": workspace.get("title", ""),
                }
                for workspace in workspaces_list
                ]
        return copy.deepcopy(workspaces_list)

    def get_workspace(self, workspace_id: str) -> 'NocoDBWorkspace':
        """
        Get a workspace by ID
        
        Args:
            workspace_id (str): The workspace ID
            
        Returns:
            NocoDBWorkspace: The workspace object
        """

        # pylint: disable=import-outside-toplevel
        from .workspace import NocoDBWorkspace
        return NocoDBWorkspace(
            base_url=self._base_url,
            xc_token=self._xc_token,
            workspace_id=workspace_id,
            cache_ttl=self._cache_ttl,
            timeout=self._timeout,
        )

    def get_base_url(self) -> str:
        """
        Get the base URL of the NocoDB instance
        
        Returns:
            str: The base URL
        """
        return self._base_url

    # pylint: disable=unused-argument
    def _get_cache_ttl(self, cache_key: Optional[str] = None) -> Optional[int]:
        """
        Get cache TTL for a specific cache key
        Priority is given to the registry, otherwise the default value is used
        
        Args:
            cache_key (str): The cache key to get TTL for
            
        Returns:
            int: The TTL in seconds
        """
        # return self._cache_ttl_policies.get(cache_key, self._default_cache_ttl)
        return self._cache_ttl

    def clear_workspaces_cache(self):
        """
        Clear workspaces cache
        """
        with self._cache_lock:
            self._workspaces_cache = None
            self._workspaces_timeout = 0

    def clear_projects_cache(self):
        """
        Clear projects cache
        """
        with self._cache_lock:
            self._projects_cache = None
            self._projects_timeout = 0

    def _get(self, path: str, **kwargs) -> Dict:
        """
        Send a GET request to the NocoDB API
        
        Note: This method is intended for internal use by NocoDB-related classes
        (NocoDBProject, NocoDBTable, NocoDBColumn, etc.) and should not be called
        directly by external code.
        
        Args:
            path (str): The API endpoint path
            **kwargs: Additional arguments to pass to requests.get
            
        Returns:
            Dict: The JSON response from the API
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self._base_url}{path}"
        headers = {"xc-token": self._xc_token}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']
        response = requests.get(url, headers=headers, timeout=self._timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, data: Optional[Union[Dict, List[Dict]]] = None, **kwargs) -> Dict:
        """
        Send a POST request to the NocoDB API
        
        Note: This method is intended for internal use by NocoDB-related classes
        (NocoDBProject, NocoDBTable, NocoDBColumn, etc.) and should not be called
        directly by external code.
        
        Args:
            path (str): The API endpoint path
            data (Optional[Union[Dict, List[Dict]]]): The data to send in the request body
            **kwargs: Additional arguments to pass to requests.post
            
        Returns:
            Dict: The JSON response from the API
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self._base_url}{path}"
        headers = {"xc-token": self._xc_token}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']
        response = requests.post(url, headers=headers, json=data, timeout=self._timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    def _delete(self, path: str, data: Optional[Union[Dict, List[Dict]]] = None, **kwargs) -> Any:
        """
        Send a DELETE request to the NocoDB API
        
        Note: This method is intended for internal use by NocoDB-related classes
        (NocoDBProject, NocoDBTable, NocoDBColumn, etc.) and should not be called
        directly by external code.
        
        Args:
            path (str): The API endpoint path
            data (Optional[Union[Dict, List[Dict]]]): The data to send in the request body
            **kwargs: Additional arguments to pass to requests.delete
            
        Returns:
            Dict: The JSON response from the API
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self._base_url}{path}"
        headers = {"xc-token": self._xc_token}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']
        response = requests.delete(url, headers=headers, json=data, timeout=self._timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    def _patch(self, path: str, data: Optional[Union[Dict, List[Dict]]] = None, **kwargs) -> Dict:
        """
        Send a PATCH request to the NocoDB API
        
        Note: This method is intended for internal use by NocoDB-related classes
        (NocoDBProject, NocoDBTable, NocoDBColumn, etc.) and should not be called
        directly by external code.
        
        Args:
            path (str): The API endpoint path
            data (Optional[Union[Dict, List[Dict]]]): The data to send in the request body
            **kwargs: Additional arguments to pass to requests.patch
            
        Returns:
            Dict: The JSON response from the API
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self._base_url}{path}"
        headers = {"xc-token": self._xc_token}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']
        response = requests.patch(url, headers=headers, json=data, timeout=self._timeout, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def get_full_info(self, force_refresh: bool = False) -> Dict:
        """
        Get NocoDB instance information from /api/v1/db/meta/nocodb/info
        
        Returns:
            dict: JSON response from the NocoDB API (deep copy for safety)
       
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        with self._cache_lock:
            current_time = time.time()
            cache_ttl = self._get_cache_ttl("nocodb_info")
            if(not force_refresh and
               self._nocodb_info_cache is not None and
               (cache_ttl is None or current_time - self._nocodb_info_timestamp < cache_ttl)
               ):
                return copy.deepcopy(self._nocodb_info_cache)

            self._nocodb_info_cache = self._get("/api/v1/db/meta/nocodb/info")
            self._nocodb_info_timestamp = current_time
            return copy.deepcopy(self._nocodb_info_cache)

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
        info = self.get_full_info(force_refresh=force_refresh)
        return info.get("version", "Unknown")

    def is_cloud(self, force_refresh: bool = False) -> bool:
        """
        Check if server is NocoDB Cloud
        
        Returns:
            bool: True if server is NocoDB Cloud
        """
        info = self.get_full_info(force_refresh=force_refresh)
        return info.get("isCloud", False)

    def get_me_full_info(self, force_refresh: bool = False) -> Dict:
        """
        Get current user information
        
        Returns:
            dict: User information (deep copy for safety)
        """
        with self._cache_lock:
            current_time = time.time()
            cache_ttl = self._get_cache_ttl("user_me")
            if(not force_refresh and self._user_me_cache is not None and
               (cache_ttl is None or current_time - self._nocodb_info_timestamp < cache_ttl)
               ):
                return copy.deepcopy(self._user_me_cache)

            self._user_me_cache = self._get("/api/v1/auth/user/me")
            self._user_me_timestamp = current_time
            return copy.deepcopy(self._user_me_cache)

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
        me = self.get_me_full_info(force_refresh=force_refresh)
        return me.get("id", "Unknown") if me else "Unknown"

    def user_email(self, force_refresh: bool = False) -> str:
        """
        Get current user email
        
        Returns:
            str: User email
        """
        me = self.get_me_full_info(force_refresh=force_refresh)
        return me.get("email", "Unknown") if me else "Unknown"

    def user_display_name(self, force_refresh: bool = False) -> str:
        """
        Get current user display name
        
        Returns:
            str: User display name
        """
        me = self.get_me_full_info(force_refresh=force_refresh)
        return me.get("display_name", "Unknown") if me else "Unknown"

    def get_projects_full_info_backend(self, force_refresh: bool = False) -> Dict:
        """
        Get projects data
        
        Returns:
            dict: Projects data (deep copy for safety)
        """

        with self._cache_lock:
            current_time = time.time()
            cache_ttl = self._get_cache_ttl("projects")
            if(not force_refresh and self._projects_cache is not None and
               (cache_ttl is None or current_time - self._nocodb_info_timestamp < cache_ttl)
               ):
                return copy.deepcopy(self._projects_cache)

            self._projects_cache = self._get(f"{self.get_meta_v2_prefix()}/bases")
            self._projects_timeout = current_time
            return copy.deepcopy(self._projects_cache)

    def _validate_project_access(self) -> None:
        """
        Validate if the current instance has permission to access project data
        
        Raises:
            ValueError: When the instance type does not match the deployment mode
        """
        is_cloud_instance = self.is_cloud()
        class_name = type(self).__name__
        
        # Check if allowed conditions are met
        allowed_conditions = [
            (is_cloud_instance and class_name == "NocoDBWorkspace"),
            (not is_cloud_instance and class_name == "NocoDBClient")
        ]
        
        if not any(allowed_conditions):
            raise ValueError(
                f"Invalid project access: "
                f"Instance type '{class_name}' is not allowed for "
                f"{'cloud' if is_cloud_instance else 'self-hosted'} instance. "
                f"Only NocoDBWorkspace can access projects on cloud instances, "
                f"and only NocoDBClient can access projects on self-hosted instances."
            )

    def get_projects_full_info(self, force_refresh: bool = False) -> Dict:
        """
        Get projects data
        
        Returns:
            dict: Projects data
        """
        # Validate project access permissions
        self._validate_project_access()
        
        return self.get_projects_full_info_backend(force_refresh=force_refresh)

    get_bases_full_info = get_projects_full_info

    def list_projects(self, force_refresh: bool = False,
                      full_info: bool = False, convert_time: bool = False) -> List[Dict[str, Any]]:
        """
        List projects
        
        Returns:
            dict: Projects list (deep copy for safety)
        """
        # Validate project access permissions
        self._validate_project_access()
        
        projects_data = self.get_projects_full_info(force_refresh= force_refresh)
        projects_list: List[Dict[str, Any]] = projects_data.get("list", [])

        if convert_time:
            projects_list =[
                {
                    **project,
                    'created_at': parse_metadata_datetime(project.get('created_at', None)),
                    'updated_at': parse_metadata_datetime(project.get('updated_at', None))
                }
                for project in projects_list
            ]

        if not full_info:
            projects_list = [
                {
                    "id": project.get("id", ""),
                    "title": project.get("title", ""),
                }
                for project in projects_list
                ]
        return copy.deepcopy(projects_list)

    list_bases = list_projects

    def count_projects(self, force_refresh: bool = False) -> Optional[int]:
        """
        Count the number of projects in the database
        
        Args:
            force_refresh (bool): Whether to force a refresh of the project list
            
        Returns:
            int: The number of projects
        """
        # Validate project access permissions
        self._validate_project_access()
        
        projects = self.get_projects_full_info(force_refresh=force_refresh)
        if projects is None:
            return None
        return count_of_nocodb_data(projects)

    count_bases = count_projects

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
        return NocoDBProject(self,
                             project_id=project_id,
                             **kwargs)

    get_base = get_project

    def get_project_title(self, project_id: str, force_refresh: bool = False) -> str:
        """
        Get project title by project ID
        
        Args:
            project_id (str): Project ID
            force_refresh (bool): Whether to force refresh cache
            
        Returns:
            str: Project title
            
        Raises:
            ValueError: When project is not found or title is empty
        """
        # Validate project access permissions
        self._validate_project_access()
        
        projects = self.list_projects(force_refresh=force_refresh)
        if projects is None:
            raise ListRetrievalError(
                "Failed to get project list",
                api_endpoint="/api/v2/meta/bases/",
                expected_format="List of project objects"
            )
            
        for project in projects:
            if project.get("id") == project_id:
                title = project.get("title")
                if title is not None:
                    return title
                raise ValueError(f"Project {project_id} has empty title")
                
        raise ValueError(f"Project with ID {project_id} not found")

    get_base_title = get_project_title

    def get_workspace_title(self, workspace_id: str, force_refresh: bool = False) -> str:
        """
        Get workspace title by workspace ID

        Args:
            workspace_id (str): Workspace ID
            force_refresh (bool): Whether to force refresh cache
            
        Returns:
            str: Workspace title
            
        Raises:
            ValueError: When workspace is not found or title is empty
        """
        if not self.is_cloud():
            raise ValueError("Workspace operations are only supported for cloud instances")
            
        workspaces = self.list_workspaces(force_refresh=force_refresh)
        if workspaces is None:
            raise ListRetrievalError(
                "Failed to get workspace list",
                api_endpoint="/api/v2/meta/workspaces/",
                expected_format="List of workspace objects"
            )
            
        for workspace in workspaces:
            if workspace.get("id") == workspace_id:
                title = workspace.get("title")
                if title is not None:
                    return title
                raise ValueError(f"Workspace {workspace_id} has empty title")
                
        raise ValueError(f"Workspace with ID {workspace_id} not found")

    def get_meta_v2_prefix(self) -> str:
        """
        Get the meta v2 prefix for the API
        
        Returns:
            str: The meta v2 prefix
        """

        return "/api/v2/meta"

    def create_project(self, title: str, description: Optional[str] = None,
                      return_type: Literal["object", "json", "both"] = 'object') -> Union[Dict, 'NocoDBProject', Tuple['NocoDBProject', Dict]]:
        """
        Create a new NocoDB project
        
        Args:
            title (str): Project title
            description (Optional[str]): Project description, optional
            return_type (str): Return type, 'json' returns JSON response, 'object' returns NocoDBProject object,
                              'both' returns tuple (NocoDBProject object, JSON response), default is 'object'
            
        Returns:
            Union[Dict, NocoDBProject, Tuple[NocoDBProject, Dict]]:
                - If return_type='json': Returns API JSON response
                - If return_type='object': Returns NocoDBProject object
                - If return_type='both': Returns tuple (NocoDBProject object, JSON response)
                
        Raises:
            requests.exceptions.RequestException: HTTP request failed
            ValueError: When return_type parameter is invalid
        """
        path = f"{self.get_meta_v2_prefix()}/bases"
        data = {"title": title}
        if description is not None:
            data["description"] = description
            
        response = self._post(path, data=data)

        self.clear_projects_cache()

        if return_type == 'object':
            project_id = response.get('id')
            if project_id is None:
                raise MissingFieldError(
                    "Project ID not included in response",
                    api_endpoint="/api/v2/meta/bases/",
                    expected_format="JSON object with 'id' field"
                )
            # pylint: disable=import-outside-toplevel
            from .project import NocoDBProject
            project_obj = NocoDBProject(self, project_id,
                                       timeout=self._timeout, cache_ttl=self._cache_ttl)
            return project_obj
        elif return_type == 'json':
            return response
        elif return_type == 'both':
            project_id = response.get('id')
            if project_id is None:
                raise MissingFieldError(
                    "Project ID not included in response",
                    api_endpoint="/api/v2/meta/bases/",
                    expected_format="JSON object with 'id' field"
                )
            # pylint: disable=import-outside-toplevel
            from .project import NocoDBProject
            project_obj = NocoDBProject(self, project_id,
                                       timeout=self._timeout, cache_ttl=self._cache_ttl)
            return (project_obj, response)
        else:
            raise ValueError(f"Invalid return_type argument: {return_type}. Options: 'json', 'object', or 'both'")

    def find_workspaces_by_title(self, title: str, match_func: Optional[Callable[[str, str], bool]] =None, force_refresh: bool = False) -> list:
        """
        Find matching workspace_id list by title
        
        Args:
            title (str): Title string to search for
            match_func (Callable): Matching function that takes two string parameters and returns bool, defaults to exact match
            force_refresh (bool): Whether to force refresh cache
            
        Returns:
            List[str]: List of matching workspace IDs
        """
        from .utils import exact_match  # Avoid circular import

        if match_func is None:
            match_func = exact_match

        workspaces: Optional[List[Dict[str, Any]]] = self.list_workspaces(force_refresh=force_refresh)
        if workspaces is None:
            return []

        return [
            workspace["id"] for workspace in workspaces
            if match_func(title, workspace.get("title", ""))
        ]

    def find_projects_by_title(self, title: str, match_func: Optional[Callable[[str, str], bool]] =None, force_refresh: bool = False) -> list:
        """
        Find matching project_id list by title
        
        Args:
            title (str): Title string to search for
            match_func (Callable): Matching function that takes two string parameters and returns bool, defaults to exact match
            force_refresh (bool): Whether to force refresh cache
            
        Returns:
            List[str]: List of matching project IDs
        """
        # Validate project access permissions
        self._validate_project_access()

        from .utils import exact_match  # Avoid circular import

        if match_func is None:
            match_func = exact_match

        projects: Optional[List[Dict[str, Any]]] = self.list_projects(force_refresh=force_refresh)
        if projects is None:
            return []

        return [
            project["id"] for project in projects
            if match_func(title, project.get("title", ""))
        ]

    find_bases_by_title = find_projects_by_title

    def _extract_project_id(self, project: Union[str, 'NocoDBProject']) -> str:
        """
        Extract project_id from string or NocoDBProject object
        
        Args:
            project (Union[str, NocoDBProject]): Project ID string or NocoDBProject object
            
        Returns:
            str: Extracted project_id string
            
        Raises:
            TypeError: When argument type is not str or NocoDBProject
        """
        if isinstance(project, str):
            return project
        else:
            # Lazy import to avoid circular import
            from .project import NocoDBProject
            if isinstance(project, NocoDBProject):
                return project.get_project_id()
            else:
                raise TypeError(
                    f"Argument type must be str or NocoDBProject, actual type is {type(project)}"
                )

    def delete_project(self, project: Union[str, 'NocoDBProject']) -> Dict:
        """
        Delete a project, supports project ID string or NocoDBProject object
        
        Args:
            project (Union[str, NocoDBProject]): Project ID string or NocoDBProject object instance
            
        Returns:
            Dict: JSON response from API delete operation
            
        Raises:
            requests.exceptions.RequestException: HTTP request failed
            ValueError: Project access validation failed
            TypeError: Argument type error
            
        Example:
            # Use project ID string
            client.delete_project("proj_123")
            
            # Use NocoDBProject object
            project_obj = client.get_project("proj_123")
            client.delete_project(project_obj)
        """
        # Extract project_id
        project_id = self._extract_project_id(project)
        
        # Validate project access permissions
        self._validate_project_access()
        
        # Build API path
        path = f"{self.get_meta_v2_prefix()}/bases/{project_id}"
        
        # Send DELETE request
        response = self._delete(path)
        
        # Clear project cache to ensure subsequent operations get latest data
        self.clear_projects_cache()
        
        return response

    def update_project(self, project: Union[str, 'NocoDBProject'],
                      title: Optional[str] = None,
                      order: Optional[int] = None,
                      meta: Optional[Dict] = None,
                      return_type: Literal["object", "json", "both"] = 'json') -> Union[Dict, 'NocoDBProject', Tuple['NocoDBProject', Dict]]:
        """
        Update a project, supports project ID string or NocoDBProject object
        
        Args:
            project (Union[str, NocoDBProject]): Project ID string or NocoDBProject object instance
            title (Optional[str]): New project title, optional
            order (Optional[int]): New project order, optional
            meta (Optional[Dict]): New project metadata, optional
            return_type (str): Return type, 'json' returns JSON response, 'object' returns NocoDBProject object,
                              'both' returns tuple (NocoDBProject object, JSON response), default is 'json'
            
        Returns:
            Union[Dict, NocoDBProject, Tuple[NocoDBProject, Dict]]:
                - If return_type='json': Returns API JSON response
                - If return_type='object': Returns NocoDBProject object
                - If return_type='both': Returns tuple (NocoDBProject object, JSON response)
                
        Raises:
            requests.exceptions.RequestException: HTTP request failed
            ValueError: Project access validation failed or no update parameters provided
            TypeError: Argument type error
            
        Example:
            # Update project title using project ID
            client.update_project("proj_123", title="New Project Title")
            
            # Update project using NocoDBProject object
            project_obj = client.get_project("proj_123")
            client.update_project(project_obj, title="Updated Title", order=2)
        """
        # Extract project_id
        project_id = self._extract_project_id(project)
        
        # Validate project access permissions
        self._validate_project_access()
        
        # Check if at least one update parameter is provided
        if title is None and order is None and meta is None:
            raise ValueError("At least one update parameter (title, order, or meta) must be provided")
        
        # Build update data
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if order is not None:
            update_data["order"] = order
        if meta is not None:
            update_data["meta"] = meta
        
        # Build API path
        path = f"{self.get_meta_v2_prefix()}/bases/{project_id}"
        
        # Send PATCH request
        response = self._patch(path, data=update_data)
        
        # Clear project cache to ensure subsequent operations get latest data
        self.clear_projects_cache()
        
        # If project object was provided, also clear its specific cache
        # pylint: disable=import-outside-toplevel
        from .project import NocoDBProject
        if isinstance(project, NocoDBProject):
            project.clear_project_info_cache()
        
        if return_type == 'object':
            project_obj = NocoDBProject(self, project_id,
                                       timeout=self._timeout, cache_ttl=self._cache_ttl)
            return project_obj
        elif return_type == 'json':
            return response
        elif return_type == 'both':
            project_obj = NocoDBProject(self, project_id,
                                       timeout=self._timeout, cache_ttl=self._cache_ttl)
            return (project_obj, response)
        else:
            raise ValueError(f"Invalid return_type argument: {return_type}. Options: 'json', 'object', or 'both'")

    update_base = update_project

    delete_base = delete_project
