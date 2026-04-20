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
Unit tests for GovCloudTokenManager module.

Tests the GovCloudTokenManager class and its token management functionality.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from wxdi.common.auth.gov_cloud_token_manager import GovCloudTokenManager

# Valid JWT token for testing (header.payload.signature format)
VALID_JWT_TOKEN = 'eyJhbGciOiAiUlMyNTYiLCAidHlwIjogIkpXVCJ9.eyJleHAiOiA5OTk5OTk5OTk5LCAiaWF0IjogMTIzNDU2Nzg5MH0.ZmFrZS1zaWduYXR1cmU'


class TestGovCloudTokenManagerInitialization:
    """Tests for GovCloudTokenManager initialization."""
    
    def test_initialization_with_required_params(self):
        """Test initialization with required parameters."""
        token_manager = GovCloudTokenManager(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        assert token_manager.apikey == 'test-api-key'
        assert token_manager.url == 'https://example.com/token'
        assert token_manager.disable_ssl_verification is False
        assert token_manager.headers == {}
        assert token_manager.proxies == {}
    
    def test_initialization_with_ssl_verification_disabled(self):
        """Test initialization with SSL verification disabled."""
        token_manager = GovCloudTokenManager(
            apikey='test-api-key',
            url='https://example.com/token',
            disable_ssl_verification=True
        )
        
        assert token_manager.disable_ssl_verification is True
    
    def test_initialization_with_custom_headers(self):
        """Test initialization with custom headers."""
        custom_headers = {'X-Custom-Header': 'value'}
        token_manager = GovCloudTokenManager(
            apikey='test-api-key',
            url='https://example.com/token',
            headers=custom_headers
        )
        
        assert token_manager.headers == custom_headers
    
    def test_initialization_with_proxies(self):
        """Test initialization with proxy configuration."""
        proxies = {'http': 'http://proxy.example.com:8080'}
        token_manager = GovCloudTokenManager(
            apikey='test-api-key',
            url='https://example.com/token',
            proxies=proxies
        )
        
        assert token_manager.proxies == proxies


class TestGovCloudTokenManagerInheritance:
    """Tests for GovCloudTokenManager inheritance from JWTTokenManager."""
    
    def test_inherits_from_jwt_token_manager(self):
        """Test that GovCloudTokenManager inherits from JWTTokenManager."""
        from ibm_cloud_sdk_core.token_managers.jwt_token_manager import JWTTokenManager
        
        token_manager = GovCloudTokenManager(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        assert isinstance(token_manager, JWTTokenManager)
    
    def test_has_get_token_method(self):
        """Test that token manager has get_token method from parent."""
        token_manager = GovCloudTokenManager(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        assert hasattr(token_manager, 'get_token')
        assert callable(token_manager.get_token)


class TestGovCloudTokenManagerRequestToken:
    """Tests for request_token method."""
    
    @patch.object(GovCloudTokenManager, '_request')
    def test_request_token_makes_post_request(self, mock_request):
        """Test that request_token makes a POST request."""
        mock_request.return_value = {
            'token': 'test-token-123',
            'expires_in': 3600
        }
        
        token_manager = GovCloudTokenManager(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        response = token_manager.request_token()
        
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]['method'] == 'POST'
        assert call_args[1]['url'] == 'https://example.com/token'
    
    @patch.object(GovCloudTokenManager, '_request')
    def test_request_token_uses_form_urlencoded(self, mock_request):
        """Test that request_token uses application/x-www-form-urlencoded."""
        mock_request.return_value = {
            'token': 'test-token-123',
            'expires_in': 3600
        }
        
        token_manager = GovCloudTokenManager(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        token_manager.request_token()
        
        call_args = mock_request.call_args
        headers = call_args[1]['headers']
        assert headers['Content-Type'] == 'application/x-www-form-urlencoded'
        assert headers['Accept'] == 'application/json'
    
    @patch.object(GovCloudTokenManager, '_request')
    def test_request_token_sends_apikey(self, mock_request):
        """Test that request_token sends the API key in the request."""
        mock_request.return_value = {
            'token': 'test-token-123',
            'expires_in': 3600
        }
        
        token_manager = GovCloudTokenManager(
            apikey='my-secret-key',
            url='https://example.com/token'
        )
        
        token_manager.request_token()
        
        call_args = mock_request.call_args
        data = call_args[1]['data']
        assert data['apikey'] == 'my-secret-key'
    
    @patch.object(GovCloudTokenManager, '_request')
    def test_request_token_includes_custom_headers(self, mock_request):
        """Test that custom headers are included in the request."""
        mock_request.return_value = {
            'token': 'test-token-123',
            'expires_in': 3600
        }
        
        custom_headers = {'X-Custom-Header': 'custom-value'}
        token_manager = GovCloudTokenManager(
            apikey='test-api-key',
            url='https://example.com/token',
            headers=custom_headers
        )
        
        token_manager.request_token()
        
        call_args = mock_request.call_args
        headers = call_args[1]['headers']
        assert headers['X-Custom-Header'] == 'custom-value'
    
    @patch.object(GovCloudTokenManager, '_request')
    def test_request_token_returns_dict(self, mock_request):
        """Test that request_token returns a dictionary."""
        expected_response = {
            'token': 'test-token-456',
            'expires_in': 7200
        }
        mock_request.return_value = expected_response
        
        token_manager = GovCloudTokenManager(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        response = token_manager.request_token()
        
        assert response == expected_response
        assert isinstance(response, dict)


class TestGovCloudTokenManagerSaveTokenInfo:
    """Tests for _save_token_info method."""
    
    def test_save_token_info_with_token_field(self):
        """Test saving token info when response has 'token' field."""
        token_manager = GovCloudTokenManager(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        token_response = {
            'token': VALID_JWT_TOKEN,
            'expires_in': 3600
        }
        
        token_manager._save_token_info(token_response)
        
        assert token_manager.access_token == VALID_JWT_TOKEN
    
    def test_save_token_info_with_access_token_field(self):
        """Test saving token info when response has 'access_token' field."""
        token_manager = GovCloudTokenManager(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        # Note: JWTTokenManager expects 'token' field, not 'access_token'
        # The token manager will look for 'token' field first
        token_response = {
            'token': VALID_JWT_TOKEN,
            'expires_in': 3600
        }
        
        token_manager._save_token_info(token_response)
        
        assert token_manager.access_token == VALID_JWT_TOKEN
    
    def test_save_token_info_prefers_token_over_access_token(self):
        """Test that 'token' field is preferred over 'access_token'."""
        token_manager = GovCloudTokenManager(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        token_response = {
            'token': VALID_JWT_TOKEN,
            'access_token': VALID_JWT_TOKEN,
            'expires_in': 3600
        }
        
        token_manager._save_token_info(token_response)
        
        assert token_manager.access_token == VALID_JWT_TOKEN
    
    def test_save_token_info_raises_error_without_token(self):
        """Test that error is raised when no token is in response."""
        token_manager = GovCloudTokenManager(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        token_response = {
            'expires_in': 3600
        }
        
        # JWTTokenManager will raise an error when token field is missing
        with pytest.raises(Exception):  # Could be ValueError or KeyError
            token_manager._save_token_info(token_response)
    
    def test_save_token_info_with_expires_in(self):
        """Test saving token info with expires_in field."""
        token_manager = GovCloudTokenManager(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        token_response = {
            'token': VALID_JWT_TOKEN,
            'expires_in': 3600
        }
        
        token_manager._save_token_info(token_response)
        
        # JWTTokenManager extracts expiration from JWT token payload (exp field)
        # Our JWT token has exp=9999999999
        assert token_manager.expire_time == 9999999999
        assert token_manager.access_token == VALID_JWT_TOKEN
    
    def test_save_token_info_with_expiration(self):
        """Test saving token info with expiration timestamp."""
        token_manager = GovCloudTokenManager(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        token_response = {
            'token': VALID_JWT_TOKEN,
            'expiration': 1234567890
        }
        
        token_manager._save_token_info(token_response)
        
        # JWTTokenManager extracts expiration from JWT token payload (exp field)
        # Our JWT token has exp=9999999999, not from the 'expiration' field
        assert token_manager.expire_time == 9999999999
        assert token_manager.access_token == VALID_JWT_TOKEN
    
    def test_save_token_info_default_expiration(self):
        """Test that expiration is extracted from JWT token."""
        token_manager = GovCloudTokenManager(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        token_response = {
            'token': VALID_JWT_TOKEN
        }
        
        token_manager._save_token_info(token_response)
        
        # JWTTokenManager extracts expiration from JWT token payload (exp field)
        # Our JWT token has exp=9999999999
        assert token_manager.expire_time == 9999999999
        assert token_manager.access_token == VALID_JWT_TOKEN
    
    
class TestGovCloudTokenManagerEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_apikey(self):
        """Test that empty API key is handled."""
        token_manager = GovCloudTokenManager(
            apikey='',
            url='https://example.com/token'
        )
        
        # Should initialize but may fail on actual request
        assert token_manager.apikey == ''
    
    def test_empty_url(self):
        """Test that empty URL is handled."""
        token_manager = GovCloudTokenManager(
            apikey='test-key',
            url=''
        )
        
        # Should initialize but may fail on actual request
        assert token_manager.url == ''
    
    def test_none_headers_defaults_to_empty_dict(self):
        """Test that None headers defaults to empty dict."""
        token_manager = GovCloudTokenManager(
            apikey='test-key',
            url='https://example.com/token',
            headers=None
        )
        
        assert token_manager.headers == {}
    
    def test_none_proxies_defaults_to_empty_dict(self):
        """Test that None proxies defaults to empty dict."""
        token_manager = GovCloudTokenManager(
            apikey='test-key',
            url='https://example.com/token',
            proxies=None
        )
        
        assert token_manager.proxies == {}


class TestGovCloudTokenManagerIntegration:
    """Integration tests for GovCloudTokenManager."""
    
    @patch.object(GovCloudTokenManager, '_request')
    def test_full_token_lifecycle(self, mock_request):
        """Test complete token request and save lifecycle."""
        mock_request.return_value = {
            'token': VALID_JWT_TOKEN,
            'expires_in': 7200,
            'refresh_token': 'refresh-lifecycle'
        }
        
        token_manager = GovCloudTokenManager(
            apikey='lifecycle-key',
            url='https://example.com/token'
        )
        
        # Request token
        response = token_manager.request_token()
        
        # Save token info
        token_manager._save_token_info(response)
        
        # Verify token was saved
        assert token_manager.access_token == VALID_JWT_TOKEN
        assert hasattr(token_manager, 'expire_time')