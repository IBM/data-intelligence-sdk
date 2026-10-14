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

All model names and field names mirror the Java model classes in the
wkc-data-quality service (subprojects/api/src/main/java/.../api/models/v4/).
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, model_validator


class DataContractType(str, Enum):
    """Valid values for the type field on data contract models."""

    CONTRACT = "contract"
    CONTRACT_TEMPLATE = "contract_template"


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------


class ConnectionInfo(BaseModel):
    """Reference to a connection asset (mirrors ServerMapping.ConnectionID)."""

    model_config = ConfigDict(extra="allow")

    id: str


class ServerMapping(BaseModel):
    """Maps a logical server name from the contract to a connection asset.

    Mirrors ``ServerMapping`` in the Java service.
    """

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
    type: Optional[DataContractType] = None
    data_product_id: Optional[str] = None


class DataContractPrototypeJson(BaseModel):
    """Prototype for creating/replacing a data contract using JSON content."""

    model_config = ConfigDict(extra="allow")

    name: str
    contract_json: Dict[str, Any]
    server_mappings: Optional[List[ServerMapping]] = None
    type: Optional[DataContractType] = None
    data_product_id: Optional[str] = None


# Union type accepted by create/replace methods.
DataContractPrototype = Union[DataContractPrototypeYaml, DataContractPrototypeJson]


class DataContractValidationRequest(BaseModel):
    """Request body for validating a data contract against the ODCS schema."""

    model_config = ConfigDict(extra="allow")

    data_contract_content: str


class DataContractTestRequest(BaseModel):
    """Request body for triggering a data contract test run.

    Mirrors ``TestDataContractRequest`` in the Java service.
    """

    model_config = ConfigDict(extra="allow")

    server_mappings: Optional[List[ServerMapping]] = None
    retain_dq_objects: bool = True
    schema_validation: bool = True
    job_name: Optional[str] = None


# ---------------------------------------------------------------------------
# Response models — data contract asset
# ---------------------------------------------------------------------------


class DataContract(BaseModel):
    """A persisted data contract asset.

    Mirrors ``DataContract`` in the Java service.

    Handles two response shapes:

    Flat (OpenAPI spec):
        ``{"id": "...", "name": "...", "contract_yaml": "...", "server_mappings": [...]}``

    Nested (actual API response):
        ``{"metadata": {"asset_id": "...", "name": "..."}, "entity": {...}, "href": "..."}``

    In the nested shape ``id`` and ``name`` are promoted from ``metadata`` so
    callers can always use ``contract.id`` and ``contract.name`` regardless of
    which shape the server returned.
    """

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[DataContractType] = None
    data_product_id: Optional[str] = None
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
            if not values.get("id"):
                values["id"] = metadata.get("asset_id")
            if not values.get("name"):
                values["name"] = metadata.get("name")
        return values


class DataContractCollection(BaseModel):
    """Response wrapper returned by list operations."""

    model_config = ConfigDict(extra="allow")

    data_contracts: List[DataContract] = []
    total_count: int = 0


# ---------------------------------------------------------------------------
# Response models — validation
# ---------------------------------------------------------------------------


class DataContractValidationError(BaseModel):
    """A single validation error from the ODCS schema check.

    Mirrors ``DataContractValidationError`` in the Java service.
    """

    model_config = ConfigDict(extra="allow")

    property: Optional[str] = None
    message: str
    type: str


class DataContractValidationResponse(BaseModel):
    """Result of validating a data contract against the ODCS schema.

    Mirrors ``DataContractValidationResponse`` in the Java service.
    """

    model_config = ConfigDict(extra="allow")

    valid: bool
    errors: List[DataContractValidationError] = []
    error_count: int = 0


# ---------------------------------------------------------------------------
# Response models — test results (structured, from DataContractTestResult)
# ---------------------------------------------------------------------------


class DataContractTestResultJobRun(BaseModel):
    """Job-run reference nested inside a job info block.

    Mirrors ``DataContractTestResult.JobRun`` in the Java service.
    """

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    state: Optional[str] = None


class DataContractTestResultJobInfo(BaseModel):
    """Reference to the job that orchestrated the data contract test.

    Mirrors ``DataContractTestResult.JobInfo`` in the Java service.
    """

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    run: Optional[DataContractTestResultJobRun] = None


