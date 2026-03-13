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
Provider for managing data quality dimensions.
"""

import json
from typing import Optional

from .base_provider import BaseProvider
from .config import ProviderConfig
from ..utils import get_request_headers


class DimensionsProvider(BaseProvider):
    """Provider for managing data quality dimensions.

    This provider allows interaction with the data quality dimensions API,
    including retrieving dimension information.
    
    Args:
        config (ProviderConfig): Configuration containing URL and authentication token

    Example:
        >>> from dq_validator.provider import ProviderConfig, DimensionsProvider
        >>> config = ProviderConfig(
        ...     url="https://your-instance.com",
        ...     auth_token="Bearer your-token"
        ... )
        >>> provider = DimensionsProvider(config)
        >>> dimension = provider.search_dimension()
    """

    def __init__(self, config: ProviderConfig):
        """Initialize the DimensionsProvider with configuration.

        Args:
            config (ProviderConfig): Provider configuration with URL and auth token
        """
        super().__init__(config)
    
    def search_dimension(self, name: str) -> str:
        """
        Search for a data quality dimension ID by name.
        
        This method searches for dimension information by name and returns the dimension ID.
        The name matching is case-insensitive.
        
        Args:
            name (str): The name of the dimension (e.g., "Completeness", "Accuracy")
        
        Returns:
            str: The dimension ID
        
        Raises:
            ValueError: If the API request fails, dimension not found, or response is invalid
        
        Example:
            >>> provider = DimensionProvider(config)
            >>> dimension_id = provider.search_dimension("Completeness")
            '371114cd-5516-4691-8b2e-1e66edf66486'
            >>> # Case-insensitive matching
            >>> dimension_id = provider.search_dimension("completeness")
            '371114cd-5516-4691-8b2e-1e66edf66486'
        """
        from ..utils import get_url_with_query_params
        
        # Build the URL for dimensions search API
        url = f"{self.config.url}/data_quality/v4/search_dq_dimension"
        
        # Add name as query parameter
        params = {"name": name}
        url = get_url_with_query_params(url, params)
        
        # Get request headers
        headers = get_request_headers(self.config.auth_token)
        
        # Make POST request
        response = self.session.post(url, headers=headers, verify=False)
        
        if not response.ok:
            raise ValueError(
                f"Failed to get dimension. "
                f"Status: {response.status_code}, "
                f"Response: {response.text}"
            )
        
        # Parse response
        result = json.loads(response.text)
        
        # Extract dimensions list
        dimensions = result.get("dimensions", [])
        
        if not dimensions:
            raise ValueError(f"Dimension with name '{name}' not found")
        
        # Find dimension with matching name (case-insensitive)
        name_lower = name.lower()
        matching_dimension = None
        for dimension in dimensions:
            dimension_name = dimension.get("name", "")
            if dimension_name.lower() == name_lower:
                matching_dimension = dimension
                break
        
        if not matching_dimension:
            raise ValueError(f"Dimension with name '{name}' not found in results")
        
        # Extract and return the ID
        dimension_id = matching_dimension.get("id")
        if not dimension_id:
            raise ValueError("Dimension ID not found in response")
        
        return dimension_id