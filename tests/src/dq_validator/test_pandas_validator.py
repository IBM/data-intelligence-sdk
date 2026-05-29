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
Unit tests for PandasValidator

Tests the Pandas DataFrame integration including:
- Initialization and configuration
- Summary statistics calculation
- Validation column addition
- Invalid/valid row filtering
- Column expansion
- Chunked processing
- Error handling
"""

import math
import pytest
import sys
from typing import Dict, Any

# Check if pandas is available
try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

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

if PANDAS_AVAILABLE:
    from wxdi.dq_validator.integrations import PandasValidator


# Skip all tests if pandas is not available
pytestmark = pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")


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
def sample_dataframe():
    """Create sample DataFrame for testing"""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "B", "Charlie", "David", "Eve"],
            "age": [25, 30, 17, 35, 40],
            "status": ["active", "ACTIVE", "inactive", "pending", "Active"],
        }
    )


class TestPandasValidatorInitialization:
    """Test PandasValidator initialization"""

    def test_basic_initialization(self, sample_validator):
        """Test basic initialization with default parameters"""
        pandas_validator = PandasValidator(sample_validator)

        assert pandas_validator.validator == sample_validator
        assert pandas_validator.chunk_size == 10000
        assert pandas_validator.column_prefix == "dq_"

    def test_custom_chunk_size(self, sample_validator):
        """Test initialization with custom chunk size"""
        pandas_validator = PandasValidator(sample_validator, chunk_size=5000)

        assert pandas_validator.chunk_size == 5000

    def test_custom_column_prefix(self, sample_validator):
        """Test initialization with custom column prefix"""
        pandas_validator = PandasValidator(
            sample_validator, column_prefix="validation_"
        )

        assert pandas_validator.column_prefix == "validation_"

    def test_invalid_chunk_size(self, sample_validator):
        """Test initialization with invalid chunk size"""
        with pytest.raises(ValueError, match="chunk_size must be positive"):
            PandasValidator(sample_validator, chunk_size=0)

        with pytest.raises(ValueError, match="chunk_size must be positive"):
            PandasValidator(sample_validator, chunk_size=-100)


class TestSummaryStatistics:
    """Test summary statistics calculation"""

    def test_basic_summary(self, sample_validator, sample_dataframe):
        """Test basic summary statistics"""
        pandas_validator = PandasValidator(sample_validator)
        summary = pandas_validator.get_summary_statistics(sample_dataframe)

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

    def test_all_valid_rows(self, sample_validator):
        """Test summary with all valid rows"""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 35],
                "status": ["active", "inactive", "active"],
            }
        )

        pandas_validator = PandasValidator(sample_validator)
        summary = pandas_validator.get_summary_statistics(df)

        assert summary["total_rows"] == 3
        assert summary["valid_rows"] == 3
        assert summary["invalid_rows"] == 0
        assert math.isclose(summary["pass_rate"], 100.0)

    def test_all_invalid_rows(self, sample_validator):
        """Test summary with all invalid rows"""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["A", "B", "C"],  # All too short
                "age": [15, 16, 17],  # All under 18
                "status": ["pending", "deleted", "archived"],  # All invalid
            }
        )

        pandas_validator = PandasValidator(sample_validator)
        summary = pandas_validator.get_summary_statistics(df)

        assert summary["total_rows"] == 3
        assert summary["valid_rows"] == 0
        assert summary["invalid_rows"] == 3
        assert math.isclose(summary["pass_rate"], 0.0, abs_tol=1e-9)

    def test_empty_dataframe(self, sample_validator):
        """Test summary with empty DataFrame"""
        df = pd.DataFrame(columns=["id", "name", "age", "status"])

        pandas_validator = PandasValidator(sample_validator)
        summary = pandas_validator.get_summary_statistics(df)

        assert summary["total_rows"] == 0
        assert summary["valid_rows"] == 0
        assert summary["invalid_rows"] == 0
        assert math.isclose(summary["pass_rate"], 0.0, abs_tol=1e-9)

    def test_chunked_processing(self, sample_validator):
        """Test summary with chunked processing"""
        # Create DataFrame larger than chunk size
        df = pd.DataFrame(
            {
                "id": range(1, 101),
                "name": ["Alice"] * 100,
                "age": [25] * 100,
                "status": ["active"] * 100,
            }
        )

        pandas_validator = PandasValidator(sample_validator, chunk_size=30)
        summary = pandas_validator.get_summary_statistics(df)

        assert summary["total_rows"] == 100
        assert summary["valid_rows"] == 100


class TestAddValidationColumn:
    """Test adding validation column to DataFrame"""

    def test_basic_validation_column(self, sample_validator, sample_dataframe):
        """Test adding validation column"""
        pandas_validator = PandasValidator(sample_validator)
        df_validated = pandas_validator.add_validation_column(sample_dataframe)

        # Check that original columns are preserved
        assert all(col in df_validated.columns for col in sample_dataframe.columns)

        # Check that validation column is added
        assert "dq_validation_result" in df_validated.columns

        # Check that DataFrame has same number of rows
        assert len(df_validated) == len(sample_dataframe)

    def test_validation_result_structure(self, sample_validator, sample_dataframe):
        """Test structure of validation result"""
        pandas_validator = PandasValidator(sample_validator)
        df_validated = pandas_validator.add_validation_column(sample_dataframe)

        # Check first validation result
        result = df_validated["dq_validation_result"].iloc[0]

        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "score" in result
        assert "pass_rate" in result
        assert "total_checks" in result
        assert "passed_checks" in result
        assert "failed_checks" in result
        assert "error_count" in result
        assert "errors" in result

        assert isinstance(result["is_valid"], bool)
        assert isinstance(result["score"], str)
        assert isinstance(result["pass_rate"], float)
        assert isinstance(result["errors"], list)

    def test_custom_column_prefix(self, sample_validator, sample_dataframe):
        """Test validation column with custom prefix"""
        pandas_validator = PandasValidator(sample_validator, column_prefix="val_")
        df_validated = pandas_validator.add_validation_column(sample_dataframe)

        assert "val_validation_result" in df_validated.columns
        assert "dq_validation_result" not in df_validated.columns

    def test_column_conflict_detection(self, sample_validator):
        """Test detection of column name conflicts"""
        df = pd.DataFrame(
            {
                "id": [1, 2],
                "name": ["Alice", "Bob"],
                "age": [25, 30],
                "status": ["active", "inactive"],
                "dq_validation_result": ["existing", "data"],  # Conflict!
            }
        )

        pandas_validator = PandasValidator(sample_validator)

        with pytest.raises(ValueError, match="already exists"):
            pandas_validator.add_validation_column(df)


class TestInvalidRowFiltering:
    """Test filtering invalid rows"""

    def test_get_invalid_rows(self, sample_validator, sample_dataframe):
        """Test getting invalid rows"""
        pandas_validator = PandasValidator(sample_validator)
        invalid_df = pandas_validator.get_invalid_rows(sample_dataframe)

        # Should have validation column
        assert "dq_validation_result" in invalid_df.columns

        # All rows should be invalid
        for _, row in invalid_df.iterrows():
            assert row["dq_validation_result"]["is_valid"] is False

    def test_get_valid_rows(self, sample_validator, sample_dataframe):
        """Test getting valid rows"""
        pandas_validator = PandasValidator(sample_validator)
        valid_df = pandas_validator.get_valid_rows(sample_dataframe)

        # Should have validation column
        assert "dq_validation_result" in valid_df.columns

        # All rows should be valid
        for _, row in valid_df.iterrows():
            assert row["dq_validation_result"]["is_valid"] is True

    def test_no_invalid_rows(self, sample_validator):
        """Test when there are no invalid rows"""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 35],
                "status": ["active", "inactive", "active"],
            }
        )

        pandas_validator = PandasValidator(sample_validator)
        invalid_df = pandas_validator.get_invalid_rows(df)

        assert len(invalid_df) == 0

    def test_no_valid_rows(self, sample_validator):
        """Test when there are no valid rows"""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["A", "B", "C"],
                "age": [15, 16, 17],
                "status": ["pending", "deleted", "archived"],
            }
        )

        pandas_validator = PandasValidator(sample_validator)
        valid_df = pandas_validator.get_valid_rows(df)

        assert len(valid_df) == 0


class TestColumnExpansion:
    """Test expanding validation column"""

    def test_basic_expansion(self, sample_validator, sample_dataframe):
        """Test basic column expansion"""
        pandas_validator = PandasValidator(sample_validator)
        df_validated = pandas_validator.add_validation_column(sample_dataframe)
        df_expanded = pandas_validator.expand_validation_column(df_validated)

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
        assert all(col in df_expanded.columns for col in sample_dataframe.columns)

    def test_expansion_with_custom_prefix(self, sample_validator, sample_dataframe):
        """Test expansion with custom prefix"""
        pandas_validator = PandasValidator(sample_validator, column_prefix="val_")
        df_validated = pandas_validator.add_validation_column(sample_dataframe)
        df_expanded = pandas_validator.expand_validation_column(df_validated)

        assert "val_is_valid" in df_expanded.columns
        assert "val_score" in df_expanded.columns
        assert "val_pass_rate" in df_expanded.columns

    def test_expansion_without_validation_column(
        self, sample_validator, sample_dataframe
    ):
        """Test expansion when validation column doesn't exist"""
        pandas_validator = PandasValidator(sample_validator)

        with pytest.raises(
            ValueError, match="does not contain validation result column"
        ):
            pandas_validator.expand_validation_column(sample_dataframe)


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_dataframe_with_missing_columns(self, sample_validator):
        """Test DataFrame missing required columns"""
        df = pd.DataFrame(
            {
                "id": [1, 2],
                "name": ["Alice", "Bob"],
                # Missing 'age' and 'status' columns
            }
        )

        pandas_validator = PandasValidator(sample_validator)

        # Should raise error when trying to validate
        with pytest.raises(Exception):
            pandas_validator.get_summary_statistics(df)

    def test_dataframe_with_null_values(self, sample_validator):
        """Test DataFrame with null values"""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", None, "Charlie"],
                "age": [25, 30, None],
                "status": ["active", "inactive", None],
            }
        )

        pandas_validator = PandasValidator(sample_validator)
        summary = pandas_validator.get_summary_statistics(df)

        # Should handle nulls gracefully
        assert summary["total_rows"] == 3
        assert summary["invalid_rows"] > 0  # Nulls should cause failures

    def test_large_dataframe_chunked_processing(self, sample_validator):
        """Test chunked processing with large DataFrame"""
        # Create large DataFrame
        df = pd.DataFrame(
            {
                "id": range(1, 10001),
                "name": ["Alice"] * 10000,
                "age": [25] * 10000,
                "status": ["active"] * 10000,
            }
        )

        pandas_validator = PandasValidator(sample_validator, chunk_size=1000)
        summary = pandas_validator.get_summary_statistics(df)

        assert summary["total_rows"] == 10000
        assert summary["valid_rows"] == 10000

    def test_string_representation(self, sample_validator):
        """Test string representation of validator"""
        pandas_validator = PandasValidator(sample_validator, chunk_size=5000)
        str_repr = str(pandas_validator)

        assert "PandasValidator" in str_repr
        assert "5000" in str_repr


