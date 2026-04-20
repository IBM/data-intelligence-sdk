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
Unit tests for ComparisonCheck
"""

import pytest
from datetime import datetime, date
from wxdi.dq_validator.checks.comparison_check import ComparisonCheck, ComparisonOperator
from wxdi.dq_validator.metadata import AssetMetadata, ColumnMetadata, DataType
from wxdi.dq_validator.data_quality_dimension import DataQualityDimension


class TestComparisonCheckInitialization:
    """Test ComparisonCheck initialization and parameter validation"""
    
    def test_init_with_enum_operator_and_value(self):
        """Test initialization with enum operator and target value"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_value=18)
        assert check.operator == ComparisonOperator.GREATER_THAN
        assert check.target_value == 18
        assert check.target_column is None
        assert check.is_column_comparison == False
    
    def test_init_with_string_operator_and_value(self):
        """Test initialization with string operator and target value"""
        check = ComparisonCheck(operator='>', target_value=18)
        assert check.operator == ComparisonOperator.GREATER_THAN
        assert check.target_value == 18
    
    def test_init_with_enum_operator_and_column(self):
        """Test initialization with enum operator and target column"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_column='min_value')
        assert check.operator == ComparisonOperator.GREATER_THAN
        assert check.target_column == 'min_value'
        assert check.target_value is None
        assert check.is_column_comparison == True
    
    def test_init_all_operators_as_enum(self):
        """Test initialization with all operator enums"""
        operators = [
            ComparisonOperator.GREATER_THAN,
            ComparisonOperator.LESS_THAN,
            ComparisonOperator.GREATER_THAN_OR_EQUAL,
            ComparisonOperator.LESS_THAN_OR_EQUAL,
            ComparisonOperator.EQUAL,
            ComparisonOperator.NOT_EQUAL
        ]
        for op in operators:
            check = ComparisonCheck(operator=op, target_value=10)
            assert check.operator == op
    
    def test_init_all_operators_as_string(self):
        """Test initialization with all operator strings"""
        operators = ['>', '<', '>=', '<=', '==', '!=']
        for op in operators:
            check = ComparisonCheck(operator=op, target_value=10)
            assert check.operator.value == op
    
    def test_init_invalid_string_operator_raises_error(self):
        """Test that invalid string operator raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            ComparisonCheck(operator='<>', target_value=10)
        assert "Invalid operator '<>'" in str(exc_info.value)
    
    def test_init_invalid_operator_type_raises_error(self):
        """Test that invalid operator type raises TypeError"""
        with pytest.raises(TypeError) as exc_info:
            ComparisonCheck(operator=123, target_value=10)  # type: ignore[arg-type]
        assert "operator must be ComparisonOperator or str" in str(exc_info.value)
    
    def test_init_no_target_raises_error(self):
        """Test that no target raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            ComparisonCheck(operator=ComparisonOperator.GREATER_THAN)
        assert "Either target_column or target_value must be specified" in str(exc_info.value)
    
    def test_init_both_targets_raises_error(self):
        """Test that both targets raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            ComparisonCheck(
                operator=ComparisonOperator.GREATER_THAN,
                target_column='col1',
                target_value=10
            )
        assert "Cannot specify both target_column and target_value" in str(exc_info.value)
    
    def test_get_check_name(self):
        """Test get_check_name returns correct name"""
        check = ComparisonCheck(operator='>', target_value=10)
        assert check.get_check_name() == "comparison_check"
    
    def test_get_dimension(self):
        """Test get_dimension returns correct dimension"""
        check = ComparisonCheck(operator='>', target_value=10)
        assert check.get_dimension() == DataQualityDimension.VALIDITY
    
    def test_set_dimension(self):
        """Test set_dimension changes the dimension"""
        check = ComparisonCheck(operator='>', target_value=10)
        assert check.get_dimension() == DataQualityDimension.VALIDITY
        
        check.set_dimension(DataQualityDimension.CONSISTENCY)
        assert check.get_dimension() == DataQualityDimension.CONSISTENCY


