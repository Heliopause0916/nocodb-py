"""
Filename: src/nocodb_py/utils.py

Utility functions for NocoDB Python client
This module provides utility functions for handling NocoDB data
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

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

def count_of_nocodb_data(nocodb_data: Optional[Dict]) -> Optional[int]:
    """
    计算nocodb数据的条数
    
    Args:
        nocodb_data (list): nocodb数据列表
        
    Returns:
        int: 数据条数，如果数据为空则返回None
    """
    if not nocodb_data:
        return None

    # 优先从 pageInfo 获取
    page_info = nocodb_data.get("pageInfo")
    if isinstance(page_info, Dict):
        total_rows = page_info.get("totalRows")
        if total_rows is not None:
            return total_rows

    # 备用方案：计算 list 长度
    list_data = nocodb_data.get("list")
    if isinstance(list_data, List):
        return len(list_data)

    return None
