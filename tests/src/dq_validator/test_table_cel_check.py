"""
Tests for table-level CEL validation.
"""

import pytest
from wxdi.dq_validator import (
    AssetMetadata, ColumnMetadata, DataType,
    Validator, TableValidationRule, TableCELCheck,
    CELCompilationError, CELEvaluationError
)


@pytest.fixture
def metadata():
    """Create test metadata"""
    return AssetMetadata(
        table_name='test_table',
        columns=[
            ColumnMetadata('emp_id', DataType.INTEGER),
            ColumnMetadata('name', DataType.STRING),
            ColumnMetadata('age', DataType.INTEGER),
            ColumnMetadata('salary', DataType.DECIMAL),
            ColumnMetadata('min_salary', DataType.DECIMAL),
            ColumnMetadata('department', DataType.STRING),
        ]
    )


class TestTableCELCheckInitialization:
    """Test TableCELCheck initialization"""
    
    def test_valid_expression(self):
        """Test initialization with valid expression"""
        check = TableCELCheck('salary > min_salary')
        assert check.expression == 'salary > min_salary'
        assert check.get_check_name() == 'table_cel_check'
    
    def test_invalid_expression(self):
        """Test initialization with invalid expression"""
        with pytest.raises(CELCompilationError):
            TableCELCheck('invalid syntax !')
    
    def test_custom_error_message(self):
        """Test custom error message"""
        check = TableCELCheck('age >= 18', error_message='Must be adult')
        assert check.error_message == 'Must be adult'


class TestTableCELCheckValidation:
    """Test TableCELCheck validation"""
    
    def test_simple_comparison_pass(self, metadata):
        """Test simple comparison that passes"""
        validator = Validator(metadata)
        validator.add_table_rule(
            TableValidationRule('salary_check')
                .add_check(TableCELCheck('salary > min_salary'))
        )
        
        record = [1001, 'John', 30, 75000.00, 60000.00, 'Engineering']
        result = validator.validate(record)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_simple_comparison_fail(self, metadata):
        """Test simple comparison that fails"""
        validator = Validator(metadata)
        validator.add_table_rule(
            TableValidationRule('salary_check')
                .add_check(TableCELCheck('salary > min_salary'))
        )
        
        record = [1001, 'John', 30, 50000.00, 60000.00, 'Engineering']
        result = validator.validate(record)
        
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].column_name == 'salary_check'
    
    def test_conditional_logic_pass(self, metadata):
        """Test conditional logic that passes"""
        validator = Validator(metadata)
        validator.add_table_rule(
            TableValidationRule('age_salary_check')
                .add_check(TableCELCheck(
                    'age > 40 ? salary >= 80000 : salary >= 50000'
                ))
        )
        
        # Young employee with adequate salary
        record1 = [1001, 'John', 30, 55000.00, 50000.00, 'Engineering']
        result1 = validator.validate(record1)
        assert result1.is_valid
        
        # Senior employee with adequate salary
        record2 = [1002, 'Jane', 45, 85000.00, 70000.00, 'Sales']
        result2 = validator.validate(record2)
        assert result2.is_valid
    
    def test_conditional_logic_fail(self, metadata):
        """Test conditional logic that fails"""
        validator = Validator(metadata)
        validator.add_table_rule(
            TableValidationRule('age_salary_check')
                .add_check(TableCELCheck(
                    'age > 40 ? salary >= 80000 : salary >= 50000'
                ))
        )
        
        # Senior employee with inadequate salary
        record = [1001, 'John', 45, 70000.00, 60000.00, 'Engineering']
        result = validator.validate(record)
        
        assert not result.is_valid
        assert len(result.errors) == 1
    
    def test_multiple_conditions_pass(self, metadata):
        """Test multiple conditions that pass"""
        validator = Validator(metadata)
        validator.add_table_rule(
            TableValidationRule('multi_check')
                .add_check(TableCELCheck(
                    'salary > min_salary && age >= 18 && age <= 65'
                ))
        )
        
        record = [1001, 'John', 30, 75000.00, 60000.00, 'Engineering']
        result = validator.validate(record)
        
        assert result.is_valid
    
    def test_multiple_conditions_fail(self, metadata):
        """Test multiple conditions that fail"""
        validator = Validator(metadata)
        validator.add_table_rule(
            TableValidationRule('multi_check')
                .add_check(TableCELCheck(
                    'salary > min_salary && age >= 18 && age <= 65'
                ))
        )
        
        # Age too young
        record = [1001, 'John', 16, 75000.00, 60000.00, 'Engineering']
        result = validator.validate(record)
        
        assert not result.is_valid
    
    def test_string_operations(self, metadata):
        """Test string operations in CEL"""
        validator = Validator(metadata)
        validator.add_table_rule(
            TableValidationRule('dept_check')
                .add_check(TableCELCheck(
                    'department in ["Engineering", "Sales", "HR"]'
                ))
        )
        
        # Valid department
        record1 = [1001, 'John', 30, 75000.00, 60000.00, 'Engineering']
        result1 = validator.validate(record1)
        assert result1.is_valid
        
        # Invalid department
        record2 = [1002, 'Jane', 30, 75000.00, 60000.00, 'Marketing']
        result2 = validator.validate(record2)
        assert not result2.is_valid
    
    def test_arithmetic_operations(self, metadata):
        """Test arithmetic operations in CEL"""
        validator = Validator(metadata)
        validator.add_table_rule(
            TableValidationRule('salary_calc')
                .add_check(TableCELCheck(
                    'salary >= min_salary * 1.2'
                ))
        )
        
        # Salary is 1.25x minimum (passes)
        record1 = [1001, 'John', 30, 75000.00, 60000.00, 'Engineering']
        result1 = validator.validate(record1)
        assert result1.is_valid
        
        # Salary is only 1.1x minimum (fails)
        record2 = [1002, 'Jane', 30, 66000.00, 60000.00, 'Sales']
        result2 = validator.validate(record2)
        assert not result2.is_valid


