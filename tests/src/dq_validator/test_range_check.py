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
Unit tests for RangeCheck
"""

import pytest
from decimal import Decimal
from datetime import datetime, date
from wxdi.dq_validator.checks.range_check import RangeCheck
from wxdi.dq_validator.data_quality_dimension import DataQualityDimension


class TestRangeCheckInitialization:
    """Test RangeCheck initialization and parameter validation"""

    def test_init_with_min_value_only(self):
        """Test initialization with only min_value"""
        check = RangeCheck(min_value=10)
        assert isinstance(check.min_value, Decimal)
        assert check.min_value == Decimal("10")
        assert check.max_value is None

    def test_init_with_max_value_only(self):
        """Test initialization with only max_value"""
        check = RangeCheck(max_value=20)
        assert isinstance(check.max_value, Decimal)
        assert check.min_value is None
        assert check.max_value == Decimal("20")

    def test_init_with_both_values(self):
        """Test successful initialization with min and max"""
        check = RangeCheck(min_value=10, max_value=20)
        assert isinstance(check.min_value, Decimal)
        assert isinstance(check.max_value, Decimal)
        assert check.min_value == Decimal("10")
        assert check.max_value == Decimal("20")

    def test_init_with_no_parameters_raises_error(self):
        """Test that missing min or max raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            RangeCheck()
        assert "At least one of min_value or max_value must be specified" in str(
            exc_info.value
        )

    def test_init_min_greater_than_max_raises_error(self):
        """Test that min_value > max_value raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            RangeCheck(min_value=20, max_value=10)
        assert "min_value (20) cannot be greater than max_value (10)" in str(
            exc_info.value
        )

    def test_init_incompatible_numeric_and_string_raises_error(self):
        """Test initialization failure when min is Decimal and max is string"""
        with pytest.raises(TypeError) as exc_info:
            RangeCheck(min_value=10, max_value="20")
        assert "Incompatible types of min_value and max_value" in str(exc_info.value)

    def test_init_incompatible_datetime_and_decimal_raises_error(self):
        """Test initialization failure when min is datetime and max is Decimal"""
        with pytest.raises(TypeError) as exc_info:
            RangeCheck(min_value=date(2024, 1, 1), max_value=500.5)
        assert "Incompatible types of min_value and max_value" in str(exc_info.value)

    def test_init_incompatible_string_and_datetime_raises_error(self):
        """Test initialization failure when min is string and max is datetime"""
        with pytest.raises(TypeError) as exc_info:
            RangeCheck(min_value="2024-01-01", max_value=date(2024, 12, 31))
        assert "Incompatible types of min_value and max_value" in str(exc_info.value)

    def test_get_check_name(self):
        """Test get_check_name returns correct name"""
        check = RangeCheck(min_value=10, max_value=20)
        assert check.get_check_name() == "range_check"
    
    def test_get_dimension(self):
        """Test get_dimension returns correct dimension"""
        check = RangeCheck(min_value=10, max_value=20)
        assert check.get_dimension() == DataQualityDimension.VALIDITY
    
    def test_set_dimension(self):
        """Test set_dimension changes the dimension"""
        check = RangeCheck(min_value=10, max_value=20)
        assert check.get_dimension() == DataQualityDimension.VALIDITY
        
        check.set_dimension(DataQualityDimension.CONSISTENCY)
        assert check.get_dimension() == DataQualityDimension.CONSISTENCY


class TestRangeCheckNormalization:
    """Test normalization logic via class initialization"""

    def test_normalize_numeric_init(self):
        """Test normalization of int and float values to Decimal"""
        check = RangeCheck(min_value=10, max_value=20.5)
        assert isinstance(check.min_value, Decimal)
        assert isinstance(check.max_value, Decimal)
        assert check.min_value == Decimal("10")
        assert check.max_value == Decimal("20.5")

    def test_normalize_decimal_init(self):
        """Test normalization of default Decimal values to Decimal"""
        check = RangeCheck(min_value=Decimal("10"), max_value=Decimal("20.5"))
        assert isinstance(check.min_value, Decimal)
        assert isinstance(check.max_value, Decimal)
        assert check.min_value == Decimal("10")
        assert check.max_value == Decimal("20.5")

    def test_normalize_date_init(self):
        """Test normalization of date and default datetime objects to datetime"""
        check = RangeCheck(
            min_value=date(2024, 1, 1),
            max_value=datetime(2024, 12, 31, 23, 59, 59, 999999),
        )
        assert isinstance(check.min_value, datetime)
        assert isinstance(check.max_value, datetime)
        assert check.min_value == datetime(2024, 1, 1, 0, 0, 0)
        assert check.max_value == datetime(2024, 12, 31, 23, 59, 59, 999999)
        assert check.max_value.microsecond == 999999

    def test_normalize_string_fallback_init(self):
        """Test non-numeric and non-date inputs fallback to string during init"""
        check = RangeCheck(min_value="alpha", max_value="omega")
        assert isinstance(check.min_value, str)
        assert isinstance(check.max_value, str)
        assert check.min_value == "alpha"
        assert check.max_value == "omega"

    def test_normalization_none_init(self):
        """Test normalization of None inputs return None"""
        check = RangeCheck(min_value="alpha")
        assert isinstance(check.min_value, str)
        assert check.min_value == "alpha"
        assert check.max_value == None


class TestRangeCheckValidation:
    """Test validation logic for various scenarios"""

    def test_range_passes(self):
        """Test value within range passes"""
        check = RangeCheck(min_value=10, max_value=20)
        context = {"column_name": "score"}
        assert check.validate(15, context) is None
        assert check.validate(10, context) is None  # Boundary inclusive
        assert check.validate(20, context) is None  # Boundary inclusive

    def test_less_than_min_fails(self):
        """Test value below minimum fails"""
        check = RangeCheck(min_value=10, max_value=20)
        context = {"column_name": "score"}
        result = check.validate(5, context)
        assert result is not None
        assert "score (5) is less than minimum (10)" in result.message

    def test_greater_than_max_fails(self):
        """Test value above maximum fails"""
        check = RangeCheck(min_value=10, max_value=20)
        context = {"column_name": "score"}
        result = check.validate(25, context)
        assert result is not None
        assert "score (25) is greater than maximum (20)" in result.message

    def test_none_value_fails(self):
        """Test None value fails check"""
        check = RangeCheck(min_value="alpha", max_value="gamma")
        context = {"column_name": "title"}
        result = check.validate(None, context)
        assert result is not None
        assert "title is None, cannot check to be within range" in result.message

    def test_range_empty_string_passes(self):
        """Passes because '' is not less than the min '' and not greater than 'z'"""
        check = RangeCheck(min_value="", max_value="z")
        context = {"column_name": "code"}
        result = check.validate("", context)
        assert result is None

    def test_range_empty_string_fails(self):
        """Fails because '' is lexicographically less than 'a'"""
        check = RangeCheck(min_value="a", max_value="z")
        context = {"column_name": "code"}
        result = check.validate("", context)
        assert result is not None
        assert "code () is less than minimum (a)" in result.message

    def test_range_whitespace_passes(self):
        """Passes because '  ' (two spaces) is 'greater' than ' ' (one space)"""
        check = RangeCheck(min_value=" ", max_value="z")
        context = {"column_name": "padded_val"}
        result = check.validate("  ", context)
        assert result is None

    def test_range_whitespace_fails(self):
        """Fails because a space is lexicographically less than the character '0'"""
        check = RangeCheck(min_value="0", max_value="9")
        context = {"column_name": "digit_check"}
        result = check.validate(" ", context)
        assert result is not None
        assert "digit_check ( ) is less than minimum (0)" in result.message


class TestRangeCheckDataTypes:
    """Test range check with different data types"""

    def test_date_range_passes(self):
        """Test validation passes for date value in range"""
        check = RangeCheck(date(2024, 1, 1), date(2024, 1, 31))
        context = {"column_name": "created_at"}
        result = check.validate(date(2024, 1, 15), context)
        assert result is None

    def test_date_range_fails(self):
        """Test validation fails for date value out of range"""
        check = RangeCheck(date(2024, 1, 1), date(2024, 1, 31))
        context = {"column_name": "created_at"}
        result = check.validate(date(2024, 2, 1), context)
        assert result is not None
        assert (
            "created_at (2024-02-01 00:00:00) is greater than maximum (2024-01-31 00:00:00)"
            in result.message
        )

    def test_datetime_range_passes(self):
        """Test validation passes for datetime value in range"""
        check = RangeCheck(datetime(2024, 1, 1, 0, 0), datetime(2024, 1, 1, 23, 59))
        context = {"column_name": "timestamp"}
        result = check.validate(datetime(2024, 1, 1, 12, 0), context)
        assert result is None

    def test_datetime_range_fails(self):
        """Test validation fails for datetime value out of range"""
        check = RangeCheck(datetime(2024, 1, 1, 0, 0), datetime(2024, 1, 1, 12, 0))
        context = {"column_name": "timestamp"}
        val = datetime(2024, 1, 1, 15, 0)
        result = check.validate(val, context)
        assert result is not None
        assert (
            "timestamp (2024-01-01 15:00:00) is greater than maximum (2024-01-01 12:00:00)"
            in result.message
        )

    def test_string_range_passes(self):
        """Test validation passes for string value in range"""
        check = RangeCheck("apple", "cherry")
        context = {"column_name": "fruit"}
        result = check.validate("banana", context)
        assert result is None

    def test_string_range_fails(self):
        """Test validation fails for string value out of range"""
        check = RangeCheck("apple", "cherry")
        context = {"column_name": "fruit"}
        result = check.validate("date", context)
        assert result is not None
        assert "fruit (date) is greater than maximum (cherry)" in result.message

    def test_int_range_passes(self):
        """Test validation passes for integer value in range"""
        check = RangeCheck(1, 10)
        context = {"column_name": "count"}
        result = check.validate(5, context)
        assert result is None

    def test_int_range_fails(self):
        """Test validation fails for integer value out of range"""
        check = RangeCheck(1, 10)
        context = {"column_name": "count"}
        result = check.validate(15, context)
        assert result is not None
        assert "count (15) is greater than maximum (10)" in result.message

    def test_float_range_passes(self):
        """Test validation passes for float value in range"""
        check = RangeCheck(1.0, 5.5)
        context = {"column_name": "rating"}
        result = check.validate(3.2, context)
        assert result is None

    def test_float_range_fails(self):
        """Test validation fails for float value out of range"""
        check = RangeCheck(1.0, 5.5)
        context = {"column_name": "rating"}
        result = check.validate(0.5, context)
        assert result is not None
        assert "rating (0.5) is less than minimum (1.0)" in result.message

    def test_decimal_range_passes(self):
        """Test validation passes for decimal value in range"""
        check = RangeCheck(Decimal("10.00"), Decimal("20.00"))
        context = {"column_name": "price"}
        result = check.validate(Decimal("15.50"), context)
        assert result is None

    def test_decimal_range_fails(self):
        """Test validation fails for decimal value out of range"""
        check = RangeCheck(Decimal("10.00"), Decimal("20.00"))
        context = {"column_name": "price"}
        result = check.validate(Decimal("25.00"), context)
        assert result is not None
        assert "price (25.00) is greater than maximum (20.00)" in result.message


class TestRangeCheckTypeMismatch:
    """Test for type mismatches between values and range boundaries"""

    def test_decimal_range_with_string_value_fails(self):
        """Test validation error when comparing a string value against a numeric range"""
        check = RangeCheck(min_value=10, max_value=20)
        context = {"column_name": "age"}
        result = check.validate("25", context)
        assert result is not None
        assert "Cannot compare str with min_value Decimal" in result.message

    def test_datetime_range_with_decimal_value_fails(self):
        """Test validation error when comparing a numeric value against a datetime range"""
        check = RangeCheck(min_value=date(2024, 1, 1), max_value=date(2024, 12, 31))
        context = {"column_name": "created_at"}
        result = check.validate(500, context)
        assert result is not None
        assert "Cannot compare Decimal with min_value datetime" in result.message

    def test_string_range_with_datetime_value_fails(self):
        """Test validation error when comparing a datetime value against a string range"""
        check = RangeCheck(min_value="aaa", max_value="zzz")
        context = {"column_name": "code"}
        result = check.validate(datetime(2024, 1, 1), context)
        assert result is not None
        assert "Cannot compare datetime with min_value str" in result.message

    def test_decimal_range_with_datetime_value_fails(self):
        """Test validation error when comparing a datetime value against a numeric range"""
        check = RangeCheck(min_value=0, max_value=100)
        context = {"column_name": "score"}
        result = check.validate(datetime(2025, 1, 1), context)
        assert result is not None
        assert "Cannot compare datetime with min_value Decimal" in result.message

    def test_datetime_range_with_string_value_fails(self):
        """Test validation error when comparing a string value against a datetime range"""
        check = RangeCheck(min_value=date(2024, 1, 1), max_value=date(2024, 12, 31))
        context = {"column_name": "deadline"}
        result = check.validate("2024-06-01", context)
        assert result is not None
        assert "Cannot compare str with min_value datetime" in result.message

    def test_string_range_with_decimal_value_fails(self):
        """Test validation error when comparing a numeric value against a string range"""
        check = RangeCheck(min_value="A", max_value="Z")
        context = {"column_name": "category_code"}
        result = check.validate(10.5, context)
        assert result is not None
        assert "Cannot compare Decimal with min_value str" in result.message


class TestRangeCheckEdgeCases:
    """Test edge cases for RangeCheck"""

    def test_repr(self):
        """Test __repr__ output"""
        check = RangeCheck(5, 15)
        repr_str = repr(check)
        assert "RangeCheck" in repr_str
        assert "min=5" in repr_str
        assert "max=15" in repr_str
