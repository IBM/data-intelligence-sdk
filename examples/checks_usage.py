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
Example usage of ChecksProvider for managing data quality checks.

This example demonstrates the ChecksProvider operations:

create_check(): Create a new data quality check
   - Requires: name, dimension_id, native_id, and either project_id OR catalog_id
   - Optional: check_type (defaults to the check name if not provided)
   - Returns: The check ID (string)

get_checks(): Retrieve checks for a specific asset filtered by check type
   - Requires: dq_asset_id, check_type, and either project_id OR catalog_id
   - Optional: include_children (defaults to True)
   - Returns: List of check objects matching the criteria

Either project_id or catalog_id must be provided (but not both).
"""

from wxdi.dq_validator.provider import ProviderConfig, ChecksProvider


def main():
    """Main function demonstrating CheckProvider usage."""

    print("=" * 70)
    print("CheckProvider - Usage Examples")
    print("=" * 70)

    # Step 1: Configure the provider with your instance URL and authentication token
    config = ProviderConfig(
        url="https://your-instance.com",
        auth_token="Bearer your-auth-token-here"
    )

    print("\nConfiguration:")
    print(f"  URL: {config.url}")
    print(f"  Auth Token: {config.auth_token[:50]}...")

    # Step 2: Create a ChecksProvider instance
    check_provider = ChecksProvider(config)
    print("\n✓ ChecksProvider initialized")

    # Define IDs that will be used throughout the examples
    project_id = "your-project-id-here"
    catalog_id = "your-catalog-id-here"  # Alternative to project_id

    # =========================================================================
    # Example 1: Create a new check without specifying check_type (using project_id)
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 1: Create Check without check_type (defaults to name)")
    print("=" * 70)

    try:
        # Note: Update these values with your actual data
        # When check_type is not provided, it defaults to the check name
        check_id = check_provider.create_check(
            name="uniqueness_check",
            dimension_id="371114cd-5516-4691-8b2e-1e66edf66486",  # Use appropriate dimension ID
            native_id="your-asset-id/your-check-id-1",  # Format: <asset_id>/<check_id>
            project_id=project_id
            # check_type not specified - will default to "uniqueness_check"
        )
        print(f"\n✓ Successfully created check")
        print(f"  New Check ID: {check_id}")

    except ValueError as e:
        print(f"\n✗ Error creating check: {e}")

    # =========================================================================
    # Example 2: Create a comparison check with parent_check_id (using project_id)
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 2: Create a Comparison Check with parent_check_id (using project_id)")
    print("=" * 70)

    try:
        # First, let's assume we have a parent check ID from Example 1
        parent_check_id = "848aaddc-7401-4a43-ad2b-96a0946d4674"  # Replace with actual parent ID

        check_id = check_provider.create_check(
            name="Example Comparison Check",
            dimension_id="ec453723-669c-48bb-82c1-11b69b3b8c93",  # Validity dimension
            native_id="your-asset-id/your-check-id-2",
            check_type="comparison",
            project_id=project_id,
            parent_check_id=parent_check_id  # Optional: Link to parent check
        )
        print(f"\n✓ Successfully created comparison check with parent")
        print(f"  New Check ID: {check_id}")
        print(f"  Parent Check ID: {parent_check_id}")

    except ValueError as e:
        print(f"\n✗ Error creating check: {e}")

    # =========================================================================
    # Example 3: Create a check using catalog_id instead of project_id
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 3: Create Check using catalog_id")
    print("=" * 70)

    try:
        check_id = check_provider.create_check(
            name="Catalog Check Example",
            dimension_id="371114cd-5516-4691-8b2e-1e66edf66486",
            native_id="catalog-asset-id/catalog-check-id",
            check_type="data_rule",
            catalog_id=catalog_id
        )
        print(f"\n✓ Successfully created check using catalog_id")
        print(f"  New Check ID: {check_id}")

    except ValueError as e:
        print(f"\n✗ Error creating check: {e}")

    # =========================================================================
    # Example 4: Create multiple checks with different types
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 4: Create Multiple Checks with Different Types")
    print("=" * 70)

    check_configs = [
        {
            "name": "Uniqueness Check",
            "dimension_id": "371114cd-5516-4691-8b2e-1e66edf66486",
            "native_id": "asset-1/uniqueness-check",
            "check_type": "data_rule"
        },
        {
            "name": "Completeness Check",
            "dimension_id": "ec453723-669c-48bb-82c1-11b69b3b8c93",
            "native_id": "asset-1/completeness-check",
            "check_type": "data_rule",
            "parent_check_id": "parent-check-id-123"  # Optional: Add parent for hierarchical checks
        },
        {
            "name": "Format Validation Check",
            "dimension_id": "371114cd-5516-4691-8b2e-1e66edf66486",
            "native_id": "asset-1/format-check",
            "check_type": "comparison",
            "parent_check_id": "parent-check-id-456"  # Optional: Add parent for hierarchical checks
        }
    ]

    created_checks = []
    for config in check_configs:
        try:
            # Get parent_check_id if it exists in config, otherwise None
            parent_check_id = config.get("parent_check_id")

            check_id = check_provider.create_check(
                name=config["name"],
                dimension_id=config["dimension_id"],
                native_id=config["native_id"],
                check_type=config["check_type"],
                project_id=project_id,
                parent_check_id=parent_check_id
            )
            created_checks.append({
                "id": check_id,
                "name": config["name"],
                "type": config["check_type"]
            })
            print(f"\n✓ Created: {config['name']}")
            print(f"  ID: {check_id}")
            print(f"  Type: {config['check_type']}")
        except ValueError as e:
            print(f"\n✗ Error creating {config['name']}: {e}")

    print(f"\n\nSummary: Successfully created {len(created_checks)} checks")

    # =========================================================================
    # Example 5: Error handling - Missing required parameters
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 5: Error Handling - Missing project_id and catalog_id")
    print("=" * 70)

    try:
        # This should fail because neither project_id nor catalog_id is provided
        check_provider.create_check(
            name="Invalid Check",
            dimension_id="371114cd-5516-4691-8b2e-1e66edf66486",
            native_id="asset/check"
            # Missing both project_id and catalog_id
        )
    except ValueError as e:
        print(f"\n✓ Expected error caught: {e}")

    # =========================================================================
    # Example 6: Error handling - Both project_id and catalog_id provided
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 6: Error Handling - Both project_id and catalog_id provided")
    print("=" * 70)

    try:
        # This should fail because both project_id and catalog_id are provided
        check_provider.create_check(
            name="Invalid Check",
            dimension_id="371114cd-5516-4691-8b2e-1e66edf66486",
            native_id="asset/check",
            project_id=project_id,
            catalog_id=catalog_id  # Both provided - should fail
        )
    except ValueError as e:
        print(f"\n✓ Expected error caught: {e}")

    # =========================================================================
    # Example 7: Get checks for a specific asset filtered by check type
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 7: Get Checks for an Asset (filtered by check_type)")
    print("=" * 70)

    try:
        # Retrieve all checks for a specific column asset filtered by check type
        column_asset_id = "your-column-asset-id-here"
        check_type = "case"  # e.g., "case", "completeness", "comparison", etc.

        checks = check_provider.get_checks(
            dq_asset_id=column_asset_id,
            check_type=check_type,
            project_id=project_id
        )

        print(f"\n✓ Successfully retrieved checks")
        print(f"  Asset ID: {column_asset_id}")
        print(f"  Check Type Filter: {check_type}")
        print(f"  Number of checks found: {len(checks)}")

        # Display details of each check
        for i, check in enumerate(checks, 1):
            print(f"\n  Check {i}:")
            print(f"    ID: {check.get('id')}")
            print(f"    Name: {check.get('name')}")
            print(f"    Type: {check.get('type')}")
            print(f"    Native ID: {check.get('native_id')}")

    except ValueError as e:
        print(f"\n✗ Error retrieving checks: {e}")

    # =========================================================================
    # Example 8: Get checks with include_children parameter
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 8: Get Checks with include_children=False")
    print("=" * 70)

    try:
        checks = check_provider.get_checks(
            dq_asset_id="your-asset-id",
            check_type="completeness",
            project_id=project_id,
            include_children=False  # Don't include child checks
        )

        print(f"\n✓ Successfully retrieved checks (without children)")
        print(f"  Number of checks found: {len(checks)}")

    except ValueError as e:
        print(f"\n✗ Error retrieving checks: {e}")

    print("\n" + "=" * 70)
    print("Examples Complete!")
    print("=" * 70)
    print("\nKey Points:")
    print("  • create_check() creates a new data quality check and returns the check ID")
    print("  • get_checks() retrieves checks for an asset filtered by type")
    print("  • Either project_id OR catalog_id must be provided (not both)")
    print("  • check_type defaults to the check name if not specified in create_check()")
    print("  • native_id format: <asset_id>/<check_id>")
    print("  • get_checks() returns a list of check objects")
    print("  • Extract check ID from returned dict using check_body.get('id') for each check in the list of retrieved checks")


if __name__ == "__main__":
    main()