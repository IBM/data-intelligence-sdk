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

from requests import Session
import json
from typing import Optional

from .base_provider import BaseProvider
from .config import ProviderConfig
from ..utils import get_request_headers, get_url_with_query_params


class DQSearchProvider(BaseProvider):
    """Provider for searching data quality checks and assets.

    This provider allows searching for DQ checks and assets using their native IDs.

    Args:
        config (ProviderConfig): Configuration containing URL and authentication token

    Example:
        >>> from dq_validator.provider import ProviderConfig, DQSearchProvider
        >>> config = ProviderConfig(
        ...     url="https://your-instance.com",
        ...     auth_token="Bearer your-token"
        ... )
        >>> provider = DQSearchProvider(config)
        >>> check = provider.search_dq_check(
        ...     native_id="b2debda2-6ab9-4a39-8c23-17954e004dcf/7377e2cd-ac0e-4833-8760-fd0e8cb682aa",
        ...     check_type="format",
        ...     project_id="24419069-d649-45cb-a2c1-64d6eed650d5"
        ... )
    """

    def __init__(self, config: ProviderConfig):
        """Initialize the DQSearchProvider with configuration.

        Args:
            config (ProviderConfig): Provider configuration with URL and auth token
        """
        super().__init__(config)
    
    def search_dq_check(
        self,
        native_id: str,
        check_type: str,
        project_id: Optional[str] = None,
        catalog_id: Optional[str] = None,
        include_children: bool = True
    ) -> dict:
        """Search for a DQ check by native ID and type.

        This method searches for data quality checks using the native ID (format: <cams_data_asset_id>/<check_id>)
        and the check type.

        Args:
            native_id (str): The native ID of the check in format <cams_data_asset_id>/<check_id>
            check_type (str): The type of check (e.g., "format", "completeness", "range", etc.)
            project_id (str, optional): The project ID containing the check
            catalog_id (str, optional): The catalog ID containing the check
            include_children (bool, optional): Include child checks. Default is True

        Returns:
            dict: The response from the API containing the check data

        Raises:
            ValueError: If the API request fails or returns an error status, or if neither
                project_id nor catalog_id is provided, or if both are provided
            
        Example:
            >>> # Using project_id
            >>> provider.search_dq_check(
            ...     native_id="b2debda2-6ab9-4a39-8c23-17954e004dcf/7377e2cd-ac0e-4833-8760-fd0e8cb682aa",
            ...     check_type="format",
            ...     project_id="24419069-d649-45cb-a2c1-64d6eed650d5"
            ... )
            >>> # Using catalog_id
            >>> provider.search_dq_check(
            ...     native_id="b2debda2-6ab9-4a39-8c23-17954e004dcf/7377e2cd-ac0e-4833-8760-fd0e8cb682aa",
            ...     check_type="format",
            ...     catalog_id="catalog-123"
            ... )
            {
                'id': 'ad277842-dea7-44ef-8e4b-d940df0f79aa',
                'name': 'Format check',
                'type': 'format',
                ...
            }
        """
        # Validate that exactly one of project_id or catalog_id is provided
        if project_id is None and catalog_id is None:
            raise ValueError("Either project_id or catalog_id must be provided")
        if project_id is not None and catalog_id is not None:
            raise ValueError("Only one of project_id or catalog_id should be provided, not both")
        
        url = f"{self.config.url}/data_quality/v4/search_dq_check"

        # Build query parameters
        params = {
            "native_id": native_id,
            "type": check_type,
            "include_children": str(include_children).lower()
        }
        
        # Add either project_id or catalog_id
        if project_id is not None:
            params["project_id"] = project_id
        elif catalog_id is not None:
            params["catalog_id"] = catalog_id
        
        url = get_url_with_query_params(url, params)
        
        headers = get_request_headers(self.config.auth_token)
        
        response = self.session.post(url, headers=headers, verify=False)
        
        if not response.ok:
            raise ValueError(
                f"Failed to search DQ check with native_id={native_id}, type={check_type}. "
                f"Status: {response.status_code}, "
                f"Response: {response.text}"
            )

        return json.loads(response.text)

    def search_dq_asset(
        self,
        native_id: str,
        project_id: Optional[str] = None,
        catalog_id: Optional[str] = None,
        asset_type: str = "column",
        include_children: bool = True,
        get_actual_asset: bool = False,
    ) -> dict:
        """Search for a DQ asset by native ID.

        This method searches for data quality assets using the native ID (format: <cams_data_asset_id>/<column_name>).

        Args:
            native_id (str): The native ID of the asset in format <cams_data_asset_id>/<column_name>
            project_id (str, optional): The project ID containing the asset
            catalog_id (str, optional): The catalog ID containing the asset
            asset_type (str, optional): The type of asset. Default is "column"
            include_children (bool, optional): Include child assets. Default is True
            get_actual_asset (bool, optional): Get the actual asset details. Default is False

        Returns:
            dict: The response from the API containing the asset data

        Raises:
            ValueError: If the API request fails or returns an error status, or if neither
                project_id nor catalog_id is provided, or if both are provided
            
        Example:
            >>> # Using project_id
            >>> provider.search_dq_asset(
            ...     native_id="b2debda2-6ab9-4a39-8c23-17954e004dcf/RTN",
            ...     project_id="24419069-d649-45cb-a2c1-64d6eed650d5",
            ...     asset_type="column"
            ... )
            >>> # Using catalog_id
            >>> provider.search_dq_asset(
            ...     native_id="b2debda2-6ab9-4a39-8c23-17954e004dcf/RTN",
            ...     catalog_id="catalog-123",
            ...     asset_type="column"
            ... )
            {
                'id': '1488a413-99f9-4bed-906d-c33b505d5728',
                'name': 'RTN',
                'type': 'column',
                ...
            }
        """
        # Validate that exactly one of project_id or catalog_id is provided
        if project_id is None and catalog_id is None:
            raise ValueError("Either project_id or catalog_id must be provided")
        if project_id is not None and catalog_id is not None:
            raise ValueError("Only one of project_id or catalog_id should be provided, not both")
        
        url = f"{self.config.url}/data_quality/v4/search_dq_asset"

        # Build query parameters
        params = {
            "native_id": native_id,
            "type": asset_type,
            "include_children": str(include_children).lower(),
            "get_actual_asset": str(get_actual_asset).lower(),
        }
        
        # Add either project_id or catalog_id
        if project_id is not None:
            params["project_id"] = project_id
        elif catalog_id is not None:
            params["catalog_id"] = catalog_id
        
        url = get_url_with_query_params(url, params)
        
        headers = get_request_headers(self.config.auth_token)
        
        response = self.session.post(url, headers=headers, verify=False)
        
        if not response.ok:
            raise ValueError(
                f"Failed to search DQ asset with native_id={native_id}, type={asset_type}. "
                f"Status: {response.status_code}, "
                f"Response: {response.text}"
            )

        return json.loads(response.text)
