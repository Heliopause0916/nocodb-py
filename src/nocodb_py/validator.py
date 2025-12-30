"""
NocoDB Column Validator Module

This module provides a flexible validation system for NocoDB column types.
It supports multiple validation levels and uses a decorator-based registration system
for maximum pluggability.

The validator system uses a unified validation approach with direction-aware conversion:
- "to_python": API data → Python internal object (with validation)
- "to_api": Python object → API data format (validate format compatibility)

Each validation returns a ValidationResult containing:
- is_valid: Whether validation passed
- error_message: Detailed error message if failed
- converted_value: The normalized/converted value
- value_type: The type of converted value ("python" or "api")

Note: This module now serves as the main entry point for the validator system.
All validators are organized in the validators/ subdirectory.
"""

# Import all validators from the organized structure
from .validators import (
    ValidationResult,
    ValidationLevel,
    Validator,
    register_validator,
    get_validator,
    validate_value,
    SingleLineTextValidator,
    LongTextValidator,
    DurationValidator
)

# Re-export for backward compatibility
__all__ = [
    'ValidationResult',
    'ValidationLevel',
    'Validator',
    'register_validator',
    'get_validator',
    'validate_value',
    'SingleLineTextValidator',
    'LongTextValidator',
    'DurationValidator'
]


# All validator classes and functions are now imported from the validators package
# This file serves as the main entry point for backward compatibility


# The validate_value function is now imported from the validators package
