# Copyright 2026 IBM Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Auth Provider module for authentication.

This module provides an AuthProvider class that generates authentication tokens
based on the environment configuration using appropriate IBM Cloud SDK authenticators.
Implements factory pattern for authenticator creation with comprehensive error handling.
"""

from __future__ import annotations

from ibm_cloud_sdk_core.authenticators import (
    Authenticator,
    CloudPakForDataAuthenticator,
    IAMAuthenticator,
    MCSPV2Authenticator,
)

from .auth_config import AuthConfig, EnvironmentType
from .gov_cloud_authenticator import GovCloudAuthenticator


class AuthProvider:
    """
    Authentication provider for different cloud environments.
    
    This class implements a factory pattern to create and manage authenticators
    for various cloud environments. It provides a unified interface for token
    generation across different authentication mechanisms.
    
    Authenticator mapping:
        - IBM_CLOUD: IAMAuthenticator (IBM Cloud IAM)
        - AWS_CLOUD: MCSPV2Authenticator (Multi-Cloud Service Platform V2)
        - ON_PREM: CloudPakForDataAuthenticator (Cloud Pak for Data)
        - GOV_CLOUD: GovCloudAuthenticator (Government Cloud custom implementation)
    
    Attributes:
        config: The authentication configuration
        authenticator: The created authenticator instance
    
    Example:
        >>> config = AuthConfig(
        ...     environment_type=EnvironmentType.IBM_CLOUD,
        ...     api_key="your-api-key"
        ... )
        >>> provider = AuthProvider(config)
        >>> token = provider.get_token()
    """
    
    
    def __init__(self, config: AuthConfig) -> None:
        """
        Initialize the AuthProvider with an environment configuration.
        
        Args:
            config: AuthConfig instance with authentication details
        
        Raises:
            ValueError: If authenticator creation fails due to invalid configuration
        """
        self.config = config
        self.authenticator: Authenticator = self._create_authenticator()
    
    def _create_authenticator(self) -> Authenticator:
        """
        Create the appropriate authenticator based on environment type.
        
        Uses factory pattern to instantiate the correct authenticator.
        All required fields are validated by AuthConfig before reaching here.
        
        Returns:
            An authenticator instance based on the environment type
            
        Raises:
            ValueError: If the environment type is not supported
        """
        authenticator_factory = {
            EnvironmentType.IBM_CLOUD: self._create_ibm_cloud_authenticator,
            EnvironmentType.AWS_CLOUD: self._create_aws_cloud_authenticator,
            EnvironmentType.ON_PREM: self._create_on_prem_authenticator,
            EnvironmentType.GOV_CLOUD: self._create_gov_cloud_authenticator,
        }
        
        factory_method = authenticator_factory.get(self.config.environment_type)
        if factory_method is None:
            raise ValueError(
                f"Unsupported environment type: {self.config.environment_type.value}"
            )
        
        return factory_method()
    
    def _create_ibm_cloud_authenticator(self) -> IAMAuthenticator:
        """
        Create IAMAuthenticator for IBM Cloud.
        
        Returns:
            IAMAuthenticator instance configured for IBM Cloud
        """
        return IAMAuthenticator(
            apikey=str(self.config.api_key),
            url=str(self.config.url)
        )
    
    def _create_aws_cloud_authenticator(self) -> MCSPV2Authenticator:
        """
        Create MCSPV2Authenticator for AWS Cloud.
        
        Returns:
            MCSPV2Authenticator instance configured for AWS Cloud
        """
        return MCSPV2Authenticator(
            apikey=str(self.config.api_key),
            url=str(self.config.url),
            scope_collection_type='accounts',
            scope_id=str(self.config.account_id)
        )
    
    def _create_on_prem_authenticator(self) -> CloudPakForDataAuthenticator:
        """
        Create CloudPakForDataAuthenticator for on-premises deployment.
        
        Supports both API key and username/password authentication.
        
        Returns:
            CloudPakForDataAuthenticator instance configured for on-premises
        """
        base_params = {
            'username': str(self.config.username),
            'url': str(self.config.url),
            'disable_ssl_verification': self.config.disable_ssl_verification
        }
        
        if self.config.api_key:
            return CloudPakForDataAuthenticator(
                **base_params,
                apikey=str(self.config.api_key)
            )
        else:
            return CloudPakForDataAuthenticator(
                **base_params,
                password=str(self.config.password)
            )
    
    def _create_gov_cloud_authenticator(self) -> GovCloudAuthenticator:
        """
        Create GovCloudAuthenticator for Government Cloud.
        
        Returns:
            GovCloudAuthenticator instance configured for Government Cloud
        """
        return GovCloudAuthenticator(
            apikey=str(self.config.api_key),
            url=str(self.config.url),
            disable_ssl_verification=self.config.disable_ssl_verification
        )
    
    def get_token(self) -> str:
        """
        Generate and return an authentication token.
        
        This method validates the authenticator and retrieves a token from
        the token manager. The token is automatically refreshed if expired.
        
        Returns:
            str: The authentication token
            
        Raises:
            ValueError: If the authenticator doesn't have a token_manager
            Exception: If token generation fails
        """
        # Validate the authenticator configuration
        self.authenticator.validate()
        
        # All authenticators have a token_manager attribute
        # IAMAuthenticator, MCSPV2Authenticator, CloudPakForDataAuthenticator, GovCloudAuthenticator
        token_manager = getattr(self.authenticator, 'token_manager', None)
        if token_manager is None:
            raise ValueError(
                f"Authenticator {type(self.authenticator).__name__} does not have token_manager"
            )
        
        return token_manager.get_token()