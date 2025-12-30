"""
Datetime Column Validators

This module contains validators for datetime-based column types:
- Date: Date values (YYYY-MM-DD format)
- Time: Time values (HH:mm:ss format)
- DateTime: Datetime values (ISO 8601 format with timezone)
"""

import warnings
from datetime import date, time, datetime
from typing import Any, Literal, Optional
from ...column import NocoDBColumnType, NocoDBColumn
from ...utils import (
    parse_record_date,
    parse_record_time,
    parse_record_datetime,
    date_to_record_format,
    time_to_record_format,
    datetime_to_record_format
)
from ..base import Validator, ValidationResult, ValidationLevel, register_validator


@register_validator(NocoDBColumnType.DATE)
class DateValidator(Validator):
    """
    Validator for Date column type.
    
    Validates that the value is a date in YYYY-MM-DD format.
    Supports None values as valid input.
    """
    
    def validate(self,
                value: Any,
                column: Optional[NocoDBColumn],
                level: ValidationLevel = ValidationLevel.STRUCTURAL,
                direction: Literal["to_python", "to_api"] = "to_python") -> ValidationResult:
        """
        Unified validation and conversion for Date column type.
        
        Args:
            value: The value to validate and convert
            column: The NocoDBColumn instance for contextual information
            level: The validation level to use
            direction: Conversion direction
                - "to_python": API data → Python internal object (with validation)
                - "to_api": Python object → API data format (validate format compatibility)
                
        Returns:
            ValidationResult: Detailed validation result with converted value and value type
        """
        # Map direction to value_type: "to_python" -> "python", "to_api" -> "api"
        value_type = "python" if direction == "to_python" else "api"
        
        # Handle None value - Date supports None
        if value is None:
            return ValidationResult(
                is_valid=True,
                error_message="",
                converted_value=None,
                value_type=value_type
            )
        
        # Convert value based on direction
        if direction == "to_python":
            # API → Python: convert to date object
            if isinstance(value, date):
                # Already a date object
                if isinstance(value, datetime):
                    # Warn if datetime is provided (time component will be lost)
                    column_title = column.get_title() if column else 'unknown'
                    warnings.warn(
                        f"Date column '{column_title}' received datetime value {value}. "
                        f"Time component will be lost.",
                        UserWarning,
                        stacklevel=2
                    )
                    converted_value = value.date()
                else:
                    converted_value = value
            elif isinstance(value, str):
                # Parse string to date
                try:
                    converted_value = parse_record_date(value)
                except ValueError as e:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Failed to parse date string '{value}': {str(e)}",
                        converted_value=None,
                        value_type=value_type
                    )
            else:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Invalid type for date: {type(value).__name__}. Must be string or date object.",
                    converted_value=None,
                    value_type=value_type
                )
            
        elif direction == "to_api":
            # Python → API: convert to string
            if isinstance(value, date):
                # Convert date to string
                if isinstance(value, datetime):
                    # Warn if datetime is provided (time component will be lost)
                    column_title = column.get_title() if column else 'unknown'
                    warnings.warn(
                        f"Date column '{column_title}' received datetime value {value}. "
                        f"Time component will be lost.",
                        UserWarning,
                        stacklevel=2
                    )
                    converted_value = date_to_record_format(value.date())
                else:
                    converted_value = date_to_record_format(value)
            elif isinstance(value, str):
                # Validate string format
                try:
                    # Try to parse to validate format
                    parsed_date = parse_record_date(value)
                    # Re-format to ensure consistent output
                    converted_value = date_to_record_format(parsed_date)
                except ValueError as e:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Invalid date string format '{value}': {str(e)}",
                        converted_value=None,
                        value_type=value_type
                    )
            else:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Invalid type for date: {type(value).__name__}. Must be string or date object.",
                    converted_value=None,
                    value_type=value_type
                )
        else:
            # Invalid direction
            raise ValueError(f"Invalid direction: {direction}. Must be 'to_python' or 'to_api'")
        
        # For FULL validation, could add additional checks (e.g., range constraints)
        if level == ValidationLevel.FULL:
            # In a real implementation, this could check column constraints
            # For now, just return valid result
            pass
        
        return ValidationResult(
            is_valid=True,
            error_message="",
            converted_value=converted_value,
            value_type=value_type
        )


