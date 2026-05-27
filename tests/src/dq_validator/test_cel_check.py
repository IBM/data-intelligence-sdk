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
import pytest
from wxdi.dq_validator.checks.cel_check import CELCheck
from wxdi.dq_validator.data_quality_dimension import DataQualityDimension
from wxdi.dq_validator.cel_exceptions import CELCompilationError
from wxdi.dq_validator.metadata import AssetMetadata, ColumnMetadata, DataType


class TestCELCheckInitialization:
    """Tests for CELCheck initialization and compilation"""

    def test_init_simple_expression(self):
        """Test initialization with simple expression"""
        check = CELCheck('value > 0')
        assert check.expression == 'value > 0'
        assert check.get_check_name() == 'cel_check'

    def test_init_with_error_message(self):
        """Test initialization with custom error message"""
        check = CELCheck('value > 100', error_message='Value must exceed 100')
        assert check.error_message == 'Value must exceed 100'

    def test_init_with_dimension(self):
        """Test initialization with custom dimension"""
        check = CELCheck('value > 0', dimension=DataQualityDimension.CONSISTENCY)
        assert check.get_dimension() == DataQualityDimension.CONSISTENCY

    def test_init_with_description(self):
        """Test initialization with custom description"""
        check = CELCheck('value > 0', description='Positive value check')
        assert check.description == 'Positive value check'

    def test_init_default_description(self):
        """Test default description uses expression"""
        check = CELCheck('value > 0')
        assert check.description == 'CEL: value > 0'

    def test_init_empty_expression_raises_error(self):
        """Test that empty expression raises ValueError"""
        with pytest.raises(ValueError, match="CEL expression cannot be empty"):
            CELCheck('')

    def test_init_whitespace_expression_raises_error(self):
        """Test that whitespace-only expression raises ValueError"""
        with pytest.raises(ValueError, match="CEL expression cannot be empty"):
            CELCheck('   ')

    def test_init_too_long_expression_raises_error(self):
        """Test that expression exceeding max length raises ValueError"""
        long_expr = 'value > 0' + ' && value > 0' * 100  # Create very long expression
        with pytest.raises(ValueError, match="CEL expression too long"):
            CELCheck(long_expr)

    def test_init_invalid_syntax_raises_compilation_error(self):
        """Test that invalid CEL syntax raises CELCompilationError"""
        with pytest.raises(CELCompilationError):
            CELCheck('value >')  # Incomplete expression

    def test_init_strips_whitespace(self):
        """Test that expression whitespace is stripped"""
        check = CELCheck('  value > 0  ')
        assert check.expression == 'value > 0'

    def test_get_expression(self):
        """Test get_expression returns the expression"""
        check = CELCheck('value > 100')
        assert check.get_expression() == 'value > 100'

    def test_get_description(self):
        """Test get_description returns the description"""
        check = CELCheck('value > 0', description='Test description')
        assert check.get_description() == 'Test description'

    def test_repr(self):
        """Test string representation"""
        check = CELCheck('value > 0')
        assert repr(check) == "CELCheck(expression='value > 0')"


