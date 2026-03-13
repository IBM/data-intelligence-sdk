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
Base classes for DataFrame validation integration.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Dict, Optional

# Generic DataFrame type
DF = TypeVar('DF')


class DataFrameValidator(ABC, Generic[DF]):
    """
    Abstract base class for memory-efficient DataFrame validation.
    
    This class provides a consistent interface for validating DataFrames
    across different libraries (Pandas, PySpark, etc.) while ensuring:
    - Memory efficiency through chunked/distributed processing
    - Consistent API across implementations
    - Column name conflict prevention
    - Lazy evaluation where possible
    """
    
    # Column name constants
    DEFAULT_COLUMN_PREFIX = "dq_"
    VALIDATION_RESULT_COLUMN = "validation_result"
    
    def __init__(self, validator, column_prefix: Optional[str] = None):
        """
        Initialize DataFrame validator with core validator.
        
        Args:
            validator: Configured Validator instance with validation rules
            column_prefix: Prefix for validation columns (default: "dq_")
                          This prevents conflicts with existing DataFrame columns
        """
        self.validator = validator
        self.column_prefix = column_prefix or self.DEFAULT_COLUMN_PREFIX
        self.result_column_name = f"{self.column_prefix}{self.VALIDATION_RESULT_COLUMN}"
    
    @abstractmethod
    def get_summary_statistics(self, df: DF) -> Dict:
        """
        Get validation summary statistics WITHOUT collecting all results.
        
        This method computes aggregate statistics efficiently without
        loading all ValidationResults into memory.
        
        Args:
            df: DataFrame to validate
        
        Returns:
            Dictionary with aggregated statistics:
            - total_rows: Total number of rows validated
            - valid_rows: Number of valid rows
            - invalid_rows: Number of invalid rows
            - pass_rate: Percentage of valid rows
            - total_checks: Total validation checks performed
            - passed_checks: Number of checks that passed
            - failed_checks: Number of checks that failed
        """
        pass
    
    @abstractmethod
    def add_validation_column(self, df: DF) -> DF:
        """
        Add validation result struct column to DataFrame.
        
        This method adds a single column containing a struct with all
        validation results. The column name is {prefix}validation_result
        (e.g., "dq_validation_result").
        
        The struct contains:
        - is_valid: boolean
        - score: string (e.g., "5/6")
        - pass_rate: float
        - total_checks: int
        - passed_checks: int
        - failed_checks: int
        - error_count: int
        - errors: array of JSON strings
        
        Args:
            df: DataFrame to validate
        
        Returns:
            DataFrame with validation result struct column added
            
        Note: Method name is SINGULAR (add_validation_column) not plural
        """
        pass
    
    @abstractmethod
    def get_invalid_rows(self, df: DF) -> DF:
        """
        Get only invalid rows from DataFrame.
        
        This is a convenience method that filters the DataFrame to return
        only rows that failed validation.
        
        Args:
            df: DataFrame to validate
        
        Returns:
            Filtered DataFrame containing only invalid rows
        """
        pass
    
    @abstractmethod
    def get_valid_rows(self, df: DF) -> DF:
        """
        Get only valid rows from DataFrame.
        
        This is a convenience method that filters the DataFrame to return
        only rows that passed validation.
        
        Args:
            df: DataFrame to validate
        
        Returns:
            Filtered DataFrame containing only valid rows
        """
        pass
    
    @abstractmethod
    def expand_validation_column(self, df: DF) -> DF:
        """
        Expand validation struct column into separate columns.
        
        This method takes a DataFrame with the validation struct column
        and expands it into individual columns with the prefix applied.
        
        Creates columns:
        - {prefix}is_valid
        - {prefix}score
        - {prefix}pass_rate
        - {prefix}total_checks
        - {prefix}passed_checks
        - {prefix}failed_checks
        - {prefix}error_count
        - {prefix}errors
        
        Args:
            df: DataFrame with validation column
        
        Returns:
            DataFrame with validation fields as separate columns
            
        Raises:
            ValueError: If validation column doesn't exist
        """
        pass