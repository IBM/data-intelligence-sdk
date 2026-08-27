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
    ConnectionInfo,
    ServerMapping,
    DataContractPrototypeYaml,
    DataContractPrototypeJson,
    DataContractPrototype,
    DataContractValidationRequest,
    DataContractTestRequest,
    DataContract,
    DataContractCollection,
    DataContractValidationError,
    DataContractValidationResponse,
    DataContractInfo,
    LogEntry,
    CheckResult,
    DataContractTestResponse,
    DataContractTestResponseCollection,
)

__all__ = [
    "DataContractsProvider",
    "ConnectionInfo",
    "ServerMapping",
    "DataContractPrototypeYaml",
    "DataContractPrototypeJson",
    "DataContractPrototype",
    "DataContractValidationRequest",
    "DataContractTestRequest",
    "DataContract",
    "DataContractCollection",
    "DataContractValidationError",
    "DataContractValidationResponse",
    "DataContractInfo",
    "LogEntry",
    "CheckResult",
    "DataContractTestResponse",
    "DataContractTestResponseCollection",
]

# Made with Bob
