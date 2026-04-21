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
Comprehensive unit tests for the GlossaryProvider module.

This test suite validates all aspects of the GlossaryProvider including:
    - Configuration validation
    - Fetching published artifacts by ID
    - Fetching terms by version ID
    - Response parsing and model creation
    - Error handling (HTTP errors, network errors, invalid responses)
    - Query parameter handling

Test Coverage:
    - TestProviderConfig: Configuration class validation
    - TestGlossaryProvider: Provider functionality
    - TestGlossaryTermModel: Response model parsing
    - TestUtilityFunctions: Helper function validation

Running Tests:
    Run all glossary tests:
    $ pytest tests/src/provider/test_glossary.py -v

    Run specific test:
    $ pytest tests/src/provider/test_glossary.py::TestGlossaryProvider::test_get_published_artifact_success -v

    Run with coverage:
    $ pytest tests/src/provider/test_glossary.py --cov=dq_validator.provider --cov-report=html

Note:
    Tests use pytest-mock to avoid actual network calls.
    Test data is loaded from tests/data/ directory.

See Also:
    - src/dq_validator/provider/glossary.py: GlossaryProvider implementation
    - src/dq_validator/provider/response_model.py: Response models
"""

import json
import pytest
from pathlib import Path
from wxdi.dq_validator.provider.glossary import GlossaryProvider
from wxdi.dq_validator.provider.config import ProviderConfig
from wxdi.dq_validator.provider.response_model import GlossaryTerm
from wxdi.dq_validator.utils import get_request_headers, get_url_with_query_params


# Test constants
MOCK_URL = "https://test.example.com"
MOCK_AUTH_TOKEN = "Bearer test-token-123"
MOCK_PROJECT_ID = "test-project-id"
MOCK_TERM_ID = "30d1b847-0aa9-4840-a182-dd157fe977a0"
MOCK_VERSION_ID = "bdeef8cc-d9ab-4822-b3df-cef82b4de538_0"

# Get test data directory
TEST_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


def load_test_data(filename: str) -> str:
    """Load test data from JSON file"""
    file_path = TEST_DATA_DIR / filename
    with open(file_path, "r") as f:
        return f.read()


# ============================================================================
# ProviderConfig Tests
# ============================================================================


class TestProviderConfig:
    """Test ProviderConfig class"""

    def test_config_with_all_parameters(self):
        """Test creating config with all parameters"""
        config = ProviderConfig(
            url=MOCK_URL, auth_token=MOCK_AUTH_TOKEN, project_id=MOCK_PROJECT_ID
        )
        assert config.url == MOCK_URL
        assert config.auth_token == MOCK_AUTH_TOKEN
        assert config.project_id == MOCK_PROJECT_ID

    def test_config_without_project_id(self):
        """Test creating config without project_id"""
        config = ProviderConfig(url=MOCK_URL, auth_token=MOCK_AUTH_TOKEN)
        assert config.url == MOCK_URL
        assert config.auth_token == MOCK_AUTH_TOKEN
        assert config.project_id is None

    def test_config_attributes_accessible(self):
        """Test that config attributes are accessible"""
        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN, MOCK_PROJECT_ID)
        assert hasattr(config, "url")
        assert hasattr(config, "auth_token")
        assert hasattr(config, "project_id")


# ============================================================================
# Utility Functions Tests
# ============================================================================


class TestUtilityFunctions:
    """Test utility functions"""

    def test_get_request_headers_with_auth(self):
        """Test getting request headers with auth token"""
        headers = get_request_headers(MOCK_AUTH_TOKEN)
        assert headers["Authorization"] == MOCK_AUTH_TOKEN
        assert headers["Content-Type"] == "application/json"

    def test_get_request_headers_custom_content_type(self):
        """Test getting request headers with custom content type"""
        headers = get_request_headers(MOCK_AUTH_TOKEN, "text/plain")
        assert headers["Authorization"] == MOCK_AUTH_TOKEN
        assert headers["Content-Type"] == "text/plain"

    def test_get_request_headers_no_auth(self):
        """Test getting request headers without auth token"""
        headers = get_request_headers("")
        assert "Authorization" not in headers
        assert headers["Content-Type"] == "application/json"

    def test_get_url_with_query_params(self):
        """Test adding query parameters to URL"""
        url = "https://example.com/api"
        params = {"key1": "value1", "key2": "value2"}
        result = get_url_with_query_params(url, params)
        assert "key1=value1" in result
        assert "key2=value2" in result
        assert result.startswith(url)

    def test_get_url_without_query_params(self):
        """Test URL without query parameters"""
        url = "https://example.com/api"
        result = get_url_with_query_params(url, None)
        assert result == url


# ============================================================================
# GlossaryProvider Tests
# ============================================================================


class TestGlossaryProvider:
    """Test GlossaryProvider class"""

    def test_provider_initialization(self):
        """Test provider initialization with config"""
        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)
        assert provider.config == config
        assert provider.config.url == MOCK_URL
        assert provider.config.auth_token == MOCK_AUTH_TOKEN

    def test_get_published_artifact_success(self, mocker):
        """Test successful retrieval of published artifact"""
        # Load test data
        test_data = load_test_data("term_latest_version.json")

        # Mock response
        mock_response = mocker.MagicMock()
        mock_response.text = test_data
        mock_response.status_code = 200

        # Mock Session.get
        mock_session = mocker.MagicMock()
        mock_session.get.return_value = mock_response
        mocker.patch(
            "wxdi.dq_validator.provider.base_provider.Session", return_value=mock_session
        )

        # Create provider and call method
        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)
        result = provider.get_published_artifact_by_id(MOCK_TERM_ID)

        # Verify
        assert isinstance(result, GlossaryTerm)
        assert result.metadata.artifact_id == MOCK_TERM_ID
        assert result.metadata.name == "mango"
        assert result.metadata.state == "PUBLISHED"

        # Verify URL was constructed correctly
        expected_url = (
            f"{MOCK_URL}/v3/governance_artifact_types/glossary_term/{MOCK_TERM_ID}"
        )
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        assert call_args[0][0] == expected_url

    def test_get_published_artifact_with_options(self, mocker):
        """Test retrieval with query options"""
        test_data = load_test_data("term_latest_version.json")

        mock_response = mocker.MagicMock()
        mock_response.text = test_data
        mock_response.status_code = 200

        mock_session = mocker.MagicMock()
        mock_session.get.return_value = mock_response
        mocker.patch(
            "wxdi.dq_validator.provider.base_provider.Session", return_value=mock_session
        )

        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)

        options = {"include": "metadata", "limit": "10"}
        result = provider.get_published_artifact_by_id(MOCK_TERM_ID, options)

        # Verify result
        assert isinstance(result, GlossaryTerm)

        # Verify URL includes query parameters
        call_args = mock_session.get.call_args
        called_url = call_args[0][0]
        assert "include=metadata" in called_url
        assert "limit=10" in called_url

    def test_get_term_by_version_id_success(self, mocker):
        """Test successful retrieval of term by version ID"""
        # Load test data with full details
        test_data = load_test_data("term_response.json")

        mock_response = mocker.MagicMock()
        mock_response.text = test_data
        mock_response.status_code = 200

        mock_session = mocker.MagicMock()
        mock_session.get.return_value = mock_response
        mocker.patch(
            "wxdi.dq_validator.provider.base_provider.Session", return_value=mock_session
        )

        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)
        result = provider.get_term_by_version_id(MOCK_TERM_ID, MOCK_VERSION_ID)

        # Verify
        assert isinstance(result, GlossaryTerm)
        assert result.metadata.artifact_id == MOCK_TERM_ID
        assert result.metadata.version_id == MOCK_VERSION_ID
        assert result.metadata.name == "mango"
        assert result.metadata.effective_start_date is not None

        # Verify extended attributes
        assert result.entity is not None
        assert len(result.entity.extended_attribute_groups.dq_constraints) == 2

        # Verify URL was constructed correctly
        expected_url = (
            f"{MOCK_URL}/v3/glossary_terms/{MOCK_TERM_ID}/versions/{MOCK_VERSION_ID}"
        )
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        assert call_args[0][0] == expected_url

    def test_get_term_by_version_id_with_options(self, mocker):
        """Test retrieval by version ID with query options"""
        test_data = load_test_data("term_response.json")

        mock_response = mocker.MagicMock()
        mock_response.text = test_data
        mock_response.status_code = 200

        mock_session = mocker.MagicMock()
        mock_session.get.return_value = mock_response
        mocker.patch(
            "wxdi.dq_validator.provider.base_provider.Session", return_value=mock_session
        )

        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)

        options = {"included_extended_attribute_groups": "dq_constraints"}
        result = provider.get_term_by_version_id(MOCK_TERM_ID, MOCK_VERSION_ID, options)

        # Verify result
        assert isinstance(result, GlossaryTerm)

        # Verify URL includes query parameters
        call_args = mock_session.get.call_args
        called_url = call_args[0][0]
        assert "included_extended_attribute_groups=dq_constraints" in called_url

    def test_get_term_by_version_id_draft(self, mocker):
        """Test successful retrieval of term by version ID"""
        # Load test data with full details
        test_data = load_test_data("term_draft.json")

        mock_response = mocker.MagicMock()
        mock_response.text = test_data
        mock_response.status_code = 200

        mock_session = mocker.MagicMock()
        mock_session.get.return_value = mock_response
        mocker.patch(
            "wxdi.dq_validator.provider.base_provider.Session", return_value=mock_session
        )

        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)
        result = provider.get_term_by_version_id(MOCK_TERM_ID, MOCK_VERSION_ID)

        # Verify
        assert isinstance(result, GlossaryTerm)
        assert result.metadata.artifact_id == MOCK_TERM_ID
        assert result.metadata.version_id == MOCK_VERSION_ID
        assert result.metadata.name == "mango"
        assert result.metadata.effective_start_date is None
        assert result.metadata.draft_mode is not None
        assert result.metadata.workflow_id is not None
        assert result.metadata.workflow_state is not None
        assert result.metadata.state == "DRAFT_HISTORY"

        # Verify extended attributes
        assert result.entity.extended_attribute_groups is None

        # Verify URL was constructed correctly
        expected_url = (
            f"{MOCK_URL}/v3/glossary_terms/{MOCK_TERM_ID}/versions/{MOCK_VERSION_ID}"
        )
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        assert call_args[0][0] == expected_url

    def test_request_headers_included(self, mocker):
        """Test that authorization headers are included in requests"""
        test_data = load_test_data("term_latest_version.json")

        mock_response = mocker.MagicMock()
        mock_response.text = test_data

        mock_session = mocker.MagicMock()
        mock_session.get.return_value = mock_response
        mocker.patch(
            "wxdi.dq_validator.provider.base_provider.Session", return_value=mock_session
        )

        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)
        provider.get_published_artifact_by_id(MOCK_TERM_ID)

        # Verify headers were passed as keyword argument
        call_args = mock_session.get.call_args
        assert "headers" in call_args.kwargs
        headers = call_args.kwargs["headers"]
        assert "Authorization" in headers
        assert headers["Authorization"] == MOCK_AUTH_TOKEN


# ============================================================================
# GlossaryTerm Model Tests
# ============================================================================


class TestGlossaryTermModel:
    """Test GlossaryTerm response model"""

    def test_parse_latest_version_response(self):
        """Test parsing latest version response"""
        test_data = load_test_data("term_latest_version.json")
        term = GlossaryTerm.from_json(test_data)

        assert term.metadata.artifact_id == MOCK_TERM_ID
        assert term.metadata.version_id == MOCK_VERSION_ID
        assert term.metadata.name == "mango"
        assert term.metadata.state == "PUBLISHED"

    def test_parse_full_term_response(self):
        """Test parsing full term response with DQ constraints"""
        test_data = load_test_data("term_response.json")
        term = GlossaryTerm.from_json(test_data)

        # Verify metadata
        assert term.metadata.artifact_id == MOCK_TERM_ID
        assert term.metadata.name == "mango"

        # Verify DQ constraints
        dq_constraints = term.entity.extended_attribute_groups.dq_constraints
        assert len(dq_constraints) == 2

        # First constraint: data_type
        first_constraint = dq_constraints[0]
        assert first_constraint.metadata.type == "data_type"
        assert len(first_constraint.check) == 2

        # Second constraint: length
        second_constraint = dq_constraints[1]
        assert second_constraint.metadata.type == "length"
        assert len(second_constraint.check) == 2

    def test_model_to_dict(self):
        """Test converting model to dictionary"""
        test_data = load_test_data("term_latest_version.json")
        term = GlossaryTerm.from_json(test_data)

        result_dict = term.to_dict()
        assert isinstance(result_dict, dict)
        assert "metadata" in result_dict
        assert "entity" in result_dict
        assert result_dict["metadata"]["artifact_id"] == MOCK_TERM_ID

    def test_model_to_json(self):
        """Test converting model to JSON string"""
        test_data = load_test_data("term_latest_version.json")
        term = GlossaryTerm.from_json(test_data)

        result_json = term.to_json()
        assert isinstance(result_json, str)

        # Verify it's valid JSON
        parsed = json.loads(result_json)
        assert parsed["metadata"]["artifact_id"] == MOCK_TERM_ID

    def test_model_from_dict(self):
        """Test creating model from dictionary"""
        test_data = load_test_data("term_latest_version.json")
        data_dict = json.loads(test_data)

        term = GlossaryTerm.from_dict(data_dict)
        assert isinstance(term, GlossaryTerm)
        assert term.metadata.artifact_id == MOCK_TERM_ID

    def test_dq_constraint_check_values(self):
        """Test extracting check constraint values"""
        test_data = load_test_data("term_response.json")
        term = GlossaryTerm.from_json(test_data)

        # Get first constraint (data_type)
        first_constraint = term.entity.extended_attribute_groups.dq_constraints[0]

        # Verify check values
        checks = {check.name: check for check in first_constraint.check}
        assert "data_type" in checks
        assert checks["data_type"].value == "STRING"
        assert "length" in checks
        assert checks["length"].numeric_value == 80

        # Get second constraint (length)
        second_constraint = term.entity.extended_attribute_groups.dq_constraints[1]
        checks = {check.name: check for check in second_constraint.check}
        assert "min" in checks
        assert checks["min"].numeric_value == 3
        assert "max" in checks
        assert checks["max"].numeric_value == 80


# ============================================================================
# Integration Tests
# ============================================================================


class TestGlossaryProviderIntegration:
    """Integration tests for GlossaryProvider workflow"""

    def test_full_workflow_get_latest_then_version(self, mocker):
        """Test complete workflow: get latest version, then get full details"""
        # Load test data
        latest_data = load_test_data("term_latest_version.json")
        full_data = load_test_data("term_response.json")

        # Mock responses
        mock_response_latest = mocker.MagicMock()
        mock_response_latest.text = latest_data

        mock_response_full = mocker.MagicMock()
        mock_response_full.text = full_data

        # Mock Session to return different responses
        mock_session = mocker.MagicMock()
        mock_session.get.side_effect = [mock_response_latest, mock_response_full]
        mocker.patch(
            "wxdi.dq_validator.provider.base_provider.Session", return_value=mock_session
        )

        # Create provider
        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)

        # Step 1: Get latest version
        latest_term = provider.get_published_artifact_by_id(MOCK_TERM_ID)
        assert latest_term.metadata.version_id == MOCK_VERSION_ID

        # Step 2: Get full details using version_id
        full_term = provider.get_term_by_version_id(
            MOCK_TERM_ID, latest_term.metadata.version_id
        )

        # Verify full details
        assert full_term.metadata.artifact_id == MOCK_TERM_ID
        assert len(full_term.entity.extended_attribute_groups.dq_constraints) == 2


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestGlossaryProviderErrorHandling:
    """Test error handling in GlossaryProvider"""

    def test_get_published_artifact_http_error(self, mocker):
        """Test handling of HTTP errors (404, 500, etc.) in get_published_artifact_by_id"""
        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)

        # Mock a 404 response
        mock_response = mocker.Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_response.text = json.dumps({"error": "Artifact not found"})

        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.return_value = mock_response

        # The implementation checks response.ok and raises ValueError
        with pytest.raises(ValueError) as exc_info:
            provider.get_published_artifact_by_id("non-existent-artifact")

        # Verify the error message contains artifact_id
        assert "Cannot get artifact" in str(exc_info.value)
        assert "non-existent-artifact" in str(exc_info.value)

    def test_get_term_by_version_id_http_error(self, mocker):
        """Test handling of HTTP errors in get_term_by_version_id"""
        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)

        # Mock a 404 response
        mock_response = mocker.Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_response.text = json.dumps({"error": "Version not found"})

        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.return_value = mock_response

        # The implementation checks response.ok and raises ValueError
        with pytest.raises(ValueError) as exc_info:
            provider.get_term_by_version_id("artifact-123", "version-456")

        # Verify the error message contains both artifact_id and version_id
        assert "Cannot get artifact" in str(exc_info.value)
        assert "artifact-123" in str(exc_info.value)
        assert "version-456" in str(exc_info.value)

    def test_get_published_artifact_invalid_json(self, mocker):
        """Test handling of invalid JSON response in get_published_artifact_by_id"""
        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)

        # Mock a response with invalid JSON
        mock_response = mocker.Mock()
        mock_response.ok = True
        mock_response.text = "This is not valid JSON"

        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.return_value = mock_response

        # Should raise JSONDecodeError
        with pytest.raises(json.JSONDecodeError):
            provider.get_published_artifact_by_id(MOCK_TERM_ID)

    def test_get_term_by_version_id_invalid_json(self, mocker):
        """Test handling of invalid JSON response in get_term_by_version_id"""
        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)

        # Mock a response with invalid JSON
        mock_response = mocker.Mock()
        mock_response.ok = True
        mock_response.text = "This is not valid JSON"

        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.return_value = mock_response

        # Should raise JSONDecodeError
        with pytest.raises(json.JSONDecodeError):
            provider.get_term_by_version_id(MOCK_TERM_ID, MOCK_VERSION_ID)

    def test_get_published_artifact_malformed_response(self, mocker):
        """Test handling of malformed response in get_published_artifact_by_id"""
        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)

        # Mock a response with valid JSON but missing required fields
        malformed_json = {"some_field": "some_value"}
        mock_response = mocker.Mock()
        mock_response.ok = True
        mock_response.text = json.dumps(malformed_json)

        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.return_value = mock_response

        # Should raise ValidationError from Pydantic
        with pytest.raises(Exception):  # Pydantic ValidationError
            provider.get_published_artifact_by_id(MOCK_TERM_ID)

    def test_get_term_by_version_id_malformed_response(self, mocker):
        """Test handling of malformed response in get_term_by_version_id"""
        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)

        # Mock a response with valid JSON but missing required fields
        malformed_json = {"some_field": "some_value"}
        mock_response = mocker.Mock()
        mock_response.ok = True
        mock_response.text = json.dumps(malformed_json)

        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.return_value = mock_response

        # Should raise ValidationError from Pydantic
        with pytest.raises(Exception):  # Pydantic ValidationError
            provider.get_term_by_version_id(MOCK_TERM_ID, MOCK_VERSION_ID)

    def test_get_published_artifact_network_error(self, mocker):
        """Test handling of network errors in get_published_artifact_by_id"""
        from requests.exceptions import ConnectionError

        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)

        # Mock a network error
        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.side_effect = ConnectionError(
            "Network unreachable"
        )

        # Should raise ConnectionError
        with pytest.raises(ConnectionError):
            provider.get_published_artifact_by_id(MOCK_TERM_ID)

    def test_get_term_by_version_id_network_error(self, mocker):
        """Test handling of network errors in get_term_by_version_id"""
        from requests.exceptions import ConnectionError

        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)

        # Mock a network error
        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.side_effect = ConnectionError(
            "Network unreachable"
        )

        # Should raise ConnectionError
        with pytest.raises(ConnectionError):
            provider.get_term_by_version_id(MOCK_TERM_ID, MOCK_VERSION_ID)

    def test_get_published_artifact_timeout(self, mocker):
        """Test handling of timeout errors in get_published_artifact_by_id"""
        from requests.exceptions import Timeout

        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)

        # Mock a timeout error
        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.side_effect = Timeout("Request timed out")

        # Should raise Timeout
        with pytest.raises(Timeout):
            provider.get_published_artifact_by_id(MOCK_TERM_ID)

    def test_get_term_by_version_id_timeout(self, mocker):
        """Test handling of timeout errors in get_term_by_version_id"""
        from requests.exceptions import Timeout

        config = ProviderConfig(MOCK_URL, MOCK_AUTH_TOKEN)
        provider = GlossaryProvider(config)

        # Mock a timeout error
        mock_session = mocker.patch("wxdi.dq_validator.provider.base_provider.Session")
        mock_session.return_value.get.side_effect = Timeout("Request timed out")

        # Should raise Timeout
        with pytest.raises(Timeout):
            provider.get_term_by_version_id(MOCK_TERM_ID, MOCK_VERSION_ID)


# Made with Bob
