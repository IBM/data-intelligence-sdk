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
Unit tests for ValidValuesCheck
"""

import pytest
from wxdi.dq_validator.checks.valid_values_check import ValidValuesCheck
from wxdi.dq_validator.data_quality_dimension import DataQualityDimension


class TestValidValuesCheckInitialization:
    """Test ValidValuesCheck initialization and parameter validation"""
    
    def test_init_with_string_values(self):
        """Test initialization with string values"""
        check = ValidValuesCheck(['active', 'inactive', 'pending'])
        assert check.valid_values == ['active', 'inactive', 'pending']
        assert check.case_sensitive == False  # Default
    
    def test_init_with_numeric_values(self):
        """Test initialization with numeric values"""
        check = ValidValuesCheck([1, 2, 3, 4, 5])
        assert check.valid_values == [1, 2, 3, 4, 5]
    
    def test_init_case_sensitive_true(self):
        """Test initialization with case_sensitive=True"""
        check = ValidValuesCheck(['Active', 'Inactive'], case_sensitive=True)
        assert check.case_sensitive == True
    
    def test_init_case_sensitive_false(self):
        """Test initialization with case_sensitive=False"""
        check = ValidValuesCheck(['active', 'inactive'], case_sensitive=False)
        assert check.case_sensitive == False
    
    def test_init_empty_list_raises_error(self):
        """Test that empty list raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            ValidValuesCheck([])
        assert "valid_values cannot be empty" in str(exc_info.value)
    
    def test_init_not_list_raises_error(self):
        """Test that non-list raises TypeError"""
        with pytest.raises(TypeError) as exc_info:
            ValidValuesCheck('not_a_list') # type: ignore[arg-type]
        assert "valid_values must be a list" in str(exc_info.value)
    
    def test_init_with_mixed_types(self):
        """Test initialization with mixed type values"""
        check = ValidValuesCheck([1, 'text', True])
        assert check.valid_values == [1, 'text', True]
    
    def test_get_check_name(self):
        """Test get_check_name returns correct name"""
        check = ValidValuesCheck(['a', 'b'])
        assert check.get_check_name() == "valid_values_check"
    
    def test_get_dimension(self):
        """Test get_dimension returns correct dimension"""
        check = ValidValuesCheck(['a', 'b'])
        assert check.get_dimension() == DataQualityDimension.VALIDITY
    
    def test_set_dimension(self):
        """Test set_dimension changes the dimension"""
        check = ValidValuesCheck(['a', 'b'])
        assert check.get_dimension() == DataQualityDimension.VALIDITY
        
        check.set_dimension(DataQualityDimension.CONSISTENCY)
        assert check.get_dimension() == DataQualityDimension.CONSISTENCY


class TestValidValuesCheckCaseSensitive:
    """Test ValidValuesCheck with case_sensitive=True"""
    
    def test_exact_match_passes(self):
        """Test exact match passes with case_sensitive=True"""
        check = ValidValuesCheck(['active', 'inactive', 'pending'], case_sensitive=True)
        context = {'column_name': 'status'}
        result = check.validate('active', context)
        assert result is None
    
    def test_case_mismatch_fails(self):
        """Test case mismatch fails with case_sensitive=True"""
        check = ValidValuesCheck(['active', 'inactive', 'pending'], case_sensitive=True)
        context = {'column_name': 'status'}
        result = check.validate('Active', context)
        assert result is not None
        assert result.column_name == 'status'
        assert result.check_name == 'valid_values_check'
        assert "has invalid value 'Active'" in result.message
    
    def test_uppercase_mismatch_fails(self):
        """Test uppercase mismatch fails with case_sensitive=True"""
        check = ValidValuesCheck(['active', 'inactive'], case_sensitive=True)
        context = {'column_name': 'status'}
        result = check.validate('ACTIVE', context)
        assert result is not None
        assert "has invalid value 'ACTIVE'" in result.message
    
    def test_invalid_value_fails(self):
        """Test invalid value fails with case_sensitive=True"""
        check = ValidValuesCheck(['active', 'inactive'], case_sensitive=True)
        context = {'column_name': 'status'}
        result = check.validate('archived', context)
        assert result is not None
        assert "has invalid value 'archived'" in result.message


