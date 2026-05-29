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
Unit tests for CaseCheck
"""

import pytest
from datetime import date
from wxdi.dq_validator.checks.case_check import CaseCheck, ColumnCaseEnum
from wxdi.dq_validator.data_quality_dimension import DataQualityDimension


class TestCaseCheckInitialization:
    """Test CaseCheck initialization and parameter validation"""
    
    def test_init_with_no_parameter(self):
        """Test initialization without a paramater defaults to CaseCheckEnum : ANY_CASE """
        check = CaseCheck()
        assert check.case_type == ColumnCaseEnum.ANY_CASE

    def test_init_with_parameter(self):
        """Test initialization with a specific case type"""
        check = CaseCheck(case_type=ColumnCaseEnum.UPPER_CASE)
        assert check.case_type == ColumnCaseEnum.UPPER_CASE

    def test_init_with_different_datatype_raises_error(self):
        """Test initialization with a different datatype  raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            CaseCheck("AnyCase")
        assert "case_type must be a ColumnCaseEnum" in str(exc_info.value)

    def test_get_check_name(self):
        """Test get_check_name returns correct name"""
        check = CaseCheck()
        assert check.get_check_name() == "case_check"
    
    def test_get_dimension(self):
        """Test get_dimension returns correct dimension"""
        check = CaseCheck()
        assert check.get_dimension() == DataQualityDimension.CONSISTENCY
    
    def test_set_dimension(self):
        """Test set_dimension changes the dimension"""
        check = CaseCheck()
        assert check.get_dimension() == DataQualityDimension.CONSISTENCY
        
        check.set_dimension(DataQualityDimension.VALIDITY)
        assert check.get_dimension() == DataQualityDimension.VALIDITY


class TestCaseCheckHelperMethods:
    """Test helper methods for word and sentence delimiters"""

    def test_is_word_delimiter(self):
        """Test detection of word delimiters (non-alphabetic characters)"""
        check = CaseCheck()
        assert check._is_word_delimiter(" ") is True
        assert check._is_word_delimiter("-") is True
        assert check._is_word_delimiter("_") is True
        assert check._is_word_delimiter("1") is True
        assert check._is_word_delimiter("'") is True
        assert check._is_word_delimiter(",") is True
        
    def test_not_word_delimiter(self):
        """Test detection of word delimiters fails for alphabetic characters"""
        check = CaseCheck()
        assert check._is_word_delimiter("a") is False
        assert check._is_word_delimiter("Z") is False

    def test_is_sentence_delimiter(self):
        """Test detection of sentence boundaries (. ! ?) """
        check = CaseCheck()
        assert check._is_sentence_delimiter(".") is True
        assert check._is_sentence_delimiter("!") is True
        assert check._is_sentence_delimiter("?") is True
        
    def test_not_sentence_delimiter(self):
        """Test detection of sentence boundaries (. ! ?) fails """
        check = CaseCheck()
        assert check._is_sentence_delimiter(" ") is False
        assert check._is_sentence_delimiter(",") is False
        assert check._is_sentence_delimiter("a") is False
        assert check._is_sentence_delimiter("\n") is False