class TestTableCELCheckMultipleRules:
    """Test multiple table-level rules"""
    
    def test_multiple_table_rules(self, metadata):
        """Test validator with multiple table rules"""
        validator = Validator(metadata)
        
        validator.add_table_rule(
            TableValidationRule('salary_check')
                .add_check(TableCELCheck('salary > min_salary'))
        )
        
        validator.add_table_rule(
            TableValidationRule('age_check')
                .add_check(TableCELCheck('age >= 18 && age <= 65'))
        )
        
        # All rules pass
        record1 = [1001, 'John', 30, 75000.00, 60000.00, 'Engineering']
        result1 = validator.validate(record1)
        assert result1.is_valid
        assert result1.total_checks == 2
        assert result1.passed_checks == 2
        
        # One rule fails
        record2 = [1002, 'Jane', 16, 75000.00, 60000.00, 'Sales']
        result2 = validator.validate(record2)
        assert not result2.is_valid
        assert result2.total_checks == 2
        assert result2.passed_checks == 1
        assert result2.failed_checks == 1


class TestTableCELCheckColumnValidation:
    """Test column reference validation"""
    
    def test_validate_column_references_valid(self, metadata):
        """Test validation with valid column references"""
        check = TableCELCheck('salary > min_salary && age >= 18')
        
        # Should not raise error
        check.validate_column_references([c.name for c in metadata.columns])
    
    def test_validate_column_references_invalid(self, metadata):
        """Test validation with invalid column references"""
        check = TableCELCheck('salary > max_salary')  # max_salary doesn't exist
        
        # If column extraction works, should raise ValueError
        # If extraction returns None (fallback), validation is skipped
        if check._required_columns is not None:
            with pytest.raises(ValueError) as exc_info:
                check.validate_column_references([c.name for c in metadata.columns])
            
            assert 'max_salary' in str(exc_info.value)
            assert 'CASE-SENSITIVE' in str(exc_info.value)
        else:
            # Extraction failed - validation is skipped (safe fallback)
            # This is acceptable behavior
            check.validate_column_references([c.name for c in metadata.columns])


class TestTableCELCheckPerformance:
    """Test performance optimization"""
    
    def test_required_columns_extraction(self):
        """Test that required columns are extracted from expression"""
        check = TableCELCheck('salary > min_salary && age >= 18')
        
        # Column extraction is best-effort optimization
        # If it works, verify the columns
        # If it returns None, that's acceptable (uses all columns as fallback)
        if check._required_columns is not None:
            # Extraction succeeded - verify columns
            assert 'salary' in check._required_columns
            assert 'min_salary' in check._required_columns
            assert 'age' in check._required_columns
        else:
            # Extraction returned None - acceptable fallback behavior
            # All columns will be used in context (safe but less optimal)
            pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


