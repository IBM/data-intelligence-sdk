# Copyright 2026 IBM Corporation
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0);
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# See the LICENSE file in the project root for license information.

"""List of various Date Separators, Date formats, Time formats, Timestamp formats

Users can now reference formats using readable constant names from the DateTimeFormats class.
For example: DateTimeFormats.ISO_DATE instead of "%yyyy-%mm-%dd"

Usage:
    from dq_validator.datetime_formats import DateTimeFormats
    
    # Use constants directly
    format_pattern = DateTimeFormats.ISO_DATE
    
    # Access format dictionaries
    python_format = DateTimeFormats.DATE_FORMATS[DateTimeFormats.ISO_DATE]
"""


class DateTimeFormats:
    """
    Global constants for datetime format patterns.
    Similar to Java's public static final constants.
    
    All format constants and dictionaries are accessible as class attributes.
    """
    
    # Date Separators
    DATE_SEPARATORS = ["-", "/", "."]
    
    # ==================== DATE FORMAT CONSTANTS ====================
    # ISO and standard formats
    ISO_DATE = "%yyyy-%mm-%dd"                          # Example: 2026-02-09
    ISO_DATE_SHORT_MONTH = "%yyyy-%mmm-%dd"             # Example: 2026-Feb-09
    
    # European formats (DD.MM.YYYY)
    EUROPEAN_DATE_SHORT = "%dd.%mm.%yy"                 # Example: 09.02.26
    EUROPEAN_DATE = "%dd.%mm.%yyyy"                     # Example: 09.02.2026
    
    # US formats (MM-DD-YYYY)
    US_DATE_SHORT = "%mm-%dd-%yy"                       # Example: 02-09-26
    US_DATE = "%mm-%dd-%yyyy"                           # Example: 02-09-2026
    
    # UK/European formats (DD-MM-YYYY)
    UK_DATE_SHORT = "%dd-%mm-%yy"                       # Example: 09-02-26
    UK_DATE = "%dd-%mm-%yyyy"                           # Example: 09-02-2026
    
    # Alternative ISO formats
    ISO_DATE_REVERSE_DAY = "%yyyy-%dd-%mm"              # Example: 2026-09-02
    ISO_DATE_REVERSE_SHORT = "%yy-%mm-%dd"              # Example: 26-02-09
    ISO_DATE_REVERSE_DAY_SHORT = "%yy-%dd-%mm"          # Example: 26-09-02
    
    # Slash-separated formats
    UK_DATE_SLASH = "%dd/%mm/%yyyy"                     # Example: 09/02/2026
    UK_DATE_SLASH_SHORT = "%dd/%mm/%yy"                 # Example: 09/02/26
    US_DATE_SLASH = "%mm/%dd/%yyyy"                     # Example: 02/09/2026
    US_DATE_SLASH_SHORT = "%mm/%dd/%yy"                 # Example: 02/09/26
    
    # Month-year only formats
    MONTH_YEAR = "%mm/%yyyy"                            # Example: 02/2026
    MONTH_YEAR_SHORT = "%mm/%yy"                        # Example: 02/26
    
    # Text month formats
    ISO_DATE_TEXT_MONTH = "%yyyy-%mmm-%dd"              # Example: 2026-Feb-09
    ISO_DATE_TEXT_MONTH_SHORT = "%yy-%mmm-%dd"          # Example: 26-Feb-09
    UK_DATE_TEXT_MONTH = "%dd-%mmm-%yyyy"               # Example: 09-Feb-2026
    US_DATE_TEXT_MONTH = "%mm-%dd-%yyyy"                # Example: 02-09-2026
    UK_DATE_TEXT_MONTH_SHORT = "%dd-%mmm-%yy"           # Example: 09-Feb-26
    COMPACT_DATE_TEXT_MONTH = "%dd%mmm%yy"              # Example: 09Feb26
    TEXT_MONTH_DAY_SHORT = "%mmm-%dd-%yy"               # Example: Feb-09-26
    ISO_DATE_TEXT_MONTH_REVERSE = "%yyyy-%dd-%mmm"      # Example: 2026-09-Feb
    ISO_DATE_TEXT_MONTH_REVERSE_SHORT = "%yy-%dd-%mmm"  # Example: 26-09-Feb
    TEXT_MONTH_YEAR = "%mmm/%yyyy"                      # Example: Feb/2026
    TEXT_MONTH_YEAR_SHORT = "%mmm/%yy"                  # Example: Feb/26
    US_TEXT_MONTH_LONG = "%mmm %dd, %yyyy"              # Example: Feb 09, 2026
    US_TEXT_MONTH_LONG_PERIOD = "%mmm. %dd, %yyyy"      # Example: Feb. 09, 2026
    
    # ==================== TIME FORMAT CONSTANTS ====================
    # 24-hour formats
    TIME_24H = "%HH:%nn:%ss"                            # Example: 14:30:45
    TIME_24H_SHORT = "%HH:%nn"                          # Example: 14:30
    
    # 24-hour with fractional seconds
    TIME_24H_MICROSECONDS = "%HH:%nn:%ss.6"             # Example: 14:30:45.123456
    TIME_24H_MICROSECONDS_5 = "%HH:%nn:%ss.5"           # Example: 14:30:45.12345
    TIME_24H_MILLISECONDS = "%HH:%nn:%ss.4"             # Example: 14:30:45.1234
    TIME_24H_MILLISECONDS_3 = "%HH:%nn:%ss.3"           # Example: 14:30:45.123
    TIME_24H_CENTISECONDS = "%HH:%nn:%ss.2"             # Example: 14:30:45.12
    TIME_24H_DECISECONDS = "%HH:%nn:%ss.1"              # Example: 14:30:45.1
    
    # 12-hour formats with AM/PM
    TIME_12H_AMPM_SPACE = "%hh:%nn:%ss %a"              # Example: 02:30:45 PM
    TIME_12H_AMPM = "%hh:%nn:%ss%a"                     # Example: 02:30:45PM
    TIME_12H_SHORT_AMPM_SPACE = "%hh:%nn %a"            # Example: 02:30 PM
    TIME_12H_SHORT_AMPM = "%hh:%nn%a"                   # Example: 02:30PM
    TIME_12H_CENTISECONDS_AMPM = "%hh:%nn:%ss.2 %a"     # Example: 02:30:45.12 PM
    TIME_12H_DECISECONDS_AMPM = "%hh:%nn:%ss.1 %a"      # Example: 02:30:45.1 PM
    
    # Time with timezone
    TIME_24H_TIMEZONE_Z = "%HH:%nn:%ssZ"                # Example: 14:30:45+0530
    TIME_24H_TIMEZONE_Z_SPACE = "%HH:%nn:%ss Z"         # Example: 14:30:45 +0530
    TIME_24H_TIMEZONE_X = "%HH:%nn:%ssX"                # Example: 14:30:45+0530
    TIME_24H_TIMEZONE_X_SPACE = "%HH:%nn:%ss X"         # Example: 14:30:45 +0530
    
    # ==================== TIMESTAMP FORMAT CONSTANTS ====================
    # ISO 8601 formats with fractional seconds
    ISO_TIMESTAMP_MICROSECONDS = "%yyyy-%mm-%dd %HH:%nn:%ss.6"      # Example: 2026-02-09 14:30:45.123456
    ISO_TIMESTAMP_MICROSECONDS_5 = "%yyyy-%mm-%dd %HH:%nn:%ss.5"    # Example: 2026-02-09 14:30:45.12345
    ISO_TIMESTAMP_MILLISECONDS = "%yyyy-%mm-%dd %HH:%nn:%ss.4"      # Example: 2026-02-09 14:30:45.1234
    ISO_TIMESTAMP_MILLISECONDS_3 = "%yyyy-%mm-%dd %HH:%nn:%ss.3"    # Example: 2026-02-09 14:30:45.123
    ISO_TIMESTAMP_CENTISECONDS = "%yyyy-%mm-%dd %HH:%nn:%ss.2"      # Example: 2026-02-09 14:30:45.12
    ISO_TIMESTAMP_DECISECONDS = "%yyyy-%mm-%dd %HH:%nn:%ss.1"       # Example: 2026-02-09 14:30:45.1
    
    # Standard ISO 8601 formats
    ISO_TIMESTAMP = "%yyyy-%mm-%dd %HH:%nn:%ss"                     # Example: 2026-02-09 14:30:45
    ISO_TIMESTAMP_T = "%yyyy-%mm-%ddT%HH:%nn:%ss"                   # Example: 2026-02-09T14:30:45
    ISO_TIMESTAMP_T_SPACE = "%yyyy-%mm-%dd T %HH:%nn:%ss"           # Example: 2026-02-09 T 14:30:45
    
    # ISO 8601 with timezone
    ISO_TIMESTAMP_TIMEZONE_Z = "%yyyy-%mm-%dd %HH:%nn:%ssZ"         # Example: 2026-02-09 14:30:45+0530
    ISO_TIMESTAMP_T_TIMEZONE_Z = "%yyyy-%mm-%ddT%HH:%nn:%ssZ"       # Example: 2026-02-09T14:30:45+0530
    ISO_TIMESTAMP_TIMEZONE_Z_SPACE = "%yyyy-%mm-%dd %HH:%nn:%ss Z"  # Example: 2026-02-09 14:30:45 +0530
    ISO_TIMESTAMP_T_TIMEZONE_Z_SPACE = "%yyyy-%mm-%ddT%HH:%nn:%ss Z" # Example: 2026-02-09T14:30:45 +0530
    ISO_TIMESTAMP_TIMEZONE_X = "%yyyy-%mm-%dd %HH:%nn:%ssX"         # Example: 2026-02-09 14:30:45+0530
    ISO_TIMESTAMP_T_TIMEZONE_X = "%yyyy-%mm-%ddT%HH:%nn:%ssX"       # Example: 2026-02-09T14:30:45+0530
    ISO_TIMESTAMP_TIMEZONE_X_SPACE = "%yyyy-%mm-%dd %HH:%nn:%ss X"  # Example: 2026-02-09 14:30:45 +0530
    ISO_TIMESTAMP_T_TIMEZONE_X_SPACE = "%yyyy-%mm-%ddT%HH:%nn:%ss X" # Example: 2026-02-09T14:30:45 +0530
    
    # ISO 8601 with 12-hour time
    ISO_TIMESTAMP_12H_AMPM = "%yyyy-%mm-%dd %HH:%nn:%ss%a"          # Example: 2026-02-09 02:30:45PM
    ISO_TIMESTAMP_12H_AMPM_SPACE = "%yyyy-%mm-%dd %HH:%nn:%ss %a"   # Example: 2026-02-09 02:30:45 PM
    
    # European/UK formats (DD-MM-YYYY)
    UK_TIMESTAMP_SHORT = "%dd-%mm-%yyyy %HH:%nn"                    # Example: 09-02-2026 14:30
    US_TIMESTAMP_SHORT = "%mm-%dd-%yyyy %HH:%nn"                    # Example: 02-09-2026 14:30
    UK_TIMESTAMP_12H_AMPM = "%dd-%mm-%yyyy %HH:%nn%a"               # Example: 09-02-2026 02:30PM
    US_TIMESTAMP_12H_AMPM = "%mm-%dd-%yyyy %HH:%nn%a"               # Example: 02-09-2026 02:30PM
    UK_TIMESTAMP_12H_AMPM_SPACE = "%dd-%mm-%yyyy %HH:%nn %a"        # Example: 09-02-2026 02:30 PM
    US_TIMESTAMP_12H_AMPM_SPACE = "%mm-%dd-%yyyy %HH:%nn %a"        # Example: 02-09-2026 02:30 PM
    UK_TIMESTAMP = "%dd-%mm-%yyyy %HH:%nn:%ss"                      # Example: 09-02-2026 14:30:45
    US_TIMESTAMP = "%mm-%dd-%yyyy %HH:%nn:%ss"                      # Example: 02-09-2026 14:30:45
    UK_TIMESTAMP_12H_AMPM_FULL = "%dd-%mm-%yyyy %HH:%nn:%ss%a"      # Example: 09-02-2026 02:30:45PM
    US_TIMESTAMP_12H_AMPM_FULL = "%mm-%dd-%yyyy %HH:%nn:%ss%a"      # Example: 02-09-2026 02:30:45PM
    UK_TIMESTAMP_12H_AMPM_FULL_SPACE = "%dd-%mm-%yyyy %HH:%nn:%ss %a" # Example: 09-02-2026 02:30:45 PM
    US_TIMESTAMP_12H_AMPM_FULL_SPACE = "%mm-%dd-%yyyy %HH:%nn:%ss %a" # Example: 02-09-2026 02:30:45 PM
    
    # ==================== FORMAT DICTIONARIES ====================
    # Date Formats Dictionary - Maps format constants to Python datetime format strings
    DATE_FORMATS = {
        ISO_DATE: "%Y-%m-%d",
        ISO_DATE_SHORT_MONTH: "%Y-%b-%d",
        EUROPEAN_DATE_SHORT: "%d.%m.%y",
        EUROPEAN_DATE: "%d.%m.%Y",
        US_DATE_SHORT: "%m-%d-%y",
        US_DATE: "%m-%d-%Y",
        UK_DATE_SHORT: "%d-%m-%y",
        UK_DATE: "%d-%m-%Y",
        ISO_DATE_REVERSE_DAY: "%Y-%d-%m",
        ISO_DATE_REVERSE_SHORT: "%y-%m-%d",
        ISO_DATE_REVERSE_DAY_SHORT: "%y-%d-%m",
        UK_DATE_SLASH: "%d/%m/%Y",
        UK_DATE_SLASH_SHORT: "%d/%m/%y",
        US_DATE_SLASH: "%m/%d/%Y",
        US_DATE_SLASH_SHORT: "%m/%d/%y",
        MONTH_YEAR: "%m/%Y",
        MONTH_YEAR_SHORT: "%m/%y",
        ISO_DATE_TEXT_MONTH: "%Y-%b-%d",
        ISO_DATE_TEXT_MONTH_SHORT: "%y-%b-%d",
        UK_DATE_TEXT_MONTH: "%d-%b-%Y",
        US_DATE_TEXT_MONTH: "%m-%d-%Y",
        UK_DATE_TEXT_MONTH_SHORT: "%d-%b-%y",
        COMPACT_DATE_TEXT_MONTH: "%d%b%y",
        TEXT_MONTH_DAY_SHORT: "%b-%d-%y",
        ISO_DATE_TEXT_MONTH_REVERSE: "%Y-%d-%b",
        ISO_DATE_TEXT_MONTH_REVERSE_SHORT: "%y-%d-%b",
        TEXT_MONTH_YEAR: "%b/%Y",
        TEXT_MONTH_YEAR_SHORT: "%b/%y",
        US_TEXT_MONTH_LONG: "%b %d, %Y",
        US_TEXT_MONTH_LONG_PERIOD: "%b. %d, %Y",
    }
    
    # Time Formats Dictionary - Maps format constants to Python datetime format strings
    TIME_FORMATS = {
        TIME_24H: "%H:%M:%S",
        TIME_24H_SHORT: "%H:%M",
        TIME_24H_MICROSECONDS: "%H:%M:%S.%f",
        TIME_24H_MICROSECONDS_5: "%H:%M:%S.%f",
        TIME_24H_MILLISECONDS: "%H:%M:%S.%f",
        TIME_24H_MILLISECONDS_3: "%H:%M:%S.%f",
        TIME_24H_CENTISECONDS: "%H:%M:%S.%f",
        TIME_24H_DECISECONDS: "%H:%M:%S.%f",
        TIME_12H_AMPM_SPACE: "%I:%M:%S %p",
        TIME_12H_AMPM: "%I:%M:%S%p",
        TIME_12H_SHORT_AMPM_SPACE: "%I:%M %p",
        TIME_12H_SHORT_AMPM: "%I:%M%p",
        TIME_12H_CENTISECONDS_AMPM: "%I:%M:%S.%f %p",
        TIME_12H_DECISECONDS_AMPM: "%I:%M:%S.%f %p",
        TIME_24H_TIMEZONE_Z: "%H:%M:%S%z",
        TIME_24H_TIMEZONE_Z_SPACE: "%H:%M:%S %z",
        TIME_24H_TIMEZONE_X: "%H:%M:%S%z",
        TIME_24H_TIMEZONE_X_SPACE: "%H:%M:%S %z",
    }
    
    # Timestamp Formats Dictionary - Maps format constants to Python datetime format strings
    TIMESTAMP_FORMATS = {
        ISO_TIMESTAMP_MICROSECONDS: "%Y-%m-%d %H:%M:%S.%f",
        ISO_TIMESTAMP_MICROSECONDS_5: "%Y-%m-%d %H:%M:%S.%f",
        ISO_TIMESTAMP_MILLISECONDS: "%Y-%m-%d %H:%M:%S.%f",
        ISO_TIMESTAMP_MILLISECONDS_3: "%Y-%m-%d %H:%M:%S.%f",
        ISO_TIMESTAMP_CENTISECONDS: "%Y-%m-%d %H:%M:%S.%f",
        ISO_TIMESTAMP_DECISECONDS: "%Y-%m-%d %H:%M:%S.%f",
        ISO_TIMESTAMP: "%Y-%m-%d %H:%M:%S",
        ISO_TIMESTAMP_T: "%Y-%m-%dT%H:%M:%S",
        ISO_TIMESTAMP_T_SPACE: "%Y-%m-%d T %H:%M:%S",
        ISO_TIMESTAMP_TIMEZONE_Z: "%Y-%m-%d %H:%M:%S%z",
        ISO_TIMESTAMP_T_TIMEZONE_Z: "%Y-%m-%dT%H:%M:%S%z",
        ISO_TIMESTAMP_TIMEZONE_Z_SPACE: "%Y-%m-%d %H:%M:%S %z",
        ISO_TIMESTAMP_T_TIMEZONE_Z_SPACE: "%Y-%m-%dT%H:%M:%S %z",
        ISO_TIMESTAMP_TIMEZONE_X: "%Y-%m-%d %H:%M:%S%z",
        ISO_TIMESTAMP_T_TIMEZONE_X: "%Y-%m-%dT%H:%M:%S%z",
        ISO_TIMESTAMP_TIMEZONE_X_SPACE: "%Y-%m-%d %H:%M:%S %z",
        ISO_TIMESTAMP_T_TIMEZONE_X_SPACE: "%Y-%m-%dT%H:%M:%S %z",
        ISO_TIMESTAMP_12H_AMPM: "%Y-%m-%d %I:%M:%S%p",
        ISO_TIMESTAMP_12H_AMPM_SPACE: "%Y-%m-%d %I:%M:%S %p",
        UK_TIMESTAMP_SHORT: "%d-%m-%Y %H:%M",
        US_TIMESTAMP_SHORT: "%m-%d-%Y %H:%M",
        UK_TIMESTAMP_12H_AMPM: "%d-%m-%Y %I:%M%p",
        US_TIMESTAMP_12H_AMPM: "%m-%d-%Y %I:%M%p",
        UK_TIMESTAMP_12H_AMPM_SPACE: "%d-%m-%Y %I:%M %p",
        US_TIMESTAMP_12H_AMPM_SPACE: "%m-%d-%Y %I:%M %p",
        UK_TIMESTAMP: "%d-%m-%Y %H:%M:%S",
        US_TIMESTAMP: "%m-%d-%Y %H:%M:%S",
        UK_TIMESTAMP_12H_AMPM_FULL: "%d-%m-%Y %I:%M:%S%p",
        US_TIMESTAMP_12H_AMPM_FULL: "%m-%d-%Y %I:%M:%S%p",
        UK_TIMESTAMP_12H_AMPM_FULL_SPACE: "%d-%m-%Y %I:%M:%S %p",
        US_TIMESTAMP_12H_AMPM_FULL_SPACE: "%m-%d-%Y %I:%M:%S %p",
    }


# Backward compatibility: Export at module level for existing code
DATE_SEPARATORS = DateTimeFormats.DATE_SEPARATORS
DATE_FORMATS = DateTimeFormats.DATE_FORMATS
TIME_FORMATS = DateTimeFormats.TIME_FORMATS
TIMESTAMP_FORMATS = DateTimeFormats.TIMESTAMP_FORMATS
