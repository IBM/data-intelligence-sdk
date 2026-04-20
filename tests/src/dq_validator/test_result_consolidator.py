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
Tests for ValidationResultConsolidated utility.
"""

import pytest
from wxdi.dq_validator.result import ValidationResult
from wxdi.dq_validator.result_consolidator import ValidationResultConsolidated
from wxdi.dq_validator.base import ValidationError
from wxdi.dq_validator import Validator, ValidationRule, AssetMetadata, ColumnMetadata
from wxdi.dq_validator.checks import LengthCheck, CompletenessCheck
from wxdi.dq_validator.metadata import DataType


@pytest.fixture
def sample_validator():
    """Create a sample validator for testing"""
    metadata = AssetMetadata('test_table', [
        ColumnMetadata('email', DataType.STRING),
        ColumnMetadata('name', DataType.STRING)
    ])
    validator = Validator(metadata)
    # Add multiple checks to each column for comprehensive testing
    validator.add_rule(ValidationRule('email').add_check(CompletenessCheck()).add_check(LengthCheck(min_length=5)))
    validator.add_rule(ValidationRule('name').add_check(CompletenessCheck()).add_check(LengthCheck(min_length=2)))
    return validator


class TestValidationResultConsolidated:
    """Test ValidationResultConsolidated class"""
    
    def test_init_with_error_storage(self, sample_validator):
        """Test initialization with error storage enabled"""
        consolidator = ValidationResultConsolidated(sample_validator, store_errors=True)
        assert consolidator.store_errors is True
        assert consolidator.total_records == 0
        assert consolidator.valid_records == 0
        assert consolidator.invalid_records == 0
    
    def test_init_without_error_storage(self, sample_validator):
        """Test initialization with error storage disabled"""
        consolidator = ValidationResultConsolidated(sample_validator, store_errors=False)
        assert consolidator.store_errors is False
        assert consolidator.total_records == 0
    
    def test_add_valid_result(self, sample_validator):
        """Test adding a valid result"""
        consolidator = ValidationResultConsolidated(sample_validator)
        
        result = ValidationResult(["test@example.com"], 0)
        result.total_checks = 2
        result.passed_checks = 2
        result.failed_checks = 0
        
        consolidator.add_result(result)
        
        assert consolidator.total_records == 1
        assert consolidator.valid_records == 1
        assert consolidator.invalid_records == 0
    
    def test_add_invalid_result(self, sample_validator):
        """Test adding an invalid result"""
        consolidator = ValidationResultConsolidated(sample_validator)
        
        result = ValidationResult(["invalid"], 0)
        result.total_checks = 2
        result.passed_checks = 1
        result.failed_checks = 1
        
        error = ValidationError(
            column_name="email",
            check_name="completeness_check",
            message="Invalid email format",
            value="invalid",
            expected="valid email"
        )
        result.add_error(error)
        
        consolidator.add_result(result)
        
        assert consolidator.total_records == 1
        assert consolidator.valid_records == 0
        assert consolidator.invalid_records == 1
    
    def test_add_multiple_results(self, sample_validator):
        """Test adding multiple results"""
        consolidator = ValidationResultConsolidated(sample_validator)
        
        # Valid result
        result1 = ValidationResult(["test@example.com"], 0)
        result1.total_checks = 2
        result1.passed_checks = 2
        
        # Invalid result
        result2 = ValidationResult(["invalid"], 1)
        result2.total_checks = 2
        result2.passed_checks = 1
        error = ValidationError("email", "completeness_check", "Invalid", "invalid")
        result2.add_error(error)
        
        consolidator.add_results([result1, result2])
        
        assert consolidator.total_records == 2
        assert consolidator.valid_records == 1
        assert consolidator.invalid_records == 1
    
    def test_get_overall_statistics(self, sample_validator):
        """Test getting overall statistics"""
        consolidator = ValidationResultConsolidated(sample_validator)
        
        # Add some results
        for i in range(10):
            result = ValidationResult([f"test{i}@example.com"], i)
            result.total_checks = 2
            if i < 7:  # 7 valid, 3 invalid
                result.passed_checks = 2
            else:
                result.passed_checks = 1
                error = ValidationError("email", "completeness_check", "Invalid", f"test{i}")
                result.add_error(error)
            consolidator.add_result(result)
        
        stats = consolidator.get_overall_statistics()
        
        assert stats['total_records'] == 10
        assert stats['valid_records'] == 7
        assert stats['invalid_records'] == 3
        assert stats['pass_rate'] == 70.0
        assert stats['total_errors'] == 3
    
    def test_get_column_statistics_single(self, sample_validator):
        """Test getting statistics for a single column"""
        consolidator = ValidationResultConsolidated(sample_validator)
        
        # Add results with errors on 'email' column
        for i in range(5):
            result = ValidationResult([f"test{i}"], i)
            result.total_checks = 2
            result.passed_checks = 1
            error = ValidationError("email", "completeness_check", "Invalid", f"test{i}")
            result.add_error(error)
            consolidator.add_result(result)
        
        stats = consolidator.get_column_statistics('email')
        
        # Email has 2 checks (completeness_check and length_check), so 5 records * 2 checks = 10 total
        assert stats['failed'] == 5  # 5 completeness_check failures
        assert stats['passed'] == 5  # 5 length_check passes
        assert stats['total'] == 10  # 5 records * 2 checks
    
    def test_get_column_statistics_all(self, sample_validator):
        """Test getting statistics for all columns"""
        consolidator = ValidationResultConsolidated(sample_validator)
        
        # Add errors for different columns
        result1 = ValidationResult(["test"], 0)
        result1.total_checks = 3
        result1.passed_checks = 1
        result1.add_error(ValidationError("email", "completeness_check", "Invalid", "test"))
        result1.add_error(ValidationError("name", "length_check", "Too short", "a"))
        
        consolidator.add_result(result1)
        
        stats = consolidator.get_column_statistics()
        
        assert 'email' in stats
        assert 'name' in stats
        assert stats['email']['failed'] == 1
        assert stats['name']['failed'] == 1
    
    def test_get_check_statistics_single(self, sample_validator):
        """Test getting statistics for a single check type"""
        consolidator = ValidationResultConsolidated(sample_validator)
        
        # Add results with completeness_check errors
        for i in range(3):
            result = ValidationResult([f"test{i}"], i)
            result.total_checks = 2
            result.passed_checks = 1
            error = ValidationError("email", "completeness_check", "Invalid", f"test{i}")
            result.add_error(error)
            consolidator.add_result(result)
        
        stats = consolidator.get_check_statistics('completeness_check')
        
        # completeness_check is on both email and name columns, so 3 records * 2 columns = 6 total
        assert stats['failed'] == 3  # 3 email completeness failures
        assert stats['passed'] == 3  # 3 name completeness passes
        assert stats['total'] == 6  # 3 records * 2 columns
    
    def test_get_check_statistics_all(self, sample_validator):
        """Test getting statistics for all check types"""
        consolidator = ValidationResultConsolidated(sample_validator)
        
        result = ValidationResult(["test"], 0)
        result.total_checks = 3
        result.passed_checks = 1
        result.add_error(ValidationError("email", "completeness_check", "Invalid", "test"))
        result.add_error(ValidationError("name", "length_check", "Too short", "a"))
        
        consolidator.add_result(result)
        
        stats = consolidator.get_check_statistics()
        
        assert 'completeness_check' in stats
        assert 'length_check' in stats
        assert stats['completeness_check']['failed'] == 1
        assert stats['length_check']['failed'] == 1
    
    def test_get_combined_statistics_both_specified(self, sample_validator):
        """Test getting combined statistics with both column and check specified"""
        consolidator = ValidationResultConsolidated(sample_validator)
        
        result = ValidationResult(["test"], 0)
        result.total_checks = 2
        result.passed_checks = 1
        result.add_error(ValidationError("email", "completeness_check", "Invalid", "test"))
        
        consolidator.add_result(result)
        
        stats = consolidator.get_combined_statistics('email', 'completeness_check')
        
        assert stats['failed'] == 1
        assert stats['total'] == 1
    
    def test_get_combined_statistics_column_only(self, sample_validator):
        """Test getting combined statistics with only column specified"""
        consolidator = ValidationResultConsolidated(sample_validator)
        
        result = ValidationResult(["test"], 0)
        result.total_checks = 3
        result.passed_checks = 1
        result.add_error(ValidationError("email", "completeness_check", "Invalid", "test"))
        result.add_error(ValidationError("email", "length_check", "Too short", "a"))
        
        consolidator.add_result(result)
        
        stats = consolidator.get_combined_statistics(column_name='email')
        
        assert 'completeness_check' in stats
        assert 'length_check' in stats
        assert stats['completeness_check']['failed'] == 1
        assert stats['length_check']['failed'] == 1
    
    def test_get_combined_statistics_check_only(self, sample_validator):
        """Test getting combined statistics with only check specified"""
        consolidator = ValidationResultConsolidated(sample_validator)
        
        result = ValidationResult(["test"], 0)
        result.total_checks = 3
        result.passed_checks = 1
        result.add_error(ValidationError("email", "completeness_check", "Invalid", "test"))
        result.add_error(ValidationError("name", "completeness_check", "Invalid", "123"))
        
        consolidator.add_result(result)
        
        stats = consolidator.get_combined_statistics(check_name='completeness_check')
        
        assert 'email' in stats
        assert 'name' in stats
        assert stats['email']['failed'] == 1
        assert stats['name']['failed'] == 1
    
    def test_get_combined_statistics_all(self, sample_validator):
        """Test getting all combined statistics"""
        consolidator = ValidationResultConsolidated(sample_validator)
        
        result = ValidationResult(["test"], 0)
        result.total_checks = 3
        result.passed_checks = 1
        result.add_error(ValidationError("email", "completeness_check", "Invalid", "test"))
        result.add_error(ValidationError("name", "length_check", "Too short", "a"))
        
        consolidator.add_result(result)
        
        stats = consolidator.get_combined_statistics()
        
        assert 'email' in stats
        assert 'name' in stats
        assert 'completeness_check' in stats['email']
        assert 'length_check' in stats['name']
    
    def test_get_errors_by_column_with_storage(self, sample_validator):
        """Test getting errors by column when storage is enabled"""
        consolidator = ValidationResultConsolidated(sample_validator, store_errors=True)
        
        result = ValidationResult(["test"], 0)
        result.total_checks = 2
        result.passed_checks = 1
        result.add_error(ValidationError("email", "completeness_check", "Invalid", "test"))
        
        consolidator.add_result(result)
        
        errors = consolidator.get_errors_by_column('email')
        
        assert len(errors) == 1
        assert errors[0]['column'] == 'email'
        assert errors[0]['check'] == 'completeness_check'
        assert errors[0]['record_index'] == 0
    
    def test_get_errors_by_column_without_storage(self, sample_validator):
        """Test getting errors by column when storage is disabled"""
        consolidator = ValidationResultConsolidated(sample_validator, store_errors=False)
        
        result = ValidationResult(["test"], 0)
        result.total_checks = 2
        result.passed_checks = 1
        result.add_error(ValidationError("email", "completeness_check", "Invalid", "test"))
        
        consolidator.add_result(result)
        
        with pytest.raises(RuntimeError, match="Error details not available"):
            consolidator.get_errors_by_column('email')
    
    def test_get_errors_by_check_with_storage(self, sample_validator):
        """Test getting errors by check when storage is enabled"""
        consolidator = ValidationResultConsolidated(sample_validator, store_errors=True)
        
        result = ValidationResult(["test"], 0)
        result.total_checks = 2
        result.passed_checks = 1
        result.add_error(ValidationError("email", "completeness_check", "Invalid", "test"))
        
        consolidator.add_result(result)
        
        errors = consolidator.get_errors_by_check('completeness_check')
        
        assert len(errors) == 1
        assert errors[0]['check'] == 'completeness_check'
    
    def test_get_errors_by_check_without_storage(self, sample_validator):
        """Test getting errors by check when storage is disabled"""
        consolidator = ValidationResultConsolidated(sample_validator, store_errors=False)
        
        with pytest.raises(RuntimeError, match="Error details not available"):
            consolidator.get_errors_by_check('completeness_check')
    
    def test_get_errors_by_column_and_check(self, sample_validator):
        """Test getting errors by column and check combination"""
        consolidator = ValidationResultConsolidated(sample_validator, store_errors=True)
        
        result = ValidationResult(["test"], 0)
        result.total_checks = 3
        result.passed_checks = 1
        result.add_error(ValidationError("email", "completeness_check", "Invalid", "test"))
        result.add_error(ValidationError("email", "length_check", "Too short", "a"))
        
        consolidator.add_result(result)
        
        errors = consolidator.get_errors_by_column_and_check('email', 'completeness_check')
        
        assert len(errors) == 1
        assert errors[0]['column'] == 'email'
        assert errors[0]['check'] == 'completeness_check'
    
    def test_get_all_errors_with_storage(self, sample_validator):
        """Test getting all errors when storage is enabled"""
        consolidator = ValidationResultConsolidated(sample_validator, store_errors=True)
        
        result = ValidationResult(["test"], 0)
        result.total_checks = 3
        result.passed_checks = 1
        result.add_error(ValidationError("email", "completeness_check", "Invalid", "test"))
        result.add_error(ValidationError("name", "length_check", "Too short", "a"))
        
        consolidator.add_result(result)
        
        errors = consolidator.get_all_errors()
        
        assert len(errors) == 2
    
    def test_get_all_errors_without_storage(self, sample_validator):
        """Test getting all errors when storage is disabled"""
        consolidator = ValidationResultConsolidated(sample_validator, store_errors=False)
        
        with pytest.raises(RuntimeError, match="Error details not available"):
            consolidator.get_all_errors()
    
    def test_get_columns(self, sample_validator):
        """Test getting list of validated columns"""
        consolidator = ValidationResultConsolidated(sample_validator)
        
        result = ValidationResult(["test"], 0)
        result.total_checks = 3
        result.passed_checks = 1
        result.add_error(ValidationError("email", "completeness_check", "Invalid", "test"))
        result.add_error(ValidationError("name", "length_check", "Too short", "a"))
        
        consolidator.add_result(result)
        
        columns = consolidator.get_columns()
        
        assert 'email' in columns
        assert 'name' in columns
        assert len(columns) == 2
    
    def test_get_checks(self, sample_validator):
        """Test getting list of executed checks"""
        consolidator = ValidationResultConsolidated(sample_validator)
        
        result = ValidationResult(["test"], 0)
        result.total_checks = 3
        result.passed_checks = 1
        result.add_error(ValidationError("email", "completeness_check", "Invalid", "test"))
        result.add_error(ValidationError("name", "length_check", "Too short", "a"))
        
        consolidator.add_result(result)
        
        checks = consolidator.get_checks()
        
        assert 'completeness_check' in checks
        assert 'length_check' in checks
        assert len(checks) == 2
    
    def test_to_dict(self, sample_validator):
        """Test converting consolidator to dictionary"""
        consolidator = ValidationResultConsolidated(sample_validator)
        
        result = ValidationResult(["test"], 0)
        result.total_checks = 2
        result.passed_checks = 1
        result.add_error(ValidationError("email", "completeness_check", "Invalid", "test"))
        
        consolidator.add_result(result)
        
        data = consolidator.to_dict()
        
        assert 'overall' in data
        assert 'by_column' in data
        assert 'by_check' in data
        assert 'combined' in data
        assert 'columns' in data
        assert 'checks' in data
        assert 'error_count' in data
    
    def test_repr(self, sample_validator):
        """Test string representation"""
        consolidator = ValidationResultConsolidated(sample_validator)
        
        result1 = ValidationResult(["test"], 0)
        result1.total_checks = 2
        result1.passed_checks = 2
        
        result2 = ValidationResult(["invalid"], 1)
        result2.total_checks = 2
        result2.passed_checks = 1
        result2.add_error(ValidationError("email", "completeness_check", "Invalid", "invalid"))
        
        consolidator.add_results([result1, result2])
        
        repr_str = repr(consolidator)
        
        assert 'ValidationResultConsolidated' in repr_str
        assert 'records=2' in repr_str
        assert 'valid=1' in repr_str
        assert 'invalid=1' in repr_str
        assert 'errors=1' in repr_str