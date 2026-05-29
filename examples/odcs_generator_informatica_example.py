#!/usr/bin/env python3
# coding: utf-8

# Copyright 2026 IBM Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Example usage of ODCS Generator to create ODCS YAML files from Informatica CDGC assets.

This example demonstrates:
1. Connecting to Informatica CDGC using credentials
2. Generating ODCS from an Informatica asset
3. Saving the ODCS to a YAML file
4. Using the generator programmatically
5. Batch processing multiple assets
"""

import os
import sys
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
from wxdi.odcs_generator.generate_odcs_from_informatica import (
    InformaticaClient,
    generate_odcs_yaml,
    write_yaml_file,
    extract_column_position
)


def example_basic_usage():
    """Basic example: Generate ODCS from an Informatica asset"""

    # Get credentials from environment variables
    cdgc_url = os.getenv('INFORMATICA_CDGC_URL')
    username = os.getenv('INFORMATICA_USERNAME')
    password = os.getenv('INFORMATICA_PASSWORD')

    if not all([cdgc_url, username, password]):
        print("Error: Please set INFORMATICA_CDGC_URL, INFORMATICA_USERNAME, and INFORMATICA_PASSWORD environment variables")
        print("\nExample:")
        print("  export INFORMATICA_CDGC_URL='https://cdgc.dm-us.informaticacloud.com'")
        print("  export INFORMATICA_USERNAME='your_username'")
        print("  export INFORMATICA_PASSWORD='your_pwd'")
        sys.exit(1)

    # Replace with your actual asset ID
    asset_id = "1b5fc805-252d-4ba2-bd90-e943103e411b"

    print(f"Connecting to Informatica CDGC at {cdgc_url}...")

    # Initialize Informatica client
    client = InformaticaClient(cdgc_url, username, password)

    print(f"Fetching asset details for {asset_id}...")

    # Fetch asset data
    asset_data = client.get_asset_details(asset_id)

    # Get column IDs from hierarchy
    column_ids = [col['core.identity'] for col in asset_data.get('hierarchy', [])]

    print(f"Found {len(column_ids)} columns. Fetching column details...")

    # Fetch column details concurrently
    column_details = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_col_id = {
            executor.submit(client.get_column_details, col_id): col_id
            for col_id in column_ids
        }

        for future in as_completed(future_to_col_id):
            try:
                col_data = future.result()
                column_details.append(col_data)
            except Exception as e:
                col_id = future_to_col_id[future]
                print(f"Warning: Failed to fetch column {col_id}: {e}")

    # Sort columns by position
    column_details.sort(key=extract_column_position)

    print("Generating ODCS YAML...")

    # Generate ODCS
    odcs_data = generate_odcs_yaml(asset_data, column_details, client.base_url)

    # Determine output filename
    asset_name = odcs_data.get('name', 'asset').lower().replace(' ', '-')
    output_file = f"{asset_name}-odcs.yaml"

    # Write to file
    write_yaml_file(output_file, odcs_data)

    print(f"✓ Successfully generated ODCS file: {output_file}")

    return odcs_data


def example_custom_processing():
    """Example: Generate ODCS with custom processing"""

    cdgc_url = os.getenv('INFORMATICA_CDGC_URL')
    username = os.getenv('INFORMATICA_USERNAME')
    password = os.getenv('INFORMATICA_PASSWORD')

    if not all([cdgc_url, username, password]):
        print("Error: Environment variables not set")
        sys.exit(1)

    asset_id = "1b5fc805-252d-4ba2-bd90-e943103e411b"

    print("Example: Custom ODCS Processing")
    print("=" * 50)

    # Initialize client
    client = InformaticaClient(cdgc_url, username, password)

    # Fetch data
    asset_data = client.get_asset_details(asset_id)
    column_ids = [col['core.identity'] for col in asset_data.get('hierarchy', [])]

    # Fetch columns
    column_details = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(client.get_column_details, col_id) for col_id in column_ids]
        for future in as_completed(futures):
            try:
                column_details.append(future.result())
            except Exception as e:
                print(f"Warning: {e}")

    column_details.sort(key=extract_column_position)

    # Generate base ODCS
    odcs_data = generate_odcs_yaml(asset_data, column_details, client.base_url)

    # Customize the ODCS
    print("\nCustomizing ODCS metadata...")

    # Update contract metadata
    odcs_data['domain'] = 'Finance'
    odcs_data['dataProduct'] = 'Customer Analytics'
    odcs_data['version'] = '2.0.0'
    odcs_data['name'] = 'Customer Transaction Contract'

    # Add quality rules
    odcs_data['quality'] = [
        {
            'type': 'completeness',
            'description': 'All required fields must be populated',
            'dimension': 'completeness',
            'weight': 'high'
        },
        {
            'type': 'uniqueness',
            'description': 'Primary key must be unique',
            'dimension': 'uniqueness',
            'weight': 'critical'
        }
    ]

    # Update server configuration with actual values
    if odcs_data.get('servers'):
        odcs_data['servers'][0]['server'] = 'prod.snowflake.acme.com'
        odcs_data['servers'][0]['database'] = 'ANALYTICS_DB'
        odcs_data['servers'][0]['account'] = 'acme_prod'

    # Add stakeholders
    odcs_data['stakeholders'] = [
        {
            'username': 'data.owner@acme.com',
            'role': 'Data Owner',
            'dateIn': '2024-01-01',
            'dateOut': None,
            'replaced': False
        },
        {
            'username': 'data.steward@acme.com',
            'role': 'Data Steward',
            'dateIn': '2024-01-01',
            'dateOut': None,
            'replaced': False
        }
    ]

    # Save customized ODCS
    output_file = "customized-customer-contract-odcs.yaml"
    write_yaml_file(output_file, odcs_data)

    print(f"✓ Customized ODCS saved to: {output_file}")

    return odcs_data


def example_batch_processing():
    """Example: Process multiple assets in batch"""

    cdgc_url = os.getenv('INFORMATICA_CDGC_URL')
    username = os.getenv('INFORMATICA_USERNAME')
    password = os.getenv('INFORMATICA_PASSWORD')

    if not all([cdgc_url, username, password]):
        print("Error: Environment variables not set")
        sys.exit(1)

    # List of asset IDs to process
    asset_ids = [
        "1b5fc805-252d-4ba2-bd90-e943103e411b",
        "2c6gd916-363e-5cb1-af01-5gb3dfb2291c",
        "3d7he027-474f-6dc2-bg12-6hc4egc3302d"
    ]

    print("Example: Batch Processing Multiple Assets")
    print("=" * 50)

    # Initialize client
    client = InformaticaClient(cdgc_url, username, password)

    results = {
        'success': [],
        'failed': []
    }

    for i, asset_id in enumerate(asset_ids, 1):
        print(f"\nProcessing asset {i}/{len(asset_ids)}: {asset_id}")

        try:
            # Fetch asset data
            asset_data = client.get_asset_details(asset_id)
            column_ids = [col['core.identity'] for col in asset_data.get('hierarchy', [])]

            # Fetch columns
            column_details = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(client.get_column_details, col_id) for col_id in column_ids]
                for future in as_completed(futures):
                    try:
                        column_details.append(future.result())
                    except Exception:
                        pass

            column_details.sort(key=extract_column_position)

            # Generate ODCS
            odcs_data = generate_odcs_yaml(asset_data, column_details, client.base_url)

            # Save to file
            asset_name = odcs_data.get('name', f'asset-{i}').lower().replace(' ', '-')
            output_file = f"batch-{asset_name}-odcs.yaml"
            write_yaml_file(output_file, odcs_data)

            results['success'].append({
                'asset_id': asset_id,
                'output_file': output_file
            })

            print(f"  ✓ Success: {output_file}")

        except Exception as e:
            results['failed'].append({
                'asset_id': asset_id,
                'error': str(e)
            })
            print(f"  ✗ Failed: {e}")

    # Print summary
    print("\n" + "=" * 50)
    print("Batch Processing Summary")
    print("=" * 50)
    print(f"Total assets: {len(asset_ids)}")
    print(f"Successful: {len(results['success'])}")
    print(f"Failed: {len(results['failed'])}")

    if results['failed']:
        print("\nFailed assets:")
        for item in results['failed']:
            print(f"  - {item['asset_id']}: {item['error']}")

    return results


def example_programmatic_usage():
    """Example: Using the module programmatically in your code"""

    print("Example: Programmatic Usage")
    print("=" * 50)

    # Configuration
    config = {
        'cdgc_url': os.getenv('INFORMATICA_CDGC_URL'),
        'username': os.getenv('INFORMATICA_USERNAME'),
        'password': os.getenv('INFORMATICA_PASSWORD'),
        'asset_id': '1b5fc805-252d-4ba2-bd90-e943103e411b'
    }

    if not all([config['cdgc_url'], config['username'], config['password']]):
        print("Error: Environment variables not set")
        return None

    try:
        # Step 1: Initialize client
        print("Step 1: Initializing Informatica client...")
        client = InformaticaClient(
            config['cdgc_url'],
            config['username'],
            config['password']
        )

        # Step 2: Fetch asset metadata
        print("Step 2: Fetching asset metadata...")
        asset_data = client.get_asset_details(config['asset_id'])
        table_name = asset_data['summary']['core.name']
        print(f"  Found table: {table_name}")

        # Step 3: Fetch column metadata
        print("Step 3: Fetching column metadata...")
        column_ids = [col['core.identity'] for col in asset_data.get('hierarchy', [])]
        print(f"  Found {len(column_ids)} columns")

        column_details = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(client.get_column_details, col_id) for col_id in column_ids]
            for future in as_completed(futures):
                try:
                    column_details.append(future.result())
                except Exception as e:
                    print(f"  Warning: {e}")

        column_details.sort(key=extract_column_position)

        # Step 4: Generate ODCS
        print("Step 4: Generating ODCS...")
        odcs_data = generate_odcs_yaml(asset_data, column_details, client.base_url)

        # Step 5: Process or save ODCS
        print("Step 5: Saving ODCS...")
        output_file = f"{table_name.lower()}-programmatic-odcs.yaml"
        write_yaml_file(output_file, odcs_data)

        print(f"\n✓ ODCS generated successfully: {output_file}")

        # You can now use odcs_data in your application
        print(f"\nODCS Summary:")
        print(f"  - Contract ID: {odcs_data['id']}")
        print(f"  - Table: {odcs_data['schema'][0]['name']}")
        print(f"  - Columns: {len(odcs_data['schema'][0]['properties'])}")
        print(f"  - Server Type: {odcs_data['servers'][0]['type']}")

        return odcs_data

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


def main():
    """Run all examples"""

    print("\n" + "=" * 70)
    print("INFORMATICA ODCS GENERATOR - EXAMPLES")
    print("=" * 70)

    examples = [
        ("Basic Usage", example_basic_usage),
        ("Custom Processing", example_custom_processing),
        ("Batch Processing", example_batch_processing),
        ("Programmatic Usage", example_programmatic_usage)
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nTo run a specific example, uncomment the corresponding line below:")
    print("Or run all examples by uncommenting the loop.\n")

    # Uncomment to run specific examples:
    # example_basic_usage()
    # example_custom_processing()
    # example_batch_processing()
    # example_programmatic_usage()

    # Uncomment to run all examples:
    # for name, example_func in examples:
    #     print(f"\n{'=' * 70}")
    #     print(f"Running: {name}")
    #     print('=' * 70)
    #     try:
    #         example_func()
    #     except Exception as e:
    #         print(f"Error in {name}: {e}")
    #     print()

    print("\nNote: Make sure to set the following environment variables:")
    print("  - INFORMATICA_CDGC_URL")
    print("  - INFORMATICA_USERNAME")
    print("  - INFORMATICA_PASSWORD")
    print("\nAnd update the asset IDs in the examples with your actual asset IDs.")


if __name__ == '__main__':
    main()

