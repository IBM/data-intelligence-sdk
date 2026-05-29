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
Example usage of AssetProvider for managing data quality assets.

This example demonstrates:

get_assets(): Retrieve data quality assets
   - Requires: Either project_id OR catalog_id (but not both)
   - Optional: start, limit, include_children, asset_type
   - Returns: Dictionary containing assets data
   - Common asset_types: "data_asset", "column"
"""

from wxdi.dq_validator.provider import ProviderConfig
from wxdi.dq_validator.provider.assets import DQAssetsProvider
import json


def main():
    """Main function demonstrating AssetProvider usage."""

    print("=" * 70)
    print("AssetProvider - Usage Examples")
    print("=" * 70)

    # Step 1: Configure the provider with your instance URL and authentication token
    config = ProviderConfig(
        url="https://your-instance.cloud.ibm.com",
        auth_token="Bearer your-auth-token-here"
    )

    print("\nConfiguration:")
    print(f"  URL: {config.url}")
    print(f"  Auth Token: {config.auth_token[:50]}...")

    # Step 2: Create a DQAssetsProvider instance
    asset_provider = DQAssetsProvider(config)
    print("\n✓ DQAssetsProvider initialized")

    # Define IDs that will be used throughout the examples
    project_id = "your-project-id-here"  # Replace with your actual project ID
    catalog_id = "your-catalog-id-here"  # Alternative to project_id

    # =========================================================================
    # Example 1: Get data assets with children (using project_id)
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 1: Get Data Assets with Children (using project_id)")
    print("=" * 70)

    try:
        print(f"\nParameters:")
        print(f"  project_id: {project_id}")
        print(f"  include_children: True")
        print(f"  asset_type: data_asset")

        assets_response = asset_provider.get_assets(
            project_id=project_id,
            include_children=True,
            asset_type="data_asset",
            limit=5
        )

        print(f"\n✓ Successfully retrieved data assets")

        assets = assets_response.get("assets", [])
        total_count = assets_response.get("total_count", 0)

        print(f"\nSummary:")
        print(f"  Total Count: {total_count}")
        print(f"  Assets Returned: {len(assets)}")

        if assets:
            asset = assets[0]
            print(f"\nFirst asset:")
            print(f"  ID: {asset.get('id')}")
            print(f"  Name: {asset.get('name', 'N/A')}")
            print(f"  Type: {asset.get('type', 'N/A')}")
            children = asset.get('children', [])
            print(f"  Children Count: {len(children)}")

    except ValueError as e:
        print(f"\n✗ Error: {e}")

    # =========================================================================
    # Example 2: Get column assets without children (using project_id)
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 2: Get Column Assets without Children (using project_id)")
    print("=" * 70)

    try:
        print(f"\nParameters:")
        print(f"  project_id: {project_id}")
        print(f"  include_children: False")
        print(f"  asset_type: column")

        assets_response = asset_provider.get_assets(
            project_id=project_id,
            include_children=False,
            asset_type="column",
            limit=5
        )

        print(f"\n✓ Successfully retrieved column assets")

        assets = assets_response.get("assets", [])
        print(f"\nAssets Returned: {len(assets)}")

        if assets:
            print(f"\nFirst 2 columns:")
            for idx, asset in enumerate(assets[:2], 1):
                print(f"  {idx}. {asset.get('name', 'N/A')} (ID: {asset.get('id')})")

    except ValueError as e:
        print(f"\n✗ Error: {e}")

    # =========================================================================
    # Example 3: Get data assets using catalog_id
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 3: Get Data Assets using catalog_id")
    print("=" * 70)

    try:
        print(f"\nParameters:")
        print(f"  catalog_id: {catalog_id}")
        print(f"  include_children: True")
        print(f"  asset_type: data_asset")

        assets_response = asset_provider.get_assets(
            catalog_id=catalog_id,
            include_children=True,
            asset_type="data_asset",
            limit=5
        )

        print(f"\n✓ Successfully retrieved data assets using catalog_id")

        assets = assets_response.get("assets", [])
        total_count = assets_response.get("total_count", 0)

        print(f"\nSummary:")
        print(f"  Total Count: {total_count}")
        print(f"  Assets Returned: {len(assets)}")

        if assets:
            asset = assets[0]
            print(f"\nFirst asset:")
            print(f"  ID: {asset.get('id')}")
            print(f"  Name: {asset.get('name', 'N/A')}")
            children = asset.get('children', [])
            print(f"  Children Count: {len(children)}")

    except ValueError as e:
        print(f"\n✗ Error: {e}")

    # =========================================================================
    # Example 4: Get column assets using catalog_id
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 4: Get Column Assets using catalog_id")
    print("=" * 70)

    try:
        print(f"\nParameters:")
        print(f"  catalog_id: {catalog_id}")
        print(f"  asset_type: column")

        assets_response = asset_provider.get_assets(
            catalog_id=catalog_id,
            asset_type="column",
            limit=5
        )

        print(f"\n✓ Successfully retrieved column assets using catalog_id")

        assets = assets_response.get("assets", [])
        print(f"\nAssets Returned: {len(assets)}")

        if assets:
            print(f"\nFirst 2 columns:")
            for idx, asset in enumerate(assets[:2], 1):
                print(f"  {idx}. {asset.get('name', 'N/A')} (ID: {asset.get('id')})")

    except ValueError as e:
        print(f"\n✗ Error: {e}")

    print("\n" + "=" * 70)
    print("Examples Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()