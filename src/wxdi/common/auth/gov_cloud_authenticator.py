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
Government Cloud Authenticator for Authentication.

This module provides an authenticator that extends IAMRequestBasedAuthenticator
to handle Government Cloud specific authentication using a custom token manager.
Implements proper encapsulation and type safety.
"""

from __future__ import annotations

from typing import Optional

from ibm_cloud_sdk_core.authenticators.iam_request_based_authenticator import (
    IAMRequestBasedAuthenticator,
)

from .gov_cloud_token_manager import GovCloudTokenManager


class GovCloudAuthenticator(IAMRequestBasedAuthenticator):
    """
    Government Cloud Authenticator.
    
    This authenticator extends IAMRequestBasedAuthenticator and uses a custom
    token manager to handle Government Cloud specific authentication flows.
    
    The authenticator manages the complete token lifecycle:
    - Token acquisition from Government Cloud endpoints
    - Automatic token refresh when expired
    - Token expiration handling
    - SSL verification control
    
    Attributes:
        token_manager: The Government Cloud token manager instance
        apikey: The API key for authentication
        url: The token endpoint URL
    
    Note:
        headers, proxies, and disable_ssl_verification are managed by the token_manager
        and can be accessed via token_manager.headers, token_manager.proxies, and
        token_manager.disable_ssl_verification respectively.
    
    Example:
        >>> authenticator = GovCloudAuthenticator(
        ...     apikey="your-api-key",
        ...     url="https://dai.ibmforusgov.com/api/rest/mcsp/apikeys/token"
        ... )
        >>> authenticator.validate()
        >>> token = authenticator.token_manager.get_token()
    """
    
    __slots__ = ('token_manager', 'apikey', 'url')
    
    def __init__(
        self,
        apikey: str,
        url: str,
        *,
        disable_ssl_verification: bool = False,
        headers: Optional[dict[str, str]] = None,
        proxies: Optional[dict[str, str]] = None
    ) -> None:
        """
        Initialize the Government Cloud authenticator.
        
        Args:
            apikey: Your API key for Government Cloud
            url: The token endpoint URL
            disable_ssl_verification: Whether to disable SSL verification (default: False)
            headers: Optional headers to include in token requests
            proxies: Optional proxy configuration
            
        Raises:
            ValueError: If apikey or url is not provided
        """
        self._validate_init_params(apikey, url)
        
        # Store parameters
        self.apikey = apikey
        self.url = url
        
        # Create the Government Cloud token manager
        self.token_manager = GovCloudTokenManager(
            apikey=apikey,
            url=url,
            disable_ssl_verification=disable_ssl_verification,
            headers=headers,
            proxies=proxies
        )
    
    @staticmethod
    def _validate_init_params(apikey: str, url: str) -> None:
        """
        Validate initialization parameters.
        
        Args:
            apikey: The API key to validate
            url: The URL to validate
            
        Raises:
            ValueError: If apikey or url is not provided
        """
        if not apikey:
            raise ValueError('The apikey must be specified.')
        if not url:
            raise ValueError('The url must be specified.')
    
    def validate(self) -> None:
        """
        Validate the authenticator configuration.
        
        This method ensures that all required fields are properly set
        before attempting authentication.
        
        Raises:
            ValueError: If apikey or url is not specified
        """
        if not self.apikey:
            raise ValueError('The apikey must be specified.')
        if not self.url:
            raise ValueError('The url must be specified.')
    
    def set_headers(self, headers: dict[str, str]) -> None:
        """
        Set headers to be included in token requests.
        
        Args:
            headers: Dictionary of headers to include
        """
        if self.token_manager:
            self.token_manager.headers = headers
    
    def set_proxies(self, proxies: dict[str, str]) -> None:
        """
        Set proxy configuration for token requests.
        
        Args:
            proxies: Dictionary of proxy configuration
        """
        if self.token_manager:
            self.token_manager.proxies = proxies
    
    def set_disable_ssl_verification(self, status: bool = False) -> None:
        """
        Set whether to disable SSL verification.
        
        Args:
            status: True to disable SSL verification, False to enable (default: False)
        """
        if self.token_manager:
            self.token_manager.disable_ssl_verification = status