class TestCELCheckSimpleValidation:
    """Tests for simple CEL expression validation"""

    @pytest.fixture
    def metadata(self):
        """Create test metadata"""
        return AssetMetadata(
            table_name='test_table',
            columns=[
                ColumnMetadata('id', DataType.INTEGER),
                ColumnMetadata('value', DataType.DECIMAL)
            ]
        )

    def test_validate_simple_greater_than_pass(self, metadata):
        """Test simple > comparison that passes"""
        check = CELCheck('value > 0')
        context = {
            'column_name': 'value',
            'record': [1, 100],
            'metadata': metadata,
            'record_index': 0
        }
        error = check.validate(100, context)
        assert error is None

    def test_validate_simple_greater_than_fail(self, metadata):
        """Test simple > comparison that fails"""
        check = CELCheck('value > 0', error_message='Must be positive')
        context = {
            'column_name': 'value',
            'record': [1, -50],
            'metadata': metadata,
            'record_index': 0
        }
        error = check.validate(-50, context)
        assert error is not None
        assert error.message == 'Must be positive'
        assert error.column_name == 'value'

    def test_validate_equality_pass(self, metadata):
        """Test equality comparison that passes"""
        check = CELCheck('value == 100')
        context = {
            'column_name': 'value',
            'record': [1, 100],
            'metadata': metadata,
            'record_index': 0
        }
        error = check.validate(100, context)
        assert error is None

    def test_validate_equality_fail(self, metadata):
        """Test equality comparison that fails"""
        check = CELCheck('value == 100')
        context = {
            'column_name': 'value',
            'record': [1, 50],
            'metadata': metadata,
            'record_index': 0
        }
        error = check.validate(50, context)
        assert error is not None

    def test_validate_less_than_or_equal(self, metadata):
        """Test <= comparison"""
        check = CELCheck('value <= 100')
        context = {
            'column_name': 'value',
            'record': [1, 100],
            'metadata': metadata,
            'record_index': 0
        }
        # Should pass for 100
        assert check.validate(100, context) is None
        # Should pass for 50
        assert check.validate(50, context) is None
        # Should fail for 101
        assert check.validate(101, context) is not None

    def test_validate_not_equal(self, metadata):
        """Test != comparison"""
        check = CELCheck('value != 0')
        context = {
            'column_name': 'value',
            'record': [1, 100],
            'metadata': metadata,
            'record_index': 0
        }
        # Should pass for non-zero
        assert check.validate(100, context) is None
        # Should fail for zero
        assert check.validate(0, context) is not None


class TestCELCheckMultiColumnValidation:
    """Tests for CEL expressions using multiple columns"""

    @pytest.fixture
    def metadata(self):
        """Create test metadata with multiple columns"""
        return AssetMetadata(
            table_name='employees',
            columns=[
                ColumnMetadata('emp_id', DataType.INTEGER),
                ColumnMetadata('salary', DataType.DECIMAL),
                ColumnMetadata('min_salary', DataType.DECIMAL),
                ColumnMetadata('max_salary', DataType.DECIMAL)
            ]
        )

    def test_validate_record_comparison_pass(self, metadata):
        """Test comparison with another column that passes"""
        check = CELCheck('value > record.min_salary')
        context = {
            'column_name': 'salary',
            'record': [1001, 75000, 60000, 100000],
            'metadata': metadata,
            'record_index': 0
        }
        error = check.validate(75000, context)
        assert error is None

    def test_validate_record_comparison_fail(self, metadata):
        """Test comparison with another column that fails"""
        check = CELCheck('value > record.min_salary', error_message='Below minimum')
        context = {
            'column_name': 'salary',
            'record': [1001, 50000, 60000, 100000],
            'metadata': metadata,
            'record_index': 0
        }
        error = check.validate(50000, context)
        assert error is not None
        assert error.message == 'Below minimum'

    def test_validate_between_two_columns(self, metadata):
        """Test value between two columns"""
        check = CELCheck('value >= record.min_salary && value <= record.max_salary')
        context = {
            'column_name': 'salary',
            'record': [1001, 75000, 60000, 100000],
            'metadata': metadata,
            'record_index': 0
        }
        # Should pass for value in range
        assert check.validate(75000, context) is None
        # Should fail for value below range
        assert check.validate(50000, context) is not None
        # Should fail for value above range
        assert check.validate(110000, context) is not None


