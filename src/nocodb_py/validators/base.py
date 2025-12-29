"""
Base Validator Classes and Registration System

This module contains the foundation classes for the NocoDB column validation system.
It includes the validation result container, validation levels, base validator class,
and the decorator-based registration system.
"""

from dataclasses import dataclass
from enum import Enum, auto
from functools import wraps
from typing import Any, Dict, Type, Optional, Union, Literal
from ..column import NocoDBColumnType, NocoDBColumn


@dataclass
class ValidationResult:
    """
    Validation result container with detailed information.
    
    Attributes:
        is_valid: Whether the validation passed
        error_message: Detailed error message if validation failed
        converted_value: The normalized/converted value
        value_type: The type of the converted value ("python" or "api")
    """
    is_valid: bool
    error_message: str = ""
    converted_value: Any = None
    value_type: Literal["python", "api"] = "python"


class ValidationLevel(Enum):
    """
    Validation levels for column data validation.
    
    Attributes:
        STRUCTURAL: Basic structural validation (type checking, format validation)
        FULL: Complete validation including contextual checks (network validation, etc.)
    """
    STRUCTURAL = auto()
    FULL = auto()


class Validator:
    """
    Base validator class for NocoDB column types.
    
    This class defines the interface for all column validators.
    Subclasses should implement validation logic for specific column types.
    """
    
    #pylint: disable=unused-argument
    def validate(self,
                value: Any,
                column: NocoDBColumn,
                level: ValidationLevel,
                direction: Literal["to_python", "to_api"] = "to_python") -> ValidationResult:
        """
        Unified validation and conversion method for column types.
        
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
        # Default implementation: always return valid result
        # Map direction to value_type: "to_python" -> "python", "to_api" -> "api"
        value_type = "python" if direction == "to_python" else "api"
        return ValidationResult(
            is_valid=True,
            error_message="",
            converted_value=value,
            value_type=value_type
        )


# Validator registry
VALIDATOR_REGISTRY: Dict[NocoDBColumnType, Type[Validator]] = {}


def register_validator(column_type: NocoDBColumnType):
    """
    Decorator for registering validators for specific column types.
    
    Args:
        column_type: The NocoDBColumnType to register the validator for
        
    Returns:
        Decorator function
    """
    def decorator(validator_class: Type[Validator]):
        VALIDATOR_REGISTRY[column_type] = validator_class
        return validator_class
    return decorator


def get_validator(column_type: NocoDBColumnType) -> Validator:
    """
    Get a validator instance for the specified column type.
    
    Args:
        column_type: The NocoDBColumnType to get a validator for
        
    Returns:
        Validator: An instance of the appropriate validator class
        
    Raises:
        ValueError: If no validator is registered for the column type
    """
    if column_type not in VALIDATOR_REGISTRY:
        raise ValueError(f"No validator registered for column type: {column_type}")
    
    validator_class = VALIDATOR_REGISTRY[column_type]
    return validator_class()


def validate_value(
    value: Any,
    column_type: NocoDBColumnType,
    column: Optional[Any] = None,
    level: ValidationLevel = ValidationLevel.STRUCTURAL,
    direction: Literal["to_python", "to_api"] = "to_python"
) -> ValidationResult:
    """
    Validate a value for a specific column type.
    
    Args:
        value: The value to validate
        column_type: The NocoDBColumnType to validate against
        column: Optional column instance for contextual validation
        level: The validation level to use
        direction: Conversion direction
            - "to_python": API data → Python internal object (with validation)
            - "to_api": Python object → API data format (validate format compatibility)
            
    Returns:
        ValidationResult: Detailed validation result with error message and converted value
    """
    # Check if column is read-only (this should be checked first)
    if column_type.is_read_only():
        return ValidationResult(
            is_valid=False,
            error_message="Cannot modify read-only column",
            converted_value=None,
            value_type="python" if direction == "to_python" else "api"
        )
    
    try:
        validator = get_validator(column_type)
    except ValueError:
        # If no validator is registered, return a valid result with the original value
        return ValidationResult(
            is_valid=True,
            error_message="",
            converted_value=value,
            value_type="python" if direction == "to_python" else "api"
        )
    
    # Use the unified validate method
    if column is None:
        # For validation without column context, create a minimal column info dict
        column_info = {"title": "temp", "uidt": column_type.value}
        # Create a simple object with column_info attribute
        column = type('SimpleColumn', (), {'column_info': column_info})()
    
    return validator.validate(value, column, level, direction)