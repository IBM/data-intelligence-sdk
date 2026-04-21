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

from wxdi.dq_validator.provider import ProviderConfig, DimensionsProvider


class TestDimensionsProvider:
    """Test suite for DimensionsProvider class."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return ProviderConfig(
            url="https://test-instance.com",
            auth_token="Bearer test-token"
        )
    
    @pytest.fixture
    def provider(self, config):
        """Create a test DimensionsProvider instance."""
        with patch('wxdi.dq_validator.provider.base_provider.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            provider = DimensionsProvider(config)
            yield provider
    
    # ==================== search_dimension Tests ====================
    
    def test_search_dimension_success(self, provider):
        """Test successful dimension search."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "dimensions": [
                {
                    "id": "371114cd-5516-4691-8b2e-1e66edf66486",
                    "name": "Completeness",
                    "description": "Data is complete if it contains all required values.",
                    "is_default": True
                }
            ]
        })
        provider.session.post.return_value = mock_response
        
        # Execute
        result = provider.search_dimension("Completeness")
        
        # Verify
        assert result == "371114cd-5516-4691-8b2e-1e66edf66486"
        
        # Verify the API call
        provider.session.post.assert_called_once()
        call_args = provider.session.post.call_args
        
        # Check URL
        assert "https://test-instance.com/data_quality/v4/search_dq_dimension" in call_args[0][0]
        assert "name=Completeness" in call_args[0][0]
        
        # Check headers
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["Content-Type"] == "application/json"
    
    def test_search_dimension_case_insensitive(self, provider):
        """Test case-insensitive dimension search."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "dimensions": [
                {
                    "id": "accuracy-id-123",
                    "name": "Accuracy",
                    "description": "Data accuracy dimension"
                }
            ]
        })
        provider.session.post.return_value = mock_response
        
        # Execute with lowercase
        result = provider.search_dimension("accuracy")
        
        # Verify - should match case-insensitively
        assert result == "accuracy-id-123"
    
    def test_search_dimension_multiple_results(self, provider):
        """Test searching when API returns multiple dimensions."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "dimensions": [
                {
                    "id": "completeness-id",
                    "name": "Completeness",
                    "description": "Completeness dimension"
                },
                {
                    "id": "accuracy-id",
                    "name": "Accuracy",
                    "description": "Accuracy dimension"
                },
                {
                    "id": "validity-id",
                    "name": "Validity",
                    "description": "Validity dimension"
                }
            ]
        })
        provider.session.post.return_value = mock_response
        
        # Execute - search for Accuracy
        result = provider.search_dimension("Accuracy")
        
        # Verify - should find the correct one
        assert result == "accuracy-id"
    
    def test_search_dimension_api_failure(self, provider):
        """Test failed dimension search request."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        provider.session.post.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider.search_dimension("Completeness")
        
        assert "Failed to get dimension" in str(exc_info.value)
        assert "500" in str(exc_info.value)
    
    def test_search_dimension_not_found_empty_list(self, provider):
        """Test searching when API returns empty list."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "dimensions": []
        })
        provider.session.post.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider.search_dimension("NonExistent")
        
        assert "Dimension with name 'NonExistent' not found" in str(exc_info.value)
    
    def test_search_dimension_not_found_no_match(self, provider):
        """Test searching when name doesn't match any result."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "dimensions": [
                {
                    "id": "completeness-id",
                    "name": "Completeness",
                    "description": "Completeness dimension"
                }
            ]
        })
        provider.session.post.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider.search_dimension("InvalidDimension")
        
        assert "Dimension with name 'InvalidDimension' not found in results" in str(exc_info.value)
    
    def test_search_dimension_missing_id_in_response(self, provider):
        """Test searching when ID is missing in response."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "dimensions": [
                {
                    "name": "Completeness",
                    "description": "Completeness dimension"
                    # Missing "id" field
                }
            ]
        })
        provider.session.post.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider.search_dimension("Completeness")
        
        assert "Dimension ID not found in response" in str(exc_info.value)
    
    def test_search_dimension_missing_dimensions_key(self, provider):
        """Test searching when response doesn't have 'dimensions' key."""
        # Setup mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = json.dumps({
            "data": []
            # Missing "dimensions" key
        })
        provider.session.post.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(ValueError) as exc_info:
            provider.search_dimension("Completeness")
        
        assert "Dimension with name 'Completeness' not found" in str(exc_info.value)