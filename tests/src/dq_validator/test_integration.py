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
Integration tests for Data Intelligence SDK
"""

import math
import pytest
from wxdi.dq_validator import (
    AssetMetadata,
    ColumnMetadata,
    DataType,
    Validator,
    ValidationRule,
    ComparisonCheck,
    ComparisonOperator,
    ValidValuesCheck,
    LengthCheck,
)


class TestBasicIntegration:
    """Test basic integration scenarios"""

    def setup_method(self):
        """Set up test metadata"""
        self.metadata = AssetMetadata(
            table_name="test_table",
            columns=[
                ColumnMetadata("id", DataType.INTEGER),
                ColumnMetadata("name", DataType.STRING, length=100),
                ColumnMetadata("age", DataType.INTEGER),
                ColumnMetadata("status", DataType.STRING, length=20),
            ],
        )

    def test_single_rule_single_check_passes(self):
        """Test single rule with single check passes"""
        validator = Validator(self.metadata)
        validator.add_rule(
            ValidationRule("name").add_check(LengthCheck(min_length=2, max_length=50))
        )

        record = [1, "John Doe", 25, "active"]
        result = validator.validate(record)

        assert result.is_valid
        assert result.score == "1/1"
        assert math.isclose(result.pass_rate, 100.0)
        assert len(result.errors) == 0

    def test_single_rule_single_check_fails(self):
        """Test single rule with single check fails"""
        validator = Validator(self.metadata)
        validator.add_rule(
            ValidationRule("name").add_check(LengthCheck(min_length=10, max_length=50))
        )

        record = [1, "John", 25, "active"]
        result = validator.validate(record)

        assert not result.is_valid
        assert result.score == "0/1"
        assert math.isclose(result.pass_rate, 0.0, abs_tol=1e-9)
        assert len(result.errors) == 1
        assert result.errors[0].column_name == "name"

    def test_multiple_rules_all_pass(self):
        """Test multiple rules all pass"""
        validator = Validator(self.metadata)
        validator.add_rule(
            ValidationRule("name").add_check(LengthCheck(min_length=2, max_length=50))
        )
        validator.add_rule(
            ValidationRule("age").add_check(
                ComparisonCheck(operator=">=", target_value=18)
            )
        )
        validator.add_rule(
            ValidationRule("status").add_check(ValidValuesCheck(["active", "inactive"]))
        )

        record = [1, "John Doe", 25, "active"]
        result = validator.validate(record)

        assert result.is_valid
        assert result.score == "3/3"
        assert math.isclose(result.pass_rate, 100.0)

    def test_multiple_rules_some_fail(self):
        """Test multiple rules with some failures"""
        validator = Validator(self.metadata)
        validator.add_rule(
            ValidationRule("name").add_check(LengthCheck(min_length=2, max_length=50))
        )
        validator.add_rule(
            ValidationRule("age").add_check(
                ComparisonCheck(operator=">=", target_value=18)
            )
        )
        validator.add_rule(
            ValidationRule("status").add_check(ValidValuesCheck(["active", "inactive"]))
        )

        record = [1, "John Doe", 15, "pending"]  # age < 18, status invalid
        result = validator.validate(record)

        assert not result.is_valid
        assert result.score == "1/3"
        assert result.pass_rate == pytest.approx(33.33, rel=0.1)
        assert len(result.errors) == 2

    def test_single_rule_multiple_checks(self):
        """Test single rule with multiple checks"""
        validator = Validator(self.metadata)
        validator.add_rule(
            ValidationRule("age")
            .add_check(ComparisonCheck(operator=">=", target_value=18))
            .add_check(ComparisonCheck(operator="<=", target_value=65))
        )

        record = [1, "John Doe", 30, "active"]
        result = validator.validate(record)

        assert result.is_valid
        assert result.score == "2/2"
        assert math.isclose(result.pass_rate, 100.0)


class TestBatchValidation:
    """Test batch validation scenarios"""

    def setup_method(self):
        """Set up test metadata and validator"""
        self.metadata = AssetMetadata(
            table_name="users",
            columns=[
                ColumnMetadata("id", DataType.INTEGER),
                ColumnMetadata("username", DataType.STRING),
                ColumnMetadata("age", DataType.INTEGER),
            ],
        )

        self.validator = Validator(self.metadata)
        self.validator.add_rule(
            ValidationRule("username").add_check(
                LengthCheck(min_length=3, max_length=20)
            )
        )
        self.validator.add_rule(
            ValidationRule("age").add_check(
                ComparisonCheck(operator=">=", target_value=18)
            )
        )

    def test_batch_all_pass(self):
        """Test batch validation with all records passing"""
        records = [[1, "alice", 25], [2, "bob", 30], [3, "charlie", 22]]

        results = self.validator.validate_batch(records)

        assert len(results) == 3
        assert all(r.is_valid for r in results)
        assert all(r.score == "2/2" for r in results)

    def test_batch_some_fail(self):
        """Test batch validation with some failures"""
        records = [
            [1, "alice", 25],  # Pass
            [2, "ab", 30],  # Fail: username too short
            [3, "charlie", 15],  # Fail: age < 18
        ]

        results = self.validator.validate_batch(records)

        assert len(results) == 3
        assert results[0].is_valid
        assert not results[1].is_valid
        assert not results[2].is_valid

        # Check specific errors
        assert len(results[1].errors) == 1
        assert results[1].errors[0].column_name == "username"

        assert len(results[2].errors) == 1
        assert results[2].errors[0].column_name == "age"

    def test_batch_record_indices(self):
        """Test batch validation tracks record indices"""
        records = [
            [1, "alice", 25],
            [2, "bob", 30],
        ]

        results = self.validator.validate_batch(records)

        assert results[0].record_index == 0
        assert results[1].record_index == 1


class TestComplexScenarios:
    """Test complex validation scenarios"""

    def test_column_to_column_comparison(self):
        """Test column-to-column comparison"""
        metadata = AssetMetadata(
            table_name="transactions",
            columns=[
                ColumnMetadata("id", DataType.INTEGER),
                ColumnMetadata("amount", DataType.DECIMAL),
                ColumnMetadata("min_amount", DataType.DECIMAL),
            ],
        )

        validator = Validator(metadata)
        validator.add_rule(
            ValidationRule("amount").add_check(
                ComparisonCheck(operator=">", target_column="min_amount")
            )
        )

        # Pass case
        record_pass = [1, 100.00, 50.00]
        result_pass = validator.validate(record_pass)
        assert result_pass.is_valid

        # Fail case
        record_fail = [2, 30.00, 50.00]
        result_fail = validator.validate(record_fail)
        assert not result_fail.is_valid
        assert (
            "amount (30.0) > min_amount (50.0) failed" in result_fail.errors[0].message
        )

    def test_case_insensitive_validation(self):
        """Test case-insensitive validation"""
        metadata = AssetMetadata(
            table_name="data",
            columns=[
                ColumnMetadata("id", DataType.INTEGER),
                ColumnMetadata("status", DataType.STRING),
            ],
        )

        validator = Validator(metadata)
        validator.add_rule(
            ValidationRule("status").add_check(
                ValidValuesCheck(["active", "inactive"], case_sensitive=False)
            )
        )

        # Test various cases
        test_cases = [
            [1, "active"],
            [2, "ACTIVE"],
            [3, "Active"],
            [4, "AcTiVe"],
        ]

        results = validator.validate_batch(test_cases)
        assert all(r.is_valid for r in results)

    def test_multiple_checks_per_field(self):
        """Test multiple checks on same field"""
        metadata = AssetMetadata(
            table_name="data",
            columns=[
                ColumnMetadata("id", DataType.INTEGER),
                ColumnMetadata("age", DataType.INTEGER),
            ],
        )

        validator = Validator(metadata)
        validator.add_rule(
            ValidationRule("age")
            .add_check(ComparisonCheck(operator=">=", target_value=18))
            .add_check(ComparisonCheck(operator="<=", target_value=65))
            .add_check(ComparisonCheck(operator="!=", target_value=0))
        )

        # All checks pass
        record_pass = [1, 30]
        result_pass = validator.validate(record_pass)
        assert result_pass.is_valid
        assert result_pass.score == "3/3"

        # Some checks fail
        record_fail = [2, 70]  # > 65
        result_fail = validator.validate(record_fail)
        assert not result_fail.is_valid
        assert result_fail.score == "2/3"

    def test_length_check_with_integers(self):
        """Test length check converts integers to strings"""
        metadata = AssetMetadata(
            table_name="data",
            columns=[
                ColumnMetadata("id", DataType.INTEGER),
            ],
        )

        validator = Validator(metadata)
        validator.add_rule(
            ValidationRule("id").add_check(LengthCheck(min_length=4, max_length=6))
        )

        # Pass: 12345 -> "12345" (length 5)
        result_pass = validator.validate([12345])
        assert result_pass.is_valid

        # Fail: 12 -> "12" (length 2)
        result_fail = validator.validate([12])
        assert not result_fail.is_valid


class TestValidationResultDetails:
    """Test ValidationResult details"""

    def test_result_to_dict(self):
        """Test ValidationResult.to_dict()"""
        metadata = AssetMetadata(
            table_name="test",
            columns=[
                ColumnMetadata("id", DataType.INTEGER),
                ColumnMetadata("name", DataType.STRING),
            ],
        )

        validator = Validator(metadata)
        validator.add_rule(ValidationRule("name").add_check(LengthCheck(min_length=5)))

        record = [1, "abc"]
        result = validator.validate(record)

        result_dict = result.to_dict()

        assert "record_index" in result_dict
        assert "is_valid" in result_dict
        assert "score" in result_dict
        assert "pass_rate" in result_dict
        assert "total_checks" in result_dict
        assert "passed_checks" in result_dict
        assert "failed_checks" in result_dict
        assert "errors" in result_dict

        assert result_dict["is_valid"] == False
        assert result_dict["total_checks"] == 1
        assert result_dict["failed_checks"] == 1
        assert len(result_dict["errors"]) == 1

    def test_error_to_dict(self):
        """Test ValidationError.to_dict()"""
        metadata = AssetMetadata(
            table_name="test",
            columns=[
                ColumnMetadata("id", DataType.INTEGER),
                ColumnMetadata("age", DataType.INTEGER),
            ],
        )

        validator = Validator(metadata)
        validator.add_rule(
            ValidationRule("age").add_check(
                ComparisonCheck(operator=">=", target_value=18)
            )
        )

        record = [1, 15]
        result = validator.validate(record)

        error_dict = result.errors[0].to_dict()

        assert "column" in error_dict
        assert "check" in error_dict
        assert "message" in error_dict
        assert "value" in error_dict
        assert "expected" in error_dict

        assert error_dict["column"] == "age"
        assert error_dict["check"] == "comparison_check"


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_record_array(self):
        """Test validation with empty record array"""
        metadata = AssetMetadata(
            table_name="test",
            columns=[
                ColumnMetadata("id", DataType.INTEGER),
            ],
        )

        validator = Validator(metadata)
        validator.add_rule(
            ValidationRule("id").add_check(
                ComparisonCheck(operator=">", target_value=0)
            )
        )

        # Empty record should cause error
        record = []
        result = validator.validate(record)

        assert not result.is_valid
        assert len(result.errors) > 0

    def test_validator_with_no_rules(self):
        """Test validator with no rules"""
        metadata = AssetMetadata(
            table_name="test",
            columns=[
                ColumnMetadata("id", DataType.INTEGER),
            ],
        )

        validator = Validator(metadata)

        record = [1]
        result = validator.validate(record)

        assert result.is_valid
        assert result.total_checks == 0
        assert result.score == "0/0"

    def test_fluent_api_chaining(self):
        """Test fluent API method chaining"""
        metadata = AssetMetadata(
            table_name="test",
            columns=[
                ColumnMetadata("id", DataType.INTEGER),
                ColumnMetadata("name", DataType.STRING),
                ColumnMetadata("age", DataType.INTEGER),
            ],
        )

        # Chain multiple add_rule calls
        validator = (
            Validator(metadata)
            .add_rule(ValidationRule("name").add_check(LengthCheck(min_length=2)))
            .add_rule(
                ValidationRule("age").add_check(
                    ComparisonCheck(operator=">=", target_value=0)
                )
            )
        )

        record = [1, "John", 25]
        result = validator.validate(record)

        assert result.is_valid
        assert result.total_checks == 2
