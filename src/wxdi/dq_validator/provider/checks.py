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
Provider for managing data quality checks.
"""

import json
from typing import Optional

from .base_provider import BaseProvider
from .config import ProviderConfig
from ..utils import get_request_headers


class ChecksProvider(BaseProvider):
    """Provider for managing data quality checks.

    This provider allows interaction with the data quality checks API,
    including creating new checks for data assets.
    
    Args:
        config (ProviderConfig): Configuration containing URL and authentication token

    Example:
        >>> from dq_validator.provider import ProviderConfig, ChecksProvider
        >>> config = ProviderConfig(
        ...     url="https://your-instance.com",
        ...     auth_token="Bearer your-token",
        ...     project_id="project-123"
        ... )
        >>> provider = ChecksProvider(config)
        >>> provider.create_check(
        ...     asset_id="asset-123",
        ...     column_name="email",
        ...     check_name="format_check",
        ...     number_of_occurrences=10,
        ...     total_records=100
        ... )
    """

    def __init__(self, config: ProviderConfig):
        """Initialize the ChecksProvider with configuration.

        Args:
            config (ProviderConfig): Provider configuration with URL and auth token
        """
        super().__init__(config)
    
    def create_check(
        self,
        name: str,
        dimension_id: str,
        native_id: str,
        check_type: Optional[str] = None,
        project_id: Optional[str] = None,
        catalog_id: Optional[str] = None
    ) -> str:
        """
        Create a new check for a data asset.
        
        Args:
            name: Name of the check (e.g., "check_uniqueness_of_id")
            dimension_id: The dimension ID for the check
            native_id: Native ID in format "<asset_id>/<check_id>"
            check_type: Type of check (optional, defaults to the check name if not provided)
            project_id (str, optional): The project ID containing the check
            catalog_id (str, optional): The catalog ID containing the check
        
        Returns:
            str: The check_id of the created check
        
        Raises:
            ValueError: If the API request fails or returns an error status, or if neither
                project_id nor catalog_id is provided, or if both are provided
        
        Example:
            >>> provider.create_check(
            ...     name="check_uniqueness_of_id",
            ...     dimension_id="371114cd-5516-4691-8b2e-1e66edf66486",
            ...     native_id="4cdcd382-4e3a-4537-b7ae-09993acee4cf/3e51167c-6eb2-4069-96dc-5d6df808fd47",
            ...     project_id="project-123"
            ... )
            '6be18374-573a-4cf8-8ab7-e428506e428b'
        """
        from ..utils import get_url_with_query_params
        
        # Validate that exactly one of project_id or catalog_id is provided
        if project_id is None and catalog_id is None:
            raise ValueError("Either project_id or catalog_id must be provided")
        if project_id is not None and catalog_id is not None:
            raise ValueError("Only one of project_id or catalog_id should be provided, not both")
        
        # Default check_type to name if not provided
        if check_type is None:
            check_type = name
        
        # Build the URL for check creation API
        url = f"{self.config.url}/data_quality/v4/checks"
        
        # Add either project_id or catalog_id as query parameter
        params = {}
        if project_id is not None:
            params["project_id"] = project_id
        elif catalog_id is not None:
            params["catalog_id"] = catalog_id
        url = get_url_with_query_params(url, params)
        
        # Prepare the payload
        payload = {
            "dimension": {
                "id": dimension_id
            },
            "name": name,
            "type": check_type,
            "native_id": native_id,
            "details": '{"origin": "SDK"}'
        }
        
        # Get request headers
        headers = get_request_headers(self.config.auth_token)
        
        # Make POST request
        response = self.session.post(
            url,
            headers=headers,
            data=json.dumps(payload),
            verify=False
        )
        
        if not response.ok:
            raise ValueError(
                f"Failed to create check. "
                f"Status: {response.status_code}, "
                f"Response: {response.text}"
            )
        
        # Parse response and extract check_id
        result = json.loads(response.text)
        check_id = result.get("id")
        if not check_id:
            raise ValueError("Check ID not found in response")
        
        return check_id
    
    def get_checks(
        self,
        asset_id: str,
        check_type: str,
        project_id: Optional[str] = None,
        catalog_id: Optional[str] = None,
        include_children: bool = True
    ) -> list:
        """
        Get all checks for a specific asset filtered by check type.
        
        Args:
            asset_id: The data quality asset identifier (column asset ID)
            check_type: Type of check to filter by (e.g., "case", "completeness", "comparison")
            project_id (str, optional): The project ID containing the checks
            catalog_id (str, optional): The catalog ID containing the checks
            include_children (bool, optional): If true include the children in the returned resource. Defaults to True.
        
        Returns:
            list: List of check objects matching the criteria
        
        Raises:
            ValueError: If the API request fails or returns an error status, or if neither
                project_id nor catalog_id is provided, or if both are provided
        
        Example:
            >>> provider.get_checks(
            ...     asset_id="column-asset-123",
            ...     check_type="case",
            ...     project_id="project-123"
            ... )
            [{'id': 'check-id-1', 'type': 'case', ...}, ...]
        """
        from ..utils import get_url_with_query_params
        
        # Validate that exactly one of project_id or catalog_id is provided
        if project_id is None and catalog_id is None:
            raise ValueError("Either project_id or catalog_id must be provided")
        if project_id is not None and catalog_id is not None:
            raise ValueError("Only one of project_id or catalog_id should be provided, not both")
        
        # Build the URL for checks API
        url = f"{self.config.url}/data_quality/v4/checks"
        
        # Add query parameters
        params = {
            "asset.id": asset_id,
            "type": check_type,
            "include_children": str(include_children).lower()
        }
        if project_id is not None:
            params["project_id"] = project_id
        elif catalog_id is not None:
            params["catalog_id"] = catalog_id
        
        url = get_url_with_query_params(url, params)
        
        # Get request headers
        headers = get_request_headers(self.config.auth_token)
        
        # Make GET request
        response = self.session.get(
            url,
            headers=headers,
            verify=False
        )
        
        if not response.ok:
            raise ValueError(
                f"Failed to get checks. "
                f"Status: {response.status_code}, "
                f"Response: {response.text}"
            )
        
        # Parse response and return checks list
        result = json.loads(response.text)
        checks = result.get("checks", [])
        
        return checks