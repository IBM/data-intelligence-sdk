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
Table-level validation rule classes.

Unlike column-level ValidationRule which validates individual column values,
TableValidationRule validates entire records/rows for cross-column business logic.
"""

from typing import List, Any
from .base import BaseCheck, ValidationError
from .metadata import AssetMetadata


class TableValidationRule:
    """
    Validation rules for entire table records.
    
    Unlike ValidationRule which is tied to a specific column, TableValidationRule
    validates the entire record. This is useful for:
    - Cross-column validation (e.g., start_date < end_date)
    - Complex business rules spanning multiple fields
    - Conditional logic based on multiple columns
    
    Example:
        >>> from wxdi.dq_validator import TableValidationRule, TableCELCheck
        >>> 
        >>> # Multi-column validation
        >>> rule = TableValidationRule('salary_age_check')
        >>> rule.add_check(TableCELCheck(
        ...     'salary > min_salary && age >= 18',
        ...     error_message='Invalid salary/age combination'
        ... ))
        >>> 
        >>> # Complex business rules
        >>> rule = TableValidationRule('department_rules')
        >>> rule.add_check(TableCELCheck(
        ...     'department == "Sales" ? salary >= 50000 : salary >= 40000',
        ...     error_message='Salary does not meet department requirements'
        ... ))
    """
    
    def __init__(self, rule_name: str = "table_rule"):
        """
        Initialize table-level validation rule.
        
        Args:
            rule_name: Name/description of this rule (used in error messages)
        """
        self.rule_name = rule_name
        self.checks: List[BaseCheck] = []
    
    def add_check(self, check: BaseCheck) -> 'TableValidationRule':
        """
        Add a validation check (fluent API).
        
        Args:
            check: The check to add (typically TableCELCheck)
        
        Returns:
            Self for method chaining
        
        Example:
            >>> rule = TableValidationRule('business_rules')
            >>> rule.add_check(TableCELCheck('salary > 0'))
            >>> rule.add_check(TableCELCheck('age >= 18'))
        """
        self.checks.append(check)
        return self
    
    def validate(
        self,
        record: List[Any],
        metadata: AssetMetadata,
        record_index: int = 0
    ) -> List[ValidationError]:
        """
        Validate the entire record.
        
        Args:
            record: The record array to validate
            metadata: Asset metadata for column mapping
            record_index: Position of the record in the batch (for context)
        
        Returns:
            List of validation errors (empty if all checks pass)
        """
        errors = []
        
        # Build context for table-level checks
        # Note: No 'value' or 'column_name' since we're validating entire record
        context = {
            'record': record,
            'metadata': metadata,
            'column_name': None,  # No specific column
            'rule_name': self.rule_name,
            'record_index': record_index
        }
        
        # Run all checks (value=None for table-level)
        for check in self.checks:
            error = check.validate(None, context)
            if error:
                errors.append(error)
        
        return errors
    
    def __repr__(self) -> str:
        return f"TableValidationRule(name='{self.rule_name}', checks={len(self.checks)})"

# Made with Bob
