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
Validation rule classes.
"""

from typing import List, Any
from .base import BaseCheck, ValidationError
from .metadata import AssetMetadata


class ValidationRule:
    """Validation rules for a specific column"""
    
    def __init__(self, column_name: str):
        """
        Initialize validation rule
        
        Args:
            column_name: Name of the column to validate
        """
        self.column_name = column_name
        self.checks: List[BaseCheck] = []
    
    def add_check(self, check: BaseCheck) -> 'ValidationRule':
        """
        Add a validation check (fluent API)
        
        Args:
            check: The check to add
        
        Returns:
            Self for method chaining
        """
        self.checks.append(check)
        return self
    
    def validate(
        self,
        record: List[Any],
        metadata: AssetMetadata
    ) -> List[ValidationError]:
        """
        Validate the column value in the record
        
        Args:
            record: The record array
            metadata: Asset metadata for column mapping
        
        Returns:
            List of validation errors (empty if all pass)
        """
        errors = []
        
        # Get the value for this column
        try:
            value = metadata.get_value(record, self.column_name)
        except (ValueError, IndexError) as e:
            errors.append(ValidationError(
                column_name=self.column_name,
                check_name='record_structure',
                message=str(e),
                value=None
            ))
            return errors
        
        # Build context for checks
        context = {
            'record': record,
            'metadata': metadata,
            'column_name': self.column_name
        }
        
        # Run all checks
        for check in self.checks:
            error = check.validate(value, context)
            if error:
                errors.append(error)
        
        return errors
    
    def __repr__(self) -> str:
        return f"ValidationRule(column='{self.column_name}', checks={len(self.checks)})"

