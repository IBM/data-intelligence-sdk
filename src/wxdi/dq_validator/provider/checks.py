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
from typing import Optional, Dict, Any

from .base_provider import BaseProvider
from .config import ProviderConfig
from ..utils import get_request_headers

# Error message constants
_ERR_MISSING_PROJECT_OR_CATALOG = "Either project_id or catalog_id must be provided"
_ERR_BOTH_PROJECT_AND_CATALOG = "Only one of project_id or catalog_id should be provided, not both"


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
        catalog_id: Optional[str] = None,
        parent_check_id: Optional[str] = None
    ) -> str:
        """
        Create a new check for a data asset.
        
        Note: Table-level checks are created without a parent_check_id, while column-level checks
        require the table-level check ID as parent_check_id to establish the hierarchical relationship.
        
        Args:
            name: Name of the check (e.g., "check_uniqueness_of_id")
            dimension_id: The dimension ID for the check
            native_id: Native ID in format "<asset_id>/<check_id>"
            check_type: Type of check (optional, defaults to the check name if not provided)
            project_id (str, optional): The project ID containing the check
            catalog_id (str, optional): The catalog ID containing the check
            parent_check_id (str, optional): The parent check ID. Required for column-level checks
                (use table-level check ID). Omit for table-level checks.
        
        Returns:
            str: The check ID from the created check
        
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
            >>> # With parent parameter
            >>> provider.create_check(
            ...     name="Format check",
            ...     dimension_id="ec453723-669c-48bb-82c1-11b69b3b8c93",
            ...     native_id="ba23145a-6d0a-46db-b314-41526b1e465f/format/sample3",
            ...     project_id="project-123",
            ...     parent_check_id="848aaddc-7401-4a43-ad2b-96a0946d4674"
            ... )
            '7be18374-573a-4cf8-8ab7-e428506e428c'
        """
        # Call _create_check_full and extract just the ID
        result = self._create_check_full(
            name=name,
            dimension_id=dimension_id,
            native_id=native_id,
            check_type=check_type,
            project_id=project_id,
            catalog_id=catalog_id,
            parent_check_id=parent_check_id
        )
        return result["id"]
    
    def _create_check_full(
        self,
        name: str,
        dimension_id: str,
        native_id: str,
        check_type: Optional[str] = None,
        project_id: Optional[str] = None,
        catalog_id: Optional[str] = None,
        parent_check_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new check and return the full check body.
        
        This method creates a check and returns the complete check object including
        all properties like id, name, type, native_id, parent, etc.
        
        Note: Table-level checks are created without a parent_check_id, while column-level checks
        require the table-level check ID as parent_check_id to establish the hierarchical relationship.
        
        Args:
            name: Name of the check
            dimension_id: ID of the dimension this check belongs to
            native_id: Native identifier for the check
            check_type: Type of check (defaults to name if not provided)
            project_id: Project ID (mutually exclusive with catalog_id)
            catalog_id: Catalog ID (mutually exclusive with project_id)
            parent_check_id: Optional parent check ID for hierarchical checks. Required for column-level
                checks (use table-level check ID). Omit for table-level checks.
        
        Returns:
            Dict containing the full check body with all properties
        
        Raises:
            ValueError: If neither or both project_id and catalog_id are provided,
                       or if the API request fails
        
        Example:
            >>> from wxdi.dq_validator.provider import ProviderConfig, ChecksProvider
            >>> config = ProviderConfig(url="https://example.com", auth_token="token")
            >>> provider = ChecksProvider(config)
            >>> check = provider.create_check_full(
            ...     name="Format check",
            ...     dimension_id="ec453723-669c-48bb-82c1-11b69b3b8c93",
            ...     native_id="ba23145a-6d0a-46db-b314-41526b1e465f/format/sample3",
            ...     project_id="project-123",
            ...     parent_check_id="848aaddc-7401-4a43-ad2b-96a0946d4674"
            ... )
            >>> print(check)
            {'id': '7be18374-573a-4cf8-8ab7-e428506e428c', 'name': 'Format check',
             'type': 'format', 'native_id': '...', 'parent': {'id': '...'}, ...}
        """
        from ..utils import get_url_with_query_params
        
        # Validate that exactly one of project_id or catalog_id is provided
        if project_id is None and catalog_id is None:
            raise ValueError(_ERR_MISSING_PROJECT_OR_CATALOG)
        if project_id is not None and catalog_id is not None:
            raise ValueError(_ERR_BOTH_PROJECT_AND_CATALOG)
        
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
        
        # Add parent only if provided
        if parent_check_id is not None:
            payload["parent"] = {
                "id": parent_check_id
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
        
        # Parse response and return full check body
        result = json.loads(response.text)
        if not result.get("id"):
            raise ValueError("Check ID not found in response")
        
        return result
    
    def get_checks(
        self,
        dq_asset_id: str,
        check_type: str,
        project_id: Optional[str] = None,
        catalog_id: Optional[str] = None,
        include_children: bool = True
    ) -> list:
        """
        Get all checks for a specific asset filtered by check type.
        
        Args:
            dq_asset_id: The data quality asset identifier (column asset ID)
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
            ...     dq_asset_id="column-asset-123",
            ...     check_type="case",
            ...     project_id="project-123"
            ... )
            [{'id': 'check-id-1', 'type': 'case', ...}, ...]
        """
        from ..utils import get_url_with_query_params
        
        # Validate that exactly one of project_id or catalog_id is provided
        if project_id is None and catalog_id is None:
            raise ValueError(_ERR_MISSING_PROJECT_OR_CATALOG)
        if project_id is not None and catalog_id is not None:
            raise ValueError(_ERR_BOTH_PROJECT_AND_CATALOG)
        
        # Build the URL for checks API
        url = f"{self.config.url}/data_quality/v4/checks"
        
        # Add query parameters
        params = {
            "asset.id": dq_asset_id,
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