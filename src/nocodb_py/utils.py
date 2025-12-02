"""
Filename: src/nocodb_py/utils.py

Utility functions for NocoDB Python client
This module provides utility functions for handling NocoDB data
"""

from datetime import datetime, timezone
from typing import Optional

# 支持的时间格式常量
UTC_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# UNIX 时间戳 0 对应的 UTC 时间
EPOCH_ZERO = datetime.fromtimestamp(0, tz=timezone.utc)

def parse_utc_datetime(value: Optional[str], format_str: str = UTC_DATETIME_FORMAT) -> datetime:
    """
    解析UTC时间字符串为datetime对象
    如果解析失败，则返回UNIX时间戳0对应的UTC时间
    
    Args:
        value (Optional[str]): UTC时间字符串
        
    Returns:
        datetime: UTC时间对象，如果解析失败则返回UNIX时间戳0对应的UTC时间
    """

    if not value:
        return EPOCH_ZERO
    try:
        naive_dt = datetime.strptime(value, format_str)
        return naive_dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return EPOCH_ZERO


