"""
Text Column Validators

This module contains validators for text-based column types:
- SingleLineText: Single line text input
- LongText: Multi-line text input
"""

from typing import Any, Literal
from ...column import NocoDBColumnType, NocoDBColumn
from ..base import Validator, ValidationResult, ValidationLevel, register_validator


def _convert_to_string(value: Any, direction: Literal["to_python", "to_api"], value_type: Literal["python", "api"]) -> ValidationResult:
    """
    Internal helper function to convert value to string with error handling.
    
    Args:
        value: The value to convert
        direction: Conversion direction
        value_type: The target value type ("python" or "api")
        
    Returns:
        ValidationResult: Result containing converted value or error message
    """
    # Handle None value
    if value is None:
        return ValidationResult(
            is_valid=True,
            error_message="",
            converted_value=None,
            value_type=value_type
        )
    
    # Convert value to string based on direction
    if direction == "to_python":
        # API → Python: try to convert any type to string
        try:
            converted_value = str(value)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"Failed to convert value to string: {str(e)}",
                converted_value=None,
                value_type=value_type
            )
        
    elif direction == "to_api":
        # Python → API: try to convert any type to string
        try:
            converted_value = str(value)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"Failed to convert value to string: {str(e)}",
                converted_value=None,
                value_type=value_type
            )
        
    else:
        # Invalid direction
        raise ValueError(f"Invalid direction: {direction}. Must be 'to_python' or 'to_api'")
    
    return ValidationResult(
        is_valid=True,
        error_message="",
        converted_value=converted_value,
        value_type=value_type
    )


@register_validator(NocoDBColumnType.SINGLE_LINE_TEXT)
class SingleLineTextValidator(Validator):
    """
    Validator for SingleLineText column type.
    
    Validates that the value is a string and optionally checks length constraints.
    """
    
    def validate(self,
                value: Any,
                column: NocoDBColumn,
                level: ValidationLevel,
                direction: Literal["to_python", "to_api"] = "to_python") -> ValidationResult:
        """
        Unified validation and conversion for SingleLineText column type.
        
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
        
        # Use helper function for string conversion
        result = _convert_to_string(value, direction, value_type)
        
        # If conversion failed, return the error result
        if not result.is_valid:
            return result
        
        # For FULL validation, could add additional checks (e.g., length constraints)
        if level == ValidationLevel.FULL:
            # In a real implementation, this could check column constraints
            # For now, just return valid result
            pass
        
        return result


@register_validator(NocoDBColumnType.LONG_TEXT)
class LongTextValidator(Validator):
    """
    Validator for LongText column type.
    
    Validates that the value is a string. LongText supports multi-line content.
    """
    
    def validate(self,
                value: Any,
                column: NocoDBColumn,
                level: ValidationLevel,
                direction: Literal["to_python", "to_api"] = "to_python") -> ValidationResult:
        """
        Unified validation and conversion for LongText column type.
        
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
        
        # Use helper function for string conversion
        result = _convert_to_string(value, direction, value_type)
        
        # If conversion failed, return the error result
        if not result.is_valid:
            return result
        
        # For FULL validation, could add additional checks (e.g., length constraints)
        if level == ValidationLevel.FULL:
            # In a real implementation, this could check column constraints
            # For now, just return valid result
            pass
        
        return result