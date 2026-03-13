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
Range validation check
"""

from decimal import Decimal
from datetime import date, datetime
from typing import Any, Dict, Optional
from ..base import BaseCheck, ValidationError
from ..data_quality_dimension import DataQualityDimension


class RangeCheck(BaseCheck):
    """Validates that a value lies within a min/max range """

    def __init__(
        self,
        min_value: Optional[Any] = None,
        max_value: Optional[Any] = None
    ):
        """
        Initialize range check

        Args:
            min_value: Minimum allowed value (optional)
            max_value: Maximum allowed value (optional)
        """
        super().__init__(DataQualityDimension.VALIDITY)

        self.min_value = self._normalize(min_value)
        self.max_value = self._normalize(max_value)

        if self.min_value is None and self.max_value is None:
            raise ValueError("At least one of min_value or max_value must be specified")

        try:
            if self.min_value is not None and self.max_value is not None and self.min_value > self.max_value:
                raise ValueError(
                    f"min_value ({self.min_value}) cannot be greater than max_value ({self.max_value})"
                )
        except TypeError as e:
            raise TypeError(
                f"Incompatible types of min_value and max_value: {str(e)}"
            )

    def get_check_name(self) -> str:
        return "range_check"

    # Normalization
    def _normalize(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, (int, float, Decimal)):
            return Decimal(str(value))
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime(value.year, value.month, value.day)

        # String fallback
        return str(value)

    def validate(self, value: Any, context: Dict[str, Any]) -> Optional[ValidationError]:
        
        """
        Validate range

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
                message=f"{column_name} is None, cannot check to be within range",
                value=value
            )

        try:
            value_norm = self._normalize(value)
        except Exception:
            return ValidationError(
                column_name=column_name,
                check_name=self.get_check_name(),
                message=f"{column_name} value cannot be normalized",
                value=value
            )

        # Minimum check
        if self.min_value is not None:
            try:
                if value_norm < self.min_value:
                    return ValidationError(
                        column_name=column_name,
                        check_name=self.get_check_name(),
                        message=(
                            f"{column_name} ({value_norm}) is less than "
                            f"minimum ({self.min_value})"
                        ),
                        value=value,
                        expected=f">= {self.min_value}"
                    )
            except TypeError as e:
                return ValidationError(
                    column_name=column_name,
                    check_name=self.get_check_name(),
                    message=f"Cannot compare {type(value_norm).__name__} with min_value {type(self.min_value).__name__}: {str(e)}",
                    value=value
                )

        # Maximum check
        if self.max_value is not None:
            try:
                if value_norm > self.max_value:
                    return ValidationError(
                        column_name=column_name,
                        check_name=self.get_check_name(),
                        message=(
                            f"{column_name} ({value_norm}) is greater than "
                            f"maximum ({self.max_value})"
                        ),
                        value=value,
                        expected=f"<= {self.max_value}"
                    )
            except TypeError as e :
                return ValidationError(
                    column_name=column_name,
                    check_name=self.get_check_name(),
                    message=f"Cannot compare {type(value_norm).__name__} with max_value {type(self.max_value).__name__}: {str(e)}",
                    value=value
                )

        return None  # Validation passed

    def __repr__(self) -> str:
        return f"RangeCheck(min={self.min_value}, max={self.max_value})"
