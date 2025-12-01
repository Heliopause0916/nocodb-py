"""
NocoDB Client for Python
This module provides a client class to interact with NocoDB API
"""

import requests

class NocoDBClient:
    """
    A client class for interacting with NocoDB API
    
    Attributes:
        base_url (str): The base URL of the NocoDB instance
        xc_token (str): The authentication token for NocoDB API
    """
    
    def __init__(self, base_url: str, xc_token: str):
        """
        Initialize the NocoDBClient with base_url and xc_token
        
        Args:
            base_url (str): The base URL of the NocoDB instance
            xc_token (str): The authentication token for NocoDB API
        """
        self.base_url = base_url
        self.xc_token = xc_token
        
    def __str__(self) -> str:
        """
        String representation of the NocoDBClient
        
        Returns:
            str: String representation of the client
        """
        return f"NocoDBClient(base_url='{self.base_url}', xc_token='***')"
    
    def __repr__(self) -> str:
        """
        Official string representation of the NocoDBClient
        
        Returns:
            str: Official representation of the client
        """
        return self.__str__()
    
    def __get(self, path: str) -> dict:
        url = f"{self.base_url}{path}"
        headers = {"xc-token": self.xc_token}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def __get_nocodb_info(self):
        """
        Get NocoDB instance information from /api/v1/db/meta/nocodb/info
        
        Returns:
            dict: JSON response from the NocoDB API
       
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        return self.__get("/api/v1/db/meta/nocodb/info")

    def server_version(self) -> str:
        """
        Get NocoDB server version
        
        Returns:
            str: Server version string
        """
        info = self.__get_nocodb_info()
        return info.get("version", "Unknown")

    def __get_me(self) -> dict:
        """
        Get current user information
        
        Returns:
            dict: User information
        """
        return self.__get("/api/v1/auth/user/me")
    
    def user_id(self) -> str:
        """
        Get current user ID
        
        Returns:
            str: User ID
        """
        me = self.__get_me()
        return me.get("id", "Unknown") if me else "Unknown"
    
    def user_email(self) -> str:
        """
        Get current user email
        
        Returns:
            str: User email
        """
        me = self.__get_me()
        return me.get("email", "Unknown") if me else "Unknown"
    
    def user_display_name(self) -> str:
        """
        Get current user display name
        
        Returns:
            str: User display name
        """
        me = self.__get_me()
        return me.get("display_name", "Unknown") if me else "Unknown"
