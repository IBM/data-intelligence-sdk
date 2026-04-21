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
Integration Tests for Collibra ODCS Generator
"""

import os
import pytest
import tempfile
import yaml
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from wxdi.odcs_generator.generate_odcs_from_collibra import (
    CollibraClient,
    ODCSGenerator,
    parse_arguments,
    validate_arguments,
    determine_output_file,
    write_yaml_file
)


class TestCollibraClient:
    """Test CollibraClient class"""

    def test_client_initialization(self):
        """Test client initialization with valid parameters"""
        client = CollibraClient(
            base_url="https://acme.collibra.com",
            username="testuser",
            password="testpass"
        )

        assert client.base_url == "https://acme.collibra.com"
        assert client.auth == ("testuser", "testpass")
        assert client.session is not None

    def test_base_url_trailing_slash_removal(self):
        """Test that trailing slash is removed from base URL"""
        client = CollibraClient(
            base_url="https://acme.collibra.com/",
            username="testuser",
            password="testpass"
        )

        assert client.base_url == "https://acme.collibra.com"

    @patch('wxdi.odcs_generator.generate_odcs_from_collibra.requests.Session.get')
    def test_get_asset(self, mock_get):
        """Test asset retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "test-asset-id",
            "displayName": "Test Table",
            "type": {"name": "Table"}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = CollibraClient(
            base_url="https://acme.collibra.com",
            username="testuser",
            password="testpass"
        )

        asset = client.get_asset("test-asset-id")

        assert asset["id"] == "test-asset-id"
        assert asset["displayName"] == "Test Table"
        mock_get.assert_called_once()

    @patch('wxdi.odcs_generator.generate_odcs_from_collibra.requests.Session.get')
    def test_get_asset_attributes(self, mock_get):
        """Test asset attributes retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "type": {"name": "Description"},
                    "value": "Test description"
                },
                {
                    "type": {"name": "Data Type"},
                    "value": "VARCHAR"
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = CollibraClient(
            base_url="https://acme.collibra.com",
            username="testuser",
            password="testpass"
        )

        attributes = client.get_asset_attributes("test-asset-id")

        assert len(attributes) == 2
        assert attributes[0]["type"]["name"] == "Description"
        assert attributes[1]["type"]["name"] == "Data Type"

    @patch('wxdi.odcs_generator.generate_odcs_from_collibra.requests.Session.get')
    def test_get_asset_relations_as_source(self, mock_get):
        """Test asset relations retrieval where asset is source"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "source": {"id": "asset-1"},
                    "target": {"id": "column-1"}
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = CollibraClient(
            base_url="https://acme.collibra.com",
            username="testuser",
            password="testpass"
        )

        relations = client.get_asset_relations("asset-1", as_source=True)

        assert len(relations) == 1
        assert relations[0]["source"]["id"] == "asset-1"
        # Verify correct parameter was used
        call_args = mock_get.call_args
        assert 'sourceId' in call_args[1]['params']

    @patch('wxdi.odcs_generator.generate_odcs_from_collibra.requests.Session.get')
    def test_get_asset_relations_as_target(self, mock_get):
        """Test asset relations retrieval where asset is target"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "source": {"id": "column-1"},
                    "target": {"id": "asset-1"}
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = CollibraClient(
            base_url="https://acme.collibra.com",
            username="testuser",
            password="testpass"
        )

        relations = client.get_asset_relations("asset-1", as_source=False)

        assert len(relations) == 1
        assert relations[0]["target"]["id"] == "asset-1"
        # Verify correct parameter was used
        call_args = mock_get.call_args
        assert 'targetId' in call_args[1]['params']

    @patch('wxdi.odcs_generator.generate_odcs_from_collibra.requests.Session.get')
    def test_get_asset_tags(self, mock_get):
        """Test asset tags retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"name": "PII"},
            {"name": "Sensitive"},
            {"name": "Production"}
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = CollibraClient(
            base_url="https://acme.collibra.com",
            username="testuser",
            password="testpass"
        )

        tags = client.get_asset_tags("test-asset-id")

        assert len(tags) == 3
        assert "PII" in tags
        assert "Sensitive" in tags
        assert "Production" in tags

    @patch('wxdi.odcs_generator.generate_odcs_from_collibra.requests.Session.get')
    def test_get_asset_tags_error_handling(self, mock_get):
        """Test that tag retrieval errors are handled gracefully"""
        mock_get.side_effect = Exception("API Error")

        client = CollibraClient(
            base_url="https://acme.collibra.com",
            username="testuser",
            password="testpass"
        )

        tags = client.get_asset_tags("test-asset-id")

        assert tags == []

    @patch('wxdi.odcs_generator.generate_odcs_from_collibra.requests.Session.post')
    def test_get_asset_classifications(self, mock_post):
        """Test asset classifications retrieval via GraphQL"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "api": {
                    "asset": {
                        "id": "test-asset-id",
                        "classesForAsset": [
                            {
                                "id": "class-1",
                                "label": "Confidential",
                                "status": "ACCEPTED"
                            },
                            {
                                "id": "class-2",
                                "label": "Public",
                                "status": "REJECTED"
                            }
                        ]
                    }
                }
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = CollibraClient(
            base_url="https://acme.collibra.com",
            username="testuser",
            password="testpass"
        )

        classifications = client.get_asset_classifications("test-asset-id")

        # Only ACCEPTED classifications should be returned
        assert len(classifications) == 1
        assert "Confidential" in classifications
        assert "Public" not in classifications


class TestODCSGenerator:
    """Test ODCSGenerator class"""

    def test_generator_initialization(self):
        """Test generator initialization"""
        mock_client = Mock(spec=CollibraClient)
        generator = ODCSGenerator(mock_client)

        assert generator.client == mock_client

    def test_convert_timestamp(self):
        """Test timestamp conversion"""
        # Test with valid timestamp (milliseconds)
        timestamp_ms = 1609459200000  # 2021-01-01 00:00:00 UTC
        result = ODCSGenerator._convert_timestamp(timestamp_ms)

        assert "2021-01-01" in result
        assert result.endswith('Z')

        # Test with zero timestamp
        result = ODCSGenerator._convert_timestamp(0)
        assert result.endswith('Z')

    def test_build_attribute_map(self):
        """Test attribute map building"""
        attributes = [
            {
                "type": {"name": "Description"},
                "value": "Test description"
            },
            {
                "type": {"name": "Data Type"},
                "value": "VARCHAR"
            },
            {
                "type": {"name": "Empty"},
                "value": None
            }
        ]

        attr_map = ODCSGenerator._build_attribute_map(attributes)

        assert attr_map["Description"] == "Test description"
        assert attr_map["Data Type"] == "VARCHAR"
        assert "Empty" not in attr_map

    def test_logical_type_mapping(self):
        """Test logical type mapping"""
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["text"] == "string"
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["whole number"] == "integer"
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["decimal number"] == "number"
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["date time"] == "timestamp"
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["true/false"] == "boolean"

    def test_create_server_definition(self):
        """Test server definition creation"""
        server = ODCSGenerator._create_server_definition()

        assert "id" in server
        assert server["id"].startswith("server-")
        assert server["server"] == "CONFIGURE_SERVER_HOSTNAME"
        assert server["type"] == "DEFINE_SERVER_TYPE"

    def test_extract_custom_properties(self):
        """Test custom properties extraction"""
        mock_client = Mock(spec=CollibraClient)
        generator = ODCSGenerator(mock_client)

        attr_map = {
            "Description": "Test description",  # Should be excluded
            "Owner": "John Doe",
            "Created Date": "2024-01-01",
            "Custom Field": "Custom Value"
        }

        custom_props = generator._extract_custom_properties(attr_map)

        # Description should be excluded
        assert not any(prop["property"] == "description" for prop in custom_props)

        # Other properties should be included (converted to lowercase with underscores)
        assert any(prop["property"] == "owner" for prop in custom_props)
        assert any(prop["property"] == "created_date" for prop in custom_props)

    @patch.object(CollibraClient, 'get_asset')
    @patch.object(CollibraClient, 'get_asset_tags')
    @patch.object(CollibraClient, 'get_asset_attributes')
    @patch.object(CollibraClient, 'get_asset_relations')
    def test_generate_odcs_structure(self, mock_relations, mock_attrs, mock_tags, mock_asset):
        """Test ODCS structure generation"""
        # Mock asset data
        mock_asset.return_value = {
            "id": "test-asset-id",
            "displayName": "Test Table",
            "type": {"name": "Table"},
            "domain": {"name": "Finance"},
            "createdOn": 1609459200000
        }

        mock_tags.return_value = ["PII", "Production"]
        mock_attrs.return_value = [
            {"type": {"name": "Description"}, "value": "Test table description"}
        ]
        mock_relations.return_value = []

        client = CollibraClient(
            base_url="https://acme.collibra.com",
            username="testuser",
            password="testpass"
        )
        generator = ODCSGenerator(client)

        odcs = generator.generate_odcs("test-asset-id")

        # Verify ODCS structure
        assert odcs["id"] == "test-asset-id"
        assert odcs["kind"] == "DataContract"
        assert odcs["apiVersion"] == "v3.1.0"
        assert odcs["domain"] == "Finance"
        assert odcs["status"] == "active"
        assert "PII" in odcs["tags"]
        assert "Production" in odcs["tags"]

        # Verify authoritative definitions
        assert len(odcs["description"]["authoritativeDefinitions"]) == 1
        auth_def = odcs["description"]["authoritativeDefinitions"][0]
        assert auth_def["type"] == "collibra-asset"
        assert "test-asset-id" in auth_def["url"]

        # Verify schema
        assert "schema" in odcs
        assert isinstance(odcs["schema"], list)

        # Verify servers
        assert "servers" in odcs
        assert isinstance(odcs["servers"], list)


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
            '--url', 'https://acme.collibra.com',
            '-u', 'testuser',
            '-p', 'testpass'
        ]):
            args = parse_arguments()
            assert args.asset_id == 'test-asset-id'
            assert args.output == 'output.yaml'
            assert args.url == 'https://acme.collibra.com'
            assert args.username == 'testuser'
            assert args.password == 'testpass'

    @patch.dict(os.environ, {
        'COLLIBRA_URL': 'https://env.collibra.com',
        'COLLIBRA_USERNAME': 'envuser',
        'COLLIBRA_PASSWORD': 'envpass'
    })
    def test_parse_arguments_from_environment(self):
        """Test that environment variables are used as defaults"""
        with patch('sys.argv', ['script.py', 'test-asset-id']):
            args = parse_arguments()
            assert args.url == 'https://env.collibra.com'
            assert args.username == 'envuser'
            assert args.password == 'envpass'


class TestHelperFunctions:
    """Test helper functions"""

    def test_determine_output_file_with_custom_output(self):
        """Test output file determination with custom output"""
        args = Mock()
        args.output = 'custom-output.yaml'

        odcs_data = {'name': 'Test Contract'}

        output_file = determine_output_file(args, odcs_data)
        assert output_file == 'custom-output.yaml'

    def test_determine_output_file_from_asset_name(self):
        """Test output file determination from asset name"""
        args = Mock()
        args.output = None

        odcs_data = {'name': 'Customer Transactions'}

        output_file = determine_output_file(args, odcs_data)
        assert output_file == 'customer-transactions-odcs.yaml'

    def test_determine_output_file_default(self):
        """Test output file determination with default"""
        args = Mock()
        args.output = None

        odcs_data = {}

        output_file = determine_output_file(args, odcs_data)
        assert output_file == 'asset-odcs.yaml'

    def test_write_yaml_file(self):
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
            write_yaml_file(temp_file, odcs_data)

            # Read and verify
            with open(temp_file, 'r') as f:
                content = f.read()
                loaded_data = yaml.safe_load(content)

            assert loaded_data["id"] == "test-id"
            assert loaded_data["kind"] == "DataContract"
            assert "⚠️" in content  # Check for warning comments
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestIntegrationScenarios:
    """Integration test scenarios"""

    @patch.dict(os.environ, {
        'COLLIBRA_URL': 'https://acme.collibra.com',
        'COLLIBRA_USERNAME': 'testuser',
        'COLLIBRA_PASSWORD': 'testpass'
    })
    @patch.object(CollibraClient, 'get_asset')
    @patch.object(CollibraClient, 'get_asset_tags')
    @patch.object(CollibraClient, 'get_asset_attributes')
    @patch.object(CollibraClient, 'get_asset_relations')
    def test_end_to_end_odcs_generation(self, mock_relations, mock_attrs, mock_tags, mock_asset):
        """Test end-to-end ODCS generation flow"""
        # Mock asset data
        mock_asset.return_value = {
            "id": "test-id",
            "displayName": "CUSTOMER_TABLE",
            "type": {"name": "Table"},
            "domain": {"name": "Sales"},
            "createdOn": 1609459200000
        }

        mock_tags.return_value = ["Production"]

        mock_attrs.return_value = [
            {"type": {"name": "Description"}, "value": "Customer information table"},
            {"type": {"name": "Owner"}, "value": "Data Team"}
        ]

        # Mock relations with columns
        mock_relations.side_effect = [
            [],  # as_source
            [    # as_target
                {
                    "source": {
                        "id": "col-1",
                        "displayName": "customer_id",
                        "type": {"name": "Column"}
                    },
                    "target": {"id": "test-id"}
                }
            ]
        ]

        # Create client and generator
        client = CollibraClient(
            base_url="https://acme.collibra.com",
            username="testuser",
            password="testpass"
        )
        generator = ODCSGenerator(client)

        # Generate ODCS
        odcs = generator.generate_odcs("test-id")

        # Verify ODCS structure
        assert odcs["id"] == "test-id"
        assert odcs["kind"] == "DataContract"
        assert odcs["domain"] == "Sales"
        assert len(odcs["schema"]) == 1
        assert odcs["schema"][0]["name"] == "CUSTOMER_TABLE"
        assert odcs["schema"][0]["description"] == "Customer information table"

    def test_error_handling_invalid_asset_id(self):
        """Test error handling for invalid asset ID"""
        mock_client = Mock(spec=CollibraClient)
        generator = ODCSGenerator(mock_client)

        with pytest.raises(ValueError, match="Asset ID is required"):
            generator.generate_odcs("")

    @patch.object(CollibraClient, 'get_asset')
    def test_error_handling_api_failure(self, mock_asset):
        """Test error handling when API calls fail"""
        mock_asset.side_effect = Exception("API Error")

        client = CollibraClient(
            base_url="https://acme.collibra.com",
            username="testuser",
            password="testpswd"
        )
        generator = ODCSGenerator(client)

        # Should handle error gracefully
        with pytest.raises(Exception):
            generator.generate_odcs("test-id")


class TestDataTypeMapping:
    """Test data type mapping functionality"""

    def test_logical_type_mapping_coverage(self):
        """Test that common data types are mapped"""
        mapping = ODCSGenerator.LOGICAL_TYPE_MAPPING

        assert mapping["text"] == "string"
        assert mapping["whole number"] == "integer"
        assert mapping["decimal number"] == "number"
        assert mapping["date time"] == "timestamp"
        assert mapping["true/false"] == "boolean"
        assert mapping["geographical"] == "string"

    def test_numeric_types_list(self):
        """Test numeric types list"""
        numeric_types = ODCSGenerator.NUMERIC_TYPES

        assert "DECIMAL" in numeric_types
        assert "NUMERIC" in numeric_types
        assert "NUMBER" in numeric_types


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

