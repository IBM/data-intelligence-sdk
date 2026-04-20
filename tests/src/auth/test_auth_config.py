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
Unit tests for AuthConfig module.

Tests the AuthConfig class and EnvironmentType enum functionality.
"""

import pytest
from wxdi.common.auth import AuthConfig, EnvironmentType


class TestEnvironmentType:
    """Tests for EnvironmentType enum."""
    
    def test_environment_type_values(self):
        """Test that all environment types have correct values."""
        assert EnvironmentType.IBM_CLOUD.value == "ibm_cloud"
        assert EnvironmentType.AWS_CLOUD.value == "aws_cloud"
        assert EnvironmentType.GOV_CLOUD.value == "gov_cloud"
        assert EnvironmentType.ON_PREM.value == "on_prem"
    
    def test_environment_type_members(self):
        """Test that all expected environment types exist."""
        env_types = [e.name for e in EnvironmentType]
        assert "IBM_CLOUD" in env_types
        assert "AWS_CLOUD" in env_types
        assert "GOV_CLOUD" in env_types
        assert "ON_PREM" in env_types


class TestAuthConfigIBMCloud:
    """Tests for AuthConfig with IBM_CLOUD environment."""
    
    def test_ibm_cloud_with_api_key(self):
        """Test IBM_CLOUD configuration with API key."""
        config = AuthConfig(
            environment_type=EnvironmentType.IBM_CLOUD,
            api_key='test-api-key'
        )
        assert config.environment_type == EnvironmentType.IBM_CLOUD
        assert config.api_key == 'test-api-key'
        assert config.url == 'https://iam.cloud.ibm.com/identity/token'
    
    def test_ibm_cloud_with_custom_url(self):
        """Test IBM_CLOUD with custom URL."""
        custom_url = 'https://custom.ibm.com/token'
        config = AuthConfig(
            environment_type=EnvironmentType.IBM_CLOUD,
            api_key='test-key',
            url=custom_url
        )
        assert config.url == custom_url
    
    def test_ibm_cloud_missing_api_key(self):
        """Test that IBM_CLOUD requires API key."""
        with pytest.raises(ValueError, match="API key must be provided"):
            AuthConfig(environment_type=EnvironmentType.IBM_CLOUD)
    
    def test_ibm_cloud_trailing_slash_stripped(self):
        """Test that trailing slashes are stripped from URL."""
        config = AuthConfig(
            environment_type=EnvironmentType.IBM_CLOUD,
            api_key='test-key',
            url='https://custom.ibm.com/token///'
        )
        assert config.url == 'https://custom.ibm.com/token'


class TestAuthConfigAWSCloud:
    """Tests for AuthConfig with AWS_CLOUD environment."""
    
    def test_aws_cloud_with_default_url(self):
        """Test AWS_CLOUD with default URL."""
        config = AuthConfig(
            environment_type=EnvironmentType.AWS_CLOUD,
            api_key='test-key',
            account_id='account-123'
        )
        assert config.environment_type == EnvironmentType.AWS_CLOUD
        assert config.url == 'https://account-iam.platform.saas.ibm.com'
        assert config.account_id == 'account-123'
    
    def test_aws_cloud_with_custom_url(self):
        """Test AWS_CLOUD with custom URL."""
        custom_url = 'https://custom-account-iam.example.com'
        config = AuthConfig(
            environment_type=EnvironmentType.AWS_CLOUD,
            api_key='test-key',
            account_id='account-123',
            url=custom_url
        )
        assert config.url == custom_url
        assert config.account_id == 'account-123'
    
    def test_aws_cloud_missing_api_key(self):
        """Test that AWS_CLOUD requires API key."""
        with pytest.raises(ValueError, match="API key must be provided"):
            AuthConfig(
                environment_type=EnvironmentType.AWS_CLOUD,
                account_id='account-123'
            )
    
    def test_aws_cloud_missing_account_id(self):
        """Test that AWS_CLOUD requires account ID."""
        with pytest.raises(ValueError, match="Account ID must be provided"):
            AuthConfig(
                environment_type=EnvironmentType.AWS_CLOUD,
                api_key='test-key'
            )
    
    def test_aws_cloud_account_id_required(self):
        """Test that account_id is stored correctly for AWS_CLOUD."""
        config = AuthConfig(
            environment_type=EnvironmentType.AWS_CLOUD,
            api_key='test-key',
            account_id='my-account'
        )
        assert config.account_id == 'my-account'


class TestAuthConfigGovCloud:
    """Tests for AuthConfig with GOV_CLOUD environment."""
    
    def test_gov_cloud_with_api_key(self):
        """Test GOV_CLOUD configuration."""
        config = AuthConfig(
            environment_type=EnvironmentType.GOV_CLOUD,
            api_key='test-key'
        )
        assert config.environment_type == EnvironmentType.GOV_CLOUD
        assert config.url == 'https://dai.ibmforusgov.com/api/rest/mcsp/apikeys/token'
    
    def test_gov_cloud_missing_api_key(self):
        """Test that GOV_CLOUD requires API key."""
        with pytest.raises(ValueError, match="API key must be provided"):
            AuthConfig(environment_type=EnvironmentType.GOV_CLOUD)


class TestAuthConfigOnPrem:
    """Tests for AuthConfig with ON_PREM environment."""
    
    def test_on_prem_with_api_key(self):
        """Test ON_PREM with username and API key."""
        config = AuthConfig(
            environment_type=EnvironmentType.ON_PREM,
            url='https://cpd.example.com',
            username='admin',
            api_key='test-key'
        )
        assert config.environment_type == EnvironmentType.ON_PREM
        assert config.url == 'https://cpd.example.com/icp4d-api/v1/authorize'
        assert config.username == 'admin'
        assert config.api_key == 'test-key'
    
    def test_on_prem_with_password(self):
        """Test ON_PREM with username and password."""
        config = AuthConfig(
            environment_type=EnvironmentType.ON_PREM,
            url='https://cpd.example.com',
            username='admin',
            password='secret'
        )
        assert config.url == 'https://cpd.example.com/icp4d-api/v1/authorize'
        assert config.username == 'admin'
        assert config.password == 'secret'
    
    def test_on_prem_url_already_has_path(self):
        """Test that path is not duplicated if already present."""
        config = AuthConfig(
            environment_type=EnvironmentType.ON_PREM,
            url='https://cpd.example.com/icp4d-api/v1/authorize',
            username='admin',
            api_key='test-key'
        )
        assert config.url == 'https://cpd.example.com/icp4d-api/v1/authorize'
    
    def test_on_prem_missing_url(self):
        """Test that ON_PREM requires URL."""
        with pytest.raises(ValueError, match="URL must be specified"):
            AuthConfig(
                environment_type=EnvironmentType.ON_PREM,
                username='admin',
                password='secret'
            )
    
    def test_on_prem_missing_username(self):
        """Test that ON_PREM requires username."""
        with pytest.raises(ValueError, match="Username must be provided"):
            AuthConfig(
                environment_type=EnvironmentType.ON_PREM,
                url='https://cpd.example.com',
                api_key='test-key'
            )
    
    def test_on_prem_missing_credentials(self):
        """Test that ON_PREM requires either API key or password."""
        with pytest.raises(ValueError, match="Either api_key or password must be provided"):
            AuthConfig(
                environment_type=EnvironmentType.ON_PREM,
                url='https://cpd.example.com',
                username='admin'
            )
    
    def test_on_prem_trailing_slash_stripped(self):
        """Test that trailing slash is stripped before appending path."""
        config = AuthConfig(
            environment_type=EnvironmentType.ON_PREM,
            url='https://cpd.example.com/',
            username='admin',
            api_key='test-key'
        )
        assert config.url == 'https://cpd.example.com/icp4d-api/v1/authorize'


class TestAuthConfigValidation:
    """Tests for AuthConfig validation."""
    
    def test_invalid_environment_type(self):
        """Test that invalid environment type raises TypeError."""
        with pytest.raises(TypeError, match="environment_type must be an instance of EnvironmentType"):
            AuthConfig(
                environment_type="invalid",  # type: ignore
                api_key='test-key'
            )
    
    def test_url_trailing_slash_stripping(self):
        """Test that multiple trailing slashes are stripped."""
        config = AuthConfig(
            environment_type=EnvironmentType.IBM_CLOUD,
            api_key='test-key',
            url='https://example.com///'
        )
        assert config.url == 'https://example.com'
    
    def test_disable_ssl_verification_default_true(self):
        """Test that disable_ssl_verification defaults to True."""
        config = AuthConfig(
            environment_type=EnvironmentType.IBM_CLOUD,
            api_key='test-key'
        )
        assert config.disable_ssl_verification is True
    
    def test_disable_ssl_verification_can_be_set_false(self):
        """Test that disable_ssl_verification can be set to False."""
        config = AuthConfig(
            environment_type=EnvironmentType.IBM_CLOUD,
            api_key='test-key',
            disable_ssl_verification=False
        )
        assert config.disable_ssl_verification is False
    
    def test_disable_ssl_verification_with_on_prem(self):
        """Test disable_ssl_verification with ON_PREM environment."""
        config = AuthConfig(
            environment_type=EnvironmentType.ON_PREM,
            url='https://cpd.example.com',
            username='admin',
            api_key='test-key',
            disable_ssl_verification=False
        )
        assert config.disable_ssl_verification is False