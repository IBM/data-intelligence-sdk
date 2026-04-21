"""
   Copyright 2026 IBM Corporation

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
"""
Example usage of IssuesProvider for managing data quality issues.

This example demonstrates five main operations:

1. get_issues(): Retrieve a specific issue for a DQ asset, check type, and check_id
   - Requires: dq_asset_id, check_type, check_id, and either project_id OR catalog_id
   - Optional: limit, latest_only, include_children, sort_by, sort_direction
   - Returns: The specific issue item matching the check_id, or None if not found

2. update_issue_values(): Update issue metrics when you have the issue ID directly
   - Requires: issue_id, occurrences, tested_records, and either project_id OR catalog_id
   - Optional: operation ("add" or "replace", default: "add")

3. update_issue_metrics(): Update issue metrics using CAMS asset and check IDs OR check_native_id
   - Option A: Provide asset_id and check_id
   - Option B: Provide check_native_id (format: "<asset_id>/<check_id>")
   - Also requires: occurrences, tested_records, column_name, check_type, and either project_id OR catalog_id
   - Optional: asset_type (default: "column"), operation (default: "add")
   - This method automatically searches for the DQ asset, check, and issue before updating

4. create_issue(): Create a new data quality issue for a check
   - Requires: dq_check_id, reported_for_id, number_of_occurrences, number_of_tested_records, and either project_id OR catalog_id
   - Optional: status (default: "actual"), ignored (default: False)
   - Returns: The created issue_id

5. create_issues_bulk(): Create multiple issues, assets, and checks in a single API call
   - Requires: payload (dict with issues, assets, existing_checks), and either project_id OR catalog_id
   - Optional: incremental_reporting (default: False), refresh_assets (default: False)
   - Returns: The full API response with created issues

