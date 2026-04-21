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
Generate ODCS YAML file from Informatica Asset

This script fetches asset metadata from Informatica and generates an ODCS v3 compliant YAML file.

Usage:
    python odcs_generator/generate_odcs_from_informatica.py <asset_id>
    python odcs_generator/generate_odcs_from_informatica.py 1b5fc805-252d-4ba2-bd90-e943103e411b --cdgc-url https://cdgc.dm-us.informaticacloud.com -u username -p password

Environment Variables:
    INFORMATICA_CDGC_URL: Informatica CDGC URL (required, e.g., https://cdgc.dm-us.informaticacloud.com)
    INFORMATICA_USERNAME: Informatica username (required)
    INFORMATICA_PASSWORD: Informatica password (required)
"""

import argparse
import os
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import yaml

# Constants
CORE_NAME_ATTR = 'core.name'

# Resource type mapping from Informatica to ODCS
RESOURCE_TYPE_MAPPING = {
    'SqlServer': 'sqlserver',
    'Oracle': 'oracle',
    'PostgreSQL': 'postgresql',
    'MySQL': 'mysql',
    'Snowflake': 'snowflake',
    'Redshift': 'redshift',
    'BigQuery': 'bigquery',
    'Databricks': 'databricks',
    'Synapse': 'synapse',
    'DB2': 'db2',
    'Teradata': 'custom',
    'Hive': 'hive',
    'Impala': 'impala'
}

# System attributes mapping for custom properties
SYSTEM_ATTRIBUTES_MAPPING = {
    'core.resourceName': 'Catalog Source Name',
    'com.infa.odin.models.relational.NumberOfRows': 'Number of rows',
    'core.origin': 'Origin',
    'com.infa.odin.models.relational.Owner': 'Schema',
    'core.sourceCreatedBy': 'Source Created By',
    'core.sourceCreatedOn': 'Source Created On',
    'core.sourceModifiedBy': 'Source Modified By',
    'core.sourceModifiedOn': 'Source Modified On'
}

class InformaticaClient:

    CONTENT_TYPE_JSON = "application/json"
    HEADERS_JSON = {"Accept": CONTENT_TYPE_JSON}
    HEADERS_CONTENT_JSON = {"Content-Type": CONTENT_TYPE_JSON}

    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.region = self._extract_region_from_url(base_url)
        self.identity_url = f"https://{self.region}.informaticacloud.com"
        self._auth_token: Optional[str] = None

    def _extract_region_from_url(self, base_url: str) -> str:
        """Extract region identifier from base URL.

        Examples:
            https://cdgc.dm-us.informaticacloud.com -> dm-us
            https://cdgc.na1.informaticacloud.com -> na1
        """
        # Remove protocol and trailing slash
        url = base_url.replace('https://', '').rstrip('/')

        # Extract hostname
        hostname = url.split('/')[0]

        # Remove 'cdgc.' prefix if present
        if hostname.startswith('cdgc.'):
            hostname = hostname[5:]

        # Extract region (everything before .informaticacloud.com)
        if '.informaticacloud.com' in hostname:
            region = hostname.split('.informaticacloud.com')[0]
            return region

        # Fallback: return the hostname as-is
        return hostname

    def get_session_id(self) -> Dict[str, Any]:
        url = f"{self.identity_url}/identity-service/api/v1/Login"
        payload = {"username": self.username, "password": self.password}
        response = requests.post(url, json=payload, headers=self.HEADERS_CONTENT_JSON)
        response.raise_for_status()
        return response.json()

    def get_auth_token(self) -> str:
        """Get authentication token with caching to avoid repeated auth calls."""
        if self._auth_token is None:
            session_id = self.get_session_id()["sessionId"]
            url = f"{self.identity_url}/identity-service/api/v1/jwt/Token?client_id=idmc_api&nonce=1234"
            response = requests.post(url, headers={"Accept": self.CONTENT_TYPE_JSON, "IDS-SESSION-ID": session_id, "Cookie": f"USER_SESSION={session_id}"})
            response.raise_for_status()
            self._auth_token = response.json()["jwt_token"]
        return str(self._auth_token)

    def _fetch_asset(self, asset_id: str) -> Dict[str, Any]:
        """Fetch asset data from Informatica API."""
        auth_token = self.get_auth_token()
        url = f"{self.base_url}/data360/search/v1/assets/{asset_id}?scheme=internal&segments=all"
        response = requests.get(url, headers={"Authorization": f"Bearer {auth_token}"})
        response.raise_for_status()
        return response.json()

    def get_asset_details(self, asset_id: str) -> Dict[str, Any]:
        """Fetch asset details including table and column information."""
        return self._fetch_asset(asset_id)

    def validate_asset_is_table(self, asset_data: Dict[str, Any]) -> None:
        """Validate that the asset is a table and not a schema or other type.

        Args:
            asset_data: The asset data returned from Informatica API

        Raises:
            ValueError: If the asset is not a table
        """
        # Check the asset class type from systemAttributes (correct location)
        asset_class = asset_data.get('systemAttributes', {}).get('core.classType', '')

        # Valid table class types in Informatica
        valid_table_types = [
            'com.infa.odin.models.relational.Table',
            'com.infa.odin.models.relational.View'
        ]

        if asset_class not in valid_table_types:
            asset_name = asset_data.get('summary', {}).get(CORE_NAME_ATTR, 'unknown')
            raise ValueError(
                f"Asset '{asset_name}' is not a type 'Table'. "
                f"This script only processes table assets. Please provide a table asset ID."
            )

    def get_column_details(self, column_id: str) -> Dict[str, Any]:
        """Fetch detailed information for a specific column."""
        return self._fetch_asset(column_id)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Generate ODCS YAML file from Informatica asset',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="")

    parser.add_argument('asset_id', help='Informatica asset ID')
    parser.add_argument('-o', '--output', help='Output YAML file path (default: <asset_name>-odcs.yaml)')
    parser.add_argument('--cdgc-url', help='Informatica CDGC URL (e.g., https://cdgc.dm-us.informaticacloud.com)',
                        default=os.getenv('INFORMATICA_CDGC_URL'))
    parser.add_argument('-u', '--username', help='Informatica username', default=os.getenv('INFORMATICA_USERNAME'))
    parser.add_argument('-p', '--password', help='Informatica password', default=os.getenv('INFORMATICA_PASSWORD'))
    return parser.parse_args()

def validate_arguments(args):
    if not args.cdgc_url:
        print("Error: Informatica CDGC URL is required. Set INFORMATICA_CDGC_URL environment variable or use --cdgc-url")
        print("Example: --cdgc-url https://cdgc.dm-us.informaticacloud.com")
        sys.exit(1)

    if not args.username:
        print("Error: Informatica username is required. Set INFORMATICA_USERNAME environment variable or use --username")
        sys.exit(1)

    if not args.password:
        print("Error: Informatica password is required. Set INFORMATICA_PASSWORD environment variable or use --password")
        sys.exit(1)

def extract_column_position(col_data: Dict[str, Any]) -> int:
    """Extract column position from column data."""
    self_attrs = col_data.get('selfAttributes', {})
    position = self_attrs.get('core.Position')

    try:
        return int(position) if position is not None else 999999
    except (ValueError, TypeError):
        return 999999


def build_physical_type(datatype: str, datatype_length: str, datatype_scale: str) -> str:
    """Build physical type string with length/scale if available."""
    physical_type = datatype
    if datatype_length:
        if datatype_scale and datatype_scale != '0':
            physical_type = f"{datatype}({datatype_length},{datatype_scale})"
        else:
            physical_type = f"{datatype}({datatype_length})"
    return physical_type


def build_column_property(column_detail: Dict[str, Any]) -> Dict[str, Any]:
    """Build a single column property from column detail data."""
    col_summary = column_detail.get('summary', {})
    col_self_attrs = column_detail.get('selfAttributes', {})

    col_name = col_summary.get(CORE_NAME_ATTR)
    datatype = col_self_attrs.get('com.infa.odin.models.relational.Datatype')
    datatype_length = col_self_attrs.get('com.infa.odin.models.relational.DatatypeLength', '')
    datatype_scale = col_self_attrs.get('com.infa.odin.models.relational.DatatypeScale', '')

    physical_type = build_physical_type(datatype, datatype_length, datatype_scale)
    col_description = col_summary.get('core.description', '')

    prop = {
        'name': col_name,
        'physicalType': physical_type,
    }

    if col_description:
        prop['description'] = col_description

    # Check if column is nullable
    nullable_str = col_self_attrs.get('com.infa.odin.models.relational.Nullable', 'true')
    is_nullable = nullable_str.lower() == 'true'
    prop['required'] = not is_nullable

    # Check if column is primary key
    pk_str = col_self_attrs.get('com.infa.odin.models.relational.PrimaryKeyColumn', 'false')
    is_primary_key = pk_str.lower() == 'true'
    if is_primary_key:
        prop['primaryKey'] = True

    return prop


def build_custom_properties(table_self_attrs: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build custom properties list from table attributes."""
    custom_properties = []

    for key, ui_field_name in SYSTEM_ATTRIBUTES_MAPPING.items():
        value = table_self_attrs.get(key)
        if value:
            custom_properties.append({
                'property': ui_field_name,
                'value': value
            })

    return custom_properties


def generate_odcs_yaml(asset_data: Dict[str, Any], column_details: List[Dict[str, Any]], base_url: str) -> Dict[str, Any]:
    """Generate ODCS YAML structure from Informatica asset data."""

    # Extract table information
    table_id = asset_data['core.identity']
    name = asset_data['summary'][CORE_NAME_ATTR]

    # Extract actual table name from selfAttributes (physical table name)
    table_self_attrs = asset_data.get('selfAttributes', {})
    table_name = table_self_attrs.get(CORE_NAME_ATTR, name)

    # Extract schema name for physical name construction
    schema_name = table_self_attrs.get('com.infa.odin.models.relational.Owner', '')

    # Build physical name as schema/table_name
    physical_name = f"{schema_name}/{table_name}" if schema_name else table_name

    created_ts = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    # Extract table description if available
    table_description = asset_data.get('summary', {}).get('core.description')

    # Extract resource information for server configuration
    resource_type = table_self_attrs.get('core.resourceType', '')

    # Build custom properties using helper function
    custom_properties = build_custom_properties(table_self_attrs)

    # Map resource type to ODCS server type
    server_type = RESOURCE_TYPE_MAPPING.get(resource_type)

    # Build properties from column details using helper function
    properties = [build_column_property(column_detail) for column_detail in column_details]

    # Build schema entry
    schema_entry = {
        'id': table_id,
        'name': table_name,
        'physicalName': physical_name,
        'physicalType': 'Table',
        'properties': properties
    }

    if table_description:
        schema_entry['description'] = table_description

    # Build ODCS structure
    odcs = {
        'id': table_id,
        'kind': 'DataContract',
        'apiVersion': 'v3.1.0',
        'domain': 'Sample Domain',
        'dataProduct': 'Sample data product',
        'version': '1.0.0',
        'name': 'Sample contract',
        'status': 'active',
        'contractCreatedTs': created_ts,
        'description': {
            'authoritativeDefinitions': [
                {
                    'type': 'informatica-asset',
                    'url': f"{base_url}/asset/{table_id}"
                }
            ]
        },
        'schema': [schema_entry],
        'customProperties': custom_properties,
        'servers': [
            {
                'id': 'server-' + table_id[:8],
                'server': 'CONFIGURE_SERVER_HOSTNAME',
                'type': server_type if server_type else 'CONFIGURE_SERVER_TYPE',
                'schema': schema_name if schema_name else 'CONFIGURE_SCHEMA_NAME'
            }
        ]
    }

    return odcs

def _add_server_warning_comments(modified_lines: List[str], line: str) -> None:
    """Add warning comment block before server definition"""
    separator = '  # ============================================'
    modified_lines.append(separator)
    modified_lines.append('  # ⚠️  MANUAL CONFIGURATION REQUIRED')
    modified_lines.append(separator)
    modified_lines.append('  # Please add/update the required server info:')
    modified_lines.append(line)


def _add_inline_comment_if_needed(line: str) -> str:
    """Add inline comment to server configuration fields if needed"""
    if '  server:' in line and 'CONFIGURE_SERVER_HOSTNAME' in line:
        return line + '  # ⚠️ UPDATE: e.g., prod.snowflake.acme.com'
    elif '  type:' in line and 'CONFIGURE_SERVER_TYPE' in line:
        return line + '  # ⚠️ UPDATE: e.g., snowflake, postgres, bigquery, redshift'
    elif '  schema:' in line and 'CONFIGURE_SCHEMA_NAME' in line:
        return line + '  # ⚠️ UPDATE: e.g., public, dbo, my_schema'
    return line


def determine_output_file(args, asset_data: Dict[str, Any]) -> str:
    """Determine the output file path using the asset name"""
    if args.output:
        return args.output

    # Try to get name from ODCS data first (for generated ODCS), then from asset summary
    asset_name = asset_data.get('name') or asset_data.get('summary', {}).get(CORE_NAME_ATTR, 'asset')
    # Sanitize the name for use as a filename
    file_name = asset_name.lower().replace(' ', '-')
    return f"{file_name}-odcs.yaml"


def write_yaml_file(output_file: str, odcs_data: Dict[str, Any]) -> None:
    """Write ODCS data to YAML file with manual configuration comments"""
    print(f"\nWriting ODCS to {output_file}...")

    # First, write the YAML normally
    yaml_content = yaml.dump(odcs_data, default_flow_style=False, sort_keys=False, allow_unicode=True)

    # Add manual configuration comments to the servers section
    lines = yaml_content.split('\n')
    modified_lines = []
    in_servers_section = False
    server_block_started = False

    for line in lines:
        # Detect servers section
        if line.startswith('servers:'):
            in_servers_section = True
            modified_lines.append(line)
            continue

        # Detect start of a server block (first item in servers array)
        if in_servers_section and line.strip().startswith('- id:') and not server_block_started:
            server_block_started = True
            _add_server_warning_comments(modified_lines, line)
            continue

        # Add inline comments for server and type fields
        if in_servers_section and server_block_started:
            line = _add_inline_comment_if_needed(line)

        modified_lines.append(line)

    # Write the modified content
    with open(output_file, 'w') as f:
        f.write('\n'.join(modified_lines))


def main():
    args = parse_arguments()
    validate_arguments(args)

    try:
        print(f"Fetching asset details for {args.asset_id}...")
        client = InformaticaClient(args.cdgc_url, args.username, args.password)

        # Fetch table asset details
        asset_data = client.get_asset_details(args.asset_id)

        # Validate that the asset is a table, not a schema or other type
        client.validate_asset_is_table(asset_data)

        # Get column IDs from hierarchy
        column_ids = [col['core.identity'] for col in asset_data.get('hierarchy', [])]

        print("Fetching column details...")

        # Fetch details for each column concurrently for better performance
        column_details = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all column detail requests
            future_to_col_id = {
                executor.submit(client.get_column_details, col_id): col_id
                for col_id in column_ids
            }

            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_col_id):
                col_id = future_to_col_id[future]
                try:
                    col_data = future.result()
                    column_details.append(col_data)
                    completed += 1
                    print(f"  Fetched column {completed}/{len(column_ids)}...")
                except Exception as e:
                    print(f"  Warning: Failed to fetch column {col_id}: {e}")

        column_details.sort(key=extract_column_position)

        print("Generating ODCS YAML...")
        odcs_data = generate_odcs_yaml(asset_data, column_details, client.base_url)

        output_file = determine_output_file(args, asset_data)
        write_yaml_file(output_file, odcs_data)

        print(f"✓ Successfully generated ODCS file: {output_file}")

    except ValueError as e:
        print(f"\n✗ Validation Error: {e}")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"\n✗ HTTP Error: {e}")
        if e.response.status_code == 401:
            print("  Authentication failed. Please check your credentials.")
        elif e.response.status_code == 404:
            print(f"  Asset {args.asset_id} not found.")
        else:
            print(f"  Status code: {e.response.status_code}")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"\n✗ Connection Error: Unable to connect to Informatica CDGC at {args.cdgc_url}")
        print("  Please check your network connection and CDGC URL.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("\n✗ Timeout Error: Request timed out")
        print("  The server took too long to respond. Please try again.")
        sys.exit(1)
    except KeyError as e:
        print(f"\n✗ Data Error: Missing expected field {e}")
        print("  The asset data structure may be incomplete or invalid.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        print("  An unexpected error occurred. Please check your inputs and try again.")
        sys.exit(1)

if __name__ == '__main__':
    main()
