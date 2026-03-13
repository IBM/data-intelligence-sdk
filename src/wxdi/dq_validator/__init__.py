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
IBM watsonx.data intelligence SDK

A Python SDK for performing data quality validations on streaming data records (arrays)
using predefined asset metadata and validation rules.
"""

from .metadata import DataType, ColumnMetadata, AssetMetadata
from .base import BaseCheck, ValidationError
from .result import ValidationResult
from .result_consolidator import ValidationResultConsolidated
from .rule import ValidationRule
from .validator import Validator
from .checks.length_check import LengthCheck
from .checks.valid_values_check import ValidValuesCheck
from .checks.comparison_check import ComparisonCheck, ComparisonOperator
from .checks.case_check import CaseCheck, ColumnCaseEnum
from .checks.completeness_check import CompletenessCheck
from .checks.range_check import RangeCheck
from .checks.regex_check import RegexCheck
from .checks.datatype_check import DataTypeCheck
from .checks.format_check import FormatCheck, FormatConstraintType
from .datetime_formats import DateTimeFormats
from .data_quality_dimension import DataQualityDimension

# Re-export auth module for backward compatibility
from wxdi.common.auth import AuthConfig, EnvironmentType, GovCloudAuthenticator, AuthProvider
from ..version import __version__

__all__ = [
    # Metadata
    "DataType",
    "ColumnMetadata",
    "AssetMetadata",
    # Base classes
    "BaseCheck",
    "ValidationError",
    # Core classes
    "ValidationResult",
    "ValidationResultConsolidated",
    "ValidationRule",
    "Validator",
    # Checks
    "LengthCheck",
    "ValidValuesCheck",
    "ComparisonCheck",
    "ComparisonOperator",
    "CaseCheck",
    "ColumnCaseEnum",
    "CompletenessCheck",
    "RangeCheck",
    "RegexCheck",
    "DataTypeCheck",
    "FormatCheck",
    "FormatConstraintType",
    # Authentication
    "AuthConfig",
    "EnvironmentType",
    "GovCloudAuthenticator",
    "AuthProvider",
    # DateTime Formats
    "DateTimeFormats",
    # Data Quality Dimensions
    "DataQualityDimension",
]