class DataContractTestResultSchemaValidationSummary(BaseModel):
    """Aggregated schema-validation counts for a test run.

    Mirrors ``DataContractTestResult.SchemaValidationSummary``.
    """

    model_config = ConfigDict(extra="allow")

    status: Optional[str] = None
    total_assets: Optional[int] = None
    passed_assets: Optional[int] = None
    failed_assets: Optional[int] = None
    missing_assets_count: Optional[int] = None
    total_columns: Optional[int] = None
    passed_columns: Optional[int] = None
    failed_columns: Optional[int] = None
    missing_columns_count: Optional[int] = None
    type_mismatch_count: Optional[int] = None
    unexpected_columns_count: Optional[int] = None


class DataContractTestResultDataQualitySummary(BaseModel):
    """Aggregated data-quality check counts for a test run.

    Mirrors ``DataContractTestResult.DataQualitySummary``.
    """

    model_config = ConfigDict(extra="allow")

    status: Optional[str] = None
    total_checks: Optional[int] = None
    passed_checks: Optional[int] = None
    failed_checks: Optional[int] = None
    error_checks: Optional[int] = None


class DataContractTestResultSummary(BaseModel):
    """Top-level aggregated summary of schema validation and data quality results.

    Mirrors ``DataContractTestResult.Summary``.
    """

    model_config = ConfigDict(extra="allow")

    status: Optional[str] = None
    schema_validation: Optional[DataContractTestResultSchemaValidationSummary] = None
    data_quality: Optional[DataContractTestResultDataQualitySummary] = None


class DataContractTestResultPhysicalTypeCheck(BaseModel):
    """Physical container type check result for a data asset.

    Mirrors ``DataContractTestResult.PhysicalTypeCheck``.
    """

    model_config = ConfigDict(extra="allow")

    expected: Optional[str] = None
    actual: Optional[str] = None
    status: Optional[str] = None


class DataContractTestResultColumnsSummary(BaseModel):
    """Column count summary within asset schema validation.

    Mirrors ``DataContractTestResult.ColumnsSummary``.
    """

    model_config = ConfigDict(extra="allow")

    expected_count: Optional[int] = None
    actual_count: Optional[int] = None
    matched_count: Optional[int] = None
    missing_count: Optional[int] = None
    unexpected_count: Optional[int] = None


class DataContractTestResultAssetSchemaValidation(BaseModel):
    """Schema validation result block for a single data asset.

    Mirrors ``DataContractTestResult.AssetSchemaValidation``.
    """

    model_config = ConfigDict(extra="allow")

    status: Optional[str] = None
    exists: Optional[bool] = None
    physical_type: Optional[DataContractTestResultPhysicalTypeCheck] = None
    columns_summary: Optional[DataContractTestResultColumnsSummary] = None
    missing_columns: List[str] = []
    unexpected_columns: List[str] = []


class DataContractTestResultColumnTypeCheck(BaseModel):
    """Data type check result for a single column.

    Mirrors ``DataContractTestResult.ColumnTypeCheck``.
    """

    model_config = ConfigDict(extra="allow")

    expected_logical_type: Optional[str] = None
    actual_logical_type: Optional[str] = None
    expected_physical_type: Optional[str] = None
    actual_physical_type: Optional[str] = None
    status: Optional[str] = None


class DataContractTestResultRequiredCheck(BaseModel):
    """Nullability constraint check result for a single column.

    Mirrors ``DataContractTestResult.RequiredCheck``.
    """

    model_config = ConfigDict(extra="allow")

    expected_required: Optional[bool] = None
    actual_nullable: Optional[bool] = None
    null_count: Optional[int] = None
    status: Optional[str] = None


class DataContractTestResultPrimaryKeyCheck(BaseModel):
    """Primary key constraint check result for a single column.

    Mirrors ``DataContractTestResult.PrimaryKeyCheck``.
    """

    model_config = ConfigDict(extra="allow")

    expected_primary_key: Optional[bool] = None
    actual_primary_key: Optional[bool] = None
    expected_position: Optional[int] = None
    actual_position: Optional[int] = None
    status: Optional[str] = None


class DataContractTestResultUniqueCheck(BaseModel):
    """Uniqueness constraint check result for a single column.

    Mirrors ``DataContractTestResult.UniqueCheck``.
    """

    model_config = ConfigDict(extra="allow")

    expected_unique: Optional[bool] = None
    duplicate_count: Optional[int] = None
    status: Optional[str] = None


