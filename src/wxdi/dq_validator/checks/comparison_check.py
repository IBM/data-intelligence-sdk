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
Comparison validation check - validates value comparison against another column or constant.
"""

from enum import Enum
from typing import Union, Any, Dict, Optional
from ..base import BaseCheck, ValidationError
from ..data_quality_dimension import DataQualityDimension


class ComparisonOperator(Enum):
    """Supported comparison operators"""
    GREATER_THAN = '>'
    LESS_THAN = '<'
    GREATER_THAN_OR_EQUAL = '>='
    LESS_THAN_OR_EQUAL = '<='
    EQUAL = '=='
    NOT_EQUAL = '!='


class ComparisonCheck(BaseCheck):
    """Validates value comparison against another column or constant"""
    
    def __init__(
        self,
        operator: Union[ComparisonOperator, str],
        target_column: Optional[str] = None,
        target_value: Optional[Any] = None
    ):
        """
        Initialize comparison check
        
        Args:
            operator: Comparison operator (ComparisonOperator enum or string)
            target_column: Name of column to compare against (for column-to-column)
            target_value: Constant value to compare against (for column-to-value)
        
        Raises:
            ValueError: If parameters are invalid
        
        Note: Exactly one of target_column or target_value must be provided
        """
        super().__init__(DataQualityDimension.VALIDITY)
        
        # Convert string operator to enum if needed
        if isinstance(operator, str):
            try:
                # Try to find matching enum by value
                self.operator = next(op for op in ComparisonOperator if op.value == operator)
            except StopIteration:
                valid_ops = [op.value for op in ComparisonOperator]
                raise ValueError(f"Invalid operator '{operator}'. Must be one of: {', '.join(valid_ops)}")
        elif isinstance(operator, ComparisonOperator):
            self.operator = operator
        else:
            raise TypeError(f"operator must be ComparisonOperator or str, got {type(operator).__name__}")
        
        # Validate that exactly one target is provided
        if target_column is None and target_value is None:
            raise ValueError("Either target_column or target_value must be specified")
        
        if target_column is not None and target_value is not None:
            raise ValueError("Cannot specify both target_column and target_value")
        
        self.target_column = target_column
        self.target_value = target_value
        self.is_column_comparison = target_column is not None
    
    def get_check_name(self) -> str:
        """Return check name"""
        return "comparison_check"
    
    def _compare(self, value: Any, target: Any) -> bool:
        """Execute the comparison operation"""
        op = self.operator
        
        if op == ComparisonOperator.GREATER_THAN:
            return value > target
        elif op == ComparisonOperator.LESS_THAN:
            return value < target
        elif op == ComparisonOperator.GREATER_THAN_OR_EQUAL:
            return value >= target
        elif op == ComparisonOperator.LESS_THAN_OR_EQUAL:
            return value <= target
        elif op == ComparisonOperator.EQUAL:
            return value == target
        elif op == ComparisonOperator.NOT_EQUAL:
            return value != target
        else:
            raise ValueError(f"Invalid operator: {op}")
    
    def validate(self, value: Any, context: Dict[str, Any]) -> Optional[ValidationError]:
        """
        Validate comparison
        
        Args:
            value: The value to validate
            context: Context containing column_name, record, metadata
        
        Returns:
            ValidationError if validation fails, None if passes
        """
        column_name = context.get('column_name', 'unknown')
        record = context.get('record')
        metadata = context.get('metadata')
        
        # Check if value is None
        if value is None:
            return ValidationError(
                column_name=column_name,
                check_name=self.get_check_name(),
                message=f"{column_name} is None, cannot perform comparison",
                value=value
            )
        
        # Get target value
        if self.is_column_comparison:
            # Column-to-column comparison
            # Validate required context for column comparison
            if metadata is None:
                return ValidationError(
                    column_name=column_name,
                    check_name=self.get_check_name(),
                    message="Metadata is required for column-to-column comparison",
                    value=value
                )
            
            if record is None:
                return ValidationError(
                    column_name=column_name,
                    check_name=self.get_check_name(),
                    message="Record is required for column-to-column comparison",
                    value=value
                )
            
            try:
                target = metadata.get_value(record, self.target_column)
            except (ValueError, IndexError) as e:
                return ValidationError(
                    column_name=column_name,
                    check_name=self.get_check_name(),
                    message=f"Target column '{self.target_column}' not found: {str(e)}",
                    value=value
                )
            
            # Check if target is None
            if target is None:
                return ValidationError(
                    column_name=column_name,
                    check_name=self.get_check_name(),
                    message=f"Cannot compare: {column_name}={value}, {self.target_column}=None",
                    value=value
                )
            
            # Check type compatibility
            if type(value) != type(target):
                return ValidationError(
                    column_name=column_name,
                    check_name=self.get_check_name(),
                    message=f"Type mismatch: {column_name} is {type(value).__name__}, {self.target_column} is {type(target).__name__}",
                    value=value
                )
            
            target_display = f"{self.target_column} ({target})"
        else:
            # Column-to-value comparison
            target = self.target_value
            
            # Check type compatibility
            if type(value) != type(target):
                return ValidationError(
                    column_name=column_name,
                    check_name=self.get_check_name(),
                    message=f"Type mismatch: {column_name} is {type(value).__name__}, target is {type(target).__name__}",
                    value=value
                )
            
            target_display = str(target)
        
        # Perform comparison
        try:
            comparison_result = self._compare(value, target)
        except TypeError as e:
            return ValidationError(
                column_name=column_name,
                check_name=self.get_check_name(),
                message=f"Cannot compare {type(value).__name__} with {type(target).__name__}: {str(e)}",
                value=value
            )
        
        if not comparison_result:
            return ValidationError(
                column_name=column_name,
                check_name=self.get_check_name(),
                message=f"{column_name} ({value}) {self.operator.value} {target_display} failed",
                value=value,
                expected=f"{self.operator.value} {target_display}"
            )
        
        return None  # Validation passed
    
    def __repr__(self) -> str:
        target = self.target_column if self.is_column_comparison else self.target_value
        return f"ComparisonCheck(operator={self.operator.value}, target={target})"

