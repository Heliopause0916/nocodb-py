"""
Filename: src/nocodb_py/workspace.py

NocoDB Workspace for Python
This module provides a Python interface to interact with NocoDB workspaces.

Note: This module only supports the NocoDB Cloud API. 
It cannot be used with self-hosted NocoDB instances.
"""

from typing import Optional
from .client import NocoDBClient

# pylint: disable=too-many-instance-attributes
# pylint: disable=trailing-whitespace
# pylint: disable=too-many-public-methods
# pylint: disable=line-too-long
# pylint: disable=import-outside-toplevel

class NocoDBWorkspace(NocoDBClient):
    """
    NocoDB Workspace Class
    This class provides methods to interact with NocoDB workspaces.
    
    Note: This class only supports the NocoDB Cloud API. 
    It cannot be used with self-hosted NocoDB instances.
    
    Attributes:
        base_url (str): The base URL of the NocoDB instance
        xc_token (str): The NocoDB API token
        workspace_id (str): The workspace ID
        cache_ttl (int): The cache time to live in seconds
        timeout (int): The request timeout in seconds
    """


    def __init__(self, base_url: str, xc_token: str, workspace_id: Optional[str] = None,
                cache_ttl: Optional[int] = 300,
                timeout = 10):
        """
        Initialize the NocoDBWorkspace
        
        Args:
            workspace_id (str): The workspace ID
        """
        super().__init__(
            base_url=base_url,
            xc_token=xc_token,
            timeout=timeout,
            cache_ttl=cache_ttl
        )

        self._workspace_id = workspace_id

        self._workspace_projects_cache = None
        self._workspace_projects_timestamp = 0

    def __str__(self) -> str:
        """
        String representation of the NocoDBWorkspace
        
        Returns:
            str: String representation including workspace info
        """
        workspace_info = f", workspace_id='{self._workspace_id}'" if self._workspace_id else ""
        return f"NocoDBWorkspace(base_url='{self._base_url}', xc_token='***'{workspace_info})"

    def __repr__(self) -> str:
        """
        Official string representation of the NocoDBWorkspace
        
        Returns:
            str: Official representation of the workspace
        """
        return self.__str__()

    def __eq__(self, other) -> bool:
        """
        Equality comparison for NocoDBWorkspace
        
        Args:
            other: The object to compare with
            
        Returns:
            bool: True if objects are equal, False otherwise
        """
        if not isinstance(other, NocoDBWorkspace):
            return NotImplemented

        if not super().__eq__(other):
            return False

        return self._workspace_id == other._workspace_id

    def __hash__(self) -> int:
        """
        Hash implementation for NocoDBWorkspace.
        
        Returns:
            int: Hash value based on immutable attributes including workspace_id
        """
        parent_hash = super().__hash__()
        return hash((parent_hash, self._workspace_id))

    def get_workspace_id(self) -> Optional[str]:
        """
        Get the workspace ID of the NocoDB instance
        
        Returns:
            str: The workspace ID
        """
        return self._workspace_id
    
    get_id = get_workspace_id  # Alias for get_workspace_id

    def get_meta_v2_prefix(self) -> str:
        """
        Get the meta v2 prefix for the workspace
        
        Returns:
            str: The meta v2 prefix
        """
        return f"/api/v2/meta/workspaces/{self._workspace_id}"