class TestComparisonCheckColumnToValue:
    """Test ComparisonCheck with column-to-value comparisons"""
    
    def test_greater_than_passes(self):
        """Test greater than comparison passes"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_value=18)
        context = {'column_name': 'age'}
        result = check.validate(25, context)
        assert result is None
    
    def test_greater_than_fails(self):
        """Test greater than comparison fails"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_value=18)
        context = {'column_name': 'age'}
        result = check.validate(15, context)
        assert result is not None
        assert "age (15) > 18 failed" in result.message
    
    def test_less_than_passes(self):
        """Test less than comparison passes"""
        check = ComparisonCheck(operator=ComparisonOperator.LESS_THAN, target_value=100)
        context = {'column_name': 'score'}
        result = check.validate(75, context)
        assert result is None
    
    def test_less_than_fails(self):
        """Test less than comparison fails"""
        check = ComparisonCheck(operator=ComparisonOperator.LESS_THAN, target_value=100)
        context = {'column_name': 'score'}
        result = check.validate(150, context)
        assert result is not None
        assert "score (150) < 100 failed" in result.message
    
    def test_greater_than_or_equal_passes_equal(self):
        """Test >= passes when equal"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN_OR_EQUAL, target_value=18)
        context = {'column_name': 'age'}
        result = check.validate(18, context)
        assert result is None
    
    def test_greater_than_or_equal_passes_greater(self):
        """Test >= passes when greater"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN_OR_EQUAL, target_value=18)
        context = {'column_name': 'age'}
        result = check.validate(25, context)
        assert result is None
    
    def test_greater_than_or_equal_fails(self):
        """Test >= fails when less"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN_OR_EQUAL, target_value=18)
        context = {'column_name': 'age'}
        result = check.validate(17, context)
        assert result is not None
        assert "age (17) >= 18 failed" in result.message
    
    def test_less_than_or_equal_passes_equal(self):
        """Test <= passes when equal"""
        check = ComparisonCheck(operator=ComparisonOperator.LESS_THAN_OR_EQUAL, target_value=100)
        context = {'column_name': 'discount'}
        result = check.validate(100, context)
        assert result is None
    
    def test_less_than_or_equal_passes_less(self):
        """Test <= passes when less"""
        check = ComparisonCheck(operator=ComparisonOperator.LESS_THAN_OR_EQUAL, target_value=100)
        context = {'column_name': 'discount'}
        result = check.validate(75, context)
        assert result is None
    
    def test_less_than_or_equal_fails(self):
        """Test <= fails when greater"""
        check = ComparisonCheck(operator=ComparisonOperator.LESS_THAN_OR_EQUAL, target_value=100)
        context = {'column_name': 'discount'}
        result = check.validate(150, context)
        assert result is not None
        assert "discount (150) <= 100 failed" in result.message
    
    def test_equal_passes(self):
        """Test == passes when equal"""
        check = ComparisonCheck(operator=ComparisonOperator.EQUAL, target_value=200)
        context = {'column_name': 'status_code'}
        result = check.validate(200, context)
        assert result is None
    
    def test_equal_fails(self):
        """Test == fails when not equal"""
        check = ComparisonCheck(operator=ComparisonOperator.EQUAL, target_value=200)
        context = {'column_name': 'status_code'}
        result = check.validate(404, context)
        assert result is not None
        assert "status_code (404) == 200 failed" in result.message
    
    def test_not_equal_passes(self):
        """Test != passes when not equal"""
        check = ComparisonCheck(operator=ComparisonOperator.NOT_EQUAL, target_value=0)
        context = {'column_name': 'amount'}
        result = check.validate(100, context)
        assert result is None
    
    def test_not_equal_fails(self):
        """Test != fails when equal"""
        check = ComparisonCheck(operator=ComparisonOperator.NOT_EQUAL, target_value=0)
        context = {'column_name': 'amount'}
        result = check.validate(0, context)
        assert result is not None
        assert "amount (0) != 0 failed" in result.message


class TestComparisonCheckColumnToColumn:
    """Test ComparisonCheck with column-to-column comparisons"""
    
    def setup_method(self):
        """Set up metadata for column-to-column tests"""
        self.metadata = AssetMetadata(
            table_name='test',
            columns=[
                ColumnMetadata('salary', DataType.DECIMAL),
                ColumnMetadata('min_salary', DataType.DECIMAL)
            ]
        )
    
    def test_column_to_column_greater_than_passes(self):
        """Test column-to-column > passes"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_column='min_salary')
        record = [60000.00, 50000.00]
        context = {'column_name': 'salary', 'record': record, 'metadata': self.metadata}
        result = check.validate(60000.00, context)
        assert result is None
    
    def test_column_to_column_greater_than_fails(self):
        """Test column-to-column > fails"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_column='min_salary')
        record = [45000.00, 50000.00]
        context = {'column_name': 'salary', 'record': record, 'metadata': self.metadata}
        result = check.validate(45000.00, context)
        assert result is not None
        assert "salary (45000.0) > min_salary (50000.0) failed" in result.message
    
    def test_column_to_column_target_not_found(self):
        """Test error when target column not found"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_column='nonexistent')
        record = [60000.00, 50000.00]
        context = {'column_name': 'salary', 'record': record, 'metadata': self.metadata}
        result = check.validate(60000.00, context)
        assert result is not None
        assert "Target column 'nonexistent' not found" in result.message
    
    def test_column_to_column_target_is_none(self):
        """Test error when target column value is None"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_column='min_salary')
        record = [60000.00, None]
        context = {'column_name': 'salary', 'record': record, 'metadata': self.metadata}
        result = check.validate(60000.00, context)
        assert result is not None
        assert "min_salary=None" in result.message


class TestComparisonCheckStringComparison:
    """Test ComparisonCheck with string values"""
    
    def test_string_greater_than_passes(self):
        """Test string lexicographic > passes"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_value='apple')
        context = {'column_name': 'fruit'}
        result = check.validate('banana', context)
        assert result is None  # 'banana' > 'apple'
    
    def test_string_less_than_passes(self):
        """Test string lexicographic < passes"""
        check = ComparisonCheck(operator=ComparisonOperator.LESS_THAN, target_value='zebra')
        context = {'column_name': 'word'}
        result = check.validate('apple', context)
        assert result is None  # 'apple' < 'zebra'
    
    def test_string_equal_passes(self):
        """Test string == passes"""
        check = ComparisonCheck(operator=ComparisonOperator.EQUAL, target_value='test')
        context = {'column_name': 'value'}
        result = check.validate('test', context)
        assert result is None


