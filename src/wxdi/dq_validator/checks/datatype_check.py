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

from typing import Dict, Any, Optional
from ..datatypes import DataType, DataTypeEnum
from ..inferred_engine import InferredTypeEngine
from ..base import BaseCheck, ValidationError
from ..data_quality_dimension import DataQualityDimension


class DataTypeCheck(BaseCheck):
    """Validates a value to be of the same data type as that of the expected type"""

    def __init__(self, expected_type: Optional[DataType] = None):
        """
        Initialize datatype check
        
        Args:
            expected_type: Data type expected of the input value to pass the check
        """
        super().__init__(DataQualityDimension.VALIDITY)
        
        self.expected_type = expected_type
        self.engine = InferredTypeEngine()

    def get_check_name(self) -> str:
        return "datatype_check"

    def validate(self, value: Any, context: Dict[str, Any]) -> Optional[ValidationError]:
        column_name = context.get("column_name", "unknown")

        if value is None or self.expected_type is None:
            return None

        inferred = self.engine.infer(value)
        
        # If type inference failed, skip validation
        if inferred is None:
            return None

        # If type inference failed, skip validation
        if inferred is None:
            return None

        if not self.expected_type.is_compatible(inferred):
            return ValidationError(
                column_name=column_name,
                check_name=self.get_check_name(),
                message=(
                    f"{column_name} value '{value}' inferred as {inferred} "
                    f"is not compatible with expected type {self.expected_type}"
                ),
                value=value,
                expected=str(self.expected_type)
            )

        return None

    def __repr__(self) -> str:
        return f"datatype_check(expected={self.expected_type})"