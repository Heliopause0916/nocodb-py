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
        
    def __str__(self):
        """
        String representation of the NocoDBClient
        
        Returns:
            str: String representation of the client
        """
        return f"NocoDBClient(base_url='{self.base_url}', xc_token='***')"
    
    def __repr__(self):
        """
        Official string representation of the NocoDBClient
        
        Returns:
            str: Official representation of the client
        """
        return self.__str__()
    
    def get_nocodb_info(self):
        """
        Get NocoDB instance information from /api/v1/db/meta/nocodb/info
        
        Returns:
            dict: JSON response from the NocoDB API
       
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.base_url}/api/v1/db/meta/nocodb/info"
        headers = {"xc-token": self.xc_token}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        return response.json()
