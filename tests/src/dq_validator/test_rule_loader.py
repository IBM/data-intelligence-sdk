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
Test suite for RuleLoader module
"""

import pytest
import json
from pathlib import Path
from wxdi.dq_validator.rule_loader import RuleLoader
from wxdi.dq_validator.metadata import AssetMetadata, ColumnMetadata, DataType
from wxdi.dq_validator.validator import Validator
from wxdi.dq_validator.provider.response_model import (
    GlossaryTerm,
    Metadata,
    GlossaryTermEntity,
    ExtendedAttributeGroups,
)
from wxdi.dq_validator.provider.constraint_model import (
    DataQualityConstraint,
    ConstraintMetadata,
    CheckConstraint,
    CheckType,
)
from wxdi.dq_validator.provider.data_asset_model import DataAsset
from datetime import datetime


class TestRuleLoader:
    """Test cases for RuleLoader class"""

    @pytest.fixture
    def base_url(self):
        """Base URL for API"""
        return "https://api.example.com"

    @pytest.fixture
    def auth_token(self):
        """Authentication token"""
        return "test-token-12345"

    @pytest.fixture
    def rule_loader(self, base_url, auth_token):
        """Create RuleLoader instance"""
        return RuleLoader(base_url, auth_token)

    @pytest.fixture
    def asset_metadata(self):
        """Create sample asset metadata"""
        columns = [
            ColumnMetadata("id", DataType.INTEGER),
            ColumnMetadata("name", DataType.STRING, length=100),
            ColumnMetadata("age", DataType.INTEGER),
        ]
        return AssetMetadata("users", columns)

    @pytest.fixture
    def mock_glossary_term_basic(self):
        """Create a basic glossary term without DQ constraints"""
        return GlossaryTerm(
            metadata=Metadata(
                artifact_type="glossary_term",
                artifact_id="term-123",
                version_id="version-456",
                source_repository_id="repo-789",
                global_id="global-123",
                effective_start_date=datetime(2026, 1, 1),
                created_by="user1",
                created_at=datetime(2026, 1, 1),
                modified_by="user1",
                modified_at=datetime(2026, 1, 1),
                revision="0",
                state="PUBLISHED",
            ),
            entity=GlossaryTermEntity(
                abbreviations=[],
                state="PUBLISHED",
                default_locale_id="en-US",
                reference_copy=False,
                steward_ids=[],
                steward_group_ids=[],
                custom_relationships=[],
                custom_attributes=[],
            ),
        )

    @pytest.fixture
    def mock_glossary_term_with_constraints(self):
        """Create a glossary term with DQ constraints"""
        # Create completeness constraint
        completeness_constraint = DataQualityConstraint(
            metadata=ConstraintMetadata(type=CheckType.COMPLETENESS),
            origin=[],
            check=[CheckConstraint(name="missing_values_allowed", boolean_value=False)],
        )

        # Create range constraint
        range_constraint = DataQualityConstraint(
            metadata=ConstraintMetadata(type=CheckType.RANGE),
            origin=[],
            check=[
                CheckConstraint(name="min", numeric_value=0),
                CheckConstraint(name="max", numeric_value=120),
            ],
        )

        # Create data type constraint
        datatype_constraint = DataQualityConstraint(
            metadata=ConstraintMetadata(type=CheckType.DATA_TYPE),
            origin=[],
            check=[
                CheckConstraint(name="data_type", value="integer"),
                CheckConstraint(name="length", numeric_value=10),
            ],
        )

        return GlossaryTerm(
            metadata=Metadata(
                artifact_type="glossary_term",
                artifact_id="term-123",
                version_id="version-456",
                source_repository_id="repo-789",
                global_id="global-123",
                effective_start_date=datetime(2026, 1, 1),
                created_by="user1",
                created_at=datetime(2026, 1, 1),
                modified_by="user1",
                modified_at=datetime(2026, 1, 1),
                revision="0",
                state="PUBLISHED",
            ),
            entity=GlossaryTermEntity(
                abbreviations=[],
                state="PUBLISHED",
                default_locale_id="en-US",
                reference_copy=False,
                steward_ids=[],
                steward_group_ids=[],
                custom_relationships=[],
                custom_attributes=[],
                extended_attribute_groups=ExtendedAttributeGroups(
                    dq_constraints=[
                        completeness_constraint,
                        range_constraint,
                        datatype_constraint,
                    ]
                ),
            ),
        )

    def test_rule_loader_initialization(self, base_url, auth_token):
        """Test RuleLoader initialization"""
        loader = RuleLoader(base_url, auth_token)
        assert loader.base_url == base_url
        assert loader.auth_token == auth_token

    def test_load_from_glossary_no_version_id(
        self, rule_loader, asset_metadata, mocker
    ):
        """Test load_from_glossary raises ValueError when no version_id"""
        # Mock the provider to return a term without version_id
        mock_term = mocker.Mock()
        mock_term.metadata.version_id = None

        mock_provider = mocker.patch("wxdi.dq_validator.rule_loader.GlossaryProvider")
        mock_provider.return_value.get_published_artifact_by_id.return_value = mock_term

        with pytest.raises(ValueError, match="No version_id found"):
            rule_loader.load_from_glossary("term-123", "age", asset_metadata)

    def test_load_from_glossary_no_constraints(
        self, rule_loader, asset_metadata, mock_glossary_term_basic, mocker
    ):
        """Test load_from_glossary with no DQ constraints"""
        mock_provider = mocker.patch("wxdi.dq_validator.rule_loader.GlossaryProvider")
        mock_provider.return_value.get_published_artifact_by_id.return_value = (
            mock_glossary_term_basic
        )
        mock_provider.return_value.get_term_by_version_id.return_value = (
            mock_glossary_term_basic
        )

        validator = rule_loader.load_from_glossary("term-123", "age", asset_metadata)

        assert isinstance(validator, Validator)
        assert validator.metadata == asset_metadata
        assert len(validator.rules) == 0

    def test_load_from_glossary_with_constraints(
        self,
        rule_loader,
        asset_metadata,
        mock_glossary_term_basic,
        mock_glossary_term_with_constraints,
        mocker,
    ):
        """Test load_from_glossary with DQ constraints"""
        mock_provider = mocker.patch("wxdi.dq_validator.rule_loader.GlossaryProvider")
        mock_provider.return_value.get_published_artifact_by_id.return_value = (
            mock_glossary_term_basic
        )
        mock_provider.return_value.get_term_by_version_id.return_value = (
            mock_glossary_term_with_constraints
        )

        validator = rule_loader.load_from_glossary("term-123", "age", asset_metadata)

        assert isinstance(validator, Validator)
        assert validator.metadata == asset_metadata
        assert len(validator.rules) == 1

        rule = validator.rules[0]
        assert rule.column_name == "age"
        assert len(rule.checks) == 3

    def test_load_from_glossary_provider_config(
        self, rule_loader, asset_metadata, mock_glossary_term_basic, mocker
    ):
        """Test that GlossaryProvider is initialized with correct config"""
        mock_provider_class = mocker.patch("wxdi.dq_validator.rule_loader.GlossaryProvider")
        mock_provider_config = mocker.patch("wxdi.dq_validator.rule_loader.ProviderConfig")

        mock_provider_instance = mocker.Mock()
        mock_provider_instance.get_published_artifact_by_id.return_value = (
            mock_glossary_term_basic
        )
        mock_provider_instance.get_term_by_version_id.return_value = (
            mock_glossary_term_basic
        )
        mock_provider_class.return_value = mock_provider_instance

        rule_loader.load_from_glossary("term-123", "age", asset_metadata)

        # Verify ProviderConfig was called with correct parameters
        mock_provider_config.assert_called_once_with(
            rule_loader.base_url, rule_loader.auth_token
        )

        # Verify GlossaryProvider was initialized with the config
        mock_provider_class.assert_called_once()

    def test_load_from_glossary_api_calls(
        self,
        rule_loader,
        asset_metadata,
        mock_glossary_term_basic,
        mock_glossary_term_with_constraints,
        mocker,
    ):
        """Test that correct API calls are made"""
        mock_provider = mocker.patch("wxdi.dq_validator.rule_loader.GlossaryProvider")
        mock_instance = mock_provider.return_value

        mock_instance.get_published_artifact_by_id.return_value = (
            mock_glossary_term_basic
        )
        mock_instance.get_term_by_version_id.return_value = (
            mock_glossary_term_with_constraints
        )

        rule_loader.load_from_glossary("term-123", "age", asset_metadata)

        # Verify get_published_artifact_by_id was called
        mock_instance.get_published_artifact_by_id.assert_called_once_with("term-123")

        # Verify get_term_by_version_id was called with correct parameters
        mock_instance.get_term_by_version_id.assert_called_once_with(
            "term-123",
            "version-456",
            {"included_extended_attribute_groups": "dq_constraints"},
        )

    def test_load_from_glossary_constraint_filtering(
        self,
        rule_loader,
        asset_metadata,
        mock_glossary_term_basic,
        mocker,
    ):
        """Test that None checks are filtered out"""
        # Create a constraint with unsupported type that returns None from to_check()
        unsupported_constraint = DataQualityConstraint(
            metadata=ConstraintMetadata(type=CheckType.UNIQUENESS),  # Not supported
            origin=[],
            check=[],
        )

        mock_term_with_none = GlossaryTerm(
            metadata=mock_glossary_term_basic.metadata,
            entity=GlossaryTermEntity(
                abbreviations=[],
                state="PUBLISHED",
                default_locale_id="en-US",
                reference_copy=False,
                steward_ids=[],
                steward_group_ids=[],
                custom_relationships=[],
                custom_attributes=[],
                extended_attribute_groups=ExtendedAttributeGroups(
                    dq_constraints=[unsupported_constraint]
                ),
            ),
        )

        mock_provider = mocker.patch("wxdi.dq_validator.rule_loader.GlossaryProvider")
        mock_provider.return_value.get_published_artifact_by_id.return_value = (
            mock_glossary_term_basic
        )
        mock_provider.return_value.get_term_by_version_id.return_value = (
            mock_term_with_none
        )

        validator = rule_loader.load_from_glossary("term-123", "age", asset_metadata)

        # Should have no rules since the constraint returned None
        assert len(validator.rules) == 0


class TestRuleLoaderCams:
    """Test cases for RuleLoader.load_from_cams method"""

    @pytest.fixture
    def base_url(self):
        """Base URL for API"""
        return "https://api.example.com"

    @pytest.fixture
    def auth_token(self):
        """Authentication token"""
        return "test-token-12345"

    @pytest.fixture
    def project_id(self):
        """Project ID"""
        return "72d21c1d-499b-4784-a3c7-6f84507f9a20"

    @pytest.fixture
    def rule_loader(self, base_url, auth_token):
        """Create RuleLoader instance"""
        return RuleLoader(base_url, auth_token)

    @pytest.fixture
    def data_asset_json(self):
        """Load the data asset response JSON"""
        json_path = Path(__file__).parent.parent.parent / "data" / "data_asset_response.json"
        with open(json_path, "r") as f:
            return json.load(f)

    @pytest.fixture
    def mock_data_asset(self, data_asset_json):
        """Create DataAsset from JSON"""
        return DataAsset.from_dict(data_asset_json)

    def test_load_from_cams_with_auto_metadata(
        self, rule_loader, project_id, mock_data_asset, mocker
    ):
        """Test load_from_cams with automatic metadata extraction"""
        mock_provider = mocker.patch("wxdi.dq_validator.rule_loader.CamsProvider")
        mock_provider.return_value.get_asset_by_id.return_value = mock_data_asset

        validator = rule_loader.load_from_cams(
            "6862f3ba-81f5-4122-8286-62bb4c5d6543", project_id
        )

        assert isinstance(validator, Validator)
        assert validator.metadata.table_name == "DEPARTMENT"
        assert len(validator.metadata.columns) == 5

        # Check column names
        column_names = [col.name for col in validator.metadata.columns]
        assert "DEPTNO" in column_names
        assert "DEPTNAME" in column_names
        assert "MGRNO" in column_names
        assert "ADMRDEPT" in column_names
        assert "LOCATION" in column_names

    def test_load_from_cams_with_provided_metadata(
        self, rule_loader, project_id, mock_data_asset, mocker
    ):
        """Test load_from_cams with user-provided metadata"""
        mock_provider = mocker.patch("wxdi.dq_validator.rule_loader.CamsProvider")
        mock_provider.return_value.get_asset_by_id.return_value = mock_data_asset

        # Provide custom metadata
        custom_metadata = AssetMetadata(
            "CUSTOM_TABLE",
            [
                ColumnMetadata("DEPTNO", DataType.STRING, length=3),
                ColumnMetadata("DEPTNAME", DataType.STRING, length=36),
            ],
        )

        validator = rule_loader.load_from_cams(
            "6862f3ba-81f5-4122-8286-62bb4c5d6543", project_id, custom_metadata
        )

        assert isinstance(validator, Validator)
        assert validator.metadata.table_name == "CUSTOM_TABLE"
        assert len(validator.metadata.columns) == 2

    def test_load_from_cams_rules_created(
        self, rule_loader, project_id, mock_data_asset, mocker
    ):
        """Test that validation rules are created from column checks"""
        mock_provider = mocker.patch("wxdi.dq_validator.rule_loader.CamsProvider")
        mock_provider.return_value.get_asset_by_id.return_value = mock_data_asset

        validator = rule_loader.load_from_cams(
            "6862f3ba-81f5-4122-8286-62bb4c5d6543", project_id
        )

        # Should have rules for columns with checks
        # DEPTNO has 4 checks, MGRNO has 3, ADMRDEPT has 3, DEPTNAME has 3
        # LOCATION has 0 checks
        assert len(validator.rules) == 4

        # Check that rules are for the correct columns
        rule_columns = [rule.column_name for rule in validator.rules]
        assert "DEPTNO" in rule_columns
        assert "MGRNO" in rule_columns
        assert "ADMRDEPT" in rule_columns
        assert "DEPTNAME" in rule_columns
        assert "LOCATION" not in rule_columns  # No checks for this column

    def test_load_from_cams_check_types(
        self, rule_loader, project_id, mock_data_asset, mocker
    ):
        """Test that different check types are correctly loaded"""
        mock_provider = mocker.patch("wxdi.dq_validator.rule_loader.CamsProvider")
        mock_provider.return_value.get_asset_by_id.return_value = mock_data_asset

        validator = rule_loader.load_from_cams(
            "6862f3ba-81f5-4122-8286-62bb4c5d6543", project_id
        )

        # Find DEPTNO rule (has format, uniqueness, completeness, data_class checks)
        deptno_rule = next(r for r in validator.rules if r.column_name == "DEPTNO")
        # Note: uniqueness and data_class checks return None, so only 2 checks should be added
        assert len(deptno_rule.checks) == 2

        # Find DEPTNAME rule (has uniqueness, completeness, case checks)
        deptname_rule = next(
            r for r in validator.rules if r.column_name == "DEPTNAME"
        )
        # Note: uniqueness check returns None, so only 2 checks should be added
        assert len(deptname_rule.checks) == 2

    def test_load_from_cams_provider_config(
        self, rule_loader, project_id, mock_data_asset, mocker
    ):
        """Test that CamsProvider is initialized with correct config"""
        mock_provider_class = mocker.patch("wxdi.dq_validator.rule_loader.CamsProvider")
        mock_provider_config = mocker.patch("wxdi.dq_validator.rule_loader.ProviderConfig")

        mock_provider_instance = mocker.Mock()
        mock_provider_instance.get_asset_by_id.return_value = mock_data_asset
        mock_provider_class.return_value = mock_provider_instance

        rule_loader.load_from_cams(
            "6862f3ba-81f5-4122-8286-62bb4c5d6543", project_id
        )

        # Verify ProviderConfig was called with correct parameters
        mock_provider_config.assert_called_once_with(
            rule_loader.base_url, rule_loader.auth_token, project_id=project_id
        )

    def test_load_from_cams_column_metadata_extraction(
        self, rule_loader, project_id, mock_data_asset, mocker
    ):
        """Test that column metadata is correctly extracted from data asset"""
        mock_provider = mocker.patch("wxdi.dq_validator.rule_loader.CamsProvider")
        mock_provider.return_value.get_asset_by_id.return_value = mock_data_asset

        validator = rule_loader.load_from_cams(
            "6862f3ba-81f5-4122-8286-62bb4c5d6543", project_id
        )

        # Check DEPTNO column metadata (uses inferred type)
        deptno_col = validator.metadata.get_column("DEPTNO")
        assert deptno_col.name == "DEPTNO"
        assert deptno_col.data_type == DataType.STRING
        assert deptno_col.length == 3
        assert deptno_col.nullable is False

        # Check MGRNO column metadata (uses inferred type INT8 -> INTEGER)
        mgrno_col = validator.metadata.get_column("MGRNO")
        assert mgrno_col.name == "MGRNO"
        assert mgrno_col.data_type == DataType.INTEGER
        assert mgrno_col.length == 6
        assert mgrno_col.precision == 3
        assert mgrno_col.nullable is True

    def test_load_from_cams_type_conversion(
        self, rule_loader, project_id, mock_data_asset, mocker
    ):
        """Test CAMS type to DataType conversion"""
        mock_provider = mocker.patch("wxdi.dq_validator.rule_loader.CamsProvider")
        mock_provider.return_value.get_asset_by_id.return_value = mock_data_asset

        validator = rule_loader.load_from_cams(
            "6862f3ba-81f5-4122-8286-62bb4c5d6543", project_id
        )

        # Check various type conversions
        # STRING type (from inferred type)
        deptno_col = validator.metadata.get_column("DEPTNO")
        assert deptno_col.data_type == DataType.STRING

        # INTEGER type (from INT8 inferred type)
        mgrno_col = validator.metadata.get_column("MGRNO")
        assert mgrno_col.data_type == DataType.INTEGER

    def test_load_from_cams_skips_unsupported_checks(
        self, rule_loader, project_id, mock_data_asset, mocker
    ):
        """Test that unsupported check types are skipped"""
        mock_provider = mocker.patch("wxdi.dq_validator.rule_loader.CamsProvider")
        mock_provider.return_value.get_asset_by_id.return_value = mock_data_asset

        validator = rule_loader.load_from_cams(
            "6862f3ba-81f5-4122-8286-62bb4c5d6543", project_id
        )

        # DEPTNO has uniqueness and data_class checks which return None
        # So it should have 2 checks instead of 4
        deptno_rule = next(r for r in validator.rules if r.column_name == "DEPTNO")
        assert len(deptno_rule.checks) == 2

    def test_load_from_cams_column_without_checks(
        self, rule_loader, project_id, mock_data_asset, mocker
    ):
        """Test that columns without checks don't create rules"""
        mock_provider = mocker.patch("wxdi.dq_validator.rule_loader.CamsProvider")
        mock_provider.return_value.get_asset_by_id.return_value = mock_data_asset

        validator = rule_loader.load_from_cams(
            "6862f3ba-81f5-4122-8286-62bb4c5d6543", project_id
        )

        # LOCATION has no checks, so no rule should be created
        location_rules = [r for r in validator.rules if r.column_name == "LOCATION"]
        assert len(location_rules) == 0


# Made with Bob
