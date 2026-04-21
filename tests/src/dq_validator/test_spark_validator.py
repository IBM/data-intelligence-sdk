"""
   Copyright 2026 IBM Corporation

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
"""
Unit tests for SparkValidator

Tests the PySpark DataFrame integration including:
- Initialization and configuration
- Summary statistics calculation (distributed)
- Validation column addition (UDF-based)
- Invalid/valid row filtering
- Column expansion
- Validation report writing
- Error sampling
- Distributed processing
"""

import math
import pytest
import sys
from typing import Dict, Any
import tempfile
import shutil

# Check if pyspark is available
try:
    from pyspark.sql import SparkSession
    from pyspark.sql.types import StructType, StructField, IntegerType, StringType

    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False

from wxdi.dq_validator import (
    AssetMetadata,
    ColumnMetadata,
    DataType,
    Validator,
    ValidationRule,
)
from wxdi.dq_validator.checks import (
    LengthCheck,
    ValidValuesCheck,
    ComparisonCheck,
    ComparisonOperator,
)

if PYSPARK_AVAILABLE:
    from wxdi.dq_validator.integrations import SparkValidator


# Skip all tests if pyspark is not available
pytestmark = pytest.mark.skipif(not PYSPARK_AVAILABLE, reason="pyspark not installed")


@pytest.fixture(scope="module")
def spark():
    """Create Spark session for testing"""
    if not PYSPARK_AVAILABLE:
        return None

    # Set Python executable and path for Spark workers
    import os
    from pathlib import Path

    python_path = sys.executable
    os.environ["PYSPARK_PYTHON"] = python_path
    os.environ["PYSPARK_DRIVER_PYTHON"] = python_path

    # Add src directory to PYTHONPATH so workers can import dq_validator
    src_path = str(Path(__file__).parent.parent / "src")
    current_pythonpath = os.environ.get("PYTHONPATH", "")
    if current_pythonpath:
        os.environ["PYTHONPATH"] = f"{src_path}{os.pathsep}{current_pythonpath}"
    else:
        os.environ["PYTHONPATH"] = src_path

    spark = (
        SparkSession.builder.appName("DataQualityTests")
        .master("local[2]")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.python.worker.reuse", "false")
        .config("spark.sql.execution.pyspark.udf.faulthandler.enabled", "true")
        .config("spark.python.worker.faulthandler.enabled", "true")
        .getOrCreate()
    )

    yield spark

    spark.stop()


@pytest.fixture
def sample_metadata():
    """Create sample metadata for testing"""
    return AssetMetadata(
        table_name="test_table",
        columns=[
            ColumnMetadata("id", DataType.INTEGER),
            ColumnMetadata("name", DataType.STRING, length=50),
            ColumnMetadata("age", DataType.INTEGER),
            ColumnMetadata("status", DataType.STRING, length=20),
        ],
    )


@pytest.fixture
def sample_validator(sample_metadata):
    """Create sample validator with rules"""
    validator = Validator(sample_metadata)

    # Add validation rules
    validator.add_rule(
        ValidationRule("name").add_check(LengthCheck(min_length=2, max_length=50))
    )
    validator.add_rule(
        ValidationRule("age").add_check(
            ComparisonCheck(
                operator=ComparisonOperator.GREATER_THAN_OR_EQUAL, target_value=18
            )
        )
    )
    validator.add_rule(
        ValidationRule("status").add_check(
            ValidValuesCheck(["active", "inactive"], case_sensitive=False)
        )
    )

    return validator


@pytest.fixture
def sample_dataframe(spark):
    """Create sample Spark DataFrame for testing"""
    if not PYSPARK_AVAILABLE:
        return None

    data = [
        (1, "Alice", 25, "active"),
        (2, "B", 30, "ACTIVE"),
        (3, "Charlie", 17, "inactive"),
        (4, "David", 35, "pending"),
        (5, "Eve", 40, "Active"),
    ]

    schema = StructType(
        [
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("age", IntegerType(), True),
            StructField("status", StringType(), True),
        ]
    )

    return spark.createDataFrame(data, schema)


class TestSparkValidatorInitialization:
    """Test SparkValidator initialization"""

    def test_basic_initialization(self, sample_validator):
        """Test basic initialization with default parameters"""
        spark_validator = SparkValidator(sample_validator)

        assert spark_validator.validator == sample_validator
        assert spark_validator.column_prefix == "dq_"

    def test_custom_column_prefix(self, sample_validator):
        """Test initialization with custom column prefix"""
        spark_validator = SparkValidator(sample_validator, column_prefix="validation_")

        assert spark_validator.column_prefix == "validation_"

    def test_string_representation(self, sample_validator):
        """Test string representation of validator"""
        spark_validator = SparkValidator(sample_validator)
        str_repr = str(spark_validator)

        assert "SparkValidator" in str_repr


class TestSummaryStatistics:
    """Test summary statistics calculation with distributed aggregation"""

    def test_basic_summary(self, sample_validator, sample_dataframe):
        """Test basic summary statistics"""
        spark_validator = SparkValidator(sample_validator)
        summary = spark_validator.get_summary_statistics(sample_dataframe)

        assert isinstance(summary, dict)
        assert "total_rows" in summary
        assert "valid_rows" in summary
        assert "invalid_rows" in summary
        assert "pass_rate" in summary
        assert "total_checks" in summary
        assert "passed_checks" in summary
        assert "failed_checks" in summary

        assert summary["total_rows"] == 5
        assert summary["valid_rows"] + summary["invalid_rows"] == 5
        assert 0 <= summary["pass_rate"] <= 100

    def test_all_valid_rows(self, spark, sample_validator):
        """Test summary with all valid rows"""
        data = [
            (1, "Alice", 25, "active"),
            (2, "Bob", 30, "inactive"),
            (3, "Charlie", 35, "active"),
        ]

        schema = StructType(
            [
                StructField("id", IntegerType(), True),
                StructField("name", StringType(), True),
                StructField("age", IntegerType(), True),
                StructField("status", StringType(), True),
            ]
        )

        df = spark.createDataFrame(data, schema)

        spark_validator = SparkValidator(sample_validator)
        summary = spark_validator.get_summary_statistics(df)

        assert summary["total_rows"] == 3
        assert summary["valid_rows"] == 3
        assert summary["invalid_rows"] == 0
        assert math.isclose(summary["pass_rate"], 100.0)

    def test_all_invalid_rows(self, spark, sample_validator):
        """Test summary with all invalid rows"""
        data = [
            (1, "A", 15, "pending"),
            (2, "B", 16, "deleted"),
            (3, "C", 17, "archived"),
        ]

        schema = StructType(
            [
                StructField("id", IntegerType(), True),
                StructField("name", StringType(), True),
                StructField("age", IntegerType(), True),
                StructField("status", StringType(), True),
            ]
        )

        df = spark.createDataFrame(data, schema)

        spark_validator = SparkValidator(sample_validator)
        summary = spark_validator.get_summary_statistics(df)

        assert summary["total_rows"] == 3
        assert summary["valid_rows"] == 0
        assert summary["invalid_rows"] == 3
        assert math.isclose(summary["pass_rate"], 0.0, abs_tol=1e-9)

    def test_empty_dataframe(self, spark, sample_validator):
        """Test summary with empty DataFrame"""
        schema = StructType(
            [
                StructField("id", IntegerType(), True),
                StructField("name", StringType(), True),
                StructField("age", IntegerType(), True),
                StructField("status", StringType(), True),
            ]
        )

        df = spark.createDataFrame([], schema)

        spark_validator = SparkValidator(sample_validator)
        summary = spark_validator.get_summary_statistics(df)

        assert summary["total_rows"] == 0
        assert summary["valid_rows"] == 0
        assert summary["invalid_rows"] == 0
        assert math.isclose(summary["pass_rate"], 0.0, abs_tol=1e-9)

    def test_large_dataframe(self, spark, sample_validator):
        """Test summary with large DataFrame (distributed processing)"""
        # Create large dataset
        data = [(i, "Alice", 25, "active") for i in range(1, 1001)]

        schema = StructType(
            [
                StructField("id", IntegerType(), True),
                StructField("name", StringType(), True),
                StructField("age", IntegerType(), True),
                StructField("status", StringType(), True),
            ]
        )

        df = spark.createDataFrame(data, schema)

        spark_validator = SparkValidator(sample_validator)
        summary = spark_validator.get_summary_statistics(df)

        assert summary["total_rows"] == 1000
        assert summary["valid_rows"] == 1000


class TestAddValidationColumn:
    """Test adding validation column using Spark UDF"""

    def test_basic_validation_column(self, sample_validator, sample_dataframe):
        """Test adding validation column"""
        spark_validator = SparkValidator(sample_validator)
        df_validated = spark_validator.add_validation_column(sample_dataframe)

        # Check that original columns are preserved
        original_cols = sample_dataframe.columns
        assert all(col in df_validated.columns for col in original_cols)

        # Check that validation column is added
        assert "dq_validation_result" in df_validated.columns

        # Check that DataFrame has same number of rows
        assert df_validated.count() == sample_dataframe.count()

    def test_validation_result_structure(self, sample_validator, sample_dataframe):
        """Test structure of validation result"""
        spark_validator = SparkValidator(sample_validator)
        df_validated = spark_validator.add_validation_column(sample_dataframe)

        # Get schema of validation column
        validation_col = df_validated.schema["dq_validation_result"]

        # Check that it's a struct type
        assert validation_col.dataType.typeName() == "struct"

        # Check field names
        field_names = [f.name for f in validation_col.dataType.fields]
        assert "is_valid" in field_names
        assert "score" in field_names
        assert "pass_rate" in field_names
        assert "total_checks" in field_names
        assert "passed_checks" in field_names
        assert "failed_checks" in field_names
        assert "error_count" in field_names
        assert "errors" in field_names

    def test_custom_column_prefix(self, sample_validator, sample_dataframe):
        """Test validation column with custom prefix"""
        spark_validator = SparkValidator(sample_validator, column_prefix="val_")
        df_validated = spark_validator.add_validation_column(sample_dataframe)

        assert "val_validation_result" in df_validated.columns
        assert "dq_validation_result" not in df_validated.columns

    def test_column_conflict_detection(self, spark, sample_validator):
        """Test detection of column name conflicts"""
        data = [
            (1, "Alice", 25, "active", "existing_data"),
            (2, "Bob", 30, "inactive", "existing_data"),
        ]

        schema = StructType(
            [
                StructField("id", IntegerType(), True),
                StructField("name", StringType(), True),
                StructField("age", IntegerType(), True),
                StructField("status", StringType(), True),
                StructField("dq_validation_result", StringType(), True),  # Conflict!
            ]
        )

        df = spark.createDataFrame(data, schema)

        spark_validator = SparkValidator(sample_validator)

        with pytest.raises(ValueError, match="already exists"):
            spark_validator.add_validation_column(df)


class TestInvalidRowFiltering:
    """Test filtering invalid rows with distributed operations"""

    def test_get_invalid_rows(self, sample_validator, sample_dataframe):
        """Test getting invalid rows"""
        spark_validator = SparkValidator(sample_validator)
        invalid_df = spark_validator.get_invalid_rows(sample_dataframe)

        # Should have validation column
        assert "dq_validation_result" in invalid_df.columns

        # Collect and check all rows are invalid
        rows = invalid_df.select("dq_validation_result.is_valid").collect()
        for row in rows:
            assert row["is_valid"] is False

    def test_get_valid_rows(self, sample_validator, sample_dataframe):
        """Test getting valid rows"""
        spark_validator = SparkValidator(sample_validator)
        valid_df = spark_validator.get_valid_rows(sample_dataframe)

        # Should have validation column
        assert "dq_validation_result" in valid_df.columns

        # Collect and check all rows are valid
        rows = valid_df.select("dq_validation_result.is_valid").collect()
        for row in rows:
            assert row["is_valid"] is True

    def test_no_invalid_rows(self, spark, sample_validator):
        """Test when there are no invalid rows"""
        data = [
            (1, "Alice", 25, "active"),
            (2, "Bob", 30, "inactive"),
            (3, "Charlie", 35, "active"),
        ]

        schema = StructType(
            [
                StructField("id", IntegerType(), True),
                StructField("name", StringType(), True),
                StructField("age", IntegerType(), True),
                StructField("status", StringType(), True),
            ]
        )

        df = spark.createDataFrame(data, schema)

        spark_validator = SparkValidator(sample_validator)
        invalid_df = spark_validator.get_invalid_rows(df)

        assert invalid_df.count() == 0

    def test_no_valid_rows(self, spark, sample_validator):
        """Test when there are no valid rows"""
        data = [
            (1, "A", 15, "pending"),
            (2, "B", 16, "deleted"),
            (3, "C", 17, "archived"),
        ]

        schema = StructType(
            [
                StructField("id", IntegerType(), True),
                StructField("name", StringType(), True),
                StructField("age", IntegerType(), True),
                StructField("status", StringType(), True),
            ]
        )

        df = spark.createDataFrame(data, schema)

        spark_validator = SparkValidator(sample_validator)
        valid_df = spark_validator.get_valid_rows(df)

        assert valid_df.count() == 0


class TestColumnExpansion:
    """Test expanding validation column"""

    def test_basic_expansion(self, sample_validator, sample_dataframe):
        """Test basic column expansion"""
        spark_validator = SparkValidator(sample_validator)
        df_validated = spark_validator.add_validation_column(sample_dataframe)
        df_expanded = spark_validator.expand_validation_column(df_validated)

        # Check that expanded columns exist
        assert "dq_is_valid" in df_expanded.columns
        assert "dq_score" in df_expanded.columns
        assert "dq_pass_rate" in df_expanded.columns
        assert "dq_total_checks" in df_expanded.columns
        assert "dq_passed_checks" in df_expanded.columns
        assert "dq_failed_checks" in df_expanded.columns
        assert "dq_error_count" in df_expanded.columns
        assert "dq_errors" in df_expanded.columns

        # Original validation column should be removed
        assert "dq_validation_result" not in df_expanded.columns

        # Original columns should be preserved
        original_cols = sample_dataframe.columns
        assert all(col in df_expanded.columns for col in original_cols)

    def test_expansion_with_custom_prefix(self, sample_validator, sample_dataframe):
        """Test expansion with custom prefix"""
        spark_validator = SparkValidator(sample_validator, column_prefix="val_")
        df_validated = spark_validator.add_validation_column(sample_dataframe)
        df_expanded = spark_validator.expand_validation_column(df_validated)

        assert "val_is_valid" in df_expanded.columns
        assert "val_score" in df_expanded.columns
        assert "val_pass_rate" in df_expanded.columns

    def test_expansion_without_validation_column(
        self, sample_validator, sample_dataframe
    ):
        """Test expansion when validation column doesn't exist"""
        spark_validator = SparkValidator(sample_validator)

        with pytest.raises(
            ValueError, match="does not contain validation result column"
        ):
            spark_validator.expand_validation_column(sample_dataframe)


