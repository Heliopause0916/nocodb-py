"""
NocoDB Validators Package

This package contains all column validators organized by category.
Validators are registered using the decorator-based registration system.

Categories:
- basic: Basic column types (text, numeric, datetime, boolean)
- selection: Selection types (single select, multi select)
- validation: Validation types (email, URL, phone number, currency)
- special: Special types (JSON, geometry, attachment, user)
- system: System types (ID, audit fields, computed fields)
"""

# Use relative imports
from .base import ValidationResult, ValidationLevel, Validator, register_validator, get_validator, validate_value

# Import basic validators
from .basic.text import SingleLineTextValidator, LongTextValidator
from .basic.numeric import NumberValidator, DecimalValidator, PercentValidator, RatingValidator
from .basic.checkbox import CheckboxValidator
from .basic.datetime import DateValidator, TimeValidator, DateTimeValidator, YearValidator
from .basic.duration import DurationValidator

__all__ = [
    'ValidationResult',
    'ValidationLevel',
    'Validator',
    'register_validator',
    'get_validator',
    'validate_value',
    'SingleLineTextValidator',
    'LongTextValidator',
    'NumberValidator',
    'DecimalValidator',
    'PercentValidator',
    'RatingValidator',
    'CheckboxValidator',
    'DateValidator',
    'TimeValidator',
    'DateTimeValidator',
    'YearValidator',
    'DurationValidator',
]