"""
   Copyright 2026 IBM Corporation

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
"""
Test suite for DataContractsProvider
"""

import io
import json
import pytest

from wxdi.dq_validator.provider.config import ProviderConfig
from wxdi.data_contracts import DataContractsProvider
from wxdi.data_contracts.models import (
    DataContract,
    DataContractCollection,
    DataContractPrototypeJson,
    DataContractPrototypeYaml,
    DataContractTestRequest,
    DataContractTestResponse,
    DataContractTestResult,
    DataContractTestResultCollection,
    DataContractTestResultPrototype,
    DataContractValidationRequest,
    DataContractValidationResponse,
    DataContractType,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

BASE_URL = "https://api.example.com"
AUTH_TOKEN = "Bearer test-token-12345"
PROJECT_ID = "72d21c1d-499b-4784-a3c7-6f84507f9a20"
CATALOG_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
CONTRACT_ID = "58be8340-2844-47ab-9528-c6d0cb235354"
TEST_RUN_ID = "7c8d9e0f-1a2b-3c4d-5e6f-7a8b9c0d1e2f"


@pytest.fixture
def config_with_project():
    return ProviderConfig(BASE_URL, AUTH_TOKEN, project_id=PROJECT_ID)


@pytest.fixture
def config_with_catalog():
    return ProviderConfig(BASE_URL, AUTH_TOKEN, catalog_id=CATALOG_ID)


@pytest.fixture
def data_contract_json():
    return {
        "id": CONTRACT_ID,
        "name": "Sales_Data_Contract",
        "type": "contract",
        "data_product_id": "dp-abc123",
        "contract_yaml": "dataContractSpecification: '1.0.0'\nid: sales-contract",
        "server_mappings": [
            {"server": "my-postgres", "connection": {"id": "81bafdbd-b7c6-45c5-a4fd-6ec135f66f4e"}}
        ],
    }


@pytest.fixture
def data_contract_collection_json(data_contract_json):
    return {
        "data_contracts": [data_contract_json],
        "total_count": 1,
    }


@pytest.fixture
def validation_response_valid_json():
    return {"valid": True, "errors": [], "error_count": 0}


@pytest.fixture
def validation_response_invalid_json():
    return {
        "valid": False,
        "error_count": 1,
        "errors": [
            {"property": "$.info.title", "message": "Required property 'title' is missing", "type": "required"}
        ],
    }


@pytest.fixture
def test_response_json():
    """Trigger response returned by POST /test (DataContractTestResponse shape)."""
    return {
        "id": TEST_RUN_ID,
        "href": f"/data_quality/v4/projects/{PROJECT_ID}/data_contracts/{CONTRACT_ID}/test_results/{TEST_RUN_ID}",
        "status": "starting",
        "data_contract_id": CONTRACT_ID,
        "data_contract_name": "Sales Data Contract",
        "run_by": "system",
        "job": {"id": "job-abc123", "run": {"id": TEST_RUN_ID}},
    }


@pytest.fixture
def test_result_json():
    """Persisted result returned by GET/POST/PUT /test_results (DataContractTestResult shape)."""
    return {
        "id": TEST_RUN_ID,
        "href": f"/data_quality/v4/projects/{PROJECT_ID}/data_contracts/{CONTRACT_ID}/test_results/{TEST_RUN_ID}",
        "status": "completed",
        "server_mappings": [],
        "data_assets": [],
    }


@pytest.fixture
def test_response_collection_json(test_result_json):
    return {"test_results": [test_result_json]}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_ok_response(mocker, method: str, payload):
    """Return a mock session where session.<method>() returns an ok response."""
    mock_resp = mocker.Mock()
    mock_resp.ok = True
    mock_resp.json.return_value = payload
    mock_resp.status_code = 200
    mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
    getattr(mock_session_cls.return_value, method).return_value = mock_resp
    return mock_session_cls


def _mock_error_response(mocker, method: str, status: int = 500):
    """Return a mock session where session.<method>() returns an error response."""
    mock_resp = mocker.Mock()
    mock_resp.ok = False
    mock_resp.status_code = status
    mock_resp.text = json.dumps({"error": "Something went wrong"})
    mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
    getattr(mock_session_cls.return_value, method).return_value = mock_resp
    return mock_session_cls


# ===========================================================================
# DATA CONTRACT MODEL NORMALISATION
# ===========================================================================


class TestDataContractModelNormalisation:
    """Verify DataContract handles both the flat spec shape and the nested
    real-API (CAMS asset) shape transparently."""

    def test_flat_shape_unchanged(self):
        dc = DataContract(
            id="flat-id",
            name="flat-name",
            contract_yaml="x: 1",
            server_mappings=[],
        )
        assert dc.id == "flat-id"
        assert dc.name == "flat-name"

    def test_nested_shape_promotes_id_and_name(self):
        nested = {
            "metadata": {
                "asset_id": "019fcafb-4a62-726d-9017-335baf537171",
                "name": "My_Contract_1",
                "project_id": "6ce47397-abfd-4c4a-8a98-d9db02ca6937",
            },
            "entity": {
                "ibm_data_contract": {
                    "name": "My_Contract_1",
                    "status": "active",
                    "content_format": "yaml",
                }
            },
            "href": "/v2/assets/019fcafb-4a62-726d-9017-335baf537171",
        }
        dc = DataContract(**nested)
        assert dc.id == "019fcafb-4a62-726d-9017-335baf537171"
        assert dc.name == "My_Contract_1"

    def test_nested_shape_flat_id_takes_precedence(self):
        """If the server ever sends both top-level id and metadata, top-level wins."""
        nested = {
            "id": "top-level-id",
            "metadata": {"asset_id": "metadata-id", "name": "meta-name"},
        }
        dc = DataContract(**nested)
        assert dc.id == "top-level-id"

    def test_nested_shape_missing_metadata(self):
        """No metadata key → id and name stay None, no error."""
        dc = DataContract(server_mappings=[])
        assert dc.id is None
        assert dc.name is None

    def test_list_response_promotes_fields(self):
        """DataContractCollection built from bare-list response normalises each item."""
        items = [
            {
                "metadata": {
                    "asset_id": "id-1",
                    "name": "contract-1",
                }
            }
        ]
        col = DataContractCollection(data_contracts=items, total_count=1)
        assert col.data_contracts[0].id == "id-1"
        assert col.data_contracts[0].name == "contract-1"


# ===========================================================================
# PROJECT-SCOPED TESTS
# ===========================================================================


class TestListProjectDataContracts:

    def test_success_returns_collection(self, config_with_project, data_contract_collection_json, mocker):
        _mock_ok_response(mocker, "get", data_contract_collection_json)
        provider = DataContractsProvider(config_with_project)
        result = provider.list_project_data_contracts(PROJECT_ID)
        assert isinstance(result, DataContractCollection)
        assert result.total_count == 1
        assert len(result.data_contracts) == 1
        assert result.data_contracts[0].id == CONTRACT_ID

    def test_correct_url_and_params(self, config_with_project, data_contract_collection_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "get", data_contract_collection_json)
        DataContractsProvider(config_with_project).list_project_data_contracts(PROJECT_ID, limit=50)
        call_kwargs = mock_session_cls.return_value.get.call_args
        assert f"/projects/{PROJECT_ID}/data_contracts" in call_kwargs[0][0]
        assert call_kwargs[1]["params"]["limit"] == 50

    def test_api_returns_bare_list(self, config_with_project, data_contract_json, mocker):
        # Real API may return a plain JSON array instead of the wrapped object
        _mock_ok_response(mocker, "get", [data_contract_json])
        result = DataContractsProvider(config_with_project).list_project_data_contracts(PROJECT_ID)
        assert isinstance(result, DataContractCollection)
        assert result.total_count == 1
        assert len(result.data_contracts) == 1
        assert result.data_contracts[0].id == CONTRACT_ID

    def test_error_raises_value_error(self, config_with_project, mocker):
        _mock_error_response(mocker, "get", status=404)
        with pytest.raises(ValueError, match=PROJECT_ID):
            DataContractsProvider(config_with_project).list_project_data_contracts(PROJECT_ID)

    def test_empty_project_id_raises(self, config_with_project):
        with pytest.raises(ValueError, match="project_id"):
            DataContractsProvider(config_with_project).list_project_data_contracts("")


class TestCreateProjectDataContract:

    def test_success_yaml_body(self, config_with_project, data_contract_json, mocker):
        mock_resp = mocker.Mock()
        mock_resp.ok = True
        mock_resp.json.return_value = data_contract_json
        mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_cls.return_value.post.return_value = mock_resp

        body = DataContractPrototypeYaml(
            name="Sales_Data_Contract",
            contract_yaml="dataContractSpecification: '1.0.0'\nid: sales",
        )
        result = DataContractsProvider(config_with_project).create_project_data_contract(PROJECT_ID, body)
        assert isinstance(result, DataContract)
        assert result.name == "Sales_Data_Contract"

    def test_success_json_body(self, config_with_project, data_contract_json, mocker):
        mock_resp = mocker.Mock()
        mock_resp.ok = True
        mock_resp.json.return_value = data_contract_json
        mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_cls.return_value.post.return_value = mock_resp

        body = DataContractPrototypeJson(
            name="Sales_Data_Contract",
            contract_json={"dataContractSpecification": "1.0.0"},
        )
        result = DataContractsProvider(config_with_project).create_project_data_contract(PROJECT_ID, body)
        assert isinstance(result, DataContract)

    def test_validate_param_forwarded(self, config_with_project, data_contract_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "post", data_contract_json)
        body = DataContractPrototypeYaml(name="c", contract_yaml="x: 1")
        DataContractsProvider(config_with_project).create_project_data_contract(
            PROJECT_ID, body, validate=False
        )
        call_kwargs = mock_session_cls.return_value.post.call_args
        assert call_kwargs[1]["params"]["validate"] == "false"

    def test_validate_true_by_default(self, config_with_project, data_contract_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "post", data_contract_json)
        body = DataContractPrototypeYaml(name="c", contract_yaml="x: 1")
        DataContractsProvider(config_with_project).create_project_data_contract(PROJECT_ID, body)
        call_kwargs = mock_session_cls.return_value.post.call_args
        assert call_kwargs[1]["params"]["validate"] == "true"

    def test_error_raises_value_error(self, config_with_project, mocker):
        _mock_error_response(mocker, "post", status=400)
        body = DataContractPrototypeYaml(name="c", contract_yaml="bad")
        with pytest.raises(ValueError, match=PROJECT_ID):
            DataContractsProvider(config_with_project).create_project_data_contract(PROJECT_ID, body)

    def test_empty_project_id_raises(self, config_with_project):
        with pytest.raises(ValueError, match="project_id"):
            DataContractsProvider(config_with_project).create_project_data_contract(
                "", DataContractPrototypeYaml(name="c", contract_yaml="x")
            )


class TestDeleteProjectDataContracts:

    def test_success_no_return(self, config_with_project, mocker):
        mock_resp = mocker.Mock()
        mock_resp.ok = True
        mock_resp.status_code = 204
        mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_cls.return_value.delete.return_value = mock_resp
        result = DataContractsProvider(config_with_project).delete_project_data_contracts(
            PROJECT_ID, data_contract_ids=CONTRACT_ID
        )
        assert result is None

    def test_ids_forwarded_as_query_param(self, config_with_project, mocker):
        mock_resp = mocker.Mock()
        mock_resp.ok = True
        mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_cls.return_value.delete.return_value = mock_resp
        ids = f"{CONTRACT_ID},another-id"
        DataContractsProvider(config_with_project).delete_project_data_contracts(
            PROJECT_ID, data_contract_ids=ids
        )
        call_kwargs = mock_session_cls.return_value.delete.call_args
        assert call_kwargs[1]["params"]["data_contract_ids"] == ids

    def test_error_raises_value_error(self, config_with_project, mocker):
        _mock_error_response(mocker, "delete", status=404)
        with pytest.raises(ValueError, match=PROJECT_ID):
            DataContractsProvider(config_with_project).delete_project_data_contracts(
                PROJECT_ID, data_contract_ids=CONTRACT_ID
            )

    def test_empty_ids_raises(self, config_with_project):
        with pytest.raises(ValueError, match="data_contract_ids"):
            DataContractsProvider(config_with_project).delete_project_data_contracts(
                PROJECT_ID, data_contract_ids=""
            )

    def test_empty_project_id_raises(self, config_with_project):
        with pytest.raises(ValueError, match="project_id"):
            DataContractsProvider(config_with_project).delete_project_data_contracts(
                "", data_contract_ids=CONTRACT_ID
            )


class TestGetProjectDataContract:

    def test_success(self, config_with_project, data_contract_json, mocker):
        _mock_ok_response(mocker, "get", data_contract_json)
        result = DataContractsProvider(config_with_project).get_project_data_contract(
            PROJECT_ID, CONTRACT_ID
        )
        assert isinstance(result, DataContract)
        assert result.id == CONTRACT_ID

    def test_correct_url(self, config_with_project, data_contract_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "get", data_contract_json)
        DataContractsProvider(config_with_project).get_project_data_contract(PROJECT_ID, CONTRACT_ID)
        url = mock_session_cls.return_value.get.call_args[0][0]
        assert f"/projects/{PROJECT_ID}/data_contracts/{CONTRACT_ID}" in url

    def test_not_found_raises_value_error(self, config_with_project, mocker):
        _mock_error_response(mocker, "get", status=404)
        with pytest.raises(ValueError, match=CONTRACT_ID):
            DataContractsProvider(config_with_project).get_project_data_contract(
                PROJECT_ID, CONTRACT_ID
            )

    def test_empty_contract_id_raises(self, config_with_project):
        with pytest.raises(ValueError, match="data_contract_id"):
            DataContractsProvider(config_with_project).get_project_data_contract(PROJECT_ID, "")


class TestReplaceProjectDataContract:

    def test_success(self, config_with_project, data_contract_json, mocker):
        _mock_ok_response(mocker, "put", data_contract_json)
        body = DataContractPrototypeYaml(name="Sales_Data_Contract", contract_yaml="x: 1")
        result = DataContractsProvider(config_with_project).replace_project_data_contract(
            PROJECT_ID, CONTRACT_ID, body
        )
        assert isinstance(result, DataContract)

    def test_validate_true_by_default(self, config_with_project, data_contract_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "put", data_contract_json)
        body = DataContractPrototypeYaml(name="c", contract_yaml="x: 1")
        DataContractsProvider(config_with_project).replace_project_data_contract(
            PROJECT_ID, CONTRACT_ID, body
        )
        assert mock_session_cls.return_value.put.call_args[1]["params"]["validate"] == "true"

    def test_error_raises_value_error(self, config_with_project, mocker):
        _mock_error_response(mocker, "put", status=400)
        body = DataContractPrototypeYaml(name="c", contract_yaml="bad")
        with pytest.raises(ValueError, match=CONTRACT_ID):
            DataContractsProvider(config_with_project).replace_project_data_contract(
                PROJECT_ID, CONTRACT_ID, body
            )


class TestValidateProjectDataContract:

    def test_valid_contract(self, config_with_project, validation_response_valid_json, mocker):
        _mock_ok_response(mocker, "post", validation_response_valid_json)
        body = DataContractValidationRequest(data_contract_content='{"id": "x"}')
        result = DataContractsProvider(config_with_project).validate_project_data_contract(
            PROJECT_ID, body
        )
        assert isinstance(result, DataContractValidationResponse)
        assert result.valid is True
        assert result.error_count == 0

    def test_invalid_contract(self, config_with_project, validation_response_invalid_json, mocker):
        _mock_ok_response(mocker, "post", validation_response_invalid_json)
        body = DataContractValidationRequest(data_contract_content='bad yaml')
        result = DataContractsProvider(config_with_project).validate_project_data_contract(
            PROJECT_ID, body
        )
        assert result.valid is False
        assert result.error_count == 1
        assert result.errors[0].type == "required"

    def test_correct_url(self, config_with_project, validation_response_valid_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "post", validation_response_valid_json)
        body = DataContractValidationRequest(data_contract_content="x")
        DataContractsProvider(config_with_project).validate_project_data_contract(PROJECT_ID, body)
        url = mock_session_cls.return_value.post.call_args[0][0]
        assert f"/projects/{PROJECT_ID}/data_contracts_validation" in url

    def test_sends_raw_text_body_with_text_plain_content_type(
        self, config_with_project, validation_response_valid_json, mocker
    ):
        mock_session_cls = _mock_ok_response(mocker, "post", validation_response_valid_json)
        content = "id: my-contract\nname: test"
        body = DataContractValidationRequest(data_contract_content=content)
        DataContractsProvider(config_with_project).validate_project_data_contract(PROJECT_ID, body)
        call_kwargs = mock_session_cls.return_value.post.call_args
        # Body must be the raw string, NOT a JSON-wrapped object
        assert call_kwargs[1]["data"] == content
        assert call_kwargs[1]["headers"]["Content-Type"] == "text/plain"

    def test_server_error_raises(self, config_with_project, mocker):
        _mock_error_response(mocker, "post", status=500)
        body = DataContractValidationRequest(data_contract_content="x")
        with pytest.raises(ValueError, match=PROJECT_ID):
            DataContractsProvider(config_with_project).validate_project_data_contract(PROJECT_ID, body)


class TestUploadProjectDataContractFile:

    def test_success_create(self, config_with_project, data_contract_json, mocker):
        mock_resp = mocker.Mock()
        mock_resp.ok = True
        mock_resp.json.return_value = data_contract_json
        mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_cls.return_value.post.return_value = mock_resp

        file_content = io.BytesIO(b"dataContractSpecification: '1.0.0'")
        result = DataContractsProvider(config_with_project).upload_project_data_contract_file(
            PROJECT_ID, file_content, name="Sales_Data_Contract"
        )
        assert isinstance(result, DataContract)

    def test_correct_url(self, config_with_project, data_contract_json, mocker):
        mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_cls.return_value.post.return_value = mocker.Mock(
            ok=True, json=lambda: data_contract_json
        )
        DataContractsProvider(config_with_project).upload_project_data_contract_file(
            PROJECT_ID, b"content", name="contract"
        )
        url = mock_session_cls.return_value.post.call_args[0][0]
        assert f"/projects/{PROJECT_ID}/data_contracts_upload" in url

    def test_server_mappings_forwarded(self, config_with_project, data_contract_json, mocker):
        mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_cls.return_value.post.return_value = mocker.Mock(
            ok=True, json=lambda: data_contract_json
        )
        mappings = '[{"server":"s","connection":{"id":"c"}}]'
        DataContractsProvider(config_with_project).upload_project_data_contract_file(
            PROJECT_ID, b"content", name="c", server_mappings=mappings
        )
        form_data = mock_session_cls.return_value.post.call_args[1]["data"]
        assert form_data["server_mappings"] == mappings

    def test_data_contract_id_forwarded_for_update(self, config_with_project, data_contract_json, mocker):
        mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_cls.return_value.post.return_value = mocker.Mock(
            ok=True, json=lambda: data_contract_json
        )
        DataContractsProvider(config_with_project).upload_project_data_contract_file(
            PROJECT_ID, b"content", name="c", data_contract_id=CONTRACT_ID
        )
        form_data = mock_session_cls.return_value.post.call_args[1]["data"]
        assert form_data["data_contract_id"] == CONTRACT_ID

    def test_error_raises_value_error(self, config_with_project, mocker):
        _mock_error_response(mocker, "post", status=415)
        with pytest.raises(ValueError, match=PROJECT_ID):
            DataContractsProvider(config_with_project).upload_project_data_contract_file(
                PROJECT_ID, b"bad", name="c"
            )


class TestTestProjectDataContract:

    def test_success(self, config_with_project, test_response_json, mocker):
        _mock_ok_response(mocker, "post", test_response_json)
        body = DataContractTestRequest(
            server_mappings=[{"server": "my-pg", "connection": {"id": "conn-1"}}],
            retain_dq_objects=True,
        )
        result = DataContractsProvider(config_with_project).test_project_data_contract(
            PROJECT_ID, CONTRACT_ID, body
        )
        assert isinstance(result, DataContractTestResponse)
        assert result.status == "starting"
        assert result.id == TEST_RUN_ID
        assert result.job.id == "job-abc123"
        assert result.job.run.id == TEST_RUN_ID

    def test_no_body_uses_default(self, config_with_project, test_response_json, mocker):
        _mock_ok_response(mocker, "post", test_response_json)
        result = DataContractsProvider(config_with_project).test_project_data_contract(
            PROJECT_ID, CONTRACT_ID
        )
        assert isinstance(result, DataContractTestResponse)

    def test_correct_url(self, config_with_project, test_response_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "post", test_response_json)
        DataContractsProvider(config_with_project).test_project_data_contract(
            PROJECT_ID, CONTRACT_ID
        )
        url = mock_session_cls.return_value.post.call_args[0][0]
        assert f"/projects/{PROJECT_ID}/data_contracts/{CONTRACT_ID}/test" in url

    def test_error_raises_value_error(self, config_with_project, mocker):
        _mock_error_response(mocker, "post", status=400)
        with pytest.raises(ValueError, match=CONTRACT_ID):
            DataContractsProvider(config_with_project).test_project_data_contract(
                PROJECT_ID, CONTRACT_ID
            )


class TestListProjectDataContractTestResults:

    def test_success(self, config_with_project, test_response_collection_json, mocker):
        _mock_ok_response(mocker, "get", test_response_collection_json)
        result = DataContractsProvider(config_with_project).list_project_data_contract_test_results(
            PROJECT_ID, CONTRACT_ID
        )
        assert isinstance(result, DataContractTestResultCollection)
        assert len(result.test_results) == 1

    def test_include_all_details_forwarded(self, config_with_project, test_response_collection_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "get", test_response_collection_json)
        DataContractsProvider(config_with_project).list_project_data_contract_test_results(
            PROJECT_ID, CONTRACT_ID, include_all_details=True
        )
        params = mock_session_cls.return_value.get.call_args[1]["params"]
        assert params["include_all_details"] == "true"

    def test_error_raises_value_error(self, config_with_project, mocker):
        _mock_error_response(mocker, "get", status=404)
        with pytest.raises(ValueError, match=CONTRACT_ID):
            DataContractsProvider(config_with_project).list_project_data_contract_test_results(
                PROJECT_ID, CONTRACT_ID
            )


class TestDeleteProjectDataContractTestResults:

    def test_success_no_return(self, config_with_project, mocker):
        mock_resp = mocker.Mock()
        mock_resp.ok = True
        mock_resp.status_code = 204
        mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_cls.return_value.delete.return_value = mock_resp
        result = DataContractsProvider(config_with_project).delete_project_data_contract_test_results(
            PROJECT_ID, CONTRACT_ID
        )
        assert result is None

    def test_correct_url(self, config_with_project, mocker):
        mock_resp = mocker.Mock()
        mock_resp.ok = True
        mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_cls.return_value.delete.return_value = mock_resp
        DataContractsProvider(config_with_project).delete_project_data_contract_test_results(
            PROJECT_ID, CONTRACT_ID
        )
        url = mock_session_cls.return_value.delete.call_args[0][0]
        assert f"/projects/{PROJECT_ID}/data_contracts/{CONTRACT_ID}/test_results" in url

    def test_error_raises_value_error(self, config_with_project, mocker):
        _mock_error_response(mocker, "delete", status=500)
        with pytest.raises(ValueError, match=CONTRACT_ID):
            DataContractsProvider(config_with_project).delete_project_data_contract_test_results(
                PROJECT_ID, CONTRACT_ID
            )


class TestGetProjectDataContractTestResult:

    def test_success(self, config_with_project, test_result_json, mocker):
        _mock_ok_response(mocker, "get", test_result_json)
        result = DataContractsProvider(config_with_project).get_project_data_contract_test_result(
            PROJECT_ID, CONTRACT_ID, TEST_RUN_ID
        )
        assert isinstance(result, DataContractTestResult)
        assert result.id == TEST_RUN_ID

    def test_correct_url(self, config_with_project, test_result_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "get", test_result_json)
        DataContractsProvider(config_with_project).get_project_data_contract_test_result(
            PROJECT_ID, CONTRACT_ID, TEST_RUN_ID
        )
        url = mock_session_cls.return_value.get.call_args[0][0]
        assert (
            f"/projects/{PROJECT_ID}/data_contracts/{CONTRACT_ID}/test_results/{TEST_RUN_ID}"
            in url
        )

    def test_not_found_raises_value_error(self, config_with_project, mocker):
        _mock_error_response(mocker, "get", status=404)
        with pytest.raises(ValueError, match=TEST_RUN_ID):
            DataContractsProvider(config_with_project).get_project_data_contract_test_result(
                PROJECT_ID, CONTRACT_ID, TEST_RUN_ID
            )

    def test_empty_test_run_id_raises(self, config_with_project):
        with pytest.raises(ValueError, match="test_run_id"):
            DataContractsProvider(config_with_project).get_project_data_contract_test_result(
                PROJECT_ID, CONTRACT_ID, ""
            )


class TestCreateProjectDataContractTestResult:

    def test_success(self, config_with_project, test_result_json, mocker):
        _mock_ok_response(mocker, "post", test_result_json)
        result = DataContractsProvider(config_with_project).create_project_data_contract_test_result(
            PROJECT_ID, CONTRACT_ID, DataContractTestResultPrototype(status="completed")
        )
        assert isinstance(result, DataContractTestResult)
        assert result.id == TEST_RUN_ID

    def test_correct_url(self, config_with_project, test_result_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "post", test_result_json)
        DataContractsProvider(config_with_project).create_project_data_contract_test_result(
            PROJECT_ID, CONTRACT_ID, DataContractTestResultPrototype(status="completed")
        )
        url = mock_session_cls.return_value.post.call_args[0][0]
        assert f"/projects/{PROJECT_ID}/data_contracts/{CONTRACT_ID}/test_results" in url

    def test_body_serialised_as_json(self, config_with_project, test_result_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "post", test_result_json)
        DataContractsProvider(config_with_project).create_project_data_contract_test_result(
            PROJECT_ID, CONTRACT_ID, DataContractTestResultPrototype(status="completed")
        )
        body = mock_session_cls.return_value.post.call_args[1]["json"]
        assert body["status"] == "completed"

    def test_error_raises_value_error(self, config_with_project, mocker):
        _mock_error_response(mocker, "post", status=400)
        with pytest.raises(ValueError, match=CONTRACT_ID):
            DataContractsProvider(config_with_project).create_project_data_contract_test_result(
                PROJECT_ID, CONTRACT_ID, DataContractTestResultPrototype()
            )

    def test_empty_project_id_raises(self, config_with_project):
        with pytest.raises(ValueError, match="project_id"):
            DataContractsProvider(config_with_project).create_project_data_contract_test_result(
                "", CONTRACT_ID, DataContractTestResultPrototype()
            )

    def test_empty_contract_id_raises(self, config_with_project):
        with pytest.raises(ValueError, match="data_contract_id"):
            DataContractsProvider(config_with_project).create_project_data_contract_test_result(
                PROJECT_ID, "", DataContractTestResultPrototype()
            )


class TestUpdateProjectDataContractTestResult:

    def test_success(self, config_with_project, test_result_json, mocker):
        _mock_ok_response(mocker, "put", test_result_json)
        result = DataContractsProvider(config_with_project).update_project_data_contract_test_result(
            PROJECT_ID, CONTRACT_ID, TEST_RUN_ID, DataContractTestResultPrototype(status="completed")
        )
        assert isinstance(result, DataContractTestResult)
        assert result.id == TEST_RUN_ID

    def test_correct_url(self, config_with_project, test_result_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "put", test_result_json)
        DataContractsProvider(config_with_project).update_project_data_contract_test_result(
            PROJECT_ID, CONTRACT_ID, TEST_RUN_ID, DataContractTestResultPrototype(status="completed")
        )
        url = mock_session_cls.return_value.put.call_args[0][0]
        assert (
            f"/projects/{PROJECT_ID}/data_contracts/{CONTRACT_ID}/test_results/{TEST_RUN_ID}"
            in url
        )

    def test_body_serialised_as_json(self, config_with_project, test_result_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "put", test_result_json)
        DataContractsProvider(config_with_project).update_project_data_contract_test_result(
            PROJECT_ID, CONTRACT_ID, TEST_RUN_ID, DataContractTestResultPrototype(status="failed")
        )
        body = mock_session_cls.return_value.put.call_args[1]["json"]
        assert body["status"] == "failed"

    def test_not_found_raises_value_error(self, config_with_project, mocker):
        _mock_error_response(mocker, "put", status=404)
        with pytest.raises(ValueError, match=TEST_RUN_ID):
            DataContractsProvider(config_with_project).update_project_data_contract_test_result(
                PROJECT_ID, CONTRACT_ID, TEST_RUN_ID, DataContractTestResultPrototype()
            )

    def test_empty_project_id_raises(self, config_with_project):
        with pytest.raises(ValueError, match="project_id"):
            DataContractsProvider(config_with_project).update_project_data_contract_test_result(
                "", CONTRACT_ID, TEST_RUN_ID, DataContractTestResultPrototype()
            )

    def test_empty_contract_id_raises(self, config_with_project):
        with pytest.raises(ValueError, match="data_contract_id"):
            DataContractsProvider(config_with_project).update_project_data_contract_test_result(
                PROJECT_ID, "", TEST_RUN_ID, DataContractTestResultPrototype()
            )

    def test_empty_test_run_id_raises(self, config_with_project):
        with pytest.raises(ValueError, match="test_run_id"):
            DataContractsProvider(config_with_project).update_project_data_contract_test_result(
                PROJECT_ID, CONTRACT_ID, "", DataContractTestResultPrototype()
            )


# ===========================================================================
# CATALOG-SCOPED TESTS
# ===========================================================================


class TestListCatalogDataContracts:

    def test_success_returns_collection(self, config_with_catalog, data_contract_collection_json, mocker):
        _mock_ok_response(mocker, "get", data_contract_collection_json)
        result = DataContractsProvider(config_with_catalog).list_catalog_data_contracts(CATALOG_ID)
        assert isinstance(result, DataContractCollection)
        assert result.total_count == 1

    def test_url_uses_catalogs_path(self, config_with_catalog, data_contract_collection_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "get", data_contract_collection_json)
        DataContractsProvider(config_with_catalog).list_catalog_data_contracts(CATALOG_ID)
        url = mock_session_cls.return_value.get.call_args[0][0]
        assert f"/catalogs/{CATALOG_ID}/data_contracts" in url
        assert "/projects/" not in url

    def test_limit_forwarded(self, config_with_catalog, data_contract_collection_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "get", data_contract_collection_json)
        DataContractsProvider(config_with_catalog).list_catalog_data_contracts(CATALOG_ID, limit=100)
        params = mock_session_cls.return_value.get.call_args[1]["params"]
        assert params["limit"] == 100

    def test_api_returns_bare_list(self, config_with_catalog, data_contract_json, mocker):
        # Real API may return a plain JSON array instead of the wrapped object
        _mock_ok_response(mocker, "get", [data_contract_json])
        result = DataContractsProvider(config_with_catalog).list_catalog_data_contracts(CATALOG_ID)
        assert isinstance(result, DataContractCollection)
        assert result.total_count == 1
        assert len(result.data_contracts) == 1

    def test_error_raises_value_error(self, config_with_catalog, mocker):
        _mock_error_response(mocker, "get", status=500)
        with pytest.raises(ValueError, match=CATALOG_ID):
            DataContractsProvider(config_with_catalog).list_catalog_data_contracts(CATALOG_ID)

    def test_empty_catalog_id_raises(self, config_with_catalog):
        with pytest.raises(ValueError, match="catalog_id"):
            DataContractsProvider(config_with_catalog).list_catalog_data_contracts("")


class TestCreateCatalogDataContract:

    def test_success(self, config_with_catalog, data_contract_json, mocker):
        _mock_ok_response(mocker, "post", data_contract_json)
        body = DataContractPrototypeYaml(name="Sales_Data_Contract", contract_yaml="x: 1")
        result = DataContractsProvider(config_with_catalog).create_catalog_data_contract(
            CATALOG_ID, body
        )
        assert isinstance(result, DataContract)

    def test_url_uses_catalogs_path(self, config_with_catalog, data_contract_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "post", data_contract_json)
        body = DataContractPrototypeYaml(name="c", contract_yaml="x: 1")
        DataContractsProvider(config_with_catalog).create_catalog_data_contract(CATALOG_ID, body)
        url = mock_session_cls.return_value.post.call_args[0][0]
        assert f"/catalogs/{CATALOG_ID}/data_contracts" in url
        assert "/projects/" not in url

    def test_validate_true_by_default(self, config_with_catalog, data_contract_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "post", data_contract_json)
        body = DataContractPrototypeYaml(name="c", contract_yaml="x: 1")
        DataContractsProvider(config_with_catalog).create_catalog_data_contract(CATALOG_ID, body)
        assert mock_session_cls.return_value.post.call_args[1]["params"]["validate"] == "true"

    def test_error_raises_value_error(self, config_with_catalog, mocker):
        _mock_error_response(mocker, "post", status=400)
        body = DataContractPrototypeYaml(name="c", contract_yaml="bad")
        with pytest.raises(ValueError, match=CATALOG_ID):
            DataContractsProvider(config_with_catalog).create_catalog_data_contract(CATALOG_ID, body)


class TestDeleteCatalogDataContracts:

    def test_success_no_return(self, config_with_catalog, mocker):
        mock_resp = mocker.Mock()
        mock_resp.ok = True
        mock_resp.status_code = 204
        mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_cls.return_value.delete.return_value = mock_resp
        result = DataContractsProvider(config_with_catalog).delete_catalog_data_contracts(
            CATALOG_ID, data_contract_ids=CONTRACT_ID
        )
        assert result is None

    def test_url_uses_catalogs_path(self, config_with_catalog, mocker):
        mock_resp = mocker.Mock()
        mock_resp.ok = True
        mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_cls.return_value.delete.return_value = mock_resp
        DataContractsProvider(config_with_catalog).delete_catalog_data_contracts(
            CATALOG_ID, data_contract_ids=CONTRACT_ID
        )
        url = mock_session_cls.return_value.delete.call_args[0][0]
        assert f"/catalogs/{CATALOG_ID}/data_contracts" in url
        assert "/projects/" not in url

    def test_error_raises_value_error(self, config_with_catalog, mocker):
        _mock_error_response(mocker, "delete", status=404)
        with pytest.raises(ValueError, match=CATALOG_ID):
            DataContractsProvider(config_with_catalog).delete_catalog_data_contracts(
                CATALOG_ID, data_contract_ids=CONTRACT_ID
            )


class TestGetCatalogDataContract:

    def test_success(self, config_with_catalog, data_contract_json, mocker):
        _mock_ok_response(mocker, "get", data_contract_json)
        result = DataContractsProvider(config_with_catalog).get_catalog_data_contract(
            CATALOG_ID, CONTRACT_ID
        )
        assert isinstance(result, DataContract)
        assert result.id == CONTRACT_ID

    def test_url_uses_catalogs_path(self, config_with_catalog, data_contract_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "get", data_contract_json)
        DataContractsProvider(config_with_catalog).get_catalog_data_contract(CATALOG_ID, CONTRACT_ID)
        url = mock_session_cls.return_value.get.call_args[0][0]
        assert f"/catalogs/{CATALOG_ID}/data_contracts/{CONTRACT_ID}" in url

    def test_not_found_raises_value_error(self, config_with_catalog, mocker):
        _mock_error_response(mocker, "get", status=404)
        with pytest.raises(ValueError, match=CONTRACT_ID):
            DataContractsProvider(config_with_catalog).get_catalog_data_contract(
                CATALOG_ID, CONTRACT_ID
            )

    def test_empty_contract_id_raises(self, config_with_catalog):
        with pytest.raises(ValueError, match="data_contract_id"):
            DataContractsProvider(config_with_catalog).get_catalog_data_contract(CATALOG_ID, "")


class TestReplaceCatalogDataContract:

    def test_success(self, config_with_catalog, data_contract_json, mocker):
        _mock_ok_response(mocker, "put", data_contract_json)
        body = DataContractPrototypeYaml(name="c", contract_yaml="x: 1")
        result = DataContractsProvider(config_with_catalog).replace_catalog_data_contract(
            CATALOG_ID, CONTRACT_ID, body
        )
        assert isinstance(result, DataContract)

    def test_url_uses_catalogs_path(self, config_with_catalog, data_contract_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "put", data_contract_json)
        body = DataContractPrototypeYaml(name="c", contract_yaml="x: 1")
        DataContractsProvider(config_with_catalog).replace_catalog_data_contract(
            CATALOG_ID, CONTRACT_ID, body
        )
        url = mock_session_cls.return_value.put.call_args[0][0]
        assert f"/catalogs/{CATALOG_ID}/data_contracts/{CONTRACT_ID}" in url
        assert "/projects/" not in url

    def test_error_raises_value_error(self, config_with_catalog, mocker):
        _mock_error_response(mocker, "put", status=400)
        body = DataContractPrototypeYaml(name="c", contract_yaml="bad")
        with pytest.raises(ValueError, match=CONTRACT_ID):
            DataContractsProvider(config_with_catalog).replace_catalog_data_contract(
                CATALOG_ID, CONTRACT_ID, body
            )


class TestValidateCatalogDataContract:

    def test_valid_contract(self, config_with_catalog, validation_response_valid_json, mocker):
        _mock_ok_response(mocker, "post", validation_response_valid_json)
        body = DataContractValidationRequest(data_contract_content='{"id": "x"}')
        result = DataContractsProvider(config_with_catalog).validate_catalog_data_contract(
            CATALOG_ID, body
        )
        assert result.valid is True

    def test_url_uses_catalogs_path(self, config_with_catalog, validation_response_valid_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "post", validation_response_valid_json)
        body = DataContractValidationRequest(data_contract_content="x")
        DataContractsProvider(config_with_catalog).validate_catalog_data_contract(CATALOG_ID, body)
        url = mock_session_cls.return_value.post.call_args[0][0]
        assert f"/catalogs/{CATALOG_ID}/data_contracts_validation" in url
        assert "/projects/" not in url

    def test_sends_raw_text_body_with_text_plain_content_type(
        self, config_with_catalog, validation_response_valid_json, mocker
    ):
        mock_session_cls = _mock_ok_response(mocker, "post", validation_response_valid_json)
        content = "id: my-contract\nname: test"
        body = DataContractValidationRequest(data_contract_content=content)
        DataContractsProvider(config_with_catalog).validate_catalog_data_contract(CATALOG_ID, body)
        call_kwargs = mock_session_cls.return_value.post.call_args
        assert call_kwargs[1]["data"] == content
        assert call_kwargs[1]["headers"]["Content-Type"] == "text/plain"

    def test_error_raises_value_error(self, config_with_catalog, mocker):
        _mock_error_response(mocker, "post", status=500)
        body = DataContractValidationRequest(data_contract_content="x")
        with pytest.raises(ValueError, match=CATALOG_ID):
            DataContractsProvider(config_with_catalog).validate_catalog_data_contract(CATALOG_ID, body)


class TestUploadCatalogDataContractFile:

    def test_success(self, config_with_catalog, data_contract_json, mocker):
        mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_cls.return_value.post.return_value = mocker.Mock(
            ok=True, json=lambda: data_contract_json
        )
        result = DataContractsProvider(config_with_catalog).upload_catalog_data_contract_file(
            CATALOG_ID, b"contract content", name="Sales_Data_Contract"
        )
        assert isinstance(result, DataContract)

    def test_url_uses_catalogs_path(self, config_with_catalog, data_contract_json, mocker):
        mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_cls.return_value.post.return_value = mocker.Mock(
            ok=True, json=lambda: data_contract_json
        )
        DataContractsProvider(config_with_catalog).upload_catalog_data_contract_file(
            CATALOG_ID, b"content", name="c"
        )
        url = mock_session_cls.return_value.post.call_args[0][0]
        assert f"/catalogs/{CATALOG_ID}/data_contracts_upload" in url
        assert "/projects/" not in url

    def test_error_raises_value_error(self, config_with_catalog, mocker):
        _mock_error_response(mocker, "post", status=413)
        with pytest.raises(ValueError, match=CATALOG_ID):
            DataContractsProvider(config_with_catalog).upload_catalog_data_contract_file(
                CATALOG_ID, b"too-big", name="c"
            )

    def test_data_contract_id_forwarded(self, config_with_catalog, data_contract_json, mocker):
        mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_cls.return_value.post.return_value = mocker.Mock(
            ok=True, json=lambda: data_contract_json
        )
        DataContractsProvider(config_with_catalog).upload_catalog_data_contract_file(
            CATALOG_ID, b"content", name="c", data_contract_id=CONTRACT_ID
        )
        form_data = mock_session_cls.return_value.post.call_args[1]["data"]
        assert form_data["data_contract_id"] == CONTRACT_ID


# ===========================================================================
# TYPE FIELD TESTS
# ===========================================================================


class TestTypeField:
    """Verify that the type field is present and correctly handled across all
    affected models: DataContractPrototypeYaml, DataContractPrototypeJson,
    and DataContract."""

    # ------------------------------------------------------------------
    # DataContractPrototypeYaml
    # ------------------------------------------------------------------

    def test_yaml_prototype_type_included_in_serialization(self):
        body = DataContractPrototypeYaml(name="c", contract_yaml="x: 1", type=DataContractType.CONTRACT)
        payload = json.loads(body.model_dump_json(exclude_none=True))
        assert payload["type"] == "contract"

    def test_yaml_prototype_type_excluded_when_none(self):
        body = DataContractPrototypeYaml(name="c", contract_yaml="x: 1")
        payload = json.loads(body.model_dump_json(exclude_none=True))
        assert "type" not in payload

    def test_yaml_prototype_type_defaults_to_none(self):
        body = DataContractPrototypeYaml(name="c", contract_yaml="x: 1")
        assert body.type is None

    # ------------------------------------------------------------------
    # DataContractPrototypeJson
    # ------------------------------------------------------------------

    def test_json_prototype_type_included_in_serialization(self):
        body = DataContractPrototypeJson(
            name="c", contract_json={"id": "x"}, type=DataContractType.CONTRACT
        )
        payload = json.loads(body.model_dump_json(exclude_none=True))
        assert payload["type"] == "contract"

    def test_json_prototype_type_excluded_when_none(self):
        body = DataContractPrototypeJson(name="c", contract_json={"id": "x"})
        payload = json.loads(body.model_dump_json(exclude_none=True))
        assert "type" not in payload

    def test_json_prototype_type_defaults_to_none(self):
        body = DataContractPrototypeJson(name="c", contract_json={"id": "x"})
        assert body.type is None

    # ------------------------------------------------------------------
    # DataContract (response model)
    # ------------------------------------------------------------------

    def test_data_contract_parses_type_from_response(self):
        dc = DataContract(id="x", name="y", type=DataContractType.CONTRACT)
        assert dc.type == DataContractType.CONTRACT

    def test_data_contract_type_defaults_to_none(self):
        dc = DataContract(id="x", name="y")
        assert dc.type is None

    # ------------------------------------------------------------------
    # End-to-end: type flows through create request body
    # ------------------------------------------------------------------

    def test_type_sent_in_create_project_request_body(self, config_with_project, data_contract_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "post", data_contract_json)
        body = DataContractPrototypeYaml(name="c", contract_yaml="x: 1", type=DataContractType.CONTRACT)
        DataContractsProvider(config_with_project).create_project_data_contract(PROJECT_ID, body)
        sent = json.loads(mock_session_cls.return_value.post.call_args[1]["data"])
        assert sent["type"] == "contract"

    def test_type_sent_in_replace_project_request_body(self, config_with_project, data_contract_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "put", data_contract_json)
        body = DataContractPrototypeYaml(name="c", contract_yaml="x: 1", type=DataContractType.CONTRACT)
        DataContractsProvider(config_with_project).replace_project_data_contract(
            PROJECT_ID, CONTRACT_ID, body
        )
        sent = json.loads(mock_session_cls.return_value.put.call_args[1]["data"])
        assert sent["type"] == "contract"

    def test_type_sent_in_create_catalog_request_body(self, config_with_catalog, data_contract_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "post", data_contract_json)
        body = DataContractPrototypeYaml(name="c", contract_yaml="x: 1", type=DataContractType.CONTRACT)
        DataContractsProvider(config_with_catalog).create_catalog_data_contract(CATALOG_ID, body)
        sent = json.loads(mock_session_cls.return_value.post.call_args[1]["data"])
        assert sent["type"] == "contract"

    def test_type_sent_in_replace_catalog_request_body(self, config_with_catalog, data_contract_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "put", data_contract_json)
        body = DataContractPrototypeYaml(name="c", contract_yaml="x: 1", type=DataContractType.CONTRACT)
        DataContractsProvider(config_with_catalog).replace_catalog_data_contract(
            CATALOG_ID, CONTRACT_ID, body
        )
        sent = json.loads(mock_session_cls.return_value.put.call_args[1]["data"])
        assert sent["type"] == "contract"

    def test_type_returned_in_response(self, config_with_project, data_contract_json, mocker):
        _mock_ok_response(mocker, "get", data_contract_json)
        result = DataContractsProvider(config_with_project).get_project_data_contract(
            PROJECT_ID, CONTRACT_ID
        )
        assert result.type == DataContractType.CONTRACT


    # ------------------------------------------------------------------
    # data_product_id field
    # ------------------------------------------------------------------

    def test_yaml_prototype_data_product_id_included_in_serialization(self):
        body = DataContractPrototypeYaml(name="c", contract_yaml="x: 1", data_product_id="dp-abc123")
        payload = json.loads(body.model_dump_json(exclude_none=True))
        assert payload["data_product_id"] == "dp-abc123"

    def test_yaml_prototype_data_product_id_excluded_when_none(self):
        body = DataContractPrototypeYaml(name="c", contract_yaml="x: 1")
        payload = json.loads(body.model_dump_json(exclude_none=True))
        assert "data_product_id" not in payload

    def test_json_prototype_data_product_id_included_in_serialization(self):
        body = DataContractPrototypeJson(name="c", contract_json={"id": "x"}, data_product_id="dp-abc123")
        payload = json.loads(body.model_dump_json(exclude_none=True))
        assert payload["data_product_id"] == "dp-abc123"

    def test_json_prototype_data_product_id_excluded_when_none(self):
        body = DataContractPrototypeJson(name="c", contract_json={"id": "x"})
        payload = json.loads(body.model_dump_json(exclude_none=True))
        assert "data_product_id" not in payload

    def test_data_contract_parses_data_product_id_from_response(self):
        dc = DataContract(id="x", name="y", data_product_id="dp-abc123")
        assert dc.data_product_id == "dp-abc123"

    def test_data_contract_data_product_id_defaults_to_none(self):
        dc = DataContract(id="x", name="y")
        assert dc.data_product_id is None

    def test_data_product_id_sent_in_create_project_request_body(
        self, config_with_project, data_contract_json, mocker
    ):
        mock_session_cls = _mock_ok_response(mocker, "post", data_contract_json)
        body = DataContractPrototypeYaml(name="c", contract_yaml="x: 1", data_product_id="dp-abc123")
        DataContractsProvider(config_with_project).create_project_data_contract(PROJECT_ID, body)
        sent = json.loads(mock_session_cls.return_value.post.call_args[1]["data"])
        assert sent["data_product_id"] == "dp-abc123"

    def test_data_product_id_returned_in_response(
        self, config_with_project, data_contract_json, mocker
    ):
        _mock_ok_response(mocker, "get", data_contract_json)
        result = DataContractsProvider(config_with_project).get_project_data_contract(
            PROJECT_ID, CONTRACT_ID
        )
        assert result.data_product_id == "dp-abc123"

class TestCreateCatalogDataContractTestResult:

    def test_success(self, config_with_catalog, test_result_json, mocker):
        _mock_ok_response(mocker, "post", test_result_json)
        result = DataContractsProvider(config_with_catalog).create_catalog_data_contract_test_result(
            CATALOG_ID, CONTRACT_ID, DataContractTestResultPrototype(status="completed")
        )
        assert isinstance(result, DataContractTestResult)
        assert result.id == TEST_RUN_ID

    def test_url_uses_catalogs_path(self, config_with_catalog, test_result_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "post", test_result_json)
        DataContractsProvider(config_with_catalog).create_catalog_data_contract_test_result(
            CATALOG_ID, CONTRACT_ID, DataContractTestResultPrototype(status="completed")
        )
        url = mock_session_cls.return_value.post.call_args[0][0]
        assert f"/catalogs/{CATALOG_ID}/data_contracts/{CONTRACT_ID}/test_results" in url
        assert "/projects/" not in url

    def test_body_serialised_as_json(self, config_with_catalog, test_result_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "post", test_result_json)
        DataContractsProvider(config_with_catalog).create_catalog_data_contract_test_result(
            CATALOG_ID, CONTRACT_ID, DataContractTestResultPrototype(status="completed")
        )
        body = mock_session_cls.return_value.post.call_args[1]["json"]
        assert body["status"] == "completed"

    def test_error_raises_value_error(self, config_with_catalog, mocker):
        _mock_error_response(mocker, "post", status=400)
        with pytest.raises(ValueError, match=CONTRACT_ID):
            DataContractsProvider(config_with_catalog).create_catalog_data_contract_test_result(
                CATALOG_ID, CONTRACT_ID, DataContractTestResultPrototype()
            )

    def test_empty_catalog_id_raises(self, config_with_catalog):
        with pytest.raises(ValueError, match="catalog_id"):
            DataContractsProvider(config_with_catalog).create_catalog_data_contract_test_result(
                "", CONTRACT_ID, DataContractTestResultPrototype()
            )

    def test_empty_contract_id_raises(self, config_with_catalog):
        with pytest.raises(ValueError, match="data_contract_id"):
            DataContractsProvider(config_with_catalog).create_catalog_data_contract_test_result(
                CATALOG_ID, "", DataContractTestResultPrototype()
            )


class TestUpdateCatalogDataContractTestResult:

    def test_success(self, config_with_catalog, test_result_json, mocker):
        _mock_ok_response(mocker, "put", test_result_json)
        result = DataContractsProvider(config_with_catalog).update_catalog_data_contract_test_result(
            CATALOG_ID, CONTRACT_ID, TEST_RUN_ID, DataContractTestResultPrototype(status="completed")
        )
        assert isinstance(result, DataContractTestResult)
        assert result.id == TEST_RUN_ID

    def test_url_uses_catalogs_path(self, config_with_catalog, test_result_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "put", test_result_json)
        DataContractsProvider(config_with_catalog).update_catalog_data_contract_test_result(
            CATALOG_ID, CONTRACT_ID, TEST_RUN_ID, DataContractTestResultPrototype(status="completed")
        )
        url = mock_session_cls.return_value.put.call_args[0][0]
        assert (
            f"/catalogs/{CATALOG_ID}/data_contracts/{CONTRACT_ID}/test_results/{TEST_RUN_ID}"
            in url
        )
        assert "/projects/" not in url

    def test_body_serialised_as_json(self, config_with_catalog, test_result_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "put", test_result_json)
        DataContractsProvider(config_with_catalog).update_catalog_data_contract_test_result(
            CATALOG_ID, CONTRACT_ID, TEST_RUN_ID, DataContractTestResultPrototype(status="failed")
        )
        body = mock_session_cls.return_value.put.call_args[1]["json"]
        assert body["status"] == "failed"

    def test_not_found_raises_value_error(self, config_with_catalog, mocker):
        _mock_error_response(mocker, "put", status=404)
        with pytest.raises(ValueError, match=TEST_RUN_ID):
            DataContractsProvider(config_with_catalog).update_catalog_data_contract_test_result(
                CATALOG_ID, CONTRACT_ID, TEST_RUN_ID, DataContractTestResultPrototype()
            )

    def test_empty_catalog_id_raises(self, config_with_catalog):
        with pytest.raises(ValueError, match="catalog_id"):
            DataContractsProvider(config_with_catalog).update_catalog_data_contract_test_result(
                "", CONTRACT_ID, TEST_RUN_ID, DataContractTestResultPrototype()
            )

    def test_empty_contract_id_raises(self, config_with_catalog):
        with pytest.raises(ValueError, match="data_contract_id"):
            DataContractsProvider(config_with_catalog).update_catalog_data_contract_test_result(
                CATALOG_ID, "", TEST_RUN_ID, DataContractTestResultPrototype()
            )

    def test_empty_test_run_id_raises(self, config_with_catalog):
        with pytest.raises(ValueError, match="test_run_id"):
            DataContractsProvider(config_with_catalog).update_catalog_data_contract_test_result(
                CATALOG_ID, CONTRACT_ID, "", DataContractTestResultPrototype()
            )


class TestListCatalogDataContractTestResults:

    def test_success(self, config_with_catalog, test_response_collection_json, mocker):
        _mock_ok_response(mocker, "get", test_response_collection_json)
        result = DataContractsProvider(config_with_catalog).list_catalog_data_contract_test_results(
            CATALOG_ID, CONTRACT_ID
        )
        assert isinstance(result, DataContractTestResultCollection)
        assert len(result.test_results) == 1

    def test_single_result_object_wrapped_into_collection(self, config_with_catalog, test_result_json, mocker):
        # For catalogs the server returns only the latest run, as a bare test result.
        _mock_ok_response(mocker, "get", test_result_json)
        result = DataContractsProvider(config_with_catalog).list_catalog_data_contract_test_results(
            CATALOG_ID, CONTRACT_ID
        )
        assert isinstance(result, DataContractTestResultCollection)
        assert len(result.test_results) == 1
        assert result.test_results[0].id == TEST_RUN_ID
        assert result.total_count == 1

    def test_url_uses_catalogs_path(self, config_with_catalog, test_response_collection_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "get", test_response_collection_json)
        DataContractsProvider(config_with_catalog).list_catalog_data_contract_test_results(
            CATALOG_ID, CONTRACT_ID
        )
        url = mock_session_cls.return_value.get.call_args[0][0]
        assert f"/catalogs/{CATALOG_ID}/data_contracts/{CONTRACT_ID}/test_results" in url
        assert "/projects/" not in url

    def test_include_all_details_forwarded(self, config_with_catalog, test_response_collection_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "get", test_response_collection_json)
        DataContractsProvider(config_with_catalog).list_catalog_data_contract_test_results(
            CATALOG_ID, CONTRACT_ID, include_all_details=True
        )
        params = mock_session_cls.return_value.get.call_args[1]["params"]
        assert params["include_all_details"] == "true"

    def test_error_raises_value_error(self, config_with_catalog, mocker):
        _mock_error_response(mocker, "get", status=404)
        with pytest.raises(ValueError, match=CONTRACT_ID):
            DataContractsProvider(config_with_catalog).list_catalog_data_contract_test_results(
                CATALOG_ID, CONTRACT_ID
            )

    def test_empty_catalog_id_raises(self, config_with_catalog):
        with pytest.raises(ValueError, match="catalog_id"):
            DataContractsProvider(config_with_catalog).list_catalog_data_contract_test_results(
                "", CONTRACT_ID
            )

    def test_empty_contract_id_raises(self, config_with_catalog):
        with pytest.raises(ValueError, match="data_contract_id"):
            DataContractsProvider(config_with_catalog).list_catalog_data_contract_test_results(
                CATALOG_ID, ""
            )


class TestGetCatalogDataContractTestResult:

    def test_success(self, config_with_catalog, test_result_json, mocker):
        _mock_ok_response(mocker, "get", test_result_json)
        result = DataContractsProvider(config_with_catalog).get_catalog_data_contract_test_result(
            CATALOG_ID, CONTRACT_ID, TEST_RUN_ID
        )
        assert isinstance(result, DataContractTestResult)
        assert result.id == TEST_RUN_ID

    def test_url_uses_catalogs_path(self, config_with_catalog, test_result_json, mocker):
        mock_session_cls = _mock_ok_response(mocker, "get", test_result_json)
        DataContractsProvider(config_with_catalog).get_catalog_data_contract_test_result(
            CATALOG_ID, CONTRACT_ID, TEST_RUN_ID
        )
        url = mock_session_cls.return_value.get.call_args[0][0]
        assert (
            f"/catalogs/{CATALOG_ID}/data_contracts/{CONTRACT_ID}/test_results/{TEST_RUN_ID}"
            in url
        )
        assert "/projects/" not in url

    def test_not_found_raises_value_error(self, config_with_catalog, mocker):
        _mock_error_response(mocker, "get", status=404)
        with pytest.raises(ValueError, match=TEST_RUN_ID):
            DataContractsProvider(config_with_catalog).get_catalog_data_contract_test_result(
                CATALOG_ID, CONTRACT_ID, TEST_RUN_ID
            )

    def test_empty_catalog_id_raises(self, config_with_catalog):
        with pytest.raises(ValueError, match="catalog_id"):
            DataContractsProvider(config_with_catalog).get_catalog_data_contract_test_result(
                "", CONTRACT_ID, TEST_RUN_ID
            )

    def test_empty_contract_id_raises(self, config_with_catalog):
        with pytest.raises(ValueError, match="data_contract_id"):
            DataContractsProvider(config_with_catalog).get_catalog_data_contract_test_result(
                CATALOG_ID, "", TEST_RUN_ID
            )

    def test_empty_test_run_id_raises(self, config_with_catalog):
        with pytest.raises(ValueError, match="test_run_id"):
            DataContractsProvider(config_with_catalog).get_catalog_data_contract_test_result(
                CATALOG_ID, CONTRACT_ID, ""
            )


class TestDeleteCatalogDataContractTestResults:

    def test_success_no_return(self, config_with_catalog, mocker):
        mock_resp = mocker.Mock()
        mock_resp.ok = True
        mock_resp.status_code = 204
        mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_cls.return_value.delete.return_value = mock_resp
        result = DataContractsProvider(config_with_catalog).delete_catalog_data_contract_test_results(
            CATALOG_ID, CONTRACT_ID
        )
        assert result is None

    def test_url_uses_catalogs_path(self, config_with_catalog, mocker):
        mock_resp = mocker.Mock()
        mock_resp.ok = True
        mock_session_cls = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_cls.return_value.delete.return_value = mock_resp
        DataContractsProvider(config_with_catalog).delete_catalog_data_contract_test_results(
            CATALOG_ID, CONTRACT_ID
        )
        url = mock_session_cls.return_value.delete.call_args[0][0]
        assert f"/catalogs/{CATALOG_ID}/data_contracts/{CONTRACT_ID}/test_results" in url
        assert "/projects/" not in url

    def test_error_raises_value_error(self, config_with_catalog, mocker):
        _mock_error_response(mocker, "delete", status=500)
        with pytest.raises(ValueError, match=CONTRACT_ID):
            DataContractsProvider(config_with_catalog).delete_catalog_data_contract_test_results(
                CATALOG_ID, CONTRACT_ID
            )

    def test_empty_catalog_id_raises(self, config_with_catalog):
        with pytest.raises(ValueError, match="catalog_id"):
            DataContractsProvider(config_with_catalog).delete_catalog_data_contract_test_results(
                "", CONTRACT_ID
            )

    def test_empty_contract_id_raises(self, config_with_catalog):
        with pytest.raises(ValueError, match="data_contract_id"):
            DataContractsProvider(config_with_catalog).delete_catalog_data_contract_test_results(
                CATALOG_ID, ""
            )


# Made with Bob