class TestComparisonCheckDateComparison:
    """Test ComparisonCheck with date and datetime values"""
    
    def test_date_greater_than_passes(self):
        """Test date > passes"""
        check = ComparisonCheck(
            operator=ComparisonOperator.GREATER_THAN,
            target_value=date(2024, 1, 1)
        )
        context = {'column_name': 'end_date'}
        result = check.validate(date(2024, 12, 31), context)
        assert result is None
    
    def test_date_less_than_passes(self):
        """Test date < passes"""
        check = ComparisonCheck(
            operator=ComparisonOperator.LESS_THAN,
            target_value=date(2024, 12, 31)
        )
        context = {'column_name': 'start_date'}
        result = check.validate(date(2024, 1, 1), context)
        assert result is None
    
    def test_datetime_greater_than_passes(self):
        """Test datetime > passes"""
        check = ComparisonCheck(
            operator=ComparisonOperator.GREATER_THAN,
            target_value=datetime(2024, 1, 1, 0, 0, 0)
        )
        context = {'column_name': 'timestamp'}
        result = check.validate(datetime(2024, 6, 15, 12, 0, 0), context)
        assert result is None
    
    def test_datetime_less_than_or_equal_passes(self):
        """Test datetime <= passes"""
        check = ComparisonCheck(
            operator=ComparisonOperator.LESS_THAN_OR_EQUAL,
            target_value=datetime(2024, 12, 31, 23, 59, 59)
        )
        context = {'column_name': 'timestamp'}
        result = check.validate(datetime(2024, 6, 15, 12, 0, 0), context)
        assert result is None


