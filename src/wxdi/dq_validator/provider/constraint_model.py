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
Pydantic models for Data Quality Constraints
"""

from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel

from wxdi.dq_validator.base import BaseCheck
from wxdi.dq_validator.checks.case_check import CaseCheck, ColumnCaseEnum
from wxdi.dq_validator.checks.completeness_check import CompletenessCheck
from wxdi.dq_validator.checks.datatype_check import DataTypeCheck
from wxdi.dq_validator.checks.format_check import FormatCheck
from wxdi.dq_validator.checks.length_check import LengthCheck
from wxdi.dq_validator.checks.range_check import RangeCheck
from wxdi.dq_validator.checks.regex_check import RegexCheck
from wxdi.dq_validator.checks.valid_values_check import ValidValuesCheck
from wxdi.dq_validator.datatypes import DataType

try:
    from enum import StrEnum
except ImportError:
    # Remove when support for Python 3.10 is removed
    from enum import Enum
    class StrEnum(str, Enum):
        pass

class CheckType(StrEnum):
    """Enumeration of data quality check types"""

    UNIQUENESS = "uniqueness"
    COMPLETENESS = "completeness"
    COMPARISON = "comparison"
    DATA_CLASS = "data_class"
    DATA_TYPE = "data_type"
    FORMAT = "format"
    RANGE = "range"
    POSSIBLE_VALUES = "possible_values"
    REGEX = "regex"
    LENGTH = "length"
    RULE = "rule"
    CASE = "case"
    NONSTANDARD_MISSING_VALUES = "nonstandard_missing_values"
    SUSPECT_VALUES = "suspect_values"
    REFERENTIAL_INTEGRITY = "referential_integrity"
    HISTORY_STABILITY = "history_stability"


class CheckConstraint(BaseModel):
    """Data quality check constraint"""

    name: str
    value: Optional[str] = None
    numeric_value: Optional[int] = None
    boolean_value: Optional[bool] = None
    list_value: Optional[list] = None
    timestamp_value: Optional[datetime] = None
    date_value: Optional[datetime] = None
    time_value: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "CheckConstraint":
        """Create CheckConstraint instance from dictionary"""
        return cls(**data)

    def get_constraint_value(self) -> Any:
        """Get the actual constraint value from the appropriate field"""
        c_values = [
            x
            for x in [
                self.value,
                self.numeric_value,
                self.boolean_value,
                self.list_value,
                self.timestamp_value,
                self.date_value,
                self.time_value,
            ]
            if x is not None
        ]
        return c_values[0] if c_values else None


class CheckDefinition:
    """Definition of a data quality check with all possible parameters"""

    range_type: Optional[str] = None
    min: Optional[int] = None
    max: Optional[int] = None
    case_type: Optional[str] = None
    missing_values_allowed: Optional[bool] = None
    data_type: Optional[str] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    length: Optional[int] = None
    formats: Optional[List[str]] = None
    unique: Optional[bool] = None
    expression: Optional[str] = None
    values: Optional[List[str]] = None
    data_class: Optional[str] = None
    allowed_values: Optional[List[str]] = None
    parent_asset_id: Optional[str] = None
    parent_column_name: Optional[str] = None
    metric: Optional[List[str]] = None


class ConstraintMetadata(BaseModel):
    """Metadata for data quality constraints"""

    type: CheckType
    check_id: Optional[str] = None
    confirmed: Optional[bool] = None
    hidden: Optional[bool] = None
    dimension: Optional[str] = None
    created_at: Optional[str] = None
    description: Optional[str] = None
    modified_at: Optional[str] = None
    origin_type: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "ConstraintMetadata":
        """Create ConstraintMetadata instance from dictionary"""
        return cls(**data)


class DataQualityConstraint(BaseModel):
    """Data quality constraint model"""

    metadata: ConstraintMetadata
    origin: List[dict]
    check: List[CheckConstraint]

    @classmethod
    def from_dict(cls, data: Dict) -> "DataQualityConstraint":
        """Create DataQualityConstraint instance from dictionary"""
        return cls(
            metadata=ConstraintMetadata.from_dict(data["metadata"]),
            origin=data["origin"],
            check=[CheckConstraint.from_dict(c) for c in data["check"]],
        )

    def map_checks(self) -> CheckDefinition:
        """Map check constraints to a CheckDefinition object"""
        combined = CheckDefinition()
        for constraint in self.check:
            constraint_name = constraint.name
            constraint_value = constraint.get_constraint_value()
            setattr(combined, constraint_name, constraint_value)
        return combined

    def to_check(self) -> Optional[BaseCheck]:
        """
        Convert the constraint to a BaseCheck instance

        Returns:
            BaseCheck instance or None if the check type is not supported
        """
        name = self.metadata.type
        check_def = self.map_checks()

        if name == CheckType.COMPLETENESS:
            return CompletenessCheck(check_def.missing_values_allowed)
        if name == CheckType.DATA_TYPE:
            data_type = DataType(
                check_def.data_type,
                check_def.length,
                check_def.precision,
                check_def.scale,
            )
            return DataTypeCheck(data_type)
        if name == CheckType.FORMAT:
            return FormatCheck(
                formats=set(check_def.formats) if check_def.formats else None
            )
        if name == CheckType.RANGE:
            return RangeCheck(check_def.min, check_def.max)
        if name == CheckType.POSSIBLE_VALUES:
            if not check_def.values:
                raise ValueError("`values` not defined with valid values")
            return ValidValuesCheck(check_def.values)
        if name == CheckType.REGEX:
            if check_def.expression is None:
                raise ValueError("`expression` not defined for regex check")
            return RegexCheck(check_def.expression)
        if name == CheckType.LENGTH:
            return LengthCheck(check_def.min, check_def.max)
        if name == CheckType.CASE:
            # Convert string to ColumnCaseEnum
            try:
                case_enum = ColumnCaseEnum(check_def.case_type)
                return CaseCheck(case_enum)
            except (ValueError, AttributeError):
                return None

        return None


# Made with Bob
