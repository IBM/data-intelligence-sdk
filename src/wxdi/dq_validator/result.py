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
Validation result classes.
"""

from typing import List, Any
from .base import ValidationError


class ValidationResult:
    """Result of validating a single record"""
    
    def __init__(self, record: List[Any], record_index: int = 0):
        """
        Initialize validation result
        
        Args:
            record: The validated record
            record_index: Index of the record in batch (for tracking)
        """
        self.record = record
        self.record_index = record_index
        self.errors: List[ValidationError] = []
        self.total_checks = 0
        self.passed_checks = 0
        self.failed_checks = 0
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)"""
        return len(self.errors) == 0
    
    @property
    def score(self) -> str:
        """Get score as string (e.g., '5/5')"""
        return f"{self.passed_checks}/{self.total_checks}"
    
    @property
    def pass_rate(self) -> float:
        """Get pass rate as percentage"""
        if self.total_checks == 0:
            return 100.0
        return (self.passed_checks / self.total_checks) * 100.0
    
    def add_error(self, error: ValidationError) -> None:
        """
        Add a validation error
        
        Args:
            error: ValidationError to add
        """
        self.errors.append(error)
        self.failed_checks += 1
    
    def increment_passed(self) -> None:
        """Increment passed check count"""
        self.passed_checks += 1
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'record_index': self.record_index,
            'is_valid': self.is_valid,
            'score': self.score,
            'pass_rate': self.pass_rate,
            'total_checks': self.total_checks,
            'passed_checks': self.passed_checks,
            'failed_checks': self.failed_checks,
            'errors': [error.to_dict() for error in self.errors]
        }
    
    def __repr__(self) -> str:
        status = "PASS" if self.is_valid else "FAIL"
        return f"ValidationResult(record_index={self.record_index}, score={self.score}, status={status})"

