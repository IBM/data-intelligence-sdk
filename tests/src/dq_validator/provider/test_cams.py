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
Test suite for CamsProvider module
"""

import pytest
import json
from pathlib import Path
from wxdi.dq_validator.provider.cams import CamsProvider
from wxdi.dq_validator.provider.config import ProviderConfig
from wxdi.dq_validator.provider.data_asset_model import DataAsset


class TestCamsProvider:
    """Test cases for CamsProvider class"""

    @pytest.fixture
    def base_url(self):
        """Base URL for API"""
        return "https://api.example.com"

    @pytest.fixture
    def auth_token(self):
        """Authentication token"""
        return "Bearer test-token-12345"

    @pytest.fixture
    def project_id(self):
        """Project ID"""
        return "72d21c1d-499b-4784-a3c7-6f84507f9a20"

    @pytest.fixture
    def catalog_id(self):
        """Catalog ID"""
        return "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

    @pytest.fixture
    def config_with_project(self, base_url, auth_token, project_id):
        """Create ProviderConfig with project_id"""
        return ProviderConfig(base_url, auth_token, project_id=project_id)

    @pytest.fixture
    def config_with_catalog(self, base_url, auth_token, catalog_id):
        """Create ProviderConfig with catalog_id"""
        return ProviderConfig(base_url, auth_token, catalog_id=catalog_id)

    @pytest.fixture
    def config_without_project_or_catalog(self, base_url, auth_token):
        """Create ProviderConfig without project_id or catalog_id - should fail"""
        return ProviderConfig(base_url, auth_token)

    @pytest.fixture
    def data_asset_json(self):
        """Load the data asset response JSON"""
        json_path = Path(__file__).parent.parent.parent.parent / "data" / "data_asset_response.json"
        with open(json_path, "r") as f:
            return json.load(f)

    @pytest.fixture
    def mock_data_asset(self, data_asset_json):
        """Create DataAsset from JSON"""
        return DataAsset.from_dict(data_asset_json)

    def test_provider_initialization(self, config_with_project):
        """Test CamsProvider initialization"""
        provider = CamsProvider(config_with_project)
        assert provider.config == config_with_project
        assert provider.config.url == "https://api.example.com"
        assert provider.config.auth_token == "Bearer test-token-12345"
        assert provider.config.project_id == "72d21c1d-499b-4784-a3c7-6f84507f9a20"

    def test_get_asset_by_id_success(
        self, config_with_project, data_asset_json, mocker
    ):
        """Test successful asset retrieval"""
        provider = CamsProvider(config_with_project)

        # Mock the session.get call
        mock_response = mocker.Mock()
        mock_response.text = json.dumps(data_asset_json)
        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.return_value = mock_response

        asset = provider.get_asset_by_id("6862f3ba-81f5-4122-8286-62bb4c5d6543")

        assert isinstance(asset, DataAsset)
        assert asset.metadata.asset_id == "6862f3ba-81f5-4122-8286-62bb4c5d6543"
        assert asset.metadata.name == "DEPARTMENT"

    def test_get_asset_by_id_with_project_id(
        self, config_with_project, data_asset_json, mocker
    ):
        """Test that project_id is included in query parameters"""
        provider = CamsProvider(config_with_project)

        mock_response = mocker.Mock()
        mock_response.text = json.dumps(data_asset_json)
        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_instance = mock_session.return_value
        mock_session_instance.get.return_value = mock_response

        # Mock get_url_with_query_params to capture the call
        mock_get_url = mocker.patch(
            "wxdi.dq_validator.provider.cams.get_url_with_query_params"
        )
        mock_get_url.return_value = (
            "https://api.example.com/v2/assets/asset-123?project_id=project-456"
        )

        provider.get_asset_by_id("asset-123")

        # Verify get_url_with_query_params was called with project_id
        mock_get_url.assert_called_once()
        call_args = mock_get_url.call_args
        assert call_args[0][0] == "https://api.example.com/v2/assets/asset-123"
        assert call_args[0][1]["project_id"] == "72d21c1d-499b-4784-a3c7-6f84507f9a20"

    def test_get_asset_by_id_without_project_id(
        self, config_without_project_or_catalog, data_asset_json, mocker
    ):
        """Test asset retrieval without project_id"""
        provider = CamsProvider(config_without_project_or_catalog)

        mock_response = mocker.Mock()
        mock_response.text = json.dumps(data_asset_json)
        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.return_value = mock_response

        mock_get_url = mocker.patch(
            "wxdi.dq_validator.provider.cams.get_url_with_query_params"
        )
        mock_get_url.return_value = "https://api.example.com/v2/assets/asset-123"

        provider.get_asset_by_id("asset-123")

        # Verify get_url_with_query_params was called without project_id
        mock_get_url.assert_called_once()
        call_args = mock_get_url.call_args
        assert "project_id" not in call_args[0][1]

    def test_get_asset_by_id_with_options(
        self, config_with_project, data_asset_json, mocker
    ):
        """Test asset retrieval with additional options"""
        provider = CamsProvider(config_with_project)

        mock_response = mocker.Mock()
        mock_response.text = json.dumps(data_asset_json)
        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.return_value = mock_response

        mock_get_url = mocker.patch(
            "wxdi.dq_validator.provider.cams.get_url_with_query_params"
        )
        mock_get_url.return_value = "https://api.example.com/v2/assets/asset-123?project_id=project-456&include=metadata"

        options = {"include": "metadata"}
        provider.get_asset_by_id("asset-123", options)

        # Verify both project_id and custom options are included
        mock_get_url.assert_called_once()
        call_args = mock_get_url.call_args
        query_params = call_args[0][1]
        assert query_params["project_id"] == "72d21c1d-499b-4784-a3c7-6f84507f9a20"
        assert query_params["include"] == "metadata"

    def test_get_asset_by_id_url_construction(
        self, config_with_project, data_asset_json, mocker
    ):
        """Test correct URL construction"""
        provider = CamsProvider(config_with_project)

        mock_response = mocker.Mock()
        mock_response.text = json.dumps(data_asset_json)
        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_instance = mock_session.return_value
        mock_session_instance.get.return_value = mock_response

        asset_id = "6862f3ba-81f5-4122-8286-62bb4c5d6543"
        provider.get_asset_by_id(asset_id)

        # Verify the session.get was called
        mock_session_instance.get.assert_called_once()
        call_args = mock_session_instance.get.call_args

        # Check that headers were passed
        assert "headers" in call_args[1]
        assert call_args[1]["verify"] is False

    def test_get_asset_by_id_headers(
        self, config_with_project, data_asset_json, mocker
    ):
        """Test that correct headers are sent"""
        provider = CamsProvider(config_with_project)

        mock_response = mocker.Mock()
        mock_response.text = json.dumps(data_asset_json)
        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_instance = mock_session.return_value
        mock_session_instance.get.return_value = mock_response

        # Mock get_request_headers to verify it's called
        mock_get_headers = mocker.patch(
            "wxdi.dq_validator.provider.cams.get_request_headers"
        )
        mock_get_headers.return_value = {
            "Authorization": "Bearer test-token-12345",
            "Content-Type": "application/json",
        }

        provider.get_asset_by_id("asset-123")

        # Verify get_request_headers was called with auth_token
        mock_get_headers.assert_called_once_with("Bearer test-token-12345")

        # Verify session.get was called with the headers
        mock_session_instance.get.assert_called_once()
        call_args = mock_session_instance.get.call_args
        assert call_args[1]["headers"] == {
            "Authorization": "Bearer test-token-12345",
            "Content-Type": "application/json",
        }

    def test_get_asset_by_id_returns_data_asset(
        self, config_with_project, data_asset_json, mocker
    ):
        """Test that DataAsset object is correctly constructed"""
        provider = CamsProvider(config_with_project)

        mock_response = mocker.Mock()
        mock_response.text = json.dumps(data_asset_json)
        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.return_value = mock_response

        asset = provider.get_asset_by_id("6862f3ba-81f5-4122-8286-62bb4c5d6543")

        # Verify DataAsset structure
        assert isinstance(asset, DataAsset)
        assert hasattr(asset, "metadata")
        assert hasattr(asset, "entity")
        assert hasattr(asset.entity, "data_asset")
        assert hasattr(asset.entity, "column_info")

        # Verify specific data
        assert len(asset.entity.data_asset.columns) == 5
        assert "DEPTNO" in asset.entity.column_info
        assert "MGRNO" in asset.entity.column_info

    def test_get_asset_by_id_json_parsing(self, config_with_project, mocker):
        """Test JSON parsing of response"""
        provider = CamsProvider(config_with_project)

        # Create a minimal valid JSON response
        minimal_json = {
            "metadata": {
                "project_id": "test-project",
                "name": "TEST_TABLE",
                "tags": [],
                "asset_type": "data_asset",
                "catalog_id": "test-catalog",
                "created": 1234567890,
                "created_at": "2024-01-01T00:00:00Z",
                "owner_id": "owner-123",
                "size": 0,
                "version": 1,
                "asset_state": "available",
                "asset_attributes": [],
                "asset_id": "asset-123",
                "asset_category": "USER",
                "creator_id": "creator-123",
            },
            "entity": {
                "data_asset": {
                    "columns": [],
                    "dataset": True,
                    "mime_type": "application/x-ibm-rel-table",
                    "properties": [],
                },
                "column_info": {},
                "data_profile": {"attribute_classes": []},
                "key_analyses": {
                    "fk_defined": 0,
                    "pk_defined": 0,
                    "fk_assigned": 0,
                    "pk_assigned": 0,
                    "fk_suggested": 0,
                    "pk_suggested": 0,
                    "primary_keys": [],
                    "fk_defined_as_pk": 0,
                    "overlap_assigned": 0,
                    "fk_assigned_as_pk": 0,
                    "overlap_suggested": 0,
                    "fk_suggested_as_pk": 0,
                    "key_analysis_area_id": "area-123",
                },
                "discovered_asset": {"extended_metadata": []},
                "dataview_visualization": {"jobs": {}},
                "metadata_enrichment_info": {"MDE_instrumented": False},
                "asset_data_quality_constraint": {
                    "asset_checks": [],
                    "rejected_checks": [],
                    "suggested_checks": [],
                },
                "metadata_enrichment_area_info": {
                    "job_id": "job-123",
                    "area_id": "area-123",
                    "added_date": 1234567890,
                    "job_run_id": "run-123",
                    "last_enrichment_status": "finished",
                    "last_enrichment_timestamp": 1234567890,
                },
            },
            "href": "/v2/assets/asset-123",
        }

        mock_response = mocker.Mock()
        mock_response.text = json.dumps(minimal_json)
        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.return_value = mock_response

        asset = provider.get_asset_by_id("asset-123")

        assert isinstance(asset, DataAsset)
        assert asset.metadata.name == "TEST_TABLE"
        assert asset.metadata.asset_id == "asset-123"

    def test_get_asset_by_id_http_error(self, config_with_project, mocker):
        """Test handling of HTTP errors (404, 500, etc.)"""
        provider = CamsProvider(config_with_project)

        # Mock a 404 response
        mock_response = mocker.Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_response.text = json.dumps({"error": "Asset not found"})

        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.return_value = mock_response

        # The implementation checks response.ok and raises ValueError
        with pytest.raises(ValueError) as exc_info:
            provider.get_asset_by_id("non-existent-asset")

        # Verify the error message
        assert "Could not find data asset" in str(exc_info.value)
        assert "non-existent-asset" in str(exc_info.value)
        assert config_with_project.project_id in str(exc_info.value)

    def test_get_asset_by_id_invalid_json(self, config_with_project, mocker):
        """Test handling of invalid JSON response"""
        provider = CamsProvider(config_with_project)

        # Mock a response with invalid JSON
        mock_response = mocker.Mock()
        mock_response.text = "This is not valid JSON"

        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.return_value = mock_response

        # Should raise JSONDecodeError
        with pytest.raises(json.JSONDecodeError):
            provider.get_asset_by_id("asset-123")

    def test_get_asset_by_id_malformed_response(self, config_with_project, mocker):
        """Test handling of malformed response (valid JSON but invalid structure)"""
        provider = CamsProvider(config_with_project)

        # Mock a response with valid JSON but missing required fields
        malformed_json = {"some_field": "some_value"}
        mock_response = mocker.Mock()
        mock_response.text = json.dumps(malformed_json)

        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.return_value = mock_response

        # Should raise ValidationError from Pydantic
        with pytest.raises(Exception):  # Pydantic ValidationError
            provider.get_asset_by_id("asset-123")

    def test_get_asset_by_id_network_error(self, config_with_project, mocker):
        """Test handling of network errors"""
        provider = CamsProvider(config_with_project)

        # Mock a network error
        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.side_effect = ConnectionError("Network error")

        # Should raise ConnectionError
        with pytest.raises(ConnectionError):
            provider.get_asset_by_id("asset-123")

    def test_get_asset_by_id_timeout(self, config_with_project, mocker):
        """Test handling of timeout errors"""
        provider = CamsProvider(config_with_project)

        # Mock a timeout error
        from requests.exceptions import Timeout

        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.side_effect = Timeout("Request timeout")

        # Should raise Timeout
        with pytest.raises(Timeout):
            provider.get_asset_by_id("asset-123")

    def test_config_with_catalog_id(self, config_with_catalog, catalog_id):
        """Test ProviderConfig initialization with catalog_id"""
        provider = CamsProvider(config_with_catalog)
        assert provider.config.catalog_id == catalog_id
        assert provider.config.project_id is None

    def test_get_asset_by_id_with_catalog_id(
        self, config_with_catalog, data_asset_json, mocker
    ):
        """Test that catalog_id is included in query parameters"""
        provider = CamsProvider(config_with_catalog)

        mock_response = mocker.Mock()
        mock_response.text = json.dumps(data_asset_json)
        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session_instance = mock_session.return_value
        mock_session_instance.get.return_value = mock_response

        # Mock get_url_with_query_params to capture the call
        mock_get_url = mocker.patch(
            "wxdi.dq_validator.provider.cams.get_url_with_query_params"
        )
        mock_get_url.return_value = (
            "https://api.example.com/v2/assets/asset-123?catalog_id=catalog-456"
        )

        provider.get_asset_by_id("asset-123")

        # Verify get_url_with_query_params was called with catalog_id
        mock_get_url.assert_called_once()
        call_args = mock_get_url.call_args
        assert call_args[0][0] == "https://api.example.com/v2/assets/asset-123"
        assert call_args[0][1]["catalog_id"] == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        assert "project_id" not in call_args[0][1]

    def test_get_asset_by_id_catalog_error_message(self, config_with_catalog, mocker):
        """Test error message includes catalog_id when using catalog"""
        provider = CamsProvider(config_with_catalog)

        # Mock a 404 response
        mock_response = mocker.Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_response.text = json.dumps({"error": "Asset not found"})

        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.return_value = mock_response

        with pytest.raises(ValueError) as exc_info:
            provider.get_asset_by_id("non-existent-asset")

        # Verify the error message includes catalog context
        assert "Could not find data asset" in str(exc_info.value)
        assert "non-existent-asset" in str(exc_info.value)
        assert "catalog" in str(exc_info.value)
        assert config_with_catalog.catalog_id in str(exc_info.value)

    def test_get_asset_by_id_with_catalog_and_options(
        self, config_with_catalog, data_asset_json, mocker
    ):
        """Test asset retrieval with catalog_id and additional options"""
        # Mock a timeout error
        from requests.exceptions import Timeout

        provider = CamsProvider(config_with_catalog)

        mock_response = mocker.Mock()
        mock_response.text = json.dumps(data_asset_json)
        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.return_value = mock_response
        mock_session.return_value.get.side_effect = [mocker.DEFAULT, Timeout("Request timeout")]

        mock_get_url = mocker.patch(
            "wxdi.dq_validator.provider.cams.get_url_with_query_params"
        )
        mock_get_url.return_value = "https://api.example.com/v2/assets/asset-123?catalog_id=catalog-456&include=metadata"

        options = {"include": "metadata"}
        provider.get_asset_by_id("asset-123", options)

        # Verify both catalog_id and custom options are included
        mock_get_url.assert_called_once()
        call_args = mock_get_url.call_args
        query_params = call_args[0][1]
        assert query_params["catalog_id"] == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        assert query_params["include"] == "metadata"
        assert "project_id" not in query_params

        # Should raise Timeout with side effect set above
        with pytest.raises(Timeout):
            provider.get_asset_by_id("asset-123")


# Made with Bob
