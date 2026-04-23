# -*- coding: utf-8 -*-
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
Integration Tests for Informatica ODCS Generator
"""

import os
import pytest
import tempfile
import yaml
from unittest.mock import Mock, patch, MagicMock
from wxdi.odcs_generator.generate_odcs_from_informatica import (
    InformaticaClient,
    parse_arguments,
    validate_arguments,
    generate_odcs_yaml,
    build_physical_type,
    build_column_property,
    build_custom_properties,
    extract_column_position,
    RESOURCE_TYPE_MAPPING,
    SYSTEM_ATTRIBUTES_MAPPING
)


class TestInformaticaClient:
    """Test InformaticaClient class"""

    def test_client_initialization(self):
        """Test client initialization with valid parameters"""
        client = InformaticaClient(
            base_url="https://cdgc.dm-us.informaticacloud.com",
            username="testuser",
            password="testpass"
        )

        assert client.base_url == "https://cdgc.dm-us.informaticacloud.com"
        assert client.username == "testuser"
        assert client.password == "testpass"
        assert client.region == "dm-us"
        assert client.identity_url == "https://dm-us.informaticacloud.com"

    def test_extract_region_from_url(self):
        """Test region extraction from various URL formats"""
        client = InformaticaClient(
            base_url="https://cdgc.dm-us.informaticacloud.com",
            username="test",
            password="test"
        )

        # Test various URL formats
        assert client._extract_region_from_url("https://cdgc.dm-us.informaticacloud.com") == "dm-us"
        assert client._extract_region_from_url("https://cdgc.na1.informaticacloud.com") == "na1"
        assert client._extract_region_from_url("https://cdgc.eu1.informaticacloud.com/") == "eu1"

    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.requests.post')
    def test_get_session_id(self, mock_post):
        """Test session ID retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {"sessionId": "test-session-id"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = InformaticaClient(
            base_url="https://cdgc.dm-us.informaticacloud.com",
            username="testuser",
            password="testpass"
        )

        session_data = client.get_session_id()

        assert session_data["sessionId"] == "test-session-id"
        mock_post.assert_called_once()

    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.requests.post')
    def test_get_auth_token_caching(self, mock_post):
        """Test that auth token is cached"""
        # Mock session ID call
        mock_session_response = Mock()
        mock_session_response.json.return_value = {"sessionId": "test-session-id"}
        mock_session_response.raise_for_status = Mock()

        # Mock JWT token call
        mock_jwt_response = Mock()
        mock_jwt_response.json.return_value = {"jwt_token": "test-jwt-token"}
        mock_jwt_response.raise_for_status = Mock()

        mock_post.side_effect = [mock_session_response, mock_jwt_response]

        client = InformaticaClient(
            base_url="https://cdgc.dm-us.informaticacloud.com",
            username="testuser",
            password="testpass"
        )

        # First call should make API requests
        token1 = client.get_auth_token()
        assert token1 == "test-jwt-token"
        assert mock_post.call_count == 2

        # Second call should use cached token
        token2 = client.get_auth_token()
        assert token2 == "test-jwt-token"
        assert mock_post.call_count == 2  # No additional calls


class TestHelperFunctions:
    """Test helper functions"""

    def test_extract_column_position(self):
        """Test column position extraction"""
        # Valid position
        col_data = {"selfAttributes": {"core.Position": "5"}}
        assert extract_column_position(col_data) == 5

        # Missing position
        col_data = {"selfAttributes": {}}
        assert extract_column_position(col_data) == 999999

        # Invalid position
        col_data = {"selfAttributes": {"core.Position": "invalid"}}
        assert extract_column_position(col_data) == 999999

    def test_build_physical_type(self):
        """Test physical type construction"""
        # Type with length
        assert build_physical_type("VARCHAR", "255", "") == "VARCHAR(255)"

        # Type with length and scale
        assert build_physical_type("DECIMAL", "10", "2") == "DECIMAL(10,2)"

        # Type without length
        assert build_physical_type("INTEGER", "", "") == "INTEGER"

        # Type with length but scale is 0
        assert build_physical_type("NUMBER", "18", "0") == "NUMBER(18)"

    def test_build_column_property(self):
        """Test column property building"""
        column_detail = {
            "summary": {
                "core.name": "customer_id",
                "core.description": "Customer identifier"
            },
            "selfAttributes": {
                "com.infa.odin.models.relational.Datatype": "VARCHAR",
                "com.infa.odin.models.relational.DatatypeLength": "50",
                "com.infa.odin.models.relational.Nullable": "false",
                "com.infa.odin.models.relational.PrimaryKeyColumn": "true"
            }
        }

        prop = build_column_property(column_detail)

        assert prop["name"] == "customer_id"
        assert prop["physicalType"] == "VARCHAR(50)"
        assert prop["description"] == "Customer identifier"
        assert prop["required"] is True
        assert prop["primaryKey"] is True

    def test_build_custom_properties(self):
        """Test custom properties building"""
        table_attrs = {
            "core.resourceName": "TestCatalog",
            "com.infa.odin.models.relational.NumberOfRows": "1000",
            "core.origin": "Production",
            "com.infa.odin.models.relational.Owner": "dbo"
        }

        custom_props = build_custom_properties(table_attrs)

        assert len(custom_props) == 4
        assert {"property": "Catalog Source Name", "value": "TestCatalog"} in custom_props
        assert {"property": "Number of rows", "value": "1000"} in custom_props
        assert {"property": "Origin", "value": "Production"} in custom_props
        assert {"property": "Schema", "value": "dbo"} in custom_props


class TestODCSGeneration:
    """Test ODCS YAML generation"""

    def test_generate_odcs_yaml_structure(self):
        """Test ODCS YAML structure generation"""
        asset_data = {
            "core.identity": "test-asset-id",
            "summary": {
                "core.name": "CUSTOMER_TABLE",
                "core.description": "Customer information table"
            },
            "selfAttributes": {
                "core.name": "customer_table",
                "core.businessName": "customer_table",
                "com.infa.odin.models.relational.Owner": "dbo",
                "core.resourceType": "Snowflake",
                "core.resourceName": "TestCatalog"
            }
        }

        column_details = [
            {
                "summary": {
                    "core.name": "id",
                    "core.description": "Primary key"
                },
                "selfAttributes": {
                    "com.infa.odin.models.relational.Datatype": "INTEGER",
                    "com.infa.odin.models.relational.Nullable": "false",
                    "com.infa.odin.models.relational.PrimaryKeyColumn": "true",
                    "core.Position": "1"
                }
            }
        ]

        base_url = "https://cdgc.dm-us.informaticacloud.com"

        odcs = generate_odcs_yaml(asset_data, column_details, base_url)

        # Verify structure
        assert odcs["id"] == "test-asset-id"
        assert odcs["kind"] == "DataContract"
        assert odcs["apiVersion"] == "v3.1.0"
        assert odcs["status"] == "active"

        # Verify schema
        assert len(odcs["schema"]) == 1
        schema = odcs["schema"][0]
        assert schema["name"] == "customer_table"
        assert schema["physicalName"] == "dbo/customer_table"
        assert schema["physicalType"] == "Table"
        assert len(schema["properties"]) == 1

        # Verify column
        column = schema["properties"][0]
        assert column["name"] == "id"
        assert column["physicalType"] == "INTEGER"
        assert column["required"] is True
        assert column["primaryKey"] is True

        # Verify servers
        assert len(odcs["servers"]) == 1
        server = odcs["servers"][0]
        assert server["type"] == "snowflake"
        assert server["schema"] == "dbo"

        # Verify authoritative definitions
        assert len(odcs["description"]["authoritativeDefinitions"]) == 1
        auth_def = odcs["description"]["authoritativeDefinitions"][0]
        assert auth_def["type"] == "informatica-asset"
        assert "test-asset-id" in auth_def["url"]


class TestResourceTypeMapping:
    """Test resource type mapping"""

    def test_resource_type_mapping_coverage(self):
        """Test that common database types are mapped"""
        assert RESOURCE_TYPE_MAPPING["Snowflake"] == "snowflake"
        assert RESOURCE_TYPE_MAPPING["PostgreSQL"] == "postgresql"
        assert RESOURCE_TYPE_MAPPING["Oracle"] == "oracle"
        assert RESOURCE_TYPE_MAPPING["SqlServer"] == "sqlserver"
        assert RESOURCE_TYPE_MAPPING["BigQuery"] == "bigquery"
        assert RESOURCE_TYPE_MAPPING["Redshift"] == "redshift"


class TestArgumentParsing:
    """Test command-line argument parsing"""

    def test_parse_arguments_with_asset_id(self):
        """Test parsing with required asset ID"""
        with patch('sys.argv', ['script.py', 'test-asset-id']):
            args = parse_arguments()
            assert args.asset_id == 'test-asset-id'

    def test_parse_arguments_with_all_options(self):
        """Test parsing with all command-line options"""
        with patch('sys.argv', [
            'script.py',
            'test-asset-id',
            '-o', 'output.yaml',
            '--cdgc-url', 'https://cdgc.test.com',
            '-u', 'testuser',
            '-p', 'testpass'
        ]):
            args = parse_arguments()
            assert args.asset_id == 'test-asset-id'
            assert args.output == 'output.yaml'
            assert args.cdgc_url == 'https://cdgc.test.com'
            assert args.username == 'testuser'
            assert args.password == 'testpass'


class TestIntegrationScenarios:
    """Integration test scenarios"""

    @patch.dict(os.environ, {
        'INFORMATICA_CDGC_URL': 'https://cdgc.dm-us.informaticacloud.com',
        'INFORMATICA_USERNAME': 'testuser',
        'INFORMATICA_PASSWORD': 'testpawd'
    })
    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.InformaticaClient')
    def test_end_to_end_odcs_generation(self, mock_client_class):
        """Test end-to-end ODCS generation flow"""
        # Mock client instance
        mock_client = Mock()
        mock_client.base_url = "https://cdgc.dm-us.informaticacloud.com"
        mock_client_class.return_value = mock_client

        # Mock asset data
        mock_client.get_asset_details.return_value = {
            "core.identity": "test-id",
            "summary": {"core.name": "TEST_TABLE"},
            "selfAttributes": {
                "core.businessName": "test_table",
                "com.infa.odin.models.relational.Owner": "public",
                "core.resourceType": "PostgreSQL"
            },
            "hierarchy": [{"core.identity": "col-1"}]
        }

        # Mock column data
        mock_client.get_column_details.return_value = {
            "summary": {"core.name": "id"},
            "selfAttributes": {
                "com.infa.odin.models.relational.Datatype": "INTEGER",
                "core.Position": "1"
            }
        }

        # Generate ODCS
        asset_data = mock_client.get_asset_details("test-id")
        column_ids = [col['core.identity'] for col in asset_data.get('hierarchy', [])]
        column_details = [mock_client.get_column_details(col_id) for col_id in column_ids]

        odcs = generate_odcs_yaml(asset_data, column_details, mock_client.base_url)

        # Verify ODCS structure
        assert odcs["id"] == "test-id"
        assert odcs["kind"] == "DataContract"
        assert len(odcs["schema"]) == 1
        assert len(odcs["schema"][0]["properties"]) == 1
        assert odcs["servers"][0]["type"] == "postgresql"

    def test_yaml_file_generation(self):
        """Test YAML file writing"""
        odcs_data = {
            "id": "test-id",
            "kind": "DataContract",
            "apiVersion": "v3.1.0",
            "schema": [{"name": "test_table"}],
            "servers": [{"id": "server-1", "server": "CONFIGURE_SERVER_HOSTNAME"}]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_file = f.name

        try:
            # Write YAML
            yaml_content = yaml.dump(odcs_data, default_flow_style=False, sort_keys=False)
            with open(temp_file, 'w') as f:
                f.write(yaml_content)

            # Read and verify
            with open(temp_file, 'r') as f:
                loaded_data = yaml.safe_load(f)

            assert loaded_data["id"] == "test-id"
            assert loaded_data["kind"] == "DataContract"
            assert loaded_data["apiVersion"] == "v3.1.0"
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

