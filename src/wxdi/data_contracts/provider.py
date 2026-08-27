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
Provider for the Data Contracts API.

Covers all project-scoped and catalog-scoped endpoints under
/data_quality/v4/projects/{project_id}/data_contracts and
/data_quality/v4/catalogs/{catalog_id}/data_contracts.
"""

from __future__ import annotations

import json
from typing import IO, Optional

from wxdi.dq_validator.provider.base_provider import BaseProvider
from wxdi.dq_validator.provider.config import ProviderConfig
from wxdi.dq_validator.utils import get_request_headers
from .models import (
    DataContract,
    DataContractCollection,
    DataContractPrototype,
    DataContractPrototypeJson,
    DataContractPrototypeYaml,
    DataContractTestResponse,
    DataContractTestResponseCollection,
    DataContractValidationRequest,
    DataContractValidationResponse,
    DataContractTestRequest,
)


class DataContractsProvider(BaseProvider):
    """Provider for managing data contracts via the Data Quality API.

    Supports all project-scoped and catalog-scoped data contract operations
    including CRUD, validation, file upload, and test execution.

    Args:
        config (ProviderConfig): Configuration containing the base URL and
            authentication token.

    Example:
        >>> from wxdi.data_contracts import DataContractsProvider
        >>> from wxdi.dq_validator.provider import ProviderConfig
        >>> config = ProviderConfig(
        ...     url="https://your-cpd-host",
        ...     auth_token="Bearer <token>",
        ... )
        >>> provider = DataContractsProvider(config)
        >>> collection = provider.list_project_data_contracts("my-project-id")
        >>> print(collection.total_count)
    """

    _ERR_PROJECT_ID = "project_id must be provided"
    _ERR_CATALOG_ID = "catalog_id must be provided"
    _ERR_CONTRACT_ID = "data_contract_id must be provided"
    _ERR_TEST_RUN_ID = "test_run_id must be provided"

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _serialize_prototype(
        self, body: DataContractPrototype
    ) -> str:
        """Serialize a DataContractPrototype to a JSON string for the request body."""
        return body.model_dump_json(exclude_none=True)

    # ==================================================================
    # PROJECT-SCOPED ENDPOINTS
    # ==================================================================

    # ------------------------------------------------------------------
    # POST /data_quality/v4/projects/{project_id}/data_contracts_validation
    # ------------------------------------------------------------------

    def validate_project_data_contract(
        self,
        project_id: str,
        body: DataContractValidationRequest,
    ) -> DataContractValidationResponse:
        """Validate a data contract against the ODCS schema (project-scoped).

        HTTP 200 means the validation process completed — inspect
        ``response.valid`` to determine whether the contract is actually valid.

        Args:
            project_id: The project that owns the contract.
            body: The validation request containing the raw contract content.

        Returns:
            DataContractValidationResponse with ``valid``, ``errors``, and
            ``error_count`` fields.

        Raises:
            ValueError: If the server returns a non-2xx response.
        """
        if not project_id:
            raise ValueError(self._ERR_PROJECT_ID)

        url = (
            f"{self.config.url}/data_quality/v4/projects/{project_id}"
            "/data_contracts_validation"
        )
        headers = get_request_headers(self.config.auth_token, content_type="text/plain")
        response = self.session.post(
            url,
            headers=headers,
            data=body.data_contract_content,
            verify=False,
        )
        if not response.ok:
            raise ValueError(
                f"Failed to validate data contract in project {project_id}: "
                f"{response.status_code} {response.text}"
            )
        return DataContractValidationResponse(**response.json())

    # ------------------------------------------------------------------
    # GET /data_quality/v4/projects/{project_id}/data_contracts
    # ------------------------------------------------------------------

    def list_project_data_contracts(
        self,
        project_id: str,
        *,
        limit: int = 20,
    ) -> DataContractCollection:
        """List all data contracts in a project.

        Args:
            project_id: The project identifier.
            limit: Maximum number of results to return (1-200, default 20).

        Returns:
            DataContractCollection containing a list of data contracts and
            the total count.

        Raises:
            ValueError: If the server returns a non-2xx response.
        """
        if not project_id:
            raise ValueError(self._ERR_PROJECT_ID)

        url = f"{self.config.url}/data_quality/v4/projects/{project_id}/data_contracts"
        headers = get_request_headers(self.config.auth_token)
        response = self.session.get(
            url,
            headers=headers,
            params={"limit": limit},
            verify=False,
        )
        if not response.ok:
            raise ValueError(
                f"Failed to list data contracts in project {project_id}: "
                f"{response.status_code} {response.text}"
            )
        raw = response.json()
        if isinstance(raw, list):
            return DataContractCollection(data_contracts=raw, total_count=len(raw))
        return DataContractCollection(**raw)

    # ------------------------------------------------------------------
    # POST /data_quality/v4/projects/{project_id}/data_contracts
    # ------------------------------------------------------------------

    def create_project_data_contract(
        self,
        project_id: str,
        body: DataContractPrototype,
        *,
        validate: bool = True,
    ) -> DataContract:
        """Create a new data contract in a project.

        Args:
            project_id: The project identifier.
            body: Either a ``DataContractPrototypeYaml`` or a
                ``DataContractPrototypeJson`` instance.
            validate: When ``False``, skips ODCS schema validation before
                creating the contract. Defaults to ``True``.

        Returns:
            The created DataContract.

        Raises:
            ValueError: If the server returns a non-2xx response.
        """
        if not project_id:
            raise ValueError(self._ERR_PROJECT_ID)

        url = f"{self.config.url}/data_quality/v4/projects/{project_id}/data_contracts"
        headers = get_request_headers(self.config.auth_token)
        response = self.session.post(
            url,
            headers=headers,
            params={"validate": str(validate).lower()},
            data=self._serialize_prototype(body),
            verify=False,
        )
        if not response.ok:
            raise ValueError(
                f"Failed to create data contract in project {project_id}: "
                f"{response.status_code} {response.text}"
            )
        return DataContract(**response.json())

    # ------------------------------------------------------------------
    # DELETE /data_quality/v4/projects/{project_id}/data_contracts
    # ------------------------------------------------------------------

    def delete_project_data_contracts(
        self,
        project_id: str,
        *,
        data_contract_ids: str,
    ) -> None:
        """Delete one or more data contracts from a project.

        Args:
            project_id: The project identifier.
            data_contract_ids: Comma-separated list of contract IDs to delete.

        Raises:
            ValueError: If ``data_contract_ids`` is empty or the server returns
                a non-2xx response.
        """
        if not project_id:
            raise ValueError(self._ERR_PROJECT_ID)
        if not data_contract_ids:
            raise ValueError("data_contract_ids must be provided")

        url = f"{self.config.url}/data_quality/v4/projects/{project_id}/data_contracts"
        headers = get_request_headers(self.config.auth_token)
        response = self.session.delete(
            url,
            headers=headers,
            params={"data_contract_ids": data_contract_ids},
            verify=False,
        )
        if not response.ok:
            raise ValueError(
                f"Failed to delete data contracts in project {project_id}: "
                f"{response.status_code} {response.text}"
            )

    # ------------------------------------------------------------------
    # GET /data_quality/v4/projects/{project_id}/data_contracts/{id}
    # ------------------------------------------------------------------

    def get_project_data_contract(
        self,
        project_id: str,
        data_contract_id: str,
    ) -> DataContract:
        """Retrieve a specific data contract from a project.

        Args:
            project_id: The project identifier.
            data_contract_id: The data contract identifier.

        Returns:
            The requested DataContract.

        Raises:
            ValueError: If the contract is not found or the server returns a
                non-2xx response.
        """
        if not project_id:
            raise ValueError(self._ERR_PROJECT_ID)
        if not data_contract_id:
            raise ValueError(self._ERR_CONTRACT_ID)

        url = (
            f"{self.config.url}/data_quality/v4/projects/{project_id}"
            f"/data_contracts/{data_contract_id}"
        )
        headers = get_request_headers(self.config.auth_token)
        response = self.session.get(url, headers=headers, verify=False)
        if not response.ok:
            raise ValueError(
                f"Failed to get data contract {data_contract_id} in project "
                f"{project_id}: {response.status_code} {response.text}"
            )
        return DataContract(**response.json())

    # ------------------------------------------------------------------
    # PUT /data_quality/v4/projects/{project_id}/data_contracts/{id}
    # ------------------------------------------------------------------

    def replace_project_data_contract(
        self,
        project_id: str,
        data_contract_id: str,
        body: DataContractPrototype,
        *,
        validate: bool = True,
    ) -> DataContract:
        """Replace (full update) a data contract in a project.

        Args:
            project_id: The project identifier.
            data_contract_id: The data contract identifier.
            body: Either a ``DataContractPrototypeYaml`` or a
                ``DataContractPrototypeJson`` instance.
            validate: When ``False``, skips ODCS schema validation. Defaults
                to ``True``.

        Returns:
            The updated DataContract.

        Raises:
            ValueError: If the server returns a non-2xx response.
        """
        if not project_id:
            raise ValueError(self._ERR_PROJECT_ID)
        if not data_contract_id:
            raise ValueError(self._ERR_CONTRACT_ID)

        url = (
            f"{self.config.url}/data_quality/v4/projects/{project_id}"
            f"/data_contracts/{data_contract_id}"
        )
        headers = get_request_headers(self.config.auth_token)
        response = self.session.put(
            url,
            headers=headers,
            params={"validate": str(validate).lower()},
            data=self._serialize_prototype(body),
            verify=False,
        )
        if not response.ok:
            raise ValueError(
                f"Failed to replace data contract {data_contract_id} in project "
                f"{project_id}: {response.status_code} {response.text}"
            )
        return DataContract(**response.json())

    # ------------------------------------------------------------------
    # POST /data_quality/v4/projects/{project_id}/data_contracts_upload
    # ------------------------------------------------------------------

    def upload_project_data_contract_file(
        self,
        project_id: str,
        file: IO[bytes] | bytes,
        name: str,
        *,
        server_mappings: Optional[str] = None,
        data_contract_id: Optional[str] = None,
        validate: bool = True,
    ) -> DataContract:
        """Upload a YAML or JSON file to create or update a data contract in a project.

        Args:
            project_id: The project identifier.
            file: A file-like object (opened in binary mode) or raw bytes.
            name: A name for the data contract.
            server_mappings: Optional JSON string of server mappings, e.g.
                ``'[{"server":"my-server","connection":{"id":"conn-123"}}]'``.
            data_contract_id: If provided, the existing contract is updated
                instead of creating a new one.
            validate: When ``False``, skips ODCS schema validation. Defaults
                to ``True``.

        Returns:
            The created or updated DataContract.

        Raises:
            ValueError: If the server returns a non-2xx response.
        """
        if not project_id:
            raise ValueError(self._ERR_PROJECT_ID)

        url = (
            f"{self.config.url}/data_quality/v4/projects/{project_id}"
            "/data_contracts_upload"
        )
        # For multipart uploads we must NOT set Content-Type manually —
        # requests will set the correct multipart boundary automatically.
        headers = {"Authorization": self.config.auth_token} if self.config.auth_token else {}

        form_data: dict = {"name": name, "validate": str(validate).lower()}
        if server_mappings is not None:
            form_data["server_mappings"] = server_mappings
        if data_contract_id is not None:
            form_data["data_contract_id"] = data_contract_id

        files = {"file": file}
        response = self.session.post(
            url,
            headers=headers,
            data=form_data,
            files=files,
            verify=False,
        )
        if not response.ok:
            raise ValueError(
                f"Failed to upload data contract file to project {project_id}: "
                f"{response.status_code} {response.text}"
            )
        return DataContract(**response.json())

    # ------------------------------------------------------------------
    # POST /data_quality/v4/projects/{project_id}/data_contracts/{id}/test
    # ------------------------------------------------------------------

    def test_project_data_contract(
        self,
        project_id: str,
        data_contract_id: str,
        body: Optional[DataContractTestRequest] = None,
    ) -> DataContractTestResponse:
        """Trigger a test run for a data contract (internal endpoint).

        Args:
            project_id: The project identifier.
            data_contract_id: The data contract identifier.
            body: Optional test configuration with server mappings and options.
                Defaults to ``DataContractTestRequest()`` if not provided.

        Returns:
            DataContractTestResponse describing the initiated test run.

        Raises:
            ValueError: If the server returns a non-2xx response.
        """
        if not project_id:
            raise ValueError(self._ERR_PROJECT_ID)
        if not data_contract_id:
            raise ValueError(self._ERR_CONTRACT_ID)

        if body is None:
            body = DataContractTestRequest()

        url = (
            f"{self.config.url}/data_quality/v4/projects/{project_id}"
            f"/data_contracts/{data_contract_id}/test"
        )
        headers = get_request_headers(self.config.auth_token)
        response = self.session.post(
            url,
            headers=headers,
            data=body.model_dump_json(exclude_none=True),
            verify=False,
        )
        if not response.ok:
            raise ValueError(
                f"Failed to trigger test for data contract {data_contract_id} "
                f"in project {project_id}: {response.status_code} {response.text}"
            )
        return DataContractTestResponse(**response.json())

    # ------------------------------------------------------------------
    # GET /data_quality/v4/projects/{project_id}/data_contracts/{id}/test_results
    # ------------------------------------------------------------------

    def list_project_data_contract_test_results(
        self,
        project_id: str,
        data_contract_id: str,
        *,
        include_all_details: bool = False,
    ) -> DataContractTestResponseCollection:
        """List all test run results for a data contract (internal endpoint).

        Args:
            project_id: The project identifier.
            data_contract_id: The data contract identifier.
            include_all_details: When ``True``, each result includes full logs,
                server mappings, and check results. Defaults to ``False``.

        Returns:
            DataContractTestResponseCollection.

        Raises:
            ValueError: If no test runs exist (404) or another non-2xx
                response is returned.
        """
        if not project_id:
            raise ValueError(self._ERR_PROJECT_ID)
        if not data_contract_id:
            raise ValueError(self._ERR_CONTRACT_ID)

        url = (
            f"{self.config.url}/data_quality/v4/projects/{project_id}"
            f"/data_contracts/{data_contract_id}/test_results"
        )
        headers = get_request_headers(self.config.auth_token)
        response = self.session.get(
            url,
            headers=headers,
            params={"include_all_details": str(include_all_details).lower()},
            verify=False,
        )
        if not response.ok:
            raise ValueError(
                f"Failed to list test results for data contract {data_contract_id} "
                f"in project {project_id}: {response.status_code} {response.text}"
            )
        return DataContractTestResponseCollection(**response.json())

    # ------------------------------------------------------------------
    # DELETE /data_quality/v4/projects/{project_id}/data_contracts/{id}/test_results
    # ------------------------------------------------------------------

    def delete_project_data_contract_test_results(
        self,
        project_id: str,
        data_contract_id: str,
    ) -> None:
        """Delete all test results for a data contract (internal endpoint).

        Args:
            project_id: The project identifier.
            data_contract_id: The data contract identifier.

        Raises:
            ValueError: If the server returns a non-2xx response.
        """
        if not project_id:
            raise ValueError(self._ERR_PROJECT_ID)
        if not data_contract_id:
            raise ValueError(self._ERR_CONTRACT_ID)

        url = (
            f"{self.config.url}/data_quality/v4/projects/{project_id}"
            f"/data_contracts/{data_contract_id}/test_results"
        )
        headers = get_request_headers(self.config.auth_token)
        response = self.session.delete(url, headers=headers, verify=False)
        if not response.ok:
            raise ValueError(
                f"Failed to delete test results for data contract {data_contract_id} "
                f"in project {project_id}: {response.status_code} {response.text}"
            )

    # ------------------------------------------------------------------
    # GET /data_quality/v4/projects/{project_id}/data_contracts/{id}/test_results/{run_id}
    # ------------------------------------------------------------------

    def get_project_data_contract_test_result(
        self,
        project_id: str,
        data_contract_id: str,
        test_run_id: str,
        *,
        include_all_details: bool = False,
    ) -> DataContractTestResponse:
        """Retrieve a specific test run result (internal endpoint).

        Args:
            project_id: The project identifier.
            data_contract_id: The data contract identifier.
            test_run_id: The test run identifier.
            include_all_details: When ``True``, includes full logs, server
                mappings, and check results. Defaults to ``False``.

        Returns:
            DataContractTestResponse for the specified test run.

        Raises:
            ValueError: If the test run is not found or the server returns a
                non-2xx response.
        """
        if not project_id:
            raise ValueError(self._ERR_PROJECT_ID)
        if not data_contract_id:
            raise ValueError(self._ERR_CONTRACT_ID)
        if not test_run_id:
            raise ValueError(self._ERR_TEST_RUN_ID)

        url = (
            f"{self.config.url}/data_quality/v4/projects/{project_id}"
            f"/data_contracts/{data_contract_id}/test_results/{test_run_id}"
        )
        headers = get_request_headers(self.config.auth_token)
        response = self.session.get(
            url,
            headers=headers,
            params={"include_all_details": str(include_all_details).lower()},
            verify=False,
        )
        if not response.ok:
            raise ValueError(
                f"Failed to get test result {test_run_id} for data contract "
                f"{data_contract_id} in project {project_id}: "
                f"{response.status_code} {response.text}"
            )
        return DataContractTestResponse(**response.json())

    # ==================================================================
    # CATALOG-SCOPED ENDPOINTS
    # ==================================================================

    # ------------------------------------------------------------------
    # POST /data_quality/v4/catalogs/{catalog_id}/data_contracts_validation
    # ------------------------------------------------------------------

    def validate_catalog_data_contract(
        self,
        catalog_id: str,
        body: DataContractValidationRequest,
    ) -> DataContractValidationResponse:
        """Validate a data contract against the ODCS schema (catalog-scoped).

        Args:
            catalog_id: The catalog identifier.
            body: The validation request containing the raw contract content.

        Returns:
            DataContractValidationResponse.

        Raises:
            ValueError: If the server returns a non-2xx response.
        """
        if not catalog_id:
            raise ValueError(self._ERR_CATALOG_ID)

        url = (
            f"{self.config.url}/data_quality/v4/catalogs/{catalog_id}"
            "/data_contracts_validation"
        )
        headers = get_request_headers(self.config.auth_token, content_type="text/plain")
        response = self.session.post(
            url,
            headers=headers,
            data=body.data_contract_content,
            verify=False,
        )
        if not response.ok:
            raise ValueError(
                f"Failed to validate data contract in catalog {catalog_id}: "
                f"{response.status_code} {response.text}"
            )
        return DataContractValidationResponse(**response.json())

    # ------------------------------------------------------------------
    # GET /data_quality/v4/catalogs/{catalog_id}/data_contracts
    # ------------------------------------------------------------------

    def list_catalog_data_contracts(
        self,
        catalog_id: str,
        *,
        limit: int = 20,
    ) -> DataContractCollection:
        """List all data contracts in a catalog.

        Args:
            catalog_id: The catalog identifier.
            limit: Maximum number of results to return (1-200, default 20).

        Returns:
            DataContractCollection.

        Raises:
            ValueError: If the server returns a non-2xx response.
        """
        if not catalog_id:
            raise ValueError(self._ERR_CATALOG_ID)

        url = f"{self.config.url}/data_quality/v4/catalogs/{catalog_id}/data_contracts"
        headers = get_request_headers(self.config.auth_token)
        response = self.session.get(
            url,
            headers=headers,
            params={"limit": limit},
            verify=False,
        )
        if not response.ok:
            raise ValueError(
                f"Failed to list data contracts in catalog {catalog_id}: "
                f"{response.status_code} {response.text}"
            )
        raw = response.json()
        if isinstance(raw, list):
            return DataContractCollection(data_contracts=raw, total_count=len(raw))
        return DataContractCollection(**raw)

    # ------------------------------------------------------------------
    # POST /data_quality/v4/catalogs/{catalog_id}/data_contracts
    # ------------------------------------------------------------------

    def create_catalog_data_contract(
        self,
        catalog_id: str,
        body: DataContractPrototype,
        *,
        validate: bool = True,
    ) -> DataContract:
        """Create a new data contract in a catalog.

        Args:
            catalog_id: The catalog identifier.
            body: Either a ``DataContractPrototypeYaml`` or a
                ``DataContractPrototypeJson`` instance.
            validate: When ``False``, skips ODCS schema validation. Defaults
                to ``True``.

        Returns:
            The created DataContract.

        Raises:
            ValueError: If the server returns a non-2xx response.
        """
        if not catalog_id:
            raise ValueError(self._ERR_CATALOG_ID)

        url = f"{self.config.url}/data_quality/v4/catalogs/{catalog_id}/data_contracts"
        headers = get_request_headers(self.config.auth_token)
        response = self.session.post(
            url,
            headers=headers,
            params={"validate": str(validate).lower()},
            data=self._serialize_prototype(body),
            verify=False,
        )
        if not response.ok:
            raise ValueError(
                f"Failed to create data contract in catalog {catalog_id}: "
                f"{response.status_code} {response.text}"
            )
        return DataContract(**response.json())

    # ------------------------------------------------------------------
    # DELETE /data_quality/v4/catalogs/{catalog_id}/data_contracts
    # ------------------------------------------------------------------

    def delete_catalog_data_contracts(
        self,
        catalog_id: str,
        *,
        data_contract_ids: str,
    ) -> None:
        """Delete one or more data contracts from a catalog.

        Args:
            catalog_id: The catalog identifier.
            data_contract_ids: Comma-separated list of contract IDs to delete.

        Raises:
            ValueError: If ``data_contract_ids`` is empty or the server returns
                a non-2xx response.
        """
        if not catalog_id:
            raise ValueError(self._ERR_CATALOG_ID)
        if not data_contract_ids:
            raise ValueError("data_contract_ids must be provided")

        url = f"{self.config.url}/data_quality/v4/catalogs/{catalog_id}/data_contracts"
        headers = get_request_headers(self.config.auth_token)
        response = self.session.delete(
            url,
            headers=headers,
            params={"data_contract_ids": data_contract_ids},
            verify=False,
        )
        if not response.ok:
            raise ValueError(
                f"Failed to delete data contracts in catalog {catalog_id}: "
                f"{response.status_code} {response.text}"
            )

    # ------------------------------------------------------------------
    # GET /data_quality/v4/catalogs/{catalog_id}/data_contracts/{id}
    # ------------------------------------------------------------------

    def get_catalog_data_contract(
        self,
        catalog_id: str,
        data_contract_id: str,
    ) -> DataContract:
        """Retrieve a specific data contract from a catalog.

        Args:
            catalog_id: The catalog identifier.
            data_contract_id: The data contract identifier.

        Returns:
            The requested DataContract.

        Raises:
            ValueError: If the contract is not found or the server returns a
                non-2xx response.
        """
        if not catalog_id:
            raise ValueError(self._ERR_CATALOG_ID)
        if not data_contract_id:
            raise ValueError(self._ERR_CONTRACT_ID)

        url = (
            f"{self.config.url}/data_quality/v4/catalogs/{catalog_id}"
            f"/data_contracts/{data_contract_id}"
        )
        headers = get_request_headers(self.config.auth_token)
        response = self.session.get(url, headers=headers, verify=False)
        if not response.ok:
            raise ValueError(
                f"Failed to get data contract {data_contract_id} in catalog "
                f"{catalog_id}: {response.status_code} {response.text}"
            )
        return DataContract(**response.json())

    # ------------------------------------------------------------------
    # PUT /data_quality/v4/catalogs/{catalog_id}/data_contracts/{id}
    # ------------------------------------------------------------------

    def replace_catalog_data_contract(
        self,
        catalog_id: str,
        data_contract_id: str,
        body: DataContractPrototype,
        *,
        validate: bool = True,
    ) -> DataContract:
        """Replace (full update) a data contract in a catalog.

        Args:
            catalog_id: The catalog identifier.
            data_contract_id: The data contract identifier.
            body: Either a ``DataContractPrototypeYaml`` or a
                ``DataContractPrototypeJson`` instance.
            validate: When ``False``, skips ODCS schema validation. Defaults
                to ``True``.

        Returns:
            The updated DataContract.

        Raises:
            ValueError: If the server returns a non-2xx response.
        """
        if not catalog_id:
            raise ValueError(self._ERR_CATALOG_ID)
        if not data_contract_id:
            raise ValueError(self._ERR_CONTRACT_ID)

        url = (
            f"{self.config.url}/data_quality/v4/catalogs/{catalog_id}"
            f"/data_contracts/{data_contract_id}"
        )
        headers = get_request_headers(self.config.auth_token)
        response = self.session.put(
            url,
            headers=headers,
            params={"validate": str(validate).lower()},
            data=self._serialize_prototype(body),
            verify=False,
        )
        if not response.ok:
            raise ValueError(
                f"Failed to replace data contract {data_contract_id} in catalog "
                f"{catalog_id}: {response.status_code} {response.text}"
            )
        return DataContract(**response.json())

    # ------------------------------------------------------------------
    # POST /data_quality/v4/catalogs/{catalog_id}/data_contracts_upload
    # ------------------------------------------------------------------

    def upload_catalog_data_contract_file(
        self,
        catalog_id: str,
        file: IO[bytes] | bytes,
        name: str,
        *,
        server_mappings: Optional[str] = None,
        data_contract_id: Optional[str] = None,
        validate: bool = True,
    ) -> DataContract:
        """Upload a YAML or JSON file to create or update a data contract in a catalog.

        Args:
            catalog_id: The catalog identifier.
            file: A file-like object (opened in binary mode) or raw bytes.
            name: A name for the data contract.
            server_mappings: Optional JSON string of server mappings, e.g.
                ``'[{"server":"my-server","connection":{"id":"conn-123"}}]'``.
            data_contract_id: If provided, the existing contract is updated
                instead of creating a new one.
            validate: When ``False``, skips ODCS schema validation. Defaults
                to ``True``.

        Returns:
            The created or updated DataContract.

        Raises:
            ValueError: If the server returns a non-2xx response.
        """
        if not catalog_id:
            raise ValueError(self._ERR_CATALOG_ID)

        url = (
            f"{self.config.url}/data_quality/v4/catalogs/{catalog_id}"
            "/data_contracts_upload"
        )
        headers = {"Authorization": self.config.auth_token} if self.config.auth_token else {}

        form_data: dict = {"name": name, "validate": str(validate).lower()}
        if server_mappings is not None:
            form_data["server_mappings"] = server_mappings
        if data_contract_id is not None:
            form_data["data_contract_id"] = data_contract_id

        files = {"file": file}
        response = self.session.post(
            url,
            headers=headers,
            data=form_data,
            files=files,
            verify=False,
        )
        if not response.ok:
            raise ValueError(
                f"Failed to upload data contract file to catalog {catalog_id}: "
                f"{response.status_code} {response.text}"
            )
        return DataContract(**response.json())


__all__ = ["DataContractsProvider"]

# Made with Bob
