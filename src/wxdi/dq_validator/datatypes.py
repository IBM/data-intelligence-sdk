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

from decimal import Decimal, InvalidOperation
from datetime import datetime, date, time
import re
from typing import Optional
from enum import Enum
from .utils import get_or_default


class DataTypeEnum(str, Enum):
    INT8 = "INT8"
    INT16 = "INT16"
    INT32 = "INT32"
    INT64 = "INT64"
    DECIMAL = "DECIMAL"
    STRING = "STRING"
    DATE = "DATE"
    TIME = "TIME"
    TIMESTAMP = "TIMESTAMP"
    UNKNOWN = "UNKNOWN"


class DataType:
    _DEFAULT_DTYPE = DataTypeEnum.UNKNOWN
    _DEFAULT_LENGTH = 0
    _DEFAULT_PRECISION = 0
    _DEFAULT_SCALE = 0

    def __init__(
        self,
        dtype: Optional[str] = _DEFAULT_DTYPE,
        length: Optional[int] = _DEFAULT_LENGTH,
        precision: Optional[int] = _DEFAULT_PRECISION,
        scale: Optional[int] = _DEFAULT_SCALE,
    ):
        self.dtype = get_or_default(dtype, DataType._DEFAULT_DTYPE)
        self.length = get_or_default(length, DataType._DEFAULT_LENGTH)
        self.precision = get_or_default(precision, DataType._DEFAULT_PRECISION)
        self.scale = get_or_default(scale, DataType._DEFAULT_SCALE)

    def is_integer(self):
        return self.dtype in {
            DataTypeEnum.INT8,
            DataTypeEnum.INT16,
            DataTypeEnum.INT32,
            DataTypeEnum.INT64,
        }

    def is_compatible(self, inferred: "DataType") -> bool:
        """IBM DataType.isCompatibleWithValue"""

        if self.dtype == DataTypeEnum.DECIMAL:
            if inferred.dtype in {
                DataTypeEnum.DECIMAL,
                DataTypeEnum.INT8,
                DataTypeEnum.INT16,
                DataTypeEnum.INT32,
                DataTypeEnum.INT64,
            }:
                return (
                    inferred.scale <= self.scale
                    and inferred.precision - inferred.scale
                    <= self.precision - self.scale
                )
            return False

        if self.dtype == DataTypeEnum.INT8:
            return inferred.dtype == DataTypeEnum.INT8

        if self.dtype == DataTypeEnum.INT16:
            return inferred.dtype in (DataTypeEnum.INT8, DataTypeEnum.INT16)

        if self.dtype == DataTypeEnum.INT32:
            return inferred.dtype in (
                DataTypeEnum.INT8,
                DataTypeEnum.INT16,
                DataTypeEnum.INT32,
            )

        if self.dtype == DataTypeEnum.INT64:
            return inferred.dtype in (
                DataTypeEnum.INT8,
                DataTypeEnum.INT16,
                DataTypeEnum.INT32,
                DataTypeEnum.INT64,
            )

        if self.dtype == DataTypeEnum.STRING:
            return (
                inferred.dtype == DataTypeEnum.STRING and inferred.length <= self.length
            )

        return self == inferred

    def __eq__(self, other):
        if not isinstance(other, DataType):
            return False
        if self.dtype != other.dtype:
            return False
        if self.dtype == DataTypeEnum.STRING:
            return self.length == other.length
        if self.dtype == DataTypeEnum.DECIMAL:
            return (
                self.precision == other.precision
                and self.scale == other.scale
                and self.length == other.length
            )
        return True

    def __repr__(self):
        if self.dtype == DataTypeEnum.DECIMAL:
            return f"decimal({self.precision},{self.scale})"
        if self.dtype == DataTypeEnum.STRING:
            return f"varchar({self.length})"
        return self.dtype.lower()
