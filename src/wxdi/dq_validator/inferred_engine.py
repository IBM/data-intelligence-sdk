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

from .datatypes import DataType, DataTypeEnum
from decimal import Decimal, InvalidOperation
from datetime import datetime, date, time
from typing import Optional
from .datetime_formats import (
    DATE_FORMATS,
    TIME_FORMATS,
    TIMESTAMP_FORMATS,
    DATE_SEPARATORS,
)
from typing import Optional
import re


class InferredTypeEngine:

    US_NUMBER = re.compile(r"-?(\d{1,3}(,\d{3})*|\d+)(\.\d+)?$")
    DE_NUMBER = re.compile(r"-?(\d{1,3}(\.\d{3})*|\d+)(,\d+)?$")

    def __init__(self):
        self.inferred_type: Optional[DataType] = None
        self.inferred_format: Optional[str] = None

    def infer(
        self, value, allowed_formats: set[str] | None = None
    ) -> Optional[DataType]:

        self.inferred_type = None
        self.inferred_format = None

        if allowed_formats:
            date_formats = {
                k: v for k, v in DATE_FORMATS.items() if k in allowed_formats
            }
            time_formats = {
                k: v for k, v in TIME_FORMATS.items() if k in allowed_formats
            }
            timestamp_formats = {
                k: v for k, v in TIMESTAMP_FORMATS.items() if k in allowed_formats
            }
        else:
            date_formats = DATE_FORMATS
            time_formats = TIME_FORMATS
            timestamp_formats = TIMESTAMP_FORMATS

        if value is None:
            self.inferred_type = None

        elif isinstance(value, (int, float, Decimal)):
            self.inferred_type = self._infer_decimal(Decimal(str(value)))

        elif isinstance(value, str):
            s = value.strip()
            # Try numeric
            num = self._parse_number(s)

            if num is not None:
                self.inferred_type = self._infer_decimal(num)
            # Try datetime
            else:
                for fmt in self._expand_date_formats(date_formats.values()):
                    if self._try_parse(s, fmt):
                        self.inferred_type = DataType(DataTypeEnum.DATE, len(s))
                        self.inferred_format = fmt
                        break

                for fmt in time_formats.values():
                    if self._try_parse(s, fmt):
                        self.inferred_type = DataType(DataTypeEnum.TIME, len(s))
                        self.inferred_format = fmt
                        break

                for fmt in self._expand_timestamp_formats(timestamp_formats.values()):
                    if self._try_parse(s, fmt):
                        self.inferred_type = DataType(DataTypeEnum.TIMESTAMP, len(s))
                        self.inferred_format = fmt
                        break

                if self.inferred_type is None:
                    self.inferred_type = DataType(DataTypeEnum.STRING, length=len(s))

        # Date/time
        elif isinstance(value, datetime):
            self.inferred_type = DataType(
                DataTypeEnum.TIMESTAMP, length=len(str(value))
            )

        elif isinstance(value, date):
            self.inferred_type = DataType(DataTypeEnum.DATE, length=len(str(value)))

        elif isinstance(value, time):
            self.inferred_type = DataType(DataTypeEnum.TIME, length=len(str(value)))

        else:
            self.inferred_type = DataType(DataTypeEnum.STRING, length=len(str(value)))

        type_format_map: dict[str, dict[str, str]] = {
            DataTypeEnum.DATE: DATE_FORMATS,
            DataTypeEnum.TIME: TIME_FORMATS,
            DataTypeEnum.TIMESTAMP: TIMESTAMP_FORMATS,
        }
        lookup = (
            type_format_map.get(self.inferred_type.dtype, {})
            if self.inferred_type and self.inferred_type.dtype
            else {}
        )

        self.inferred_format = next(
            (k for k, v in lookup.items() if v == self.inferred_format), None
        )

        return self.inferred_type

    def _expand_date_formats(self, formats):
        expanded = []

        for fmt in formats:
            if "-" not in fmt:
                expanded.append(fmt)
            else:
                for sep in DATE_SEPARATORS:
                    expanded.append(fmt.replace("-", sep))

        return expanded

    def _expand_timestamp_formats(self, formats):
        expanded = []

        for fmt in formats:
            for sep in DATE_SEPARATORS:
                expanded.append(fmt.replace("-", sep))

        return expanded

    def _infer_decimal(self, d: Decimal):
        tuple_info = d.as_tuple()
        exponent = tuple_info.exponent

        # Handle special values (NaN, Infinity) - treat as DECIMAL with max precision
        if not isinstance(exponent, int):
            # For special values, use maximum precision to represent them
            return DataType(
                DataTypeEnum.DECIMAL, precision=38, scale=0, length=len(str(d))
            )

        if exponent > 0:
            d = d + Decimal(0)
            exponent = d.as_tuple().exponent
            if not isinstance(exponent, int):
                return DataType(
                    DataTypeEnum.DECIMAL, precision=38, scale=0, length=len(str(d))
                )

        if exponent < 0:
            d = d.normalize()
            exponent = d.as_tuple().exponent
            if not isinstance(exponent, int):
                return DataType(
                    DataTypeEnum.DECIMAL, precision=38, scale=0, length=len(str(d))
                )
            if exponent > 0:
                d = Decimal(int(d))
                exponent = d.as_tuple().exponent
                if not isinstance(exponent, int):
                    return DataType(
                        DataTypeEnum.DECIMAL, precision=38, scale=0, length=len(str(d))
                    )

        scale = -exponent if exponent < 0 else 0
        precision = len(d.as_tuple().digits)

        if scale > precision:
            precision = scale + 1

        # Integer detection
        is_integer = False
        try:
            if scale == 0:
                int(d)
                is_integer = True
        except Exception:
            pass

        if is_integer:
            n = int(d)
            if -128 <= n <= 127:
                dtype = DataTypeEnum.INT8
            elif -32768 <= n <= 32767:
                dtype = DataTypeEnum.INT16
            elif -2147483648 <= n <= 2147483647:
                dtype = DataTypeEnum.INT32
            else:
                dtype = DataTypeEnum.INT64
        else:
            dtype = DataTypeEnum.DECIMAL

        return DataType(dtype, precision=precision, scale=scale, length=len(str(d)))

    def _normalize_timezone(self, s: str) -> str:
        # Zulu = UTC
        if s.endswith("Z"):
            return s[:-1] + "+0000"
        return s

    def _parse_number(self, s):
        try:
            d = Decimal(s)
            tuple_info = d.as_tuple()
            exponent = tuple_info.exponent

            # Handle special values (NaN, Infinity) - still return the Decimal
            if not isinstance(exponent, int):
                return d

            precision = len(tuple_info.digits)
            scale = -exponent

            if precision < 255 and -254 < scale < 255:
                return d
        except InvalidOperation:
            pass

        if self.US_NUMBER.match(s):
            return Decimal(s.replace(",", ""))

        if self.DE_NUMBER.match(s):
            return Decimal(s.replace(".", "").replace(",", "."))

        return None

    def _try_parse(self, s, fmt):
        try:
            s_normal = self._normalize_timezone(s)
            datetime.strptime(s_normal, fmt)
            return True
        except ValueError:
            return False
