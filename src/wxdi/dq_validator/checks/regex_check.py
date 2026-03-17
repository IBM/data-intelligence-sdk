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
Regex validation check - validates value matches a regular expression.
"""

import re
from typing import Any, Dict, Optional
from ..base import BaseCheck, ValidationError
from ..utils import get_or_default
from ..data_quality_dimension import DataQualityDimension


class RegexCheck(BaseCheck):
    """Validates that a value matches a regex pattern"""

    _DEFAULT_CASE_SENSITIVE = True

    def __init__(
        self, pattern: str = "", case_sensitive: bool = _DEFAULT_CASE_SENSITIVE
    ):
        """
        Initialize regex check

        Args:
            pattern: Regular expression pattern
            case_sensitive: Whether matching is case-sensitive
        """
        super().__init__(DataQualityDimension.VALIDITY)

        # Validate parameters
        if not isinstance(pattern, str) or not pattern:
            raise ValueError("pattern must be a non-empty string")

        self.pattern = pattern
        self.case_sensitive = get_or_default(
            case_sensitive, RegexCheck._DEFAULT_CASE_SENSITIVE
        )

        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            self._compiled_pattern = re.compile(pattern, flags)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{pattern}': {str(e)}")

    def get_check_name(self) -> str:
        """Return check name"""
        return "regex_check"

    def validate(
        self, value: Any, context: Dict[str, Any]
    ) -> Optional[ValidationError]:
        """
        Validate regex match

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
                message=f"{column_name} is None, cannot perform regex check",
                value=value,
            )

        value_str = str(value).strip()

        if not self._compiled_pattern.search(value_str):
            return ValidationError(
                column_name=column_name,
                check_name=self.get_check_name(),
                message=(
                    f"{column_name} ('{value_str}') does not match "
                    f"pattern '{self.pattern}'"
                ),
                value=value,
                expected=self.pattern,
            )

        return None  # Validation passed

    def __repr__(self) -> str:
        return (
            f"RegexCheck(pattern='{self.pattern}', "
            f"case_sensitive={self.case_sensitive})"
        )
