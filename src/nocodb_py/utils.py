"""
Filename: src/nocodb_py/utils.py

Utility functions for NocoDB Python client
This module provides utility functions for handling NocoDB data
"""

# pylint: disable=too-many-instance-attributes
# pylint: disable=trailing-whitespace
# pylint: disable=line-too-long

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Supported time format constants
UTC_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# UTC time corresponding to UNIX timestamp 0
EPOCH_ZERO = datetime.fromtimestamp(0, tz=timezone.utc)

def parse_utc_datetime(value: Optional[str], format_str: str = UTC_DATETIME_FORMAT) -> datetime:
    """
    Parse UTC time string into a datetime object.
    If parsing fails, returns UTC time corresponding to UNIX timestamp 0.
    
    Args:
        value (Optional[str]): UTC time string
        
    Returns:
        datetime: UTC datetime object, returns UTC time corresponding to UNIX timestamp 0 if parsing fails
    """

    if not value:
        return EPOCH_ZERO
    try:
        naive_dt = datetime.strptime(value, format_str)
        return naive_dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return EPOCH_ZERO

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
