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

import json
from typing import Optional

from .base_provider import BaseProvider
from .config import ProviderConfig
from ..utils import get_request_headers


class IssuesProvider(BaseProvider):
    """Provider for managing data quality issues.

    This provider allows interaction with the data quality issues API,
    including updating issue occurrences and tested records.
    
    Args:
        config (ProviderConfig): Configuration containing URL and authentication token

    Example:
        >>> from dq_validator.provider import ProviderConfig, IssuesProvider
        >>> config = ProviderConfig(
        ...     url="https://your-instance.com",
        ...     auth_token="Bearer your-token"
        ... )
        >>> provider = IssuesProvider(config)
        >>> provider.update_issue_values("issue-123", "project-123", occurrences=10, tested_records=100)
    """
    
    # Error message constants
    _ERR_MISSING_PROJECT_OR_CATALOG = "Either project_id or catalog_id must be provided"
    _ERR_BOTH_PROJECT_AND_CATALOG = "Only one of project_id or catalog_id should be provided, not both"

    def __init__(self, config: ProviderConfig):
        """Initialize the IssuesProvider with configuration.

        Args:
            config (ProviderConfig): Provider configuration with URL and auth token
        """
        super().__init__(config)
    
    def _patch_issue_field(
        self,
        issue_id: str,
        field_path: str,
        value,
        operation: str,
        project_id: Optional[str] = None,
        catalog_id: Optional[str] = None
    ) -> dict:
        """Internal method to patch issue fields with a specified operation.

        Args:
            issue_id (str): The unique identifier of the issue to update
            field_path (str): The JSON Patch path (e.g., "/number_of_occurrences")
            value: The value to set or add (int, bool, str, etc.)
            operation (str): The JSON Patch operation ("replace" or "add")
            project_id (str, optional): The project ID containing the issue
            catalog_id (str, optional): The catalog ID containing the issue
            
        Returns:
            dict: The response from the API containing the updated issue data

        Raises:
            ValueError: If the API request fails or returns an error status, or if neither
                project_id nor catalog_id is provided, or if both are provided
        """
        from ..utils import get_url_with_query_params
        
        # Validate that exactly one of project_id or catalog_id is provided
        if project_id is None and catalog_id is None:
            raise ValueError(self._ERR_MISSING_PROJECT_OR_CATALOG)
        if project_id is not None and catalog_id is not None:
            raise ValueError(self._ERR_BOTH_PROJECT_AND_CATALOG)
        
        url = f"{self.config.url}/data_quality/v4/issues/{issue_id}"
        
        # Add either project_id or catalog_id as query parameter
        params = {}
        if project_id is not None:
            params["project_id"] = project_id
        elif catalog_id is not None:
            params["catalog_id"] = catalog_id
        url = get_url_with_query_params(url, params)
        
        # Prepare the JSON Patch payload
        patch_payload = [
            {
                "op": operation,
                "path": field_path,
                "value": value
            }
        ]
        
        headers = get_request_headers(
            self.config.auth_token, content_type="application/json-patch+json"
        )
        
        response = self.session.patch(
            url,
            headers=headers,
            data=json.dumps(patch_payload),
            verify=False
        )

        if not response.ok:
            raise ValueError(
                f"Failed to {operation} {field_path} for issue {issue_id}. "
                f"Status: {response.status_code}, "
                f"Response: {response.text}"
            )

        return json.loads(response.text)
    
    def update_issue_values(
        self,
        issue_id: str,
        occurrences: int,
        tested_records: int,
        project_id: Optional[str] = None,
        catalog_id: Optional[str] = None,
        operation: str = "add"
    ) -> dict:
        """Update issue occurrences and tested records in a single PATCH call.
        
        This method combines updates for both number_of_occurrences and number_of_tested_records
        in a single API call for better performance. Both occurrences and tested_records are mandatory.
        
        Args:
            issue_id (str): The unique identifier of the issue to update
            occurrences (int): The number of occurrences to update/add (mandatory)
            tested_records (int): The number of tested records to update/add (mandatory)
            project_id (str, optional): The project ID containing the issue
            catalog_id (str, optional): The catalog ID containing the issue
            operation (str): Operation for both metrics - "add" or "replace" (default: "add")
            
        Returns:
            dict: The response from the API containing the updated issue data
            
        Raises:
            ValueError: If the API request fails or returns an error status, or if neither
                project_id nor catalog_id is provided, or if both are provided
            
        Example:
            >>> # Update both metrics with add operation using project_id
            >>> provider.update_issue_values("issue-123", occurrences=10, tested_records=100, project_id="project-456")
            {'issue_id': 'issue-123', 'number_of_occurrences': 777, 'number_of_tested_records': 1100, ...}
            
            >>> # Use catalog_id instead
            >>> provider.update_issue_values("issue-123", occurrences=10, tested_records=100, catalog_id="catalog-789")
            
            >>> # Use replace operation for both
            >>> provider.update_issue_values(
            ...     "issue-123",
            ...     occurrences=100,
            ...     tested_records=1000,
            ...     project_id="project-456",
            ...     operation="replace"
            ... )
        """
        from ..utils import get_url_with_query_params
        
        # Validate that exactly one of project_id or catalog_id is provided
        if project_id is None and catalog_id is None:
            raise ValueError(self._ERR_MISSING_PROJECT_OR_CATALOG)
        if project_id is not None and catalog_id is not None:
            raise ValueError(self._ERR_BOTH_PROJECT_AND_CATALOG)
        
        # Build patch operations list
        patch_operations = []
        
        # Add occurrences operation
        patch_operations.append({
            "op": operation,
            "path": "/number_of_occurrences",
            "value": occurrences
        })
        
        # Add tested records operation
        patch_operations.append({
            "op": operation,
            "path": "/number_of_tested_records",
            "value": tested_records
        })
        
        # Make the PATCH request
        url = f"{self.config.url}/data_quality/v4/issues/{issue_id}"
        
        # Add either project_id or catalog_id as query parameter
        params = {}
        if project_id is not None:
            params["project_id"] = project_id
        elif catalog_id is not None:
            params["catalog_id"] = catalog_id
        url = get_url_with_query_params(url, params)
        
        headers = get_request_headers(
            self.config.auth_token,
            content_type="application/json-patch+json"
        )
        
        response = self.session.patch(
            url,
            headers=headers,
            data=json.dumps(patch_operations),
            verify=False
        )
        
        if not response.ok:
            raise ValueError(
                f"Failed to update issue metrics for issue {issue_id}. "
                f"Status: {response.status_code}, "
                f"Response: {response.text}"
            )
        
        return json.loads(response.text)
    
    def get_issue(
        self,
        reported_for_id: str,
        dq_check_id: str,
        project_id: Optional[str] = None,
        catalog_id: Optional[str] = None
    ) -> dict:
        """Get the issue for a specific asset and check.

        This method uses the REST API POST /data_quality/v4/search_dq_issue
        to search for an issue and returns the full response.

        Args:
            reported_for_id (str): The DQ asset ID to search for
            dq_check_id (str): The check ID to search for
            project_id (str, optional): The project ID containing the issue
            catalog_id (str, optional): The catalog ID containing the issue
            
        Returns:
            dict: The response from the API containing the issue data

        Raises:
            ValueError: If the API request fails or returns an error status, or if neither
                project_id nor catalog_id is provided, or if both are provided
            
        Example:
            >>> # Using project_id
            >>> provider.get_issue(
            ...     reported_for_id="1488a413-99f9-4bed-906d-c33b505d5728",
            ...     dq_check_id="ad277842-dea7-44ef-8e4b-d940df0f79aa",
            ...     project_id="24419069-d649-45cb-a2c1-64d6eed650d5"
            ... )
            >>> # Using catalog_id
            >>> provider.get_issue(
            ...     reported_for_id="1488a413-99f9-4bed-906d-c33b505d5728",
            ...     dq_check_id="ad277842-dea7-44ef-8e4b-d940df0f79aa",
            ...     catalog_id="catalog-123"
            ... )
            {
                'id': 'b8f4252b-cd35-4668-9b35-4635bfc6e2e0',
                'project_id': '24419069-d649-45cb-a2c1-64d6eed650d5',
                ...
            }
        """
        from ..utils import get_url_with_query_params
        
        # Validate that exactly one of project_id or catalog_id is provided
        if project_id is None and catalog_id is None:
            raise ValueError(self._ERR_MISSING_PROJECT_OR_CATALOG)
        if project_id is not None and catalog_id is not None:
            raise ValueError(self._ERR_BOTH_PROJECT_AND_CATALOG)
        
        url = f"{self.config.url}/data_quality/v4/search_dq_issue"

        # Build query parameters
        params = {
            "reported_for.id": reported_for_id,
            "check.id": dq_check_id,
        }
        
        # Add either project_id or catalog_id
        if project_id is not None:
            params["project_id"] = project_id
        elif catalog_id is not None:
            params["catalog_id"] = catalog_id
        
        url = get_url_with_query_params(url, params)
        
        headers = get_request_headers(self.config.auth_token)

        # Make POST request
        response = self.session.post(url, headers=headers, verify=False)
        
        if not response.ok:
            raise ValueError(
                f"Failed to search for issue. "
                f"Status: {response.status_code}, "
                f"Response: {response.text}"
            )
        
        return json.loads(response.text)
    
    def get_issue_id(
        self,
        reported_for_id: str,
        dq_check_id: str,
        project_id: Optional[str] = None,
        catalog_id: Optional[str] = None
    ) -> str:
        """Get the issue ID for a specific asset and check.
        
        This method uses the REST API POST /data_quality/v4/search_dq_issue
        to search for an issue and returns just the issue ID.
        
        Args:
            reported_for_id (str): The DQ asset ID to search for
            dq_check_id (str): The check ID to search for
            project_id (str, optional): The project ID containing the issue
            catalog_id (str, optional): The catalog ID containing the issue
            
        Returns:
            str: The issue ID
            
        Raises:
            ValueError: If the API request fails or returns an error status, or if neither
                project_id nor catalog_id is provided, or if both are provided
            
        Example:
            >>> # Using project_id
            >>> provider.get_issue_id(
            ...     reported_for_id="1488a413-99f9-4bed-906d-c33b505d5728",
            ...     dq_check_id="ad277842-dea7-44ef-8e4b-d940df0f79aa",
            ...     project_id="24419069-d649-45cb-a2c1-64d6eed650d5"
            ... )
            >>> # Using catalog_id
            >>> provider.get_issue_id(
            ...     reported_for_id="1488a413-99f9-4bed-906d-c33b505d5728",
            ...     dq_check_id="ad277842-dea7-44ef-8e4b-d940df0f79aa",
            ...     catalog_id="catalog-123"
            ... )
            'b8f4252b-cd35-4668-9b35-4635bfc6e2e0'
        """
        issue = self.get_issue(reported_for_id, dq_check_id, project_id, catalog_id)
        issue_id = issue.get("id")
        if issue_id is None:
            raise ValueError("Issue ID not found in response")
        return issue_id
    
    def _validate_and_resolve_ids(
        self,
        asset_id: Optional[str],
        check_id: Optional[str],
        check_native_id: Optional[str]
    ) -> tuple[str, str, str]:
        """Validate and resolve asset_id, check_id, and check_native_id.
        
        Args:
            asset_id: The CAMS data asset ID (optional)
            check_id: The CAMS check ID (optional)
            check_native_id: The check native_id (optional)
            
        Returns:
            tuple: (asset_id, check_id, check_native_id) all resolved
            
        Raises:
            ValueError: If validation fails or IDs cannot be resolved
        """
        SEPARATOR = '/'
        
        # Validate that either (asset_id + check_id) or check_native_id is provided
        has_cams_ids = asset_id is not None and check_id is not None
        has_native_id = check_native_id is not None
        
        if not has_cams_ids and not has_native_id:
            raise ValueError("Either (asset_id and check_id) or check_native_id must be provided")
        
        # If check_native_id is provided without asset_id/check_id, extract them
        if has_native_id and not has_cams_ids:
            # Parse check_native_id: first part before first SEPARATOR is asset_id, rest is check_id
            # Format: "<asset_id>/<check_id>" where check_id can contain slashes
            first_slash_index = check_native_id.find(SEPARATOR)
            if first_slash_index == -1:
                raise ValueError(f"Invalid check_native_id format (missing {SEPARATOR}): {check_native_id}")
            asset_id = check_native_id[:first_slash_index]
            check_id = check_native_id[first_slash_index + 1:]
        elif not has_native_id:
            # Construct check_native_id from asset_id and check_id
            # At this point, has_cams_ids is guaranteed to be True
            check_native_id = f"{asset_id}{SEPARATOR}{check_id}"
        
        # At this point, all IDs should be set
        assert asset_id is not None, "asset_id should be set by now"
        assert check_id is not None, "check_id should be set by now"
        assert check_native_id is not None, "check_native_id should be set by now"
        
        return asset_id, check_id, check_native_id

    def update_issue_metrics(
        self,
        occurrences: int,
        tested_records: int,
        column_name: str,
        check_type: str,
        project_id: Optional[str] = None,
        catalog_id: Optional[str] = None,
        asset_type: str = "column",
        operation: str = "add",
        asset_id: Optional[str] = None,
        check_id: Optional[str] = None,
        check_native_id: Optional[str] = None
    ) -> dict:
        """Update issue metrics using CAMS asset and check IDs or check native_id.
        
        This is a convenience method that combines searching for the DQ asset,
        finding the issue by check ID, and updating its metrics in a single call.
        
        Args:
            occurrences (int): The number of occurrences to update/add
            tested_records (int): The number of tested records to update/add
            column_name (str): The column name (required for column type assets)
            check_type (str): The type of check (e.g., "format", "completeness", "range",
                "datatype", "length", "regex", "valid_values", "case", "comparison")
            project_id (str, optional): The project ID containing the issue
            catalog_id (str, optional): The catalog ID containing the issue
            asset_type (str, optional): The type of asset ("column" or "table"). Default is "column"
            operation (str, optional): Operation for both metrics - "add" or "replace". Default is "add"
            asset_id (str, optional): The CAMS data asset ID (required if check_native_id not provided)
            check_id (str, optional): The CAMS check ID (required if check_native_id not provided)
            check_native_id (str, optional): The check native_id (required if asset_id and check_id not provided).
                Format: "<asset_id>/<check_id>" where check_id can contain slashes
            
        Returns:
            dict: The response from the API containing the updated issue data
            
        Raises:
            ValueError: If the API request fails or returns an error status, or if neither
                project_id nor catalog_id is provided, or if both are provided, or if neither
                (asset_id + check_id) nor check_native_id is provided
            
        Example:
            >>> # Using asset_id and check_id with project_id
            >>> provider.update_issue_metrics(
            ...     asset_id="b2debda2-6ab9-4a39-8c23-17954e004dcf",
            ...     check_id="7377e2cd-ac0e-4833-8760-fd0e8cb682aa",
            ...     occurrences=10,
            ...     tested_records=100,
            ...     column_name="RTN",
            ...     check_type="format",
            ...     project_id="24419069-d649-45cb-a2c1-64d6eed650d5",
            ...     asset_type="column"
            ... )
            >>> # Using check_native_id with project_id
            >>> provider.update_issue_metrics(
            ...     check_native_id="b2debda2-6ab9-4a39-8c23-17954e004dcf/rtn/format",
            ...     occurrences=10,
            ...     tested_records=100,
            ...     column_name="RTN",
            ...     check_type="format",
            ...     project_id="24419069-d649-45cb-a2c1-64d6eed650d5"
            ... )
            >>> # Using check_native_id with catalog_id
            >>> provider.update_issue_metrics(
            ...     check_native_id="b2debda2-6ab9-4a39-8c23-17954e004dcf/rtn/format",
            ...     occurrences=10,
            ...     tested_records=100,
            ...     column_name="RTN",
            ...     check_type="format",
            ...     catalog_id="catalog-789"
            ... )
            {'issue_id': 'b8f4252b-cd35-4668-9b35-4635bfc6e2e0', 'number_of_occurrences': 10, ...}
        """
        # Validate that exactly one of project_id or catalog_id is provided
        if project_id is None and catalog_id is None:
            raise ValueError(self._ERR_MISSING_PROJECT_OR_CATALOG)
        if project_id is not None and catalog_id is not None:
            raise ValueError(self._ERR_BOTH_PROJECT_AND_CATALOG)
        
        # Validate and resolve asset_id, check_id, and check_native_id
        asset_id, check_id, check_native_id = self._validate_and_resolve_ids(
            asset_id, check_id, check_native_id
        )
        
        from .dq_search import DQSearchProvider
        
        # Create DQSearchProvider instance with the same config
        search_provider = DQSearchProvider(self.config)
        
        # Build native IDs for searching
        # For asset: <asset_id> (for table) or <asset_id>/<column_name> (for column)
        asset_native_id = asset_id  # For table type, just the asset ID
        if asset_type == "column":
            asset_native_id += '/' + column_name
        
        # Search for the DQ asset
        asset_response = search_provider.search_dq_asset(
            native_id=asset_native_id,
            project_id=project_id,
            catalog_id=catalog_id,
            asset_type=asset_type
        )
        dq_asset_id = asset_response.get("id")
        if not dq_asset_id:
            raise ValueError(f"DQ asset not found for CAMS asset ID: {asset_id}")
        
        # Get the issue using get_issues with the check_id
        issue = self.get_issues(
            dq_asset_id=dq_asset_id,
            check_type=check_type,
            check_id=check_id,
            project_id=project_id,
            catalog_id=catalog_id
        )
        
        if not issue:
            raise ValueError(
                f"Issue not found for CAMS check ID: {check_id} "
                f"with type: {check_type}"
            )
        
        # Get the issue ID from the returned issue
        issue_id = issue.get("id")
        if not issue_id:
            raise ValueError("Issue ID not found in response")
        
        # Update the issue values
        return self.update_issue_values(
            issue_id=issue_id,
            occurrences=occurrences,
            tested_records=tested_records,
            project_id=project_id,
            catalog_id=catalog_id,
            operation=operation
        )
    
    def get_issues(
        self,
        dq_asset_id: str,
        check_type: str,
        check_id: str,
        project_id: Optional[str] = None,
        catalog_id: Optional[str] = None,
        limit: Optional[int] = 200,
        latest_only: Optional[bool] = True,
        include_children: Optional[bool] = False,
        sort_by: Optional[str] = "check_name",
        sort_direction: Optional[str] = "asc"
    ) -> Optional[dict]:
        """Get issues for a specific DQ asset and check type, filtered by check_id.
        
        This method uses the REST API GET /data_quality/v4/issues to retrieve
        issues based on the DQ asset ID and check type, then filters to return
        only the issue whose check.native_id contains the specified check_id.
        
        Args:
            dq_asset_id (str): The DQ asset ID (reported_for.id)
            check_type (str): The type of check (e.g., "completeness", "format", "range",
                "datatype", "length", "regex", "valid_values", "case", "comparison")
            check_id (str): The check ID to filter by. Returns only the issue whose
                check.native_id contains this check_id
            project_id (str, optional): The project ID containing the issues
            catalog_id (str, optional): The catalog ID containing the issues
            limit (int, optional): Maximum number of issues to return. Default is 20
            latest_only (bool, optional): Return only the latest issues. Default is True
            include_children (bool, optional): Include child issues. Default is False
            sort_by (str, optional): Field to sort by. Default is "check_name"
            sort_direction (str, optional): Sort direction ("asc" or "desc"). Default is "asc"
            
        Returns:
            dict: The specific issue item that matches the check_id, or None if no match found
            
        Raises:
            ValueError: If the API request fails or returns an error status, or if neither
                project_id nor catalog_id is provided, or if both are provided
            
        Example:
            >>> # Filter by check_id with catalog_id
            >>> provider.get_issues(
            ...     dq_asset_id="08b139ca-35a6-4b61-b87b-aa832870d89c",
            ...     check_type="format",
            ...     check_id="45a0e78c-ee2c-40bc-956f-743251cef2a6",
            ...     catalog_id="07708fd8-8d77-4a07-a01b-0132130bce0e"
            ... )
            {
                'id': '656a80e0-64b4-418e-bdf4-de86450d2e76',
                'check': {
                    'id': '6ff20abc-b41e-4c2e-8bc8-2ad94e3fd562',
                    'native_id': 'b7a254e8-a88d-44e2-920d-5b237a1085dd/45a0e78c-ee2c-40bc-956f-743251cef2a6',
                    ...
                },
                ...
            }
            >>> # Using project_id
            >>> provider.get_issues(
            ...     dq_asset_id="08b139ca-35a6-4b61-b87b-aa832870d89c",
            ...     check_type="format",
            ...     check_id="b8f3616c-dac2-40bb-a4d3-59aba475ebee",
            ...     project_id="24419069-d649-45cb-a2c1-64d6eed650d5"
            ... )
        """
        from ..utils import get_url_with_query_params
        
        # Validate that exactly one of project_id or catalog_id is provided
        if project_id is None and catalog_id is None:
            raise ValueError(self._ERR_MISSING_PROJECT_OR_CATALOG)
        if project_id is not None and catalog_id is not None:
            raise ValueError(self._ERR_BOTH_PROJECT_AND_CATALOG)
        
        url = f"{self.config.url}/data_quality/v4/issues"
        
        # Build query parameters
        params = {
            "reported_for.id": dq_asset_id,
            "type": check_type
        }
        
        # Add either project_id or catalog_id
        if project_id is not None:
            params["project_id"] = project_id
        elif catalog_id is not None:
            params["catalog_id"] = catalog_id
        
        # Add optional parameters
        if limit is not None:
            params["limit"] = str(limit)
        if latest_only is not None:
            params["latest_only"] = str(latest_only).lower()
        if include_children is not None:
            params["include_children"] = str(include_children).lower()
        if sort_by is not None:
            params["sort_by"] = sort_by
        if sort_direction is not None:
            params["sort_direction"] = sort_direction
        
        url = get_url_with_query_params(url, params)
        
        headers = get_request_headers(self.config.auth_token)
        
        # Make GET request
        response = self.session.get(url, headers=headers, verify=False)
        
        if not response.ok:
            raise ValueError(
                f"Failed to get issues. "
                f"Status: {response.status_code}, "
                f"Response: {response.text}"
            )
        
        result = json.loads(response.text)
        
        # Filter the issues by check_id
        issues = result.get("issues", [])
        for issue in issues:
            # Get the check object from the issue
            check = issue.get("check", {})
            # Get the native_id from the check
            check_native_id = check.get("native_id", "")
            # Check if the check_id is contained in the native_id
            if check_id in check_native_id:
                return issue
        
        # If no match found, return None
        return None
    
    def create_issue(
        self,
        dq_check_id: str,
        reported_for_id: str,
        number_of_occurrences: int,
        number_of_tested_records: int,
        status: str = "actual",
        ignored: bool = False,
        project_id: Optional[str] = None,
        catalog_id: Optional[str] = None
    ) -> str:
        """
        Create a new data quality issue.
        
        This method creates a new issue for a specific check and data asset.
        
        Args:
            dq_check_id: The ID of the check for which to create the issue
            reported_for_id: The ID of the data asset being reported on
            number_of_occurrences: Number of issue occurrences
            number_of_tested_records: Total number of records tested
            status: Status of the issue (default: "actual")
            ignored: Whether the issue is ignored (default: False)
            project_id (str, optional): The project ID containing the issue
            catalog_id (str, optional): The catalog ID containing the issue
        
        Returns:
            str: The created issue ID
        
        Raises:
            ValueError: If the API request fails or returns an error status, or if neither
                project_id nor catalog_id is provided, or if both are provided
        
        Example:
            >>> provider.create_issue(
            ...     dq_check_id="6be18374-573a-4cf8-8ab7-e428506e428b",
            ...     reported_for_id="894d01fd-bdfc-4a4f-b68b-62751e06e06a",
            ...     number_of_occurrences=123,
            ...     number_of_tested_records=456789,
            ...     project_id="project-123"
            ... )
            '046605b5-48d9-489e-b846-8ef96a7a1aba'
        """
        from ..utils import get_url_with_query_params
        
        # Validate that exactly one of project_id or catalog_id is provided
        if project_id is None and catalog_id is None:
            raise ValueError(self._ERR_MISSING_PROJECT_OR_CATALOG)
        if project_id is not None and catalog_id is not None:
            raise ValueError(self._ERR_BOTH_PROJECT_AND_CATALOG)
        
        # Build the URL for issue creation API
        url = f"{self.config.url}/data_quality/v4/issues"
        
        # Add either project_id or catalog_id as query parameter
        params = {}
        if project_id is not None:
            params["project_id"] = project_id
        elif catalog_id is not None:
            params["catalog_id"] = catalog_id
        url = get_url_with_query_params(url, params)
        
        # Prepare the payload
        payload = {
            "check": {
                "id": dq_check_id
            },
            "reported_for": {
                "id": reported_for_id
            },
            "number_of_occurrences": number_of_occurrences,
            "number_of_tested_records": number_of_tested_records,
            "status": status,
            "ignored": ignored
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
                f"Failed to create issue. "
                f"Status: {response.status_code}, "
                f"Response: {response.text}"
            )
        
        # Parse response and extract issue_id
        result = json.loads(response.text)
        issue_id = result.get("id")
        if not issue_id:
            raise ValueError("Issue ID not found in response")
        
        return issue_id
    
    def create_issues_bulk(
        self,
        payload: dict,
        project_id: Optional[str] = None,
        catalog_id: Optional[str] = None,
        incremental_reporting: bool = False,
        refresh_assets: bool = False
    ) -> dict:
        """
        Create multiple data quality issues in bulk.
        
        This method creates multiple issues, assets, and checks in a single API call
        for better performance when reporting multiple related issues.
        
        Args:
            payload: The bulk payload containing issues, assets, and existing_checks arrays.
                Expected structure:
                {
                    "issues": [
                        {
                            "check": {"native_id": str, "type": str},
                            "reported_for": {"native_id": str, "type": str},
                            "number_of_occurrences": int,
                            "number_of_tested_records": int,
                            "status": str,
                            "ignored": bool
                        },
                        ...
                    ],
                    "assets": [
                        {
                            "name": str,
                            "type": str,
                            "native_id": str,
                            "weight": int,
                            "parent": {"native_id": str, "type": str} (optional)
                        },
                        ...
                    ],
                    "existing_checks": [
                        {"native_id": str, "type": str},
                        ...
                    ]
                }
            project_id (str, optional): The project ID containing the issues
            catalog_id (str, optional): The catalog ID containing the issues
            incremental_reporting (bool): If true, adds archived issue counts to new issues
                instead of replacing them. Default is False.
            refresh_assets (bool): If true, assets will be refreshed and any assets not
                present in the updated list will be deleted. Default is False.
        
        Returns:
            dict: The response from the API containing the created issues data
        
        Raises:
            ValueError: If the API request fails or returns an error status, or if neither
                project_id nor catalog_id is provided, or if both are provided
        
        Example:
            >>> payload = {
            ...     "issues": [
            ...         {
            ...             "check": {
            ...                 "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f/format/Validity",
            ...                 "type": "format"
            ...             },
            ...             "reported_for": {
            ...                 "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f",
            ...                 "type": "data_asset"
            ...             },
            ...             "number_of_occurrences": 200,
            ...             "number_of_tested_records": 1000,
            ...             "status": "aggregation",
            ...             "ignored": False
            ...         }
            ...     ],
            ...     "assets": [
            ...         {
            ...             "name": "ACCOUNT_HOLDERS.csv",
            ...             "type": "data_asset",
            ...             "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f",
            ...             "weight": 1
            ...         }
            ...     ],
            ...     "existing_checks": [
            ...         {
            ...             "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f/format/Validity",
            ...             "type": "format"
            ...         }
            ...     ]
            ... }
            >>> provider.create_issues_bulk(
            ...     payload=payload,
            ...     project_id="project-123",
            ...     incremental_reporting=True
            ... )
            {'issues': [...], 'assets': [...], ...}
        """
        from ..utils import get_url_with_query_params
        
        # Validate that exactly one of project_id or catalog_id is provided
        if project_id is None and catalog_id is None:
            raise ValueError(self._ERR_MISSING_PROJECT_OR_CATALOG)
        if project_id is not None and catalog_id is not None:
            raise ValueError(self._ERR_BOTH_PROJECT_AND_CATALOG)
        
        # Build the URL for bulk issue creation API
        url = f"{self.config.url}/data_quality/v4/create_issues"
        
        # Build query parameters
        params = {}
        if project_id is not None:
            params["project_id"] = project_id
        elif catalog_id is not None:
            params["catalog_id"] = catalog_id
        
        # Add boolean query parameters
        params["incremental_reporting"] = str(incremental_reporting).lower()
        params["refresh_assets"] = str(refresh_assets).lower()
        
        url = get_url_with_query_params(url, params)
        
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
                f"Failed to create issues in bulk. "
                f"Status: {response.status_code}, "
                f"Response: {response.text}"
            )
        
        # Parse and return response
        return json.loads(response.text)
