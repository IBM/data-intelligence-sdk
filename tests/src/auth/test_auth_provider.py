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
Unit tests for AuthProvider module.

Tests the AuthProvider class and its integration with different authenticators.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from wxdi.common.auth import AuthProvider, AuthConfig, EnvironmentType


class TestAuthProviderIBMCloud:
    """Tests for AuthProvider with IBM_CLOUD environment."""
    
    @patch('wxdi.common.auth.auth_provider.IAMAuthenticator')
    def test_ibm_cloud_authenticator_creation(self, mock_iam_auth):
        """Test that IAMAuthenticator is created for IBM_CLOUD."""
        config = AuthConfig(
            environment_type=EnvironmentType.IBM_CLOUD,
            api_key='test-api-key'
        )
        
        provider = AuthProvider(config)
        
        mock_iam_auth.assert_called_once_with(
            apikey='test-api-key',
            url='https://iam.cloud.ibm.com/identity/token'
        )
        assert provider.config == config
    
    @patch('wxdi.common.auth.auth_provider.IAMAuthenticator')
    def test_ibm_cloud_get_token(self, mock_iam_auth):
        """Test getting token from IBM_CLOUD authenticator."""
        mock_token_manager = Mock()
        mock_token_manager.get_token.return_value = 'test-token-123'
        mock_authenticator = Mock()
        mock_authenticator.token_manager = mock_token_manager
        mock_iam_auth.return_value = mock_authenticator
        
        config = AuthConfig(
            environment_type=EnvironmentType.IBM_CLOUD,
            api_key='test-api-key'
        )
        provider = AuthProvider(config)
        
        token = provider.get_token()
        
        assert token == 'test-token-123'
        mock_token_manager.get_token.assert_called_once()


class TestAuthProviderAWSCloud:
    """Tests for AuthProvider with AWS_CLOUD environment."""
    
    @patch('wxdi.common.auth.auth_provider.MCSPV2Authenticator')
    def test_aws_cloud_authenticator_creation(self, mock_mcsp_auth):
        """Test that MCSPV2Authenticator is created for AWS_CLOUD."""
        config = AuthConfig(
            environment_type=EnvironmentType.AWS_CLOUD,
            api_key='test-api-key',
            account_id='account-123'
        )
        
        provider = AuthProvider(config)
        
        mock_mcsp_auth.assert_called_once_with(
            apikey='test-api-key',
            url='https://account-iam.platform.saas.ibm.com',
            scope_collection_type='accounts',
            scope_id='account-123'
        )
    
    @patch('wxdi.common.auth.auth_provider.MCSPV2Authenticator')
    def test_aws_cloud_get_token(self, mock_mcsp_auth):
        """Test getting token from AWS_CLOUD authenticator."""
        mock_token_manager = Mock()
        mock_token_manager.get_token.return_value = 'aws-token-456'
        mock_authenticator = Mock()
        mock_authenticator.token_manager = mock_token_manager
        mock_mcsp_auth.return_value = mock_authenticator
        
        config = AuthConfig(
            environment_type=EnvironmentType.AWS_CLOUD,
            api_key='test-api-key',
            account_id='account-123'
        )
        provider = AuthProvider(config)
        
        token = provider.get_token()
        
        assert token == 'aws-token-456'
        mock_token_manager.get_token.assert_called_once()


class TestAuthProviderGovCloud:
    """Tests for AuthProvider with GOV_CLOUD environment."""
    
    @patch('wxdi.common.auth.auth_provider.GovCloudAuthenticator')
    def test_gov_cloud_authenticator_creation(self, mock_gov_cloud_auth):
        """Test that CustomAuthenticator is created for GOV_CLOUD."""
        config = AuthConfig(
            environment_type=EnvironmentType.GOV_CLOUD,
            api_key='test-api-key'
        )
        
        provider = AuthProvider(config)
        
        mock_gov_cloud_auth.assert_called_once_with(
            apikey='test-api-key',
            url='https://dai.ibmforusgov.com/api/rest/mcsp/apikeys/token',
            disable_ssl_verification=True
        )
    
    @patch('wxdi.common.auth.auth_provider.GovCloudAuthenticator')
    def test_gov_cloud_get_token(self, mock_gov_cloud_auth):
        """Test getting token from GOV_CLOUD authenticator."""
        mock_token_manager = Mock()
        mock_token_manager.get_token.return_value = 'gov-token-789'
        mock_authenticator = Mock()
        mock_authenticator.token_manager = mock_token_manager
        mock_gov_cloud_auth.return_value = mock_authenticator
        
        config = AuthConfig(
            environment_type=EnvironmentType.GOV_CLOUD,
            api_key='test-api-key'
        )
        provider = AuthProvider(config)
        
        token = provider.get_token()
        
        assert token == 'gov-token-789'
        mock_token_manager.get_token.assert_called_once()