class TestValidationReport:
    """Test validation report writing"""

    def test_write_parquet_report(self, sample_validator, sample_dataframe):
        """Test writing validation report in Parquet format"""
        spark_validator = SparkValidator(sample_validator)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = f"{tmpdir}/validation_report"

            spark_validator.write_validation_report(
                sample_dataframe, output_path=output_path, format="parquet"
            )

            # Verify report was written
            # Note: In real scenario, you'd read back and verify content

    def test_write_csv_report(self, sample_validator, sample_dataframe):
        """Test writing validation report in CSV format"""
        spark_validator = SparkValidator(sample_validator)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = f"{tmpdir}/validation_report"

            spark_validator.write_validation_report(
                sample_dataframe, output_path=output_path, format="csv"
            )

            # Verify report was written


class TestErrorSampling:
    """Test error sampling functionality"""

    def test_get_error_sample(self, sample_validator, sample_dataframe):
        """Test getting error samples"""
        spark_validator = SparkValidator(sample_validator)
        error_samples = spark_validator.get_error_sample(sample_dataframe, limit=10)

        assert isinstance(error_samples, list)
        assert len(error_samples) <= 10

        # Check structure of error samples
        if len(error_samples) > 0:
            sample = error_samples[0]
            assert "row" in sample
            assert "errors" in sample
            assert isinstance(sample["errors"], list)

    def test_error_sample_limit(self, sample_validator, sample_dataframe):
        """Test error sample limit"""
        spark_validator = SparkValidator(sample_validator)

        # Get small sample
        small_sample = spark_validator.get_error_sample(sample_dataframe, limit=2)
        assert len(small_sample) <= 2

        # Get larger sample
        large_sample = spark_validator.get_error_sample(sample_dataframe, limit=100)
        assert len(large_sample) <= 100

    def test_no_errors(self, spark, sample_validator):
        """Test error sampling when there are no errors"""
        data = [(1, "Alice", 25, "active"), (2, "Bob", 30, "inactive")]

        schema = StructType(
            [
                StructField("id", IntegerType(), True),
                StructField("name", StringType(), True),
                StructField("age", IntegerType(), True),
                StructField("status", StringType(), True),
            ]
        )

        df = spark.createDataFrame(data, schema)

        spark_validator = SparkValidator(sample_validator)
        error_samples = spark_validator.get_error_sample(df, limit=10)

        assert len(error_samples) == 0


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_dataframe_with_null_values(self, spark, sample_validator):
        """Test DataFrame with null values"""
        data = [
            (1, "Alice", 25, "active"),
            (2, None, 30, "inactive"),
            (3, "Charlie", None, "active"),
        ]

        schema = StructType(
            [
                StructField("id", IntegerType(), True),
                StructField("name", StringType(), True),
                StructField("age", IntegerType(), True),
                StructField("status", StringType(), True),
            ]
        )

        df = spark.createDataFrame(data, schema)

        spark_validator = SparkValidator(sample_validator)
        summary = spark_validator.get_summary_statistics(df)

        # Should handle nulls gracefully
        assert summary["total_rows"] == 3
        assert summary["invalid_rows"] > 0  # Nulls should cause failures

    def test_distributed_processing_consistency(self, spark, sample_validator):
        """Test that distributed processing produces consistent results"""
        # Create dataset that will be distributed across partitions
        data = [(i, "Alice", 25, "active") for i in range(1, 101)]

        schema = StructType(
            [
                StructField("id", IntegerType(), True),
                StructField("name", StringType(), True),
                StructField("age", IntegerType(), True),
                StructField("status", StringType(), True),
            ]
        )

        df = spark.createDataFrame(data, schema).repartition(4)

        spark_validator = SparkValidator(sample_validator)

        # Run validation multiple times
        summary1 = spark_validator.get_summary_statistics(df)
        summary2 = spark_validator.get_summary_statistics(df)

        # Results should be consistent
        assert summary1 == summary2