Both update methods require occurrences and tested_records as mandatory parameters.
The operation parameter (default: "add") applies to both metrics.
Either project_id or catalog_id must be provided (but not both).
"""

from wxdi.dq_validator.provider import ProviderConfig, IssuesProvider


def main():
    """Main function demonstrating IssuesProvider usage."""

    # Step 1: Configure the provider with your instance URL and authentication token
    config = ProviderConfig(
        url="https://your-instance.cloud.ibm.com",
        auth_token="Bearer your-auth-token-here"
    )

    # Step 2: Create an IssuesProvider instance
    issues_provider = IssuesProvider(config)

    # Define IDs that will be used throughout the examples
    issue_id = "your-issue-id-here"
    project_id = "your-project-id-here"
    catalog_id = "your-catalog-id-here"  # Alternative to project_id

    # Step 3: Get issues for a specific DQ asset, check type, and check_id
    print("\n--- Getting issues for a DQ asset with check_id filter ---")
    dq_asset_id = "08b139ca-35a6-4b61-b87b-aa832870d89c"
    check_type = "format"
    check_id = "065c2b72-4600-4d15-8c48-298a2abf66cd"  # The check ID to filter by

    try:
        # Get issues using catalog_id and check_id
        issue_result = issues_provider.get_issues(
            dq_asset_id=dq_asset_id,
            check_type=check_type,
            check_id=check_id,
            catalog_id="07708fd8-8d77-4a07-a01b-0132130bce0e",
            limit=20,
            latest_only=True,
            include_children=True,
            sort_by="check_name",
            sort_direction="asc"
        )
        if issue_result:
            print(f"Successfully retrieved issue for asset {dq_asset_id} with check_id {check_id}")
            print(f"Issue ID: {issue_result.get('id')}")
            print(f"Check Name: {issue_result.get('check', {}).get('name', 'N/A')}")
            print(f"Occurrences: {issue_result.get('number_of_occurrences', 0)}")
            print(f"Tested Records: {issue_result.get('number_of_tested_records', 0)}")
        else:
            print(f"No issue found matching check_id {check_id}")
    except ValueError as e:
        print(f"Error getting issues: {e}")

    # Example: Get issues using project_id instead
    try:
        issue_result = issues_provider.get_issues(
            dq_asset_id=dq_asset_id,
            check_type="format",
            check_id="b8f3616c-dac2-40bb-a4d3-59aba475ebee",
            project_id=project_id,
            limit=10
        )
        if issue_result:
            print(f"Successfully retrieved issue using project_id")
            print(f"Issue ID: {issue_result.get('id')}")
        else:
            print(f"No matching issue found")
    except ValueError as e:
        print(f"Error getting issues with project_id: {e}")

    # Step 4: Update both occurrences and tested records using issue ID directly
    # Note: Both occurrences and tested_records are mandatory
    # Either project_id OR catalog_id must be provided (but not both)
    print("\n--- Updating issue values directly ---")
    try:
        # Add to both metrics using project_id (default operation is "add")
        result = issues_provider.update_issue_values(
            issue_id,
            occurrences=10,
            tested_records=100,
            project_id=project_id
        )
        print(f"Successfully added 10 occurrences and 100 tested records to issue {issue_id}")
        print(f"Response: {result}")
    except ValueError as e:
        print(f"Error updating issue: {e}")

    # Step 4: Use catalog_id instead of project_id
    try:
        result = issues_provider.update_issue_values(
            issue_id,
            occurrences=10,
            tested_records=100,
            catalog_id=catalog_id
        )
        print(f"Successfully added metrics using catalog_id for issue {issue_id}")
        print(f"Response: {result}")
    except ValueError as e:
        print(f"Error updating issue with catalog_id: {e}")

    # Step 5: Use replace operation instead of add
    try:
        result = issues_provider.update_issue_values(
            issue_id,
            occurrences=100,
            tested_records=1000,
            project_id=project_id,
            operation="replace"
        )
        print(f"Successfully replaced metrics for issue {issue_id}")
        print(f"Response: {result}")
    except ValueError as e:
        print(f"Error replacing metrics: {e}")

    # Example: Using replace operation with different values
    try:
        # Replace both metrics with specific values
        result = issues_provider.update_issue_values(
            issue_id,
            occurrences=0,
            tested_records=0,
            project_id=project_id,
            operation="replace"
        )
        print(f"Successfully reset metrics for issue {issue_id}")
        print(f"Response: {result}")
    except ValueError as e:
        print(f"Error resetting metrics: {e}")

    # Example: Update multiple issues with both metrics
    issues_to_update = [
        ("issue-123", 10, 100),
        ("issue-456", 25, 250),
        ("issue-789", 50, 500),
    ]

    print("\n--- Updating multiple issues with both metrics ---")
    for issue_id, occurrences, records in issues_to_update:
        try:
            result = issues_provider.update_issue_values(
                issue_id,
                occurrences=occurrences,
                tested_records=records,
                project_id=project_id
            )
            print(f"✓ Updated {issue_id}: +{occurrences} occurrences, +{records} tested records")
        except ValueError as e:
            print(f"✗ Failed to update {issue_id}: {e}")

    # Step 6: Update issue metrics using CAMS IDs
    print("\n--- Updating issue metrics using CAMS IDs ---")
    try:
        # Update issue metrics by providing CAMS asset and check IDs with project_id
        result = issues_provider.update_issue_metrics(
            asset_id="b2debda2-6ab9-4a39-8c23-17954e004dcf",
            check_id="7377e2cd-ac0e-4833-8760-fd0e8cb682aa",
            occurrences=10,
            tested_records=100,
            column_name="RTN",    # Required for column type assets
            check_type="format",  # Required: e.g., "format", "completeness", "range", etc.
            project_id="24419069-d649-45cb-a2c1-64d6eed650d5",
            asset_type="column"   # Optional: "column" or "table" (default: "column")
        )
        print(f"Successfully updated issue metrics using CAMS IDs with project_id")
        print(f"Response: {result}")
    except ValueError as e:
        print(f"Error updating issue with CAMS IDs: {e}")

    # Example: Using catalog_id instead of project_id
    try:
        result = issues_provider.update_issue_metrics(
            asset_id="b2debda2-6ab9-4a39-8c23-17954e004dcf",
            check_id="7377e2cd-ac0e-4833-8760-fd0e8cb682aa",
            occurrences=10,
            tested_records=100,
            column_name="RTN",
            check_type="format",
            catalog_id="catalog-123",  # Using catalog_id instead of project_id
            asset_type="column"
        )
        print(f"Successfully updated issue metrics using CAMS IDs with catalog_id")
        print(f"Response: {result}")
    except ValueError as e:
        print(f"Error updating issue with CAMS IDs and catalog_id: {e}")

    # Example: Using check_native_id instead of cams_asset_id and cams_check_id
    print("\n--- Updating issue metrics using check_native_id ---")
    try:
        # When you have the check's native_id, you can use it directly
        # Format: "<cams_asset_id>/<check_type>/<column_name_lower>"
        # Example: "b2debda2-6ab9-4a39-8c23-17954e004dcf/format/rtn"
        result = issues_provider.update_issue_metrics(
            check_native_id="b2debda2-6ab9-4a39-8c23-17954e004dcf/format/rtn",
            occurrences=15,
            tested_records=150,
            column_name="RTN",
            check_type="format",
            project_id="24419069-d649-45cb-a2c1-64d6eed650d5"
        )
        print(f"Successfully updated issue metrics using check_native_id")
        print(f"Response: {result}")
    except ValueError as e:
        print(f"Error updating issue with check_native_id: {e}")

    # Example: Using check_native_id for comparison check with target column
    try:
        # For comparison checks with target columns, the native_id includes the operator and target column
        # Format: "<cams_asset_id>/<check_type>/<column_name_lower>/<operator_camel>/<target_column_lower>"
        # Example: "8c050374-1c06-4bcb-bbad-429233859952/comparison/nbr_years_cli/greaterThanOrEqual/min_years"
        result = issues_provider.update_issue_metrics(
            check_native_id="8c050374-1c06-4bcb-bbad-429233859952/comparison/nbr_years_cli/greaterThanOrEqual/min_years",
            occurrences=20,
            tested_records=200,
            column_name="nbr_years_cli",
            check_type="comparison",
            project_id="ae56642d-095b-47a0-be91-ed556cdbe7d6"
        )
        print(f"Successfully updated comparison check using check_native_id")
        print(f"Response: {result}")
    except ValueError as e:
        print(f"Error updating comparison check with check_native_id: {e}")

    # Example: Update multiple issues using CAMS IDs
    cams_updates = [
        {
            "asset_id": "asset-1",
            "check_id": "check-1",
            "occurrences": 5,
            "tested_records": 50,
            "column_name": "test_column",
            "check_type": "format",
            "project_id": "project-123",
            "asset_type": "column"
        },
        {
            "asset_id": "asset-2",
            "check_id": "check-2",
            "occurrences": 15,
            "tested_records": 150,
            "column_name": "another_column",
            "check_type": "completeness",
            "catalog_id": "catalog-456",  # Using catalog_id instead
            "asset_type": "table"
        },
    ]

    print("\n--- Updating multiple issues using CAMS IDs ---")
    for update_params in cams_updates:
        try:
            result = issues_provider.update_issue_metrics(**update_params)
            print(f"✓ Updated issue for asset {update_params['asset_id']}")
        except ValueError as e:
            print(f"✗ Failed to update issue for asset {update_params['asset_id']}: {e}")

    # Step 7: Create a new issue for a check (using project_id)
    print("\n--- Creating a new issue for a check (using project_id) ---")
    try:
        # Note: Update these values with your actual data
        # check_id: The ID of the check for which to create the issue
        # reported_for_id: The ID of the DQ asset being reported on
        issue_check_id = "c3c97a92-8a45-4456-be6e-ab0d13b65a33"
        reported_for_id = "3f73a9d8-1664-482b-829f-9c879a4dd5d6"

        print(f"\nCreating issue with:")
        print(f"  Check ID: {issue_check_id}")
        print(f"  Reported For ID: {reported_for_id}")
        print(f"  Occurrences: 25")
        print(f"  Tested Records: 1000")
        print(f"  Status: actual")
        print(f"  Ignored: False")
        print(f"  Project ID: {project_id}")

        new_issue_id = issues_provider.create_issue(
            dq_check_id=issue_check_id,
            reported_for_id=reported_for_id,
            number_of_occurrences=25,
            number_of_tested_records=1000,
            status="actual",
            ignored=False,
            project_id=project_id
        )

        print(f"\n✓ Successfully created issue!")
        print(f"  New Issue ID: {new_issue_id}")

    except ValueError as e:
        print(f"\n✗ Error creating issue: {e}")

    # Step 8: Create issue with different parameters (using project_id)
    print("\n--- Creating issue with ignored=True (using project_id) ---")
    try:
        new_issue_id = issues_provider.create_issue(
            dq_check_id="c3c97a92-8a45-4456-be6e-ab0d13b65a33",
            reported_for_id="3f73a9d8-1664-482b-829f-9c879a4dd5d6",
            number_of_occurrences=100,
            number_of_tested_records=5000,
            status="actual",
            ignored=True,  # This issue is ignored
            project_id=project_id
        )

        print(f"\n✓ Successfully created issue with ignored=True")
        print(f"  New Issue ID: {new_issue_id}")
        print(f"  Occurrences: 100")
        print(f"  Tested Records: 5000")
        print(f"  Ignored: True")

    except ValueError as e:
        print(f"\n✗ Error creating issue: {e}")

    # Step 9: Create issue using catalog_id
    print("\n--- Creating issue using catalog_id ---")
    try:
        new_issue_id = issues_provider.create_issue(
            dq_check_id="c3c97a92-8a45-4456-be6e-ab0d13b65a33",
            reported_for_id="3f73a9d8-1664-482b-829f-9c879a4dd5d6",
            number_of_occurrences=50,
            number_of_tested_records=2000,
            status="actual",
            ignored=False,
            catalog_id=catalog_id
        )

        print(f"\n✓ Successfully created issue using catalog_id")
        print(f"  New Issue ID: {new_issue_id}")

    except ValueError as e:
        print(f"\n✗ Error: {e}")

    # Step 10: Create multiple issues in bulk (using project_id)
    print("\n" + "=" * 70)
    print("Creating Multiple Issues in Bulk")
    print("=" * 70)

    # Construct the bulk payload with issues, assets, and existing_checks
    bulk_payload = {
            "issues": [
                {
                    "check": {
                        "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f/format/Validity",
                        "type": "format"
                    },
                    "reported_for": {
                        "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f",
                        "type": "data_asset"
                    },
                    "number_of_occurrences": 200,
                    "number_of_tested_records": 1000,
                    "status": "aggregation",
                    "ignored": False
                },
                {
                    "check": {
                        "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f/format/sample3",
                        "type": "format"
                    },
                    "reported_for": {
                        "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f/NAME",
                        "type": "column"
                    },
                    "number_of_occurrences": 200,
                    "number_of_tested_records": 1000,
                    "status": "actual",
                    "ignored": False
                }
            ],
            "assets": [
                {
                    "name": "ACCOUNT_HOLDERS.csv",
                    "type": "data_asset",
                    "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f",
                    "weight": 1
                },
                {
                    "name": "NAME",
                    "type": "column",
                    "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f/NAME",
                    "parent": {
                        "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f",
                        "type": "data_asset"
                    },
                    "weight": 1
                }
            ],
            "existing_checks": [
                {
                    "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f/format/Validity",
                    "type": "format"
                },
                {
                    "native_id": "ba23145a-6d0a-46db-b314-41526b1e465f/format/sample3",
                    "type": "format"
                }
            ]
    }

    try:
        print(f"\nCreating bulk issues with:")
        print(f"  Number of issues: {len(bulk_payload['issues'])}")
        print(f"  Number of assets: {len(bulk_payload['assets'])}")
        print(f"  Number of checks: {len(bulk_payload['existing_checks'])}")
        print(f"  Project ID: {project_id}")
        print(f"  Incremental Reporting: False")
        print(f"  Refresh Assets: False")

        response = issues_provider.create_issues_bulk(
            payload=bulk_payload,
            project_id=project_id,
            incremental_reporting=False,
            refresh_assets=False
        )

        print(f"\n✓ Successfully created issues in bulk!")
        print(f"  Response keys: {list(response.keys())}")

    except ValueError as e:
        print(f"\n✗ Error creating bulk issues: {e}")

    # Step 11: Create bulk issues with incremental reporting (using catalog_id)
    print("\n--- Creating bulk issues with incremental reporting (using catalog_id) ---")
    try:
        # Same payload structure but with incremental_reporting=True
        response = issues_provider.create_issues_bulk(
            payload=bulk_payload,
            catalog_id=catalog_id,
            incremental_reporting=True,  # Adds archived counts to new issues
            refresh_assets=False
        )

        print(f"\n✓ Successfully created bulk issues with incremental reporting!")
        print(f"  Using catalog_id: {catalog_id}")
        print(f"  Incremental reporting enabled")

    except ValueError as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()