class TestValidValuesCheckCaseInsensitive:
    """Test ValidValuesCheck with case_sensitive=False (default)"""
    
    def test_exact_match_passes(self):
        """Test exact match passes with case_sensitive=False"""
        check = ValidValuesCheck(['active', 'inactive', 'pending'], case_sensitive=False)
        context = {'column_name': 'status'}
        result = check.validate('active', context)
        assert result is None
    
    def test_uppercase_match_passes(self):
        """Test uppercase match passes with case_sensitive=False"""
        check = ValidValuesCheck(['active', 'inactive', 'pending'], case_sensitive=False)
        context = {'column_name': 'status'}
        result = check.validate('ACTIVE', context)
        assert result is None
    
    def test_titlecase_match_passes(self):
        """Test titlecase match passes with case_sensitive=False"""
        check = ValidValuesCheck(['active', 'inactive', 'pending'], case_sensitive=False)
        context = {'column_name': 'status'}
        result = check.validate('Active', context)
        assert result is None
    
    def test_mixed_case_match_passes(self):
        """Test mixed case match passes with case_sensitive=False"""
        check = ValidValuesCheck(['active', 'inactive'], case_sensitive=False)
        context = {'column_name': 'status'}
        result = check.validate('AcTiVe', context)
        assert result is None
    
    def test_invalid_value_fails(self):
        """Test invalid value fails with case_sensitive=False"""
        check = ValidValuesCheck(['active', 'inactive'], case_sensitive=False)
        context = {'column_name': 'status'}
        result = check.validate('archived', context)
        assert result is not None
        assert "has invalid value 'archived' (case-insensitive)" in result.message
    
    def test_default_is_case_insensitive(self):
        """Test default behavior is case-insensitive"""
        check = ValidValuesCheck(['active', 'inactive'])
        context = {'column_name': 'status'}
        result = check.validate('ACTIVE', context)
        assert result is None


class TestValidValuesCheckNumericValues:
    """Test ValidValuesCheck with numeric values"""
    
    def test_valid_integer_passes(self):
        """Test valid integer value passes"""
        check = ValidValuesCheck([1, 2, 3, 4, 5])
        context = {'column_name': 'priority'}
        result = check.validate(3, context)
        assert result is None
    
    def test_invalid_integer_fails(self):
        """Test invalid integer value fails"""
        check = ValidValuesCheck([1, 2, 3, 4, 5])
        context = {'column_name': 'priority'}
        result = check.validate(6, context)
        assert result is not None
        assert "has invalid value '6'" in result.message
    
    def test_valid_float_passes(self):
        """Test valid float value passes"""
        check = ValidValuesCheck([1.0, 2.5, 3.7])
        context = {'column_name': 'rating'}
        result = check.validate(2.5, context)
        assert result is None
    
    def test_type_mismatch_string_vs_int_fails(self):
        """Test type mismatch between string and int fails"""
        check = ValidValuesCheck([1, 2, 3])
        context = {'column_name': 'priority'}
        result = check.validate('3', context)
        assert result is not None
        assert "has invalid value '3'" in result.message
    
    def test_type_mismatch_int_vs_float_passes(self):
        """Test that int and float with same value are considered equal (Python behavior)"""
        check = ValidValuesCheck([1, 2, 3])
        context = {'column_name': 'value'}
        result = check.validate(1.0, context)
        assert result is None  # 1 == 1.0 in Python (numeric equality)


class TestValidValuesCheckBooleanValues:
    """Test ValidValuesCheck with boolean values"""
    
    def test_valid_true_passes(self):
        """Test valid True value passes"""
        check = ValidValuesCheck([True, False])
        context = {'column_name': 'is_active'}
        result = check.validate(True, context)
        assert result is None
    
    def test_valid_false_passes(self):
        """Test valid False value passes"""
        check = ValidValuesCheck([True, False])
        context = {'column_name': 'is_active'}
        result = check.validate(False, context)
        assert result is None
    
    def test_boolean_case_insensitive_ignored(self):
        """Test case_sensitive is ignored for non-string types"""
        check = ValidValuesCheck([True], case_sensitive=False)
        context = {'column_name': 'flag'}
        result = check.validate(True, context)
        assert result is None


class TestValidValuesCheckNoneHandling:
    """Test ValidValuesCheck with None values"""
    
    def test_none_value_fails(self):
        """Test None value returns error"""
        check = ValidValuesCheck(['active', 'inactive'])
        context = {'column_name': 'status'}
        result = check.validate(None, context)
        assert result is not None
        assert result.column_name == 'status'
        assert "is None" in result.message
        assert "expected one of" in result.message


class TestValidValuesCheckEmptyString:
    """Test ValidValuesCheck with empty strings"""
    
    def test_empty_string_in_valid_values_passes(self):
        """Test empty string passes when in valid values"""
        check = ValidValuesCheck(['', 'value1', 'value2'])
        context = {'column_name': 'optional_field'}
        result = check.validate('', context)
        assert result is None
    
    def test_empty_string_not_in_valid_values_fails(self):
        """Test empty string fails when not in valid values"""
        check = ValidValuesCheck(['value1', 'value2'])
        context = {'column_name': 'required_field'}
        result = check.validate('', context)
        assert result is not None
        assert "has invalid value ''" in result.message