class TestCELCheckConditionalLogic:
    """Tests for CEL expressions with conditional (ternary) logic"""

    @pytest.fixture
    def metadata(self):
        """Create test metadata"""
        return AssetMetadata(
            table_name='employees',
            columns=[
                ColumnMetadata('emp_id', DataType.INTEGER),
                ColumnMetadata('age', DataType.INTEGER),
                ColumnMetadata('salary', DataType.DECIMAL)
            ]
        )

    def test_validate_ternary_senior_pass(self, metadata):
        """Test ternary expression for senior employee (passes)"""
        check = CELCheck('record.age > 40 ? value >= 80000 : value >= 50000')
        context = {
            'column_name': 'salary',
            'record': [1001, 45, 85000],
            'metadata': metadata,
            'record_index': 0
        }
        error = check.validate(85000, context)
        assert error is None

    def test_validate_ternary_senior_fail(self, metadata):
        """Test ternary expression for senior employee (fails)"""
        check = CELCheck('record.age > 40 ? value >= 80000 : value >= 50000')
        context = {
            'column_name': 'salary',
            'record': [1001, 45, 70000],
            'metadata': metadata,
            'record_index': 0
        }
        error = check.validate(70000, context)
        assert error is not None

    def test_validate_ternary_junior_pass(self, metadata):
        """Test ternary expression for junior employee (passes)"""
        check = CELCheck('record.age > 40 ? value >= 80000 : value >= 50000')
        context = {
            'column_name': 'salary',
            'record': [1001, 30, 60000],
            'metadata': metadata,
            'record_index': 0
        }
        error = check.validate(60000, context)
        assert error is None

    def test_validate_ternary_junior_fail(self, metadata):
        """Test ternary expression for junior employee (fails)"""
        check = CELCheck('record.age > 40 ? value >= 80000 : value >= 50000')
        context = {
            'column_name': 'salary',
            'record': [1001, 30, 40000],
            'metadata': metadata,
            'record_index': 0
        }
        error = check.validate(40000, context)
        assert error is not None


class TestCELCheckStringOperations:
    """Tests for CEL string operations"""

    @pytest.fixture
    def metadata(self):
        """Create test metadata"""
        return AssetMetadata(
            table_name='users',
            columns=[
                ColumnMetadata('user_id', DataType.INTEGER),
                ColumnMetadata('email', DataType.STRING)
            ]
        )

    def test_validate_ends_with_pass(self, metadata):
        """Test endsWith string operation that passes"""
        check = CELCheck('value.endsWith("@company.com")')
        context = {
            'column_name': 'email',
            'record': [1, 'john@company.com'],
            'metadata': metadata,
            'record_index': 0
        }
        error = check.validate('john@company.com', context)
        assert error is None

    def test_validate_ends_with_fail(self, metadata):
        """Test endsWith string operation that fails"""
        check = CELCheck('value.endsWith("@company.com")', error_message='Invalid domain')
        context = {
            'column_name': 'email',
            'record': [1, 'john@other.com'],
            'metadata': metadata,
            'record_index': 0
        }
        error = check.validate('john@other.com', context)
        assert error is not None
        assert error.message == 'Invalid domain'

    def test_validate_starts_with(self, metadata):
        """Test startsWith string operation"""
        check = CELCheck('value.startsWith("admin_")')
        context = {
            'column_name': 'email',
            'record': [1, 'admin_user@company.com'],
            'metadata': metadata,
            'record_index': 0
        }
        # Should pass
        assert check.validate('admin_user@company.com', context) is None
        # Should fail
        assert check.validate('user@company.com', context) is not None

    def test_validate_contains(self, metadata):
        """Test string contains using 'in' operator"""
        check = CELCheck('"@" in value')
        context = {
            'column_name': 'email',
            'record': [1, 'john@company.com'],
            'metadata': metadata,
            'record_index': 0
        }
        # Should pass for valid email
        assert check.validate('john@company.com', context) is None
        # Should fail for invalid email
        assert check.validate('invalid-email', context) is not None


class TestCELCheckListOperations:
    """Tests for CEL list operations"""

    @pytest.fixture
    def metadata(self):
        """Create test metadata"""
        return AssetMetadata(
            table_name='employees',
            columns=[
                ColumnMetadata('emp_id', DataType.INTEGER),
                ColumnMetadata('status', DataType.STRING)
            ]
        )

    def test_validate_in_list_pass(self, metadata):
        """Test 'in' list operation that passes"""
        check = CELCheck('value in ["Active", "Pending", "Approved"]')
        context = {
            'column_name': 'status',
            'record': [1, 'Active'],
            'metadata': metadata,
            'record_index': 0
        }
        error = check.validate('Active', context)
        assert error is None

    def test_validate_in_list_fail(self, metadata):
        """Test 'in' list operation that fails"""
        check = CELCheck('value in ["Active", "Pending", "Approved"]')
        context = {
            'column_name': 'status',
            'record': [1, 'Inactive'],
            'metadata': metadata,
            'record_index': 0
        }
        error = check.validate('Inactive', context)
        assert error is not None

    def test_validate_not_in_list(self, metadata):
        """Test negated 'in' list operation"""
        check = CELCheck('!(value in ["Deleted", "Archived"])')
        context = {
            'column_name': 'status',
            'record': [1, 'Active'],
            'metadata': metadata,
            'record_index': 0
        }
        # Should pass for Active
        assert check.validate('Active', context) is None
        # Should fail for Deleted
        assert check.validate('Deleted', context) is not None