class DataContractTestResultColumnSchemaValidation(BaseModel):
    """Schema validation result block for a single column.

    Mirrors ``DataContractTestResult.ColumnSchemaValidation``.
    """

    model_config = ConfigDict(extra="allow")

    status: Optional[str] = None
    exists: Optional[bool] = None
    type: Optional[DataContractTestResultColumnTypeCheck] = None
    required: Optional[DataContractTestResultRequiredCheck] = None
    primary_key: Optional[DataContractTestResultPrimaryKeyCheck] = None
    unique: Optional[DataContractTestResultUniqueCheck] = None


class DataContractTestResultDqCheckResults(BaseModel):
    """Execution counts for a single data quality check.

    Mirrors ``DctrDqCheckResults`` schema in openapi.yaml.
    """

    model_config = ConfigDict(extra="allow")

    tested_record_count: Optional[int] = None
    passed_record_count: Optional[int] = None
    failed_record_count: Optional[int] = None
    failure_percentage: Optional[float] = None
    status: Optional[str] = None


class DataContractTestResultDqRuleJobRun(BaseModel):
    """Job-run reference inside a DQ rule job reference.

    Mirrors ``DctrJobRun`` (rule-level) schema in openapi.yaml.
    """

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    state: Optional[str] = None


class DataContractTestResultDqRuleJob(BaseModel):
    """Job reference inside a data quality rule reference.

    Mirrors ``DctrDqRuleJob`` schema in openapi.yaml.
    """

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    run: Optional[DataContractTestResultDqRuleJobRun] = None


class DataContractTestResultDqRuleRef(BaseModel):
    """Reference to the backing data quality rule and its job/run.

    Mirrors ``DctrDqRuleRef`` schema in openapi.yaml.
    """

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    job: Optional[DataContractTestResultDqRuleJob] = None


class DataContractTestResultDqCheck(BaseModel):
    """A single data quality check definition and its execution results.

    Mirrors ``DataContractTestResult.DqCheck`` / ``DctrDqCheck`` in the service.
    """

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    dimension: Optional[str] = None
    metric: Optional[str] = None
    query: Optional[str] = None
    must_be: Optional[Any] = None
    must_not_be: Optional[Any] = None
    must_be_greater_than: Optional[Any] = None
    must_be_greater_or_equal_to: Optional[Any] = None
    must_be_less_than: Optional[Any] = None
    must_be_less_or_equal_to: Optional[Any] = None
    must_be_between: Optional[Any] = None
    must_not_be_between: Optional[Any] = None
    business_impact: Optional[str] = None
    severity: Optional[str] = None
    unit: Optional[str] = None
    results: Optional[DataContractTestResultDqCheckResults] = None
    data_quality_rule: Optional[DataContractTestResultDqRuleRef] = None


class DataContractTestResultColumnResult(BaseModel):
    """Schema validation and data quality check results for a single column.

    Mirrors ``DataContractTestResult.ColumnResult`` / ``DctrColumnResult``.
    """

    model_config = ConfigDict(extra="allow")

    name: Optional[str] = None
    physical_name: Optional[str] = None
    status: Optional[str] = None
    schema_validation: Optional[DataContractTestResultColumnSchemaValidation] = None
    data_quality_checks: List[DataContractTestResultDqCheck] = []


class DataContractTestResultDataAsset(BaseModel):
    """Per-asset validation and check results grouped inside a test result.

    Mirrors ``DataContractTestResult.DataAsset`` / ``DctrDataAsset``.
    """

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    name: Optional[str] = None
    physical_name: Optional[str] = None
    status: Optional[str] = None
    schema_validation: Optional[DataContractTestResultAssetSchemaValidation] = None
    columns: List[DataContractTestResultColumnResult] = []
    data_quality_checks: List[DataContractTestResultDqCheck] = []


class DataContractTestResult(BaseModel):
    """A persisted data contract test execution result.

    Mirrors ``DataContractTestResult`` in the Java service.  Returned by the
    GET/POST/PUT /test_results endpoints.
    """

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    href: Optional[str] = None
    server_mappings: List[ServerMapping] = []
    status: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    job: Optional[DataContractTestResultJobInfo] = None
    summary: Optional[DataContractTestResultSummary] = None
    data_assets: List[DataContractTestResultDataAsset] = []


