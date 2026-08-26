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
Pydantic models for the Data Contracts API request and response payloads.

These models correspond to the schemas defined in the OpenAPI spec under
/data_quality/v4/projects/{project_id}/data_contracts and
/data_quality/v4/catalogs/{catalog_id}/data_contracts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, model_validator


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------

class ConnectionInfo(BaseModel):
    """Reference to a connection asset."""

    model_config = ConfigDict(extra="allow")

    id: str


class ServerMapping(BaseModel):
    """Maps a logical server name from the contract to a connection asset."""

    model_config = ConfigDict(extra="allow")

    server: str
    connection: Optional[ConnectionInfo] = None


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class DataContractPrototypeYaml(BaseModel):
    """Prototype for creating/replacing a data contract using YAML content."""

    model_config = ConfigDict(extra="allow")

    name: str
    contract_yaml: str
    server_mappings: Optional[List[ServerMapping]] = None


class DataContractPrototypeJson(BaseModel):
    """Prototype for creating/replacing a data contract using JSON content."""

    model_config = ConfigDict(extra="allow")

    name: str
    contract_json: Dict[str, Any]
    server_mappings: Optional[List[ServerMapping]] = None


# Union type accepted by create/replace methods.
# Pass either a DataContractPrototypeYaml or a DataContractPrototypeJson.
DataContractPrototype = Union[DataContractPrototypeYaml, DataContractPrototypeJson]


class DataContractValidationRequest(BaseModel):
    """Request body for validating a data contract against the ODCS schema."""

    model_config = ConfigDict(extra="allow")

    data_contract_content: str


class DataContractTestRequest(BaseModel):
    """Request body for triggering a data contract test run."""

    model_config = ConfigDict(extra="allow")

    server_mappings: Optional[List[ServerMapping]] = None
    retain_dq_objects: bool = True


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class DataContract(BaseModel):
    """A persisted data contract asset.

    Handles two response shapes:

    Flat (OpenAPI spec):
        ``{"id": "...", "name": "...", "contract_yaml": "...", "server_mappings": [...]}``

    Nested (actual API response):
        ``{"metadata": {"asset_id": "...", "name": "..."}, "entity": {"ibm_data_contract": {...}}, "href": "..."}``

    In the nested shape ``id`` and ``name`` are promoted from ``metadata`` so
    callers can always use ``contract.id`` and ``contract.name`` regardless of
    which shape the server returned.
    """

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    name: Optional[str] = None
    contract_yaml: Optional[str] = None
    contract_json: Optional[Dict[str, Any]] = None
    server_mappings: List[ServerMapping] = []

    @model_validator(mode="before")
    @classmethod
    def _promote_nested_fields(cls, values: Any) -> Any:
        """Normalise the nested CAMS asset response into flat fields."""
        if not isinstance(values, dict):
            return values
        metadata: Dict[str, Any] = values.get("metadata") or {}
        if metadata:
            # Promote id from asset_id if the top-level id is absent
            if not values.get("id"):
                values["id"] = metadata.get("asset_id")
            # Promote name if the top-level name is absent
            if not values.get("name"):
                values["name"] = metadata.get("name")
        return values


class DataContractCollection(BaseModel):
    """Response wrapper returned by list operations."""

    model_config = ConfigDict(extra="allow")

    data_contracts: List[DataContract] = []
    total_count: int = 0


class DataContractValidationError(BaseModel):
    """A single validation error from the ODCS schema check."""

    model_config = ConfigDict(extra="allow")

    property: Optional[str] = None
    message: str
    type: str


class DataContractValidationResponse(BaseModel):
    """Result of validating a data contract against the ODCS schema."""

    model_config = ConfigDict(extra="allow")

    valid: bool
    errors: List[DataContractValidationError] = []
    error_count: int = 0


class DataContractInfo(BaseModel):
    """Brief reference to a data contract embedded in test results."""

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    name: Optional[str] = None
    version: Optional[str] = None


class LogEntry(BaseModel):
    """A single log entry produced during a test run."""

    model_config = ConfigDict(extra="allow")

    level: Optional[str] = None
    message: Optional[str] = None
    timestamp: Optional[str] = None


class CheckResult(BaseModel):
    """Result for a single quality check executed during a test run."""

    model_config = ConfigDict(extra="allow")

    check_name: Optional[str] = None
    status: Optional[str] = None
    passed: Optional[bool] = None
    message: Optional[str] = None


class DataContractTestResponse(BaseModel):
    """Full result of a data contract test execution (one run)."""

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    project_id: Optional[str] = None
    status: Optional[str] = None
    run_by: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    contract: Optional[DataContractInfo] = None
    data_product: Optional[str] = None
    server_mappings: List[ServerMapping] = []
    logs: List[LogEntry] = []
    check_results: List[CheckResult] = []


class DataContractTestResponseCollection(BaseModel):
    """List of test run results for a data contract."""

    model_config = ConfigDict(extra="allow")

    test_results: List[DataContractTestResponse] = []


__all__ = [
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
