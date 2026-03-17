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
Completeness validation check - validates presence (non-null) of values.
"""

from typing import Any, Dict, Optional

from ..utils import get_or_default
from ..base import BaseCheck, ValidationError
from ..data_quality_dimension import DataQualityDimension


class CompletenessCheck(BaseCheck):
    """Validates that a value is not null unless missing values are allowed"""

    _DEFAULT_MISSING_VALUES_ALLOWED = False

    def __init__(
        self, missing_values_allowed: Optional[bool] = _DEFAULT_MISSING_VALUES_ALLOWED
    ):
        """
        Initialize completeness check

        Args:
            missing_values_allowed: Whether None values are allowed
        """
        super().__init__(DataQualityDimension.COMPLETENESS)
        
        self.missing_values_allowed = get_or_default(
            missing_values_allowed, CompletenessCheck._DEFAULT_MISSING_VALUES_ALLOWED
        )

    def get_check_name(self) -> str:
        """Return check name"""
        return "completeness_check"

    def _is_empty(self, value: Any) -> bool:
        """Determine if value should be treated as empty"""
        if value is None:
            return True
        else:
            value_str = str(value)
            return len(value_str) == 0

    def validate(
        self, value: Any, context: Dict[str, Any]
    ) -> Optional[ValidationError]:
        """
        Validate completeness (null check)

        Args:
            value: The value to validate
            context: Context containing column_name, record, metadata

        Returns:
            ValidationError if validation fails, None if passes
        """
        column_name = context.get("column_name", "unknown")

        if self._is_empty(value) and not self.missing_values_allowed:
            return ValidationError(
                column_name=column_name,
                check_name=self.get_check_name(),
                message=f"{column_name} is missing (null or empty value not allowed)",
                value=value,
                expected="non-null value",
            )

        return None  # Validation passed

    def __repr__(self) -> str:
        return (
            f"CompletenessCheck("
            f"missing_values_allowed={self.missing_values_allowed})"
        )
