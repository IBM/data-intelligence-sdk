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
Validation result consolidation utility.

This module provides utilities to aggregate and analyze validation results
across multiple records, with support for filtering by column and check type.
"""

from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from .result import ValidationResult
from .base import ValidationError
from .validator import Validator
from .data_quality_dimension import DataQualityDimension

class ValidationResultConsolidated:
    """
    Utility class for consolidating validation results incrementally.
    
    This class aggregates statistics from ValidationResult objects and provides
    methods to query results by column and/or check type. It's designed for
    memory-efficient incremental processing.
    
    Requires a Validator instance to accurately track passed and failed checks
    at the granular (column, check) level.
    
    Error storage is optional to manage memory usage for large datasets.
    
    Example:
        >>> # Without error storage (memory efficient)
        >>> consolidator = ValidationResultConsolidated(validator, store_errors=False)
        >>>
        >>> # With error storage (for detailed analysis)
        >>> consolidator = ValidationResultConsolidated(validator, store_errors=True)
        >>>
        >>> # Add results incrementally
        >>> for result in validation_results:
        ...     consolidator.add_result(result)
        >>>
        >>> # Get statistics by column
        >>> stats = consolidator.get_column_statistics('email')
        >>> print(f"Email validation: {stats['passed']}/{stats['total']}")
        >>>
        >>> # Get statistics by check type
        >>> stats = consolidator.get_check_statistics('format_check')
        >>>
        >>> # Get error details (only if store_errors=True)
        >>> if consolidator.store_errors:
        ...     errors = consolidator.get_errors_by_column('email')
    """
    
    def __init__(self, validator: Validator, store_errors: bool = True):
        """
        Initialize the consolidator with empty statistics.
        
        Args:
            validator: Validator instance used to infer which checks should be applied.
                      Required for accurate passed/failed statistics at granular level.
            store_errors: Whether to store error details (default: True).
                         Set to False for memory-efficient processing of large datasets.
        """
        self.validator = validator
        self.store_errors = store_errors
        # Overall statistics
        self.total_records = 0
        self.valid_records = 0
        self.invalid_records = 0
        
        # Column-level statistics: {column_name: {passed, failed, total}}
        self._column_stats: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {'passed': 0, 'failed': 0, 'total': 0}
        )
        
        # Check-level statistics: {check_name: {passed, failed, total}}
        self._check_stats: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {'passed': 0, 'failed': 0, 'total': 0}
        )
        
        # Combined statistics: {(column_name, check_name): {passed, failed, total}}
        self._combined_stats: Dict[Tuple[str, str], Dict[str, int]] = defaultdict(
            lambda: {'passed': 0, 'failed': 0, 'total': 0}
        )

        #Dimension level issues found
        self.issues: Dict[str, int] = defaultdict(
            lambda: 0
        )
        
        # Error storage: List of error dictionaries
        self._errors: List[Dict[str, Any]] = []
        
        # Track which columns and checks we've seen
        self._columns_seen = set()
        self._checks_seen = set()
    
    def add_result(self, result: ValidationResult) -> None:
        """
        Add a single ValidationResult to the consolidation.
        
        This method incrementally updates statistics. If store_errors is True,
        it also stores error details for later retrieval.
        
        This method accurately tracks passed and failed checks at the granular
        (column, check) level using the validator provided during initialization.
        
        Args:
            result: ValidationResult to consolidate
        """
        # Update overall statistics
        self.total_records += 1
        if result.is_valid:
            self.valid_records += 1
        else:
            self.invalid_records += 1
        
        # Build a set of failed checks for quick lookup
        failed_checks = {(error.column_name, error.check_name) for error in result.errors}
        
        # Iterate through all rules and checks in the validator
        for rule in self.validator.rules:
            column = rule.column_name
            self._columns_seen.add(column)
            
            for check in rule.checks:
                check_name = check.get_check_name()
                self._checks_seen.add(check_name)
                
                # Check if this specific (column, check) failed
                if (column, check_name) in failed_checks:
                    # Failed check
                    self._column_stats[column]['failed'] += 1
                    self._check_stats[check_name]['failed'] += 1
                    self._combined_stats[(column, check_name)]['failed'] += 1
                    self.issues[check.get_dimension().name] +=1        
                else:
                    # Passed check
                    self._column_stats[column]['passed'] += 1
                    self._check_stats[check_name]['passed'] += 1
                    self._combined_stats[(column, check_name)]['passed'] += 1
                
                # Increment totals
                self._column_stats[column]['total'] += 1
                self._check_stats[check_name]['total'] += 1
                self._combined_stats[(column, check_name)]['total'] += 1
        
        # Store error details if enabled
        if self.store_errors:
            for error in result.errors:
                error_dict = error.to_dict()
                error_dict['record_index'] = result.record_index
                self._errors.append(error_dict)
    
    def add_results(self, results: List[ValidationResult]) -> None:
        """
        Add multiple ValidationResults to the consolidation.
        
        Args:
            results: List of ValidationResult objects to consolidate
        """
        for result in results:
            self.add_result(result)
    
    def get_overall_statistics(self) -> Dict[str, Any]:
        """
        Get overall validation statistics.
        
        Returns:
            Dictionary with overall statistics:
            - total_records: Total number of records validated
            - valid_records: Number of valid records
            - invalid_records: Number of invalid records
            - pass_rate: Percentage of valid records
            - total_errors: Total number of errors
        """
        return {
            'total_records': self.total_records,
            'valid_records': self.valid_records,
            'invalid_records': self.invalid_records,
            'pass_rate': (self.valid_records / self.total_records * 100) if self.total_records > 0 else 0.0,
            'total_errors': len(self._errors)
        }
    
    def get_column_statistics(self, column_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get validation statistics for a specific column or all columns.
        
        Args:
            column_name: Name of the column (None for all columns)
        
        Returns:
            If column_name is specified: Dictionary with passed, failed, total counts
            If column_name is None: Dictionary mapping column names to their statistics
        
        Example:
            >>> # Get stats for specific column
            >>> stats = consolidator.get_column_statistics('email')
            >>> print(f"Passed: {stats['passed']}, Failed: {stats['failed']}")
            >>> 
            >>> # Get stats for all columns
            >>> all_stats = consolidator.get_column_statistics()
            >>> for col, stats in all_stats.items():
            ...     print(f"{col}: {stats['failed']} failures")
        """
        if column_name is not None:
            return dict(self._column_stats.get(column_name, {'passed': 0, 'failed': 0, 'total': 0}))
        else:
            return {col: dict(stats) for col, stats in self._column_stats.items()}
    
    def get_check_statistics(self, check_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get validation statistics for a specific check type or all check types.
        
        Args:
            check_name: Name of the check type (None for all checks)
        
        Returns:
            If check_name is specified: Dictionary with passed, failed, total counts
            If check_name is None: Dictionary mapping check names to their statistics
        
        Example:
            >>> # Get stats for specific check
            >>> stats = consolidator.get_check_statistics('format_check')
            >>> print(f"Format check failures: {stats['failed']}")
            >>> 
            >>> # Get stats for all checks
            >>> all_stats = consolidator.get_check_statistics()
            >>> for check, stats in all_stats.items():
            ...     print(f"{check}: {stats['failed']} failures")
        """
        if check_name is not None:
            return dict(self._check_stats.get(check_name, {'passed': 0, 'failed': 0, 'total': 0}))
        else:
            return {check: dict(stats) for check, stats in self._check_stats.items()}
    
    def get_combined_statistics(
        self,
        column_name: Optional[str] = None,
        check_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get validation statistics filtered by column and/or check type.
        
        Args:
            column_name: Filter by column name (None for all columns)
            check_name: Filter by check type (None for all checks)
        
        Returns:
            If both specified: Dictionary with passed, failed, total for that combination
            If one specified: Dictionary mapping the other dimension to statistics
            If neither specified: Nested dictionary with all combinations
        
        Example:
            >>> # Get stats for specific column and check
            >>> stats = consolidator.get_combined_statistics('email', 'format_check')
            >>> print(f"Email format failures: {stats['failed']}")
            >>> 
            >>> # Get all checks for a column
            >>> stats = consolidator.get_combined_statistics(column_name='email')
            >>> for check, check_stats in stats.items():
            ...     print(f"{check}: {check_stats['failed']} failures")
        """
        if column_name is not None and check_name is not None:
            # Return stats for specific combination
            return dict(self._combined_stats.get(
                (column_name, check_name),
                {'passed': 0, 'failed': 0, 'total': 0}
            ))
        elif column_name is not None:
            # Return all checks for this column
            result = {}
            for (col, check), stats in self._combined_stats.items():
                if col == column_name:
                    result[check] = dict(stats)
            return result
        elif check_name is not None:
            # Return all columns for this check
            result = {}
            for (col, check), stats in self._combined_stats.items():
                if check == check_name:
                    result[col] = dict(stats)
            return result
        else:
            # Return all combinations
            result = {}
            for (col, check), stats in self._combined_stats.items():
                if col not in result:
                    result[col] = {}
                result[col][check] = dict(stats)
            return result
    
    def get_errors_by_column(self, column_name: str) -> List[Dict[str, Any]]:
        """
        Get all error details for a specific column.
        
        Only available if store_errors=True was set during initialization.
        
        Args:
            column_name: Name of the column
        
        Returns:
            List of error dictionaries for the specified column
        
        Raises:
            RuntimeError: If store_errors is False
        
        Example:
            >>> errors = consolidator.get_errors_by_column('email')
            >>> for error in errors:
            ...     print(f"Record {error['record_index']}: {error['message']}")
        """
        if not self.store_errors:
            raise RuntimeError(
                "Error details not available. Initialize with store_errors=True to enable error storage."
            )
        return [
            error for error in self._errors
            if error['column'] == column_name
        ]
    
    def get_errors_by_check(self, check_name: str) -> List[Dict[str, Any]]:
        """
        Get all error details for a specific check type.
        
        Only available if store_errors=True was set during initialization.
        
        Args:
            check_name: Name of the check type
        
        Returns:
            List of error dictionaries for the specified check type
        
        Raises:
            RuntimeError: If store_errors is False
        
        Example:
            >>> errors = consolidator.get_errors_by_check('format_check')
            >>> for error in errors:
            ...     print(f"Column {error['column']}: {error['message']}")
        """
        if not self.store_errors:
            raise RuntimeError(
                "Error details not available. Initialize with store_errors=True to enable error storage."
            )
        return [
            error for error in self._errors
            if error['check'] == check_name
        ]
    
    def get_errors_by_column_and_check(
        self,
        column_name: str,
        check_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get all error details for a specific column and check type combination.
        
        Only available if store_errors=True was set during initialization.
        
        Args:
            column_name: Name of the column
            check_name: Name of the check type
        
        Returns:
            List of error dictionaries for the specified combination
        
        Raises:
            RuntimeError: If store_errors is False
        
        Example:
            >>> errors = consolidator.get_errors_by_column_and_check('email', 'format_check')
            >>> print(f"Found {len(errors)} email format errors")
        """
        if not self.store_errors:
            raise RuntimeError(
                "Error details not available. Initialize with store_errors=True to enable error storage."
            )
        return [
            error for error in self._errors
            if error['column'] == column_name and error['check'] == check_name
        ]
    
    def get_all_errors(self) -> List[Dict[str, Any]]:
        """
        Get all error details.
        
        Only available if store_errors=True was set during initialization.
        
        Returns:
            List of all error dictionaries
        
        Raises:
            RuntimeError: If store_errors is False
        """
        if not self.store_errors:
            raise RuntimeError(
                "Error details not available. Initialize with store_errors=True to enable error storage."
            )
        return self._errors.copy()
    
    def get_columns(self) -> List[str]:
        """
        Get list of all columns that have been validated.
        
        Returns:
            List of column names
        """
        return sorted(self._columns_seen)
    
    def get_checks(self) -> List[str]:
        """
        Get list of all check types that have been executed.
        
        Returns:
            List of check names
        """
        return sorted(self._checks_seen)
    
    def get_issues_by_dimension(self, dimension: DataQualityDimension) -> int:
        """
        Get the number of issues for a specific data quality dimension.
        
        Args:
            dimension: DataQualityDimension enum value
        
        Returns:
            Number of issues found for the specified dimension
        
        Example:
            >>> from dq_validator.data_quality_dimension import DataQualityDimension
            >>> issues = consolidator.get_issues_by_dimension(DataQualityDimension.ACCURACY)
            >>> print(f"Accuracy issues: {issues}")
        """
        return self.issues.get(dimension.name, 0)
    
    def get_all_dimension_issues(self) -> Dict[str, int]:
        """
        Get the number of issues for all data quality dimensions.
        
        Returns:
            Dictionary mapping dimension names to issue counts
        
        Example:
            >>> all_issues = consolidator.get_all_dimension_issues()
            >>> for dimension, count in all_issues.items():
            ...     print(f"{dimension}: {count} issues")
        """
        return dict(self.issues)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert consolidation to a comprehensive dictionary.
        
        Returns:
            Dictionary with all statistics and error details
        """
        return {
            'overall': self.get_overall_statistics(),
            'by_column': self.get_column_statistics(),
            'by_check': self.get_check_statistics(),
            'combined': self.get_combined_statistics(),
            'columns': self.get_columns(),
            'checks': self.get_checks(),
            'error_count': len(self._errors)
        }
    
    def __repr__(self) -> str:
        """String representation of the consolidator."""
        return (
            f"ValidationResultConsolidated("
            f"records={self.total_records}, "
            f"valid={self.valid_records}, "
            f"invalid={self.invalid_records}, "
            f"errors={len(self._errors)})"
        )