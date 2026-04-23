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
Unit tests for DataType Check
"""

from wxdi.dq_validator.checks.datatype_check import DataTypeCheck
from wxdi.dq_validator.datatypes import DataType, DataTypeEnum
from wxdi.dq_validator.data_quality_dimension import DataQualityDimension


class TestDataTypeCheckInitialization:
    """Tests for the datatype_check class initialization"""

    def test_init_with_datatype(self):
        """Test initialization with a completely intitialized datatype object"""
        expected = DataType(DataTypeEnum.INT32)
        check = DataTypeCheck(expected)
        assert check.expected_type == expected

    def test_init_without_datatype(self):
        """Test initialization without a datatype object"""
        check = DataTypeCheck()
        assert check.expected_type == None

    def test_init_with_empty_datatype(self):
        """Test initialization with an empty datatype object"""
        expected = DataType()
        check = DataTypeCheck(expected)
        assert check.expected_type.dtype == DataTypeEnum.UNKNOWN

    def test_get_check_name(self):
        """Test get_check_name returns correct name"""
        check = DataTypeCheck(DataType(DataTypeEnum.STRING, length=10))
        assert check.get_check_name() == "datatype_check"
    
    def test_get_dimension(self):
        """Test get_dimension returns correct dimension"""
        check = DataTypeCheck(DataType(DataTypeEnum.STRING, length=10))
        assert check.get_dimension() == DataQualityDimension.VALIDITY
    
    def test_set_dimension(self):
        """Test set_dimension changes the dimension"""
        check = DataTypeCheck(DataType(DataTypeEnum.STRING, length=10))
        assert check.get_dimension() == DataQualityDimension.VALIDITY
        
        check.set_dimension(DataQualityDimension.CONSISTENCY)
        assert check.get_dimension() == DataQualityDimension.CONSISTENCY


class TestDataTypeCheckValidation:
    """Test validation results for empty and non-empty values"""

    def test_empty_datatype_with_value_passes(self):
        """UNKNOWN of empty datatype doesnt match integer"""
        expected = DataType()  
        check = DataTypeCheck(expected)
        result = check.validate(123, {"column_name": "age"})
        assert result is not None
        assert "not compatible" in result.message

    def test_matching_datatype_passes(self):
        """Value matches expected type"""
        expected = DataType(DataTypeEnum.INT32)
        check = DataTypeCheck(expected)
        result = check.validate(100, {"column_name": "count"})
        assert result is None

    def test_mismatching_datatype_fails(self):
        """Value inferred as STRING but expected INT"""
        expected = DataType(DataTypeEnum.INT32)
        check = DataTypeCheck(expected)
        result = check.validate("abc", {"column_name": "count"})
        assert result is not None
        assert "not compatible" in result.message

    def test_empty_datatype_with_none_passes(self):
        """None value allowed for an empty expected type"""
        expected = DataType()
        check = DataTypeCheck(expected)
        result = check.validate(None, {"column_name": "optional"})
        assert result is None

    def test_no_datatype_with_none_passes(self):
        """With no expected type any value is allowed"""
        check = DataTypeCheck(None)
        result = check.validate(None, {"column_name": "optional"})
        assert result is None

    def test_datatype_with_none_passes(self):
        """Null value allowed regardless of datatype"""
        expected = DataType(DataTypeEnum.DATE)
        check = DataTypeCheck(expected)
        result = check.validate(None, {"column_name": "created_at"})
        assert result is None


class TestIntegerCompatibility:
    """Test validation results for various values against expected Integer types"""

    def test_int8_pass(self):
        """Test int8 value passes"""
        check = DataTypeCheck(DataType(DataTypeEnum.INT8))
        result = check.validate(127, {"column_name": "age"})
        assert result is None

    def test_int8_fail_overflow(self):
        """Test int8 value fails due to overflow"""
        check = DataTypeCheck(DataType(DataTypeEnum.INT8))
        result = check.validate(200, {"column_name": "age"})
        assert result is not None
        assert "not compatible" in result.message

    def test_int16_accepts_int8(self):
        """Test expected int16 accepts int8"""
        check = DataTypeCheck(DataType(DataTypeEnum.INT16))
        result = check.validate(100, {"column_name": "score"})
        assert result is None

    def test_int32_accepts_int16(self):
        """Test expected int32 accepts int16"""
        check = DataTypeCheck(DataType(DataTypeEnum.INT32))
        result = check.validate(30000, {"column_name": "population"})
        assert result is None

    def test_int64_accepts_int32(self):
        """Test expected int64 accepts int32"""
        check = DataTypeCheck(DataType(DataTypeEnum.INT64))
        result = check.validate(2000000000, {"column_name": "id"})
        assert result is None

    def test_int32_fail_decimal(self):
        """Test int32 should reject decimal values"""
        check = DataTypeCheck(DataType(DataTypeEnum.INT32))
        result = check.validate(12.34, {"column_name": "price"})
        assert result is not None
        assert "not compatible" in result.message

    def test_int32_fail_non_numeric_string(self):
        """Test int32 should reject non-numeric strings"""
        check = DataTypeCheck(DataType(DataTypeEnum.INT32))
        result = check.validate("abc", {"column_name": "age"})
        assert result is not None
        assert "not compatible" in result.message
    
    def test_int_accepts_numeric_string(self):
        """Numeric string value is parsed to compatible numerical type"""
        check = DataTypeCheck(DataType(DataTypeEnum.INT32))
        result = check.validate("12345", {"column_name": "age"})
        assert result is None



class TestDecimalCompatibility:
    """Test validation results for various values against expected Decimal types"""

    def test_decimal_exact(self):
        """Test decimal value passes"""
        expected = DataType(DataTypeEnum.DECIMAL, precision=5, scale=2)
        check = DataTypeCheck(expected)
        result = check.validate("123.45", {"column_name": "price"})
        assert result is None

    def test_decimal_scale_too_large(self):
        """Test decimal rejects scale overflow"""
        expected = DataType(DataTypeEnum.DECIMAL, precision=5, scale=2)
        check = DataTypeCheck(expected)
        result = check.validate("12.345", {"column_name": "price"})
        assert result is not None

    def test_decimal_integer_allowed(self):
        """Test decimal accepts integer"""
        expected = DataType(DataTypeEnum.DECIMAL, precision=10, scale=2)
        check = DataTypeCheck(expected)
        result = check.validate(100, {"column_name": "amount"})
        assert result is None

    def test_decimal_precision_overflow(self):
        """Test decimal rejects precision overflow"""
        expected = DataType(DataTypeEnum.DECIMAL, precision=4, scale=2)
        check = DataTypeCheck(expected)
        result = check.validate("123.45", {"column_name": "amount"})
        assert result is not None

    def test_decimal_rejects_date(self):
        """Testcdecimal should reject date values"""
        expected = DataType(DataTypeEnum.DECIMAL, precision=10, scale=2)
        check = DataTypeCheck(expected)
        result = check.validate("2024-01-15", {"column_name": "price"})
        assert result is not None
        assert "not compatible" in result.message


class TestStringCompatibility:
    """Test validation results for various values against expected String types"""

    def test_string_within_length(self):
        check = DataTypeCheck(DataType(DataTypeEnum.STRING, length=10))
        assert check.validate("hello", {"column_name": "name"}) is None

    def test_string_exact_length(self):
        check = DataTypeCheck(DataType(DataTypeEnum.STRING, length=5))
        assert check.validate("hello", {"column_name": "name"}) is None

    def test_string_too_long(self):
        check = DataTypeCheck(DataType(DataTypeEnum.STRING, length=5))
        result = check.validate("toolong", {"column_name": "name"})
        assert result is not None
        assert "not compatible" in result.message

    def test_string_numeric_passes(self):
        """Input string value can be parsed to Numerical value"""
        check = DataTypeCheck(DataType(DataTypeEnum.INT64, length=10))
        result = check.validate("12345", {"column_name": "code"})
        assert result is None

    def test_string_rejects_date(self):
        """String constraint should accept appropriate date values"""
        check = DataTypeCheck(DataType(DataTypeEnum.STRING, length=10))
        result = check.validate("2024-01-15", {"column_name": "dob"})
        assert result is not None
        assert "not compatible" in result.message


class TestDateTimeCompatibility:
    """Test validation results for various values against expected DateTime types"""

    def test_date_string(self):
        """Test date value passes"""
        check = DataTypeCheck(DataType(DataTypeEnum.DATE))
        result = check.validate("2024-01-10", {"column_name": "dob"})
        assert result is None

    def test_invalid_date_string(self):
        """Test date value fails"""
        check = DataTypeCheck(DataType(DataTypeEnum.DATE))
        result = check.validate("hello", {"column_name": "dob"})
        assert result is not None
        assert "not compatible" in result.message

    def test_time_string(self):
        """Test time value passes"""
        check = DataTypeCheck(DataType(DataTypeEnum.TIME))
        result = check.validate("14:23:01", {"column_name": "login_time"})
        assert result is None

    def test_timestamp_string(self):
        """Test timestamp value passes"""
        check = DataTypeCheck(DataType(DataTypeEnum.TIMESTAMP))
        result = check.validate("2024-01-10 14:23:01", {"column_name": "created_at"})
        assert result is None

    def test_timestamp_against_date(self):
        """Test timestamp value fails against expected date"""
        check = DataTypeCheck(DataType(DataTypeEnum.DATE))
        result = check.validate("2024-01-01 10:11:12", {"column_name": "created"})
        assert result is not None


class TestDateFormats:
    """Test validation results for various date formats"""

    def test_date_dash_format(self):
        """YYYY-MM-DD format should be detected as DATE"""
        check = DataTypeCheck(DataType(DataTypeEnum.DATE))
        result = check.validate("2024-01-10", {"column_name": "dob"})
        assert result is None

    def test_date_slash_format(self):
        """MM/YYYY format should be detected as DATE"""
        check = DataTypeCheck(DataType(DataTypeEnum.DATE))
        result = check.validate("01/2024", {"column_name": "dob"})
        assert result is None

    def test_date_dot_format(self):
        """DD.MM.YYYY format should be detected as DATE"""
        check = DataTypeCheck(DataType(DataTypeEnum.DATE))
        result = check.validate("10.01.2024", {"column_name": "dob"})
        assert result is None

    def test_date_month_name(self):
        """Mon-DD-YY format should be detected as DATE"""
        check = DataTypeCheck(DataType(DataTypeEnum.DATE))
        result = check.validate("Jan-10-24", {"column_name": "dob"})
        assert result is None

    def test_date_textual(self):
        """Month DD, YYYY format should be detected as DATE"""
        check = DataTypeCheck(DataType(DataTypeEnum.DATE))
        result = check.validate("Jan 10, 2024", {"column_name": "dob"})
        assert result is None


class TestTimeFormats:
    """Test validation results for various time formats"""

    def test_time_24h_seconds(self):
        """24-hour HH:MM:SS format should be detected as TIME"""
        check = DataTypeCheck(DataType(DataTypeEnum.TIME))
        result = check.validate("14:23:01", {"column_name": "login_time"})
        assert result is None

    def test_time_24h_no_seconds(self):
        """24-hour HH:MM format should be detected as TIME"""
        check = DataTypeCheck(DataType(DataTypeEnum.TIME))
        result = check.validate("09:45", {"column_name": "login_time"})
        assert result is None

    def test_time_milliseconds(self):
        """Time with milliseconds should be detected as TIME"""
        check = DataTypeCheck(DataType(DataTypeEnum.TIME))
        result = check.validate("14:23:01.123", {"column_name": "login_time"})
        assert result is None

    def test_time_12h_with_am_pm(self):
        """12-hour time with AM/PM should be detected as TIME"""
        check = DataTypeCheck(DataType(DataTypeEnum.TIME))
        result = check.validate("02:23 PM", {"column_name": "login_time"})
        assert result is None

    def test_time_12h_with_seconds(self):
        """12-hour time with seconds and AM/PM should be detected as TIME"""
        check = DataTypeCheck(DataType(DataTypeEnum.TIME))
        result = check.validate("02:23:01PM", {"column_name": "login_time"})
        assert result is None

    def test_time_with_timezone(self):
        """Time with timezone offset should be detected as TIME"""
        check = DataTypeCheck(DataType(DataTypeEnum.TIME))
        result = check.validate("14:23:01+0530", {"column_name": "login_time"})
        assert result is None


class TestTimeStampFormats:
    """Test validation results for various timestamp formats"""

    def test_timestamp_standard(self):
        """Standard YYYY-MM-DD HH:MM:SS format should be detected as TIMESTAMP"""
        check = DataTypeCheck(DataType(DataTypeEnum.TIMESTAMP))
        result = check.validate("2024-01-10 14:23:01", {"column_name": "created_at"})
        assert result is None

    def test_timestamp_iso_t(self):
        """ISO T-separated timestamp should be detected as TIMESTAMP"""
        check = DataTypeCheck(DataType(DataTypeEnum.TIMESTAMP))
        result = check.validate("2024-01-10T14:23:01", {"column_name": "created_at"})
        assert result is None

    def test_timestamp_with_millis(self):
        """Timestamp with milliseconds should be detected as TIMESTAMP"""
        check = DataTypeCheck(DataType(DataTypeEnum.TIMESTAMP))
        result = check.validate("2024-01-10 14:23:01.456", {"column_name": "created_at"})
        assert result is None

    def test_timestamp_with_timezone(self):
        """Timestamp with timezone offset should be detected as TIMESTAMP"""
        check = DataTypeCheck(DataType(DataTypeEnum.TIMESTAMP))
        result = check.validate("2024-01-10 14:23:01+0530", {"column_name": "created_at"})
        assert result is None

    def test_timestamp_12h_clock(self):
        """12-hour timestamp with AM/PM should be detected as TIMESTAMP"""
        check = DataTypeCheck(DataType(DataTypeEnum.TIMESTAMP))
        result = check.validate("2024-01-10 02:23:01PM", {"column_name": "created_at"})
        assert result is None

    def test_timestamp_european(self):
        """European DD-MM-YYYY HH:MM timestamp should be detected as TIMESTAMP"""
        check = DataTypeCheck(DataType(DataTypeEnum.TIMESTAMP))
        result = check.validate("10-01-2024 14:23", {"column_name": "created_at"})
        assert result is None

    def test_timestamp_us_format(self):
        """US MM-DD-YYYY HH:MM:SS timestamp should be detected as TIMESTAMP"""
        check = DataTypeCheck(DataType(DataTypeEnum.TIMESTAMP))
        result = check.validate("01-10-2024 14:23:01", {"column_name": "created_at"})
        assert result is None


class TestCrossTypeFailures:
    """Test failure of values against cross-types"""

    def test_string_vs_int(self):
        """Test string fails against int32"""
        check = DataTypeCheck(DataType(DataTypeEnum.INT32))
        result = check.validate("abc", {"column_name": "age"})
        assert result is not None

    def test_date_vs_decimal(self):
        """Test date fails against decimal"""
        check = DataTypeCheck(DataType(DataTypeEnum.DECIMAL, precision=5, scale=2))
        result = check.validate("2024-01-01", {"column_name": "amount"})
        assert result is not None


class TestFormatAndTypeIntegration:
    """Test proper initialization of parameters in datatypes"""

    def test_inferred_format_is_set(self):
        """Test initialization of inferred_type and inferred_format"""
        check = DataTypeCheck(DataType(DataTypeEnum.DATE))
        engine = check.engine
        check.validate("2024-01-10", {"column_name": "dob"})
        assert engine.inferred_type.dtype == DataTypeEnum.DATE
        assert engine.inferred_format is not None

    def test_repr(self):
        """Test __repr__ method"""
        check = DataTypeCheck(DataType(DataTypeEnum.INT32))
        assert "datatype_check" in repr(check)
        assert "int32" in repr(check)