class TestCaseCheckValidation:
    """Test validation logic for various case scenarios"""

    def test_any_case_passes(self):
        """Test AnyCase accepts any string format"""
        check = CaseCheck(ColumnCaseEnum.ANY_CASE)
        context = {'column_name': 'description'}
        result = check.validate("anything GOES here 123!", context)
        assert result is None

    def test_upper_case_passes(self):
        """Test UpperCase validation success"""
        check = CaseCheck(ColumnCaseEnum.UPPER_CASE)
        context = {'column_name': 'country_code'}
        result = check.validate("USA IS IN WEST", context)
        assert result is None

    def test_upper_case_fails(self):
        """Test UpperCase validation failure"""
        check = CaseCheck(ColumnCaseEnum.UPPER_CASE)
        context = {'column_name': 'country_code'}
        result = check.validate("USA is in west", context)
        assert result is not None
        assert "country_code does not follow UpperCase" in result.message

    def test_lower_case_passes(self):
        """Test LowerCase validation success"""
        check = CaseCheck(ColumnCaseEnum.LOWER_CASE)
        context = {'column_name': 'email'}
        result = check.validate("test@example.com", context)
        assert result is None

    def test_lower_case_fails(self):
        """Test LowerCase validation failure"""
        check = CaseCheck(ColumnCaseEnum.LOWER_CASE)
        context = {'column_name': 'email'}
        result = check.validate("Test@example.com", context)
        assert result is not None
        assert "email does not follow LowerCase" in result.message

    def test_name_case_passes(self):
        """Test NameCase validation success"""
        check = CaseCheck(ColumnCaseEnum.NAME_CASE)
        context = {'column_name': 'full_name'}
        result = check.validate("Jean-Luc O'Niel", context)
        assert result is None

    def test_name_case_fails(self):
        """Test NameCase validation failure"""
        check = CaseCheck(ColumnCaseEnum.NAME_CASE)
        context = {'column_name': 'full_name'}
        result = check.validate("john Doe", context)
        assert result is not None
        result = check.validate("JoHn Doe", context)
        assert result is not None
        assert "full_name does not follow NameCase" in result.message

    def test_sentence_case_passes(self):
        """Test SentenceCase validation success"""
        check = CaseCheck(ColumnCaseEnum.SENTENCE_CASE)
        context = {'column_name': 'comment'}
        result = check.validate("This is a sentence.", context)
        assert result is None
        result = check.validate("First sentence. Second sentence!", context)
        assert result is None

    def test_sentence_case_fails(self):
        """Test SentenceCase validation failure"""
        check = CaseCheck(ColumnCaseEnum.SENTENCE_CASE)
        context = {'column_name': 'comment'}
        result = check.validate("First sentence. second sentence.", context)
        assert result is not None
        assert "comment does not follow SentenceCase" in result.message

    def test_none_value_fails(self):
        """Test None input returns error"""
        check = CaseCheck(ColumnCaseEnum.UPPER_CASE)
        context = {'column_name': 'username'}
        result = check.validate(None, context)
        assert result is not None
        assert "username is None, cannot check the case" in result.message


class TestCaseCheckNonStringTypes:
    """Test validation of different non-string datatypes via auto-conversion"""

    def test_int_input_passes_upper_case(self):
        """Test Integer input to string passes UpperCase."""
        check = CaseCheck(ColumnCaseEnum.UPPER_CASE)
        context = {'column_name': 'id_number'}
        result = check.validate(100, context)
        assert result is None

    def test_float_input_passes_lower_case(self):
        """Test Float input to string passes LowerCase."""
        check = CaseCheck(ColumnCaseEnum.LOWER_CASE)
        context = {'column_name': 'score'}
        result = check.validate(99.9, context)
        assert result is None

    def test_boolean_true_fails_upper_case(self):
        """Test Bool input to string fails UpperCase."""
        check = CaseCheck(ColumnCaseEnum.UPPER_CASE)
        context = {'column_name': 'is_active'}
        result = check.validate(True, context)
        assert result is not None
        # Verify result.value maintains the original boolean type
        assert isinstance(result.value, bool)
        assert "is_active does not follow UpperCase" in result.message

    def test_boolean_false_passes_name_case(self):
        """Test Bool input to string passes NameCase """
        check = CaseCheck(ColumnCaseEnum.NAME_CASE)
        context = {'column_name': 'flag'}
        result = check.validate(False, context)
        assert result is None

    def test_date_input_passes_sentence_case(self):
        """Test Date input passes SentenceCase."""
        check = CaseCheck(ColumnCaseEnum.SENTENCE_CASE)
        context = {'column_name': 'created_at'}
        result = check.validate(date(2024, 1, 1), context)
        assert result is None

    def test_list_input_fails_lower_case(self):
        """Test List input to string fails LowerCase."""
        check = CaseCheck(ColumnCaseEnum.LOWER_CASE)
        context = {'column_name': 'tags'}
        result = check.validate([1, "A"], context)
        assert result is not None
        assert "tags" in result.message
        assert "does not follow LowerCase" in result.message

    def test_custom_object_conversion(self):
        """Test a custom object whose str() representation fails UpperCase"""
        class MockObj:
            def __str__(self):
                return "lower"
        
        check = CaseCheck(ColumnCaseEnum.UPPER_CASE)
        result = check.validate(MockObj(), {'column_name': 'obj'})
        assert result is not None
        assert "obj does not follow UpperCase" in result.message


class TestCaseCheckEdgeCases:
    """Test edge cases for CaseCheck"""

    def test_empty_string_passes(self):
        """Test that empty strings pass case validation """
        check = CaseCheck(ColumnCaseEnum.UPPER_CASE)
        result = check.validate("", {'column_name': 'test'})
        result is None

    def test_repr(self):
        """Test __repr__ output"""
        check = CaseCheck(ColumnCaseEnum.NAME_CASE)
        repr_str = repr(check)
        assert "CaseCheck" in repr_str
        assert "case_type=NameCase" in repr_str