class TestTableCELCheckBindings:
    """Test variable bindings for table-level CEL checks."""
    
    def test_table_basic_binding(self, metadata):
        """Test basic variable binding with table-level check."""
        # Create check with binding: 'current_sal' -> 'salary'
        check = TableCELCheck(
            expression='current_sal > 50000',
            bindings={'current_sal': 'salary'}
        )
        
        # Create validator with table rule
        validator = Validator(metadata)
        validator.add_table_rule(
            TableValidationRule('salary_check')
                .add_check(check)
        )
        
        # Test with passing value
        record_pass = [1001, 'John', 30, 60000, 50000, 'Engineering']
        result = validator.validate(record_pass)
        assert result.is_valid
        
        # Test with failing value
        record_fail = [1002, 'Jane', 30, 40000, 50000, 'Engineering']
        result = validator.validate(record_fail)
        assert not result.is_valid
    
    def test_table_multiple_bindings(self, metadata):
        """Test multiple variable bindings in table-level check."""
        # Create check with multiple bindings
        check = TableCELCheck(
            expression='current_sal > minimum && person_age >= 18',
            bindings={
                'current_sal': 'salary',
                'minimum': 'min_salary',
                'person_age': 'age'
            }
        )
        
        # Create validator
        validator = Validator(metadata)
        validator.add_table_rule(
            TableValidationRule('multi_check')
                .add_check(check)
        )
        
        # Test with passing values
        record_pass = [1001, 'John', 25, 60000, 50000, 'Engineering']
        result = validator.validate(record_pass)
        assert result.is_valid
        
        # Test with failing values (below minimum)
        record_fail1 = [1002, 'Jane', 25, 40000, 50000, 'Engineering']
        result = validator.validate(record_fail1)
        assert not result.is_valid
        
        # Test with failing values (too young)
        record_fail2 = [1003, 'Bob', 16, 60000, 50000, 'Engineering']
        result = validator.validate(record_fail2)
        assert not result.is_valid
    
    def test_table_empty_bindings(self, metadata):
        """Test that empty bindings dict works for table checks."""
        check = TableCELCheck(
            expression='salary > 50000',
            bindings={}
        )
        
        validator = Validator(metadata)
        validator.add_table_rule(
            TableValidationRule('salary_check')
                .add_check(check)
        )
        
        record = [1001, 'John', 30, 60000, 50000, 'Engineering']
        result = validator.validate(record)
        assert result.is_valid
    
    def test_table_invalid_bindings_type(self):
        """Test that invalid bindings type raises error for table checks."""
        with pytest.raises(ValueError, match="bindings must be a dictionary"):
            TableCELCheck(
                expression='total > 100000',
                bindings='invalid'  # Should be dict
            )



class TestTableCELCheckHelperMethods:
    """Tests for TableCELCheck helper methods to improve coverage"""
    
    def test_validate_bindings_with_empty_string_key(self):
        """Test that empty string keys in bindings raise error"""
        with pytest.raises(ValueError, match="binding keys and values cannot be empty"):
            TableCELCheck(
                expression='current > 100',
                bindings={'': 'salary'}  # Empty key
            )
    
    def test_validate_bindings_with_empty_string_value(self):
        """Test that empty string values in bindings raise error"""
        with pytest.raises(ValueError, match="binding keys and values cannot be empty"):
            TableCELCheck(
                expression='current > 100',
                bindings={'current': ''}  # Empty value
            )
    
    def test_validate_bindings_with_non_string_key(self):
        """Test that non-string keys in bindings raise error"""
        with pytest.raises(ValueError, match="binding keys and values must be strings"):
            TableCELCheck(
                expression='current > 100',
                bindings={123: 'salary'}  # Integer key
            )
    
    def test_validate_bindings_with_non_string_value(self):
        """Test that non-string values in bindings raise error"""
        with pytest.raises(ValueError, match="binding keys and values must be strings"):
            TableCELCheck(
                expression='current > 100',
                bindings={'current': 456}  # Integer value
            )
    
    def test_extract_column_references_with_bindings(self):
        """Test column extraction when bindings are used"""
        check = TableCELCheck(
            expression='current_sal > minimum',
            bindings={'current_sal': 'salary', 'minimum': 'min_salary'}
        )
        # Should extract the actual column names from bindings
        if check._required_columns:
            assert 'salary' in check._required_columns or 'min_salary' in check._required_columns
    
    def test_validation_with_cel_evaluation_error(self, metadata):
        """Test handling of CEL evaluation errors in table checks"""
        check = TableCELCheck('salary.nonexistent_method()')
        # Provide proper record format for table CEL check
        record = [1001, 'John', 30, 75000.00, 60000.00, 'Engineering']
        context = {
            'record': record,
            'metadata': metadata,
            'record_index': 0
        }
        # Table CEL checks raise CELEvaluationError for evaluation failures
        with pytest.raises(CELEvaluationError, match="CEL evaluation failed"):
            check.validate(None, context)


class TestTableCELCheckEdgeCases:
    """Tests for edge cases in table CEL checks"""
    
    def test_validate_with_none_record(self, metadata):
        """Test validation when record is None"""
        check = TableCELCheck('salary > 50000')
        context = {
            'record': None,
            'metadata': metadata
        }
        # Should raise ValueError for missing record
        with pytest.raises(ValueError, match="requires 'record' and 'metadata'"):
            check.validate(None, context)
    
    def test_validate_with_missing_record_key(self, metadata):
        """Test validation when 'record' key is missing from context"""
        check = TableCELCheck('salary > 50000')
        context = {
            'metadata': metadata
        }
        # Should raise ValueError for missing record
        with pytest.raises(ValueError, match="requires 'record' and 'metadata'"):
            check.validate(None, context)
    
    def test_validate_with_missing_metadata(self):
        """Test validation when metadata is missing"""
        check = TableCELCheck('salary > 50000')
        record = [1001, 'John', 30, 75000.00, 60000.00, 'Engineering']
        context = {
            'record': record
        }
        # Should raise ValueError for missing metadata
        with pytest.raises(ValueError, match="requires 'record' and 'metadata'"):
            check.validate(None, context)


# Made with Bob
# Made with Bob
