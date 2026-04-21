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
Unit tests for LengthCheck
"""

import pytest
from wxdi.dq_validator.checks.length_check import LengthCheck
from wxdi.dq_validator.data_quality_dimension import DataQualityDimension


class TestLengthCheckInitialization:
    """Test LengthCheck initialization and parameter validation"""
    
    def test_init_with_min_length_only(self):
        """Test initialization with only min_length"""
        check = LengthCheck(min_length=5)
        assert check.min_length == 5
        assert check.max_length is None
    
    def test_init_with_max_length_only(self):
        """Test initialization with only max_length"""
        check = LengthCheck(max_length=10)
        assert check.min_length is None
        assert check.max_length == 10
    
    def test_init_with_both_lengths(self):
        """Test initialization with both min and max length"""
        check = LengthCheck(min_length=3, max_length=20)
        assert check.min_length == 3
        assert check.max_length == 20
    
    def test_init_no_parameters_raises_error(self):
        """Test that initialization without parameters raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            LengthCheck()
        assert "At least one of min_length or max_length must be specified" in str(exc_info.value)
    
    def test_init_negative_min_length_raises_error(self):
        """Test that negative min_length raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            LengthCheck(min_length=-1)
        assert "min_length cannot be negative" in str(exc_info.value)
    
    def test_init_negative_max_length_raises_error(self):
        """Test that negative max_length raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            LengthCheck(max_length=-5)
        assert "max_length cannot be negative" in str(exc_info.value)
    
    def test_init_min_greater_than_max_raises_error(self):
        """Test that min_length > max_length raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            LengthCheck(min_length=10, max_length=5)
        assert "min_length (10) cannot be greater than max_length (5)" in str(exc_info.value)
    
    def test_get_check_name(self):
        """Test get_check_name returns correct name"""
        check = LengthCheck(min_length=1)
        assert check.get_check_name() == "length_check"
    
    def test_get_dimension(self):
        """Test get_dimension returns correct dimension"""
        check = LengthCheck(min_length=1)
        assert check.get_dimension() == DataQualityDimension.VALIDITY
    
    def test_set_dimension(self):
        """Test set_dimension changes the dimension"""
        check = LengthCheck(min_length=1)
        assert check.get_dimension() == DataQualityDimension.VALIDITY
        
        check.set_dimension(DataQualityDimension.CONSISTENCY)
        assert check.get_dimension() == DataQualityDimension.CONSISTENCY


class TestLengthCheckStringValidation:
    """Test LengthCheck with string values"""
    
    def test_string_within_range_passes(self):
        """Test string within min/max range passes"""
        check = LengthCheck(min_length=3, max_length=20)
        context = {'column_name': 'username'}
        result = check.validate('john_doe', context)
        assert result is None
    
    def test_string_too_short_fails(self):
        """Test string shorter than min_length fails"""
        check = LengthCheck(min_length=3, max_length=20)
        context = {'column_name': 'username'}
        result = check.validate('ab', context)
        assert result is not None
        assert result.column_name == 'username'
        assert result.check_name == 'length_check'
        assert "length (2) is less than minimum (3)" in result.message
    
    def test_string_too_long_fails(self):
        """Test string longer than max_length fails"""
        check = LengthCheck(min_length=3, max_length=20)
        context = {'column_name': 'username'}
        result = check.validate('a' * 25, context)
        assert result is not None
        assert "length (25) exceeds maximum (20)" in result.message
    
    def test_empty_string_with_min_zero_passes(self):
        """Test empty string passes when min_length is 0"""
        check = LengthCheck(min_length=0, max_length=100)
        context = {'column_name': 'optional_field'}
        result = check.validate('', context)
        assert result is None
    
    def test_empty_string_with_min_one_fails(self):
        """Test empty string fails when min_length is 1"""
        check = LengthCheck(min_length=1, max_length=100)
        context = {'column_name': 'required_field'}
        result = check.validate('', context)
        assert result is not None
        assert "length (0) is less than minimum (1)" in result.message
    
    def test_exact_length_required_passes(self):
        """Test exact length requirement passes"""
        check = LengthCheck(min_length=2, max_length=2)
        context = {'column_name': 'country_code'}
        result = check.validate('US', context)
        assert result is None
    
    def test_exact_length_required_fails(self):
        """Test exact length requirement fails"""
        check = LengthCheck(min_length=2, max_length=2)
        context = {'column_name': 'country_code'}
        result = check.validate('USA', context)
        assert result is not None
        assert "length (3) exceeds maximum (2)" in result.message
    
    def test_unicode_characters(self):
        """Test Unicode characters are counted correctly"""
        check = LengthCheck(min_length=1, max_length=10)
        context = {'column_name': 'name'}
        result = check.validate('日本語', context)
        assert result is None  # Length is 3 characters
    
    def test_whitespace_only_string(self):
        """Test whitespace-only string is counted"""
        check = LengthCheck(min_length=1, max_length=10)
        context = {'column_name': 'text'}
        result = check.validate('   ', context)
        assert result is None  # Length is 3


class TestLengthCheckNonStringValidation:
    """Test LengthCheck with non-string values (converted to string)"""
    
    def test_integer_value_passes(self):
        """Test integer value is converted to string"""
        check = LengthCheck(min_length=3, max_length=10)
        context = {'column_name': 'id'}
        result = check.validate(12345, context)
        assert result is None  # str(12345) = "12345", length = 5
    
    def test_integer_value_fails(self):
        """Test integer value fails when string length is out of range"""
        check = LengthCheck(min_length=1, max_length=5)
        context = {'column_name': 'number'}
        result = check.validate(123456789, context)
        assert result is not None
        assert "length (9) exceeds maximum (5)" in result.message
    
    def test_float_value_passes(self):
        """Test float value is converted to string"""
        check = LengthCheck(min_length=3, max_length=10)
        context = {'column_name': 'amount'}
        result = check.validate(123.45, context)
        assert result is None  # str(123.45) = "123.45", length = 6
    
    def test_boolean_true_passes(self):
        """Test boolean True is converted to string"""
        check = LengthCheck(min_length=4, max_length=5)
        context = {'column_name': 'flag'}
        result = check.validate(True, context)
        assert result is None  # str(True) = "True", length = 4
    
    def test_boolean_false_passes(self):
        """Test boolean False is converted to string"""
        check = LengthCheck(min_length=5, max_length=5)
        context = {'column_name': 'flag'}
        result = check.validate(False, context)
        assert result is None  # str(False) = "False", length = 5
    
    def test_list_value_passes(self):
        """Test list value is converted to string"""
        check = LengthCheck(min_length=5, max_length=50)
        context = {'column_name': 'data'}
        result = check.validate([1, 2, 3], context)
        assert result is None  # str([1, 2, 3]) = "[1, 2, 3]", length = 9
    
    def test_dict_value_passes(self):
        """Test dict value is converted to string"""
        check = LengthCheck(min_length=5, max_length=50)
        context = {'column_name': 'config'}
        result = check.validate({'a': 1}, context)
        assert result is None  # str({'a': 1}) = "{'a': 1}", length varies


class TestLengthCheckNoneHandling:
    """Test LengthCheck with None values"""
    
    def test_none_value_fails(self):
        """Test None value returns error"""
        check = LengthCheck(min_length=3, max_length=20)
        context = {'column_name': 'username'}
        result = check.validate(None, context)
        assert result is not None
        assert result.column_name == 'username'
        assert "is None, cannot check length" in result.message


class TestLengthCheckMinLengthOnly:
    """Test LengthCheck with only min_length specified"""
    
    def test_min_length_only_passes(self):
        """Test validation passes when only min_length is specified"""
        check = LengthCheck(min_length=10)
        context = {'column_name': 'description'}
        result = check.validate('a' * 100, context)
        assert result is None  # No max limit
    
    def test_min_length_only_fails(self):
        """Test validation fails when below min_length"""
        check = LengthCheck(min_length=10)
        context = {'column_name': 'description'}
        result = check.validate('short', context)
        assert result is not None
        assert "length (5) is less than minimum (10)" in result.message


class TestLengthCheckMaxLengthOnly:
    """Test LengthCheck with only max_length specified"""
    
    def test_max_length_only_passes(self):
        """Test validation passes when only max_length is specified"""
        check = LengthCheck(max_length=10)
        context = {'column_name': 'code'}
        result = check.validate('ABC', context)
        assert result is None  # No min limit
    
    def test_max_length_only_fails(self):
        """Test validation fails when exceeds max_length"""
        check = LengthCheck(max_length=10)
        context = {'column_name': 'code'}
        result = check.validate('a' * 15, context)
        assert result is not None
        assert "length (15) exceeds maximum (10)" in result.message


class TestLengthCheckEdgeCases:
    """Test LengthCheck edge cases"""
    
    def test_zero_min_length(self):
        """Test min_length of 0 is valid"""
        check = LengthCheck(min_length=0, max_length=10)
        context = {'column_name': 'field'}
        result = check.validate('', context)
        assert result is None
    
    def test_zero_max_length(self):
        """Test max_length of 0 requires empty string"""
        check = LengthCheck(min_length=0, max_length=0)
        context = {'column_name': 'field'}
        result = check.validate('', context)
        assert result is None
    
    def test_zero_max_length_fails_with_content(self):
        """Test max_length of 0 fails with non-empty string"""
        check = LengthCheck(min_length=0, max_length=0)
        context = {'column_name': 'field'}
        result = check.validate('a', context)
        assert result is not None
        assert "length (1) exceeds maximum (0)" in result.message
    
    def test_large_min_length(self):
        """Test very large min_length"""
        check = LengthCheck(min_length=1000)
        context = {'column_name': 'field'}
        result = check.validate('a' * 999, context)
        assert result is not None
        assert "length (999) is less than minimum (1000)" in result.message
    
    def test_repr(self):
        """Test __repr__ method"""
        check = LengthCheck(min_length=5, max_length=10)
        repr_str = repr(check)
        assert "LengthCheck" in repr_str
        assert "5" in repr_str
        assert "10" in repr_str