@register_validator(NocoDBColumnType.TIME)
class TimeValidator(Validator):
    """
    Validator for Time column type.
    
    Validates that the value is a time in HH:mm:ss format.
    Supports None values as valid input.
    """
    
    def validate(self,
                value: Any,
                column: Optional[NocoDBColumn],
                level: ValidationLevel = ValidationLevel.STRUCTURAL,
                direction: Literal["to_python", "to_api"] = "to_python") -> ValidationResult:
        """
        Unified validation and conversion for Time column type.
        
        Args:
            value: The value to validate and convert
            column: The NocoDBColumn instance for contextual information
            level: The validation level to use
            direction: Conversion direction
                - "to_python": API data → Python internal object (with validation)
                - "to_api": Python object → API data format (validate format compatibility)
                
        Returns:
            ValidationResult: Detailed validation result with converted value and value type
        """
        # Map direction to value_type: "to_python" -> "python", "to_api" -> "api"
        value_type = "python" if direction == "to_python" else "api"
        
        # Handle None value - Time supports None
        if value is None:
            return ValidationResult(
                is_valid=True,
                error_message="",
                converted_value=None,
                value_type=value_type
            )
        
        # Convert value based on direction
        if direction == "to_python":
            # API → Python: convert to time object
            if isinstance(value, time):
                # Already a time object
                converted_value = value
            elif isinstance(value, datetime):
                # Warn if datetime is provided (date component will be lost)
                column_title = column.get_title() if column else 'unknown'
                warnings.warn(
                    f"Time column '{column_title}' received datetime value {value}. "
                    f"Date component will be lost.",
                    UserWarning,
                    stacklevel=2
                )
                converted_value = value.time()
            elif isinstance(value, str):
                # Parse string to time
                try:
                    converted_value = parse_record_time(value)
                except ValueError as e:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Failed to parse time string '{value}': {str(e)}",
                        converted_value=None,
                        value_type=value_type
                    )
            else:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Invalid type for time: {type(value).__name__}. Must be string or time object.",
                    converted_value=None,
                    value_type=value_type
                )
            
        elif direction == "to_api":
            # Python → API: convert to string
            if isinstance(value, time):
                # Convert time to string
                converted_value = time_to_record_format(value)
            elif isinstance(value, datetime):
                # Warn if datetime is provided (date component will be lost)
                column_title = column.get_title() if column else 'unknown'
                warnings.warn(
                    f"Time column '{column_title}' received datetime value {value}. "
                    f"Date component will be lost.",
                    UserWarning,
                    stacklevel=2
                )
                converted_value = time_to_record_format(value.time())
            elif isinstance(value, str):
                # Validate string format
                try:
                    # Try to parse to validate format
                    parsed_time = parse_record_time(value)
                    # Re-format to ensure consistent output
                    converted_value = time_to_record_format(parsed_time)
                except ValueError as e:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Invalid time string format '{value}': {str(e)}",
                        converted_value=None,
                        value_type=value_type
                    )
            else:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Invalid type for time: {type(value).__name__}. Must be string or time object.",
                    converted_value=None,
                    value_type=value_type
                )
        else:
            # Invalid direction
            raise ValueError(f"Invalid direction: {direction}. Must be 'to_python' or 'to_api'")
        
        # For FULL validation, could add additional checks (e.g., range constraints)
        if level == ValidationLevel.FULL:
            # In a real implementation, this could check column constraints
            # For now, just return valid result
            pass
        
        return ValidationResult(
            is_valid=True,
            error_message="",
            converted_value=converted_value,
            value_type=value_type
        )


@register_validator(NocoDBColumnType.DATETIME)
class DateTimeValidator(Validator):
    """
    Validator for DateTime column type.
    
    Validates that the value is a datetime in ISO 8601 format with timezone.
    Supports None values as valid input.
    """
    
    def validate(self,
                value: Any,
                column: Optional[NocoDBColumn],
                level: ValidationLevel = ValidationLevel.STRUCTURAL,
                direction: Literal["to_python", "to_api"] = "to_python") -> ValidationResult:
        """
        Unified validation and conversion for DateTime column type.
        
        Args:
            value: The value to validate and convert
            column: The NocoDBColumn instance for contextual information
            level: The validation level to use
            direction: Conversion direction
                - "to_python": API data → Python internal object (with validation)
                - "to_api": Python object → API data format (validate format compatibility)
                
        Returns:
            ValidationResult: Detailed validation result with converted value and value type
        """
        # Map direction to value_type: "to_python" -> "python", "to_api" -> "api"
        value_type = "python" if direction == "to_python" else "api"
        
        # Handle None value - DateTime supports None
        if value is None:
            return ValidationResult(
                is_valid=True,
                error_message="",
                converted_value=None,
                value_type=value_type
            )
        
        # Convert value based on direction
        if direction == "to_python":
            # API → Python: convert to datetime object
            if isinstance(value, datetime):
                # Already a datetime object
                converted_value = value
            elif isinstance(value, str):
                # Parse string to datetime
                try:
                    converted_value = parse_record_datetime(value)
                except ValueError as e:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Failed to parse datetime string '{value}': {str(e)}",
                        converted_value=None,
                        value_type=value_type
                    )
            else:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Invalid type for datetime: {type(value).__name__}. Must be string or datetime object.",
                    converted_value=None,
                    value_type=value_type
                )
            
        elif direction == "to_api":
            # Python → API: convert to string
            if isinstance(value, datetime):
                # Convert datetime to string
                converted_value = datetime_to_record_format(value)
            elif isinstance(value, str):
                # Validate string format
                try:
                    # Try to parse to validate format
                    parsed_datetime = parse_record_datetime(value)
                    # Re-format to ensure consistent output
                    converted_value = datetime_to_record_format(parsed_datetime)
                except ValueError as e:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Invalid datetime string format '{value}': {str(e)}",
                        converted_value=None,
                        value_type=value_type
                    )
            else:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Invalid type for datetime: {type(value).__name__}. Must be string or datetime object.",
                    converted_value=None,
                    value_type=value_type
                )
        else:
            # Invalid direction
            raise ValueError(f"Invalid direction: {direction}. Must be 'to_python' or 'to_api'")
        
        # For FULL validation, could add additional checks (e.g., range constraints)
        if level == ValidationLevel.FULL:
            # In a real implementation, this could check column constraints
            # For now, just return valid result
            pass
        
        return ValidationResult(
            is_valid=True,
            error_message="",
            converted_value=converted_value,
            value_type=value_type
        )