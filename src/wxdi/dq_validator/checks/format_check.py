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

from typing import Set, Dict, Any, Optional

from ..inferred_engine import InferredTypeEngine
from ..base import BaseCheck, ValidationError
from ..format_engine import FormatEngine
from ..utils import get_or_default
from ..data_quality_dimension import DataQualityDimension
from enum import Enum


class FormatConstraintType(Enum):
    ValidFormats = "ValidFormats"
    InvalidFormats = "InvalidFormats"


class FormatCheck(BaseCheck):
    """
    Validates if any value is of the format specified in the list of valid or invalid formats.
    """

    _DEFAULT_FORMAT_CONSTRAINT_TYPE = FormatConstraintType.ValidFormats

    def __init__(
        self,
        constraint_type: Optional[
            FormatConstraintType
        ] = _DEFAULT_FORMAT_CONSTRAINT_TYPE,
        formats: Set[str] | None = None,
    ):
        """
        Initialize format check

        Args:
            constraint_type: Defines whether the formats defined are to be Valid or Invalid
            formats: The formats for the value that are Valid or Invalid
        """
        super().__init__(DataQualityDimension.VALIDITY)

        self.constraint_type = get_or_default(
            constraint_type, FormatCheck._DEFAULT_FORMAT_CONSTRAINT_TYPE
        )
        self.formats = set(formats) if formats is not None else set()
        self.infer_engine = InferredTypeEngine()
        self.format_engine = FormatEngine()

    def get_check_name(self) -> str:
        return "format_check"

    def validate(
        self, value: Any, context: Dict[str, Any]
    ) -> Optional[ValidationError]:
        column_name = context.get("column_name", "unknown")

        detected_format = self.format_engine.get_format(str(value))
        self.infer_engine.infer(value, self.formats)

        if self.infer_engine.inferred_format is not None:
            detected_format = self.infer_engine.inferred_format

        # Determine validity based on constraint type
        if self.constraint_type == FormatConstraintType.ValidFormats:
            is_valid = detected_format in self.formats
        elif self.constraint_type == FormatConstraintType.InvalidFormats:
            is_valid = detected_format not in self.formats
        else:
            # Handle unexpected constraint type - default to invalid
            is_valid = False

        if not is_valid:
            return ValidationError(
                column_name=column_name,
                check_name=self.get_check_name(),
                message=(
                    f"{column_name} value '{value}' has format '{detected_format}' "
                    f"which violates {self.constraint_type.value} constraint {self.formats}"
                ),
                value=value,
                expected=str(self.formats),
            )

        return None

    def __repr__(self) -> str:
        return f"FormatCheck(type={self.constraint_type.value}, formats={self.formats})"