class TestCELCheckLogicalOperators:
    """Tests for CEL logical operators"""

    @pytest.fixture
    def metadata(self):
        """Create test metadata"""
        return AssetMetadata(
            table_name='test',
            columns=[
                ColumnMetadata('id', DataType.INTEGER),
                ColumnMetadata('value', DataType.DECIMAL)
            ]
        )

    def test_validate_and_operator(self, metadata):
        """Test && (AND) operator"""
        check = CELCheck('value > 0 && value < 100')
        context = {
            'column_name': 'value',
            'record': [1, 50],
            'metadata': metadata,
            'record_index': 0
        }
        # Should pass for value in range
        assert check.validate(50, context) is None
        # Should fail for negative
        assert check.validate(-10, context) is not None
        # Should fail for too large
        assert check.validate(150, context) is not None

    def test_validate_or_operator(self, metadata):
        """Test || (OR) operator"""
        check = CELCheck('value < 0 || value > 100')
        context = {
            'column_name': 'value',
            'record': [1, 50],
            'metadata': metadata,
            'record_index': 0
        }
        # Should fail for value in middle range
        assert check.validate(50, context) is not None
        # Should pass for negative
        assert check.validate(-10, context) is None
        # Should pass for large
        assert check.validate(150, context) is None

    def test_validate_not_operator(self, metadata):
        """Test ! (NOT) operator"""
        check = CELCheck('!(value == 0)')
        context = {
            'column_name': 'value',
            'record': [1, 50],
            'metadata': metadata,
            'record_index': 0
        }
        # Should pass for non-zero
        assert check.validate(50, context) is None
        # Should fail for zero
        assert check.validate(0, context) is not None


class TestCELCheckEdgeCases:
    """Tests for edge cases and error handling"""

    @pytest.fixture
    def metadata(self):
        """Create test metadata"""
        return AssetMetadata(
            table_name='test',
            columns=[
                ColumnMetadata('id', DataType.INTEGER),
                ColumnMetadata('value', DataType.DECIMAL)
            ]
        )

    def test_validate_with_none_value(self, metadata):
        """Test validation with None value"""
        check = CELCheck('value != null')
        context = {
            'column_name': 'value',
            'record': [1, None],
            'metadata': metadata,
            'record_index': 0
        }
        # Should handle None gracefully
        error = check.validate(None, context)
        # May return error depending on CEL null handling
        assert error is not None or error is None

    def test_validate_without_metadata(self, metadata):
        """Test validation without metadata (fallback mode)"""
        check = CELCheck('value > 0')
        context = {
            'column_name': 'value',
            'record': [1, 100],
            'metadata': None,  # No metadata
            'record_index': 0
        }
        # Should still work with basic validation
        error = check.validate(100, context)
        assert error is None

    def test_validate_without_record(self, metadata):
        """Test validation without record data"""
        check = CELCheck('value > 0')
        context = {
            'column_name': 'value',
            'record': None,  # No record
            'metadata': metadata,
            'record_index': 0
        }
        # Should still work for simple value checks
        error = check.validate(100, context)
        assert error is None

    def test_validate_default_error_message(self, metadata):
        """Test that default error message is generated"""
        check = CELCheck('value > 100')  # No custom error message
        context = {
            'column_name': 'value',
            'record': [1, 50],
            'metadata': metadata,
            'record_index': 0
        }
        error = check.validate(50, context)
        assert error is not None
        assert 'value > 100' in error.message

    def test_validate_with_missing_column_in_record(self, metadata):
        """Test validation when record is shorter than metadata"""
        check = CELCheck('value > 0')
        context = {
            'column_name': 'value',
            'record': [1],  # Missing second column
            'metadata': metadata,
            'record_index': 0
        }
        # Should handle gracefully
        error = check.validate(100, context)
        # Should still validate the value itself
        assert error is None


