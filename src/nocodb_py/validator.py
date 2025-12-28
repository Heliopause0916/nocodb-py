"""
NocoDB Column Validator Module

This module provides a flexible validation system for NocoDB column types.
It supports multiple validation levels and uses a decorator-based registration system
for maximum pluggability.
"""

from dataclasses import dataclass
from enum import Enum, auto
from functools import wraps
from typing import Any, Dict, Type, Optional, Union
from .column import NocoDBColumnType, NocoDBColumn


@dataclass
class ValidationResult:
    """
    Validation result container with detailed information.
    
    Attributes:
        is_valid: Whether the validation passed
        error_message: Detailed error message if validation failed
        converted_value: The normalized/converted value
    """
    is_valid: bool
    error_message: str = ""
    converted_value: Any = None


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
    def validate(self, value: Any, column: NocoDBColumn, level: ValidationLevel) -> ValidationResult:
        """
        Validate a value for the column type.
        
        Args:
            value: The value to validate
            column: The NocoDBColumn instance for contextual information
            level: The validation level to use
            
        Returns:
            ValidationResult: Detailed validation result
        """
        # Default implementation: always return valid result
        return ValidationResult(
            is_valid=True,
            error_message="",
            converted_value=value
        )
    
    def convert(self, value: Any, column: NocoDBColumn) -> Any:
        """
        Convert the value to the expected format for the column type.
        
        Args:
            value: The value to convert
            column: The NocoDBColumn instance for contextual information
            
        Returns:
            Any: The converted value
        """
        return value
    
    def normalize(self, value: Any, column: Optional[NocoDBColumn] = None) -> Any:
        """
        Normalize the value to the expected format for the column type.
        
        Args:
            value: The value to normalize
            column: Optional column context for normalization
            
        Returns:
            Any: The normalized value
        """
        return value


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


@register_validator(NocoDBColumnType.SINGLE_LINE_TEXT)
class SingleLineTextValidator(Validator):
    """
    Validator for SingleLineText column type.
    
    Validates that the value is a string and optionally checks length constraints.
    """
    
    def validate(self, value: Any, column: NocoDBColumn, level: ValidationLevel) -> ValidationResult:
        """
        Validate a value for SingleLineText column type.
        
        Args:
            value: The value to validate
            column: The NocoDBColumn instance for contextual information
            level: The validation level to use
            
        Returns:
            ValidationResult: Detailed validation result
        """
        # Structural validation: check if value is a string
        if not isinstance(value, str):
            return ValidationResult(
                is_valid=False,
                error_message=f"Expected string type, got {type(value).__name__}",
                converted_value=None
            )
        
        # For FULL validation, could add additional checks (e.g., length constraints)
        if level == ValidationLevel.FULL:
            # In a real implementation, this could check column constraints
            # For now, just return valid result
            pass
        
        # Convert and return valid result
        converted_value = self.convert(value, column)
        return ValidationResult(
            is_valid=True,
            error_message="",
            converted_value=converted_value
        )
    
    def convert(self, value: Any, column: NocoDBColumn) -> Any:
        """
        Convert the value to a string.
        
        Args:
            value: The value to convert
            column: The NocoDBColumn instance for contextual information
            
        Returns:
            str: The converted string value, or None if value is None
        """
        if value is None:
            return None
        return str(value)
    
    def normalize(self, value: Any, column: Optional[NocoDBColumn] = None) -> Any:
        """
        Normalize the value to a string.
        
        Args:
            value: The value to normalize
            column: Optional column context (not used for SingleLineText)
            
        Returns:
            str: The normalized string value, or None if value is None
        """
        if value is None:
            return None
        return str(value)


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
    level: ValidationLevel = ValidationLevel.STRUCTURAL
) -> ValidationResult:
    """
    Validate a value for a specific column type.
    
    Args:
        value: The value to validate
        column_type: The NocoDBColumnType to validate against
        column: Optional column instance for contextual validation
        level: The validation level to use
        
    Returns:
        ValidationResult: Detailed validation result with error message and converted value
    """
    # Check if column is read-only (this should be checked first)
    if column_type.is_read_only():
        return ValidationResult(
            is_valid=False,
            error_message="Cannot modify read-only column",
            converted_value=None
        )
    
    try:
        validator = get_validator(column_type)
    except ValueError:
        # If no validator is registered, return a valid result with the original value
        return ValidationResult(
            is_valid=True,
            error_message="",
            converted_value=value
        )
    
    # Use the unified validate method
    if column is None:
        # For validation without column context, create a minimal column info dict
        column_info = {"title": "temp", "uidt": column_type.value}
        # Create a simple object with column_info attribute
        column = type('SimpleColumn', (), {'column_info': column_info})()
    
    return validator.validate(value, column, level)
