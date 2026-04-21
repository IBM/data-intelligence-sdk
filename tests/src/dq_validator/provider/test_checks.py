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

import pytest
from unittest.mock import Mock, patch
import json

from wxdi.dq_validator.provider import ProviderConfig, ChecksProvider


class TestChecksProvider:
    """Test suite for ChecksProvider class."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return ProviderConfig(
            url="https://test-instance.com",
            auth_token="Bearer test-token"
        )
    
    @pytest.fixture
    def provider(self, config):
        """Create a test ChecksProvider instance."""
        with patch('wxdi.dq_validator.provider.base_provider.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            provider = ChecksProvider(config)
            yield provider
    
    # ==================== create_check Tests ====================
    
    def test_create_check_with_project_id(self, provider):
        """Test creating a check with project_id - returns check ID only."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        expected_body = {
            "id": "check-123",
            "name": "check_uniqueness_of_id",
            "type": "uniqueness",
            "dimension": {
                "id": "dimension-456"
            },
            "native_id": "asset-789/check-123"
        }
        mock_response.text = json.dumps(expected_body)
        provider.session.post.return_value = mock_response
        
        # Execute
        result = provider.create_check(
            name="check_uniqueness_of_id",
            dimension_id="dimension-456",
            native_id="asset-789/check-123",
            check_type="uniqueness",
            project_id="project-123"
        )
        
        # Verify - should return only check ID (string)
        assert isinstance(result, str)
        assert result == "check-123"
        
        # Verify the API call
        provider.session.post.assert_called_once()
        call_args = provider.session.post.call_args
        
        # Check URL
        assert "https://test-instance.com/data_quality/v4/checks" in call_args[0][0]
        assert "project_id=project-123" in call_args[0][0]
        
        # Check headers
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["Content-Type"] == "application/json"
        
        # Check payload
        payload = json.loads(call_args[1]["data"])
        assert payload["name"] == "check_uniqueness_of_id"
        assert payload["type"] == "uniqueness"
        assert payload["dimension"]["id"] == "dimension-456"
        assert payload["native_id"] == "asset-789/check-123"
        assert json.loads(payload["details"])["origin"] == "SDK"
    
    def test_create_check_with_catalog_id(self, provider):
        """Test creating a check with catalog_id"""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        expected_body = {
            "id": "check-456",
            "name": "check_completeness",
            "type": "completeness"
        }
        mock_response.text = json.dumps(expected_body)
        provider.session.post.return_value = mock_response
        
        # Execute
        result = provider.create_check(
            name="check_completeness",
            dimension_id="dimension-789",
            native_id="asset-111/check-456",
            catalog_id="catalog-999"
        )
        
        # Verify - should return only check ID (string)
        assert isinstance(result, str)
        assert result == "check-456"
        
        # Verify the API call
        call_args = provider.session.post.call_args
        
        # Check URL contains catalog_id
        assert "catalog_id=catalog-999" in call_args[0][0]
        assert "project_id" not in call_args[0][0]
    
    def test_create_check_without_check_type(self, provider):
        """Test creating a check without check_type (should default to name) - returns check ID only."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        expected_body = {
            "id": "check-789",
            "name": "format_check",
            "type": "format_check"
        }
        mock_response.text = json.dumps(expected_body)
        provider.session.post.return_value = mock_response
        
        # Execute
        result = provider.create_check(
            name="format_check",
            dimension_id="dimension-111",
            native_id="asset-222/check-789",
            project_id="project-123"
        )
        
        # Verify - should return only check ID (string)
        assert isinstance(result, str)
        assert result == "check-789"
        
        # Verify the API call
        call_args = provider.session.post.call_args
        payload = json.loads(call_args[1]["data"])
        
        # Check that type defaults to name
        assert payload["type"] == "format_check"
        assert payload["name"] == "format_check"
    
    def test_create_check_missing_both_ids(self, provider):
        """Test creating a check without project_id or catalog_id."""
        with pytest.raises(ValueError) as exc_info:
            provider.create_check(
                name="check_test",
                dimension_id="dimension-123",
                native_id="asset-456/check-789"
            )
        
        assert "Either project_id or catalog_id must be provided" in str(exc_info.value)
    
    def test_create_check_both_ids_provided(self, provider):
        """Test creating a check with both project_id and catalog_id."""
        with pytest.raises(ValueError) as exc_info:
            provider.create_check(
                name="check_test",
                dimension_id="dimension-123",
                native_id="asset-456/check-789",
                project_id="project-123",
                catalog_id="catalog-456"
            )
        
        assert "Only one of project_id or catalog_id should be provided" in str(exc_info.value)
    
    def test_create_check_api_failure(self, provider):
        """Test failed check creation."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        provider.session.post.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider.create_check(
                name="check_test",
                dimension_id="dimension-123",
                native_id="asset-456/check-789",
                project_id="project-123"
            )
        
        assert "Failed to create check" in str(exc_info.value)
        assert "400" in str(exc_info.value)
        assert "Bad request" in str(exc_info.value)
    
    def test_create_check_missing_id_in_response(self, provider):
        """Test check creation with missing id in response."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "name": "check_test",
            "type": "test"
            # Missing "id" field
        })
        provider.session.post.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider.create_check(
                name="check_test",
                dimension_id="dimension-123",
                native_id="asset-456/check-789",
                project_id="project-123"
            )
        
        assert "Check ID not found in response" in str(exc_info.value)
    
    def test_create_check_with_special_characters_in_native_id(self, provider):
        """Test creating a check with special characters in native_id - returns check ID only."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        expected_body = {
            "id": "check-special-123",
            "name": "check_format",
            "native_id": "asset-abc-123/check-xyz-456"
        }
        mock_response.text = json.dumps(expected_body)
        provider.session.post.return_value = mock_response
        
        # Execute
        result = provider.create_check(
            name="check_format",
            dimension_id="dimension-999",
            native_id="asset-abc-123/check-xyz-456",
            project_id="project-123"
        )
        
        # Verify - should return only check ID (string)
        assert isinstance(result, str)
        assert result == "check-special-123"
        
        # Verify the payload contains the special native_id
        call_args = provider.session.post.call_args
        payload = json.loads(call_args[1]["data"])
        assert payload["native_id"] == "asset-abc-123/check-xyz-456"
    
    def test_create_check_with_parent_check_id(self, provider):
        """Test creating a check with parent_check_id."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        expected_body = {
            "id": "child-check-123",
            "name": "check_format_email",
            "type": "format",
            "parent": {
                "id": "parent-check-456"
            }
        }
        mock_response.text = json.dumps(expected_body)
        provider.session.post.return_value = mock_response
        
        # Execute
        result = provider.create_check(
            name="check_format_email",
            dimension_id="dimension-789",
            native_id="asset-111/email/format",
            check_type="format",
            project_id="project-123",
            parent_check_id="parent-check-456"
        )
        
        # Verify - should return only check ID (string)
        assert isinstance(result, str)
        assert result == "child-check-123"
        
        # Verify the API call includes parent in payload
        provider.session.post.assert_called_once()
        call_args = provider.session.post.call_args
        
        # Check payload includes parent
        payload = json.loads(call_args[1]["data"])
        assert "parent" in payload
        assert payload["parent"]["id"] == "parent-check-456"
        assert payload["native_id"] == "asset-111/email/format"
    
    # ==================== _create_check_full Tests ====================
    
    def test_create_check_full_with_project_id(self, provider):
        """Test _create_check_full returns full check body with project_id."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        expected_body = {
            "id": "check-full-123",
            "name": "check_uniqueness_of_id",
            "type": "uniqueness",
            "native_id": "asset-456/check-789",
            "dimension": {
                "id": "dimension-123"
            },
            "details": '{"origin": "SDK"}'
        }
        mock_response.text = json.dumps(expected_body)
        provider.session.post.return_value = mock_response
        
        # Execute
        result = provider._create_check_full(
            name="check_uniqueness_of_id",
            dimension_id="dimension-123",
            native_id="asset-456/check-789",
            check_type="uniqueness",
            project_id="project-123"
        )
        
        # Verify - should return full check body (dict)
        assert isinstance(result, dict)
        assert result["id"] == "check-full-123"
        assert result["name"] == "check_uniqueness_of_id"
        assert result["type"] == "uniqueness"
        assert result["native_id"] == "asset-456/check-789"
        assert result["dimension"]["id"] == "dimension-123"
        
        # Verify the API call
        provider.session.post.assert_called_once()
        call_args = provider.session.post.call_args
        
        # Check URL
        assert "https://test-instance.com/data_quality/v4/checks" in call_args[0][0]
        assert "project_id=project-123" in call_args[0][0]
        
        # Check payload
        payload = json.loads(call_args[1]["data"])
        assert payload["name"] == "check_uniqueness_of_id"
        assert payload["type"] == "uniqueness"
        assert payload["dimension"]["id"] == "dimension-123"
        assert json.loads(payload["details"])["origin"] == "SDK"
    
    def test_create_check_full_with_catalog_id(self, provider):
        """Test _create_check_full returns full check body with catalog_id."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        expected_body = {
            "id": "check-full-456",
            "name": "check_completeness",
            "type": "completeness",
            "native_id": "asset-111/check-456"
        }
        mock_response.text = json.dumps(expected_body)
        provider.session.post.return_value = mock_response
        
        # Execute
        result = provider._create_check_full(
            name="check_completeness",
            dimension_id="dimension-789",
            native_id="asset-111/check-456",
            catalog_id="catalog-999"
        )
        
        # Verify - should return full check body (dict)
        assert isinstance(result, dict)
        assert result["id"] == "check-full-456"
        assert result["name"] == "check_completeness"
        assert result["type"] == "completeness"
        
        # Verify the API call
        call_args = provider.session.post.call_args
        
        # Check URL contains catalog_id
        assert "catalog_id=catalog-999" in call_args[0][0]
        assert "project_id" not in call_args[0][0]
    
    def test_create_check_full_with_parent_check_id(self, provider):
        """Test _create_check_full returns full check body with parent."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        expected_body = {
            "id": "child-check-full-123",
            "name": "check_format_email",
            "type": "format",
            "parent": {
                "id": "parent-check-456",
                "name": "parent_check"
            }
        }
        mock_response.text = json.dumps(expected_body)
        provider.session.post.return_value = mock_response
        
        # Execute
        result = provider._create_check_full(
            name="check_format_email",
            dimension_id="dimension-789",
            native_id="asset-111/email/format",
            check_type="format",
            project_id="project-123",
            parent_check_id="parent-check-456"
        )
        
        # Verify - should return full check body with parent
        assert isinstance(result, dict)
        assert result["id"] == "child-check-full-123"
        assert result["parent"]["id"] == "parent-check-456"
        assert result["parent"]["name"] == "parent_check"
        
        # Verify the API call includes parent in payload
        provider.session.post.assert_called_once()
        call_args = provider.session.post.call_args
        
        # Check payload includes parent
        payload = json.loads(call_args[1]["data"])
        assert "parent" in payload
        assert payload["parent"]["id"] == "parent-check-456"
    
    def test_create_check_full_without_check_type(self, provider):
        """Test _create_check_full defaults check_type to name."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        expected_body = {
            "id": "check-full-789",
            "name": "format_check",
            "type": "format_check"
        }
        mock_response.text = json.dumps(expected_body)
        provider.session.post.return_value = mock_response
        
        # Execute
        result = provider._create_check_full(
            name="format_check",
            dimension_id="dimension-111",
            native_id="asset-222/check-789",
            project_id="project-123"
        )
        
        # Verify - should return full check body
        assert isinstance(result, dict)
        assert result["id"] == "check-full-789"
        assert result["name"] == "format_check"
        assert result["type"] == "format_check"
        
        # Verify the API call
        call_args = provider.session.post.call_args
        payload = json.loads(call_args[1]["data"])
        
        # Check that type defaults to name
        assert payload["type"] == "format_check"
        assert payload["name"] == "format_check"
    
    def test_create_check_full_missing_both_ids(self, provider):
        """Test _create_check_full without project_id or catalog_id."""
        with pytest.raises(ValueError) as exc_info:
            provider._create_check_full(
                name="check_test",
                dimension_id="dimension-123",
                native_id="asset-456/check-789"
            )
        
        assert "Either project_id or catalog_id must be provided" in str(exc_info.value)
    
    def test_create_check_full_both_ids_provided(self, provider):
        """Test _create_check_full with both project_id and catalog_id."""
        with pytest.raises(ValueError) as exc_info:
            provider._create_check_full(
                name="check_test",
                dimension_id="dimension-123",
                native_id="asset-456/check-789",
                project_id="project-123",
                catalog_id="catalog-456"
            )
        
        assert "Only one of project_id or catalog_id should be provided" in str(exc_info.value)
    
    def test_create_check_full_api_failure(self, provider):
        """Test _create_check_full with failed API request."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        provider.session.post.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider._create_check_full(
                name="check_test",
                dimension_id="dimension-123",
                native_id="asset-456/check-789",
                project_id="project-123"
            )
        
        assert "Failed to create check" in str(exc_info.value)
        assert "500" in str(exc_info.value)
        assert "Internal server error" in str(exc_info.value)
    
    def test_create_check_full_missing_id_in_response(self, provider):
        """Test _create_check_full with missing id in response."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "name": "check_test",
            "type": "test"
            # Missing "id" field
        })
        provider.session.post.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider._create_check_full(
                name="check_test",
                dimension_id="dimension-123",
                native_id="asset-456/check-789",
                project_id="project-123"
            )
        
        assert "Check ID not found in response" in str(exc_info.value)

    # ==================== get_checks Tests ====================
    
    def test_get_checks_with_project_id(self, provider):
        """Test getting checks with project_id."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "checks": [
                {
                    "id": "check-1",
                    "name": "case_check",
                    "type": "case",
                    "asset": {
                        "id": "asset-123"
                    }
                },
                {
                    "id": "check-2",
                    "name": "case_check_2",
                    "type": "case",
                    "asset": {
                        "id": "asset-123"
                    }
                }
            ]
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_checks(
            dq_asset_id="asset-123",
            check_type="case",
            project_id="project-456"
        )
        
        # Verify
        assert len(result) == 2
        assert result[0]["id"] == "check-1"
        assert result[1]["id"] == "check-2"
        assert result[0]["type"] == "case"
        
        # Verify the API call
        provider.session.get.assert_called_once()
        call_args = provider.session.get.call_args
        
        # Check URL
        assert "https://test-instance.com/data_quality/v4/checks" in call_args[0][0]
        assert "asset.id=asset-123" in call_args[0][0]
        assert "type=case" in call_args[0][0]
        assert "project_id=project-456" in call_args[0][0]
        assert "include_children=true" in call_args[0][0]
        
        # Check headers
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer test-token"
    
    def test_get_checks_with_catalog_id(self, provider):
        """Test getting checks with catalog_id."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "checks": [
                {
                    "id": "check-3",
                    "type": "completeness"
                }
            ]
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_checks(
            dq_asset_id="asset-789",
            check_type="completeness",
            catalog_id="catalog-999"
        )
        
        # Verify
        assert len(result) == 1
        assert result[0]["id"] == "check-3"
        
        # Verify the API call
        call_args = provider.session.get.call_args
        
        # Check URL contains catalog_id
        assert "catalog_id=catalog-999" in call_args[0][0]
        assert "project_id" not in call_args[0][0]
    
    def test_get_checks_with_include_children_false(self, provider):
        """Test getting checks with include_children=False."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "checks": []
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_checks(
            dq_asset_id="asset-111",
            check_type="format",
            project_id="project-222",
            include_children=False
        )
        
        # Verify
        assert len(result) == 0
        
        # Verify the API call
        call_args = provider.session.get.call_args
        
        # Check URL contains include_children=false
        assert "include_children=false" in call_args[0][0]
    
    def test_get_checks_empty_result(self, provider):
        """Test getting checks with no results."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "checks": []
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_checks(
            dq_asset_id="asset-nonexistent",
            check_type="unknown",
            project_id="project-123"
        )
        
        # Verify
        assert result == []
        assert len(result) == 0
    
    def test_get_checks_missing_both_ids(self, provider):
        """Test getting checks without project_id or catalog_id."""
        with pytest.raises(ValueError) as exc_info:
            provider.get_checks(
                dq_asset_id="asset-123",
                check_type="case"
            )
        
        assert "Either project_id or catalog_id must be provided" in str(exc_info.value)
    
    def test_get_checks_both_ids_provided(self, provider):
        """Test getting checks with both project_id and catalog_id."""
        with pytest.raises(ValueError) as exc_info:
            provider.get_checks(
                dq_asset_id="asset-123",
                check_type="case",
                project_id="project-123",
                catalog_id="catalog-456"
            )
        
        assert "Only one of project_id or catalog_id should be provided" in str(exc_info.value)
    
    def test_get_checks_api_failure(self, provider):
        """Test failed get checks request."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Asset not found"
        provider.session.get.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider.get_checks(
                dq_asset_id="asset-invalid",
                check_type="case",
                project_id="project-123"
            )
        
        assert "Failed to get checks" in str(exc_info.value)
        assert "404" in str(exc_info.value)
        assert "Asset not found" in str(exc_info.value)
    
    def test_get_checks_missing_checks_in_response(self, provider):
        """Test get checks with missing 'checks' field in response."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "data": []
            # Missing "checks" field
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_checks(
            dq_asset_id="asset-123",
            check_type="case",
            project_id="project-123"
        )
        
        # Verify - should return empty list when checks field is missing
        assert result == []
    
    def test_get_checks_with_multiple_check_types(self, provider):
        """Test getting checks filters by specific check_type."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "checks": [
                {
                    "id": "check-format-1",
                    "type": "format"
                },
                {
                    "id": "check-format-2",
                    "type": "format"
                }
            ]
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_checks(
            dq_asset_id="asset-multi",
            check_type="format",
            project_id="project-123"
        )
        
        # Verify
        assert len(result) == 2
        assert all(check["type"] == "format" for check in result)
        
        # Verify the API call includes the check_type filter
        call_args = provider.session.get.call_args
        assert "type=format" in call_args[0][0]
    
    def test_get_checks_with_comparison_check_type(self, provider):
        """Test getting checks with comparison check type."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "checks": [
                {
                    "id": "check-comparison-1",
                    "type": "comparison",
                    "name": "compare_columns"
                }
            ]
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_checks(
            dq_asset_id="asset-comparison",
            check_type="comparison",
            project_id="project-123"
        )
        
        # Verify
        assert len(result) == 1
        assert result[0]["type"] == "comparison"
        assert result[0]["name"] == "compare_columns"