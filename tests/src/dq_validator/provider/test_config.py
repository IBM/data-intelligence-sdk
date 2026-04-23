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
Test suite for ProviderConfig module
"""

import pytest
from unittest.mock import Mock, patch
from wxdi.dq_validator.provider.config import ProviderConfig
from wxdi.common.auth.auth_config import AuthConfig, EnvironmentType


class TestProviderConfig:
    """Test cases for ProviderConfig class"""

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
    def auth_config_ibm_cloud(self):
        """AuthConfig for IBM Cloud"""
        return AuthConfig(
            environment_type=EnvironmentType.IBM_CLOUD,
            api_key="test-api-key-12345"
        )

    @pytest.fixture
    def auth_config_aws_cloud(self):
        """AuthConfig for AWS Cloud"""
        return AuthConfig(
            environment_type=EnvironmentType.AWS_CLOUD,
            api_key="test-api-key-12345",
            account_id="test-account-id"
        )

    @pytest.fixture
    def auth_config_gov_cloud(self):
        """AuthConfig for Government Cloud"""
        return AuthConfig(
            environment_type=EnvironmentType.GOV_CLOUD,
            api_key="test-api-key-12345"
        )

    @pytest.fixture
    def auth_config_on_prem(self):
        """AuthConfig for On-Premises"""
        return AuthConfig(
            environment_type=EnvironmentType.ON_PREM,
            url="https://on-prem.example.com",
            username="test-user",
            api_key="test-api-key"
        )

    def test_config_with_auth_token_only(self, base_url, auth_token):
        """Test ProviderConfig initialization with auth_token only"""
        config = ProviderConfig(base_url, auth_token=auth_token)
        
        assert config.url == base_url
        assert config._auth_token == auth_token
        assert config.project_id is None
        assert config.catalog_id is None
        assert config.auth_provider is None
        assert config.auth_token == auth_token

    def test_config_with_project_id(self, base_url, auth_token, project_id):
        """Test ProviderConfig initialization with project_id"""
        config = ProviderConfig(base_url, auth_token=auth_token, project_id=project_id)
        
        assert config.url == base_url
        assert config.project_id == project_id
        assert config.catalog_id is None

    def test_config_with_catalog_id(self, base_url, auth_token, catalog_id):
        """Test ProviderConfig initialization with catalog_id"""
        config = ProviderConfig(base_url, auth_token=auth_token, catalog_id=catalog_id)
        
        assert config.url == base_url
        assert config.catalog_id == catalog_id
        assert config.project_id is None

    def test_config_with_auth_config_ibm_cloud(self, base_url, auth_config_ibm_cloud):
        """Test ProviderConfig initialization with AuthConfig for IBM Cloud"""
        with patch('wxdi.dq_validator.provider.config.AuthProvider') as mock_auth_provider:
            mock_provider_instance = Mock()
            mock_provider_instance.get_token.return_value = "mocked-token-12345"
            mock_auth_provider.return_value = mock_provider_instance
            
            config = ProviderConfig(base_url, auth_config=auth_config_ibm_cloud)
            
            assert config.url == base_url
            assert config.auth_provider is not None
            assert config._auth_token is None
            mock_auth_provider.assert_called_once_with(auth_config_ibm_cloud)
            
            # Test that auth_token property calls get_token
            token = config.auth_token
            assert token == "mocked-token-12345"
            mock_provider_instance.get_token.assert_called_once()

    def test_config_with_auth_config_aws_cloud(self, base_url, auth_config_aws_cloud):
        """Test ProviderConfig initialization with AuthConfig for AWS Cloud"""
        with patch('wxdi.dq_validator.provider.config.AuthProvider') as mock_auth_provider:
            mock_provider_instance = Mock()
            mock_provider_instance.get_token.return_value = "aws-token-12345"
            mock_auth_provider.return_value = mock_provider_instance
            
            config = ProviderConfig(base_url, auth_config=auth_config_aws_cloud)
            
            assert config.auth_provider is not None
            mock_auth_provider.assert_called_once_with(auth_config_aws_cloud)
            
            token = config.auth_token
            assert token == "aws-token-12345"

    def test_config_with_auth_config_gov_cloud(self, base_url, auth_config_gov_cloud):
        """Test ProviderConfig initialization with AuthConfig for Government Cloud"""
        with patch('wxdi.dq_validator.provider.config.AuthProvider') as mock_auth_provider:
            mock_provider_instance = Mock()
            mock_provider_instance.get_token.return_value = "gov-token-12345"
            mock_auth_provider.return_value = mock_provider_instance
            
            config = ProviderConfig(base_url, auth_config=auth_config_gov_cloud)
            
            assert config.auth_provider is not None
            token = config.auth_token
            assert token == "gov-token-12345"

    def test_config_with_auth_config_on_prem(self, base_url, auth_config_on_prem):
        """Test ProviderConfig initialization with AuthConfig for On-Premises"""
        with patch('wxdi.dq_validator.provider.config.AuthProvider') as mock_auth_provider:
            mock_provider_instance = Mock()
            mock_provider_instance.get_token.return_value = "on-prem-token-12345"
            mock_auth_provider.return_value = mock_provider_instance
            
            config = ProviderConfig(base_url, auth_config=auth_config_on_prem)
            
            assert config.auth_provider is not None
            token = config.auth_token
            assert token == "on-prem-token-12345"

    def test_config_with_both_auth_token_and_auth_config(
        self, base_url, auth_token, auth_config_ibm_cloud
    ):
        """Test ProviderConfig with both auth_token and auth_config (auth_config takes precedence)"""
        with patch('wxdi.dq_validator.provider.config.AuthProvider') as mock_auth_provider:
            mock_provider_instance = Mock()
            mock_provider_instance.get_token.return_value = "config-token-12345"
            mock_auth_provider.return_value = mock_provider_instance
            
            config = ProviderConfig(
                base_url,
                auth_token=auth_token,
                auth_config=auth_config_ibm_cloud
            )
            
            # auth_config should take precedence
            assert config.auth_provider is not None
            assert config._auth_token == auth_token
            
            # When getting token, auth_provider should be used first
            token = config.auth_token
            assert token == "config-token-12345"
            mock_provider_instance.get_token.assert_called_once()

    def test_config_auth_token_property_with_auth_provider(
        self, base_url, auth_config_ibm_cloud
    ):
        """Test auth_token property when auth_provider is set"""
        with patch('wxdi.dq_validator.provider.config.AuthProvider') as mock_auth_provider:
            mock_provider_instance = Mock()
            mock_provider_instance.get_token.return_value = "provider-token"
            mock_auth_provider.return_value = mock_provider_instance
            
            config = ProviderConfig(base_url, auth_config=auth_config_ibm_cloud)
            
            # First call
            token1 = config.auth_token
            assert token1 == "provider-token"
            
            # Second call - should call get_token again (no caching)
            token2 = config.auth_token
            assert token2 == "provider-token"
            assert mock_provider_instance.get_token.call_count == 2

    def test_config_auth_token_property_with_static_token(self, base_url, auth_token):
        """Test auth_token property when only static token is set"""
        config = ProviderConfig(base_url, auth_token=auth_token)
        
        token = config.auth_token
        assert token == auth_token

    def test_config_auth_token_property_no_auth(self, base_url):
        """Test auth_token property raises error when no authentication is provided"""
        config = ProviderConfig(base_url)
        
        assert config.auth_token == ''

    def test_config_get_auth_token_no_auth(self, base_url):
        """Test auth_token property raises error when no authentication is provided"""
        config = ProviderConfig(base_url)
        
        with pytest.raises(ValueError) as exc_info:
            _ = config.get_auth_token()
        
        assert "No authentication token provided" in str(exc_info.value)

    def test_config_with_all_parameters(
        self, base_url, auth_token, project_id, catalog_id, auth_config_ibm_cloud
    ):
        """Test ProviderConfig with all parameters"""
        with patch('wxdi.dq_validator.provider.config.AuthProvider') as mock_auth_provider:
            mock_provider_instance = Mock()
            returned_token = "full-config-token"
            mock_provider_instance.get_token.return_value = returned_token
            mock_auth_provider.return_value = mock_provider_instance
            
            config = ProviderConfig(
                base_url,
                auth_token=auth_token,
                project_id=project_id,
                catalog_id=catalog_id,
                auth_config=auth_config_ibm_cloud
            )
            
            assert config.url == base_url
            assert config._auth_token == auth_token
            assert config.project_id == project_id
            assert config.catalog_id == catalog_id
            assert config.auth_provider is not None
            assert config.auth_token == returned_token

    def test_config_auth_provider_none_when_no_auth_config(self, base_url, auth_token):
        """Test that auth_provider is None when auth_config is not provided"""
        config = ProviderConfig(base_url, auth_token=auth_token)
        
        assert config.auth_provider is None

    def test_config_with_project_and_catalog(
        self, base_url, auth_token, project_id, catalog_id
    ):
        """Test ProviderConfig with both project_id and catalog_id"""
        config = ProviderConfig(
            base_url,
            auth_token=auth_token,
            project_id=project_id,
            catalog_id=catalog_id
        )
        
        assert config.project_id == project_id
        assert config.catalog_id == catalog_id
        assert config.auth_token == auth_token


# Made with Bob