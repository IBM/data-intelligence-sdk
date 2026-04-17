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
Unit Tests for Collibra ODCS Generator
Tests individual functions and methods in isolation
"""

import pytest
import os
from unittest.mock import Mock, patch
from datetime import datetime
from wxdi.odcs_generator.generate_odcs_from_collibra import (
    CollibraClient,
    ODCSGenerator,
    determine_output_file
)


class TestODCSGeneratorStaticMethods:
    """Unit tests for ODCSGenerator static methods"""

    def test_convert_timestamp_with_valid_milliseconds(self):
        """Test timestamp conversion with valid milliseconds"""
        # 2021-01-01 00:00:00 UTC in milliseconds
        timestamp_ms = 1609459200000
        result = ODCSGenerator._convert_timestamp(timestamp_ms)

        assert "2021-01-01" in result
        assert result.endswith('Z')

    def test_convert_timestamp_with_zero(self):
        """Test timestamp conversion with zero"""
        result = ODCSGenerator._convert_timestamp(0)

        # Should return current time
        assert result.endswith('Z')
        assert 'T' in result

    def test_convert_timestamp_with_none(self):
        """Test timestamp conversion with None/falsy value"""
        result = ODCSGenerator._convert_timestamp(None)

        # Should return current time
        assert result.endswith('Z')

    def test_convert_timestamp_format(self):
        """Test that timestamp format is ISO 8601"""
        timestamp_ms = 1609459200000
        result = ODCSGenerator._convert_timestamp(timestamp_ms)

        # Should contain date and time separator
        assert 'T' in result
        # Should end with Z for UTC
        assert result.endswith('Z')

    def test_build_attribute_map_empty(self):
        """Test building attribute map with empty list"""
        result = ODCSGenerator._build_attribute_map([])
        assert result == {}

    def test_build_attribute_map_single_attribute(self):
        """Test building attribute map with single attribute"""
        attributes = [
            {
                "type": {"name": "Description"},
                "value": "Test description"
            }
        ]

        result = ODCSGenerator._build_attribute_map(attributes)

        assert result["Description"] == "Test description"

    def test_build_attribute_map_multiple_attributes(self):
        """Test building attribute map with multiple attributes"""
        attributes = [
            {"type": {"name": "Description"}, "value": "Desc1"},
            {"type": {"name": "Data Type"}, "value": "VARCHAR"},
            {"type": {"name": "Owner"}, "value": "John"}
        ]

        result = ODCSGenerator._build_attribute_map(attributes)

        assert len(result) == 3
        assert result["Description"] == "Desc1"
        assert result["Data Type"] == "VARCHAR"
        assert result["Owner"] == "John"

    def test_build_attribute_map_missing_type_name(self):
        """Test that attributes without type name are skipped"""
        attributes = [
            {"type": {}, "value": "Value1"},
            {"type": {"name": "Valid"}, "value": "Value2"}
        ]

        result = ODCSGenerator._build_attribute_map(attributes)

        assert len(result) == 1
        assert result["Valid"] == "Value2"

    def test_build_attribute_map_missing_value(self):
        """Test that attributes without value are skipped"""
        attributes = [
            {"type": {"name": "Empty"}, "value": None},
            {"type": {"name": "Valid"}, "value": "Value"}
        ]

        result = ODCSGenerator._build_attribute_map(attributes)

        assert len(result) == 1
        assert result["Valid"] == "Value"

    def test_build_attribute_map_empty_string_value(self):
        """Test that attributes with empty string value are skipped"""
        attributes = [
            {"type": {"name": "Empty"}, "value": ""},
            {"type": {"name": "Valid"}, "value": "Value"}
        ]

        result = ODCSGenerator._build_attribute_map(attributes)

        assert len(result) == 1
        assert result["Valid"] == "Value"

    def test_create_server_definition(self):
        """Test server definition creation"""
        server = ODCSGenerator._create_server_definition()

        assert "id" in server
        assert server["id"].startswith("server-")
        assert len(server["id"]) == 15  # "server-" + 8 hex chars
        assert server["server"] == "CONFIGURE_SERVER_HOSTNAME"
        assert server["type"] == "DEFINE_SERVER_TYPE"

    def test_create_server_definition_unique_ids(self):
        """Test that server definitions have unique IDs"""
        server1 = ODCSGenerator._create_server_definition()
        server2 = ODCSGenerator._create_server_definition()

        assert server1["id"] != server2["id"]


class TestODCSGeneratorExtractCustomProperties:
    """Unit tests for _extract_custom_properties method"""

    def test_extract_custom_properties_empty(self):
        """Test with empty attribute map"""
        mock_client = Mock(spec=CollibraClient)
        generator = ODCSGenerator(mock_client)

        result = generator._extract_custom_properties({})
        assert result == []

    def test_extract_custom_properties_excludes_description(self):
        """Test that Description is excluded"""
        mock_client = Mock(spec=CollibraClient)
        generator = ODCSGenerator(mock_client)

        attr_map = {
            "Description": "This should be excluded",
            "Owner": "John Doe"
        }

        result = generator._extract_custom_properties(attr_map)

        # Description should not be in custom properties
        assert not any(prop["property"] == "description" for prop in result)
        # Owner should be included (converted to lowercase)
        assert any(prop["property"] == "owner" for prop in result)

    def test_extract_custom_properties_multiple(self):
        """Test with multiple custom properties"""
        mock_client = Mock(spec=CollibraClient)
        generator = ODCSGenerator(mock_client)

        attr_map = {
            "Owner": "John Doe",
            "Created Date": "2024-01-01",
            "Status": "Active",
            "Custom Field": "Custom Value"
        }

        result = generator._extract_custom_properties(attr_map)

        assert len(result) == 4
        properties = {prop["property"]: prop["value"] for prop in result}
        # Property names are converted to lowercase with underscores
        assert properties["owner"] == "John Doe"
        assert properties["created_date"] == "2024-01-01"
        assert properties["status"] == "Active"
        assert properties["custom_field"] == "Custom Value"

    def test_extract_custom_properties_format(self):
        """Test that custom properties have correct format"""
        mock_client = Mock(spec=CollibraClient)
        generator = ODCSGenerator(mock_client)

        attr_map = {"Owner": "John"}

        result = generator._extract_custom_properties(attr_map)

        assert len(result) == 1
        assert "property" in result[0]
        assert "value" in result[0]
        assert result[0]["property"] == "owner"  # Converted to lowercase
        assert result[0]["value"] == "John"


class TestODCSGeneratorLogicalTypeMapping:
    """Unit tests for logical type mapping"""

    def test_text_to_string(self):
        """Test text maps to string"""
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["text"] == "string"

    def test_whole_number_to_integer(self):
        """Test whole number maps to integer"""
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["whole number"] == "integer"

    def test_decimal_number_to_number(self):
        """Test decimal number maps to number"""
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["decimal number"] == "number"

    def test_date_time_to_timestamp(self):
        """Test date time maps to timestamp"""
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["date time"] == "timestamp"

    def test_boolean_mapping(self):
        """Test true/false maps to boolean"""
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["true/false"] == "boolean"

    def test_geographical_to_string(self):
        """Test geographical maps to string"""
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["geographical"] == "string"

    def test_standard_types(self):
        """Test standard type mappings"""
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["string"] == "string"
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["integer"] == "integer"
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["number"] == "number"
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["date"] == "date"
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["time"] == "time"

    def test_complex_types(self):
        """Test complex type mappings"""
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["object"] == "object"
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["array"] == "array"

    def test_na_mapping(self):
        """Test n/a maps to None"""
        assert ODCSGenerator.LOGICAL_TYPE_MAPPING["n/a"] is None

    def test_unmapped_type(self):
        """Test that unmapped types return KeyError"""
        with pytest.raises(KeyError):
            _ = ODCSGenerator.LOGICAL_TYPE_MAPPING["unmapped_type"]


class TestODCSGeneratorNumericTypes:
    """Unit tests for numeric types list"""

    def test_decimal_in_numeric_types(self):
        """Test DECIMAL is in numeric types"""
        assert "DECIMAL" in ODCSGenerator.NUMERIC_TYPES

    def test_numeric_in_numeric_types(self):
        """Test NUMERIC is in numeric types"""
        assert "NUMERIC" in ODCSGenerator.NUMERIC_TYPES

    def test_number_in_numeric_types(self):
        """Test NUMBER is in numeric types"""
        assert "NUMBER" in ODCSGenerator.NUMERIC_TYPES

    def test_numeric_types_count(self):
        """Test expected number of numeric types"""
        assert len(ODCSGenerator.NUMERIC_TYPES) == 3


class TestODCSGeneratorExcludedAttributes:
    """Unit tests for excluded attributes"""

    def test_description_excluded(self):
        """Test that Description is in excluded attributes"""
        assert "Description" in ODCSGenerator.EXCLUDED_ATTRIBUTES

    def test_excluded_attributes_is_set(self):
        """Test that EXCLUDED_ATTRIBUTES is a set"""
        assert isinstance(ODCSGenerator.EXCLUDED_ATTRIBUTES, set)


class TestCollibraClientUnit:
    """Unit tests for CollibraClient class"""

    def test_client_initialization(self):
        """Test client initialization"""
        client = CollibraClient(
            base_url="https://test.collibra.com",
            username="testuser",
            password="testpass"
        )

        assert client.base_url == "https://test.collibra.com"
        assert client.auth == ("testuser", "testpass")
        assert client.session is not None

    def test_base_url_trailing_slash_removed(self):
        """Test that trailing slash is removed from base URL"""
        client = CollibraClient(
            base_url="https://test.collibra.com/",
            username="user",
            password="pass"
        )

        assert client.base_url == "https://test.collibra.com"
        assert not client.base_url.endswith('/')

    def test_headers_json_constant(self):
        """Test HEADERS_JSON constant"""
        assert CollibraClient.HEADERS_JSON == {"Accept": "application/json"}

    def test_headers_content_json_constant(self):
        """Test HEADERS_CONTENT_JSON constant"""
        assert CollibraClient.HEADERS_CONTENT_JSON == {"Content-Type": "application/json"}

    def test_default_limit_constant(self):
        """Test DEFAULT_LIMIT constant"""
        assert CollibraClient.DEFAULT_LIMIT == 1000
        assert isinstance(CollibraClient.DEFAULT_LIMIT, int)


class TestDetermineOutputFile:
    """Unit tests for determine_output_file function"""

    def test_with_custom_output_specified(self):
        """Test with custom output file"""
        args = Mock()
        args.output = "my-custom-file.yaml"
        odcs_data = {"name": "Test Contract"}

        result = determine_output_file(args, odcs_data)
        assert result == "my-custom-file.yaml"

    def test_from_contract_name(self):
        """Test output file from contract name"""
        args = Mock()
        args.output = None
        odcs_data = {"name": "Customer Transactions"}

        result = determine_output_file(args, odcs_data)
        assert result == "customer-transactions-odcs.yaml"

    def test_name_with_spaces(self):
        """Test name with spaces is converted to hyphens"""
        args = Mock()
        args.output = None
        odcs_data = {"name": "My Test Contract"}

        result = determine_output_file(args, odcs_data)
        assert result == "my-test-contract-odcs.yaml"
        assert " " not in result

    def test_name_with_uppercase(self):
        """Test name is converted to lowercase"""
        args = Mock()
        args.output = None
        odcs_data = {"name": "CUSTOMER_TABLE"}

        result = determine_output_file(args, odcs_data)
        assert result == "customer_table-odcs.yaml"
        assert result.islower() or "_" in result

    def test_default_when_no_name(self):
        """Test default output file when no name"""
        args = Mock()
        args.output = None
        odcs_data = {}

        result = determine_output_file(args, odcs_data)
        assert result == "asset-odcs.yaml"

    def test_name_with_special_characters(self):
        """Test name with special characters"""
        args = Mock()
        args.output = None
        odcs_data = {"name": "Test/Table\\Name"}

        result = determine_output_file(args, odcs_data)
        # Should handle special characters gracefully
        assert result.endswith("-odcs.yaml")

    def test_empty_name(self):
        """Test with empty name string"""
        args = Mock()
        args.output = None
        odcs_data = {"name": ""}

        result = determine_output_file(args, odcs_data)
        # Should use default when name is empty
        assert result.endswith("-odcs.yaml")


class TestODCSGeneratorInitialization:
    """Unit tests for ODCSGenerator initialization"""

    def test_generator_requires_client(self):
        """Test that generator requires a client"""
        mock_client = Mock(spec=CollibraClient)
        generator = ODCSGenerator(mock_client)

        assert generator.client == mock_client

    def test_generator_stores_client_reference(self):
        """Test that generator stores client reference"""
        mock_client = Mock(spec=CollibraClient)
        mock_client.base_url = "https://test.com"

        generator = ODCSGenerator(mock_client)

        assert generator.client.base_url == "https://test.com"


class TestODCSGeneratorValidation:
    """Unit tests for ODCSGenerator validation"""

    def test_generate_odcs_requires_asset_id(self):
        """Test that generate_odcs requires asset ID"""
        mock_client = Mock(spec=CollibraClient)
        generator = ODCSGenerator(mock_client)

        with pytest.raises(ValueError, match="Asset ID is required"):
            generator.generate_odcs("")

    def test_generate_odcs_rejects_none_asset_id(self):
        """Test that generate_odcs rejects None asset ID"""
        mock_client = Mock(spec=CollibraClient)
        generator = ODCSGenerator(mock_client)

        with pytest.raises((ValueError, TypeError)):
            generator.generate_odcs(None)

    def test_generate_odcs_accepts_valid_asset_id(self):
        """Test that generate_odcs accepts valid asset ID"""
        mock_client = Mock(spec=CollibraClient)
        mock_client.get_asset.return_value = {
            "id": "test-id",
            "displayName": "Test",
            "type": {"name": "Table"},
            "domain": {"name": "Domain"},
            "createdOn": 0
        }
        mock_client.get_asset_tags.return_value = []
        mock_client.get_asset_attributes.return_value = []
        mock_client.get_asset_relations.return_value = []
        mock_client.base_url = "https://test.com"

        generator = ODCSGenerator(mock_client)

        # Should not raise an error
        result = generator.generate_odcs("valid-asset-id")
        assert result is not None


class TestODCSStructureValidation:
    """Unit tests for ODCS structure validation"""

    def test_odcs_has_required_fields(self):
        """Test that generated ODCS has required fields"""
        mock_client = Mock(spec=CollibraClient)
        mock_client.get_asset.return_value = {
            "id": "test-id",
            "displayName": "Test Table",
            "type": {"name": "Table"},
            "domain": {"name": "Finance"},
            "createdOn": 1609459200000
        }
        mock_client.get_asset_tags.return_value = []
        mock_client.get_asset_attributes.return_value = []
        mock_client.get_asset_relations.return_value = []
        mock_client.base_url = "https://test.com"

        generator = ODCSGenerator(mock_client)
        odcs = generator.generate_odcs("test-id")

        # Check required ODCS fields
        required_fields = [
            'id', 'kind', 'apiVersion', 'domain', 'dataProduct',
            'version', 'name', 'status', 'contractCreatedTs',
            'description', 'tags', 'schema', 'servers'
        ]

        for field in required_fields:
            assert field in odcs, f"Missing required field: {field}"

    def test_odcs_kind_is_data_contract(self):
        """Test that ODCS kind is DataContract"""
        mock_client = Mock(spec=CollibraClient)
        mock_client.get_asset.return_value = {
            "id": "test-id",
            "displayName": "Test",
            "type": {"name": "Table"},
            "domain": {"name": "Domain"},
            "createdOn": 0
        }
        mock_client.get_asset_tags.return_value = []
        mock_client.get_asset_attributes.return_value = []
        mock_client.get_asset_relations.return_value = []
        mock_client.base_url = "https://test.com"

        generator = ODCSGenerator(mock_client)
        odcs = generator.generate_odcs("test-id")

        assert odcs["kind"] == "DataContract"

    def test_odcs_api_version(self):
        """Test that ODCS has correct API version"""
        mock_client = Mock(spec=CollibraClient)
        mock_client.get_asset.return_value = {
            "id": "test-id",
            "displayName": "Test",
            "type": {"name": "Table"},
            "domain": {"name": "Domain"},
            "createdOn": 0
        }
        mock_client.get_asset_tags.return_value = []
        mock_client.get_asset_attributes.return_value = []
        mock_client.get_asset_relations.return_value = []
        mock_client.base_url = "https://test.com"

        generator = ODCSGenerator(mock_client)
        odcs = generator.generate_odcs("test-id")

        assert odcs["apiVersion"] == "v3.1.0"


class TestCollibraClientAPIMethods:
    """Unit tests for CollibraClient API methods with mocked responses"""

    @patch('wxdi.odcs_generator.generate_odcs_from_collibra.requests.Session.get')
    def test_get_asset_success(self, mock_get):
        """Test successful asset retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "asset-123",
            "displayName": "Test Table",
            "type": {"name": "Table"},
            "domain": {"name": "Finance"}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = CollibraClient(
            "https://test.collibra.com",
            "testuser",
            "testpass"
        )

        result = client.get_asset("asset-123")

        assert result["id"] == "asset-123"
        assert result["displayName"] == "Test Table"
        mock_get.assert_called_once()

    @patch('wxdi.odcs_generator.generate_odcs_from_collibra.requests.Session.get')
    def test_get_asset_attributes_success(self, mock_get):
        """Test successful asset attributes retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"type": {"name": "Description"}, "value": "Test description"},
                {"type": {"name": "Owner"}, "value": "John Doe"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = CollibraClient(
            "https://test.collibra.com",
            "testuser",
            "testpass"
        )

        result = client.get_asset_attributes("asset-123")

        assert len(result) == 2
        assert result[0]["type"]["name"] == "Description"
        mock_get.assert_called_once()

    @patch('wxdi.odcs_generator.generate_odcs_from_collibra.requests.Session.get')
    def test_get_asset_tags_success(self, mock_get):
        """Test successful asset tags retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"name": "PII"},
            {"name": "Sensitive"}
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = CollibraClient(
            "https://test.collibra.com",
            "testuser",
            "testpass"
        )

        result = client.get_asset_tags("asset-123")

        assert len(result) == 2
        assert result[0] == "PII"
        mock_get.assert_called_once()

    @patch('wxdi.odcs_generator.generate_odcs_from_collibra.requests.Session.get')
    def test_get_asset_relations_success(self, mock_get):
        """Test successful asset relations retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "type": {"role": "target"},
                    "target": {
                        "id": "col-1",
                        "name": "customer_id",
                        "type": {"name": "Column"}
                    }
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = CollibraClient(
            "https://test.collibra.com",
            "testuser",
            "testpass"
        )

        result = client.get_asset_relations("asset-123")

        assert len(result) == 1
        assert result[0]["target"]["name"] == "customer_id"
        mock_get.assert_called_once()

class TestParseAndValidateArgumentsCollibra:
    """Unit tests for Collibra argument parsing and validation"""

    @patch('sys.argv', ['script.py', 'asset-123', '--url', 'https://test.collibra.com', '-u', 'user', '-p', 'pass'])
    def test_parse_arguments_all_provided(self):
        """Test parsing with all arguments provided"""
        from wxdi.odcs_generator.generate_odcs_from_collibra import parse_arguments

        args = parse_arguments()

        assert args.asset_id == 'asset-123'
        assert args.url == 'https://test.collibra.com'
        assert args.username == 'user'
        assert args.password == 'pass'

    @patch('sys.argv', ['script.py', 'asset-123', '-o', 'output.yaml'])
    @patch.dict(os.environ, {
        'COLLIBRA_URL': 'https://env.collibra.com',
        'COLLIBRA_USERNAME': 'envuser',
        'COLLIBRA_PASSWORD': 'envpass'  # pragma: allowlist secret
    })
    def test_parse_arguments_from_env(self):
        """Test parsing with environment variables"""
        from wxdi.odcs_generator.generate_odcs_from_collibra import parse_arguments

        args = parse_arguments()

        assert args.asset_id == 'asset-123'
        assert args.output == 'output.yaml'
        assert args.url == 'https://env.collibra.com'
        assert args.username == 'envuser'
        assert args.password == 'envpass'

    def test_validate_arguments_missing_url(self):
        """Test validation fails with missing URL"""
        from wxdi.odcs_generator.generate_odcs_from_collibra import validate_arguments

        args = Mock()
        args.url = None
        args.username = 'user'
        args.password = 'pass'

        with pytest.raises(SystemExit):
            validate_arguments(args)

    def test_validate_arguments_missing_username(self):
        """Test validation fails with missing username"""
        from wxdi.odcs_generator.generate_odcs_from_collibra import validate_arguments

        args = Mock()
        args.url = 'https://test.com'
        args.username = None
        args.password = 'pass'

        with pytest.raises(SystemExit):
            validate_arguments(args)

    def test_validate_arguments_missing_password(self):
        """Test validation fails with missing password"""
        from wxdi.odcs_generator.generate_odcs_from_collibra import validate_arguments

        args = Mock()
        args.url = 'https://test.com'
        args.username = 'user'
        args.password = None

        with pytest.raises(SystemExit):
            validate_arguments(args)

    def test_validate_arguments_all_present(self):
        """Test validation passes with all arguments"""
        from wxdi.odcs_generator.generate_odcs_from_collibra import validate_arguments

        args = Mock()
        args.url = 'https://test.com'
        args.username = 'user'
        args.password = 'pass'

        # Should not raise an exception
        validate_arguments(args)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

