"""
Checkbox Column Validator

This module contains the validator for Checkbox column type.
Checkbox represents boolean values (true/false) in NocoDB.
"""

import warnings
from typing import Any, Literal, Optional
from ...column import NocoDBColumnType, NocoDBColumn
from ..base import Validator, ValidationResult, ValidationLevel, register_validator


@register_validator(NocoDBColumnType.CHECKBOX)
class CheckboxValidator(Validator):
    """
    Validator for Checkbox column type.
    
    Validates that the value is a boolean or integer (0/1).
    Supports None values as valid input, which are converted to 0 in to_api direction.
    """
    
    def validate(self,
                value: Any,
                column: Optional[NocoDBColumn],
                level: ValidationLevel = ValidationLevel.STRUCTURAL,
                direction: Literal["to_python", "to_api"] = "to_python") -> ValidationResult:
        """
        Unified validation and conversion for Checkbox column type.
        
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
        
        # Handle None value - Checkbox supports None, but converts to 0 in to_api direction
        if value is None:
            if direction == "to_api":
                # Convert None to 0 (unchecked) for API compatibility
                return ValidationResult(
                    is_valid=True,
                    error_message="",
                    converted_value=0,
                    value_type=value_type
                )
            else:
                # Keep None for Python representation
                return ValidationResult(
                    is_valid=True,
                    error_message="",
                    converted_value=None,
                    value_type=value_type
                )
        
        # Convert value based on direction
        if direction == "to_python":
            # API → Python: convert to boolean
            if isinstance(value, bool):
                # Already boolean, use as-is
                converted_value = value
            elif isinstance(value, int):
                # Integer 0/1 → boolean
                if value == 0:
                    converted_value = False
                elif value == 1:
                    converted_value = True
                else:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Invalid integer value for checkbox: {value}. Must be 0 or 1.",
                        converted_value=None,
                        value_type=value_type
                    )
            else:
                # Try to convert string or other types
                try:
                    # Handle string representations
                    if isinstance(value, str):
                        value_lower = value.lower().strip()
                        if value_lower in ('true', '1', 'yes', 'y', 't'):
                            converted_value = True
                        elif value_lower in ('false', '0', 'no', 'n', 'f'):
                            converted_value = False
                        else:
                            raise ValueError(f"Invalid string value for checkbox: {value}")
                    else:
                        # Reject float and other non-integer types
                        return ValidationResult(
                            is_valid=False,
                            error_message=f"Invalid type for checkbox: {type(value).__name__}. Must be boolean, integer (0/1), or string.",
                            converted_value=None,
                            value_type=value_type
                        )
                except (ValueError, TypeError) as e:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Failed to convert value to checkbox: {str(e)}",
                        converted_value=None,
                        value_type=value_type
                    )
            
        elif direction == "to_api":
            # Python → API: convert to integer 0/1
            if isinstance(value, bool):
                # Boolean → integer
                converted_value = 1 if value else 0
            elif isinstance(value, int):
                # Integer 0/1 → keep as-is
                if value == 0 or value == 1:
                    converted_value = value
                else:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Invalid integer value for checkbox: {value}. Must be 0 or 1.",
                        converted_value=None,
                        value_type=value_type
                    )
            else:
                # Try to convert to boolean first, then to integer
                try:
                    if isinstance(value, str):
                        value_lower = value.lower().strip()
                        if value_lower in ('true', '1', 'yes', 'y', 't'):
                            converted_value = 1
                        elif value_lower in ('false', '0', 'no', 'n', 'f'):
                            converted_value = 0
                        else:
                            raise ValueError(f"Invalid string value for checkbox: {value}")
                    else:
                        # Reject float and other non-integer types
                        return ValidationResult(
                            is_valid=False,
                            error_message=f"Invalid type for checkbox: {type(value).__name__}. Must be boolean, integer (0/1), or string.",
                            converted_value=None,
                            value_type=value_type
                        )
                except (ValueError, TypeError) as e:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Failed to convert value to checkbox: {str(e)}",
                        converted_value=None,
                        value_type=value_type
                    )
        else:
            # Invalid direction
            raise ValueError(f"Invalid direction: {direction}. Must be 'to_python' or 'to_api'")
        
        # For FULL validation, could add additional checks (e.g., column constraints)
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
