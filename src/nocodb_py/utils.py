"""
Filename: src/nocodb_py/utils.py

Utility functions for NocoDB Python client
This module provides utility functions for handling NocoDB data
"""

# pylint: disable=too-many-instance-attributes
# pylint: disable=trailing-whitespace
# pylint: disable=line-too-long

from datetime import datetime, timezone, date, time
from typing import Dict, List, Any, Optional

# Supported time format constants
METADATA_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'  # For metadata (tables, columns, projects)
RECORD_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S%z'  # For record data (ISO 8601 with timezone)
RECORD_DATE_FORMAT = '%Y-%m-%d'                 # For record date data
RECORD_TIME_FORMAT = '%H:%M:%S'                 # For record time data

def parse_metadata_datetime(value: Optional[str], format_str: str = METADATA_DATETIME_FORMAT) -> datetime:
    """
    Parse metadata datetime string into a datetime object.
    Used for table, column, and project metadata (created_at, updated_at).
    The parsed datetime is always set to UTC+0 timezone.
    
    Args:
        value (Optional[str]): Metadata datetime string
        
    Returns:
        datetime: UTC datetime object (UTC+0 timezone)
        
    Raises:
        ValueError: If parsing fails
    """

    if not value:
        raise ValueError("Cannot parse empty datetime string")
    try:
        naive_dt = datetime.strptime(value, format_str)
        return naive_dt.replace(tzinfo=timezone.utc)
    except ValueError as e:
        raise ValueError(f"Failed to parse datetime '{value}' with format '{format_str}': {e}")

def parse_record_datetime(value: Optional[str]) -> datetime:
    """
    Parse record datetime string into a datetime object.
    Used for record data fields (ISO 8601 format with timezone).
    
    Args:
        value (Optional[str]): Record datetime string (e.g., "2025-12-28 16:00:00+00:00")
        
    Returns:
        datetime: UTC datetime object
        
    Raises:
        ValueError: If parsing fails
    """
    if not value:
        raise ValueError("Cannot parse empty datetime string")
    try:
        # Handle ISO 8601 format with timezone
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as e:
        raise ValueError(f"Failed to parse record datetime '{value}': {e}")

def parse_record_date(value: Optional[str]) -> date:
    """
    Parse record date string into a date object.
    Used for record date fields (YYYY-MM-DD format).
    
    Args:
        value (Optional[str]): Record date string (e.g., "2025-12-29")
        
    Returns:
        datetime.date: Date object
        
    Raises:
        ValueError: If parsing fails
    """
    if not value:
        raise ValueError("Cannot parse empty date string")
    try:
        return datetime.strptime(value, RECORD_DATE_FORMAT).date()
    except ValueError as e:
        raise ValueError(f"Failed to parse record date '{value}': {e}")

def parse_record_time(value: Optional[str]) -> time:
    """
    Parse record time string into a time object.
    Used for record time fields (HH:mm:ss format).
    
    Args:
        value (Optional[str]): Record time string (e.g., "21:51:00")
        
    Returns:
        datetime.time: Time object
        
    Raises:
        ValueError: If parsing fails
    """
    if not value:
        raise ValueError("Cannot parse empty time string")
    try:
        return datetime.strptime(value, RECORD_TIME_FORMAT).time()
    except ValueError as e:
        raise ValueError(f"Failed to parse record time '{value}': {e}")

def datetime_to_record_format(dt: datetime) -> str:
    """
    Convert datetime object to record format string (ISO 8601 with timezone).
    
    Args:
        dt (datetime): Datetime object
        
    Returns:
        str: Record datetime string (e.g., "2025-12-28 16:00:00+00:00")
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat(' ', 'seconds')

def date_to_record_format(d: date) -> str:
    """
    Convert date object to record format string (YYYY-MM-DD).
    
    Args:
        d (datetime.date): Date object
        
    Returns:
        str: Record date string (e.g., "2025-12-29")
    """
    return d.strftime(RECORD_DATE_FORMAT)

def time_to_record_format(t: time) -> str:
    """
    Convert time object to record format string (HH:mm:ss).
    
    Args:
        t (datetime.time): Time object
        
    Returns:
        str: Record time string (e.g., "21:51:00")
    """
    return t.strftime(RECORD_TIME_FORMAT)

# Backward compatibility - deprecated, use parse_metadata_datetime instead
def parse_utc_datetime(value: Optional[str], format_str: str = METADATA_DATETIME_FORMAT) -> datetime:
    """
    DEPRECATED: Use parse_metadata_datetime instead.
    Parse UTC time string into a datetime object.
    
    Args:
        value (Optional[str]): UTC time string
        
    Returns:
        datetime: UTC datetime object
        
    Raises:
        ValueError: If parsing fails
    """
    import warnings
    warnings.warn("parse_utc_datetime is deprecated, use parse_metadata_datetime instead",
                  DeprecationWarning, stacklevel=2)
    return parse_metadata_datetime(value, format_str)

def count_of_nocodb_data(nocodb_data: Optional[Dict]) -> Optional[int]:
    """
    Count the number of NocoDB data items.
    
    Args:
        nocodb_data (list): NocoDB data list
        
    Returns:
        int: Number of data items, returns None if data is empty
    """
    if not nocodb_data:
        return None

    # Priority: get from pageInfo
    page_info = nocodb_data.get("pageInfo")
    if isinstance(page_info, Dict):
        total_rows = page_info.get("totalRows")
        if total_rows is not None:
            return total_rows

    # Fallback: calculate list length
    list_data = nocodb_data.get("list")
    if isinstance(list_data, List):
        return len(list_data)

    return None


def exact_match(search_text: str, target_text: str) -> bool:
    """
    Exact match: Check if search text exactly equals target text (case-sensitive).
    
    Args:
        search_text (str): Text to search for
        target_text (str): Target text
        
    Returns:
        bool: True if target text exactly equals search text (case-sensitive)
    """
    return search_text == target_text


def fuzzy_match(search_text: str, target_text: str) -> bool:
    """
    Fuzzy match: Check if search text is contained within target text (case-insensitive).
    
    Args:
        search_text (str): Text to search for
        target_text (str): Target text
        
    Returns:
        bool: True if target text contains search text (case-insensitive)
    """
    return search_text.lower() in target_text.lower()
