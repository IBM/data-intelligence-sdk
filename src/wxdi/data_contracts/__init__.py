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
Data Contracts SDK package.

Provides the DataContractsProvider and all associated Pydantic models for
interacting with the Data Quality Data Contracts API.

Usage:
    >>> from wxdi.data_contracts import DataContractsProvider
    >>> from wxdi.data_contracts import DataContractPrototypeYaml
    >>> from wxdi.dq_validator.provider import ProviderConfig
    >>>
    >>> config = ProviderConfig(url="https://your-cpd-host", auth_token="Bearer <token>")
    >>> provider = DataContractsProvider(config)
    >>> collection = provider.list_project_data_contracts("my-project-id")
"""

from .provider import DataContractsProvider
from .models import (
    # Shared
    DataContractType,
    ConnectionInfo,
    ServerMapping,
    # Request bodies
    DataContractPrototypeYaml,
    DataContractPrototypeJson,
    DataContractPrototype,
    DataContractValidationRequest,
    DataContractTestRequest,
    # Data contract asset
    DataContract,
    DataContractCollection,
    # Validation
    DataContractValidationError,
    DataContractValidationResponse,
    # Test result — prototype sub-models
    DataContractTestResultJobRunPrototype,
    DataContractTestResultJobInfoPrototype,
    DataContractTestResultSchemaValidationSummaryPrototype,
    DataContractTestResultDataQualitySummaryPrototype,
    DataContractTestResultSummaryPrototype,
    DataContractTestResultPhysicalTypeCheckPrototype,
    DataContractTestResultColumnsSummaryPrototype,
    DataContractTestResultAssetSchemaValidationPrototype,
    DataContractTestResultColumnTypeCheckPrototype,
    DataContractTestResultRequiredCheckPrototype,
    DataContractTestResultPrimaryKeyCheckPrototype,
    DataContractTestResultUniqueCheckPrototype,
    DataContractTestResultColumnSchemaValidationPrototype,
    DataContractTestResultDqCheckResultsPrototype,
    DataContractTestResultDqRuleJobRunPrototype,
    DataContractTestResultDqRuleJobPrototype,
    DataContractTestResultDqRuleRefPrototype,
    DataContractTestResultDqCheckPrototype,
    DataContractTestResultColumnResultPrototype,
    DataContractTestResultDataAssetPrototype,
    # Test result — request body (top-level)
    DataContractTestResultPrototype,
    # Test result — top level
    DataContractTestResult,
    DataContractTestResultCollection,
    # Test result — sub-models
    DataContractTestResultJobRun,
    DataContractTestResultJobInfo,
    DataContractTestResultSchemaValidationSummary,
    DataContractTestResultDataQualitySummary,
    DataContractTestResultSummary,
    DataContractTestResultPhysicalTypeCheck,
    DataContractTestResultColumnsSummary,
    DataContractTestResultAssetSchemaValidation,
    DataContractTestResultColumnTypeCheck,
    DataContractTestResultRequiredCheck,
    DataContractTestResultPrimaryKeyCheck,
    DataContractTestResultUniqueCheck,
    DataContractTestResultColumnSchemaValidation,
    DataContractTestResultDqCheckResults,
    DataContractTestResultDqRuleJobRun,
    DataContractTestResultDqRuleJob,
    DataContractTestResultDqRuleRef,
    DataContractTestResultDqCheck,
    DataContractTestResultColumnResult,
    DataContractTestResultDataAsset,
)

__all__ = [
    "DataContractsProvider",
    # Shared
    "DataContractType",
    "ConnectionInfo",
    "ServerMapping",
    # Request bodies
    "DataContractPrototypeYaml",
    "DataContractPrototypeJson",
    "DataContractPrototype",
    "DataContractValidationRequest",
    "DataContractTestRequest",
    # Data contract asset
    "DataContract",
    "DataContractCollection",
    # Validation
    "DataContractValidationError",
    "DataContractValidationResponse",
    # Test result — prototype sub-models
    "DataContractTestResultJobRunPrototype",
    "DataContractTestResultJobInfoPrototype",
    "DataContractTestResultSchemaValidationSummaryPrototype",
    "DataContractTestResultDataQualitySummaryPrototype",
    "DataContractTestResultSummaryPrototype",
    "DataContractTestResultPhysicalTypeCheckPrototype",
    "DataContractTestResultColumnsSummaryPrototype",
    "DataContractTestResultAssetSchemaValidationPrototype",
    "DataContractTestResultColumnTypeCheckPrototype",
    "DataContractTestResultRequiredCheckPrototype",
    "DataContractTestResultPrimaryKeyCheckPrototype",
    "DataContractTestResultUniqueCheckPrototype",
    "DataContractTestResultColumnSchemaValidationPrototype",
    "DataContractTestResultDqCheckResultsPrototype",
    "DataContractTestResultDqRuleJobRunPrototype",
    "DataContractTestResultDqRuleJobPrototype",
    "DataContractTestResultDqRuleRefPrototype",
    "DataContractTestResultDqCheckPrototype",
    "DataContractTestResultColumnResultPrototype",
    "DataContractTestResultDataAssetPrototype",
    # Test result — request body (top-level)
    "DataContractTestResultPrototype",
    # Test result — top level
    "DataContractTestResult",
    "DataContractTestResultCollection",
    # Test result — sub-models
    "DataContractTestResultJobRun",
    "DataContractTestResultJobInfo",
    "DataContractTestResultSchemaValidationSummary",
    "DataContractTestResultDataQualitySummary",
    "DataContractTestResultSummary",
    "DataContractTestResultPhysicalTypeCheck",
    "DataContractTestResultColumnsSummary",
    "DataContractTestResultAssetSchemaValidation",
    "DataContractTestResultColumnTypeCheck",
    "DataContractTestResultRequiredCheck",
    "DataContractTestResultPrimaryKeyCheck",
    "DataContractTestResultUniqueCheck",
    "DataContractTestResultColumnSchemaValidation",
    "DataContractTestResultDqCheckResults",
    "DataContractTestResultDqRuleJobRun",
    "DataContractTestResultDqRuleJob",
    "DataContractTestResultDqRuleRef",
    "DataContractTestResultDqCheck",
    "DataContractTestResultColumnResult",
    "DataContractTestResultDataAsset",
]