class TestIntegrationScenarios:
    """Test complete integration scenarios"""

    def test_complete_workflow(self, sample_validator, sample_dataframe):
        """Test complete validation workflow"""
        spark_validator = SparkValidator(sample_validator)

        # Step 1: Get summary
        summary = spark_validator.get_summary_statistics(sample_dataframe)
        assert summary["total_rows"] == 5

        # Step 2: Add validation column
        df_validated = spark_validator.add_validation_column(sample_dataframe)
        assert "dq_validation_result" in df_validated.columns

        # Step 3: Filter invalid rows
        invalid_df = spark_validator.get_invalid_rows(sample_dataframe)
        assert invalid_df.count() == summary["invalid_rows"]

        # Step 4: Expand columns
        df_expanded = spark_validator.expand_validation_column(df_validated)
        assert "dq_is_valid" in df_expanded.columns

        # Step 5: Get error samples
        error_samples = spark_validator.get_error_sample(sample_dataframe, limit=10)
        assert isinstance(error_samples, list)

    def test_lazy_evaluation(self, sample_validator, sample_dataframe):
        """Test that operations use lazy evaluation"""
        spark_validator = SparkValidator(sample_validator)

        # These operations should not trigger computation
        df_validated = spark_validator.add_validation_column(sample_dataframe)
        invalid_df = spark_validator.get_invalid_rows(sample_dataframe)

        # Only when we call an action (count, collect, etc.) should computation happen
        count = invalid_df.count()
        assert isinstance(count, int)


