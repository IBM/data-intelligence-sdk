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
from unittest.mock import Mock, patch, MagicMock
import json

from wxdi.dq_validator.provider import ProviderConfig, IssuesProvider


class TestIssuesProvider:
    """Test suite for IssuesProvider class."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return ProviderConfig(
            url="https://test-instance.com",
            auth_token="Bearer test-token"
        )
    
    @pytest.fixture
    def provider(self, config):
        """Create a test IssuesProvider instance."""
        with patch('wxdi.dq_validator.provider.base_provider.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            provider = IssuesProvider(config)
            yield provider
    
    def test_update_issue_values_both_fields_with_project_id(self, provider):
        """Test updating both occurrences and tested records with project_id."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "issue_id": "issue-123",
            "number_of_occurrences": 777,
            "number_of_tested_records": 1100,
            "status": "updated"
        })
        provider.session.patch.return_value = mock_response
        
        # Execute
        result = provider.update_issue_values("issue-123", occurrences=10, tested_records=100, project_id="project-123")
        
        # Verify
        assert result["issue_id"] == "issue-123"
        assert result["number_of_occurrences"] == 777
        assert result["number_of_tested_records"] == 1100
        assert result["status"] == "updated"
        
        # Verify the API call
        provider.session.patch.assert_called_once()
        call_args = provider.session.patch.call_args
        
        # Check URL
        assert "https://test-instance.com/data_quality/v4/issues/issue-123" in call_args[0][0]
        assert "project_id=project-123" in call_args[0][0]
        
        # Check headers
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["Content-Type"] == "application/json-patch+json"
        
        # Check payload - should have both operations
        payload = json.loads(call_args[1]["data"])
        assert len(payload) == 2
        assert payload[0]["op"] == "add"
        assert payload[0]["path"] == "/number_of_occurrences"
        assert payload[0]["value"] == 10
        assert payload[1]["op"] == "add"
        assert payload[1]["path"] == "/number_of_tested_records"
        assert payload[1]["value"] == 100
    
    def test_update_issue_values_both_fields_with_catalog_id(self, provider):
        """Test updating both occurrences and tested records with catalog_id."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "issue_id": "issue-123",
            "number_of_occurrences": 777,
            "number_of_tested_records": 1100,
            "status": "updated"
        })
        provider.session.patch.return_value = mock_response
        
        # Execute
        result = provider.update_issue_values("issue-123", occurrences=10, tested_records=100, catalog_id="catalog-456")
        
        # Verify
        assert result["issue_id"] == "issue-123"
        
        # Verify the API call
        call_args = provider.session.patch.call_args
        
        # Check URL contains catalog_id
        assert "catalog_id=catalog-456" in call_args[0][0]
        assert "project_id" not in call_args[0][0]
    
    def test_update_issue_values_missing_both_ids(self, provider):
        """Test updating without project_id or catalog_id."""
        with pytest.raises(ValueError) as exc_info:
            provider.update_issue_values("issue-123", occurrences=10, tested_records=100)
        
        assert "Either project_id or catalog_id must be provided" in str(exc_info.value)
    
    def test_update_issue_values_both_ids_provided(self, provider):
        """Test updating with both project_id and catalog_id."""
        with pytest.raises(ValueError) as exc_info:
            provider.update_issue_values(
                "issue-123",
                occurrences=10,
                tested_records=100,
                project_id="project-123",
                catalog_id="catalog-456"
            )
        
        assert "Only one of project_id or catalog_id should be provided" in str(exc_info.value)
    
    
    def test_update_issue_values_with_replace_operation(self, provider):
        """Test updating with replace operation."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "issue_id": "issue-999",
            "number_of_occurrences": 100,
            "number_of_tested_records": 1000,
            "status": "updated"
        })
        provider.session.patch.return_value = mock_response
        
        # Execute
        result = provider.update_issue_values(
            "issue-999",
            occurrences=100,
            tested_records=1000,
            project_id="project-123",
            operation="replace"
        )
        
        # Verify
        assert result["issue_id"] == "issue-999"
        assert result["number_of_occurrences"] == 100
        assert result["number_of_tested_records"] == 1000
        
        # Verify the API call
        call_args = provider.session.patch.call_args
        payload = json.loads(call_args[1]["data"])
        assert len(payload) == 2
        assert payload[0]["op"] == "replace"
        assert payload[0]["path"] == "/number_of_occurrences"
        assert payload[0]["value"] == 100
        assert payload[1]["op"] == "replace"
        assert payload[1]["path"] == "/number_of_tested_records"
        assert payload[1]["value"] == 1000
    
    def test_update_issue_values_failure(self, provider):
        """Test failed update of issue values."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Issue not found"
        provider.session.patch.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider.update_issue_values("invalid-issue", occurrences=10, tested_records=100, project_id="project-123")
        
        assert "Failed to update issue metrics for issue invalid-issue" in str(exc_info.value)
        assert "404" in str(exc_info.value)
    
    def test_update_issue_values_with_zero_values(self, provider):
        """Test updating with zero values (should be included)."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "issue_id": "issue-000",
            "number_of_occurrences": 0,
            "number_of_tested_records": 0,
            "status": "updated"
        })
        provider.session.patch.return_value = mock_response
        
        # Execute
        result = provider.update_issue_values("issue-000", occurrences=0, tested_records=0, project_id="project-123")
        
        # Verify
        assert result["number_of_occurrences"] == 0
        assert result["number_of_tested_records"] == 0
        
        # Verify the API call includes both zero values
        call_args = provider.session.patch.call_args
        payload = json.loads(call_args[1]["data"])
        assert len(payload) == 2
        assert payload[0]["value"] == 0
        assert payload[1]["value"] == 0
    
    def test_get_issue_id_success_with_project_id(self, provider):
        """Test successful retrieval of issue ID with project_id."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "id": "b8f4252b-cd35-4668-9b35-4635bfc6e2e0",
            "account_id": "999",
            "created_at": "2025-12-19T06:37:24.955Z",
            "check": {
                "id": "ad277842-dea7-44ef-8e4b-d940df0f79aa",
                "account_id": "999",
                "created_at": "2025-12-19T06:37:23.519Z",
                "dimension": {
                    "id": "ec453723-669c-48bb-82c1-11b69b3b8c93",
                    "name": "Validity",
                    "description": "Data is valid if it conforms to the syntax (format, type, range) of its definition.",
                    "is_default": True
                },
                "name": "Format check",
                "native_id": "b2debda2-6ab9-4a39-8c23-17954e004dcf/7377e2cd-ac0e-4833-8760-fd0e8cb682aa",
                "wkc_container_id": "24419069-d649-45cb-a2c1-64d6eed650d5",
                "parent": {
                    "id": "f3fca1af-f00f-42b7-af42-f0965673237e"
                },
                "type": "format"
            },
            "reported_for": {
                "id": "1488a413-99f9-4bed-906d-c33b505d5728",
                "native_id": "b2debda2-6ab9-4a39-8c23-17954e004dcf/RTN"
            },
            "number_of_occurrences": 0,
            "number_of_tested_records": 1000,
            "percent_occurrences": 0,
            "status": "actual",
            "ignored": False,
            "details": "{\"sampling\":{\"size\":1000,\"min_records\":0,\"type\":\"SEQUENTIAL\"}}",
            "archived_issues": []
        })
        provider.session.post.return_value = mock_response
        
        # Execute
        result = provider.get_issue_id(
            reported_for_id="1488a413-99f9-4bed-906d-c33b505d5728",
            dq_check_id="ad277842-dea7-44ef-8e4b-d940df0f79aa",
            project_id="24419069-d649-45cb-a2c1-64d6eed650d5"
        )
        
        # Verify
        assert result == "b8f4252b-cd35-4668-9b35-4635bfc6e2e0"
        
        # Verify the API call
        provider.session.post.assert_called_once()
        call_args = provider.session.post.call_args
        url = call_args[0][0]
        
        # Check URL contains required parameters
        assert "project_id=24419069-d649-45cb-a2c1-64d6eed650d5" in url
        assert "reported_for.id=1488a413-99f9-4bed-906d-c33b505d5728" in url
        assert "check.id=ad277842-dea7-44ef-8e4b-d940df0f79aa" in url
    
    def test_get_issue_id_success_with_catalog_id(self, provider):
        """Test successful retrieval of issue ID with catalog_id."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "id": "issue-id-789",
            "catalog_id": "catalog-123"
        })
        provider.session.post.return_value = mock_response
        
        # Execute
        result = provider.get_issue_id(
            reported_for_id="asset-id",
            dq_check_id="check-id",
            catalog_id="catalog-123"
        )
        
        # Verify
        assert result == "issue-id-789"
        
        # Verify the API call
        call_args = provider.session.post.call_args
        url = call_args[0][0]
        
        # Check URL contains catalog_id
        assert "catalog_id=catalog-123" in url
        assert "project_id" not in url
    
    def test_get_issue_id_missing_both_ids(self, provider):
        """Test get_issue_id without project_id or catalog_id."""
        with pytest.raises(ValueError) as exc_info:
            provider.get_issue_id(
                reported_for_id="asset-id",
                dq_check_id="check-id"
            )
        
        assert "Either project_id or catalog_id must be provided" in str(exc_info.value)
    
    def test_get_issue_id_both_ids_provided(self, provider):
        """Test get_issue_id with both project_id and catalog_id."""
        with pytest.raises(ValueError) as exc_info:
            provider.get_issue_id(
                reported_for_id="asset-id",
                dq_check_id="check-id",
                project_id="project-123",
                catalog_id="catalog-456"
            )
        
        assert "Only one of project_id or catalog_id should be provided" in str(exc_info.value)
    
    def test_get_issue_id_failure(self, provider):
        """Test failed retrieval of issue ID."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Not found"
        provider.session.post.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider.get_issue_id(
                reported_for_id="invalid-asset",
                dq_check_id="invalid-check",
                project_id="invalid-project"
            )
        
        assert "Failed to search for issue" in str(exc_info.value)
        assert "404" in str(exc_info.value)
    
    def test_update_issue_metrics(self, provider):
        """Test updating issue metrics using CAMS asset and check IDs."""
        with patch('wxdi.dq_validator.provider.dq_search.DQSearchProvider') as mock_search_provider_class:
            # Setup mock search provider
            mock_search_provider = Mock()
            mock_search_provider_class.return_value = mock_search_provider
            
            # Mock search_dq_asset response
            mock_search_provider.search_dq_asset.return_value = {
                "id": "dq-asset-123",
                "name": "Test Asset",
                "type": "column"
            }
            
            # Mock get_issues response (replaces search_dq_check and get_issue_id)
            mock_get_issues_response = Mock()
            mock_get_issues_response.ok = True
            mock_get_issues_response.text = json.dumps({
                "issues": [
                    {
                        "id": "issue-789",
                        "check": {
                            "id": "dq-check-456",
                            "native_id": "cams-asset-abc/cams-check-def"
                        },
                        "project_id": "project-123"
                    }
                ],
                "total_count": 1
            })
            provider.session.get.return_value = mock_get_issues_response
            
            # Mock update_issue_values response
            mock_update_response = Mock()
            mock_update_response.ok = True
            mock_update_response.text = json.dumps({
                "issue_id": "issue-789",
                "number_of_occurrences": 10,
                "number_of_tested_records": 100
            })
            provider.session.patch.return_value = mock_update_response
            
            # Execute
            result = provider.update_issue_metrics(
                asset_id="cams-asset-abc",
                check_id="cams-check-def",
                occurrences=10,
                tested_records=100,
                column_name="test_column",
                check_type="format",
                project_id="project-123",
                asset_type="column"
            )
            
            # Verify
            assert result["issue_id"] == "issue-789"
            assert result["number_of_occurrences"] == 10
            assert result["number_of_tested_records"] == 100
            
            # Verify search_dq_asset was called correctly
            mock_search_provider.search_dq_asset.assert_called_once_with(
                native_id="cams-asset-abc/test_column",
                project_id="project-123",
                catalog_id=None,
                asset_type="column"
            )
            
            # Verify get_issues (GET request) was called instead of search_dq_check
            provider.session.get.assert_called_once()
            call_args = provider.session.get.call_args
            url = call_args[0][0]
            assert "reported_for.id=dq-asset-123" in url
            assert "type=format" in url
            assert "include_children=false" in url
    
    def test_update_issue_metrics_with_check_native_id(self, provider):
        """Test updating issue metrics using check_native_id instead of asset_id and check_id."""
        with patch('wxdi.dq_validator.provider.dq_search.DQSearchProvider') as mock_search_provider_class:
            # Setup mock search provider
            mock_search_provider = Mock()
            mock_search_provider_class.return_value = mock_search_provider
            
            # Mock search_dq_asset response
            mock_search_provider.search_dq_asset.return_value = {
                "id": "dq-asset-456",
                "name": "Test Asset",
                "type": "column"
            }
            
            # Mock get_issues response
            mock_get_issues_response = Mock()
            mock_get_issues_response.ok = True
            mock_get_issues_response.text = json.dumps({
                "issues": [
                    {
                        "id": "issue-999",
                        "check": {
                            "id": "dq-check-789",
                            "native_id": "asset-abc/column_name/case"
                        },
                        "project_id": "project-456"
                    }
                ],
                "total_count": 1
            })
            provider.session.get.return_value = mock_get_issues_response
            
            # Mock update_issue_values response
            mock_update_response = Mock()
            mock_update_response.ok = True
            mock_update_response.text = json.dumps({
                "issue_id": "issue-999",
                "number_of_occurrences": 25,
                "number_of_tested_records": 250
            })
            provider.session.patch.return_value = mock_update_response
            
            # Execute - using check_native_id instead of asset_id and check_id
            result = provider.update_issue_metrics(
                check_native_id="asset-abc/column_name/case",
                occurrences=25,
                tested_records=250,
                column_name="column_name",
                check_type="case",
                project_id="project-456",
                asset_type="column"
            )
            
            # Verify
            assert result["issue_id"] == "issue-999"
            assert result["number_of_occurrences"] == 25
            assert result["number_of_tested_records"] == 250
            
            # Verify search_dq_asset was called with extracted asset_id
            mock_search_provider.search_dq_asset.assert_called_once_with(
                native_id="asset-abc/column_name",
                project_id="project-456",
                catalog_id=None,
                asset_type="column"
            )
    
    def test_validate_and_resolve_ids_with_asset_and_check_ids(self, provider):
        """Test _validate_and_resolve_ids with asset_id and check_id provided."""
        asset_id, check_id, check_native_id = provider._validate_and_resolve_ids(
            asset_id="asset-123",
            check_id="check-456",
            check_native_id=None
        )
        
        assert asset_id == "asset-123"
        assert check_id == "check-456"
        assert check_native_id == "asset-123/check-456"
    
    def test_validate_and_resolve_ids_with_check_native_id(self, provider):
        """Test _validate_and_resolve_ids with check_native_id provided."""
        asset_id, check_id, check_native_id = provider._validate_and_resolve_ids(
            asset_id=None,
            check_id=None,
            check_native_id="asset-abc/check-def"
        )
        
        assert asset_id == "asset-abc"
        assert check_id == "check-def"
        assert check_native_id == "asset-abc/check-def"
    
    def test_validate_and_resolve_ids_with_check_native_id_containing_slashes(self, provider):
        """Test _validate_and_resolve_ids with check_native_id containing multiple slashes."""
        asset_id, check_id, check_native_id = provider._validate_and_resolve_ids(
            asset_id=None,
            check_id=None,
            check_native_id="asset-123/column/check-type"
        )
        
        assert asset_id == "asset-123"
        assert check_id == "column/check-type"
        assert check_native_id == "asset-123/column/check-type"
    
    def test_validate_and_resolve_ids_with_both_provided(self, provider):
        """Test _validate_and_resolve_ids when both asset_id/check_id and check_native_id are provided."""
        # When both are provided, the original values are kept (no parsing or construction happens)
        asset_id, check_id, check_native_id = provider._validate_and_resolve_ids(
            asset_id="asset-111",
            check_id="check-222",
            check_native_id="asset-999/check-888"
        )
        
        # Original values should be returned as-is
        assert asset_id == "asset-111"
        assert check_id == "check-222"
        assert check_native_id == "asset-999/check-888"
    
    def test_validate_and_resolve_ids_with_neither_provided(self, provider):
        """Test _validate_and_resolve_ids raises error when neither IDs are provided."""
        with pytest.raises(ValueError) as exc_info:
            provider._validate_and_resolve_ids(
                asset_id=None,
                check_id=None,
                check_native_id=None
            )
        
        assert "Either (asset_id and check_id) or check_native_id must be provided" in str(exc_info.value)
    
    def test_validate_and_resolve_ids_with_only_asset_id(self, provider):
        """Test _validate_and_resolve_ids raises error when only asset_id is provided."""
        with pytest.raises(ValueError) as exc_info:
            provider._validate_and_resolve_ids(
                asset_id="asset-123",
                check_id=None,
                check_native_id=None
            )
        
        assert "Either (asset_id and check_id) or check_native_id must be provided" in str(exc_info.value)
    
    def test_validate_and_resolve_ids_with_only_check_id(self, provider):
        """Test _validate_and_resolve_ids raises error when only check_id is provided."""
        with pytest.raises(ValueError) as exc_info:
            provider._validate_and_resolve_ids(
                asset_id=None,
                check_id="check-456",
                check_native_id=None
            )
        
        assert "Either (asset_id and check_id) or check_native_id must be provided" in str(exc_info.value)
    
    def test_validate_and_resolve_ids_with_invalid_check_native_id_format(self, provider):
        """Test _validate_and_resolve_ids raises error for invalid check_native_id format."""
        with pytest.raises(ValueError) as exc_info:
            provider._validate_and_resolve_ids(
                asset_id=None,
                check_id=None,
                check_native_id="invalid-format-no-slash"
            )
        
        assert "Invalid check_native_id format (missing /)" in str(exc_info.value)
        assert "invalid-format-no-slash" in str(exc_info.value)
    
    def test_get_issues_with_catalog_id(self, provider):
        """Test getting issues with catalog_id and check_id filter."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "issues": [
                {
                    "id": "issue-1",
                    "check": {
                        "id": "check-1",
                        "native_id": "asset-id/065c2b72-4600-4d15-8c48-298a2abf66cd"
                    },
                    "check_name": "Completeness Check",
                    "number_of_occurrences": 5,
                    "number_of_tested_records": 100
                },
                {
                    "id": "issue-2",
                    "check": {
                        "id": "check-2",
                        "native_id": "asset-id/other-check-id"
                    },
                    "check_name": "Format Check",
                    "number_of_occurrences": 3,
                    "number_of_tested_records": 100
                }
            ],
            "total_count": 2
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_issues(
            dq_asset_id="08b139ca-35a6-4b61-b87b-aa832870d89c",
            check_type="completeness",
            check_id="065c2b72-4600-4d15-8c48-298a2abf66cd",
            catalog_id="07708fd8-8d77-4a07-a01b-0132130bce0e",
            limit=20,
            latest_only=True,
            include_children=False,
            sort_by="check_name",
            sort_direction="asc"
        )
        
        # Verify - should return only the matching issue
        assert result is not None
        assert result["id"] == "issue-1"
        assert result["check"]["id"] == "check-1"
        
        # Verify the API call
        provider.session.get.assert_called_once()
        call_args = provider.session.get.call_args
        url = call_args[0][0]
        
        # Check URL contains required parameters
        assert "catalog_id=07708fd8-8d77-4a07-a01b-0132130bce0e" in url
        assert "reported_for.id=08b139ca-35a6-4b61-b87b-aa832870d89c" in url
        assert "type=completeness" in url
        assert "limit=20" in url
        assert "latest_only=true" in url
        assert "include_children=false" in url
        assert "sort_by=check_name" in url
        assert "sort_direction=asc" in url
    
    def test_get_issues_with_project_id(self, provider):
        """Test getting issues with project_id and check_id filter."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "issues": [
                {
                    "id": "issue-3",
                    "check": {
                        "id": "check-3",
                        "native_id": "asset-id/test-check-id"
                    },
                    "check_name": "Range Check",
                    "number_of_occurrences": 10,
                    "number_of_tested_records": 200
                }
            ],
            "total_count": 1
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_issues(
            dq_asset_id="asset-id-123",
            check_type="range",
            check_id="test-check-id",
            project_id="project-456"
        )
        
        # Verify - should return the matching issue
        assert result is not None
        assert result["id"] == "issue-3"
        
        # Verify the API call
        call_args = provider.session.get.call_args
        url = call_args[0][0]
        
        # Check URL contains project_id
        assert "project_id=project-456" in url
        assert "catalog_id" not in url
        assert "include_children=false" in url
    
    def test_get_issues_missing_both_ids(self, provider):
        """Test get_issues without project_id or catalog_id."""
        with pytest.raises(ValueError) as exc_info:
            provider.get_issues(
                dq_asset_id="asset-id",
                check_type="completeness",
                check_id="test-check-id"
            )
        
        assert "Either project_id or catalog_id must be provided" in str(exc_info.value)
    
    def test_get_issues_both_ids_provided(self, provider):
        """Test get_issues with both project_id and catalog_id."""
        with pytest.raises(ValueError) as exc_info:
            provider.get_issues(
                dq_asset_id="asset-id",
                check_type="completeness",
                check_id="test-check-id",
                project_id="project-123",
                catalog_id="catalog-456"
            )
        
        assert "Only one of project_id or catalog_id should be provided" in str(exc_info.value)
    
    def test_get_issues_failure(self, provider):
        """Test failed retrieval of issues."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Not found"
        provider.session.get.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider.get_issues(
                dq_asset_id="invalid-asset",
                check_type="completeness",
                check_id="test-check-id",
                project_id="invalid-project"
            )
        
        assert "Failed to get issues" in str(exc_info.value)
        assert "404" in str(exc_info.value)
    
    def test_get_issues_with_minimal_params(self, provider):
        """Test getting issues with minimal parameters (using defaults)."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "issues": [
                {
                    "id": "issue-4",
                    "check": {
                        "id": "check-4",
                        "native_id": "asset-id/minimal-check-id"
                    }
                }
            ],
            "total_count": 1
        })
        provider.session.get.return_value = mock_response
        
        # Execute with minimal params
        result = provider.get_issues(
            dq_asset_id="asset-id",
            check_type="datatype",
            check_id="minimal-check-id",
            catalog_id="catalog-123"
        )
        
        # Verify - should return the matching issue
        assert result is not None
        assert result["id"] == "issue-4"
        
        # Verify the API call includes default values
        call_args = provider.session.get.call_args
        url = call_args[0][0]
        
        assert "limit=20" in url
        assert "latest_only=true" in url
        assert "include_children=false" in url
        assert "sort_by=check_name" in url
        assert "sort_direction=asc" in url
    
    def test_get_issues_no_match_found(self, provider):
        """Test get_issues when no matching check_id is found."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "issues": [
                {
                    "id": "issue-5",
                    "check": {
                        "id": "check-5",
                        "native_id": "asset-id/different-check-id"
                    }
                }
            ],
            "total_count": 1
        })
        provider.session.get.return_value = mock_response
        
        # Execute with a check_id that doesn't match
        result = provider.get_issues(
            dq_asset_id="asset-id",
            check_type="format",
            check_id="non-existent-check-id",
            catalog_id="catalog-123"
        )
        
        # Verify - should return None when no match found
        assert result is None
    
    def test_create_issue_with_project_id(self, provider):
        """Test creating an issue with project_id."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "id": "046605b5-48d9-489e-b846-8ef96a7a1aba",
            "check": {
                "id": "6be18374-573a-4cf8-8ab7-e428506e428b"
            },
            "reported_for": {
                "id": "894d01fd-bdfc-4a4f-b68b-62751e06e06a"
            },
            "number_of_occurrences": 123,
            "number_of_tested_records": 456789,
            "status": "actual",
            "ignored": False
        })
        provider.session.post.return_value = mock_response
        
        # Execute
        result = provider.create_issue(
            dq_check_id="6be18374-573a-4cf8-8ab7-e428506e428b",
            reported_for_id="894d01fd-bdfc-4a4f-b68b-62751e06e06a",
            number_of_occurrences=123,
            number_of_tested_records=456789,
            project_id="project-123"
        )
        
        # Verify
        assert result == "046605b5-48d9-489e-b846-8ef96a7a1aba"
        
        # Verify the API call
        provider.session.post.assert_called_once()
        call_args = provider.session.post.call_args
        
        # Check URL
        assert "https://test-instance.com/data_quality/v4/issues" in call_args[0][0]
        assert "project_id=project-123" in call_args[0][0]
        
        # Check payload
        payload = json.loads(call_args[1]["data"])
        assert payload["check"]["id"] == "6be18374-573a-4cf8-8ab7-e428506e428b"
        assert payload["reported_for"]["id"] == "894d01fd-bdfc-4a4f-b68b-62751e06e06a"
        assert payload["number_of_occurrences"] == 123
        assert payload["number_of_tested_records"] == 456789
    
    def test_create_issue_missing_both_ids(self, provider):
        """Test creating an issue without project_id or catalog_id."""
        with pytest.raises(ValueError) as exc_info:
            provider.create_issue(
                dq_check_id="check-123",
                reported_for_id="asset-456",
                number_of_occurrences=10,
                number_of_tested_records=100
            )
        
        assert "Either project_id or catalog_id must be provided" in str(exc_info.value)
    
    def test_create_issue_failure(self, provider):
        """Test failed creation of issue."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        provider.session.post.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider.create_issue(
                dq_check_id="invalid-check",
                reported_for_id="invalid-asset",
                number_of_occurrences=10,
                number_of_tested_records=100,
                project_id="project-123"
            )
        
        assert "Failed to create issue" in str(exc_info.value)
        assert "400" in str(exc_info.value)
    
    def test_create_issues_bulk_with_project_id(self, provider):
        """Test creating multiple issues in bulk with project_id."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "issues": [
                {
                    "id": "issue-bulk-1",
                    "check": {
                        "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f/format/Validity",
                        "type": "format"
                    },
                    "status": "aggregation"
                },
                {
                    "id": "issue-bulk-2",
                    "check": {
                        "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f/format/sample3",
                        "type": "format"
                    },
                    "status": "actual"
                }
            ],
            "assets": [
                {
                    "id": "asset-bulk-1",
                    "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f",
                    "type": "data_asset"
                },
                {
                    "id": "asset-bulk-2",
                    "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f/NAME",
                    "type": "column"
                }
            ]
        })
        provider.session.post.return_value = mock_response
        
        # Prepare bulk payload
        bulk_payload = {
            "issues": [
                {
                    "check": {
                        "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f/format/Validity",
                        "type": "format"
                    },
                    "reported_for": {
                        "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f",
                        "type": "data_asset"
                    },
                    "number_of_occurrences": 200,
                    "number_of_tested_records": 1000,
                    "status": "aggregation",
                    "ignored": False
                },
                {
                    "check": {
                        "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f/format/sample3",
                        "type": "format"
                    },
                    "reported_for": {
                        "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f/NAME",
                        "type": "column"
                    },
                    "number_of_occurrences": 200,
                    "number_of_tested_records": 1000,
                    "status": "actual",
                    "ignored": False
                }
            ],
            "assets": [
                {
                    "name": "ACCOUNT_HOLDERS.csv",
                    "type": "data_asset",
                    "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f",
                    "weight": 1
                },
                {
                    "name": "NAME",
                    "type": "column",
                    "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f/NAME",
                    "parent": {
                        "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f",
                        "type": "data_asset"
                    },
                    "weight": 1
                }
            ],
            "existing_checks": [
                {
                    "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f/format/Validity",
                    "type": "format"
                },
                {
                    "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f/format/sample3",
                    "type": "format"
                }
            ]
        }
        
        # Execute
        result = provider.create_issues_bulk(
            payload=bulk_payload,
            project_id="project-123",
            incremental_reporting=False,
            refresh_assets=False
        )
        
        # Verify
        assert "issues" in result
        assert len(result["issues"]) == 2
        assert result["issues"][0]["id"] == "issue-bulk-1"
        assert result["issues"][1]["id"] == "issue-bulk-2"
        
        # Verify the API call
        provider.session.post.assert_called_once()
        call_args = provider.session.post.call_args
        
        # Check URL
        assert "https://test-instance.com/data_quality/v4/create_issues" in call_args[0][0]
        assert "project_id=project-123" in call_args[0][0]
        assert "incremental_reporting=false" in call_args[0][0]
        assert "refresh_assets=false" in call_args[0][0]
        
        # Check payload
        payload = json.loads(call_args[1]["data"])
        assert len(payload["issues"]) == 2
        assert len(payload["assets"]) == 2
        assert len(payload["existing_checks"]) == 2
    
    def test_create_issues_bulk_with_catalog_id_and_incremental_reporting(self, provider):
        """Test creating bulk issues with catalog_id and incremental_reporting=True."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "issues": [
                {"id": "issue-1", "status": "aggregation"},
                {"id": "issue-2", "status": "actual"}
            ]
        })
        provider.session.post.return_value = mock_response
        
        # Minimal bulk payload
        bulk_payload = {
            "issues": [
                {
                    "check": {"native_id": "asset/check1", "type": "format"},
                    "reported_for": {"native_id": "asset", "type": "data_asset"},
                    "number_of_occurrences": 10,
                    "number_of_tested_records": 100,
                    "status": "aggregation",
                    "ignored": False
                }
            ],
            "assets": [
                {"name": "Test Asset", "type": "data_asset", "native_id": "asset", "weight": 1}
            ],
            "existing_checks": [
                {"native_id": "asset/check1", "type": "format"}
            ]
        }
        
        # Execute
        result = provider.create_issues_bulk(
            payload=bulk_payload,
            catalog_id="catalog-456",
            incremental_reporting=True,
            refresh_assets=True
        )
        
        # Verify
        assert "issues" in result
        assert len(result["issues"]) == 2
        
        # Verify the API call
        call_args = provider.session.post.call_args
        url = call_args[0][0]
        
        # Check URL contains catalog_id and boolean params
        assert "catalog_id=catalog-456" in url
        assert "project_id" not in url
        assert "incremental_reporting=true" in url
        assert "refresh_assets=true" in url
    
    def test_create_issues_bulk_missing_both_ids(self, provider):
        """Test creating bulk issues without project_id or catalog_id."""
        bulk_payload = {
            "issues": [],
            "assets": [],
            "existing_checks": []
        }
        
        with pytest.raises(ValueError) as exc_info:
            provider.create_issues_bulk(payload=bulk_payload)
        
        assert "Either project_id or catalog_id must be provided" in str(exc_info.value)
    
    def test_create_issues_bulk_both_ids_provided(self, provider):
        """Test creating bulk issues with both project_id and catalog_id."""
        bulk_payload = {
            "issues": [],
            "assets": [],
            "existing_checks": []
        }
        
        with pytest.raises(ValueError) as exc_info:
            provider.create_issues_bulk(
                payload=bulk_payload,
                project_id="project-123",
                catalog_id="catalog-456"
            )
        
        assert "Only one of project_id or catalog_id should be provided" in str(exc_info.value)
    
    def test_create_issues_bulk_failure(self, provider):
        """Test failed bulk issue creation."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.text = "Invalid payload"
        provider.session.post.return_value = mock_response
        
        bulk_payload = {
            "issues": [],
            "assets": [],
            "existing_checks": []
        }
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider.create_issues_bulk(
                payload=bulk_payload,
                project_id="project-123"
            )
        
        assert "Failed to create issues in bulk" in str(exc_info.value)
        assert "400" in str(exc_info.value)
        assert "Invalid payload" in str(exc_info.value)