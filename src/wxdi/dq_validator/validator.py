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
Main validator class for orchestrating data quality checks.
"""

from typing import List, Any
from .metadata import AssetMetadata
from .rule import ValidationRule
from .result import ValidationResult


class Validator:
    """Main validator for data quality checks"""
    
    def __init__(self, metadata: AssetMetadata):
        """
        Initialize validator
        
        Args:
            metadata: Asset metadata defining table structure
        """
        self.metadata = metadata
        self.rules: List[ValidationRule] = []
    
    def add_rule(self, rule: ValidationRule) -> 'Validator':
        """
        Add a validation rule (fluent API)
        
        Args:
            rule: The validation rule to add
        
        Returns:
            Self for method chaining
        """
        self.rules.append(rule)
        return self
    
    def validate(self, record: List[Any], record_index: int = 0) -> ValidationResult:
        """
        Validate a single record
        
        Args:
            record: The record array to validate
            record_index: Index of the record (for tracking)
        
        Returns:
            ValidationResult with errors and statistics
        """
        result = ValidationResult(record, record_index)
        
        # Count total checks
        result.total_checks = sum(len(rule.checks) for rule in self.rules)
        
        # Validate each rule
        for rule in self.rules:
            errors = rule.validate(record, self.metadata)
            
            # Track passed/failed checks
            checks_in_rule = len(rule.checks)
            failed_in_rule = len(errors)
            passed_in_rule = checks_in_rule - failed_in_rule
            
            result.passed_checks += passed_in_rule
            
            # Add errors
            for error in errors:
                result.add_error(error)
        
        return result
    
    def validate_batch(self, records: List[List[Any]]) -> List[ValidationResult]:
        """
        Validate multiple records
        
        Args:
            records: List of record arrays to validate
        
        Returns:
            List of ValidationResult objects
        """
        return [
            self.validate(record, idx)
            for idx, record in enumerate(records)
        ]
    
    def __repr__(self) -> str:
        return f"Validator(table='{self.metadata.table_name}', rules={len(self.rules)})"