class DataContractTestResultCollection(BaseModel):
    """Collection of data contract test results.

    Mirrors ``DataContractTestResultCollection`` in the Java service.
    """

    model_config = ConfigDict(extra="allow")

    test_results: List[DataContractTestResult] = []
    total_count: int = 0


# ---------------------------------------------------------------------------
# DataContractTestResultPrototype sub-models
#
# Parallel hierarchy to the DataContractTestResult sub-models. Each class
# below mirrors its DataContractTestResult* counterpart exactly in structure
# but carries a "Prototype" suffix so that request bodies and response bodies
# are distinct types and can evolve independently.
# ---------------------------------------------------------------------------


class DataContractTestResultJobRunPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultJobRun`."""

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    state: Optional[str] = None


class DataContractTestResultJobInfoPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultJobInfo`."""

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    run: Optional[DataContractTestResultJobRunPrototype] = None


class DataContractTestResultSchemaValidationSummaryPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultSchemaValidationSummary`."""

    model_config = ConfigDict(extra="allow")

    status: Optional[str] = None
    total_assets: Optional[int] = None
    passed_assets: Optional[int] = None
    failed_assets: Optional[int] = None
    missing_assets_count: Optional[int] = None
    total_columns: Optional[int] = None
    passed_columns: Optional[int] = None
    failed_columns: Optional[int] = None
    missing_columns_count: Optional[int] = None
    type_mismatch_count: Optional[int] = None
    unexpected_columns_count: Optional[int] = None


class DataContractTestResultDataQualitySummaryPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultDataQualitySummary`."""

    model_config = ConfigDict(extra="allow")

    status: Optional[str] = None
    total_checks: Optional[int] = None
    passed_checks: Optional[int] = None
    failed_checks: Optional[int] = None
    error_checks: Optional[int] = None


class DataContractTestResultSummaryPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultSummary`."""

    model_config = ConfigDict(extra="allow")

    status: Optional[str] = None
    schema_validation: Optional[
        DataContractTestResultSchemaValidationSummaryPrototype
    ] = None
    data_quality: Optional[DataContractTestResultDataQualitySummaryPrototype] = None


class DataContractTestResultPhysicalTypeCheckPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultPhysicalTypeCheck`."""

    model_config = ConfigDict(extra="allow")

    expected: Optional[str] = None
    actual: Optional[str] = None
    status: Optional[str] = None


class DataContractTestResultColumnsSummaryPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultColumnsSummary`."""

    model_config = ConfigDict(extra="allow")

    expected_count: Optional[int] = None
    actual_count: Optional[int] = None
    matched_count: Optional[int] = None
    missing_count: Optional[int] = None
    unexpected_count: Optional[int] = None


class DataContractTestResultAssetSchemaValidationPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultAssetSchemaValidation`."""

    model_config = ConfigDict(extra="allow")

    status: Optional[str] = None
    exists: Optional[bool] = None
    physical_type: Optional[DataContractTestResultPhysicalTypeCheckPrototype] = None
    columns_summary: Optional[DataContractTestResultColumnsSummaryPrototype] = None
    missing_columns: List[str] = []
    unexpected_columns: List[str] = []


class DataContractTestResultColumnTypeCheckPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultColumnTypeCheck`."""

    model_config = ConfigDict(extra="allow")

    expected_logical_type: Optional[str] = None
    actual_logical_type: Optional[str] = None
    expected_physical_type: Optional[str] = None
    actual_physical_type: Optional[str] = None
    status: Optional[str] = None


class DataContractTestResultRequiredCheckPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultRequiredCheck`."""

    model_config = ConfigDict(extra="allow")

    expected_required: Optional[bool] = None
    actual_nullable: Optional[bool] = None
    null_count: Optional[int] = None
    status: Optional[str] = None


class DataContractTestResultPrimaryKeyCheckPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultPrimaryKeyCheck`."""

    model_config = ConfigDict(extra="allow")

    expected_primary_key: Optional[bool] = None
    actual_primary_key: Optional[bool] = None
    expected_position: Optional[int] = None
    actual_position: Optional[int] = None
    status: Optional[str] = None


class DataContractTestResultUniqueCheckPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultUniqueCheck`."""

    model_config = ConfigDict(extra="allow")

    expected_unique: Optional[bool] = None
    duplicate_count: Optional[int] = None
    status: Optional[str] = None


class DataContractTestResultColumnSchemaValidationPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultColumnSchemaValidation`."""

    model_config = ConfigDict(extra="allow")

    status: Optional[str] = None
    exists: Optional[bool] = None
    type: Optional[DataContractTestResultColumnTypeCheckPrototype] = None
    required: Optional[DataContractTestResultRequiredCheckPrototype] = None
    primary_key: Optional[DataContractTestResultPrimaryKeyCheckPrototype] = None
    unique: Optional[DataContractTestResultUniqueCheckPrototype] = None


class DataContractTestResultDqCheckResultsPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultDqCheckResults`."""

    model_config = ConfigDict(extra="allow")

    tested_record_count: Optional[int] = None
    passed_record_count: Optional[int] = None
    failed_record_count: Optional[int] = None
    failure_percentage: Optional[float] = None
    status: Optional[str] = None


class DataContractTestResultDqRuleJobRunPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultDqRuleJobRun`."""

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    state: Optional[str] = None


class DataContractTestResultDqRuleJobPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultDqRuleJob`."""

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    run: Optional[DataContractTestResultDqRuleJobRunPrototype] = None


class DataContractTestResultDqRuleRefPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultDqRuleRef`."""

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    job: Optional[DataContractTestResultDqRuleJobPrototype] = None


class DataContractTestResultDqCheckPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultDqCheck`."""

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    dimension: Optional[str] = None
    metric: Optional[str] = None
    query: Optional[str] = None
    must_be: Optional[Any] = None
    must_not_be: Optional[Any] = None
    must_be_greater_than: Optional[Any] = None
    must_be_greater_or_equal_to: Optional[Any] = None
    must_be_less_than: Optional[Any] = None
    must_be_less_or_equal_to: Optional[Any] = None
    must_be_between: Optional[Any] = None
    must_not_be_between: Optional[Any] = None
    business_impact: Optional[str] = None
    severity: Optional[str] = None
    unit: Optional[str] = None
    results: Optional[DataContractTestResultDqCheckResultsPrototype] = None
    data_quality_rule: Optional[DataContractTestResultDqRuleRefPrototype] = None


class DataContractTestResultColumnResultPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultColumnResult`."""

    model_config = ConfigDict(extra="allow")

    name: Optional[str] = None
    physical_name: Optional[str] = None
    status: Optional[str] = None
    schema_validation: Optional[
        DataContractTestResultColumnSchemaValidationPrototype
    ] = None
    data_quality_checks: List[DataContractTestResultDqCheckPrototype] = []


class DataContractTestResultDataAssetPrototype(BaseModel):
    """Prototype variant of :class:`DataContractTestResultDataAsset`."""

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    name: Optional[str] = None
    physical_name: Optional[str] = None
    status: Optional[str] = None
    schema_validation: Optional[
        DataContractTestResultAssetSchemaValidationPrototype
    ] = None
    columns: List[DataContractTestResultColumnResultPrototype] = []
    data_quality_checks: List[DataContractTestResultDqCheckPrototype] = []


# ---------------------------------------------------------------------------
# DataContractTestResultPrototype — request body for POST/PUT /test_results
# ---------------------------------------------------------------------------


class DataContractTestResultPrototype(BaseModel):
    """Request body for creating or updating a data contract test result.

    Mirrors ``DataContractTestResultPrototype`` in the Java service.

    Contains the same fields as :class:`DataContractTestResult` excluding the
    server-generated ``id`` and ``href``.

    All nested sub-models use their own ``*Prototype`` variants so that request
    and response types are distinct and can evolve independently.

    Note:
        Unlike the response models, the list fields (``server_mappings`` and
        ``data_assets``) default to ``None`` rather than ``[]`` so that unset
        fields are omitted from the request body. Check for ``None`` before
        iterating over them.
    """

    model_config = ConfigDict(extra="allow")

    server_mappings: Optional[List[ServerMapping]] = None
    status: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    job: Optional[DataContractTestResultJobInfoPrototype] = None
    summary: Optional[DataContractTestResultSummaryPrototype] = None
    data_assets: Optional[List[DataContractTestResultDataAssetPrototype]] = None


__all__ = [
    "DataContractType",
    # Shared
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
    # Prototype sub-models (parallel hierarchy for request bodies)
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
    # Prototype top-level (request body for create/update test results)
    "DataContractTestResultPrototype",
]