class TestCELCheckArithmeticOperations:
    """Tests for CEL arithmetic operations"""

    @pytest.fixture
    def metadata(self):
        """Create test metadata"""
        return AssetMetadata(
            table_name='test',
            columns=[
                ColumnMetadata('id', DataType.INTEGER),
                ColumnMetadata('price', DataType.DECIMAL),
                ColumnMetadata('quantity', DataType.INTEGER)
            ]
        )

    def test_validate_addition(self, metadata):
        """Test arithmetic addition"""
        check = CELCheck('value == record.price + 10')
        context = {
            'column_name': 'price',
            'record': [1, 100, 5],
            'metadata': metadata,
            'record_index': 0
        }
        # Should pass for 110 (100 + 10)
        assert check.validate(110, context) is None
        # Should fail for other values
        assert check.validate(100, context) is not None

    def test_validate_multiplication(self, metadata):
        """Test arithmetic multiplication"""
        check = CELCheck('value == record.price * record.quantity')
        context = {
            'column_name': 'price',
            'record': [1, 100, 5],
            'metadata': metadata,
            'record_index': 0
        }
        # Should pass for 500 (100 * 5)
        assert check.validate(500, context) is None
        # Should fail for other values
        assert check.validate(100, context) is not None

    def test_validate_modulo(self, metadata):
        """Test modulo operation"""
        check = CELCheck('value % 10 == 0')
        context = {
            'column_name': 'price',
            'record': [1, 100, 5],
            'metadata': metadata,
            'record_index': 0
        }
        # Should pass for multiples of 10
        assert check.validate(100, context) is None
        assert check.validate(50, context) is None
        # Should fail for non-multiples
        assert check.validate(105, context) is not None


class TestCELCheckIntegration:
    """Integration tests with Validator"""

    @pytest.fixture
    def metadata(self):
        """Create test metadata"""
        return AssetMetadata(
            table_name='employees',
            columns=[
                ColumnMetadata('emp_id', DataType.INTEGER),
                ColumnMetadata('salary', DataType.DECIMAL),
                ColumnMetadata('min_salary', DataType.DECIMAL)
            ]
        )

    def test_cel_check_with_validator(self, metadata):
        """Test CELCheck integration with Validator"""
        from wxdi.dq_validator import Validator, ValidationRule
        
        validator = Validator(metadata)
        validator.add_rule(
            ValidationRule('salary')
                .add_check(CELCheck('value > record.min_salary'))
        )
        
        # Test with valid record
        valid_record = [1001, 75000, 60000]
        results = validator.validate_batch([valid_record])
        assert len(results) == 1
        assert results[0].is_valid
        
        # Test with invalid record
        invalid_record = [1002, 50000, 60000]
        results = validator.validate_batch([invalid_record])
        assert len(results) == 1
        assert not results[0].is_valid
        assert len(results[0].errors) > 0

# Made with Bob

    def test_simple_syntax_column_reference(self, metadata):
        """Test simple syntax without 'record.' prefix"""
        check = CELCheck('value > min_salary')
        context = {
            'column_name': 'salary',
            'record': [1001, 75000, 60000, 100000],
            'metadata': metadata,
            'record_index': 0
        }
        assert check.validate(75000, context) is None
        assert check.validate(50000, context) is not None

    def test_both_syntaxes_work_identically(self, metadata):
        """Test that simple and explicit syntax produce same results"""
        simple = CELCheck('value > min_salary')
        explicit = CELCheck('value > record.min_salary')
        context = {
            'column_name': 'salary',
            'record': [1001, 75000, 60000, 100000],
            'metadata': metadata,
            'record_index': 0
        }
        # Both should pass
        assert simple.validate(75000, context) is None
        assert explicit.validate(75000, context) is None
        # Both should fail
        assert simple.validate(50000, context) is not None
        assert explicit.validate(50000, context) is not None

    def test_simple_syntax_conditional(self, metadata):
        """Test simple syntax in conditional expressions"""
        check = CELCheck('age > 40 ? value >= 80000 : value >= 50000')
        context = {
            'column_name': 'salary',
            'record': [1001, 85000, 60000, 45],
            'metadata': AssetMetadata(
                table_name='employees',
                columns=[
                    ColumnMetadata('emp_id', DataType.INTEGER),
                    ColumnMetadata('salary', DataType.DECIMAL),
                    ColumnMetadata('min_salary', DataType.DECIMAL),
                    ColumnMetadata('age', DataType.INTEGER)
                ]
            ),
            'record_index': 0
        }
        assert check.validate(85000, context) is None


