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
Example demonstrating the complete DQ workflow:
1. Fetch CAMS asset by data_asset_id and project_id (or catalog_id)
2. Read the CAMS object to get check_id from column_info
3. Search for DQ checks by native_id (format: <data_asset_id>/<check_id>)
4. Search for DQ assets by native_id (format: <data_asset_id>/<column_name>)
5. Search issue for a specific asset and check
6. Update (patch) the issue by issue_id

This example shows how to use the CamsProvider, DQSearchProvider, and IssuesProvider
to work with data quality checks, assets, and issues.

Note: All methods now support either project_id OR catalog_id (but not both).
"""

from wxdi.dq_validator.provider import ProviderConfig, CamsProvider, DQSearchProvider, IssuesProvider


def main():
    # Configuration
    # You can use either project_id OR catalog_id (but not both)
    data_asset_id = "b2debda2-6ab9-4a39-8c23-17954e004dcf"
    project_id = "24419069-d649-45cb-a2c1-64d6eed650d5"
    catalog_id = None  # Alternative: use catalog_id instead of project_id
    column_name = "RTN"  # Column to check
    check_type = "format"  # Type of check to find

    config = ProviderConfig(
        url="https://cpd-ikc.apps.dqdev.ibm.com",
        auth_token="Bearer your-token-here",
        project_id=project_id
    )

    # Initialize providers
    cams_provider = CamsProvider(config)
    dq_search = DQSearchProvider(config)
    issues_provider = IssuesProvider(config)

    # Step 1: Fetch CAMS asset by data_asset_id and project_id
    print("=" * 70)
    print("STEP 1: Fetch CAMS Asset")
    print("=" * 70)

    try:
        cams_asset = cams_provider.get_asset_by_id(
            asset_id=data_asset_id,
            options={"hide_deprecated_response_fields": "false"}
        )

        print(f"✓ Fetched CAMS Asset:")
        print(f"  Asset ID: {cams_asset.metadata.asset_id}")
        print(f"  Name: {cams_asset.metadata.name}")
        print(f"  Asset Type: {cams_asset.metadata.asset_type}")

    except ValueError as e:
        print(f"✗ Error fetching CAMS asset: {e}")
        return

    # Step 2: Read the CAMS object to get check_id from column_info
    # Iterate through column_checks and find the first check with matching type
    print("\n" + "=" * 70)
    print("STEP 2: Extract Check ID from CAMS Asset")
    print("=" * 70)

    check_id = None

    try:
        # Navigate to column_info for the specified column
        if hasattr(cams_asset.entity, 'column_info') and column_name in cams_asset.entity.column_info:
            column_info = cams_asset.entity.column_info[column_name]

            # Iterate through column_checks to find the check with matching type
            if hasattr(column_info, 'column_checks') and column_info.column_checks:
                for check in column_info.column_checks:
                    if check.metadata.type == check_type:
                        check_id = check.metadata.check_id
                        print(f"✓ Found Check in Column '{column_name}':")
                        print(f"  Check ID: {check_id}")
                        print(f"  Check Type: {check.metadata.type}")
                        break

                if not check_id:
                    print(f"✗ No check with type '{check_type}' found for column '{column_name}'")
                    return
            else:
                print(f"✗ No checks found for column '{column_name}'")
                return
        else:
            print(f"✗ Column '{column_name}' not found in asset")
            return

    except Exception as e:
        print(f"✗ Error extracting check ID: {e}")
        return

    # Step 3: Search for DQ check by native_id
    # The native_id format is: <data_asset_id>/<check_id>
    print("\n" + "=" * 70)
    print("STEP 3: Search for DQ Check")
    print("=" * 70)

    check_native_id = f"{data_asset_id}/{check_id}"

    try:
        check_result = dq_search.search_dq_check(
            native_id=check_native_id,
            check_type=check_type,
            project_id=project_id,
            include_children=True
        )

        print(f"✓ Found DQ Check:")
        print(f"  ID: {check_result['id']}")
        print(f"  Name: {check_result['name']}")
        print(f"  Type: {check_result['type']}")
        print(f"  Native ID: {check_result['native_id']}")

        dq_check_id = check_result['id']

    except ValueError as e:
        print(f"✗ Error searching for check: {e}")
        return

    # Step 4: Search for DQ asset by native_id
    # The native_id format is: <data_asset_id>/<column_name>
    print("\n" + "=" * 70)
    print("STEP 4: Search for DQ Asset")
    print("=" * 70)

    asset_native_id = f"{data_asset_id}/{column_name}"
    asset_type = "column"

    try:
        asset_result = dq_search.search_dq_asset(
            native_id=asset_native_id,
            project_id=project_id,
            asset_type=asset_type,
            include_children=True,
            get_actual_asset=False
        )

        print(f"✓ Found DQ Asset:")
        print(f"  ID: {asset_result['id']}")
        print(f"  Name: {asset_result['name']}")
        print(f"  Type: {asset_result['type']}")
        print(f"  Native ID: {asset_result['native_id']}")

        dq_asset_id = asset_result['id']

    except ValueError as e:
        print(f"✗ Error searching for asset: {e}")
        return

    # Step 5: Search issue for a specific asset and check
    print("\n" + "=" * 70)
    print("STEP 5: Search Issue for Asset and Check")
    print("=" * 70)

    try:
        # Use either project_id or catalog_id
        issue_id = issues_provider.get_issue_id(
            reported_for_id=dq_asset_id,
            check_id=dq_check_id,
            project_id=project_id  # Or use catalog_id=catalog_id
        )

        print(f"✓ Found Issue:")
        print(f"  Issue ID: {issue_id}")

    except ValueError as e:
        print(f"✗ Error searching for issue: {e}")
        return

    # Step 6: Update (patch) the issue by issue_id
    print("\n" + "=" * 70)
    print("STEP 6: Update Issue (Patch)")
    print("=" * 70)

    try:
        # Update both occurrences and tested records in a single call
        new_occurrences = 100
        new_tested_records = 5000
        print(f"\nUpdating occurrences to {new_occurrences} and tested records to {new_tested_records}...")
        update_result = issues_provider.update_issue_values(
            issue_id=issue_id,
            occurrences=new_occurrences,
            tested_records=new_tested_records,
            project_id=project_id,  # Or use catalog_id=catalog_id
            operation="replace"  # Use "replace" to set exact values, or "add" to increment
        )
        print(f"✓ Updated occurrences: {update_result.get('number_of_occurrences', 'N/A')}")
        print(f"✓ Updated tested records: {update_result.get('number_of_tested_records', 'N/A')}")

        # The percent_occurrences is typically calculated automatically by the system
        # based on number_of_occurrences and number_of_tested_records
        if 'percent_occurrences' in update_result:
            print(f"✓ Calculated percent occurrences: {update_result['percent_occurrences']}%")

    except ValueError as e:
        print(f"✗ Error updating issue: {e}")
        return

    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETED SUCCESSFULLY")
    print("=" * 70)


def example_with_add_operations():
    """
    Example showing how to add to existing values instead of replacing them.
    """
    config = ProviderConfig(
        url="https://cpd-ikc.apps.dqdev.ibm.com",
        auth_token="Bearer your-token-here"
    )

    issues_provider = IssuesProvider(config)
    issue_id = "b8f4252b-cd35-4668-9b35-4635bfc6e2e0"

    print("=" * 70)
    print("EXAMPLE: Add Operations")
    print("=" * 70)

    project_id = "your-project-id-here"

    try:
        # Add 10 more occurrences and 50 more tested records to the existing counts
        print("\nAdding 10 occurrences and 50 tested records to existing counts...")
        result = issues_provider.update_issue_values(
            issue_id=issue_id,
            occurrences=10,
            tested_records=50,
            project_id=project_id,  # Or use catalog_id=catalog_id
            operation="add"  # Use "add" to increment existing values
        )
        print(f"✓ New occurrences count: {result.get('number_of_occurrences', 'N/A')}")
        print(f"✓ New tested records count: {result.get('number_of_tested_records', 'N/A')}")

    except ValueError as e:
        print(f"✗ Error: {e}")



if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("DQ WORKFLOW EXAMPLE")
    print("=" * 70)
    print("\nThis example demonstrates the complete workflow:")
    print("1. Fetch CAMS asset by data_asset_id and project_id (or catalog_id)")
    print("2. Read the CAMS object to get check_id from column_info")
    print("3. Search for DQ checks by native_id")
    print("4. Search for DQ assets by native_id")
    print("5. Search issue for a specific asset and check")
    print("6. Update (patch) the issue by issue_id")
    print("\nNote: All methods support either project_id OR catalog_id (but not both)")
    print("\n" + "=" * 70 + "\n")

    # Run the main workflow
    main()

    # Uncomment to run additional examples:
    # print("\n\n")
    # example_with_add_operations()
    # print("\n\n")
    # example_ignore_issue()