# Copyright 2026 IBM Corporation
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0);
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# See the LICENSE file in the project root for license information.

"""
Valid values validation check - validates value is in allowed list with optional case-insensitive comparison.
"""

from typing import List, Any, Dict, Optional, Set
from ..base import BaseCheck, ValidationError
from ..utils import get_or_default
from ..data_quality_dimension import DataQualityDimension


class ValidValuesCheck(BaseCheck):
    """Validates value is in allowed list with optional case-insensitive comparison"""

    _DEFAULT_CASE_SENSITIVE = False

    def __init__(
        self, valid_values: List[Any], case_sensitive: bool = _DEFAULT_CASE_SENSITIVE
    ):
        """
        Initialize valid values check

        Args:
            valid_values: List of allowed values
            case_sensitive: If False (default), string comparisons are case-insensitive.
                          If True, exact match required.

        Raises:
            ValueError: If valid_values is invalid
        """
        super().__init__(DataQualityDimension.VALIDITY)
        
        # Validate parameters
        if not isinstance(valid_values, list):
            raise TypeError(
                f"valid_values must be a list, got {type(valid_values).__name__}"
            )

        if len(valid_values) == 0:
            raise ValueError("valid_values cannot be empty")

        self.valid_values = valid_values
        self.case_sensitive = get_or_default(
            case_sensitive, ValidValuesCheck._DEFAULT_CASE_SENSITIVE
        )

        # Create lookup structures
        if case_sensitive:
            # Use set for O(1) lookup
            self._valid_set: Set[Any] = set(valid_values)
            self._lowercase_map: Dict[str, Any] = {}
        else:
            # For case-insensitive, create lowercase mapping for strings
            self._valid_set = set()
            self._lowercase_map = {}  # Maps lowercase to original values

            for val in valid_values:
                if isinstance(val, str):
                    lower_val = val.lower()
                    self._lowercase_map[lower_val] = val
                    self._valid_set.add(lower_val)
                else:
                    self._valid_set.add(val)

    def get_check_name(self) -> str:
        """Return check name"""
        return "valid_values_check"

    def validate(
        self, value: Any, context: Dict[str, Any]
    ) -> Optional[ValidationError]:
        """
        Validate value is in allowed list

        Args:
            value: The value to validate
            context: Context containing column_name, record, metadata

        Returns:
            ValidationError if validation fails, None if passes
        """
        column_name = context.get("column_name", "unknown")

        # Check if value is None
        if value is None:
            return ValidationError(
                column_name=column_name,
                check_name=self.get_check_name(),
                message=f"{column_name} is None, expected one of: {self.valid_values}",
                value=value,
                expected=self.valid_values,
            )

        # Check if value is in valid list
        is_valid = False

        if self.case_sensitive:
            # Case-sensitive comparison
            is_valid = value in self._valid_set
        else:
            # Case-insensitive comparison for strings, exact for others
            if isinstance(value, str):
                is_valid = value.lower() in self._valid_set
            else:
                is_valid = value in self._valid_set

        if not is_valid:
            case_note = (
                " (case-insensitive)"
                if not self.case_sensitive and isinstance(value, str)
                else ""
            )
            return ValidationError(
                column_name=column_name,
                check_name=self.get_check_name(),
                message=f"{column_name} has invalid value '{value}'{case_note}. Valid values: {self.valid_values}",
                value=value,
                expected=self.valid_values,
            )

        return None  # Validation passed

    def __repr__(self) -> str:
        return f"ValidValuesCheck(values={len(self.valid_values)}, case_sensitive={self.case_sensitive})"
