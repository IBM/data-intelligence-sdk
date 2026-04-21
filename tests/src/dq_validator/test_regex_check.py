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
Unit tests for RegexCheck
"""

import pytest
import re
from wxdi.dq_validator.checks.regex_check import RegexCheck
from wxdi.dq_validator.data_quality_dimension import DataQualityDimension

class TestRegexCheckInitialization:
    """Test RegexCheck initialization and parameter validation"""

    def test_init_with_only_pattern(self):
        """Test successful initialization with only a valid pattern"""
        pattern = r"^[A-Z]{3}$"
        check = RegexCheck(pattern = r"^[A-Z]{3}$")
        assert check.pattern == pattern
        assert check.case_sensitive is True
        assert isinstance(check._compiled_pattern, re.Pattern)
    
    def test_init_with_only_case_sensitive_raises_error(self):
        """Test failed initialization with only a case_sensitive"""
        with pytest.raises(ValueError) as exc_info:
            RegexCheck(case_sensitive=True)
        assert "pattern must be a non-empty string" in str(exc_info.value)

    def test_init_with_both_parameters(self):
        """Test successful initialization with only a valid pattern"""
        pattern = r"^[A-Z]{3}$"
        check = RegexCheck(pattern = r"^[A-Z]{3}$", case_sensitive = False)
        assert check.pattern == pattern
        assert check.case_sensitive is False
        assert isinstance(check._compiled_pattern, re.Pattern)

    def test_init_with_no_parameter_raises_error(self):
        """Test failed initialization with no parameter"""
        with pytest.raises(ValueError) as exc_info:
            RegexCheck()
        assert "pattern must be a non-empty string" in str(exc_info.value)

    def test_init_empty_string_raises_error(self):
        """Test that empty string pattern raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            RegexCheck(pattern="" , case_sensitive = True)
        assert "pattern must be a non-empty string" in str(exc_info.value)

    def test_init_invalid_type_raises_error(self):
        """Test that non-string pattern raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            RegexCheck(pattern=123)
        assert "pattern must be a non-empty string" in str(exc_info.value)

    def test_init_invalid_regex_syntax_raises_error(self):
        """Test that syntactically incorrect regex raises ValueError"""
        invalid_pattern = "[0-9"  # Missing closing bracket
        with pytest.raises(ValueError) as exc_info:
            RegexCheck(pattern=invalid_pattern)
        assert f"Invalid regex pattern '{invalid_pattern}'" in str(exc_info.value)

    def test_get_check_name(self):
        """Test get_check_name returns correct name"""
        check = RegexCheck(pattern=r"^[A-Z]{3}$")
        assert check.get_check_name() == "regex_check"
    
    def test_get_dimension(self):
        """Test get_dimension returns correct dimension"""
        check = RegexCheck(pattern=r"^[A-Z]{3}$")
        assert check.get_dimension() == DataQualityDimension.VALIDITY
    
    def test_set_dimension(self):
        """Test set_dimension changes the dimension"""
        check = RegexCheck(pattern=r"^[A-Z]{3}$")
        assert check.get_dimension() == DataQualityDimension.VALIDITY
        
        check.set_dimension(DataQualityDimension.CONSISTENCY)
        assert check.get_dimension() == DataQualityDimension.CONSISTENCY


class TestRegexCheckValidation:
    """Test validation logic for regex matching"""

    def test_regex_match_passes(self):
        """Test that value matching the pattern passes"""
        # Pattern for a simple email-like structure
        check = RegexCheck(pattern=r"^\w+@\w+\.com$")
        context = {'column_name': 'email'}
        result = check.validate("user@test.com", context)
        assert result is None

    def test_regex_no_match_fails(self):
        """Test that value not matching the pattern returns ValidationError"""
        check = RegexCheck(pattern=r"^\d{3}-\d{2}$")  # Format: 000-00
        context = {'column_name': 'code'}
        val = "123-A"
        result = check.validate(val, context)        
        assert result is not None
        assert r"code ('123-A') does not match pattern '^\d{3}-\d{2}$'" in result.message

    def test_regex_partial_match_passes(self):
        """Test that .search() allows partial matches unless anchored"""
        # Pattern is not anchored with ^ or $
        check = RegexCheck(pattern=r"cat")
        context = {'column_name': 'sentence'}
        result = check.validate("the category", context)
        assert result is None

    def test_regex_partial_match_fails(self):
        """Test that .search() fails when the pattern is nowhere in the string"""
        check = RegexCheck(pattern=r"cat")
        context = {'column_name': 'sentence'}
        result = check.validate("the dog runs", context)
        assert result is not None
        assert "sentence ('the dog runs') does not match pattern 'cat'" in result.message

    def test_case_sensitive_match_passes(self):
        """Test passes when case_sensitive is True (default)"""
        check = RegexCheck(pattern=r"^abc$")
        context = {'column_name': 'test'}    
        result = check.validate("abc", context)
        assert result is None
    
    def test_case_sensitive_match_fails(self):
        """Test fails when case_sensitive is True (default)"""
        check = RegexCheck(pattern=r"^abc$")
        context = {'column_name': 'test'}    
        result = check.validate("ABC", context)
        assert result is not None 
        assert "test ('ABC') does not match pattern '^abc$'" in result.message

    def test_case_insensitive_match_passes(self):
        """Test passes when case_sensitive is False"""
        check = RegexCheck(pattern=r"^abc$", case_sensitive=False)
        context = {'column_name': 'test'}
        result = check.validate("abc", context)
        assert result is None
        result = check.validate("ABC", context)
        assert result is None
        result = check.validate("aBc", context)
        assert result is None

    def test_case_insensitive_match_fails(self):
        """Test fails when case_sensitive is False"""
        check = RegexCheck(pattern=r"^abc$", case_sensitive=False)
        context = {'column_name': 'test'}
        result = check.validate("XabcY", context)
        assert result is not None
        assert "test ('XabcY') does not match pattern '^abc$'" in result.message

    def test_empty_string_passes(self):
        """Test that an empty string passes if the pattern allows it (e.g., zero or more)"""
        check = RegexCheck(pattern=r"^\d*$")
        context = {'column_name': 'optional_id'}
        result = check.validate("", context)
        assert result is None

    def test_empty_string_fails(self):
        """Test that an empty string fails if the pattern requires characters"""
        check = RegexCheck(pattern=r"^\d+$")
        context = {'column_name': 'required_id'}      
        result = check.validate("", context)
        assert result is not None
        assert "does not match pattern" in result.message

    def test_whitespace_string_passes(self):
        """Test that whitespace passes if the pattern allows it (Note: .strip() makes this '')"""
        check = RegexCheck(pattern=r"^$")
        context = {'column_name': 'blank_space'}       
        result = check.validate("   ", context)
        assert result is None

    def test_whitespace_string_fails(self):
        """Test that whitespace fails if the pattern expects actual content"""
        check = RegexCheck(pattern=r"^\w+$")
        context = {'column_name': 'username'}
        result = check.validate("   ", context)
        assert result is not None
        assert "('') does not match pattern" in result.message

    def test_regex_none_value_fails(self):
        """Test that None value matching the pattern fails"""
        check = RegexCheck(pattern=r"^\w+@\w+\.com$")
        context = {'column_name': 'email'}
        result = check.validate(None, context)
        assert result is not None
        assert "email is None, cannot perform regex check" in result.message


class TestRegexCheckValueDataTypes:
    """Test validation of different data types for the value parameter"""

    def test_validate_integer_passes(self):
        """Matches when the integer string representation fits the pattern"""
        check = RegexCheck(pattern=r"^\d{3}$")
        result = check.validate(123, {'column_name': 'id'})
        assert result is None

    def test_validate_integer_fails(self):
        """Fails when the integer string representation doesn't fit (too many digits)"""
        check = RegexCheck(pattern=r"^\d{2}$")
        result = check.validate(123, {'column_name': 'id'})
        assert result is not None
        assert "does not match pattern" in result.message

    def test_validate_float_passes(self):
        """Matches a decimal string representation"""
        check = RegexCheck(pattern=r"^\d+\.\d+$")
        result = check.validate(99.99, {'column_name': 'price'})
        assert result is None

    def test_validate_float_fails(self):
        """Fails when float contains unexpected characters (like the dot) for a digit-only pattern"""
        check = RegexCheck(pattern=r"^\d+$")
        result = check.validate(99.9, {'column_name': 'price'})
        assert result is not None

    def test_validate_boolean_passes(self):
        """Matches 'True' or 'False' (Python's capitalized string format)"""
        check = RegexCheck(pattern=r"^(True|False)$")
        result = check.validate(True, {'column_name': 'active'})
        assert result is None

    def test_validate_boolean_fails(self):
        check = RegexCheck(pattern=r"^true$", case_sensitive=True)
        result = check.validate(True, {'column_name': 'active'})
        assert result is not None

    def test_validate_list_passes(self):
        """Matches the literal string representation of a list"""
        check = RegexCheck(pattern=r"^\[.*\]$")
        result = check.validate([1, 2], {'column_name': 'tags'})
        assert result is None

    def test_validate_list_fails(self):
        """Fails when list contents don't match the specific pattern"""
        check = RegexCheck(pattern=r"^\[\d\]$")
        result = check.validate([1, 2], {'column_name': 'tags'})
        assert result is not None


class TestRegexCheckEdgeCases:
    """Test edge cases and special regex scenarios"""

    def test_regex_with_special_characters(self):
        """Test regex containing special characters and escape sequences"""
        check = RegexCheck(pattern=r"^\$ \d+\.\d{2}$") # Format: $ 10.00
        context = {'column_name': 'price'}
        result = check.validate("$ 10.99", context)
        assert result is None
        result = check.validate("10.99", context)
        assert result is not None

    def test_validate_none_custom_message(self):
        """Verify the specific error message for None inputs"""
        check = RegexCheck(pattern=r"^None$")
        result = check.validate(None, {'column_name': 'val'})
        assert "is None, cannot perform regex check" in result.message


    def test_repr(self):
        """Test __repr__ output"""
        check = RegexCheck(pattern=r"\d+", case_sensitive=False)
        repr_str = repr(check)
        assert "RegexCheck" in repr_str
        assert "pattern='\\d+'" in repr_str
        assert "case_sensitive=False" in repr_str