class TestIntegrationScenarios:
    """Test complete integration scenarios"""

    def test_complete_workflow(self, sample_validator, sample_dataframe):
        """Test complete validation workflow"""
        pandas_validator = PandasValidator(sample_validator)

        # Step 1: Get summary
        summary = pandas_validator.get_summary_statistics(sample_dataframe)
        assert summary["total_rows"] == 5

        # Step 2: Add validation column
        df_validated = pandas_validator.add_validation_column(sample_dataframe)
        assert "dq_validation_result" in df_validated.columns

        # Step 3: Filter invalid rows
        invalid_df = pandas_validator.get_invalid_rows(sample_dataframe)
        assert len(invalid_df) == summary["invalid_rows"]

        # Step 4: Expand columns
        df_expanded = pandas_validator.expand_validation_column(df_validated)
        assert "dq_is_valid" in df_expanded.columns

    def test_multiple_validations_same_dataframe(
        self, sample_validator, sample_dataframe
    ):
        """Test running multiple validations on same DataFrame"""
        pandas_validator = PandasValidator(sample_validator)

        # Run validation multiple times
        summary1 = pandas_validator.get_summary_statistics(sample_dataframe)
        summary2 = pandas_validator.get_summary_statistics(sample_dataframe)

        # Results should be consistent
        assert summary1 == summary2

    def test_validation_with_different_chunk_sizes(self, sample_validator):
        """Test that different chunk sizes produce same results"""
        df = pd.DataFrame(
            {
                "id": range(1, 101),
                "name": ["Alice"] * 100,
                "age": [25] * 100,
                "status": ["active"] * 100,
            }
        )

        validator1 = PandasValidator(sample_validator, chunk_size=10)
        validator2 = PandasValidator(sample_validator, chunk_size=50)

        summary1 = validator1.get_summary_statistics(df)
        summary2 = validator2.get_summary_statistics(df)

        # Results should be identical regardless of chunk size
        assert summary1 == summary2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
