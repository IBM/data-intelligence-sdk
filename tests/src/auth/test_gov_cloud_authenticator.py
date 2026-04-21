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
Unit tests for GovCloudAuthenticator module.

Tests the GovCloudAuthenticator class and its integration with GovCloudTokenManager.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from wxdi.common.auth.gov_cloud_authenticator import GovCloudAuthenticator


class TestGovCloudAuthenticatorInitialization:
    """Tests for GovCloudAuthenticator initialization."""
    
    def test_initialization_with_required_params(self):
        """Test initialization with required parameters."""
        authenticator = GovCloudAuthenticator(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        assert authenticator.token_manager is not None
        assert authenticator.token_manager.apikey == 'test-api-key'
        assert authenticator.token_manager.url == 'https://example.com/token'
    
    def test_initialization_with_ssl_verification_disabled(self):
        """Test initialization with SSL verification disabled."""
        authenticator = GovCloudAuthenticator(
            apikey='test-api-key',
            url='https://example.com/token',
            disable_ssl_verification=True
        )
        
        assert authenticator.token_manager.disable_ssl_verification is True
    
    def test_initialization_with_ssl_verification_enabled(self):
        """Test initialization with SSL verification enabled (default)."""
        authenticator = GovCloudAuthenticator(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        assert authenticator.token_manager.disable_ssl_verification is False


class TestGovCloudAuthenticatorValidation:
    """Tests for GovCloudAuthenticator validation."""
    
    def test_validate_with_valid_config(self):
        """Test validation with valid configuration."""
        authenticator = GovCloudAuthenticator(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        # Should not raise any exception
        authenticator.validate()
    
    def test_validate_with_missing_apikey(self):
        """Test validation fails with missing API key."""
        with pytest.raises(ValueError, match="apikey"):
            GovCloudAuthenticator(
                apikey='',
                url='https://example.com/token'
            )
    
    def test_validate_with_missing_url(self):
        """Test validation fails with missing URL."""
        with pytest.raises(ValueError, match="url"):
            GovCloudAuthenticator(
                apikey='test-api-key',
                url=''
            )


class TestGovCloudAuthenticatorTokenManagement:
    """Tests for GovCloudAuthenticator token management."""
    
    @patch('wxdi.common.auth.gov_cloud_authenticator.GovCloudTokenManager')
    def test_token_manager_creation(self, mock_token_manager_class):
        """Test that GovCloudTokenManager is created correctly."""
        mock_token_manager = Mock()
        mock_token_manager_class.return_value = mock_token_manager
        
        authenticator = GovCloudAuthenticator(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        mock_token_manager_class.assert_called_once_with(
            apikey='test-api-key',
            url='https://example.com/token',
            disable_ssl_verification=False,
            headers=None,
            proxies=None
        )
        assert authenticator.token_manager == mock_token_manager
    
    @patch('wxdi.common.auth.gov_cloud_authenticator.GovCloudTokenManager')
    def test_get_token(self, mock_token_manager_class):
        """Test getting token through token manager."""
        mock_token_manager = Mock()
        mock_token_manager.get_token.return_value = 'test-token-abc123'
        mock_token_manager_class.return_value = mock_token_manager
        
        authenticator = GovCloudAuthenticator(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        token = authenticator.token_manager.get_token()
        
        assert token == 'test-token-abc123'
        mock_token_manager.get_token.assert_called_once()


class TestGovCloudAuthenticatorInheritance:
    """Tests for GovCloudAuthenticator inheritance from IAMRequestBasedAuthenticator."""
    
    def test_inherits_from_iam_request_based_authenticator(self):
        """Test that GovCloudAuthenticator inherits from IAMRequestBasedAuthenticator."""
        from ibm_cloud_sdk_core.authenticators.iam_request_based_authenticator import IAMRequestBasedAuthenticator
        
        authenticator = GovCloudAuthenticator(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        assert isinstance(authenticator, IAMRequestBasedAuthenticator)
    
    def test_has_authentication_type(self):
        """Test that authenticator has authentication_type attribute."""
        authenticator = GovCloudAuthenticator(
            apikey='test-api-key',
            url='https://example.com/token'
        )
        
        # IAMRequestBasedAuthenticator should have authentication_type
        assert hasattr(authenticator, 'authentication_type')


class TestGovCloudAuthenticatorEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_none_apikey(self):
        """Test that None API key raises error."""
        with pytest.raises((ValueError, TypeError)):
            GovCloudAuthenticator(
                apikey=None,  # type: ignore
                url='https://example.com/token'
            )
    
    def test_none_url(self):
        """Test that None URL raises error."""
        with pytest.raises((ValueError, TypeError)):
            GovCloudAuthenticator(
                apikey='test-api-key',
                url=None  # type: ignore
            )
    
    def test_empty_string_apikey(self):
        """Test that empty string API key raises error."""
        with pytest.raises(ValueError):
            GovCloudAuthenticator(
                apikey='',
                url='https://example.com/token'
            )
    
    def test_empty_string_url(self):
        """Test that empty string URL raises error."""
        with pytest.raises(ValueError):
            GovCloudAuthenticator(
                apikey='test-api-key',
                url=''
            )
    
    def test_whitespace_apikey(self):
        """Test that whitespace-only API key is accepted but may fail on validation."""
        # GovCloudAuthenticator doesn't strip whitespace, so it accepts it
        authenticator = GovCloudAuthenticator(
            apikey='   ',
            url='https://example.com/token'
        )
        # The whitespace apikey is stored as-is
        assert authenticator.apikey == '   '
    
    def test_whitespace_url(self):
        """Test that whitespace-only URL is accepted but may fail on validation."""
        # GovCloudAuthenticator doesn't strip whitespace, so it accepts it
        authenticator = GovCloudAuthenticator(
            apikey='test-api-key',
            url='   '
        )
        # The whitespace url is stored as-is
        assert authenticator.url == '   '


class TestGovCloudAuthenticatorIntegration:
    """Integration tests for GovCloudAuthenticator."""
    
    @patch('wxdi.common.auth.gov_cloud_authenticator.GovCloudTokenManager')
    def test_full_authentication_flow(self, mock_token_manager_class):
        """Test complete authentication flow."""
        mock_token_manager = Mock()
        mock_token_manager.get_token.return_value = 'integration-token-xyz'
        mock_token_manager_class.return_value = mock_token_manager
        
        # Create authenticator
        authenticator = GovCloudAuthenticator(
            apikey='integration-key',
            url='https://integration.example.com/token'
        )
        
        # Validate
        authenticator.validate()
        
        # Get token
        token = authenticator.token_manager.get_token()
        
        assert token == 'integration-token-xyz'
        mock_token_manager.get_token.assert_called_once()
    
    @patch('wxdi.common.auth.gov_cloud_authenticator.GovCloudTokenManager')
    def test_multiple_token_requests(self, mock_token_manager_class):
        """Test multiple token requests use the same token manager."""
        mock_token_manager = Mock()
        mock_token_manager.get_token.side_effect = ['token1', 'token2', 'token3']
        mock_token_manager_class.return_value = mock_token_manager
        
        authenticator = GovCloudAuthenticator(
            apikey='test-key',
            url='https://example.com/token'
        )
        
        token1 = authenticator.token_manager.get_token()
        token2 = authenticator.token_manager.get_token()
        token3 = authenticator.token_manager.get_token()
        
        assert token1 == 'token1'
        assert token2 == 'token2'
        assert token3 == 'token3'
        assert mock_token_manager.get_token.call_count == 3
        # Token manager should only be created once
        assert mock_token_manager_class.call_count == 1