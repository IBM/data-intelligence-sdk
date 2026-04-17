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
Generate ODCS YAML file from Collibra Asset

This script fetches asset metadata from Collibra and generates an ODCS v3 compliant YAML file.

Usage:
    python generate_odcs_from_collibra.py <asset_id>
    python generate_odcs_from_collibra.py 019a57f9-62d2-7aa0-9f22-4fa2cea1180b

Environment Variables:
    COLLIBRA_URL: Collibra instance URL (required)
    COLLIBRA_USERNAME: Collibra username (required)
    COLLIBRA_PASSWORD: Collibra password (required)
"""

import argparse
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests
import yaml


class CollibraClient:
    """Client for interacting with Collibra REST API"""

    HEADERS_JSON = {"Accept": "application/json"}
    HEADERS_CONTENT_JSON = {"Content-Type": "application/json"}
    DEFAULT_LIMIT = 1000

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
        self.session = requests.Session()
        self.session.auth = self.auth

    def get_asset(self, asset_id: str) -> Dict[str, Any]:
        """Fetch asset details from Collibra"""
        url = f"{self.base_url}/rest/2.0/assets/{asset_id}"
        response = self.session.get(url, headers=self.HEADERS_JSON)
        response.raise_for_status()
        return response.json()

    def get_asset_attributes(self, asset_id: str) -> List[Dict[str, Any]]:
        """Fetch all attributes for an asset"""
        url = f"{self.base_url}/rest/2.0/attributes"
        params = {'assetId': asset_id, 'limit': self.DEFAULT_LIMIT}
        response = self.session.get(url, params=params, headers=self.HEADERS_JSON)
        response.raise_for_status()
        return response.json().get('results', [])

    def get_asset_relations(self, asset_id: str, as_source: bool = True) -> List[Dict[str, Any]]:
        """Fetch all relations for an asset

        Args:
            asset_id: The asset ID
            as_source: If True, fetch relations where asset is source; if False, where asset is target
        """
        url = f"{self.base_url}/rest/2.0/relations"
        param_key = 'sourceId' if as_source else 'targetId'
        params = {param_key: asset_id, 'limit': self.DEFAULT_LIMIT}
        response = self.session.get(url, params=params, headers=self.HEADERS_JSON)
        response.raise_for_status()
        return response.json().get('results', [])

    def get_asset_tags(self, asset_id: str) -> List[str]:
        """Fetch tags directly assigned to an asset"""
        url = f"{self.base_url}/rest/2.0/assets/{asset_id}/tags"
        try:
            response = self.session.get(url, headers=self.HEADERS_JSON)
            response.raise_for_status()
            results = response.json()
            return [tag['name'] for tag in results if 'name' in tag]
        except Exception as e:
            print(f"Warning: Could not fetch tags: {e}")
            return []

    def get_asset_classifications(self, asset_id: str) -> List[str]:
        """Fetch data classifications for an asset using GraphQL API"""
        url = f"{self.base_url}/graphql"

        query = """
        query AssetClassification($id: ID!) {
            api {
                asset(id: $id) {
                    id
                    classesForAsset {
                        id
                        classificationId
                        label
                        percentage
                        status
                    }
                }
            }
        }
        """

        payload = {"query": query, "variables": {"id": asset_id}}

        try:
            response = self.session.post(url, json=payload, headers=self.HEADERS_CONTENT_JSON)
            response.raise_for_status()
            data = response.json()

            asset_data = data.get('data', {}).get('api', {}).get('asset', {})
            classes = asset_data.get('classesForAsset', [])

            return [
                cls['label']
                for cls in classes
                if cls.get('status') == 'ACCEPTED' and cls.get('label')
            ]
        except Exception:
            return []

class ODCSGenerator:
    """Generate ODCS YAML from Collibra asset metadata"""

    UTC_TIMEZONE_SUFFIX = '+00:00'
    EXCLUDED_ATTRIBUTES = {'Description'}
    LOGICAL_TYPE_MAPPING = {
        'text': 'string',
        'whole number': 'integer',
        'decimal number': 'number',
        'date time': 'timestamp',
        'string': 'string',
        'integer': 'integer',
        'number': 'number',
        'date': 'date',
        'time': 'time',
        'object': 'object',
        'array': 'array',
        'geographical': 'string',
        'true/false': 'boolean',
        'n/a': None
    }
    NUMERIC_TYPES = ['DECIMAL', 'NUMERIC', 'NUMBER']

    def __init__(self, collibra_client: CollibraClient):
        self.client = collibra_client

    def generate_odcs(self, asset_id: str) -> Dict[str, Any]:
        """Generate ODCS structure from a single Collibra asset

        Args:
            asset_id: Collibra asset ID to include in the contract

        Returns:
            ODCS data contract dictionary with single asset in schema array

        Raises:
            ValueError: If asset is not a table
        """
        if not asset_id:
            raise ValueError("Asset ID is required")

        print(f"Generating ODCS for asset: {asset_id}")
        print(f"\n=== Processing asset: {asset_id} ===")

        # Fetch asset details for contract-level metadata
        print("Fetching asset details...")
        asset = self.client.get_asset(asset_id)

        # Validate that the asset is a table
        asset_type = asset.get('type', {}).get('name', '').lower()
        print(f"Asset type: {asset_type}")

        if 'table' not in asset_type:
            raise ValueError(
                f"Asset '{asset.get('displayName', asset_id)}' is is not a type 'Table'. "
                f"This script only processes table assets. "
                f"Please provide a table asset ID."
            )

        domain_name = asset.get('domain', {}).get('name', '')
        asset_display_name = asset.get('displayName', asset.get('name', 'asset'))
        created_date = datetime.now(timezone.utc).isoformat().replace(self.UTC_TIMEZONE_SUFFIX, 'Z')

        odcs = {
            'id': asset_id,
            'kind': 'DataContract',
            'apiVersion': 'v3.1.0',
            'domain': domain_name,
            'dataProduct': 'Sample data product',
            'version': '1.0.0',
            'name': 'Sample contract',
            'status': 'active',
            'contractCreatedTs': created_date,
            'description': {
                'authoritativeDefinitions': [{
                    'type': 'collibra-asset',
                    'url': f'{self.client.base_url}/asset/{asset_id}'
                }]
            },
            '_asset_display_name': asset_display_name
        }

        # Add tags from Collibra
        collibra_tags = self.client.get_asset_tags(asset_id)
        odcs['tags'] = collibra_tags if collibra_tags else []

        # Process the asset and build schema array
        result = self._process_asset(asset_id)
        if result:
            schema_def, server = result
            odcs['schema'] = [schema_def]
            odcs['servers'] = [server]
        else:
            odcs['schema'] = []
            odcs['servers'] = []

        return odcs

    @staticmethod
    def _convert_timestamp(timestamp_ms: int) -> str:
        """Convert millisecond timestamp to ISO format"""
        utc_timezone_suffix = '+00:00'
        if timestamp_ms:
            return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).isoformat().replace(utc_timezone_suffix, 'Z')
        return datetime.now(timezone.utc).isoformat().replace(utc_timezone_suffix, 'Z')

    @staticmethod
    def _build_attribute_map(attributes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build a dictionary mapping attribute type names to values"""
        attr_map = {}
        for attr in attributes:
            attr_type_name = attr.get('type', {}).get('name', '')
            attr_value = attr.get('value')
            if attr_type_name and attr_value:
                attr_map[attr_type_name] = attr_value
        return attr_map


    def _process_asset(self, asset_id: str) -> Optional[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """Process asset and return its schema definition and server

        Args:
            asset_id: Collibra asset ID to process

        Returns:
            Tuple of (schema_def, server) or None if processing fails
        """
        try:
            # Fetch asset details
            print("Fetching asset details...")
            asset = self.client.get_asset(asset_id)

            print("Fetching asset attributes...")
            attributes = self.client.get_asset_attributes(asset_id)

            print("Fetching asset relations (as source)...")
            source_relations = self.client.get_asset_relations(asset_id, as_source=True)

            print("Fetching asset relations (as target)...")
            target_relations = self.client.get_asset_relations(asset_id, as_source=False)
            print(f"Found {len(target_relations)} relations where asset is target")

            all_relations = source_relations + target_relations

            # Extract asset metadata
            display_name = asset.get('displayName', '')
            asset_type = asset.get('type', {}).get('name', '')


            attr_map = self._build_attribute_map(attributes)
            description = attr_map.get('Description', '')

            # Extract schema name from relations
            schema_name = self._extract_schema_from_relations(target_relations)

            # Build physical name as schema/table_name
            physical_name = f"{schema_name}/{display_name}" if schema_name else display_name

            # Create server definition with schema
            server = self._create_server_definition(schema_name)

            # Create schema definition
            schema_def = {
                'id': asset_id,
                'name': display_name,
                'physicalName': physical_name,
                'physicalType': 'table' if asset_type.lower() == 'table' else 'view',
                'description': description,
                'properties': []
            }

            # Add custom properties
            custom_properties = self._extract_custom_properties(attr_map)
            if custom_properties:
                schema_def['customProperties'] = custom_properties

            # Extract and add column properties
            columns_found = self._extract_columns_from_relations(all_relations)

            if columns_found:
                print(f"Found {len(columns_found)} unique columns from relations")
                self._add_columns_to_schema(schema_def, columns_found)

            if not schema_def['properties']:
                print("Warning: No columns found in Collibra.")

            return (schema_def, server)

        except Exception as e:
            print(f"Error processing asset {asset_id}: {e}")
            return None

    @staticmethod
    def _create_server_definition(schema_name: str = '') -> Dict[str, Any]:
        """Create server definition with placeholder values and schema"""
        server_id = f"server-{uuid.uuid4().hex[:8]}"
        return {
            'id': server_id,
            'server': 'CONFIGURE_SERVER_HOSTNAME',
            'type': 'DEFINE_SERVER_TYPE',
            'schema': schema_name if schema_name else 'CONFIGURE_SCHEMA_NAME'
        }

    def _extract_schema_from_relations(self, relations: List[Dict[str, Any]]) -> str:
        """Extract schema name from relations where table is the target

        Args:
            relations: List of relations where the table is the target

        Returns:
            Schema name if found, empty string otherwise
        """
        print("Attempting to extract schema from relations...")
        for relation in relations:
            try:
                relation_type = relation.get('type', {}).get('name', '')
                print(f"  Checking relation type: {relation_type}")

                # Check source of the relation (where table is target)
                source = relation.get('source', {})
                if source and source.get('id'):
                    source_asset = self.client.get_asset(str(source.get('id')))
                    source_type = source_asset.get('type', {}).get('name', '')
                    source_name = source_asset.get('displayName', source_asset.get('name', ''))

                    print(f"    Source: name='{source_name}', type='{source_type}'")

                    # Check if the source is a schema/database schema
                    if 'schema' in source_type.lower():
                        print(f"  ✓ Found schema from relation: {source_name}")
                        return source_name

                # Also check target of the relation (where table is source)
                target = relation.get('target', {})
                if target and target.get('id'):
                    target_asset = self.client.get_asset(str(target.get('id')))
                    target_type = target_asset.get('type', {}).get('name', '')
                    target_name = target_asset.get('displayName', target_asset.get('name', ''))

                    print(f"    Target: name='{target_name}', type='{target_type}'")

                    # Check if the target is a schema/database schema
                    if 'schema' in target_type.lower():
                        print(f"  ✓ Found schema from relation: {target_name}")
                        return target_name

            except Exception as e:
                print(f"  Warning: Error extracting schema from relation: {e}")
                continue

        print("  No schema found in relations")
        return ''

    def _extract_custom_properties(self, attr_map: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract custom properties from attribute map"""
        custom_properties = []
        for attr_name, attr_value in attr_map.items():
            if attr_name not in self.EXCLUDED_ATTRIBUTES and attr_value:
                custom_prop_name = attr_name.lower().replace(' ', '_')
                custom_properties.append({
                    'property': custom_prop_name,
                    'value': attr_value
                })
        return custom_properties

    def _extract_columns_from_relations(self, relations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract column information from asset relations"""
        print("Extracting column information from all relations...")
        print(f"Total relations found: {len(relations)}")

        columns_found = []
        seen_column_ids = set()
        seen_column_names = set()

        for relation in relations:
            # Process source
            self._process_relation_endpoint(
                relation.get('source', {}),
                'source',
                seen_column_ids,
                seen_column_names,
                columns_found
            )

            # Process target
            self._process_relation_endpoint(
                relation.get('target', {}),
                'target',
                seen_column_ids,
                seen_column_names,
                columns_found
            )

        return columns_found

    def _process_relation_endpoint(
        self,
        endpoint: Dict[str, Any],
        endpoint_type: str,
        seen_column_ids: set,
        seen_column_names: set,
        columns_found: List[Dict[str, Any]]
    ) -> None:
        """Process a single relation endpoint (source or target)"""
        if not endpoint or not endpoint.get('id'):
            return

        endpoint_id = endpoint.get('id')
        if not endpoint_id or endpoint_id in seen_column_ids:
            return

        try:
            endpoint_asset = self.client.get_asset(str(endpoint_id))
            endpoint_type_name = endpoint_asset.get('type', {}).get('name', '')
            endpoint_name = endpoint_asset.get('displayName', endpoint_asset.get('name', ''))

            if 'column' in endpoint_type_name.lower():
                print(f"  Found column ({endpoint_type}): name='{endpoint_name}', type='{endpoint_type_name}'")
                seen_column_ids.add(endpoint_id)

                if endpoint_name not in seen_column_names:
                    seen_column_names.add(endpoint_name)
                    col_attributes = self.client.get_asset_attributes(str(endpoint_id))
                    col_classifications = self.client.get_asset_classifications(str(endpoint_id))
                    columns_found.append({
                        'asset': endpoint_asset,
                        'attributes': col_attributes,
                        'classifications': col_classifications
                    })
        except Exception:
            pass

    def _add_columns_to_schema(self, schema_def: Dict[str, Any], columns_found: List[Dict[str, Any]]) -> None:
        """Add column properties to schema definition"""
        added_column_names = set()
        for col_data in columns_found:
            property_def = self._create_property_from_collibra(
                col_data['asset'],
                col_data['attributes'],
                col_data.get('classifications', [])
            )
            col_name = property_def.get('name')

            if col_name not in added_column_names:
                added_column_names.add(col_name)
                schema_def['properties'].append(property_def)
            else:
                print(f"Skipping duplicate property: {col_name}")

    def _create_property_from_collibra(
        self,
        col_asset: Dict[str, Any],
        col_attributes: List[Dict[str, Any]],
        classifications: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a property (column) definition from Collibra asset, attributes, and classifications"""
        col_name = col_asset.get('displayName', col_asset.get('name', 'unknown_column'))
        col_id = col_asset.get('id')

        attr_map = self._build_attribute_map(col_attributes)
        classifications = classifications or []

        # Extract data types
        logical_type = self._normalize_logical_type(attr_map.get('Data Type', ''))
        physical_type = self._build_physical_type(attr_map)

        # Extract metadata
        description = attr_map.get('Description', attr_map.get('Definition', ''))
        is_nullable = self._parse_boolean_value(
            attr_map.get('Is Nullable', attr_map.get('Nullable', 'true'))
        )
        is_primary_key = self._parse_boolean_value(
            attr_map.get('Is Primary Key', attr_map.get('Primary Key', attr_map.get('IsPrimaryKey', '')))
        )
        physical_name = attr_map.get('Original Name', attr_map.get('Physical Name', col_name))
        security_class = attr_map.get('Security Classification', attr_map.get('Classification', ''))

        # Build tags
        tags = self._build_column_tags(attr_map, classifications, col_id)

        # Build property definition
        prop = {
            'name': col_name,
            'physicalName': physical_name,
            'description': description,
            'required': is_nullable,
            'tags': tags
        }

        # Add optional fields
        if logical_type is not None:
            prop['logicalType'] = logical_type
        if physical_type is not None:
            prop['physicalType'] = physical_type
        if is_primary_key:
            prop['primaryKey'] = True
        if security_class:
            prop['classification'] = security_class

        return prop

    def _normalize_logical_type(self, logical_type: str) -> Optional[str]:
        """Normalize logical type to ODCS standard types"""
        if not logical_type:
            return None

        normalized = logical_type.lower().strip()
        return self.LOGICAL_TYPE_MAPPING.get(normalized, logical_type)

    def _build_physical_type(self, attr_map: Dict[str, Any]) -> Optional[str]:
        """Build physical type string with size/precision/scale"""
        technical_data_type = attr_map.get('Technical Data Type', '')
        if not technical_data_type:
            return None

        base_type = technical_data_type.upper()

        # Extract size-related attributes
        size = self._to_int(attr_map.get('Size', attr_map.get('Length', '')))
        precision = self._to_int(attr_map.get('Precision', ''))
        scale = self._to_int(attr_map.get('Scale', attr_map.get('Number Of Fractional Digits', '')))

        # For numeric types, use Size as precision if Precision is not set
        if base_type in self.NUMERIC_TYPES and precision is None and size is not None:
            precision = size

        # Build type string with parameters
        if scale is not None and precision is not None:
            return f"{base_type}({precision},{scale})"
        elif precision is not None:
            return f"{base_type}({precision})"
        elif size is not None:
            return f"{base_type}({size})"
        else:
            return base_type

    @staticmethod
    def _to_int(value: Any) -> Optional[int]:
        """Convert decimal string to integer, handling empty strings"""
        if not value:
            return None
        try:
            return int(float(str(value)))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_boolean_value(value: Any) -> bool:
        """Parse boolean value from various formats"""
        if isinstance(value, bool):
            return value
        return str(value).lower() in ['true', 'yes', '1', 'y']

    def _build_column_tags(
        self,
        attr_map: Dict[str, Any],
        classifications: List[str],
        col_id: Optional[str]
    ) -> List[str]:
        """Build tags list for a column"""
        tags = []

        # Add PII tag if applicable
        pii_value = attr_map.get('Personally Identifiable Information', attr_map.get('PII', ''))
        if pii_value and self._parse_boolean_value(pii_value):
            tags.append('PII')

        # Add classification tags
        for classification in classifications:
            tags.append(f'data_classification:{classification}')

        # Add Collibra tags
        if col_id:
            try:
                col_tags = self.client.get_asset_tags(col_id)
                if col_tags:
                    tags.extend(col_tags)
            except Exception:
                pass

        return tags



def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Generate ODCS YAML file from Collibra asset',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate ODCS from asset:
    python generate_odcs_from_collibra.py 019a57f9-62d2-7aa0-9f22-4fa2cea1180b

  With custom output:
    python generate_odcs_from_collibra.py <asset_id> -o custom-output.yaml

Environment Variables:
  COLLIBRA_URL       Collibra instance URL (required)
  COLLIBRA_USERNAME  Collibra username (required)
  COLLIBRA_PASSWORD  Collibra password (required)
        """
    )

    parser.add_argument('asset_id', help='Collibra asset ID')
    parser.add_argument('-o', '--output', help='Output YAML file path (default: <asset_name>-odcs.yaml)')
    parser.add_argument('--url', help='Collibra base URL', default=os.getenv('COLLIBRA_URL'))
    parser.add_argument('-u', '--username', help='Collibra username', default=os.getenv('COLLIBRA_USERNAME'))
    parser.add_argument('-p', '--password', help='Collibra password', default=os.getenv('COLLIBRA_PASSWORD'))

    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> None:
    """Validate required arguments"""
    if not args.url:
        print("Error: Collibra URL is required. Set COLLIBRA_URL environment variable or use --url")
        sys.exit(1)

    if not args.username:
        print("Error: Collibra username is required. Set COLLIBRA_USERNAME environment variable or use --username")
        sys.exit(1)

    if not args.password:
        print("Error: Collibra password is required. Set COLLIBRA_PASSWORD environment variable or use --password")
        sys.exit(1)


def determine_output_file(args: argparse.Namespace, odcs_data: Dict[str, Any]) -> str:
    """Determine the output file path"""
    if args.output:
        return args.output

    # Use asset display name for filename if available, otherwise use contract name
    asset_name = odcs_data.get('_asset_display_name') or odcs_data.get('name', 'asset')
    asset_name = asset_name.lower().replace(' ', '-')
    return f"{asset_name}-odcs.yaml"


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
    elif '  type:' in line and 'DEFINE_SERVER_TYPE' in line:
        return line + '  # ⚠️ UPDATE: e.g., snowflake, postgres, bigquery, redshift'
    elif '  schema:' in line and 'CONFIGURE_SCHEMA_NAME' in line:
        return line + '  # ⚠️ UPDATE: e.g., public, dbo, my_schema'
    return line


def write_yaml_file(output_file: str, odcs_data: Dict[str, Any]) -> None:
    """Write ODCS data to YAML file with manual configuration comments"""
    print(f"\nWriting ODCS to {output_file}...")

    # Remove temporary field used for filename generation
    odcs_data_copy = odcs_data.copy()
    odcs_data_copy.pop('_asset_display_name', None)

    # First, write the YAML normally
    yaml_content = yaml.dump(odcs_data_copy, default_flow_style=False, sort_keys=False, allow_unicode=True)

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
    """Main entry point"""
    args = parse_arguments()
    validate_arguments(args)

    try:
        print(f"Connecting to Collibra at {args.url}...")
        client = CollibraClient(args.url, args.username, args.password)

        print("Fetching asset...")
        generator = ODCSGenerator(client)
        odcs_data = generator.generate_odcs(args.asset_id)

        output_file = determine_output_file(args, odcs_data)
        write_yaml_file(output_file, odcs_data)

        print(f"✓ Successfully generated ODCS file: {output_file}")

    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP {e.response.status_code} - {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()