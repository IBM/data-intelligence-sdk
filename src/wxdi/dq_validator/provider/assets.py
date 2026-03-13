# Copyright 2026 IBM Corporation
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0);
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
#
# See the LICENSE file in the project root for license information.

"""
Provider for managing data quality assets.
"""

import json
from typing import Optional

from .base_provider import BaseProvider
from .config import ProviderConfig
from ..utils import get_request_headers


class DQAssetsProvider(BaseProvider):
    """Provider for managing data quality assets.

    This provider allows interaction with the data quality assets API,
    such as retrieving asset information.
    
    Args:
        config (ProviderConfig): Configuration containing URL and authentication token

    Example:
        >>> from dq_validator.provider import ProviderConfig, DQAssetsProvider
        >>> config = ProviderConfig(
        ...     url="https://your-instance.com",
        ...     auth_token="Bearer your-token"
        ... )
        >>> provider = DQAssetsProvider(config)
        >>> assets = provider.get_assets(project_id="project-123")
    """

    def __init__(self, config: ProviderConfig):
        """Initialize the DQAssetsProvider with configuration.

        Args:
            config (ProviderConfig): Provider configuration with URL and auth token
        """
        super().__init__(config)
    
    def get_assets(
        self,
        project_id: Optional[str] = None,
        catalog_id: Optional[str] = None,
        start: Optional[str] = None,
        limit: Optional[int] = None,
        include_children: Optional[bool] = None,
        asset_type: Optional[str] = None
    ) -> dict:
        """
        Get data quality assets.
        
        This method retrieves data quality assets based on the provided filters.
        
        Args:
            project_id (str, optional): The project ID to use
            catalog_id (str, optional): The catalog ID to use
            start (str, optional): The start token for pagination
            limit (int, optional): Maximum number of resources to return
            include_children (bool, optional): If true, include children in the response
            asset_type (str, optional): The type of resource to search
        
        Returns:
            dict: The response from the API containing the assets data
        
        Raises:
            ValueError: If the API request fails or returns an error status, or if neither
                project_id nor catalog_id is provided, or if both are provided
        
        Example:
            >>> # Using project_id
            >>> provider.get_assets(
            ...     project_id="project-123",
            ...     limit=10,
            ...     asset_type="column"
            ... )
            >>> # Using catalog_id
            >>> provider.get_assets(
            ...     catalog_id="catalog-123",
            ...     include_children=True
            ... )
        """
        from ..utils import get_url_with_query_params
        
        # Validate that exactly one of project_id or catalog_id is provided
        if project_id is None and catalog_id is None:
            raise ValueError("Either project_id or catalog_id must be provided")
        if project_id is not None and catalog_id is not None:
            raise ValueError("Only one of project_id or catalog_id should be provided, not both")
        
        # Build the URL for assets API
        url = f"{self.config.url}/data_quality/v4/assets"
        
        # Build query parameters
        params = {}
        if project_id is not None:
            params["project_id"] = project_id
        elif catalog_id is not None:
            params["catalog_id"] = catalog_id
        
        # Add optional parameters
        if start is not None:
            params["start"] = start
        if limit is not None:
            params["limit"] = str(limit)
        if include_children is not None:
            params["include_children"] = str(include_children).lower()
        if asset_type is not None:
            params["type"] = asset_type
        
        url = get_url_with_query_params(url, params)
        
        # Get request headers
        headers = get_request_headers(self.config.auth_token)
        
        # Make GET request
        response = self.session.get(url, headers=headers, verify=False)
        
        if not response.ok:
            raise ValueError(
                f"Failed to get assets. "
                f"Status: {response.status_code}, "
                f"Response: {response.text}"
            )
        
        # Parse and return response
        return json.loads(response.text)