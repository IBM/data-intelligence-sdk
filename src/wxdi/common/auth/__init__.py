#    Copyright 2026 IBM Corporation
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""
Authentication module for dq_validator.

This module provides comprehensive authentication utilities for various cloud
environments including IBM Cloud, AWS Cloud, Government Cloud, and on-premises
deployments. It implements a factory pattern for authenticator creation with
proper validation and error handling.

Key Components:
    - AuthConfig: Configuration dataclass for authentication parameters
    - EnvironmentType: Enum defining supported cloud environments
    - AuthProvider: Factory class for creating and managing authenticators
    - GovCloudAuthenticator: Authenticator for Government Cloud
    - GovCloudTokenManager: Token manager for Government Cloud authentication

Example:
    >>> from auth import AuthConfig, EnvironmentType, AuthProvider
    >>> config = AuthConfig(
    ...     environment_type=EnvironmentType.IBM_CLOUD,
    ...     api_key="your-api-key"
    ... )
    >>> provider = AuthProvider(config)
    >>> token = provider.get_token()
"""

from __future__ import annotations

from .auth_config import AuthConfig, EnvironmentType
from .auth_provider import AuthProvider
from .gov_cloud_authenticator import GovCloudAuthenticator
from .gov_cloud_token_manager import GovCloudTokenManager

__all__ = [
    'AuthConfig',
    'EnvironmentType',
    'AuthProvider',
    'GovCloudAuthenticator',
    'GovCloudTokenManager',
]
