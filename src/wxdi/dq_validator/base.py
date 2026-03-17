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
Base classes for validation checks and errors.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from .data_quality_dimension import DataQualityDimension


class ValidationError:
    """Represents a validation error"""
    
    def __init__(
        self,
        column_name: str,
        check_name: str,
        message: str,
        value: Any,
        expected: Any = None
    ):
        """
        Initialize validation error
        
        Args:
            column_name: Name of the column that failed
            check_name: Type of check that failed
            message: Human-readable error message
            value: The actual value that failed
            expected: The expected value/constraint (optional)
        """
        self.column_name = column_name
        self.check_name = check_name
        self.message = message
        self.value = value
        self.expected = expected
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'column': self.column_name,
            'check': self.check_name,
            'message': self.message,
            'value': str(self.value),
            'expected': str(self.expected) if self.expected is not None else None
        }
    
    def __repr__(self) -> str:
        return f"ValidationError(column='{self.column_name}', check='{self.check_name}', message='{self.message}')"


class BaseCheck(ABC):
    """Base class for all validation checks"""
    
    def __init__(self, dimension: DataQualityDimension):
        """
        Initialize base check with dimension
        
        Args:
            dimension: The data quality dimension this check belongs to
        """
        self._dimension = dimension
    
    def get_dimension(self) -> DataQualityDimension:
        """Return dimension to which the check belongs"""
        return self._dimension
    
    def set_dimension(self, dimension: DataQualityDimension) -> None:
        """Set the dimension to which the check belongs"""
        self._dimension = dimension
    
    @abstractmethod
    def validate(self, value: Any, context: Dict[str, Any]) -> Optional[ValidationError]:
        """
        Validate a value
        
        Args:
            value: The value to validate
            context: Additional context (e.g., other column values, metadata)
                    Expected keys:
                    - 'column_name': Name of the column being validated
                    - 'record': The full record array (for column-to-column comparisons)
                    - 'metadata': AssetMetadata object (for column lookups)
        
        Returns:
            ValidationError if validation fails, None if passes
        """
        pass
    
    @abstractmethod
    def get_check_name(self) -> str:
        """Return the name of this check type"""
        pass