class TestValidationRowImpl:
    """Test the validate_row_impl function execution and row validation logic"""

    def test_validation_result_content(self, sample_validator, sample_dataframe):
        """Test that validation results contain correct data for each row"""
        spark_validator = SparkValidator(sample_validator)
        df_validated = spark_validator.add_validation_column(sample_dataframe)
        
        # Collect results to verify validation logic execution
        results = df_validated.select("name", "age", "dq_validation_result").collect()
        
        # Verify we have results for all rows
        assert len(results) == 5
        
        # Check that validation results have expected structure
        for row in results:
            validation_result = row["dq_validation_result"]
            
            # Verify all fields are present
            assert "is_valid" in validation_result
            assert "score" in validation_result
            assert "pass_rate" in validation_result
            assert "total_checks" in validation_result
            assert "passed_checks" in validation_result
            assert "failed_checks" in validation_result
            assert "error_count" in validation_result
            assert "errors" in validation_result
            
            # Verify types
            assert isinstance(validation_result["is_valid"], bool)
            assert isinstance(validation_result["score"], str)  # Score is a string like "3/3"
            assert isinstance(validation_result["pass_rate"], (int, float))
            assert isinstance(validation_result["total_checks"], int)
            assert isinstance(validation_result["passed_checks"], int)
            assert isinstance(validation_result["failed_checks"], int)
            assert isinstance(validation_result["error_count"], int)
            assert isinstance(validation_result["errors"], list)
            
            # Verify logical consistency
            assert validation_result["total_checks"] == (
                validation_result["passed_checks"] + validation_result["failed_checks"]
            )
            assert validation_result["error_count"] == len(validation_result["errors"])

    def test_row_conversion_to_list(self, spark, sample_validator):
        """Test that Spark Row is correctly converted to list for validation"""
        # Create a simple dataframe with known values
        data = [
            (1, "Alice", 25, "active"),
            (2, "Bob", 30, "inactive"),
        ]
        
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("age", IntegerType(), True),
            StructField("status", StringType(), True),
        ])
        
        df = spark.createDataFrame(data, schema)
        
        spark_validator = SparkValidator(sample_validator)
        df_validated = spark_validator.add_validation_column(df)
        
        # Collect and verify that validation was performed on list-converted rows
        results = df_validated.collect()
        
        for row in results:
            validation_result = row["dq_validation_result"]
            # If validation ran successfully, it means list(row) conversion worked
            assert validation_result is not None
            assert "is_valid" in validation_result
            
            # Verify that checks were actually executed (not just returning empty results)
            assert validation_result["total_checks"] > 0

    def test_validation_with_errors(self, spark, sample_validator):
        """Test that validation errors are properly captured in JSON format"""
        # Create data that will fail validation
        data = [
            (1, "A", 15, "invalid_status"),  # Short name, young age, invalid status
        ]
        
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("age", IntegerType(), True),
            StructField("status", StringType(), True),
        ])
        
        df = spark.createDataFrame(data, schema)
        
        spark_validator = SparkValidator(sample_validator)
        df_validated = spark_validator.add_validation_column(df)
        
        # Collect and verify error messages
        result = df_validated.collect()[0]
        validation_result = result["dq_validation_result"]
        
        # Should have validation errors
        assert validation_result["is_valid"] == False
        assert validation_result["error_count"] > 0
        assert len(validation_result["errors"]) > 0
        
        # Verify errors are JSON strings
        import json
        for error_str in validation_result["errors"]:
            assert isinstance(error_str, str)
            # Should be valid JSON
            error_dict = json.loads(error_str)
            assert isinstance(error_dict, dict)
            # Should have expected error fields
            assert "column" in error_dict or "check" in error_dict


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
