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

from wxdi.dq_validator.provider import ProviderConfig, DQAssetsProvider


class TestDQAssetsProvider:
    """Test suite for DQAssetsProvider class."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return ProviderConfig(
            url="https://test-instance.com",
            auth_token="Bearer test-token"
        )
    
    @pytest.fixture
    def provider(self, config):
        """Create a test DQAssetsProvider instance."""
        with patch('wxdi.dq_validator.provider.base_provider.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            provider = DQAssetsProvider(config)
            yield provider
    
    # ==================== get_assets Tests ====================
    
    def test_get_assets_with_project_id(self, provider):
        """Test getting assets with project_id."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "assets": [
                {
                    "id": "asset-1",
                    "name": "Table1",
                    "type": "table"
                },
                {
                    "id": "asset-2",
                    "name": "Column1",
                    "type": "column"
                }
            ],
            "total_count": 2
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_assets(project_id="project-123")
        
        # Verify
        assert "assets" in result
        assert len(result["assets"]) == 2
        assert result["assets"][0]["id"] == "asset-1"
        assert result["total_count"] == 2
        
        # Verify the API call
        provider.session.get.assert_called_once()
        call_args = provider.session.get.call_args
        
        # Check URL
        assert "https://test-instance.com/data_quality/v4/assets" in call_args[0][0]
        assert "project_id=project-123" in call_args[0][0]
        
        # Check headers
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["Content-Type"] == "application/json"
    
    def test_get_assets_with_catalog_id(self, provider):
        """Test getting assets with catalog_id."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "assets": [
                {
                    "id": "asset-3",
                    "name": "Table2",
                    "type": "table"
                }
            ],
            "total_count": 1
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_assets(catalog_id="catalog-456")
        
        # Verify
        assert "assets" in result
        assert len(result["assets"]) == 1
        assert result["assets"][0]["id"] == "asset-3"
        
        # Verify the API call
        call_args = provider.session.get.call_args
        
        # Check URL contains catalog_id
        assert "catalog_id=catalog-456" in call_args[0][0]
        assert "project_id" not in call_args[0][0]
    
    def test_get_assets_with_all_optional_params(self, provider):
        """Test getting assets with all optional parameters."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "assets": [],
            "total_count": 0,
            "next": {
                "start": "next-token"
            }
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_assets(
            project_id="project-123",
            start="start-token",
            limit=50,
            include_children=True,
            asset_type="column"
        )
        
        # Verify
        assert "assets" in result
        assert result["total_count"] == 0
        
        # Verify the API call
        call_args = provider.session.get.call_args
        
        # Check URL contains all parameters
        assert "project_id=project-123" in call_args[0][0]
        assert "start=start-token" in call_args[0][0]
        assert "limit=50" in call_args[0][0]
        assert "include_children=true" in call_args[0][0]
        assert "type=column" in call_args[0][0]
    
    def test_get_assets_with_include_children_false(self, provider):
        """Test getting assets with include_children=False."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "assets": [],
            "total_count": 0
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_assets(
            project_id="project-123",
            include_children=False
        )
        
        # Verify
        assert "assets" in result
        
        # Verify the API call
        call_args = provider.session.get.call_args
        
        # Check URL contains include_children=false
        assert "include_children=false" in call_args[0][0]
    
    def test_get_assets_with_limit(self, provider):
        """Test getting assets with limit parameter."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "assets": [{"id": f"asset-{i}"} for i in range(10)],
            "total_count": 10
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_assets(
            project_id="project-123",
            limit=10
        )
        
        # Verify
        assert len(result["assets"]) == 10
        
        # Verify the API call
        call_args = provider.session.get.call_args
        
        # Check URL contains limit
        assert "limit=10" in call_args[0][0]
    
    def test_get_assets_with_start_token(self, provider):
        """Test getting assets with start token for pagination."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "assets": [{"id": "asset-next"}],
            "total_count": 1
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_assets(
            project_id="project-123",
            start="pagination-token-123"
        )
        
        # Verify
        assert len(result["assets"]) == 1
        
        # Verify the API call
        call_args = provider.session.get.call_args
        
        # Check URL contains start token
        assert "start=pagination-token-123" in call_args[0][0]
    
    def test_get_assets_with_asset_type_table(self, provider):
        """Test getting assets filtered by type=table."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "assets": [
                {"id": "asset-1", "type": "table"},
                {"id": "asset-2", "type": "table"}
            ],
            "total_count": 2
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_assets(
            project_id="project-123",
            asset_type="table"
        )
        
        # Verify
        assert len(result["assets"]) == 2
        assert all(asset["type"] == "table" for asset in result["assets"])
        
        # Verify the API call
        call_args = provider.session.get.call_args
        
        # Check URL contains type parameter
        assert "type=table" in call_args[0][0]
    
    def test_get_assets_with_asset_type_column(self, provider):
        """Test getting assets filtered by type=column."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "assets": [
                {"id": "asset-col-1", "type": "column"},
                {"id": "asset-col-2", "type": "column"}
            ],
            "total_count": 2
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_assets(
            catalog_id="catalog-456",
            asset_type="column"
        )
        
        # Verify
        assert len(result["assets"]) == 2
        assert all(asset["type"] == "column" for asset in result["assets"])
        
        # Verify the API call
        call_args = provider.session.get.call_args
        
        # Check URL contains type parameter
        assert "type=column" in call_args[0][0]
    
    def test_get_assets_missing_both_ids(self, provider):
        """Test getting assets without project_id or catalog_id."""
        with pytest.raises(ValueError) as exc_info:
            provider.get_assets()
        
        assert "Either project_id or catalog_id must be provided" in str(exc_info.value)
    
    def test_get_assets_both_ids_provided(self, provider):
        """Test getting assets with both project_id and catalog_id."""
        with pytest.raises(ValueError) as exc_info:
            provider.get_assets(
                project_id="project-123",
                catalog_id="catalog-456"
            )
        
        assert "Only one of project_id or catalog_id should be provided" in str(exc_info.value)
    
    def test_get_assets_api_failure(self, provider):
        """Test failed get assets request."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Project not found"
        provider.session.get.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider.get_assets(project_id="invalid-project")
        
        assert "Failed to get assets" in str(exc_info.value)
        assert "404" in str(exc_info.value)
        assert "Project not found" in str(exc_info.value)
    
    def test_get_assets_empty_result(self, provider):
        """Test getting assets with no results."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "assets": [],
            "total_count": 0
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_assets(project_id="project-empty")
        
        # Verify
        assert result["assets"] == []
        assert result["total_count"] == 0
    
    def test_get_assets_with_pagination_info(self, provider):
        """Test getting assets with pagination information."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "assets": [{"id": f"asset-{i}"} for i in range(100)],
            "total_count": 250,
            "next": {
                "start": "next-page-token"
            }
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_assets(
            project_id="project-123",
            limit=100
        )
        
        # Verify
        assert len(result["assets"]) == 100
        assert result["total_count"] == 250
        assert "next" in result
        assert result["next"]["start"] == "next-page-token"
    
    def test_get_assets_unauthorized(self, provider):
        """Test getting assets with unauthorized access."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        provider.session.get.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider.get_assets(project_id="project-123")
        
        assert "Failed to get assets" in str(exc_info.value)
        assert "401" in str(exc_info.value)
    
    def test_get_assets_server_error(self, provider):
        """Test getting assets with server error."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        provider.session.get.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider.get_assets(catalog_id="catalog-123")
        
        assert "Failed to get assets" in str(exc_info.value)
        assert "500" in str(exc_info.value)
        assert "Internal server error" in str(exc_info.value)
    
    def test_get_assets_with_complex_response(self, provider):
        """Test getting assets with complex nested response."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "assets": [
                {
                    "id": "asset-complex-1",
                    "name": "ComplexTable",
                    "type": "table",
                    "metadata": {
                        "columns": ["col1", "col2"],
                        "row_count": 1000
                    },
                    "children": [
                        {"id": "child-1", "type": "column"},
                        {"id": "child-2", "type": "column"}
                    ]
                }
            ],
            "total_count": 1
        })
        provider.session.get.return_value = mock_response
        
        # Execute
        result = provider.get_assets(
            project_id="project-123",
            include_children=True
        )
        
        # Verify
        assert len(result["assets"]) == 1
        asset = result["assets"][0]
        assert asset["id"] == "asset-complex-1"
        assert "metadata" in asset
        assert "children" in asset
        assert len(asset["children"]) == 2