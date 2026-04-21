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
WXDI - IBM watsonx.data intelligence SDK

A comprehensive Python SDK for data quality validation, data intelligence operations,
data product hub services, ODCS generation, and data product recommendations.
"""

# Re-export commonly used modules for convenience
from wxdi.dq_validator import (
    # Metadata
    DataType,
    ColumnMetadata,
    AssetMetadata,
    # Base classes
    BaseCheck,
    ValidationError,
    # Core classes
    ValidationResult,
    ValidationResultConsolidated,
    ValidationRule,
    Validator,
    # Checks
    LengthCheck,
    ValidValuesCheck,
    ComparisonCheck,
    ComparisonOperator,
    CaseCheck,
    ColumnCaseEnum,
    CompletenessCheck,
    RangeCheck,
    RegexCheck,
    DataTypeCheck,
    FormatCheck,
    FormatConstraintType,
    # DateTime Formats
    DateTimeFormats,
    # Data Quality Dimensions
    DataQualityDimension,
)

from wxdi.common.auth import (
    AuthConfig,
    EnvironmentType,
    GovCloudAuthenticator,
    AuthProvider,
)

from .version import __version__

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

# Note: dph_services, odcs_generator, and data_product_recommender are available as submodules
# Import them explicitly:
#   from wxdi.dph_services import DphV1
#   from wxdi.odcs_generator import CollibraClient, ODCSGenerator, InformaticaClient
#   from wxdi.data_product_recommender import DataProductRecommender

# Made with Bob