class TestComparisonCheckBooleanComparison:
    """Test ComparisonCheck with boolean values"""
    
    def test_boolean_equal_true_passes(self):
        """Test boolean == True passes"""
        check = ComparisonCheck(operator=ComparisonOperator.EQUAL, target_value=True)
        context = {'column_name': 'is_active'}
        result = check.validate(True, context)
        assert result is None
    
    def test_boolean_equal_false_passes(self):
        """Test boolean == False passes"""
        check = ComparisonCheck(operator=ComparisonOperator.EQUAL, target_value=False)
        context = {'column_name': 'is_active'}
        result = check.validate(False, context)
        assert result is None
    
    def test_boolean_not_equal_passes(self):
        """Test boolean != passes"""
        check = ComparisonCheck(operator=ComparisonOperator.NOT_EQUAL, target_value=False)
        context = {'column_name': 'is_active'}
        result = check.validate(True, context)
        assert result is None
    
    def test_boolean_greater_than_passes(self):
        """Test boolean > passes (True > False in Python)"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_value=False)
        context = {'column_name': 'flag'}
        result = check.validate(True, context)
        assert result is None


class TestComparisonCheckNoneHandling:
    """Test ComparisonCheck with None values"""
    
    def test_none_value_fails(self):
        """Test None value returns error"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_value=50000)
        context = {'column_name': 'salary'}
        result = check.validate(None, context)
        assert result is not None
        assert "is None, cannot perform comparison" in result.message


class TestComparisonCheckTypeMismatch:
    """Test ComparisonCheck with type mismatches"""
    
    def test_type_mismatch_string_vs_int_fails(self):
        """Test type mismatch between string and int fails"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_value=50000)
        context = {'column_name': 'salary'}
        result = check.validate('60000', context)
        assert result is not None
        assert "Type mismatch" in result.message
        assert "str" in result.message
        assert "int" in result.message
    
    def test_type_mismatch_int_vs_float_fails(self):
        """Test type mismatch between int and float fails"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_value=50000)
        context = {'column_name': 'value'}
        result = check.validate(60000.0, context)
        assert result is not None
        assert "Type mismatch" in result.message
    
    def test_type_mismatch_column_to_column(self):
        """Test type mismatch in column-to-column comparison"""
        metadata = AssetMetadata(
            table_name='test',
            columns=[
                ColumnMetadata('value1', DataType.STRING),
                ColumnMetadata('value2', DataType.INTEGER)
            ]
        )
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_column='value2')
        record = ['100', 50]
        context = {'column_name': 'value1', 'record': record, 'metadata': metadata}
        result = check.validate('100', context)
        assert result is not None
        assert "Type mismatch" in result.message


class TestComparisonCheckFloatComparison:
    """Test ComparisonCheck with float values"""
    
    def test_float_greater_than_passes(self):
        """Test float > passes"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_value=50.5)
        context = {'column_name': 'amount'}
        result = check.validate(75.3, context)
        assert result is None
    
    def test_float_less_than_passes(self):
        """Test float < passes"""
        check = ComparisonCheck(operator=ComparisonOperator.LESS_THAN, target_value=100.0)
        context = {'column_name': 'amount'}
        result = check.validate(99.99, context)
        assert result is None
    
    def test_float_equal_passes(self):
        """Test float == passes"""
        check = ComparisonCheck(operator=ComparisonOperator.EQUAL, target_value=3.14)
        context = {'column_name': 'pi'}
        result = check.validate(3.14, context)
        assert result is None


class TestComparisonCheckEdgeCases:
    """Test ComparisonCheck edge cases"""
    
    def test_zero_comparison(self):
        """Test comparison with zero"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_value=0)
        context = {'column_name': 'value'}
        result = check.validate(1, context)
        assert result is None
    
    def test_negative_numbers(self):
        """Test comparison with negative numbers"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_value=-10)
        context = {'column_name': 'temperature'}
        result = check.validate(-5, context)
        assert result is None
    
    def test_very_large_numbers(self):
        """Test comparison with very large numbers"""
        check = ComparisonCheck(operator=ComparisonOperator.LESS_THAN, target_value=10**100)
        context = {'column_name': 'big_number'}
        result = check.validate(10**50, context)
        assert result is None
    
    def test_repr(self):
        """Test __repr__ method"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_value=10)
        repr_str = repr(check)
        assert "ComparisonCheck" in repr_str
        assert ">" in repr_str
        assert "10" in repr_str
    
    def test_repr_with_column(self):
        """Test __repr__ method with target column"""
        check = ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_column='min_value')
        repr_str = repr(check)
        assert "ComparisonCheck" in repr_str
        assert "min_value" in repr_str

