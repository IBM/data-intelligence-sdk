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
Issue reporting utilities for data quality validation.

This module provides utilities to report validation issues to CAMS,
including creating and updating checks based on validation results.
"""

from typing import Optional, Dict, Tuple, Any
from .provider import (
    ChecksProvider,
    IssuesProvider,
    DimensionsProvider,
    DQAssetsProvider,
    DQSearchProvider,
    ProviderConfig,
    CamsProvider
)
from .validator import Validator
from .base import BaseCheck


class IssueReporter:
    """
    Issue reporter for managing data quality checks and issues.
    
    This class provides methods to create and update data quality checks
    and their corresponding issues in CAMS.
    
    Args:
        config (ProviderConfig): Configuration containing URL and authentication token
    
    Example:
        >>> from dq_validator.provider import ProviderConfig
        >>> from dq_validator.issue_reporting import IssueReporter
        >>> config = ProviderConfig(
        ...     url="https://your-instance.com",
        ...     auth_token="Bearer your-token"
        ... )
        >>> reporter = IssueReporter(config)
        >>> reporter.report_issues(stats, asset_id, project_id, validator)
    """
    
    def __init__(self, config: ProviderConfig):
        """
        Initialize the IssueReporter with configuration.
        
        Args:
            config (ProviderConfig): Provider configuration with URL and auth token
        """
        self.config = config
        self.check_provider = ChecksProvider(config)
        self.issues_provider = IssuesProvider(config)
        self.dimension_provider = DimensionsProvider(config)
        self.asset_provider = DQAssetsProvider(config)
        self.search_provider = DQSearchProvider(config)
        self.cams_provider = CamsProvider(config)
    
    @staticmethod
    def map_check_name_to_check_type(check_name: str) -> Optional[str]:
        """
        Map check class names to CheckType enum values.
        
        Args:
            check_name: Check name from check class (e.g., "format_check")
        
        Returns:
            CheckType enum value (e.g., "format") or None if not found
        
        Example:
            >>> IssueReporter.map_check_name_to_check_type("format_check")
            'format'
            >>> IssueReporter.map_check_name_to_check_type("completeness_check")
            'completeness'
        """
        # Mapping from check class names to CheckType enum values
        check_name_to_type = {
            "case_check": "case",
            "comparison_check": "comparison",
            "completeness_check": "completeness",
            "datatype_check": "data_type",
            "format_check": "format",
            "length_check": "length",
            "range_check": "range",
            "regex_check": "regex",
            "valid_values_check": "possible_values",
        }
        return check_name_to_type.get(check_name)
    
    @staticmethod
    def map_check_name_to_cpd_name(check_name: str) -> Optional[str]:
        """
        Map check class names to CPD (Cloud Pak for Data) display names.
        
        Args:
            check_name: Check name from check class (e.g., "format_check")
        
        Returns:
            CPD display name (e.g., "Format check") or None if not found
        
        Example:
            >>> IssueReporter.map_check_name_to_cpd_name("format_check")
            'Format check'
            >>> IssueReporter.map_check_name_to_cpd_name("completeness_check")
            'Completeness check'
        """
        # Mapping from check class names to CPD display names
        check_name_to_cpd_name: Dict[str, str] = {
            "case_check": "Capitalization style check",
            "comparison_check": "Comparison check",
            "completeness_check": "Completeness check",
            "datatype_check": "Data type check",
            "format_check": "Format check",
            "length_check": "Length check",
            "range_check": "Range check",
            "regex_check": "Regex check",
            "valid_values_check": "Possible values check",
        }
        return check_name_to_cpd_name.get(check_name)
    
    @staticmethod
    def get_check_from_validator(
        validator: Validator,
        column_name: str,
        check_name: str
    ) -> Optional[BaseCheck]:
        """
        Get the check object for a specific column and check name from validator.
        
        Args:
            validator: Validator instance containing rules and checks
            column_name: Name of the column
            check_name: Name of the check (e.g., "format_check")
        
        Returns:
            BaseCheck instance if found, None otherwise
        
        Example:
            >>> check = IssueReporter.get_check_from_validator(validator, "email", "format_check")
            >>> dimension_name = check.get_dimension().name
            'VALIDITY'
        """
        # Find the rule for this column
        for rule in validator.rules:
            if rule.column_name == column_name:
                # Find the check with matching name
                for check in rule.checks:
                    if check.get_check_name() == check_name:
                        return check
        return None
    
    def get_check_id(
        self,
        check_native_id: str,
        check_type: str,
        project_id: Optional[str] = None,
        catalog_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Get the check ID by searching with native_id and check_type.
        
        Args:
            check_native_id: The native ID of the check to search for
            check_type: The type of the check (e.g., "format", "data_type", "completeness")
            project_id: Project ID (optional)
            catalog_id: Catalog ID (optional)
        
        Returns:
            str: The check ID from the search response, or None if not found
        
        Example:
            >>> check_id = reporter.get_check_id(
            ...     check_native_id="8c050374-1c06-4bcb-bbad-429233859952/45877cbb-b123-44dc-9fb3-56b24ab1535e",
            ...     check_type="data_type",
            ...     project_id="project-123"
            ... )
            >>> print(check_id)
            '61f2d1b5-f5f9-42d5-89ed-14733a32bfcb'
        """
        try:
            # Call get_check to fetch check details
            check_response = self.search_provider.search_dq_check(
                native_id=check_native_id,
                check_type=check_type,
                project_id=project_id,
                catalog_id=catalog_id
            )
            
            # Extract and return native_id from response
            return check_response.get("id")
        except Exception:
            # Return None if any error occurs
            return None
    
    def create_check(
        self,
        asset_id: str,
        column_name: str,
        check_obj: BaseCheck,
        project_id: Optional[str] = None,
        catalog_id: Optional[str] = None
    ) -> str:
        """
        Create a data quality check.
        
        Args:
            cams_asset_id: Data asset ID
            column_name: Name of the column
            check_obj: BaseCheck instance to extract check details from
            project_id: Project ID (optional)
            catalog_id: Catalog ID (optional)
        
        Returns:
            str: The created check ID
        """
        # Extract check details from check object
        check_name = check_obj.get_check_name()
        dimension_name = check_obj.get_dimension().name
        
        # Map check_name to check_type
        check_type = self.map_check_name_to_check_type(check_name)
        if check_type is None:
            check_type = check_name  # Fallback to check_name
        
        # Get CPD display name for the check
        cpd_name = self.map_check_name_to_cpd_name(check_name)
        if cpd_name is None:
            cpd_name = check_name  # Fallback to check_name
        
        # Special handling for comparison check to get operator
        native_id_suffix = ""
        if check_name == "comparison_check":
            from .checks.comparison_check import ComparisonCheck
            
            if isinstance(check_obj, ComparisonCheck):
                # Get operator name and convert to camelCase
                operator_name = check_obj.operator.name  # e.g., "GREATER_THAN"
                # Convert GREATER_THAN to greaterThan
                parts = operator_name.lower().split('_')
                operator_camel = parts[0] + ''.join(word.capitalize() for word in parts[1:])
                
                # If target_column exists, include it in native_id_suffix
                if check_obj.target_column:
                    target_col_lower = check_obj.target_column.lower()
                    native_id_suffix = f"{operator_camel}/{target_col_lower}"
                else:
                    native_id_suffix = operator_camel
        
        # Get dimension ID from dimension name
        dimension_id = self.dimension_provider.search_dimension(dimension_name)
        
        # Build native_id with the suffix
        column_name_lower = column_name.lower()
        native_id = f"{asset_id}/{check_type}/{column_name_lower}/{native_id_suffix}"
        
        # Create the check and return the check_id
        check_id = self.check_provider.create_check(
            name=cpd_name,
            dimension_id=dimension_id,
            native_id=native_id,
            check_type=check_type,
            project_id=project_id,
            catalog_id=catalog_id
        )
        
        return check_id
    
    def _validate_and_prepare_check_data(
        self,
        column_name: str,
        check_name: str,
        stats: Dict[str, int],
        data_asset_entity,
        column_id_map: Dict[str, str],
        validator: Validator
    ) -> Optional[Tuple[str, str, BaseCheck, int, int]]:
        """
        Validate check data and return prepared values.
        
        Args:
            column_name: Name of the column
            check_name: Name of the check
            stats: Statistics dictionary with 'failed' and 'total' keys
            data_asset_entity: Data asset entity from CAMS
            column_id_map: Map of column names to column asset IDs
            validator: Validator instance
        
        Returns:
            Tuple of (check_type, column_id, check_obj, occurrences, total) if valid
            None if validation fails (caller should skip this check)
        """
        number_of_occurrences = stats['failed']
        total_records = stats['total']
        
        # Guard: Skip if no failures
        if number_of_occurrences <= 0:
            return None
        
        # Guard: Skip if check type cannot be mapped
        check_type = self.map_check_name_to_check_type(check_name)
        if not check_type:
            return None
        
        # Guard: Skip if column info doesn't exist
        if not (data_asset_entity.column_info and column_name in data_asset_entity.column_info):
            return None
        
        # Guard: Skip if column asset ID not found
        column_id = column_id_map.get(column_name)
        if not column_id:
            return None
        
        # Guard: Skip if check object not found in validator
        check_obj = self.get_check_from_validator(validator, column_name, check_name)
        if not check_obj:
            return None
        
        return (check_type, column_id, check_obj, number_of_occurrences, total_records)
    
    def _create_check_and_issue(
        self,
        asset_id: str,
        column_name: str,
        column_id: str,
        check_name: str,
        check_obj: BaseCheck,
        number_of_occurrences: int,
        total_records: int,
        project_id: str
    ) -> bool:
        """
        Create a check and its associated issue.
        If check creation fails with 409 (already exists), find the existing check and update its metrics.
        
        Args:
            asset_id: CAMS asset ID
            column_name: Name of the column
            column_id: Column asset ID
            check_name: Name of the check
            check_obj: Check object
            number_of_occurrences: Number of failed occurrences
            total_records: Total number of records
            project_id: Project ID
        
        Returns:
            True if successful, False if creation failed
        """
        # Get check_type for potential fallback
        check_type = self.map_check_name_to_check_type(check_name)
        if not check_type:
            print(f"Warning: Could not map check_name '{check_name}' to check_type")
            return False
        
        try:
            check_id = self.create_check(
                asset_id=asset_id,
                column_name=column_name,
                check_obj=check_obj,
                project_id=project_id
            )
            # Create the issue directly using the issues provider
            self.issues_provider.create_issue(
                check_id=check_id,
                reported_for_id=column_id,
                number_of_occurrences=number_of_occurrences,
                number_of_tested_records=total_records,
                project_id=project_id,
                catalog_id=None
            )
            return True
        except ValueError as e:
            error_msg = str(e)
            # If 409 conflict (check already exists), try to find and update it
            if "409" in error_msg or "already exists" in error_msg:
                try:
                    # Get existing checks for this column asset filtered by check type
                    checks = self.check_provider.get_checks(
                        asset_id=column_id,
                        check_type=check_type,
                        project_id=project_id
                    )
                    
                    # Find the check with matching type
                    existing_check_id = None
                    existing_check_native_id = None
                    for check in checks:
                        if check.get("type") == check_type:
                            existing_check_id = check.get("id")
                            existing_check_native_id = check.get("native_id")
                            break
                    
                    if existing_check_id:
                        # Update issue metrics for the existing check
                        try:
                            self.issues_provider.update_issue_metrics(
                                occurrences=number_of_occurrences,
                                tested_records=total_records,
                                column_name=column_name,
                                check_type=check_type,
                                project_id=project_id,
                                asset_type="column",
                                operation="add",
                                check_native_id=existing_check_native_id
                            )
                            return True
                        except ValueError as update_error:
                            # If update fails, try to create the issue
                            self._handle_update_failure(
                                update_error, asset_id, existing_check_id, check_type,
                                column_name, check_name, column_id,
                                number_of_occurrences, total_records, project_id
                            )
                            return True
                    else:
                        print(f"Warning: Check already exists but could not be found for column '{column_name}', check '{check_name}'")
                        return False
                except ValueError as get_error:
                    print(f"Warning: Failed to get existing checks for column '{column_name}', check '{check_name}': {get_error}")
                    return False
            else:
                # Different error - log and return False
                print(f"Warning: Failed to create check for column '{column_name}', check '{check_name}': {e}")
                return False
    
    def _handle_update_failure(
        self,
        error: ValueError,
        asset_id: str,
        cams_check_id: str,
        check_type: str,
        column_name: str,
        check_name: str,
        column_id: str,
        number_of_occurrences: int,
        total_records: int,
        project_id: str
    ) -> bool:
        """
        Handle failure when updating issue metrics.
        
        Args:
            error: The ValueError that was raised
            asset_id: CAMS asset ID
            cams_check_id: CAMS check ID
            check_type: Type of the check
            column_name: Name of the column
            check_name: Name of the check
            column_id: Column asset ID
            number_of_occurrences: Number of failed occurrences
            total_records: Total number of records
            project_id: Project ID
        
        Returns:
            True (always, to indicate error was handled)
        """
        error_msg = str(error)
        
        # If issue not found, try to create it
        if "Issue not found" in error_msg or "Issue ID not found" in error_msg:
            check_id = self.get_check_id(
                check_native_id=f"{asset_id}/{cams_check_id}",
                check_type=check_type,
                project_id=project_id
            )
            
            if check_id:
                # Create the issue directly using the issues provider
                self.issues_provider.create_issue(
                    check_id=cams_check_id,
                    reported_for_id=column_id,
                    number_of_occurrences=number_of_occurrences,
                    number_of_tested_records=total_records,
                    project_id=project_id,
                    catalog_id=None
                )
            else:
                print(f"Warning: Could not find check_id for column '{column_name}', check '{check_name}'. Issue not created.")
        else:
            # Different error - log and continue
            print(f"Warning: Failed to update issue metrics for column '{column_name}', check '{check_name}': {error}")
        
        return True
    
    def _handle_existing_check(
        self,
        column_info,
        check_type: str,
        asset_id: str,
        column_name: str,
        check_name: str,
        column_id: str,
        number_of_occurrences: int,
        total_records: int,
        project_id: str
    ) -> bool:
        """
        Handle updating an existing check.
        
        Args:
            column_info: Column information from data asset
            check_type: Type of the check
            asset_id: CAMS asset ID
            column_name: Name of the column
            check_name: Name of the check
            column_id: Column asset ID
            number_of_occurrences: Number of failed occurrences
            total_records: Total number of records
            project_id: Project ID
        
        Returns:
            True if check was found and handled, False if check not found
        """
        for check in column_info.column_checks:
            if check.metadata.type != check_type:
                continue
            
            cams_check_id = check.metadata.check_id
            if not cams_check_id:
                continue
            
            # Try to update existing issue metrics
            try:
                self.issues_provider.update_issue_metrics(
                    cams_asset_id=asset_id,
                    cams_check_id=cams_check_id,
                    occurrences=number_of_occurrences,
                    tested_records=total_records,
                    column_name=column_name,
                    check_type=check_type,
                    project_id=project_id,
                    asset_type="column",
                    operation="add"
                )
                return True
            except ValueError as e:
                self._handle_update_failure(
                    e, asset_id, cams_check_id, check_type,
                    column_name, check_name, column_id,
                    number_of_occurrences, total_records, project_id
                )
                return True
        
        return False
    
    def report_issues(
        self,
        stats: Dict[str, Any],
        asset_id: str,
        validator: Validator
    ) -> None:
        """
        Report issues by fetching data asset from CAMS and checking for existing checks.
        
        This method iterates over the combined statistics (column, check) pairs and:
        1. Fetches the data asset entity from CAMS
        2. Fetches all column assets and builds a lookup map
        3. For each (column, check) pair in combined_statistics:
        
          - Checks if the column has the specific check type in the data asset
          - If the check exists, obtains check_id, number_of_occurrences, and total_records
          - If the check doesn't exist, calls create_check method
        
        Args:
            stats: Nested dictionary from consolidator.get_combined_statistics()
                Format: {'column': {'check': {'passed': int, 'failed': int, 'total': int}}}
            asset_id: The CAMS Data asset ID
            project_id: Project ID containing the data asset
            validator: Validator instance containing rules and checks
        
        Example:
            >>> consolidator = ValidationResultConsolidated(validator=validator, store_errors=True)
            >>> consolidator.add_results(results)
            >>> combined_stats = consolidator.get_combined_statistics()
            >>> reporter.report_issues(
            ...     stats=combined_stats,
            ...     asset_id="asset_id_123",
            ...     project_id="project_id_456",
            ...     validator=validator
            ... )
        """
        # Validate that project_id is configured
        if not self.config.project_id:
            raise ValueError("project_id must be set in ProviderConfig before calling report_issues()")
        
        project_id = self.config.project_id
        combined_stats = {}
        for column, checks in stats.items():
            for check, stat in checks.items():
                combined_stats[(column, check)] = stat

        # Fetch data asset entity
        data_asset = self.cams_provider.get_asset_by_id(asset_id)
        data_asset_entity = data_asset.entity
        
        # Fetch all column assets once and build a lookup map for efficiency
        assets_response = self.asset_provider.get_assets(project_id=project_id, asset_type="column")
        column_id_map = {asset['name']: asset['id'] for asset in assets_response.get('assets', [])}
        
        # Iterate over combined statistics
        for (column_name, check_name), individual_stats in combined_stats.items():
            # Validate and prepare data
            validated_data = self._validate_and_prepare_check_data(
                column_name, check_name, individual_stats, data_asset_entity, column_id_map, validator
            )
            if not validated_data:
                continue
            
            check_type, column_id, check_obj, number_of_occurrences, total_records = validated_data
            # Safe to access since validation already checked column_info exists
            column_info = data_asset_entity.column_info[column_name]  # type: ignore
            
            # If no checks exist for this column, create the check and issue
            if not column_info.column_checks:
                self._create_check_and_issue(
                    asset_id, column_name, column_id, check_name,
                    check_obj, number_of_occurrences, total_records, project_id
                )
                continue
            
            # Try to handle existing check
            check_handled = self._handle_existing_check(
                column_info, check_type, asset_id, column_name, check_name,
                column_id, number_of_occurrences, total_records, project_id
            )
            
            # If check not found, create it
            if not check_handled:
                self._create_check_and_issue(
                    asset_id, column_name, column_id, check_name,
                    check_obj, number_of_occurrences, total_records, project_id
                )
