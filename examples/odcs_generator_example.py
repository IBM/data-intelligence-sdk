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
Example usage of ODCS Generator to create ODCS YAML files from Collibra assets.

This example demonstrates:
1. Connecting to Collibra using credentials
2. Generating ODCS from a Collibra asset
3. Saving the ODCS to a YAML file
4. Using the generator programmatically
"""

import os
import sys
import yaml
from wxdi.odcs_generator import CollibraClient, ODCSGenerator


def example_basic_usage():
    """Basic example: Generate ODCS from a Collibra asset"""

    # Get credentials from environment variables
    collibra_url = os.getenv('COLLIBRA_URL')
    username = os.getenv('COLLIBRA_USERNAME')
    password = os.getenv('COLLIBRA_PASSWORD')

    if not all([collibra_url, username, password]):
        print("Error: Please set COLLIBRA_URL, COLLIBRA_USERNAME, and COLLIBRA_PASSWORD environment variables")
        sys.exit(1)

    # Replace with your actual asset ID
    asset_id = "019a57f9-62d2-7aa0-9f22-4fa2cea1180b"

    print(f"Connecting to Collibra at {collibra_url}...")

    # Initialize Collibra client
    client = CollibraClient(
        base_url=collibra_url,
        username=username,
        password=password
    )

    # Create ODCS generator
    generator = ODCSGenerator(client)

    print(f"Generating ODCS for asset: {asset_id}")

    # Generate ODCS from asset
    odcs_data = generator.generate_odcs(asset_id)

    # Save to YAML file
    output_file = f"{odcs_data.get('name', 'asset').lower().replace(' ', '-')}-odcs.yaml"

    print(f"Writing ODCS to {output_file}...")
    with open(output_file, 'w') as f:
        yaml.dump(odcs_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"✓ Successfully generated ODCS file: {output_file}")

    return odcs_data


def example_custom_processing():
    """Advanced example: Generate ODCS and perform custom processing"""

    # Get credentials from environment variables
    collibra_url = os.getenv('COLLIBRA_URL')
    username = os.getenv('COLLIBRA_USERNAME')
    password = os.getenv('COLLIBRA_PASSWORD')

    if not all([collibra_url, username, password]):
        print("Error: Please set COLLIBRA_URL, COLLIBRA_USERNAME, and COLLIBRA_PASSWORD environment variables")
        sys.exit(1)

    # Replace with your actual asset ID
    asset_id = "019a57f9-62d2-7aa0-9f22-4fa2cea1180b"

    # Initialize client and generator
    client = CollibraClient(base_url=collibra_url, username=username, password=password)
    generator = ODCSGenerator(client)

    # Generate ODCS
    odcs_data = generator.generate_odcs(asset_id)

    # Custom processing: Update contract metadata
    odcs_data['dataProduct'] = 'My Custom Data Product'
    odcs_data['version'] = '2.0.0'
    odcs_data['name'] = 'Custom Contract Name'

    # Custom processing: Add quality rules
    if 'schema' in odcs_data and len(odcs_data['schema']) > 0:
        schema = odcs_data['schema'][0]
        schema['quality'] = [
            {
                'type': 'completeness',
                'dimension': 'completeness',
                'mustBe': 100,
                'mustNotBe': None
            }
        ]

    # Custom processing: Update server configuration
    if 'servers' in odcs_data and len(odcs_data['servers']) > 0:
        server = odcs_data['servers'][0]
        server['server'] = 'prod.snowflake.mycompany.com'
        server['type'] = 'snowflake'
        server['account'] = 'my_account'
        server['database'] = 'my_database'
        server['schema'] = 'my_schema'

    # Save customized ODCS
    output_file = 'custom-odcs.yaml'
    with open(output_file, 'w') as f:
        yaml.dump(odcs_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"✓ Successfully generated customized ODCS file: {output_file}")

    return odcs_data


def example_batch_processing():
    """Example: Generate ODCS for multiple assets"""

    # Get credentials from environment variables
    collibra_url = os.getenv('COLLIBRA_URL')
    username = os.getenv('COLLIBRA_USERNAME')
    password = os.getenv('COLLIBRA_PASSWORD')

    if not all([collibra_url, username, password]):
        print("Error: Please set COLLIBRA_URL, COLLIBRA_USERNAME, and COLLIBRA_PASSWORD environment variables")
        sys.exit(1)

    # List of asset IDs to process
    asset_ids = [
        "019a57f9-62d2-7aa0-9f22-4fa2cea1180b",
        # Add more asset IDs here
    ]

    # Initialize client and generator once
    client = CollibraClient(base_url=collibra_url, username=username, password=password)
    generator = ODCSGenerator(client)

    results = []

    for asset_id in asset_ids:
        try:
            print(f"\nProcessing asset: {asset_id}")
            odcs_data = generator.generate_odcs(asset_id)

            # Save to file
            output_file = f"{odcs_data.get('name', asset_id).lower().replace(' ', '-')}-odcs.yaml"
            with open(output_file, 'w') as f:
                yaml.dump(odcs_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

            results.append({'asset_id': asset_id, 'status': 'success', 'file': output_file})
            print(f"✓ Generated: {output_file}")

        except Exception as e:
            results.append({'asset_id': asset_id, 'status': 'failed', 'error': str(e)})
            print(f"✗ Failed: {str(e)}")

    # Print summary
    print("\n=== Batch Processing Summary ===")
    success_count = sum(1 for r in results if r['status'] == 'success')
    failed_count = sum(1 for r in results if r['status'] == 'failed')
    print(f"Total: {len(results)}, Success: {success_count}, Failed: {failed_count}")

    return results


if __name__ == '__main__':
    print("=== ODCS Generator Examples ===\n")

    # Run basic example
    print("1. Basic Usage Example")
    print("-" * 50)
    try:
        example_basic_usage()
    except Exception as e:
        print(f"Error: {str(e)}")

    print("\n" + "=" * 50 + "\n")

    # Uncomment to run other examples:

    # print("2. Custom Processing Example")
    # print("-" * 50)
    # try:
    #     example_custom_processing()
    # except Exception as e:
    #     print(f"Error: {str(e)}")

    # print("\n" + "=" * 50 + "\n")

    # print("3. Batch Processing Example")
    # print("-" * 50)
    # try:
    #     example_batch_processing()
    # except Exception as e:
    #     print(f"Error: {str(e)}")

# Made with Bob
