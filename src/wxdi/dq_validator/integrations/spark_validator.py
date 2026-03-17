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
PySpark DataFrame validation integration.

This module provides memory-efficient validation for PySpark DataFrames
using distributed processing with UDFs.
"""

from pyspark.sql import DataFrame as SparkDataFrame, SparkSession
from pyspark.sql.functions import udf, struct, col, sum as spark_sum, count, explode, to_json
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    BooleanType,
    FloatType,
    IntegerType,
    ArrayType,
)
from typing import Dict, Any, Optional, List
import json
from .base import DataFrameValidator
from ..result_consolidator import ValidationResultConsolidated


class SparkValidator(DataFrameValidator[SparkDataFrame]):
    """
    Memory-efficient PySpark DataFrame validator.

    This validator uses distributed processing with Spark UDFs to validate
    DataFrames without collecting data to the driver. It provides:
    - Fully distributed validation (no driver collection)
    - UDF-based row-level validation
    - Lazy evaluation
    - O(1) driver memory usage
    - Consistent struct column output

    Example:
        >>> from wxdi.dq_validator import Validator, ValidationRule, LengthCheck
        >>> from wxdi.dq_validator.integrations import SparkValidator
        >>> from pyspark.sql import SparkSession
        >>>
        >>> spark = SparkSession.builder.getOrCreate()
        >>>
        >>> # Setup validator
        >>> validator = Validator(metadata)
        >>> validator.add_rule(ValidationRule('name').add_check(LengthCheck(min_length=2)))
        >>>
        >>> # Create Spark validator
        >>> spark_validator = SparkValidator(validator)
        >>>
        >>> # Validate DataFrame (lazy, distributed)
        >>> df_validated = spark_validator.add_validation_column(df)
        >>> summary = spark_validator.get_summary_statistics(df)
    """

    def __init__(self, validator, column_prefix: Optional[str] = None):
        """
        Initialize Spark validator.

        Args:
            validator: Configured Validator instance with validation rules
            column_prefix: Prefix for validation columns (default: `dq_`)
        """
        super().__init__(validator, column_prefix)
        self._validation_udf: Optional[Any] = None

    def _create_validation_udf(self) -> Any:
        """
        Create PySpark UDF for row validation.

        This UDF is created once and reused for all validations.
        The validator is captured in the closure and serialized by Spark.

        Returns:
            UDF that validates a row and returns validation result struct
        """
        # Capture validator in closure (Spark will serialize it)
        validator = self.validator

        # Define return schema for validation result (SAME AS PANDAS)
        result_schema = StructType(
            [
                StructField("is_valid", BooleanType(), False),
                StructField("score", StringType(), False),
                StructField("pass_rate", FloatType(), False),
                StructField("total_checks", IntegerType(), False),
                StructField("passed_checks", IntegerType(), False),
                StructField("failed_checks", IntegerType(), False),
                StructField("error_count", IntegerType(), False),
                StructField("errors", ArrayType(StringType()), False),
            ]
        )

        def validate_row_impl(row):
            """
            Validate a single row.

            This function runs in Spark workers (distributed).

            Args:
                row: Spark Row (struct) with fields in metadata column order

            Returns:
                Validation result as tuple (matching struct schema)
            """
            # Unpack struct Row into ordered list of values
            record = list(row)

            # Validate using core validator
            result = validator.validate(record)

            # Convert errors to JSON strings
            error_messages = [json.dumps(e.to_dict()) for e in result.errors]

            # Return tuple matching struct schema
            return (
                result.is_valid,
                result.score,
                result.pass_rate,
                result.total_checks,
                result.passed_checks,
                result.failed_checks,
                len(result.errors),
                error_messages,
            )

        return udf(validate_row_impl, result_schema)

    def _align_dataframe_to_metadata(self, df: SparkDataFrame) -> SparkDataFrame:
        """
        Reorder DataFrame columns to match metadata order.

        This ensures that when we create the struct, the column order
        matches what the validator expects.

        Args:
            df: Input Spark DataFrame

        Returns:
            DataFrame with columns in metadata order

        Raises:
            ValueError: If required columns are missing or conflicts exist
        """
        metadata_columns = [
            col_meta.name for col_meta in self.validator.metadata.columns
        ]

        # Check for missing columns
        df_columns = set(df.columns)
        missing_cols = set(metadata_columns) - df_columns
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

        # Select columns in metadata order
        return df.select(*metadata_columns)

    def get_summary_statistics(self, df: SparkDataFrame) -> Dict[str, Any]:
        """
        Get validation summary using distributed aggregation.

        NO DATA COLLECTED TO DRIVER - All aggregation happens in workers.
        Only the final summary statistics are collected (O(1) memory).

        Args:
            df: Spark DataFrame to validate

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
        # Add validation column (distributed operation)
        df_with_validation = self.add_validation_column(df)

        # Aggregate in workers, collect only summary (O(1) memory on driver)
        result_col = self.result_column_name
        summary = df_with_validation.agg(
            count("*").alias("total_rows"),
            spark_sum(col(f"{result_col}.is_valid").cast("int")).alias("valid_rows"),
            spark_sum(f"{result_col}.total_checks").alias("total_checks"),
            spark_sum(f"{result_col}.passed_checks").alias("passed_checks"),
            spark_sum(f"{result_col}.failed_checks").alias("failed_checks"),
        ).collect()[0]

        total_rows = summary["total_rows"]
        # spark_sum returns None when aggregating over an empty DataFrame
        valid_rows = summary["valid_rows"] or 0

        return {
            "total_rows": total_rows,
            "valid_rows": valid_rows,
            "invalid_rows": total_rows - valid_rows,
            "pass_rate": (valid_rows / total_rows * 100) if total_rows > 0 else 0.0,
            "total_checks": summary["total_checks"] or 0,
            "passed_checks": summary["passed_checks"] or 0,
            "failed_checks": summary["failed_checks"] or 0,
        }

    def add_validation_column(self, df: SparkDataFrame) -> SparkDataFrame:
        """
        Add validation result struct column - FULLY DISTRIBUTED, NO COLLECTION.

        This method adds a single column containing a struct with all
        validation results. All processing happens in Spark workers.

        Args:
            df: Spark DataFrame to validate

        Returns:
            DataFrame with {prefix}validation_result struct column added.
            All processing happens in workers (lazy evaluation).

        Example:
            >>> df_validated = validator.add_validation_column(df)
            >>> # Access struct fields
            >>> df_validated.select('dq_validation_result.is_valid').show()
        """
        # Align DataFrame to metadata order
        aligned_df = self._align_dataframe_to_metadata(df)

        # Create UDF if not exists
        if self._validation_udf is None:
            self._validation_udf = self._create_validation_udf()

        # Get column names in metadata order
        metadata_columns = [
            col_meta.name for col_meta in self.validator.metadata.columns
        ]

        # Apply validation UDF (GUARANTEED ORDER via struct)
        # struct(*metadata_columns) creates struct with columns in exact order
        # Assert for type checker - we know it's not None after the check above
        assert self._validation_udf is not None
        df_with_validation = aligned_df.withColumn(
            self.result_column_name, self._validation_udf(struct(*metadata_columns))
        )

        return df_with_validation

    def get_invalid_rows(self, df: SparkDataFrame) -> SparkDataFrame:
        """
        Filter invalid rows - FULLY DISTRIBUTED.

        This is a convenience method that adds validation column and
        filters to return only rows that failed validation.
        No data is collected to the driver.

        Args:
            df: Spark DataFrame to validate

        Returns:
            DataFrame containing only invalid rows (lazy evaluation, no collection)

        Example:
            >>> invalid_df = validator.get_invalid_rows(df)
            >>> invalid_df.write.parquet('s3://bucket/invalid-rows/')
        """
        df_with_validation = self.add_validation_column(df)
        return df_with_validation.filter(
            col(f"{self.result_column_name}.is_valid") == False
        )

    def get_valid_rows(self, df: SparkDataFrame) -> SparkDataFrame:
        """
        Filter valid rows - FULLY DISTRIBUTED.

        This is a convenience method that adds validation column and
        filters to return only rows that passed validation.
        No data is collected to the driver.

        Args:
            df: Spark DataFrame to validate

        Returns:
            DataFrame containing only valid rows (lazy evaluation, no collection)

        Example:
            >>> valid_df = validator.get_valid_rows(df)
            >>> valid_df.write.parquet('s3://bucket/valid-rows/')
        """
        df_with_validation = self.add_validation_column(df)
        return df_with_validation.filter(
            col(f"{self.result_column_name}.is_valid") == True
        )

    def expand_validation_column(self, df: SparkDataFrame) -> SparkDataFrame:
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
            >>> df_expanded.select('name', 'dq_is_valid', 'dq_score').show()
        """
        if self.result_column_name not in df.columns:
            raise ValueError(
                f"DataFrame does not contain validation result column "
                f"'{self.result_column_name}'. Call add_validation_column() first."
            )

        # Expand struct into separate columns with prefix
        result_col = self.result_column_name
        return df.select(
            "*",
            col(f"{result_col}.is_valid").alias(f"{self.column_prefix}is_valid"),
            col(f"{result_col}.score").alias(f"{self.column_prefix}score"),
            col(f"{result_col}.pass_rate").alias(f"{self.column_prefix}pass_rate"),
            col(f"{result_col}.total_checks").alias(
                f"{self.column_prefix}total_checks"
            ),
            col(f"{result_col}.passed_checks").alias(
                f"{self.column_prefix}passed_checks"
            ),
            col(f"{result_col}.failed_checks").alias(
                f"{self.column_prefix}failed_checks"
            ),
            col(f"{result_col}.error_count").alias(f"{self.column_prefix}error_count"),
            col(f"{result_col}.errors").alias(f"{self.column_prefix}errors"),
        ).drop(result_col)

    def write_validation_report(
        self, df: SparkDataFrame, output_path: str, format: str = "parquet"
    ) -> None:
        """
        Write validation results to storage WITHOUT collecting to driver.

        This method validates the DataFrame and writes the results directly
        from workers to the specified storage location.

        Args:
            df: DataFrame to validate
            output_path: Path to write results (supports S3, HDFS, local, etc.)
            format: Output format ('parquet', 'csv', 'json', etc.)

        Example:
            >>> validator.write_validation_report(
            ...     df,
            ...     's3://bucket/validation-results/',
            ...     format='parquet'
            ... )
        """
        df_with_validation = self.add_validation_column(df)

        # CSV does not support struct or array columns — expand struct and
        # convert the errors array to a JSON string so CSV can handle it.
        if format.lower() == "csv":
            df_with_validation = self.expand_validation_column(df_with_validation)
            errors_col = f"{self.column_prefix}errors"
            df_with_validation = df_with_validation.withColumn(
                errors_col, to_json(col(errors_col))
            )

        # Write directly from workers - no driver collection
        df_with_validation.write.format(format).mode("overwrite").save(output_path)

    def get_error_sample(self, df: SparkDataFrame, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get sample of validation errors (safe for large datasets).

        This method collects only a limited sample of errors, making it
        safe to use even with very large DataFrames.

        Args:
            df: DataFrame to validate
            limit: Maximum number of error samples to collect (default: 100)

        Returns:
            List of dicts, each with keys:
            - "row": dict of the original row field values
            - "errors": list of error JSON strings for that row

        Example:
            >>> error_sample = validator.get_error_sample(df, limit=50)
            >>> for sample in error_sample[:5]:
            ...     print(f"Row {sample['row']} has {len(sample['errors'])} errors")
        """
        invalid_df = self.get_invalid_rows(df)

        # Determine original data columns (exclude the validation result column)
        data_columns = [c for c in invalid_df.columns if c != self.result_column_name]

        # Take only limited sample (safe to collect)
        sample_rows = (
            invalid_df.limit(limit)
            .collect()
        )

        return [
            {
                "row": {c: row[c] for c in data_columns},
                "errors": list(row[self.result_column_name]["errors"]),
            }
            for row in sample_rows
        ]

    def get_detailed_statistics(self, df: SparkDataFrame) -> Dict[str, Any]:
        """
        Get detailed validation statistics with column and check-level breakdown.
        
        This method uses distributed aggregation in Spark to compute statistics
        by column and check type WITHOUT collecting all rows to the driver.
        Only the aggregated statistics are collected (O(columns * checks) memory).
        
        Note: This returns a dictionary with statistics, not a ValidationResultConsolidated
        object, because we compute aggregations in Spark workers for efficiency.
        
        Args:
            df: Spark DataFrame to validate
        
        Returns:
            Dictionary with detailed statistics:
            - overall: Overall statistics (total_records, valid_records, etc.)
            - by_column: Statistics grouped by column name {column: {passed, failed, total}}
            - by_check: Statistics grouped by check type {check: {passed, failed, total}}
            - combined: Statistics grouped by (column, check) {(col, check): {passed, failed, total}}
        
        Example:
            >>> stats = validator.get_detailed_statistics(df)
            >>>
            >>> # Get overall stats
            >>> print(stats['overall'])
            >>>
            >>> # Get stats for a specific column
            >>> email_stats = stats['by_column'].get('email', {})
            >>> print(f"Email: {email_stats['passed']}/{email_stats['total']} passed")
            >>>
            >>> # Get stats for a specific check type
            >>> format_stats = stats['by_check'].get('format_check', {})
            >>> print(f"Format check: {format_stats['failed']} failures")
            >>>
            >>> # Get combined stats
            >>> combined = stats['combined'].get(('email', 'format_check'), {})
        """
        # Add validation column (distributed)
        df_with_validation = self.add_validation_column(df)
        result_col = self.result_column_name
        
        # Get overall statistics and total row count
        overall_stats = self.get_summary_statistics(df)
        total_records = overall_stats['total_rows']
        
        # For column and check-level statistics, we need to explode the errors array
        # and aggregate by column and check type
        # This is done in workers, only aggregated results are collected
        
        # Explode errors to get one row per error
        df_errors = df_with_validation.select(
            col(f"{result_col}.errors").alias("errors")
        ).filter(
            col("errors").isNotNull() & (col("errors") != [])
        ).select(
            explode(col("errors")).alias("error_json")
        )
        
        # Parse error JSON and extract column and check
        from pyspark.sql.functions import from_json
        
        # Define error schema
        error_schema = StructType([
            StructField("column", StringType(), True),
            StructField("check", StringType(), True),
            StructField("message", StringType(), True),
            StructField("value", StringType(), True),
            StructField("expected", StringType(), True),
        ])
        
        df_parsed_errors = df_errors.select(
            from_json(col("error_json"), error_schema).alias("error")
        ).select(
            col("error.column").alias("column"),
            col("error.check").alias("check")
        )
        
        # Aggregate by column
        by_column_df = df_parsed_errors.groupBy("column").count()
        by_column = {
            row.column: {
                'failed': row['count'],
                'total': total_records,
                'passed': total_records - row['count']
            }
            for row in by_column_df.collect()
        }
        
        # Aggregate by check
        by_check_df = df_parsed_errors.groupBy("check").count()
        by_check = {
            row.check: {
                'failed': row['count'],
                'total': total_records,
                'passed': total_records - row['count']
            }
            for row in by_check_df.collect()
        }
        
        # Aggregate by column and check combination
        by_combined_df = df_parsed_errors.groupBy("column", "check").count()
        combined = {
            (row.column, row.check): {
                'failed': row['count'],
                'total': total_records,
                'passed': total_records - row['count']
            }
            for row in by_combined_df.collect()
        }
        
        return {
            'overall': overall_stats,
            'by_column': by_column,
            'by_check': by_check,
            'combined': combined
        }

    def __repr__(self) -> str:
        """String representation of the validator."""
        return (
            f"SparkValidator("
            f"table='{self.validator.metadata.table_name}', "
            f"rules={len(self.validator.rules)}, "
            f"prefix='{self.column_prefix}')"
        )