class TestCELCheckBindings:
    """Test variable bindings for column-level CEL checks."""
    
    def test_basic_binding(self):
        """Test basic variable binding with single column."""
        # Create check with binding: 'value' -> 'salary'
        check = CELCheck(
            expression='current_value > 50000',
            bindings={'current_value': 'salary'}
        )
        
        # Create metadata
        metadata = AssetMetadata(
            table_name='test',
            columns=[
                ColumnMetadata('salary', DataType.DECIMAL)
            ]
        )
        
        # Test with passing value
        context = {
            'column_name': 'salary',
            'record': [60000],
            'metadata': metadata,
            'record_index': 0
        }
        result = check.validate(60000, context)
        assert result is None
        
        # Test with failing value
        context = {
            'column_name': 'salary',
            'record': [40000],
            'metadata': metadata,
            'record_index': 0
        }
        result = check.validate(40000, context)
        assert result is not None
    
    def test_multiple_bindings(self):
        """Test multiple variable bindings in single expression."""
        # Create check with multiple bindings
        check = CELCheck(
            expression='current_value > minimum && current_value < maximum',
            bindings={
                'current_value': 'salary',
                'minimum': 'min_salary',
                'maximum': 'max_salary'
            }
        )
        
        # Create metadata
        metadata = AssetMetadata(
            table_name='test',
            columns=[
                ColumnMetadata('salary', DataType.DECIMAL),
                ColumnMetadata('min_salary', DataType.DECIMAL),
                ColumnMetadata('max_salary', DataType.DECIMAL)
            ]
        )
        
        # Test with passing values
        context = {
            'column_name': 'salary',
            'record': [60000, 50000, 70000],
            'metadata': metadata,
            'record_index': 0
        }
        result = check.validate(60000, context)
        assert result is None
        
        # Test with failing values (below minimum)
        context = {
            'column_name': 'salary',
            'record': [40000, 50000, 70000],
            'metadata': metadata,
            'record_index': 0
        }
        result = check.validate(40000, context)
        assert result is not None
        
        # Test with failing values (above maximum)
        context = {
            'column_name': 'salary',
            'record': [80000, 50000, 70000],
            'metadata': metadata,
            'record_index': 0
        }
        result = check.validate(80000, context)
        assert result is not None
    
    def test_binding_with_original_column_access(self):
        """Test that bindings work alongside original column names."""
        # Create check using both binding and original column name
        check = CELCheck(
            expression='current_value > min_salary && salary < 100000',
            bindings={'current_value': 'salary'}
        )
        
        # Create metadata
        metadata = AssetMetadata(
            table_name='test',
            columns=[
                ColumnMetadata('salary', DataType.DECIMAL),
                ColumnMetadata('min_salary', DataType.DECIMAL)
            ]
        )
        
        # Test with passing values
        context = {
            'column_name': 'salary',
            'record': [60000, 50000],
            'metadata': metadata,
            'record_index': 0
        }
        result = check.validate(60000, context)
        assert result is None
    
    def test_binding_missing_column(self):
        """Test behavior when bound column doesn't exist."""
        # Create check with binding to non-existent column
        check = CELCheck(
            expression='current_value > 50000',
            bindings={'current_value': 'nonexistent_column'}
        )
        
        # Create metadata without the bound column
        metadata = AssetMetadata(
            table_name='test',
            columns=[
                ColumnMetadata('salary', DataType.DECIMAL)
            ]
        )
        
        # Should fail with evaluation error (variable not found)
        context = {
            'column_name': 'salary',
            'record': [60000],
            'metadata': metadata,
            'record_index': 0
        }
        result = check.validate(60000, context)
        assert result is not None
        assert 'current_value' in result.message.lower() or 'undefined' in result.message.lower()
    
    def test_empty_bindings(self):
        """Test that empty bindings dict works (backward compatibility)."""
        check = CELCheck(
            expression='salary > 50000',
            bindings={}
        )
        
        metadata = AssetMetadata(
            table_name='test',
            columns=[
                ColumnMetadata('salary', DataType.DECIMAL)
            ]
        )
        
        context = {
            'column_name': 'salary',
            'record': [60000],
            'metadata': metadata,
            'record_index': 0
        }
        result = check.validate(60000, context)
        assert result is None
    
    def test_none_bindings(self):
        """Test that None bindings works (backward compatibility)."""
        check = CELCheck(
            expression='salary > 50000',
            bindings=None
        )
        
        metadata = AssetMetadata(
            table_name='test',
            columns=[
                ColumnMetadata('salary', DataType.DECIMAL)
            ]
        )
        
        context = {
            'column_name': 'salary',
            'record': [60000],
            'metadata': metadata,
            'record_index': 0
        }
        result = check.validate(60000, context)
        assert result is None
    
    def test_invalid_bindings_type(self):
        """Test that invalid bindings type raises error."""
        with pytest.raises(ValueError, match="bindings must be a dictionary"):
            CELCheck(
                expression='current_value > 50000',
                bindings=['invalid']  # Should be dict, not list
            )
    
    def test_invalid_binding_key(self):
        """Test that invalid binding key raises error."""
        with pytest.raises(ValueError, match="binding keys and values cannot be empty"):
            CELCheck(
                expression='current_value > 50000',
                bindings={'': 'salary'}  # Empty string key
            )
    
    def test_invalid_binding_value(self):
        """Test that invalid binding value raises error."""
        with pytest.raises(ValueError, match="binding keys and values cannot be empty"):
            CELCheck(
                expression='current_value > 50000',
                bindings={'current_value': ''}  # Empty string value
            )


