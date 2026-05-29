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
Unit Tests for Informatica ODCS Generator
Tests individual functions and methods in isolation
"""

import pytest
import os
from unittest.mock import Mock, patch
from wxdi.odcs_generator.generate_odcs_from_informatica import (
    InformaticaClient,
    extract_column_position,
    build_physical_type,
    build_column_property,
    build_custom_properties,
    generate_odcs_yaml,
    determine_output_file,
    RESOURCE_TYPE_MAPPING,
    SYSTEM_ATTRIBUTES_MAPPING
)


class TestExtractColumnPosition:
    """Unit tests for extract_column_position function"""

    def test_valid_position_as_string(self):
        """Test extraction with valid position as string"""
        col_data = {"selfAttributes": {"core.Position": "5"}}
        assert extract_column_position(col_data) == 5

    def test_valid_position_as_int(self):
        """Test extraction with valid position as integer"""
        col_data = {"selfAttributes": {"core.Position": 10}}
        assert extract_column_position(col_data) == 10

    def test_missing_self_attributes(self):
        """Test with missing selfAttributes"""
        col_data = {}
        assert extract_column_position(col_data) == 999999

    def test_missing_position_key(self):
        """Test with missing Position key"""
        col_data = {"selfAttributes": {}}
        assert extract_column_position(col_data) == 999999

    def test_none_position_value(self):
        """Test with None position value"""
        col_data = {"selfAttributes": {"core.Position": None}}
        assert extract_column_position(col_data) == 999999

    def test_invalid_position_string(self):
        """Test with invalid position string"""
        col_data = {"selfAttributes": {"core.Position": "invalid"}}
        assert extract_column_position(col_data) == 999999

    def test_empty_position_string(self):
        """Test with empty position string"""
        col_data = {"selfAttributes": {"core.Position": ""}}
        assert extract_column_position(col_data) == 999999

    def test_negative_position(self):
        """Test with negative position"""
        col_data = {"selfAttributes": {"core.Position": "-1"}}
        assert extract_column_position(col_data) == -1


class TestBuildPhysicalType:
    """Unit tests for build_physical_type function"""

    def test_type_without_length(self):
        """Test type without length or scale"""
        assert build_physical_type("INTEGER", "", "") == "INTEGER"
        assert build_physical_type("TIMESTAMP", None, None) == "TIMESTAMP"

    def test_type_with_length_only(self):
        """Test type with length but no scale"""
        assert build_physical_type("VARCHAR", "255", "") == "VARCHAR(255)"
        assert build_physical_type("CHAR", "10", None) == "CHAR(10)"

    def test_type_with_length_and_scale(self):
        """Test type with both length and scale"""
        assert build_physical_type("DECIMAL", "10", "2") == "DECIMAL(10,2)"
        assert build_physical_type("NUMBER", "18", "4") == "NUMBER(18,4)"

    def test_type_with_length_and_zero_scale(self):
        """Test type with length and scale of 0"""
        assert build_physical_type("NUMBER", "18", "0") == "NUMBER(18)"
        assert build_physical_type("DECIMAL", "10", "0") == "DECIMAL(10)"

    def test_type_with_empty_strings(self):
        """Test with empty strings for length and scale"""
        assert build_physical_type("VARCHAR", "", "") == "VARCHAR"

    def test_various_data_types(self):
        """Test with various common data types"""
        assert build_physical_type("BIGINT", "", "") == "BIGINT"
        assert build_physical_type("TEXT", "", "") == "TEXT"
        assert build_physical_type("BOOLEAN", "", "") == "BOOLEAN"
        assert build_physical_type("DATE", "", "") == "DATE"


class TestBuildColumnProperty:
    """Unit tests for build_column_property function"""

    def test_basic_column_property(self):
        """Test building basic column property"""
        column_detail = {
            "summary": {
                "core.name": "customer_id"
            },
            "selfAttributes": {
                "com.infa.odin.models.relational.Datatype": "INTEGER"
            }
        }

        prop = build_column_property(column_detail)

        assert prop["name"] == "customer_id"
        assert prop["physicalType"] == "INTEGER"
        assert prop["required"] is False  # Default when Nullable not specified (nullable=true by default)

    def test_column_with_description(self):
        """Test column with description"""
        column_detail = {
            "summary": {
                "core.name": "email",
                "core.description": "Customer email address"
            },
            "selfAttributes": {
                "com.infa.odin.models.relational.Datatype": "VARCHAR",
                "com.infa.odin.models.relational.DatatypeLength": "255"
            }
        }

        prop = build_column_property(column_detail)

        assert prop["name"] == "email"
        assert prop["physicalType"] == "VARCHAR(255)"
        assert prop["description"] == "Customer email address"

    def test_nullable_column(self):
        """Test nullable column"""
        column_detail = {
            "summary": {"core.name": "middle_name"},
            "selfAttributes": {
                "com.infa.odin.models.relational.Datatype": "VARCHAR",
                "com.infa.odin.models.relational.DatatypeLength": "50",
                "com.infa.odin.models.relational.Nullable": "true"
            }
        }

        prop = build_column_property(column_detail)

        assert prop["required"] is False

    def test_non_nullable_column(self):
        """Test non-nullable column"""
        column_detail = {
            "summary": {"core.name": "id"},
            "selfAttributes": {
                "com.infa.odin.models.relational.Datatype": "INTEGER",
                "com.infa.odin.models.relational.Nullable": "false"
            }
        }

        prop = build_column_property(column_detail)

        assert prop["required"] is True

    def test_primary_key_column(self):
        """Test primary key column"""
        column_detail = {
            "summary": {"core.name": "id"},
            "selfAttributes": {
                "com.infa.odin.models.relational.Datatype": "INTEGER",
                "com.infa.odin.models.relational.PrimaryKeyColumn": "true"
            }
        }

        prop = build_column_property(column_detail)

        assert prop.get("primaryKey") is True

    def test_non_primary_key_column(self):
        """Test non-primary key column"""
        column_detail = {
            "summary": {"core.name": "name"},
            "selfAttributes": {
                "com.infa.odin.models.relational.Datatype": "VARCHAR",
                "com.infa.odin.models.relational.PrimaryKeyColumn": "false"
            }
        }

        prop = build_column_property(column_detail)

        assert "primaryKey" not in prop or prop.get("primaryKey") is False

    def test_decimal_column_with_scale(self):
        """Test decimal column with precision and scale"""
        column_detail = {
            "summary": {"core.name": "price"},
            "selfAttributes": {
                "com.infa.odin.models.relational.Datatype": "DECIMAL",
                "com.infa.odin.models.relational.DatatypeLength": "10",
                "com.infa.odin.models.relational.DatatypeScale": "2"
            }
        }

        prop = build_column_property(column_detail)

        assert prop["physicalType"] == "DECIMAL(10,2)"

    def test_column_without_description(self):
        """Test that description is not added when empty"""
        column_detail = {
            "summary": {"core.name": "col1"},
            "selfAttributes": {
                "com.infa.odin.models.relational.Datatype": "INTEGER"
            }
        }

        prop = build_column_property(column_detail)

        assert "description" not in prop


class TestBuildCustomProperties:
    """Unit tests for build_custom_properties function"""

    def test_empty_attributes(self):
        """Test with empty attributes"""
        assert build_custom_properties({}) == []

    def test_single_attribute(self):
        """Test with single attribute"""
        attrs = {"core.resourceName": "TestCatalog"}
        props = build_custom_properties(attrs)

        assert len(props) == 1
        assert props[0]["property"] == "Catalog Source Name"
        assert props[0]["value"] == "TestCatalog"

    def test_multiple_attributes(self):
        """Test with multiple attributes"""
        attrs = {
            "core.resourceName": "TestCatalog",
            "com.infa.odin.models.relational.NumberOfRows": "1000",
            "core.origin": "Production"
        }
        props = build_custom_properties(attrs)

        assert len(props) == 3
        property_names = [p["property"] for p in props]
        assert "Catalog Source Name" in property_names
        assert "Number of rows" in property_names
        assert "Origin" in property_names

    def test_unmapped_attributes_ignored(self):
        """Test that unmapped attributes are ignored"""
        attrs = {
            "core.resourceName": "TestCatalog",
            "unmapped.attribute": "SomeValue"
        }
        props = build_custom_properties(attrs)

        assert len(props) == 1
        assert props[0]["property"] == "Catalog Source Name"

    def test_all_system_attributes(self):
        """Test with all system attributes"""
        attrs = {
            "core.resourceName": "Catalog1",
            "com.infa.odin.models.relational.NumberOfRows": "5000",
            "core.origin": "Prod",
            "com.infa.odin.models.relational.Owner": "dbo",
            "core.sourceCreatedBy": "admin",
            "core.sourceCreatedOn": "2024-01-01",
            "core.sourceModifiedBy": "user1",
            "core.sourceModifiedOn": "2024-02-01"
        }
        props = build_custom_properties(attrs)

        assert len(props) == 8


class TestGenerateOdcsYaml:
    """Unit tests for generate_odcs_yaml function"""

    def test_basic_odcs_structure(self):
        """Test basic ODCS structure generation"""
        asset_data = {
            "core.identity": "test-id",
            "summary": {"core.name": "TEST_TABLE"},
            "selfAttributes": {
                "core.businessName": "test_table",
                "com.infa.odin.models.relational.Owner": "public"
            }
        }
        column_details = []
        base_url = "https://cdgc.test.com"

        odcs = generate_odcs_yaml(asset_data, column_details, base_url)

        assert odcs["id"] == "test-id"
        assert odcs["kind"] == "DataContract"
        assert odcs["apiVersion"] == "v3.1.0"
        assert odcs["status"] == "active"
        assert "contractCreatedTs" in odcs

    def test_schema_with_columns(self):
        """Test schema generation with columns"""
        asset_data = {
            "core.identity": "test-id",
            "summary": {"core.name": "CUSTOMER"},
            "selfAttributes": {
                "core.name": "customer",
                "com.infa.odin.models.relational.Owner": "dbo"
            }
        }
        column_details = [
            {
                "summary": {"core.name": "id"},
                "selfAttributes": {
                    "com.infa.odin.models.relational.Datatype": "INTEGER",
                    "core.Position": "1"
                }
            }
        ]
        base_url = "https://cdgc.test.com"

        odcs = generate_odcs_yaml(asset_data, column_details, base_url)

        assert len(odcs["schema"]) == 1
        assert odcs["schema"][0]["name"] == "customer"
        assert len(odcs["schema"][0]["properties"]) == 1
        assert odcs["schema"][0]["properties"][0]["name"] == "id"

    def test_physical_name_construction(self):
        """Test physical name construction with schema"""
        asset_data = {
            "core.identity": "test-id",
            "summary": {"core.name": "TABLE1"},
            "selfAttributes": {
                "core.name": "table1",
                "com.infa.odin.models.relational.Owner": "schema1"
            }
        }
        column_details = []
        base_url = "https://cdgc.test.com"

        odcs = generate_odcs_yaml(asset_data, column_details, base_url)

        assert odcs["schema"][0]["physicalName"] == "schema1/table1"

    def test_server_type_mapping(self):
        """Test server type mapping from resource type"""
        asset_data = {
            "core.identity": "test-id",
            "summary": {"core.name": "TABLE1"},
            "selfAttributes": {
                "core.businessName": "table1",
                "core.resourceType": "Snowflake",
                "com.infa.odin.models.relational.Owner": "public"
            }
        }
        column_details = []
        base_url = "https://cdgc.test.com"

        odcs = generate_odcs_yaml(asset_data, column_details, base_url)

        assert odcs["servers"][0]["type"] == "snowflake"

    def test_authoritative_definition(self):
        """Test authoritative definition URL"""
        asset_data = {
            "core.identity": "asset-123",
            "summary": {"core.name": "TABLE1"},
            "selfAttributes": {"core.businessName": "table1"}
        }
        column_details = []
        base_url = "https://cdgc.test.com"

        odcs = generate_odcs_yaml(asset_data, column_details, base_url)

        auth_defs = odcs["description"]["authoritativeDefinitions"]
        assert len(auth_defs) == 1
        assert auth_defs[0]["type"] == "informatica-asset"
        assert "asset-123" in auth_defs[0]["url"]


class TestDetermineOutputFile:
    """Unit tests for determine_output_file function"""

    def test_with_custom_output(self):
        """Test with custom output file specified"""
        args = Mock()
        args.output = "custom-file.yaml"
        odcs_data = {"name": "Test"}

        result = determine_output_file(args, odcs_data)
        assert result == "custom-file.yaml"

    def test_from_asset_name(self):
        """Test output file from asset name"""
        args = Mock()
        args.output = None
        odcs_data = {"name": "Customer Transactions"}

        result = determine_output_file(args, odcs_data)
        assert result == "customer-transactions-odcs.yaml"

    def test_default_name(self):
        """Test default output file name"""
        args = Mock()
        args.output = None
        odcs_data = {}

        result = determine_output_file(args, odcs_data)
        assert result == "asset-odcs.yaml"

    def test_name_with_special_characters(self):
        """Test name with special characters"""
        args = Mock()
        args.output = None
        odcs_data = {"name": "Test Table (Production)"}

        result = determine_output_file(args, odcs_data)
        assert result == "test-table-(production)-odcs.yaml"


class TestResourceTypeMapping:
    """Unit tests for RESOURCE_TYPE_MAPPING constant"""

    def test_common_databases_mapped(self):
        """Test that common database types are mapped"""
        assert RESOURCE_TYPE_MAPPING["Snowflake"] == "snowflake"
        assert RESOURCE_TYPE_MAPPING["PostgreSQL"] == "postgresql"
        assert RESOURCE_TYPE_MAPPING["Oracle"] == "oracle"
        assert RESOURCE_TYPE_MAPPING["SqlServer"] == "sqlserver"

    def test_cloud_databases_mapped(self):
        """Test that cloud database types are mapped"""
        assert RESOURCE_TYPE_MAPPING["BigQuery"] == "bigquery"
        assert RESOURCE_TYPE_MAPPING["Redshift"] == "redshift"
        assert RESOURCE_TYPE_MAPPING["Databricks"] == "databricks"
        assert RESOURCE_TYPE_MAPPING["Synapse"] == "synapse"

    def test_mapping_count(self):
        """Test that expected number of mappings exist"""
        assert len(RESOURCE_TYPE_MAPPING) >= 13


class TestSystemAttributesMapping:
    """Unit tests for SYSTEM_ATTRIBUTES_MAPPING constant"""

    def test_core_attributes_mapped(self):
        """Test that core attributes are mapped"""
        assert "core.resourceName" in SYSTEM_ATTRIBUTES_MAPPING
        assert "core.origin" in SYSTEM_ATTRIBUTES_MAPPING

    def test_relational_attributes_mapped(self):
        """Test that relational model attributes are mapped"""
        assert "com.infa.odin.models.relational.NumberOfRows" in SYSTEM_ATTRIBUTES_MAPPING
        assert "com.infa.odin.models.relational.Owner" in SYSTEM_ATTRIBUTES_MAPPING

    def test_timestamp_attributes_mapped(self):
        """Test that timestamp attributes are mapped"""
        assert "core.sourceCreatedOn" in SYSTEM_ATTRIBUTES_MAPPING
        assert "core.sourceModifiedOn" in SYSTEM_ATTRIBUTES_MAPPING

    def test_user_attributes_mapped(self):
        """Test that user attributes are mapped"""
        assert "core.sourceCreatedBy" in SYSTEM_ATTRIBUTES_MAPPING
        assert "core.sourceModifiedBy" in SYSTEM_ATTRIBUTES_MAPPING


class TestInformaticaClientUnit:
    """Unit tests for InformaticaClient class methods"""

    def test_extract_region_from_standard_url(self):
        """Test region extraction from standard URL"""
        client = InformaticaClient(
            "https://cdgc.dm-us.informaticacloud.com",
            "user",
            "pass"
        )
        assert client.region == "dm-us"

    def test_extract_region_from_various_formats(self):
        """Test region extraction from various URL formats"""
        test_cases = [
            ("https://cdgc.na1.informaticacloud.com", "na1"),
            ("https://cdgc.eu1.informaticacloud.com/", "eu1"),
            ("https://cdgc.ap1.informaticacloud.com", "ap1"),
        ]

        for url, expected_region in test_cases:
            client = InformaticaClient(url, "user", "pass")
            assert client.region == expected_region

    def test_identity_url_construction(self):
        """Test identity URL construction"""
        client = InformaticaClient(
            "https://cdgc.dm-us.informaticacloud.com",
            "user",
            "pass"
        )
        assert client.identity_url == "https://dm-us.informaticacloud.com"

    def test_base_url_normalization(self):
        """Test that base URL trailing slash is removed"""
        client = InformaticaClient(
            "https://cdgc.test.com/",
            "user",
            "pass"
        )
        assert client.base_url == "https://cdgc.test.com"


class TestInformaticaClientAPIMethods:
    """Unit tests for InformaticaClient API methods with mocked responses"""

    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.requests.post')
    def test_get_session_id_success(self, mock_post):
        """Test successful session ID retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {"sessionId": "test-session-123"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = InformaticaClient(
            "https://cdgc.dm-us.informaticacloud.com",
            "testuser",
            "testpass"
        )

        result = client.get_session_id()

        assert result["sessionId"] == "test-session-123"
        mock_post.assert_called_once()

    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.requests.post')
    def test_get_auth_token_success(self, mock_post):
        """Test successful auth token retrieval"""
        # Mock session ID call
        mock_session_response = Mock()
        mock_session_response.json.return_value = {"sessionId": "session-123"}
        mock_session_response.raise_for_status = Mock()

        # Mock JWT token call
        mock_jwt_response = Mock()
        mock_jwt_response.json.return_value = {"jwt_token": "jwt-token-456"}
        mock_jwt_response.raise_for_status = Mock()

        mock_post.side_effect = [mock_session_response, mock_jwt_response]

        client = InformaticaClient(
            "https://cdgc.dm-us.informaticacloud.com",
            "testuser",
            "testpass"
        )

        token = client.get_auth_token()

        assert token == "jwt-token-456"
        assert mock_post.call_count == 2

    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.requests.post')
    def test_get_auth_token_caching(self, mock_post):
        """Test that auth token is cached"""
        mock_session_response = Mock()
        mock_session_response.json.return_value = {"sessionId": "session-123"}
        mock_session_response.raise_for_status = Mock()

        mock_jwt_response = Mock()
        mock_jwt_response.json.return_value = {"jwt_token": "jwt-token-456"}
        mock_jwt_response.raise_for_status = Mock()

        mock_post.side_effect = [mock_session_response, mock_jwt_response]

        client = InformaticaClient(
            "https://cdgc.dm-us.informaticacloud.com",
            "testuser",
            "testpass"
        )

        # First call
        token1 = client.get_auth_token()
        # Second call should use cached token
        token2 = client.get_auth_token()

        assert token1 == token2
        # Should only call API twice (session + jwt), not four times
        assert mock_post.call_count == 2

    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.requests.get')
    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.requests.post')
    def test_get_asset_details_success(self, mock_post, mock_get):
        """Test successful asset details retrieval"""
        # Mock auth calls
        mock_session_response = Mock()
        mock_session_response.json.return_value = {"sessionId": "session-123"}
        mock_session_response.raise_for_status = Mock()

        mock_jwt_response = Mock()
        mock_jwt_response.json.return_value = {"jwt_token": "jwt-token-456"}
        mock_jwt_response.raise_for_status = Mock()

        mock_post.side_effect = [mock_session_response, mock_jwt_response]

        # Mock asset details call
        mock_asset_response = Mock()
        mock_asset_response.json.return_value = {
            "core.identity": "asset-123",
            "summary": {"core.name": "TEST_TABLE"}
        }
        mock_asset_response.raise_for_status = Mock()
        mock_get.return_value = mock_asset_response

        client = InformaticaClient(
            "https://cdgc.dm-us.informaticacloud.com",
            "testuser",
            "testpass"
        )

        result = client.get_asset_details("asset-123")

        assert result["core.identity"] == "asset-123"
        assert result["summary"]["core.name"] == "TEST_TABLE"
        mock_get.assert_called_once()

    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.requests.get')
    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.requests.post')
    def test_get_column_details_success(self, mock_post, mock_get):
        """Test successful column details retrieval"""
        # Mock auth calls
        mock_session_response = Mock()
        mock_session_response.json.return_value = {"sessionId": "session-123"}
        mock_session_response.raise_for_status = Mock()

        mock_jwt_response = Mock()
        mock_jwt_response.json.return_value = {"jwt_token": "jwt-token-456"}
        mock_jwt_response.raise_for_status = Mock()

        mock_post.side_effect = [mock_session_response, mock_jwt_response]

        # Mock column details call
        mock_column_response = Mock()
        mock_column_response.json.return_value = {
            "summary": {"core.name": "customer_id"},
            "selfAttributes": {"com.infa.odin.models.relational.Datatype": "INTEGER"}
        }
        mock_column_response.raise_for_status = Mock()
        mock_get.return_value = mock_column_response

        client = InformaticaClient(
            "https://cdgc.dm-us.informaticacloud.com",
            "testuser",
            "testpass"
        )

        result = client.get_column_details("column-456")

        assert result["summary"]["core.name"] == "customer_id"
        mock_get.assert_called_once()


class TestParseAndValidateArguments:
    """Unit tests for argument parsing and validation"""

    @patch('sys.argv', ['script.py', 'asset-123', '--cdgc-url', 'https://test.com', '-u', 'user', '-p', 'pass'])
    def test_parse_arguments_all_provided(self):
        """Test parsing with all arguments provided"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import parse_arguments

        args = parse_arguments()

        assert args.asset_id == 'asset-123'
        assert args.cdgc_url == 'https://test.com'
        assert args.username == 'user'
        assert args.password == 'pass'

    @patch('sys.argv', ['script.py', 'asset-123', '-o', 'output.yaml'])
    @patch.dict(os.environ, {
        'INFORMATICA_CDGC_URL': 'https://env.com',
        'INFORMATICA_USERNAME': 'envuser',
        'INFORMATICA_PASSWORD': 'envpass'  # pragma: allowlist secret
    })
    def test_parse_arguments_from_env(self):
        """Test parsing with environment variables"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import parse_arguments

        args = parse_arguments()

        assert args.asset_id == 'asset-123'
        assert args.output == 'output.yaml'
        assert args.cdgc_url == 'https://env.com'
        assert args.username == 'envuser'
        assert args.password == 'envpass'

    def test_validate_arguments_missing_url(self):
        """Test validation fails with missing URL"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import validate_arguments

        args = Mock()
        args.cdgc_url = None
        args.username = 'user'
        args.password = 'pass'

        with pytest.raises(SystemExit):
            validate_arguments(args)

    def test_validate_arguments_missing_username(self):
        """Test validation fails with missing username"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import validate_arguments

        args = Mock()
        args.cdgc_url = 'https://test.com'
        args.username = None
        args.password = 'pass'

        with pytest.raises(SystemExit):
            validate_arguments(args)

    def test_validate_arguments_missing_password(self):
        """Test validation fails with missing password"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import validate_arguments

        args = Mock()
        args.cdgc_url = 'https://test.com'
        args.username = 'user'
        args.password = None

        with pytest.raises(SystemExit):
            validate_arguments(args)

    def test_validate_arguments_all_present(self):
        """Test validation passes with all arguments"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import validate_arguments

        args = Mock()
        args.cdgc_url = 'https://test.com'
        args.username = 'user'
        args.password = 'pass'

        # Should not raise an exception


class TestGenerateODCSYAML:
    """Test cases for generate_odcs_yaml function"""

    def test_generate_odcs_yaml_with_description(self):
        """Test ODCS generation with table description"""
        asset_data = {
            'core.identity': 'table-123',
            'summary': {
                'core.name': 'test_table',
                'core.description': 'Test table description'
            },
            'selfAttributes': {
                'core.businessName': 'TestTable',
                'com.infa.odin.models.relational.Owner': 'test_schema',
                'core.resourceType': 'Snowflake'
            }
        }

        column_details = [
            {
                'core.identity': 'col-1',
                'summary': {'core.name': 'id'},
                'selfAttributes': {
                    'com.infa.odin.models.relational.Datatype': 'INTEGER',
                    'com.infa.odin.models.relational.Nullable': 'false',
                    'com.infa.odin.models.relational.PrimaryKeyColumn': 'true'
                }
            }
        ]

        result = generate_odcs_yaml(asset_data, column_details, 'https://test.com')

        assert result['id'] == 'table-123'
        assert result['schema'][0]['description'] == 'Test table description'
        assert result['schema'][0]['properties'][0]['primaryKey'] is True
        assert result['servers'][0]['type'] == 'snowflake'

    def test_generate_odcs_yaml_without_description(self):
        """Test ODCS generation without table description"""
        asset_data = {
            'core.identity': 'table-456',
            'summary': {'core.name': 'test_table'},
            'selfAttributes': {
                'core.businessName': 'TestTable',
                'com.infa.odin.models.relational.Owner': 'test_schema'
            }
        }

        column_details = []

        result = generate_odcs_yaml(asset_data, column_details, 'https://test.com')

        assert 'description' not in result['schema'][0]


class TestHelperFunctions:
    """Test cases for helper functions"""

    def test_add_server_warning_comments(self):
        """Test _add_server_warning_comments function"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import _add_server_warning_comments

        modified_lines = []
        _add_server_warning_comments(modified_lines, '  - id: server-123')

        assert len(modified_lines) == 5
        assert '⚠️  MANUAL CONFIGURATION REQUIRED' in modified_lines[1]

    def test_add_inline_comment_server(self):
        """Test _add_inline_comment_if_needed for server field"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import _add_inline_comment_if_needed

        line = '  server: CONFIGURE_SERVER_HOSTNAME'
        result = _add_inline_comment_if_needed(line)
        assert '⚠️ UPDATE' in result
        assert 'prod.snowflake.acme.com' in result

    def test_add_inline_comment_type(self):
        """Test _add_inline_comment_if_needed for type field"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import _add_inline_comment_if_needed

        line = '  type: CONFIGURE_SERVER_TYPE'
        result = _add_inline_comment_if_needed(line)
        assert '⚠️ UPDATE' in result
        assert 'snowflake' in result

    def test_add_inline_comment_schema(self):
        """Test _add_inline_comment_if_needed for schema field"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import _add_inline_comment_if_needed

        line = '  schema: CONFIGURE_SCHEMA_NAME'
        result = _add_inline_comment_if_needed(line)
        assert '⚠️ UPDATE' in result
        assert 'public' in result

    def test_add_inline_comment_no_change(self):
        """Test _add_inline_comment_if_needed for normal line"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import _add_inline_comment_if_needed

        line = '  name: test'
        result = _add_inline_comment_if_needed(line)
        assert result == line

    def test_determine_output_file_with_arg(self):
        """Test determine_output_file with output argument"""
        args = Mock()
        args.output = 'custom.yaml'
        odcs_data = {'name': 'test'}

        result = determine_output_file(args, odcs_data)
        assert result == 'custom.yaml'

    def test_determine_output_file_default(self):
        """Test determine_output_file with default naming"""
        args = Mock()
        args.output = None
        odcs_data = {'name': 'Test Table'}

        result = determine_output_file(args, odcs_data)
        assert result == 'test-table-odcs.yaml'


class TestWriteYAMLFile:
    """Test cases for write_yaml_file function"""

    @patch('builtins.open', create=True)
    @patch('builtins.print')
    def test_write_yaml_file(self, mock_print, mock_open_func):
        """Test write_yaml_file function"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import write_yaml_file

        mock_file = Mock()
        mock_open_func.return_value.__enter__.return_value = mock_file

        odcs_data = {
            'id': 'test-123',
            'servers': [
                {
                    'id': 'server-1',
                    'server': 'CONFIGURE_SERVER_HOSTNAME',
                    'type': 'CONFIGURE_SERVER_TYPE',
                    'schema': 'CONFIGURE_SCHEMA_NAME'
                }
            ]
        }

        write_yaml_file('test.yaml', odcs_data)

        mock_open_func.assert_called_once_with('test.yaml', 'w')
        mock_print.assert_called()


class TestMainFunction:
    """Test cases for main function"""

    @patch('sys.argv', ['script.py', 'asset-123', '--cdgc-url', 'https://test.com',
                        '-u', 'user', '-p', 'pass'])
    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.InformaticaClient')
    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.write_yaml_file')
    @patch('builtins.print')
    def test_main_success(self, mock_print, mock_write, mock_client_class):
        """Test main function success path"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import main

        # Mock client instance
        mock_client = Mock()
        mock_client.base_url = 'https://test.com'
        mock_client.get_asset_details.return_value = {
            'core.identity': 'asset-123',
            'summary': {'core.name': 'test_table'},
            'selfAttributes': {'core.businessName': 'TestTable'},
            'hierarchy': [{'core.identity': 'col-1'}]
        }
        mock_client.get_column_details.return_value = {
            'core.identity': 'col-1',
            'summary': {'core.name': 'id'},
            'selfAttributes': {
                'com.infa.odin.models.relational.Datatype': 'INTEGER',
                'com.infa.odin.models.relational.Position': '1'
            }
        }
        mock_client_class.return_value = mock_client

        main()

        mock_client.get_asset_details.assert_called_once_with('asset-123')
        mock_write.assert_called_once()

    @patch('sys.argv', ['script.py', 'asset-123', '--cdgc-url', 'https://test.com',
                        '-u', 'user', '-p', 'pass'])
    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.InformaticaClient')
    @patch('sys.exit')
    def test_main_http_401_error(self, mock_exit, mock_client_class):
        """Test main function with 401 HTTP error"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import main
        import requests

        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 401
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_client.get_asset_details.side_effect = http_error
        mock_client_class.return_value = mock_client

        main()

        mock_exit.assert_called_once_with(1)

    @patch('sys.argv', ['script.py', 'asset-123', '--cdgc-url', 'https://test.com',
                        '-u', 'user', '-p', 'pass'])
    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.InformaticaClient')
    @patch('sys.exit')
    def test_main_http_404_error(self, mock_exit, mock_client_class):
        """Test main function with 404 HTTP error"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import main
        import requests

        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_client.get_asset_details.side_effect = http_error
        mock_client_class.return_value = mock_client

        main()

        mock_exit.assert_called_once_with(1)

    @patch('sys.argv', ['script.py', 'asset-123', '--cdgc-url', 'https://test.com',
                        '-u', 'user', '-p', 'pass'])
    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.InformaticaClient')
    @patch('sys.exit')
    def test_main_connection_error(self, mock_exit, mock_client_class):
        """Test main function with connection error"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import main
        import requests

        mock_client = Mock()
        mock_client.get_asset_details.side_effect = requests.exceptions.ConnectionError()
        mock_client_class.return_value = mock_client

        main()

        mock_exit.assert_called_once_with(1)

    @patch('sys.argv', ['script.py', 'asset-123', '--cdgc-url', 'https://test.com',
                        '-u', 'user', '-p', 'pass'])
    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.InformaticaClient')
    @patch('sys.exit')
    def test_main_timeout_error(self, mock_exit, mock_client_class):
        """Test main function with timeout error"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import main
        import requests

        mock_client = Mock()
        mock_client.get_asset_details.side_effect = requests.exceptions.Timeout()
        mock_client_class.return_value = mock_client

        main()

        mock_exit.assert_called_once_with(1)

    @patch('sys.argv', ['script.py', 'asset-123', '--cdgc-url', 'https://test.com',
                        '-u', 'user', '-p', 'pass'])
    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.InformaticaClient')
    @patch('sys.exit')
    def test_main_key_error(self, mock_exit, mock_client_class):
        """Test main function with KeyError"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import main

        mock_client = Mock()
        mock_client.get_asset_details.side_effect = KeyError('missing_field')
        mock_client_class.return_value = mock_client

        main()

        mock_exit.assert_called_once_with(1)

    @patch('sys.argv', ['script.py', 'asset-123', '--cdgc-url', 'https://test.com',
                        '-u', 'user', '-p', 'pass'])
    @patch('wxdi.odcs_generator.generate_odcs_from_informatica.InformaticaClient')
    @patch('sys.exit')
    def test_main_unexpected_error(self, mock_exit, mock_client_class):
        """Test main function with unexpected error"""
        from wxdi.odcs_generator.generate_odcs_from_informatica import main

        mock_client = Mock()
        mock_client.get_asset_details.side_effect = ValueError('unexpected error')
        mock_client_class.return_value = mock_client

        main()

        mock_exit.assert_called_once_with(1)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

