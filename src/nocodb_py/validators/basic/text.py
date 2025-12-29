"""
Text Column Validators

This module contains validators for text-based column types:
- SingleLineText: Single line text input
- LongText: Multi-line text input
"""

from typing import Any, Literal
from ...column import NocoDBColumnType, NocoDBColumn
from ..base import Validator, ValidationResult, ValidationLevel, register_validator


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
            # API → Python: ensure value is a string
            if not isinstance(value, str):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Expected string type for API data, got {type(value).__name__}",
                    converted_value=None,
                    value_type=value_type
                )
            converted_value = str(value)
            
        else:  # direction == "to_api"
            # Python → API: convert any type to string
            converted_value = str(value)
        
        # For FULL validation, could add additional checks (e.g., length constraints)
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
            # API → Python: ensure value is a string
            if not isinstance(value, str):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Expected string type for API data, got {type(value).__name__}",
                    converted_value=None,
                    value_type=value_type
                )
            converted_value = str(value)
            
        else:  # direction == "to_api"
            # Python → API: convert any type to string
            converted_value = str(value)
        
        # For FULL validation, could add additional checks (e.g., length constraints)
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