class TestAuthProviderOnPrem:
    """Tests for AuthProvider with ON_PREM environment."""
    
    @patch('wxdi.common.auth.auth_provider.CloudPakForDataAuthenticator')
    def test_on_prem_with_api_key(self, mock_cp4d_auth):
        """Test CloudPakForDataAuthenticator creation with API key."""
        config = AuthConfig(
            environment_type=EnvironmentType.ON_PREM,
            url='https://cpd.example.com',
            username='admin',
            api_key='test-key'
        )
        
        provider = AuthProvider(config)
        
        mock_cp4d_auth.assert_called_once_with(
            username='admin',
            url='https://cpd.example.com/icp4d-api/v1/authorize',
            apikey='test-key',
            disable_ssl_verification=True
        )
    
    @patch('wxdi.common.auth.auth_provider.CloudPakForDataAuthenticator')
    def test_on_prem_with_password(self, mock_cp4d_auth):
        """Test CloudPakForDataAuthenticator creation with password."""
        config = AuthConfig(
            environment_type=EnvironmentType.ON_PREM,
            url='https://cpd.example.com',
            username='admin',
            password='secret'
        )
        
        provider = AuthProvider(config)
        
        mock_cp4d_auth.assert_called_once_with(
            username='admin',
            password='secret',
            url='https://cpd.example.com/icp4d-api/v1/authorize',
            disable_ssl_verification=True
        )
    
    @patch('wxdi.common.auth.auth_provider.CloudPakForDataAuthenticator')
    def test_on_prem_get_token(self, mock_cp4d_auth):
        """Test getting token from ON_PREM authenticator."""
        mock_token_manager = Mock()
        mock_token_manager.get_token.return_value = 'on-prem-token-abc'
        mock_authenticator = Mock()
        mock_authenticator.token_manager = mock_token_manager
        mock_cp4d_auth.return_value = mock_authenticator
        
        config = AuthConfig(
            environment_type=EnvironmentType.ON_PREM,
            url='https://cpd.example.com',
            username='admin',
            api_key='test-key'
        )
        provider = AuthProvider(config)
        
        token = provider.get_token()
        
        assert token == 'on-prem-token-abc'
        mock_token_manager.get_token.assert_called_once()


class TestAuthProviderEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_invalid_config_type(self):
        """Test that invalid config type raises AttributeError."""
        with pytest.raises(AttributeError):
            AuthProvider("invalid-config")  # type: ignore
    
    @patch('wxdi.common.auth.auth_provider.IAMAuthenticator')
    def test_token_manager_none(self, mock_iam_auth):
        """Test handling when token_manager is None."""
        mock_authenticator = Mock()
        mock_authenticator.token_manager = None
        mock_iam_auth.return_value = mock_authenticator
        
        config = AuthConfig(
            environment_type=EnvironmentType.IBM_CLOUD,
            api_key='test-api-key'
        )
        provider = AuthProvider(config)
        
        with pytest.raises(Exception, match="does not have token_manager"):
            provider.get_token()
    
    @patch('wxdi.common.auth.auth_provider.IAMAuthenticator')
    def test_multiple_token_requests(self, mock_iam_auth):
        """Test multiple token requests use the same authenticator."""
        mock_token_manager = Mock()
        mock_token_manager.get_token.side_effect = ['token1', 'token2', 'token3']
        mock_authenticator = Mock()
        mock_authenticator.token_manager = mock_token_manager
        mock_iam_auth.return_value = mock_authenticator
        
        config = AuthConfig(
            environment_type=EnvironmentType.IBM_CLOUD,
            api_key='test-api-key'
        )
        provider = AuthProvider(config)
        
        token1 = provider.get_token()
        token2 = provider.get_token()
        token3 = provider.get_token()
        
        assert token1 == 'token1'
        assert token2 == 'token2'
        assert token3 == 'token3'
        assert mock_token_manager.get_token.call_count == 3
        # Authenticator should only be created once
        assert mock_iam_auth.call_count == 1


class TestAuthProviderIntegration:
    """Integration tests for AuthProvider."""
    
    @patch('wxdi.common.auth.auth_provider.IAMAuthenticator')
    @patch('wxdi.common.auth.auth_provider.GovCloudAuthenticator')
    @patch('wxdi.common.auth.auth_provider.MCSPV2Authenticator')
    @patch('wxdi.common.auth.auth_provider.CloudPakForDataAuthenticator')
    def test_different_environments_use_different_authenticators(
        self, mock_cp4d, mock_mcsp, mock_custom, mock_iam
    ):
        """Test that different environments create different authenticators."""
        # IBM Cloud
        config1 = AuthConfig(
            environment_type=EnvironmentType.IBM_CLOUD,
            api_key='key1'
        )
        AuthProvider(config1)
        assert mock_iam.call_count == 1
        
        # AWS Cloud - uses MCSPV2Authenticator
        config2 = AuthConfig(
            environment_type=EnvironmentType.AWS_CLOUD,
            api_key='key2',
            account_id='account-123'
        )
        AuthProvider(config2)
        assert mock_mcsp.call_count == 1
        
        # Gov Cloud - uses CustomAuthenticator
        config3 = AuthConfig(
            environment_type=EnvironmentType.GOV_CLOUD,
            api_key='key3'
        )
        AuthProvider(config3)
        assert mock_custom.call_count == 1
        
        # On-Prem
        config4 = AuthConfig(
            environment_type=EnvironmentType.ON_PREM,
            url='https://cpd.example.com',
            username='admin',
            api_key='key4'
        )
        AuthProvider(config4)
        assert mock_cp4d.call_count == 1