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
from wxdi.dq_validator.checks.completeness_check import CompletenessCheck
from wxdi.dq_validator.data_quality_dimension import DataQualityDimension

class TestCompletenessCheckInitialization:
    """Comprehensive tests for the CompletenessCheck class"""

    def test_init_without_missing_values_allowed(self):
        """Test default initialization (missing values should NOT be allowed)"""
        check = CompletenessCheck()
        assert check.missing_values_allowed is False

    def test_init_with_missing_values_allowed(self):
        """Test initialization with missing_values_allowed explicitly"""
        check = CompletenessCheck(missing_values_allowed=True)
        assert check.missing_values_allowed is True

    def test_get_check_name(self):
        """Ensure check name is correct"""
        check = CompletenessCheck()
        assert check.get_check_name() == "completeness_check"
    
    def test_get_dimension(self):
        """Test get_dimension returns correct dimension"""
        check = CompletenessCheck()
        assert check.get_dimension() == DataQualityDimension.COMPLETENESS
    
    def test_set_dimension(self):
        """Test set_dimension changes the dimension"""
        check = CompletenessCheck()
        assert check.get_dimension() == DataQualityDimension.COMPLETENESS
        
        check.set_dimension(DataQualityDimension.VALIDITY)
        assert check.get_dimension() == DataQualityDimension.VALIDITY

class TestValidationMissingValuesNotAllowed:
    """ Test completeness check for various value inputs"""

    def test_validate_string_passes(self):
        """Test non-empty string should pass"""
        check = CompletenessCheck(missing_values_allowed=False)
        result = check.validate("Hello", {"column_name": "name"})
        assert result is None

    def test_validate_numerical_passes(self):
        """Test numerical non-empty values should pass"""
        check = CompletenessCheck(missing_values_allowed=False)
        result = check.validate(0, {"column_name": "score"})
        assert result is None

    def test_validate_boolean_passes(self):
        """Booleans should pass"""
        check = CompletenessCheck(missing_values_allowed=False)
        result = check.validate(False, {"column_name": "is_valid"})
        assert result is None

    def test_validate_none_fails(self):
        """None should fail when not allowed"""
        check = CompletenessCheck(missing_values_allowed=False)
        result = check.validate(None, {"column_name": "user_id"})  
        assert result is not None
        assert "user_id is missing" in result.message
        assert result.value is None

    def test_validate_empty_string_fails(self):
        """Purely empty string should fail"""
        check = CompletenessCheck(missing_values_allowed=False)
        result = check.validate("", {"column_name": "email"})
        assert result is not None

    def test_validate_white_space_string_passes(self):
        """Strings with only spaces should fail"""
        check = CompletenessCheck(missing_values_allowed=False)
        result = check.validate("   ", {"column_name": "comments"})
        assert result is None


class TestValidationMissingValuesAllowed:

    def test_missing_allowed_string_passes(self):
        """Test non-empty string should pass"""
        check = CompletenessCheck(missing_values_allowed=True)
        result = check.validate("Hello", {"column_name": "name"})
        assert result is None

    def test_missing_allowed_numerical_passes(self):
        """Test numerical non-empty values should pass"""
        check = CompletenessCheck(missing_values_allowed=True)
        result = check.validate(0, {"column_name": "score"})
        assert result is None

    def test_missing_allowed_boolean_passes(self):
        """Booleans should pass"""
        check = CompletenessCheck(missing_values_allowed=True)
        result = check.validate(False, {"column_name": "is_valid"})
        assert result is None

    def test_missing_allowed_none_passes(self):
        """None should pass when missing_values_allowed is True"""
        check = CompletenessCheck(missing_values_allowed=True)
        result = check.validate(None, {"column_name": "optional_field"})
        assert result is None

    def test_missing_allowed_whitespace_passes(self):
        """Whitespace strings should pass when missing_values_allowed"""
        check = CompletenessCheck(missing_values_allowed=True)
        result = check.validate("   ", {"column_name": "notes"})
        assert result is None


class TestValidateEdgeCases:

    def test_repr(self):
        """Test the string representation"""
        check = CompletenessCheck(missing_values_allowed=True)
        assert "missing_values_allowed=True" in repr(check)