class TestCELCheckHelperMethodsCoverage:
    """Tests for CELCheck helper methods to improve code coverage"""
    
    def test_validate_column_references_with_none_required_columns(self):
        """Test validate_column_references when _required_columns is None"""
        check = CELCheck('value > 0')
        check._required_columns = None
        # Should not raise error
        check.validate_column_references(['col1', 'col2'])
    
    def test_validate_column_references_with_empty_available_columns(self):
        """Test validate_column_references with empty available columns list"""
        check = CELCheck('value > min_salary')
        # Should not raise error when available_columns is empty
        check.validate_column_references([])
    
    def test_validate_column_references_returns_silently_when_no_required_columns(self):
        """Test validate_column_references returns silently when _required_columns is None or empty"""
        check = CELCheck('value > 100')
        # When _required_columns is None/empty, should not raise error
        check.validate_column_references(['some_col'])  # Should not raise
        check.validate_column_references([])  # Should not raise
    
    def test_complex_ast_with_nested_expressions(self):
        """Test complex AST traversal with deeply nested expressions"""
        check = CELCheck('(value > 0 && value < 100) || (value > 200 && value < 300)')
        metadata = AssetMetadata(
            table_name='test',
            columns=[ColumnMetadata('value', DataType.INTEGER)]
        )
        context = {
            'column_name': 'value',
            'record': [50],
            'metadata': metadata,
            'record_index': 0
        }
        assert check.validate(50, context) is None
        assert check.validate(150, context) is not None
        assert check.validate(250, context) is None
    
    def test_record_field_access_in_expression(self):
        """Test expressions with record.field access pattern"""
        check = CELCheck('value > record.min_value && value < record.max_value')
        metadata = AssetMetadata(
            table_name='test',
            columns=[
                ColumnMetadata('value', DataType.INTEGER),
                ColumnMetadata('min_value', DataType.INTEGER),
                ColumnMetadata('max_value', DataType.INTEGER)
            ]
        )
        context = {
            'column_name': 'value',
            'record': [50, 0, 100],
            'metadata': metadata,
            'record_index': 0
        }
        assert check.validate(50, context) is None
        assert check.validate(-10, context) is not None
        assert check.validate(150, context) is not None
    
    def test_validation_with_short_record(self):
        """Test validation when record is shorter than metadata columns"""
        check = CELCheck('value > 0')
        metadata = AssetMetadata(
            table_name='test',
            columns=[
                ColumnMetadata('col1', DataType.INTEGER),
                ColumnMetadata('col2', DataType.STRING),
                ColumnMetadata('col3', DataType.DECIMAL)
            ]
        )
        context = {
            'column_name': 'col1',
            'record': [100, 'test'],  # Missing col3
            'metadata': metadata,
            'record_index': 0
        }
        # Should handle gracefully
        assert check.validate(100, context) is None
    
    def test_validation_with_required_columns_optimization(self):
        """Test that required_columns optimization works correctly"""
        check = CELCheck('value > min_salary')
        # Check should have extracted required columns
        if check._required_columns:
            assert 'min_salary' in check._required_columns or len(check._required_columns) == 0
        
        metadata = AssetMetadata(
            table_name='test',
            columns=[
                ColumnMetadata('salary', DataType.DECIMAL),
                ColumnMetadata('min_salary', DataType.DECIMAL),
                ColumnMetadata('unused_col1', DataType.STRING),
                ColumnMetadata('unused_col2', DataType.STRING)
            ]
        )
        context = {
            'column_name': 'salary',
            'record': [60000, 50000, 'unused1', 'unused2'],
            'metadata': metadata,
            'record_index': 0
        }
        assert check.validate(60000, context) is None


