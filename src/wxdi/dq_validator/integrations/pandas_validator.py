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
Pandas DataFrame validation integration.

This module provides memory-efficient validation for Pandas DataFrames
using chunked processing to handle large datasets.
"""

import pandas as pd
import json
from typing import Dict, Any, Optional
from .base import DataFrameValidator
from ..result import ValidationResult
from ..result_consolidator import ValidationResultConsolidated


class PandasValidator(DataFrameValidator[pd.DataFrame]):
    """
    Memory-efficient Pandas DataFrame validator.
    
    This validator processes DataFrames in chunks to avoid memory issues
    with large datasets. It provides:
    - Chunked processing (configurable chunk size)
    - O(chunk_size) memory usage instead of O(n)
    - Consistent struct column output
    - Column conflict detection
    
    Example:
        >>> from dq_validator import Validator, ValidationRule, LengthCheck
        >>> from dq_validator.integrations import PandasValidator
        >>> 
        >>> # Setup validator
        >>> validator = Validator(metadata)
        >>> validator.add_rule(ValidationRule('name').add_check(LengthCheck(min_length=2)))
        >>> 
        >>> # Create Pandas validator
        >>> pandas_validator = PandasValidator(validator, chunk_size=10000)
        >>> 
        >>> # Validate DataFrame
        >>> df_validated = pandas_validator.add_validation_column(df)
        >>> summary = pandas_validator.get_summary_statistics(df)
    """
    
    def __init__(
        self,
        validator,
        chunk_size: int = 10000,
        column_prefix: Optional[str] = None
    ):
        """
        Initialize Pandas validator.
        
        Args:
            validator: Configured Validator instance with validation rules
            chunk_size: Number of rows to process at once (default: 10,000)
                       Larger values = faster but more memory
                       Smaller values = slower but less memory
            column_prefix: Prefix for validation columns (default: "dq_")
        
        Raises:
            ValueError: If chunk_size is not positive
        """
        super().__init__(validator, column_prefix)
        
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        
        self.chunk_size = chunk_size
    
    def _align_dataframe_to_metadata(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Reorder DataFrame columns to match metadata order.
        
        This ensures that when we convert to arrays, the column order
        matches what the validator expects.
        
        Args:
            df: Input DataFrame
        
        Returns:
            DataFrame with columns in metadata order
        
        Raises:
            ValueError: If required columns are missing or conflicts exist
        """
        metadata_columns = [col.name for col in self.validator.metadata.columns]
        
        # Check for missing columns
        missing_cols = set(metadata_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(
                f"DataFrame missing required columns: {missing_cols}. "
                f"Expected columns: {metadata_columns}"
            )
        
        # Check for column name conflicts
        if self.result_column_name in df.columns:
            raise ValueError(
                f"Column '{self.result_column_name}' already exists in DataFrame. "
                f"Use a different column_prefix or rename the existing column."
            )
        
        # Reorder to match metadata
        # Use .loc[:, columns] to ensure DataFrame return type for type checker
        return df.loc[:, metadata_columns]
    
    def _create_validation_struct(self, result: ValidationResult) -> Dict[str, Any]:
        """
        Create validation result struct from ValidationResult.
        
        Args:
            result: ValidationResult object from core validator
        
        Returns:
            Dictionary representing validation struct with all fields
        """
        return {
            'is_valid': result.is_valid,
            'score': result.score,
            'pass_rate': result.pass_rate,
            'total_checks': result.total_checks,
            'passed_checks': result.passed_checks,
            'failed_checks': result.failed_checks,
            'error_count': len(result.errors),
            'errors': [json.dumps(e.to_dict()) for e in result.errors]
        }
    
    def get_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get validation summary WITHOUT storing all ValidationResults.
        
        This method processes the DataFrame in chunks and aggregates
        statistics without keeping all validation results in memory.
        
        Memory Usage: O(chunk_size) - processes in chunks
        
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
        aligned_df = self._align_dataframe_to_metadata(df)
        
        # Aggregate statistics across chunks
        total_rows = 0
        valid_rows = 0
        total_checks = 0
        passed_checks = 0
        failed_checks = 0
        
        for start_idx in range(0, len(aligned_df), self.chunk_size):
            end_idx = min(start_idx + self.chunk_size, len(aligned_df))
            chunk = aligned_df.iloc[start_idx:end_idx]
            
            # Convert to records and validate
            records = chunk.values.tolist()
            results = self.validator.validate_batch(records)
            
            # Aggregate only (don't store results)
            total_rows += len(results)
            valid_rows += sum(1 for r in results if r.is_valid)
            total_checks += sum(r.total_checks for r in results)
            passed_checks += sum(r.passed_checks for r in results)
            failed_checks += sum(r.failed_checks for r in results)
            
            # Free memory immediately
            del results
        
        return {
            'total_rows': total_rows,
            'valid_rows': valid_rows,
            'invalid_rows': total_rows - valid_rows,
            'pass_rate': (valid_rows / total_rows * 100) if total_rows > 0 else 0.0,
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': failed_checks
        }
    
    def add_validation_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add validation result struct column efficiently using chunked processing.
        
        This method adds a single column containing a struct (dictionary) with
        all validation results. The column name is {prefix}validation_result.
        
        Memory Usage: O(chunk_size) instead of O(n)
        
        Args:
            df: DataFrame to validate
        
        Returns:
            DataFrame with {prefix}validation_result struct column added.
            The struct contains: is_valid, score, pass_rate, total_checks,
            passed_checks, failed_checks, error_count, errors
        
        Example:
            >>> df_validated = validator.add_validation_column(df)
            >>> # Access struct fields
            >>> df_validated['dq_validation_result'].apply(lambda x: x['is_valid'])
        """
        aligned_df = self._align_dataframe_to_metadata(df)
        
        # Process in chunks to avoid memory issues
        result_chunks = []
        
        for start_idx in range(0, len(aligned_df), self.chunk_size):
            end_idx = min(start_idx + self.chunk_size, len(aligned_df))
            chunk = aligned_df.iloc[start_idx:end_idx]
            
            # Validate chunk
            records = chunk.values.tolist()
            results = self.validator.validate_batch(records)
            
            # Create struct column (dictionary per row)
            chunk_results = pd.DataFrame({
                self.result_column_name: [
                    self._create_validation_struct(r) for r in results
                ]
            }, index=chunk.index)
            
            result_chunks.append(chunk_results)
            
            # Clear results to free memory
            del results
        
        # Concatenate results
        validation_df = pd.concat(result_chunks)
        
        # Join with original DataFrame
        return df.join(validation_df)
    
    def get_invalid_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get only invalid rows from DataFrame.
        
        This is a convenience method that adds validation column and
        filters to return only rows that failed validation.
        
        Args:
            df: Original DataFrame
        
        Returns:
            DataFrame containing only invalid rows with validation column
        
        Example:
            >>> invalid_df = validator.get_invalid_rows(df)
            >>> print(f"Found {len(invalid_df)} invalid rows")
        """
        df_with_validation = self.add_validation_column(df)
        # Access nested field in struct
        mask = df_with_validation[self.result_column_name].apply(
            lambda x: not x['is_valid']
        )
        return df_with_validation.loc[mask]
    
    def get_valid_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get only valid rows from DataFrame.
        
        This is a convenience method that adds validation column and
        filters to return only rows that passed validation.
        
        Args:
            df: Original DataFrame
        
        Returns:
            DataFrame containing only valid rows
        
        Example:
            >>> valid_df = validator.get_valid_rows(df)
            >>> print(f"Found {len(valid_df)} valid rows")
        """
        df_with_validation = self.add_validation_column(df)
        # Access nested field in struct
        mask = df_with_validation[self.result_column_name].apply(
            lambda x: x['is_valid']
        )
        return df_with_validation.loc[mask]
    
    def expand_validation_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Expand validation struct column into separate columns.
        
        This method takes a DataFrame with the validation struct column
        and expands it into individual columns with the prefix applied.
        
        Args:
            df: DataFrame with validation column
        
        Returns:
            DataFrame with validation fields as separate columns:
            - {prefix}is_valid
            - {prefix}score
            - {prefix}pass_rate
            - {prefix}total_checks
            - {prefix}passed_checks
            - {prefix}failed_checks
            - {prefix}error_count
            - {prefix}errors
        
        Raises:
            ValueError: If validation column doesn't exist
        
        Example:
            >>> df_validated = validator.add_validation_column(df)
            >>> df_expanded = validator.expand_validation_column(df_validated)
            >>> print(df_expanded[['name', 'dq_is_valid', 'dq_score']])
        """
        if self.result_column_name not in df.columns:
            raise ValueError(
                f"DataFrame does not contain validation result column '{self.result_column_name}'. "
                f"Call add_validation_column() first."
            )
        
        # Expand struct into separate columns
        # Use .loc to ensure consistent DataFrame access pattern
        validation_expanded = pd.json_normalize(df.loc[:, self.result_column_name])
        
        # Rename columns with prefix
        validation_expanded.columns = [
            f"{self.column_prefix}{col}" for col in validation_expanded.columns
        ]
        
        # Set index to match original DataFrame
        validation_expanded.index = df.index
        
        # Join with original DataFrame (excluding the struct column)
        df_without_struct = df.drop(columns=[self.result_column_name])
        return df_without_struct.join(validation_expanded)
    
    def get_detailed_statistics(self, df: pd.DataFrame) -> ValidationResultConsolidated:
        """
        Get detailed validation statistics with column and check-level breakdown.
        
        This method processes the DataFrame in chunks and returns a
        ValidationResultConsolidated object that provides:
        - Statistics by column
        - Statistics by check type
        - Combined statistics (column + check)
        
        Note: Error details are NOT stored to conserve memory. Only counts are tracked.
        If you need error details, use add_validation_column() instead.
        
        Memory Usage: O(chunk_size) for processing, O(columns * checks) for statistics
        
        Args:
            df: DataFrame to validate
        
        Returns:
            ValidationResultConsolidated object with detailed statistics (no error storage)
        
        Example:
            >>> consolidator = validator.get_detailed_statistics(df)
            >>>
            >>> # Get overall stats
            >>> print(consolidator.get_overall_statistics())
            >>>
            >>> # Get stats for a specific column
            >>> email_stats = consolidator.get_column_statistics('email')
            >>> print(f"Email failures: {email_stats['failed']}/{email_stats['total']}")
            >>>
            >>> # Get stats for a specific check type
            >>> format_stats = consolidator.get_check_statistics('format_check')
            >>> print(f"Format check failures: {format_stats['failed']}")
            >>>
            >>> # Get combined stats for column and check
            >>> stats = consolidator.get_combined_statistics('email', 'format_check')
            >>> print(f"Email format failures: {stats['failed']}")
            >>>
            >>> # Get all columns that were validated
            >>> columns = consolidator.get_columns()
            >>>
            >>> # Get all check types that were executed
            >>> checks = consolidator.get_checks()
        """
        aligned_df = self._align_dataframe_to_metadata(df)
        
        # Create consolidator without error storage for memory efficiency
        consolidator = ValidationResultConsolidated(validator=self.validator, store_errors=False)
        
        # Process in chunks
        for start_idx in range(0, len(aligned_df), self.chunk_size):
            end_idx = min(start_idx + self.chunk_size, len(aligned_df))
            chunk = aligned_df.iloc[start_idx:end_idx]
            
            # Convert to records and validate
            records = chunk.values.tolist()
            results = self.validator.validate_batch(records)
            
            # Add results to consolidator (only statistics, no error details)
            consolidator.add_results(results)
            
            # Free memory immediately
            del results
        
        return consolidator
    
    def __repr__(self) -> str:
        """String representation of the validator."""
        return (
            f"PandasValidator("
            f"table='{self.validator.metadata.table_name}', "
            f"rules={len(self.validator.rules)}, "
            f"chunk_size={self.chunk_size}, "
            f"prefix='{self.column_prefix}')"
        )