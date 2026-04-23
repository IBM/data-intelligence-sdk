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
Unit tests for Format Check
"""

from wxdi.dq_validator.checks.format_check import FormatCheck, FormatConstraintType
from wxdi.dq_validator.datetime_formats import DateTimeFormats
from wxdi.dq_validator.data_quality_dimension import DataQualityDimension

class TestFormatCheckInitialization:
    """Test FormatCheck initialization"""

    def test_init_valid_formats(self):
        """Test initialization with ValidFormats and format set passes"""
        check = FormatCheck(FormatConstraintType.ValidFormats, {DateTimeFormats.ISO_DATE})
        assert check.constraint_type == FormatConstraintType.ValidFormats
        assert DateTimeFormats.ISO_DATE in check.formats

    def test_init_invalid_formats(self):
        """Test initialization with InvalidFormats and format set"""
        check = FormatCheck(FormatConstraintType.InvalidFormats, {"ABx"})
        assert check.constraint_type == FormatConstraintType.InvalidFormats

    def test_init_multiple_formats(self):
        """Test formats correctly stores multiple formats in the set"""
        formats = {DateTimeFormats.ISO_DATE, DateTimeFormats.UK_DATE, "AAA"}
        check = FormatCheck(FormatConstraintType.ValidFormats, formats)
        assert check.constraint_type == FormatConstraintType.ValidFormats
        assert check.formats == formats
        assert len(check.formats) == 3

    def test_init_without_formats(self):
        """Test initialization without format set"""
        check = FormatCheck(constraint_type=FormatConstraintType.InvalidFormats)
        assert check.constraint_type == FormatConstraintType.InvalidFormats
        assert len(check.formats) == 0

    def test_init_without_constraint_type(self):
        """Test initialization without FormatConstraintType"""
        check = FormatCheck(formats={DateTimeFormats.ISO_DATE})
        assert check.constraint_type == FormatConstraintType.ValidFormats
        assert DateTimeFormats.ISO_DATE in check.formats

    def test_init_without_parameters(self):
        """Test initialization without any parameters"""
        check = FormatCheck()
        assert check.constraint_type == FormatConstraintType.ValidFormats 
        assert len(check.formats) == 0

    def test_get_check_name(self):
        """Test get_check_name returns correct name"""
        check = FormatCheck(FormatConstraintType.ValidFormats, set())
        assert check.get_check_name() == "format_check"
    
    def test_get_dimension(self):
        """Test get_dimension returns correct dimension"""
        check = FormatCheck(FormatConstraintType.ValidFormats, set())
        assert check.get_dimension() == DataQualityDimension.VALIDITY
    
    def test_set_dimension(self):
        """Test set_dimension changes the dimension"""
        check = FormatCheck(FormatConstraintType.ValidFormats, set())
        assert check.get_dimension() == DataQualityDimension.VALIDITY
        
        check.set_dimension(DataQualityDimension.CONSISTENCY)
        assert check.get_dimension() == DataQualityDimension.CONSISTENCY


class TestValidFormats:
    """Test ValidFormats validation where value must match one of the allowed formats"""

    def test_valid_date_format_passes(self):
        """Date format in allowed list should pass"""
        check = FormatCheck(FormatConstraintType.ValidFormats, {DateTimeFormats.ISO_DATE})
        result = check.validate("2024-01-10", {"column_name": "dob"})
        assert result is None

    def test_invalid_date_format_fails(self):
        """Date not in allowed list should fail"""
        check = FormatCheck(FormatConstraintType.ValidFormats, {DateTimeFormats.UK_DATE})
        result = check.validate("2024-01-10", {"column_name": "dob"})
        assert result is not None
        assert "violates" in result.message

    def test_valid_time_passes(self):
        """Time in allowed list should pass"""
        check = FormatCheck(FormatConstraintType.ValidFormats, {DateTimeFormats.TIME_24H})
        result = check.validate("14:23:01", {"column_name": "login_time"})
        assert result is None

    def test_invalid_time_fails(self):
        """Time not in allowed list should fail"""
        check = FormatCheck(FormatConstraintType.ValidFormats, {"%hh:%nn %a"})
        result = check.validate("14:23:01", {"column_name": "login_time"})
        assert result is not None
        assert "violates" in result.message

    def test_valid_timestamp_passes(self):
        """Timestamp in allowed list should pass"""
        check = FormatCheck(FormatConstraintType.ValidFormats, {"%yyyy-%mm-%dd %HH:%nn:%ss"})
        result = check.validate("2024-01-10 14:23:01", {"column_name": "created_at"})
        assert result is None


class TestComplexFormatScenarios:
    """High-complexity format validation scenarios"""

    def test_complex_alphanumeric_with_symbols_valid(self):
        """Mixed case, digits and symbols should match expected format"""
        check = FormatCheck(
            FormatConstraintType.ValidFormats,
            {"Aa@99#Aa"}
        )
        result = check.validate("Ab@12#Xy", {"column_name": "password"})
        assert result is None

    def test_email_like_string_valid_format(self):
        """Email-like structure should match detected format"""
        check = FormatCheck(
            FormatConstraintType.ValidFormats,
            {"aaaa@aaaa.aaa"}
        )
        result = check.validate("user@mail.com", {"column_name": "email"})
        assert result is None

    def test_ideographic_common_sandwich_valid(self):
        """Common script between ideographs should be treated as ideographic"""
        check = FormatCheck(
            FormatConstraintType.ValidFormats,
            {"III"}
        )
        result = check.validate("中·国", {"column_name": "country"})
        assert result is None

    def test_emoji_surrogate_valid_format(self):
        """Emoji (surrogate pair) should be preserved as-is"""
        check = FormatCheck(
            FormatConstraintType.ValidFormats,
            {"😀"}
        )
        result = check.validate("😀", {"column_name": "icon"})
        assert result is None

    def test_string_longer_than_255_maps_to_na(self):
        """Strings longer than 255 UTF-16 units should map to <NA>"""
        long_value = "a" * 256
        check = FormatCheck(
            FormatConstraintType.ValidFormats,
            {"<NA>"}
        )
        result = check.validate(long_value, {"column_name": "payload"})
        assert result is None

    def test_numeric_value_vs_numeric_string_difference(self):
        """Numeric value should not be treated the same as numeric string"""
        check = FormatCheck(
            FormatConstraintType.ValidFormats,
            {"999"}
        )
        result = check.validate(123, {"column_name": "code"})
        assert result is None


class TestInvalidFormats:
    """Test InvalidFormats validation where value must not match any forbidden format"""

    def test_forbidden_date_fails(self):
        """Forbidden date format should fail"""
        check = FormatCheck(FormatConstraintType.InvalidFormats, {DateTimeFormats.ISO_DATE})
        result = check.validate("2024-01-10", {"column_name": "dob"})
        assert result is not None
        assert "violates" in result.message

    def test_allowed_date_passes(self):
        """Date not in forbidden list should pass"""
        check = FormatCheck(FormatConstraintType.InvalidFormats, {DateTimeFormats.UK_DATE})
        result = check.validate("2024-01-10", {"column_name": "dob"})
        assert result is None

    def test_forbidden_time_fails(self):
        """Forbidden time format should fail"""
        check = FormatCheck(FormatConstraintType.InvalidFormats, {DateTimeFormats.TIME_24H})
        result = check.validate("14:23:01", {"column_name": "time"})
        assert result is not None
        assert "violates" in result.message

    def test_allowed_time_passes(self):
        """Time not in forbidden list should pass"""
        check = FormatCheck(FormatConstraintType.InvalidFormats, {"%hh:%nn %a"})
        result = check.validate("14:23:01", {"column_name": "time"})
        assert result is None


class TestNoDetectedFormat:
    """Test behavior when InferredTypeEngine cannot detect any format"""

    def test_string_with_no_format_valid_formats(self):
        """Non-date string should fail ValidFormats"""
        check = FormatCheck(FormatConstraintType.ValidFormats, {"%yyyy-%nn-%dd"})
        result = check.validate("hello", {"column_name": "name"})
        assert result is not None
        assert "violates" in result.message

    def test_string_with_no_format_invalid_formats(self):
        """Non-date string should pass InvalidFormats"""
        check = FormatCheck(FormatConstraintType.InvalidFormats, {"%yyyy-%nn-%dd"})
        result = check.validate("hello", {"column_name": "name"})
        assert result is None


class TestEmptyAndNAFormats:
    """Tests for <EMPTY> and <NA> format handling"""

    def test_empty_string_allowed_when_empty_format_present(self):
        """Empty string should map to <EMPTY> and pass when allowed"""
        check = FormatCheck(FormatConstraintType.ValidFormats, {"<EMPTY>"})
        result = check.validate("", {"column_name": "comment"})
        assert result is None

    def test_empty_string_rejected_when_empty_format_not_allowed(self):
        """Empty string should fail ValidFormats when <EMPTY> not allowed"""
        check = FormatCheck(FormatConstraintType.ValidFormats, {"AAA"})
        result = check.validate("", {"column_name": "comment"})
        assert result is not None
        assert "violates" in result.message

    def test_empty_string_blocked_by_invalid_formats(self):
        """Empty string should fail InvalidFormats when <EMPTY> is forbidden"""
        check = FormatCheck(FormatConstraintType.InvalidFormats, {"<EMPTY>"})
        result = check.validate("", {"column_name": "comment"})
        assert result is not None
        assert "violates" in result.message

    def test_long_string_maps_to_na_and_passes_when_allowed(self):
        """String longer than 255 UTF-16 units should map to <NA> and pass when allowed"""
        long_value = "A" * 300
        check = FormatCheck(FormatConstraintType.ValidFormats, {"<NA>"})
        result = check.validate(long_value, {"column_name": "payload"})
        assert result is None

    def test_long_string_rejected_when_na_not_allowed(self):
        """String mapping to <NA> should fail ValidFormats when <NA> not allowed"""
        long_value = "A" * 300
        check = FormatCheck(FormatConstraintType.ValidFormats, {"AAA"})
        result = check.validate(long_value, {"column_name": "payload"})
        assert result is not None
        assert "violates" in result.message

    def test_na_blocked_by_invalid_formats(self):
        """<NA> should fail InvalidFormats when explicitly forbidden"""
        long_value = "A" * 300
        check = FormatCheck(FormatConstraintType.InvalidFormats, {"<NA>"})
        result = check.validate(long_value, {"column_name": "payload"})
        assert result is not None
        assert "violates" in result.message


class TestIdeographicCommonSandwich:
    """Tests ideograph + COMMON + ideograph → III behavior"""

    def test_han_common_han(self):
        """Han ideographs with COMMON in between should map to III"""
        check = FormatCheck(FormatConstraintType.ValidFormats, {"III"})
        result = check.validate("中·国", {"column_name": "value"})
        assert result is None

    def test_hiragana_common_hiragana(self):
        """Hiragana with COMMON in between should map to III"""
        check = FormatCheck(FormatConstraintType.ValidFormats, {"III"})
        result = check.validate("あ・い", {"column_name": "value"})
        assert result is None

    def test_katakana_common_katakana(self):
        """Katakana with COMMON in between should map to III"""
        check = FormatCheck(FormatConstraintType.ValidFormats, {"III"})
        result = check.validate("カ・タ", {"column_name": "value"})
        assert result is None

    def test_hangul_common_hangul(self):
        """Hangul with COMMON in between should map to III"""
        check = FormatCheck(FormatConstraintType.ValidFormats, {"III"})
        result = check.validate("한·국", {"column_name": "value"})
        assert result is None



class TestFormatCheckConstraintEdgeCases:
    """Test FormatCheck behavior when constraint type or format sets are missing or empty"""

    def test_valid_formats_empty_rejects_date(self):
        """With ValidFormats and empty set, any detected format should fail"""
        check = FormatCheck(FormatConstraintType.ValidFormats, set())
        result = check.validate("2024-01-10", {"column_name": "dob"})
        assert result is not None
        assert "violates" in result.message

    def test_invalid_formats_empty_allows_date(self):
        """With InvalidFormats and empty set, any detected format should pass"""
        check = FormatCheck(FormatConstraintType.InvalidFormats, set())
        result = check.validate("2024-01-10", {"column_name": "dob"})
        assert result is None

    def test_valid_formats_none_rejects(self):
        """formats=None behaves like empty set for ValidFormats"""
        check = FormatCheck(FormatConstraintType.ValidFormats, None)
        result = check.validate("2024-01-10", {"column_name": "dob"})
        assert result is not None
        assert "violates" in result.message

    def test_invalid_formats_none_allows(self):
        """formats=None behaves like empty set for InvalidFormats"""
        check = FormatCheck(FormatConstraintType.InvalidFormats, None)
        result = check.validate("2024-01-10", {"column_name": "dob"})
        assert result is None


class TestNumericValues:
    """Test behavior when numeric values are passed"""

    def test_numeric_value_valid_formats(self):
        """Numbers should fail ValidFormats for the date format"""
        check = FormatCheck(FormatConstraintType.ValidFormats, {DateTimeFormats.ISO_DATE})
        result = check.validate(123, {"column_name": "value"})
        assert result is not None
        assert "violates" in result.message

    def test_numeric_value_invalid_formats(self):
        """Numbers should pass in case of invalid date formats"""
        check = FormatCheck(FormatConstraintType.InvalidFormats, {DateTimeFormats.ISO_DATE})
        result = check.validate(123, {"column_name": "value"})
        assert result is None

class TestTimeZones:
    """Test handling of timezone and Zulu (Z) timestamps"""

    def test_zulu_timestamp(self):
        """Zulu timestamp should match %z-based formats"""
        check = FormatCheck(
            FormatConstraintType.ValidFormats,
            {"%yyyy-%mm-%dd %HH:%nn:%ssZ"}
        )
        result = check.validate("2024-01-10 14:23:01Z", {"column_name": "ts"})
        assert result is None
