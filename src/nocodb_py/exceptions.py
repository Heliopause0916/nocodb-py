"""
Custom exceptions for NocoDB Python SDK.
"""

from typing import Dict, Any, Optional


class NocoDBError(Exception):
    """Base exception for all NocoDB SDK errors."""
    pass


class APIError(NocoDBError):
    """Base exception for API-related errors."""
    pass


class APIResponseError(APIError):
    """Exception raised when API response format is invalid or unexpected."""
    
    def __init__(self, message: str, api_endpoint: Optional[str] = None, 
                 response_data: Optional[Dict[str, Any]] = None, 
                 expected_format: Optional[str] = None):
        """
        Initialize APIResponseError.
        
        Args:
            message: Error message describing the issue
            api_endpoint: The API endpoint that was called
            response_data: The actual response data received
            expected_format: Description of the expected response format
        """
        self.api_endpoint = api_endpoint
        self.response_data = response_data
        self.expected_format = expected_format
        super().__init__(message)
    
    def __str__(self):
        """Enhanced string representation with additional context."""
        base_message = super().__str__()
        if self.api_endpoint:
            base_message += f" (Endpoint: {self.api_endpoint})"
        if self.expected_format:
            base_message += f" (Expected: {self.expected_format})"
        return base_message


class ResponseFormatError(APIResponseError):
    """Response format does not match expected structure."""
    pass


class MissingFieldError(APIResponseError):
    """Required field is missing from API response."""
    pass


class DataTypeError(APIResponseError):
    """Field value has incorrect data type."""
    pass


class ListRetrievalError(APIResponseError):
    """Failed to retrieve list of resources."""
    pass


class RecordNotFoundError(NocoDBError):
    """Exception raised when a record is not found in the table."""
    
    def __init__(self, table_id: str, record_id: int, original_error: Exception):
        """
        Initialize RecordNotFoundError.
        
        Args:
            table_id: The ID of the table where the record was not found
            record_id: The ID of the record that was not found
            original_error: The original exception that caused this error
        """
        self.table_id = table_id
        self.record_id = record_id
        self.original_error = original_error
        super().__init__(f"Record with ID {record_id} not found in table {table_id}")
