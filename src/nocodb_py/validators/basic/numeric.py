"""
Numeric Column Validators

This module contains validators for numeric column types:
- Number: Integer and floating-point numbers
- Decimal: High-precision decimal numbers
"""

import warnings
from typing import Any, Literal, Optional
from ...column import NocoDBColumnType, NocoDBColumn
from ..base import Validator, ValidationResult, ValidationLevel, register_validator


@register_validator(NocoDBColumnType.NUMBER)
class NumberValidator(Validator):
    """
    Validator for Number column type.
    
    Validates that the value is a numeric type, primarily handling integers.
    Supports None values as valid input.
    """
    
    def validate(self,
                value: Any,
                column: Optional[NocoDBColumn],
                level: ValidationLevel = ValidationLevel.STRUCTURAL,
                direction: Literal["to_python", "to_api"] = "to_python") -> ValidationResult:
        """
        Unified validation and conversion for Number column type.
        
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
        
        # Handle None value - Number supports None
        if value is None:
            return ValidationResult(
                is_valid=True,
                error_message="",
                converted_value=None,
                value_type=value_type
            )
        
        # Convert value based on direction
        if direction == "to_python":
            # API → Python: try to convert to appropriate numeric type
            if isinstance(value, (int, float)):
                # If already a numeric type, use as-is
                converted_value = value
                # Warn if float has decimal part (not integer)
                if isinstance(value, float) and not value.is_integer():
                    column_title = column.get_title() if column else 'unknown'
                    warnings.warn(
                        f"Number column '{column_title}' received float value {value} "
                        f"that will be stored as float. Consider using Decimal type for precise decimal values.",
                        UserWarning,
                        stacklevel=2
                    )
            else:
                # For non-numeric types, try conversion
                try:
                    # First try to convert to integer (preferred for Number type)
                    try:
                        converted_value = int(value)
                    except (ValueError, TypeError):
                        # If integer conversion fails, try float
                        converted_value = float(value)
                        # Warn about precision loss if float has decimal part
                        if not converted_value.is_integer():
                            column_title = column.get_title() if column else 'unknown'
                            warnings.warn(
                                f"Number column '{column_title}' received value {value} "
                                f"that will be stored as float. Consider using Decimal type for precise decimal values.",
                                UserWarning,
                                stacklevel=2
                            )
                except (ValueError, TypeError) as e:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Failed to convert value to number: {str(e)}",
                        converted_value=None,
                        value_type=value_type
                    )
            
        elif direction == "to_api":
            # Python → API: ensure value is numeric
            if not isinstance(value, (int, float)):
                try:
                    # Try to convert to appropriate numeric type
                    try:
                        converted_value = int(value)
                    except (ValueError, TypeError):
                        converted_value = float(value)
                except (ValueError, TypeError) as e:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Failed to convert value to number: {str(e)}",
                        converted_value=None,
                        value_type=value_type
                    )
            else:
                converted_value = value
                
        else:
            # Invalid direction
            raise ValueError(f"Invalid direction: {direction}. Must be 'to_python' or 'to_api'")
        
        # For FULL validation, could add additional checks (e.g., range constraints)
        if level == ValidationLevel.FULL and column:
            # In a real implementation, this could check column constraints
            # For now, just return valid result
            pass
        
        return ValidationResult(
            is_valid=True,
            error_message="",
            converted_value=converted_value,
            value_type=value_type
        )


@register_validator(NocoDBColumnType.DECIMAL)
class DecimalValidator(Validator):
    """
    Validator for Decimal column type.
    
    Validates that the value is a numeric type suitable for decimal precision.
    Supports None values as valid input.
    """
    
    def validate(self,
                value: Any,
                column: Optional[NocoDBColumn],
                level: ValidationLevel = ValidationLevel.STRUCTURAL,
                direction: Literal["to_python", "to_api"] = "to_python") -> ValidationResult:
        """
        Unified validation and conversion for Decimal column type.
        
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
        
        # Handle None value - Decimal supports None
        if value is None:
            return ValidationResult(
                is_valid=True,
                error_message="",
                converted_value=None,
                value_type=value_type
            )
        
        # Convert value based on direction
        if direction == "to_python":
            # API → Python: try to convert to float for decimal precision
            try:
                converted_value = float(value)
                # Warn if integer value is used for Decimal type
                if converted_value.is_integer():
                    column_title = column.get_title() if column else 'unknown'
                    warnings.warn(
                        f"Decimal column '{column_title}' received integer value {value}. "
                        f"Consider using Number type for integer values.",
                        UserWarning,
                        stacklevel=2
                    )
            except (ValueError, TypeError) as e:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Failed to convert value to decimal: {str(e)}",
                    converted_value=None,
                    value_type=value_type
                )
            
        elif direction == "to_api":
            # Python → API: ensure value is numeric
            if not isinstance(value, (int, float)):
                try:
                    converted_value = float(value)
                except (ValueError, TypeError) as e:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Failed to convert value to decimal: {str(e)}",
                        converted_value=None,
                        value_type=value_type
                    )
            else:
                converted_value = value
                
        else:
            # Invalid direction
            raise ValueError(f"Invalid direction: {direction}. Must be 'to_python' or 'to_api'")
        
        # For FULL validation, could add additional checks (e.g., precision constraints)
        if level == ValidationLevel.FULL and column:
            # In a real implementation, this could check decimal precision constraints
            # For now, just return valid result
            pass
        
        return ValidationResult(
            is_valid=True,
            error_message="",
            converted_value=converted_value,
            value_type=value_type
        )