class TestValidValuesCheckMixedTypes:
    """Test ValidValuesCheck with mixed type values"""
    
    def test_mixed_types_string_passes(self):
        """Test string value passes in mixed type list"""
        check = ValidValuesCheck([1, 'text', True])
        context = {'column_name': 'mixed_field'}
        result = check.validate('text', context)
        assert result is None
    
    def test_mixed_types_int_passes(self):
        """Test int value passes in mixed type list"""
        check = ValidValuesCheck([1, 'text', True])
        context = {'column_name': 'mixed_field'}
        result = check.validate(1, context)
        assert result is None
    
    def test_mixed_types_bool_passes(self):
        """Test bool value passes in mixed type list"""
        check = ValidValuesCheck([1, 'text', True])
        context = {'column_name': 'mixed_field'}
        result = check.validate(True, context)
        assert result is None
    
    def test_mixed_types_invalid_fails(self):
        """Test invalid value fails in mixed type list"""
        check = ValidValuesCheck([1, 'text', True])
        context = {'column_name': 'mixed_field'}
        result = check.validate(2, context)
        assert result is not None


class TestValidValuesCheckDuplicates:
    """Test ValidValuesCheck with duplicate values"""
    
    def test_duplicates_in_list_allowed(self):
        """Test duplicates in valid_values list are allowed"""
        check = ValidValuesCheck(['active', 'active', 'inactive'])
        context = {'column_name': 'status'}
        result = check.validate('active', context)
        assert result is None
    
    def test_duplicates_case_insensitive(self):
        """Test duplicates with different cases in case-insensitive mode"""
        check = ValidValuesCheck(['Active', 'active', 'ACTIVE'], case_sensitive=False)
        context = {'column_name': 'status'}
        result = check.validate('active', context)
        assert result is None


class TestValidValuesCheckErrorMessages:
    """Test ValidValuesCheck error message formatting"""
    
    def test_error_message_includes_column_name(self):
        """Test error message includes column name"""
        check = ValidValuesCheck(['a', 'b'])
        context = {'column_name': 'test_column'}
        result = check.validate('c', context)
        assert result is not None
        assert 'test_column' in result.message
    
    def test_error_message_includes_invalid_value(self):
        """Test error message includes the invalid value"""
        check = ValidValuesCheck(['a', 'b'])
        context = {'column_name': 'field'}
        result = check.validate('invalid', context)
        assert result is not None
        assert 'invalid' in result.message
    
    def test_error_message_includes_valid_values(self):
        """Test error message includes list of valid values"""
        check = ValidValuesCheck(['a', 'b', 'c'])
        context = {'column_name': 'field'}
        result = check.validate('d', context)
        assert result is not None
        assert "['a', 'b', 'c']" in result.message
    
    def test_error_message_case_insensitive_note(self):
        """Test error message includes case-insensitive note for strings"""
        check = ValidValuesCheck(['active'], case_sensitive=False)
        context = {'column_name': 'status'}
        result = check.validate('invalid', context)
        assert result is not None
        assert "(case-insensitive)" in result.message
    
    def test_error_message_no_case_note_for_case_sensitive(self):
        """Test error message has no case note for case-sensitive"""
        check = ValidValuesCheck(['active'], case_sensitive=True)
        context = {'column_name': 'status'}
        result = check.validate('invalid', context)
        assert result is not None
        assert "(case-insensitive)" not in result.message


class TestValidValuesCheckEdgeCases:
    """Test ValidValuesCheck edge cases"""
    
    def test_single_valid_value(self):
        """Test with single valid value"""
        check = ValidValuesCheck(['only_value'])
        context = {'column_name': 'field'}
        result = check.validate('only_value', context)
        assert result is None
    
    def test_large_valid_values_list(self):
        """Test with large list of valid values"""
        large_list = [f'value_{i}' for i in range(1000)]
        check = ValidValuesCheck(large_list)
        context = {'column_name': 'field'}
        result = check.validate('value_500', context)
        assert result is None
    
    def test_special_characters_in_values(self):
        """Test with special characters in values"""
        check = ValidValuesCheck(['@#$%', '!@#', 'a-b-c'])
        context = {'column_name': 'field'}
        result = check.validate('@#$%', context)
        assert result is None
    
    def test_repr(self):
        """Test __repr__ method"""
        check = ValidValuesCheck(['a', 'b', 'c'], case_sensitive=True)
        repr_str = repr(check)
        assert "ValidValuesCheck" in repr_str
        assert "3" in repr_str  # Number of values
        assert "True" in repr_str  # case_sensitive

