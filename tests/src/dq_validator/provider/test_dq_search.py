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
Tests for DQSearchProvider
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from wxdi.dq_validator.provider import ProviderConfig, DQSearchProvider


@pytest.fixture
def config():
    """Create a test configuration"""
    return ProviderConfig(
        url="https://test.example.com",
        auth_token="Bearer test-token",
        project_id="test-project-id"
    )


@pytest.fixture
def provider(config):
    """Create a DQSearchProvider instance"""
    with patch('wxdi.dq_validator.provider.base_provider.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        provider = DQSearchProvider(config)
        yield provider


class TestSearchDQCheck:
    """Tests for search_dq_check method"""
    
    def test_search_dq_check_success_with_project_id(self, provider):
        """Test successful DQ check search with project_id"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = '''{
            "id": "ad277842-dea7-44ef-8e4b-d940df0f79aa",
            "account_id": "999",
            "created_at": "2025-12-19T06:37:23.519Z",
            "dimension": {
                "id": "ec453723-669c-48bb-82c1-11b69b3b8c93",
                "name": "Validity"
            },
            "name": "Format check",
            "native_id": "b2debda2-6ab9-4a39-8c23-17954e004dcf/7377e2cd-ac0e-4833-8760-fd0e8cb682aa",
            "wkc_container_id": "24419069-d649-45cb-a2c1-64d6eed650d5",
            "type": "format"
        }'''
        provider.session.post.return_value = mock_response
        
        result = provider.search_dq_check(
            native_id="b2debda2-6ab9-4a39-8c23-17954e004dcf/7377e2cd-ac0e-4833-8760-fd0e8cb682aa",
            check_type="format",
            project_id="24419069-d649-45cb-a2c1-64d6eed650d5"
        )
        
        assert result['id'] == "ad277842-dea7-44ef-8e4b-d940df0f79aa"
        assert result['name'] == "Format check"
        assert result['type'] == "format"
        assert result['native_id'] == "b2debda2-6ab9-4a39-8c23-17954e004dcf/7377e2cd-ac0e-4833-8760-fd0e8cb682aa"
        
        # Verify project_id is in the URL
        call_args = provider.session.post.call_args
        assert "project_id=24419069-d649-45cb-a2c1-64d6eed650d5" in call_args[0][0]
    
    def test_search_dq_check_success_with_catalog_id(self, provider):
        """Test successful DQ check search with catalog_id"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = '''{
            "id": "ad277842-dea7-44ef-8e4b-d940df0f79aa",
            "name": "Format check",
            "type": "format"
        }'''
        provider.session.post.return_value = mock_response
        
        result = provider.search_dq_check(
            native_id="test-native-id",
            check_type="format",
            catalog_id="catalog-123"
        )
        
        assert result['id'] == "ad277842-dea7-44ef-8e4b-d940df0f79aa"
        
        # Verify catalog_id is in the URL
        call_args = provider.session.post.call_args
        assert "catalog_id=catalog-123" in call_args[0][0]
        assert "project_id" not in call_args[0][0]
    
    def test_search_dq_check_missing_both_ids(self, provider):
        """Test DQ check search without project_id or catalog_id"""
        with pytest.raises(ValueError) as exc_info:
            provider.search_dq_check(
                native_id="test-id",
                check_type="format"
            )
        
        assert "Either project_id or catalog_id must be provided" in str(exc_info.value)
    
    def test_search_dq_check_both_ids_provided(self, provider):
        """Test DQ check search with both project_id and catalog_id"""
        with pytest.raises(ValueError) as exc_info:
            provider.search_dq_check(
                native_id="test-id",
                check_type="format",
                project_id="project-123",
                catalog_id="catalog-123"
            )
        
        assert "Only one of project_id or catalog_id should be provided" in str(exc_info.value)
    
    def test_search_dq_check_failure(self, provider):
        """Test DQ check search failure"""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Not found"
        provider.session.post.return_value = mock_response
        
        with pytest.raises(ValueError) as exc_info:
            provider.search_dq_check(
                native_id="invalid-id",
                check_type="format",
                project_id="test-project"
            )
        
        assert "Failed to search DQ check" in str(exc_info.value)
        assert "404" in str(exc_info.value)
    
    def test_search_dq_check_with_include_children(self, provider):
        """Test DQ check search with include_children parameter"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = '{"id": "test-id", "type": "format"}'
        provider.session.post.return_value = mock_response
        
        provider.search_dq_check(
            native_id="test-native-id",
            check_type="format",
            project_id="test-project",
            include_children=False
        )
        
        # Verify the URL contains include_children=false
        call_args = provider.session.post.call_args
        assert "include_children=false" in call_args[0][0]


class TestSearchDQAsset:
    """Tests for search_dq_asset method"""
    
    def test_search_dq_asset_success_with_project_id(self, provider):
        """Test successful DQ asset search with project_id"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = '''{
            "id": "1488a413-99f9-4bed-906d-c33b505d5728",
            "account_id": "999",
            "created_at": "2026-01-28T14:08:08.380Z",
            "name": "RTN",
            "native_id": "b2debda2-6ab9-4a39-8c23-17954e004dcf/RTN",
            "wkc_container_id": "24419069-d649-45cb-a2c1-64d6eed650d5",
            "type": "column"
        }'''
        provider.session.post.return_value = mock_response
        
        result = provider.search_dq_asset(
            native_id="b2debda2-6ab9-4a39-8c23-17954e004dcf/RTN",
            project_id="24419069-d649-45cb-a2c1-64d6eed650d5",
            asset_type="column"
        )
        
        assert result['id'] == "1488a413-99f9-4bed-906d-c33b505d5728"
        assert result['name'] == "RTN"
        assert result['type'] == "column"
        assert result['native_id'] == "b2debda2-6ab9-4a39-8c23-17954e004dcf/RTN"
        
        # Verify project_id is in the URL
        call_args = provider.session.post.call_args
        assert "project_id=24419069-d649-45cb-a2c1-64d6eed650d5" in call_args[0][0]
    
    def test_search_dq_asset_success_with_catalog_id(self, provider):
        """Test successful DQ asset search with catalog_id"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = '''{
            "id": "test-asset-id",
            "name": "Test Asset",
            "type": "column"
        }'''
        provider.session.post.return_value = mock_response
        
        result = provider.search_dq_asset(
            native_id="test-native-id",
            catalog_id="catalog-123",
            asset_type="column"
        )
        
        assert result['id'] == "test-asset-id"
        
        # Verify catalog_id is in the URL
        call_args = provider.session.post.call_args
        assert "catalog_id=catalog-123" in call_args[0][0]
        assert "project_id" not in call_args[0][0]
    
    def test_search_dq_asset_missing_both_ids(self, provider):
        """Test DQ asset search without project_id or catalog_id"""
        with pytest.raises(ValueError) as exc_info:
            provider.search_dq_asset(
                native_id="test-id"
            )
        
        assert "Either project_id or catalog_id must be provided" in str(exc_info.value)
    
    def test_search_dq_asset_both_ids_provided(self, provider):
        """Test DQ asset search with both project_id and catalog_id"""
        with pytest.raises(ValueError) as exc_info:
            provider.search_dq_asset(
                native_id="test-id",
                project_id="project-123",
                catalog_id="catalog-123"
            )
        
        assert "Only one of project_id or catalog_id should be provided" in str(exc_info.value)
    
    def test_search_dq_asset_failure(self, provider):
        """Test DQ asset search failure"""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Not found"
        provider.session.post.return_value = mock_response
        
        with pytest.raises(ValueError) as exc_info:
            provider.search_dq_asset(
                native_id="invalid-id",
                project_id="test-project"
            )
        
        assert "Failed to search DQ asset" in str(exc_info.value)
        assert "404" in str(exc_info.value)
    
    def test_search_dq_asset_with_optional_params(self, provider):
        """Test DQ asset search with optional parameters"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = '{"id": "test-id", "type": "column"}'
        provider.session.post.return_value = mock_response
        
        provider.search_dq_asset(
            native_id="test-native-id",
            project_id="test-project",
            asset_type="table",
            include_children=False,
            get_actual_asset=True
        )
        
        # Verify the URL contains the parameters
        call_args = provider.session.post.call_args
        url = call_args[0][0]
        assert "type=table" in url
        assert "include_children=false" in url
        assert "get_actual_asset=true" in url