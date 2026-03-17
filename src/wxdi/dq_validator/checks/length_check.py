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
Length validation check - validates length of any value (converted to string).
"""

from typing import Optional, Any, Dict
from ..base import BaseCheck, ValidationError
from ..data_quality_dimension import DataQualityDimension


class LengthCheck(BaseCheck):
    """Validates length of any value (converted to string) is within min/max bounds"""
    
    def __init__(
        self,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None
    ):
        """
        Initialize length check
        
        Args:
            min_length: Minimum allowed length (inclusive), None means no minimum
            max_length: Maximum allowed length (inclusive), None means no maximum
        
        Raises:
            ValueError: If parameters are invalid
        """
        super().__init__(DataQualityDimension.VALIDITY)
        
        # Validate parameters
        if min_length is None and max_length is None:
            raise ValueError("At least one of min_length or max_length must be specified")
        
        if min_length is not None and min_length < 0:
            raise ValueError(f"min_length cannot be negative, got {min_length}")
        
        if max_length is not None and max_length < 0:
            raise ValueError(f"max_length cannot be negative, got {max_length}")
        
        if min_length is not None and max_length is not None and min_length > max_length:
            raise ValueError(f"min_length ({min_length}) cannot be greater than max_length ({max_length})")
        
        self.min_length = min_length
        self.max_length = max_length
    
    def get_check_name(self) -> str:
        """Return check name"""
        return "length_check"
    
    def validate(self, value: Any, context: Dict[str, Any]) -> Optional[ValidationError]:
        """
        Validate length of value (converted to string)
        
        Args:
            value: The value to validate (will be converted to string)
            context: Context containing column_name, record, metadata
        
        Returns:
            ValidationError if validation fails, None if passes
        """
        column_name = context.get('column_name', 'unknown')
        
        # Check if value is None
        if value is None:
            return ValidationError(
                column_name=column_name,
                check_name=self.get_check_name(),
                message=f"{column_name} is None, cannot check length",
                value=value
            )
        
        # Convert value to string and get length
        str_value = str(value)
        actual_length = len(str_value)
        
        # Check minimum length
        if self.min_length is not None and actual_length < self.min_length:
            return ValidationError(
                column_name=column_name,
                check_name=self.get_check_name(),
                message=f"{column_name} length ({actual_length}) is less than minimum ({self.min_length})",
                value=value,
                expected=f"length >= {self.min_length}"
            )
        
        # Check maximum length
        if self.max_length is not None and actual_length > self.max_length:
            return ValidationError(
                column_name=column_name,
                check_name=self.get_check_name(),
                message=f"{column_name} length ({actual_length}) exceeds maximum ({self.max_length})",
                value=value,
                expected=f"length <= {self.max_length}"
            )
        
        return None  # Validation passed
    
    def __repr__(self) -> str:
        return f"LengthCheck(min={self.min_length}, max={self.max_length})"

