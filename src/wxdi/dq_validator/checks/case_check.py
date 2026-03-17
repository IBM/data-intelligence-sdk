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

"""
Case validation check - validates character case of string values.
"""

from enum import Enum
from typing import Any, Dict, Optional
from ..base import BaseCheck, ValidationError
from ..data_quality_dimension import DataQualityDimension


class ColumnCaseEnum(Enum):
    """Supported cases"""
    ANY_CASE = "AnyCase"
    UPPER_CASE = "UpperCase"
    LOWER_CASE = "LowerCase"
    NAME_CASE = "NameCase"
    SENTENCE_CASE = "SentenceCase"


class CaseCheck(BaseCheck):
    """Validates that a string value follows a specific case rule"""

    def __init__(self, case_type: ColumnCaseEnum = ColumnCaseEnum.ANY_CASE):
        """
        Initialize case check

        Args:
            case_type: Case type to enforce
        """
        super().__init__(DataQualityDimension.CONSISTENCY)
        
        if not isinstance(case_type, ColumnCaseEnum):
            raise ValueError(
                f"case_type must be a ColumnCaseEnum, not {type(case_type).__name__}. "
                f"Valid values are: {[c.value for c in ColumnCaseEnum]}"
            )
        
        self.case_type = case_type

    def get_check_name(self) -> str:
        return "case_check"

    def _is_word_delimiter(self, c: str) -> bool:
        return not c.isalpha()

    def _is_sentence_delimiter(self, c: str) -> bool:
        return c in ".!?"

    def _is_name_case(self, value_str: str) -> bool:
        state = 0  # 0 = start of word, 1 = inside word

        for c in value_str:
            if state == 0:
                if self._is_word_delimiter(c):
                    continue
                if c.islower():
                    return False
                state = 1
            else:
                if self._is_word_delimiter(c):
                    state = 0
                elif c.isupper():
                    return False
        return True

    def _is_sentence_case(self, value_str: str) -> bool:
        state = 0  # 0 = start of sentence, 1 = start of word, 2 = inside word

        for c in value_str:
            if state == 0:
                if self._is_sentence_delimiter(c) or c.isspace():
                    continue
                if self._is_word_delimiter(c):
                    state = 1
                elif c.islower():
                    return False
                else:
                    state = 2

            elif state == 1:
                if self._is_sentence_delimiter(c):
                    state = 0
                elif self._is_word_delimiter(c):
                    continue
                else:
                    state = 2

            else:  # state == 2
                if self._is_sentence_delimiter(c):
                    state = 0
                elif self._is_word_delimiter(c):
                    state = 1
                elif c.isupper():
                    return False

        return True
    
    # Case validation
    def _is_valid_case(self, value_str: str) -> bool:
        if self.case_type == ColumnCaseEnum.UPPER_CASE:
            return value_str == value_str.upper()

        if self.case_type == ColumnCaseEnum.LOWER_CASE:
            return value_str == value_str.lower()

        if self.case_type == ColumnCaseEnum.NAME_CASE:
            return self._is_name_case(value_str)

        if self.case_type == ColumnCaseEnum.SENTENCE_CASE:
            return self._is_sentence_case(value_str)

        return True  # AnyCase

    def validate(self, value: Any, context: Dict[str, Any]) -> Optional[ValidationError]:
        column_name = context.get("column_name", "unknown")

        # Check if value is None
        if value is None:
            return ValidationError(
                column_name=column_name,
                check_name=self.get_check_name(),
                message=f"{column_name} is None, cannot check the case",
                value=value
            )

        value_str = str(value)

        if not self._is_valid_case(value_str):
            return ValidationError(
                column_name=column_name,
                check_name=self.get_check_name(),
                message=f"{column_name} does not follow {self.case_type.value}",
                value=value,
                expected=self.case_type.value
            )

        return None

    def __repr__(self) -> str:
        return f"CaseCheck(case_type={self.case_type.value})"
