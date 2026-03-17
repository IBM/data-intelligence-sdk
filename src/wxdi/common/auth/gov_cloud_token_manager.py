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
Government Cloud Token Manager for Authentication.

This module provides a token manager that extends JWTTokenManager
to handle Government Cloud specific token requests with proper error handling
and token lifecycle management.
"""

from __future__ import annotations

from typing import Optional

from ibm_cloud_sdk_core.token_managers.jwt_token_manager import JWTTokenManager


class GovCloudTokenManager(JWTTokenManager):
    """
    Government Cloud Token Manager.
    
    This token manager extends JWTTokenManager to handle custom token
    request formats for Government Cloud authentication. It manages the
    complete token lifecycle including acquisition, storage, and expiration.
    
    Attributes:
        apikey: The API key for authentication
        headers: Optional headers to include in requests
        proxies: Optional proxy configuration
    
    Example:
        >>> manager = GovCloudTokenManager(
        ...     apikey="your-api-key",
        ...     url="https://dai.ibmforusgov.com/api/rest/mcsp/apikeys/token"
        ... )
        >>> token = manager.get_token()
    """
    
    __slots__ = ('apikey', 'headers', 'proxies')
    
    # Constants for token handling
    _CONTENT_TYPE_FORM: str = 'application/x-www-form-urlencoded'
    _CONTENT_TYPE_JSON: str = 'application/json'
    
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
        Initialize the Government Cloud token manager.
        
        Args:
            apikey: The API key for authentication
            url: The token endpoint URL
            disable_ssl_verification: Whether to disable SSL verification
            headers: Optional headers to include in requests
            proxies: Optional proxy configuration
        """
        # Initialize the base JWTTokenManager
        # token_name can be 'token' or 'access_token' depending on response format
        super().__init__(
            url=url,
            disable_ssl_verification=disable_ssl_verification,
            token_name='token'
        )
        
        self.apikey = apikey
        self.headers = headers or {}
        self.proxies = proxies or {}
    
    def request_token(self) -> dict:  # type: ignore[override]
        """
        Request a new token from the Government Cloud endpoint.
        
        This method makes a POST request to the token endpoint with the API key
        and returns the token response. Uses form-urlencoded content type for
        compatibility with Government Cloud endpoints.
        
        Returns:
            dict: The token response from the endpoint containing token and expiration info
            
        Raises:
            Exception: If the token request fails
            
        Note:
            Follows the IAMTokenManager pattern by returning dict for _save_token_info().
        """
        headers = self._build_request_headers()
        data = self._build_request_data()
        
        # Make the token request
        response = self._request(
            method='POST',
            url=self.url,
            headers=headers,
            data=data
        )
        
        return response
    
    def _build_request_headers(self) -> dict[str, str]:
        """
        Build headers for the token request.
        
        Returns:
            dict: Headers dictionary with content type and custom headers
        """
        headers = {
            'Content-Type': self._CONTENT_TYPE_FORM,
            'Accept': self._CONTENT_TYPE_JSON
        }
        headers.update(self.headers)
        return headers
    
    def _build_request_data(self) -> dict[str, str]:
        """
        Build request data for the token request.
        
        Returns:
            dict: Request data containing the API key
        """
        return {'apikey': self.apikey}
    
    def _save_token_info(self, token_response: dict) -> None:
        """
        Save token information from the response.
        
        Calls parent class to handle JWT token extraction and expiration,
        then additionally extracts the refresh token if present.
        
        Args:
            token_response: The response dictionary from the token endpoint
            
        Raises:
            ValueError: If token is not found in the response
        """
        # Parent class handles token and expiration extraction from JWT
        super()._save_token_info(token_response)
        