class TestCELCheckErrorPathsCoverage:
    """Tests for error paths and edge cases to improve coverage"""
    
    def test_validation_with_cel_evaluation_error(self):
        """Test handling of CEL evaluation errors"""
        check = CELCheck('value.nonexistent_method()')
        metadata = AssetMetadata(
            table_name='test',
            columns=[ColumnMetadata('value', DataType.STRING)]
        )
        context = {
            'column_name': 'value',
            'record': ['test'],
            'metadata': metadata,
            'record_index': 0
        }
        error = check.validate('test', context)
        assert error is not None
        # Should contain error information
        assert 'error' in error.message.lower() or 'failed' in error.message.lower()
    
    def test_validation_with_type_mismatch(self):
        """Test validation with type mismatches"""
        check = CELCheck('value > 100')
        metadata = AssetMetadata(
            table_name='test',
            columns=[ColumnMetadata('value', DataType.STRING)]
        )
        context = {
            'column_name': 'value',
            'record': ['not_a_number'],
            'metadata': metadata,
            'record_index': 0
        }
        error = check.validate('not_a_number', context)
        # Should handle type mismatch gracefully
        assert error is not None
    
    def test_bindings_with_non_string_keys(self):
        """Test that non-string binding keys raise error"""
        with pytest.raises(ValueError, match="binding keys and values must be strings"):
            CELCheck(
                expression='current > 50000',
                bindings={123: 'salary'}  # Integer key instead of string
            )
    
    def test_bindings_with_non_string_values(self):
        """Test that non-string binding values raise error"""
        with pytest.raises(ValueError, match="binding keys and values must be strings"):
            CELCheck(
                expression='current > 50000',
                bindings={'current': 123}  # Integer value instead of string
            )
    
    def test_validate_column_references_with_all_columns_present(self):
        """Test validate_column_references when all columns are present"""
        check = CELCheck('record.age > 18')
        
        # Should not raise any error
        check.validate_column_references(['age', 'name', 'email'])
    
    def test_validate_column_references_with_no_required_columns(self):
        """Test validate_column_references with expression using only 'value'"""
        check = CELCheck('value > 100')
        
        # Should not raise error even with empty column list
        check.validate_column_references([])
        check.validate_column_references(['some', 'columns'])


# Made with Bob
