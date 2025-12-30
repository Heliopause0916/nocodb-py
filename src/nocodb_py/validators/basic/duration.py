"""
Duration Column Validator

This module contains the validator for Duration column type.
Duration values are stored as seconds with 4 decimal places precision in JSON string format.
Supports time format parsing (HH:MM:SS.sss, HH:MM:SS, HH:MM, MM:SS) and range validation.
"""

from typing import Any, Literal, Optional
from ...column import NocoDBColumnType, NocoDBColumn
from ..base import Validator, ValidationResult, ValidationLevel, register_validator


def parse_time_format(time_str: str) -> float:
    """
    Parse time format string to seconds (supports fractional seconds).

    Supported formats:
    - HH:MM:SS.sss, HH:MM:SS.ss, HH:MM:SS.s (with fractional seconds)
    - HH:MM:SS (standard time format)
    - HH:MM (hours and minutes)
    - MM:SS (minutes and seconds)
    - Pure numeric (treated as seconds)

    Args:
        time_str: Time string to parse

    Returns:
        float: Total seconds with fractional part

    Raises:
        ValueError: If the string cannot be parsed
    """
    # Remove any surrounding whitespace
    time_str = time_str.strip()

    # Check if it's a pure number (no colons)
    if ':' not in time_str:
        return float(time_str)

    parts = time_str.split(':')

    if len(parts) == 3:  # HH:MM:SS[.sss]
        try:
            hours = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])  # Automatically handles fractional seconds
            return hours * 3600 + minutes * 60 + seconds
        except ValueError as e:
            raise ValueError(f"Invalid time format: {time_str}") from e

    elif len(parts) == 2:  # HH:MM or MM:SS
        try:
            first_part = float(parts[0])
            second_part = float(parts[1])

            # Determine format based on first part value
            if first_part < 24:  # Likely HH:MM (hours should be < 24)
                return first_part * 3600 + second_part * 60
            # Likely MM:SS (minutes can be >= 60)
            return first_part * 60 + second_part

        except ValueError as e:
            raise ValueError(f"Invalid time format: {time_str}") from e

    # Invalid number of parts
    raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM:SS, HH:MM, or MM:SS")


@register_validator(NocoDBColumnType.DURATION)
class DurationValidator(Validator):
    """
    Validator for Duration column type.

    Duration values are stored as seconds with 4 decimal places precision in JSON string format.
    Supports time format parsing and non-negative value validation.

    Key features:
    - Converts between API string format and Python float
    - Supports time format parsing (HH:MM:SS.sss, HH:MM:SS, HH:MM, MM:SS)
    - Validates non-negative values (FULL validation level)
    - Handles NULL values appropriately
    """

    def validate(self,
                value: Any,
                column: Optional[NocoDBColumn],
                level: ValidationLevel = ValidationLevel.STRUCTURAL,
                direction: Literal["to_python", "to_api"] = "to_python") -> ValidationResult:
        """
        Unified validation and conversion for Duration column type.

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

        # Handle None value - Duration supports None
        if value is None:
            return ValidationResult(
                is_valid=True,
                error_message="",
                converted_value=None,
                value_type=value_type
            )

        # Convert value based on direction
        if direction == "to_python":
            return self._validate_to_python(value, column, level, value_type)
        if direction == "to_api":
            return self._validate_to_api(value, column, level, value_type)
        # Invalid direction
        raise ValueError(f"Invalid direction: {direction}. Must be 'to_python' or 'to_api'")

    def _validate_to_python(self, value: Any, column: Optional[NocoDBColumn],  # pylint: disable=unused-argument
                          level: ValidationLevel, value_type: Literal["python", "api"]) -> ValidationResult:
        """Validate and convert value in to_python direction."""
        # API → Python: convert string to float, handling time formats
        if isinstance(value, (int, float)):
            # If already a numeric type, use as-is
            converted_value = float(value)
        elif isinstance(value, str):
            # Handle string values - try time format parsing first
            try:
                converted_value = parse_time_format(value)
            except ValueError:
                # If time format parsing fails, try direct conversion
                try:
                    converted_value = float(value)
                except ValueError as e:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Failed to convert value to duration: {str(e)}",
                        converted_value=None,
                        value_type=value_type
                    )
        else:
            # For other types, try conversion
            try:
                converted_value = float(value)
            except (ValueError, TypeError) as e:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Failed to convert value to duration: {str(e)}",
                    converted_value=None,
                    value_type=value_type
                )

        return self._apply_range_validation(converted_value, level, value_type)

    def _validate_to_api(self, value: Any, column: Optional[NocoDBColumn],  # pylint: disable=unused-argument
                        level: ValidationLevel, value_type: Literal["python", "api"]) -> ValidationResult:
        """Validate and convert value in to_api direction."""
        # Python → API: convert to string with 4 decimal places precision
        if isinstance(value, (int, float)):
            # Format with 4 decimal places
            converted_value = f"{float(value):.4f}"
        elif isinstance(value, str):
            # If it's already a string, validate it's a valid duration format
            try:
                # Parse to validate, then format with 4 decimal places
                parsed_value = parse_time_format(value)
                converted_value = f"{parsed_value:.4f}"
            except ValueError as e:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Invalid duration format: {str(e)}",
                    converted_value=None,
                    value_type=value_type
                )
        else:
            # For other types, try conversion
            try:
                parsed_value = float(value)
                converted_value = f"{parsed_value:.4f}"
            except (ValueError, TypeError) as e:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Failed to convert value to duration: {str(e)}",
                    converted_value=None,
                    value_type=value_type
                )

        return self._apply_range_validation(converted_value, level, value_type)

    def _apply_range_validation(self, converted_value: Any, level: ValidationLevel,
                               value_type: Literal["python", "api"]) -> ValidationResult:
        """Apply range validation if needed."""
        # Range validation (non-negative check) - only at FULL level
        if level == ValidationLevel.FULL and converted_value is not None:
            if converted_value < 0:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Duration value must be non-negative, got {converted_value}",
                    converted_value=None,
                    value_type=value_type
                )

        return ValidationResult(
            is_valid=True,
            error_message="",
            converted_value=converted_value,
            value_type=value_type
        )
