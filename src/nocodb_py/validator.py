"""
NocoDB Column Validator Module

This module provides a flexible validation system for NocoDB column types.
It supports multiple validation levels and uses a decorator-based registration system
for maximum pluggability.
"""

from enum import Enum, auto
from functools import wraps
from typing import Any, Dict, Type, Optional, Union
from .column import NocoDBColumnType, NocoDBColumn


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
    
    def validate_structural(self, value: Any) -> bool:
        """
        Perform structural validation of the value.
        
        This includes basic type checking, format validation, and other
        structural constraints that don't require external context.
        
        Args:
            value: The value to validate
            
        Returns:
            bool: True if the value passes structural validation
        """
        return True
    
    def validate_contextual(self, value: Any, column: NocoDBColumn) -> bool:
        """
        Perform contextual validation of the value.
        
        This includes validation that requires external context, such as
        network requests to verify linked record existence.
        
        Args:
            value: The value to validate
            column: The NocoDBColumn instance for contextual information
            
        Returns:
            bool: True if the value passes contextual validation
        """
        return True
    
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
    
    def validate_structural(self, value: Any) -> bool:
        """
        Validate that the value is a string.
        
        Args:
            value: The value to validate
            
        Returns:
            bool: True if the value is a string
        """
        return isinstance(value, str)
    
    def validate_contextual(self, value: Any, column: NocoDBColumn) -> bool:
        """
        Perform contextual validation for SingleLineText.
        
        For SingleLineText, this could include checking against column constraints
        like maximum length, but currently returns True as basic validation is sufficient.
        
        Args:
            value: The value to validate
            column: The NocoDBColumn instance for contextual information
            
        Returns:
            bool: True if the value passes contextual validation
        """
        # In a real implementation, this could check column constraints
        # For now, return True as structural validation is sufficient
        return True
    
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
    column: Optional[NocoDBColumn] = None,
    level: ValidationLevel = ValidationLevel.STRUCTURAL,
    normalize: bool = False
) -> Union[bool, Any]:
    """
    Validate a value for a specific column type.
    
    Args:
        value: The value to validate
        column_type: The NocoDBColumnType to validate against
        column: Optional NocoDBColumn instance for contextual validation
        level: The validation level to use
        normalize: Whether to return the normalized value instead of validation result
        
    Returns:
        Union[bool, Any]: 
            If normalize=False: boolean validation result
            If normalize=True: normalized value (or None if validation fails)
    """
    try:
        validator = get_validator(column_type)
    except ValueError:
        # If no validator is registered, return True for validation or value for normalization
        return True if not normalize else value
    
    # Check if column is read-only
    if column_type.is_read_only():
        return False if not normalize else None
    
    # Perform validation based on level
    if level == ValidationLevel.STRUCTURAL:
        is_valid = validator.validate_structural(value)
    else:  # FULL validation
        structural_valid = validator.validate_structural(value)
        contextual_valid = validator.validate_contextual(value, column) if column else True
        is_valid = structural_valid and contextual_valid
    
    if normalize:
        if is_valid:
            return validator.normalize(value, column if level == ValidationLevel.FULL else None)
        else:
            return None
    else:
        return is_valid