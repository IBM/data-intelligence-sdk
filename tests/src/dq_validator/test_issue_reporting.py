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
Tests for IssueReporter utility.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from wxdi.dq_validator.issue_reporting import IssueReporter
from wxdi.dq_validator.provider import ProviderConfig
from wxdi.dq_validator import Validator, ValidationRule, AssetMetadata, ColumnMetadata
from wxdi.dq_validator.checks import (
    FormatCheck, CompletenessCheck, ComparisonCheck, 
    LengthCheck, RangeCheck, RegexCheck, CaseCheck,
    DataTypeCheck, ValidValuesCheck
)
from wxdi.dq_validator.metadata import DataType
from wxdi.dq_validator.checks.comparison_check import ComparisonOperator
from wxdi.dq_validator.data_quality_dimension import DataQualityDimension


@pytest.fixture
def config():
    """Create a test configuration."""
    return ProviderConfig(
        url="https://test-instance.com",
        auth_token="Bearer test-token",
        project_id="project-123"
    )


@pytest.fixture
def reporter(config):
    """Create a test IssueReporter instance with mocked providers."""
    with patch('wxdi.dq_validator.issue_reporting.ChecksProvider'), \
         patch('wxdi.dq_validator.issue_reporting.IssuesProvider'), \
         patch('wxdi.dq_validator.issue_reporting.DimensionsProvider'), \
         patch('wxdi.dq_validator.issue_reporting.DQAssetsProvider'), \
         patch('wxdi.dq_validator.issue_reporting.CamsProvider'), \
         patch('wxdi.dq_validator.issue_reporting.DQSearchProvider'):
        reporter = IssueReporter(config)
        yield reporter


@pytest.fixture
def sample_validator():
    """Create a sample validator for testing"""
    metadata = AssetMetadata('test_table', [
        ColumnMetadata('email', DataType.STRING),
        ColumnMetadata('name', DataType.STRING),
        ColumnMetadata('age', DataType.INTEGER),
        ColumnMetadata('salary', DataType.FLOAT)
    ])
    validator = Validator(metadata)
    validator.add_rule(ValidationRule('email').add_check(FormatCheck(formats={'email'})))
    validator.add_rule(ValidationRule('name').add_check(CompletenessCheck()).add_check(LengthCheck(min_length=2)))
    validator.add_rule(ValidationRule('age').add_check(RangeCheck(min_value=0, max_value=120)))
    validator.add_rule(ValidationRule('salary').add_check(ComparisonCheck(
        operator=ComparisonOperator.GREATER_THAN,
        target_column='min_salary'
    )))
    return validator


class TestIssueReporterInitialization:
    """Test IssueReporter initialization"""
    
    def test_init_creates_all_providers(self, config):
        """Test that initialization creates all required providers."""
        with patch('wxdi.dq_validator.issue_reporting.ChecksProvider') as mock_checks, \
             patch('wxdi.dq_validator.issue_reporting.IssuesProvider') as mock_issues, \
             patch('wxdi.dq_validator.issue_reporting.DimensionsProvider') as mock_dimensions, \
             patch('wxdi.dq_validator.issue_reporting.DQAssetsProvider') as mock_assets, \
             patch('wxdi.dq_validator.issue_reporting.DQSearchProvider') as mock_search, \
             patch('wxdi.dq_validator.issue_reporting.CamsProvider') as mock_cams:
            
            reporter = IssueReporter(config)
            
            # Verify all providers were created with correct config
            mock_checks.assert_called_once_with(config)
            mock_issues.assert_called_once_with(config)
            mock_dimensions.assert_called_once_with(config)
            mock_assets.assert_called_once_with(config)
            mock_search.assert_called_once_with(config)
            mock_cams.assert_called_once_with(config)
            
            # Verify config is stored
            assert reporter.config == config
            
            # Verify all provider attributes exist
            assert hasattr(reporter, 'check_provider')
            assert hasattr(reporter, 'issues_provider')
            assert hasattr(reporter, 'dimension_provider')
            assert hasattr(reporter, 'asset_provider')
            assert hasattr(reporter, 'search_provider')
            assert hasattr(reporter, 'cams_provider')


class TestMapCheckNameToCheckType:
    """Test map_check_name_to_check_type static method"""
    
    def test_format_check(self):
        """Test mapping format_check to check type."""
        result = IssueReporter.map_check_name_to_check_type("format_check")
        assert result == "format"
    
    def test_completeness_check(self):
        """Test mapping completeness_check to check type."""
        result = IssueReporter.map_check_name_to_check_type("completeness_check")
        assert result == "completeness"
    
    def test_comparison_check(self):
        """Test mapping comparison_check to check type."""
        result = IssueReporter.map_check_name_to_check_type("comparison_check")
        assert result == "comparison"
    
    def test_valid_values_check(self):
        """Test mapping valid_values_check to check type."""
        result = IssueReporter.map_check_name_to_check_type("valid_values_check")
        assert result == "possible_values"
    
    def test_unknown_check(self):
        """Test mapping unknown check name returns None."""
        result = IssueReporter.map_check_name_to_check_type("unknown_check")
        assert result is None


class TestMapCheckNameToCpdName:
    """Test map_check_name_to_cpd_name static method"""
    
    def test_format_check(self):
        """Test mapping format_check to CPD name."""
        result = IssueReporter.map_check_name_to_cpd_name("format_check")
        assert result == "Format check"
    
    def test_completeness_check(self):
        """Test mapping completeness_check to CPD name."""
        result = IssueReporter.map_check_name_to_cpd_name("completeness_check")
        assert result == "Completeness check"
    
    def test_case_check(self):
        """Test mapping case_check to CPD name."""
        result = IssueReporter.map_check_name_to_cpd_name("case_check")
        assert result == "Capitalization style check"
    
    def test_valid_values_check(self):
        """Test mapping valid_values_check to CPD name."""
        result = IssueReporter.map_check_name_to_cpd_name("valid_values_check")
        assert result == "Possible values check"
    
    def test_unknown_check(self):
        """Test mapping unknown check name returns None."""
        result = IssueReporter.map_check_name_to_cpd_name("unknown_check")
        assert result is None


class TestGetCheckFromValidator:
    """Test get_check_from_validator static method"""
    
    def test_get_check_found(self, sample_validator):
        """Test getting check from validator when it exists."""
        check = IssueReporter.get_check_from_validator(
            sample_validator,
            "email",
            "format_check"
        )
        
        assert check is not None
        assert isinstance(check, FormatCheck)
        assert check.get_check_name() == "format_check"
    
    def test_get_completeness_check(self, sample_validator):
        """Test getting completeness check."""
        check = IssueReporter.get_check_from_validator(
            sample_validator,
            "name",
            "completeness_check"
        )
        
        assert check is not None
        assert isinstance(check, CompletenessCheck)
    
    def test_get_range_check(self, sample_validator):
        """Test getting range check."""
        check = IssueReporter.get_check_from_validator(
            sample_validator,
            "age",
            "range_check"
        )
        
        assert check is not None
        assert isinstance(check, RangeCheck)
    
    def test_get_comparison_check(self, sample_validator):
        """Test getting comparison check."""
        check = IssueReporter.get_check_from_validator(
            sample_validator,
            "salary",
            "comparison_check"
        )
        
        assert check is not None
        assert isinstance(check, ComparisonCheck)
    
    def test_check_not_found_wrong_column(self, sample_validator):
        """Test getting check with wrong column name."""
        check = IssueReporter.get_check_from_validator(
            sample_validator,
            "nonexistent_column",
            "format_check"
        )
        
        assert check is None
    
    def test_check_not_found_wrong_check_name(self, sample_validator):
        """Test getting check with wrong check name."""
        check = IssueReporter.get_check_from_validator(
            sample_validator,
            "email",
            "nonexistent_check"
        )
        
        assert check is None
    
    def test_multiple_checks_on_column(self, sample_validator):
        """Test getting specific check when column has multiple checks."""
        # name column has both completeness and length checks
        completeness_check = IssueReporter.get_check_from_validator(
            sample_validator,
            "name",
            "completeness_check"
        )
        length_check = IssueReporter.get_check_from_validator(
            sample_validator,
            "name",
            "length_check"
        )
        
        assert completeness_check is not None
        assert isinstance(completeness_check, CompletenessCheck)
        assert length_check is not None
        assert isinstance(length_check, LengthCheck)
    
    def test_empty_validator(self):
        """Test with validator that has no rules."""
        metadata = AssetMetadata('empty_table', [
            ColumnMetadata('col1', DataType.STRING)
        ])
        empty_validator = Validator(metadata)
        
        check = IssueReporter.get_check_from_validator(
            empty_validator,
            "col1",
            "format_check"
        )
        
        assert check is None


class TestGetCheckId:
    """Test get_check_id method"""
    
    def test_get_check_id_success(self, reporter):
        """Test successful check ID retrieval."""
        reporter.search_provider.search_dq_check = Mock(return_value={
            "id": "check-id-123",
            "native_id": "asset-id/column/check-type",
            "type": "format"
        })
        
        result = reporter.get_check_id(
            check_native_id="asset-id/column/check-type",
            check_type="format",
            project_id="project-123"
        )
        
        assert result == "check-id-123"
        reporter.search_provider.search_dq_check.assert_called_once_with(
            native_id="asset-id/column/check-type",
            check_type="format",
            project_id="project-123",
            catalog_id=None
        )
    
    def test_get_check_id_with_catalog_id(self, reporter):
        """Test check ID retrieval with catalog_id."""
        reporter.search_provider.search_dq_check = Mock(return_value={
            "id": "check-id-456"
        })
        
        result = reporter.get_check_id(
            check_native_id="asset-id/column/check-type",
            check_type="completeness",
            catalog_id="catalog-789"
        )
        
        assert result == "check-id-456"
        reporter.search_provider.search_dq_check.assert_called_once_with(
            native_id="asset-id/column/check-type",
            check_type="completeness",
            project_id=None,
            catalog_id="catalog-789"
        )
    
    def test_get_check_id_not_found(self, reporter):
        """Test check ID retrieval when check not found."""
        reporter.search_provider.search_dq_check = Mock(side_effect=ValueError("Not found"))
        
        result = reporter.get_check_id(
            check_native_id="nonexistent",
            check_type="format",
            project_id="project-123"
        )
        
        assert result is None
    
    def test_get_check_id_exception_handling(self, reporter):
        """Test that exceptions are caught and None is returned."""
        reporter.search_provider.search_dq_check = Mock(side_effect=Exception("Unexpected error"))
        
        result = reporter.get_check_id(
            check_native_id="asset-id/column/check",
            check_type="format",
            project_id="project-123"
        )
        
        assert result is None
    
    def test_get_check_id_missing_id_in_response(self, reporter):
        """Test when response doesn't contain 'id' field."""
        reporter.search_provider.search_dq_check = Mock(return_value={
            "native_id": "asset-id/column/check-type"
            # Missing 'id' field
        })
        
        result = reporter.get_check_id(
            check_native_id="asset-id/column/check-type",
            check_type="format",
            project_id="project-123"
        )
        
        assert result is None


class TestCreateCheck:
    """Test create_check method"""
    
    def test_create_check_format(self, reporter, sample_validator):
        """Test creating a format check."""
        # Setup mocks
        reporter.dimension_provider.search_dimension = Mock(return_value="dimension-id-123")
        reporter.check_provider._create_check_full = Mock(return_value={
            "id": "check-id-456",
            "name": "Format check",
            "type": "format",
            "native_id": "asset-789/format/Validity"
        })
        
        # Get the format check from validator
        format_check = IssueReporter.get_check_from_validator(
            sample_validator, "email", "format_check"
        )
        
        # Execute
        result = reporter.create_check(
            asset_id="asset-789",
            column_name="email",
            check_obj=format_check,
            project_id="project-123"
        )
        
        # Verify - now returns dict
        assert isinstance(result, dict)
        assert result["id"] == "check-id-456"
        
        # Verify dimension search was called
        reporter.dimension_provider.search_dimension.assert_called_once()
        
        # Verify check creation was called with correct parameters
        reporter.check_provider._create_check_full.assert_called_once()
        call_args = reporter.check_provider._create_check_full.call_args
        assert call_args[1]['name'] == "Format check"
        assert call_args[1]['dimension_id'] == "dimension-id-123"
        # When parent_check_id is None, native_id format is: asset_id/check_type/DimensionName
        assert "asset-789/format/Validity" in call_args[1]['native_id']
        assert call_args[1]['check_type'] == "format"
        assert call_args[1]['project_id'] == "project-123"
    
    def test_create_check_completeness(self, reporter, sample_validator):
        """Test creating a completeness check."""
        reporter.dimension_provider.search_dimension = Mock(return_value="dimension-id-comp")
        reporter.check_provider._create_check_full = Mock(return_value={
            "id": "check-id-comp",
            "name": "Completeness check",
            "type": "completeness",
            "native_id": "asset-999/completeness/Completeness"
        })
        
        completeness_check = IssueReporter.get_check_from_validator(
            sample_validator, "name", "completeness_check"
        )
        
        result = reporter.create_check(
            asset_id="asset-999",
            column_name="name",
            check_obj=completeness_check,
            project_id="project-456"
        )
        
        assert isinstance(result, dict)
        assert result["id"] == "check-id-comp"
        
        call_args = reporter.check_provider._create_check_full.call_args
        assert call_args[1]['name'] == "Completeness check"
        assert call_args[1]['check_type'] == "completeness"
        # When parent_check_id is None, native_id format is: asset_id/check_type/DimensionName
        assert "asset-999/completeness/Completeness" in call_args[1]['native_id']
    
    def test_create_check_comparison_with_target_column(self, reporter, sample_validator):
        """Test creating a comparison check with target column and parent_id."""
        reporter.dimension_provider.search_dimension = Mock(return_value="dimension-id-comp")
        reporter.check_provider._create_check_full = Mock(return_value={
            "id": "check-id-comparison",
            "name": "Comparison check",
            "type": "comparison",
            "native_id": "asset-comp/comparison/salary/greaterThan/min_salary"
        })
        
        comparison_check = IssueReporter.get_check_from_validator(
            sample_validator, "salary", "comparison_check"
        )
        
        result = reporter.create_check(
            asset_id="asset-comp",
            column_name="salary",
            check_obj=comparison_check,
            project_id="project-789",
            parent_id="parent-check-id"  # Need parent_id for column name in native_id
        )
        
        assert isinstance(result, dict)
        assert result["id"] == "check-id-comparison"
        
        call_args = reporter.check_provider._create_check_full.call_args
        # When parent_id is provided, native_id includes column name and operator details
        native_id = call_args[1]['native_id']
        assert "asset-comp/comparison/salary/" in native_id
        assert "greaterThan" in native_id
        assert "min_salary" in native_id
        assert call_args[1]['parent_check_id'] == "parent-check-id"
    
    def test_create_check_with_catalog_id(self, reporter, sample_validator):
        """Test creating a check with catalog_id instead of project_id."""
        reporter.dimension_provider.search_dimension = Mock(return_value="dimension-id-cat")
        reporter.check_provider._create_check_full = Mock(return_value={
            "id": "check-id-cat",
            "name": "Format check",
            "type": "format"
        })
        
        format_check = IssueReporter.get_check_from_validator(
            sample_validator, "email", "format_check"
        )
        
        result = reporter.create_check(
            asset_id="asset-cat",
            column_name="email",
            check_obj=format_check,
            catalog_id="catalog-999"
        )
        
        assert isinstance(result, dict)
        assert result["id"] == "check-id-cat"
        
        call_args = reporter.check_provider._create_check_full.call_args
        assert call_args[1]['catalog_id'] == "catalog-999"
        assert call_args[1]['project_id'] is None
    
    def test_create_check_lowercase_column_name(self, reporter, sample_validator):
        """Test that column name is converted to lowercase in native_id when parent_id is provided."""
        reporter.dimension_provider.search_dimension = Mock(return_value="dim-id")
        reporter.check_provider._create_check_full = Mock(return_value={
            "id": "check-id",
            "name": "Format check",
            "type": "format",
            "native_id": "asset-id/format/email/"
        })
        
        format_check = IssueReporter.get_check_from_validator(
            sample_validator, "email", "format_check"
        )
        
        reporter.create_check(
            asset_id="asset-id",
            column_name="EMAIL",  # Uppercase
            check_obj=format_check,
            project_id="project-id",
            parent_id="parent-id"  # Need parent_id for column name to be in native_id
        )
        
        call_args = reporter.check_provider._create_check_full.call_args
        native_id = call_args[1]['native_id']
        # Should be lowercase
        assert "/email/" in native_id
        assert "/EMAIL/" not in native_id


class TestValidateAndPrepareCheckData:
    """Test _validate_and_prepare_check_data method"""
    
    def test_validate_skip_no_failures(self, reporter, sample_validator):
        """Test that validation returns None when there are no failures."""
        stats = {'failed': 0, 'total': 100}
        
        result = reporter._validate_and_prepare_check_data(
            column_name="email",
            check_name="format_check",
            stats=stats,
            data_asset_entity=Mock(),
            assets_map={},
            validator=sample_validator
        )
        
        assert result is None
    
    def test_validate_skip_unmapped_check_type(self, reporter, sample_validator):
        """Test that validation returns None for unmapped check types."""
        stats = {'failed': 10, 'total': 100}
        
        result = reporter._validate_and_prepare_check_data(
            column_name="email",
            check_name="unknown_check",  # Not in mapping
            stats=stats,
            data_asset_entity=Mock(),
            assets_map={},
            validator=sample_validator
        )
        
        assert result is None
    
    def test_validate_skip_missing_column_info(self, reporter, sample_validator):
        """Test that validation returns None when column info is missing."""
        stats = {'failed': 10, 'total': 100}
        data_asset_entity = Mock()
        data_asset_entity.column_info = {}  # Empty column info
        
        result = reporter._validate_and_prepare_check_data(
            column_name="email",
            check_name="format_check",
            stats=stats,
            data_asset_entity=data_asset_entity,
            assets_map={},
            validator=sample_validator
        )
        
        assert result is None
    
    def test_validate_skip_missing_column_asset_id(self, reporter, sample_validator):
        """Test that validation returns None when column asset ID not found."""
        stats = {'failed': 10, 'total': 100}
        data_asset_entity = Mock()
        data_asset_entity.column_info = {"email": Mock()}
        assets_map = {}  # Empty map
        
        result = reporter._validate_and_prepare_check_data(
            column_name="email",
            check_name="format_check",
            stats=stats,
            data_asset_entity=data_asset_entity,
            assets_map=assets_map,
            validator=sample_validator
        )
        
        assert result is None
    
    def test_validate_skip_check_not_in_validator(self, reporter, sample_validator):
        """Test that validation returns None when check not found in validator."""
        stats = {'failed': 10, 'total': 100}
        data_asset_entity = Mock()
        data_asset_entity.column_info = {"email": Mock()}
        assets_map = {"email": {"id": "column-asset-id"}}
        
        result = reporter._validate_and_prepare_check_data(
            column_name="email",
            check_name="range_check",  # email doesn't have range check
            stats=stats,
            data_asset_entity=data_asset_entity,
            assets_map=assets_map,
            validator=sample_validator
        )
        
        assert result is None
    
    def test_validate_success(self, reporter, sample_validator):
        """Test successful validation returns tuple with all data."""
        stats = {'failed': 10, 'total': 100}
        data_asset_entity = Mock()
        data_asset_entity.column_info = {"email": Mock()}
        assets_map = {"email": {"id": "column-asset-id-123", "name": "email"}}
        
        result = reporter._validate_and_prepare_check_data(
            column_name="email",
            check_name="format_check",
            stats=stats,
            data_asset_entity=data_asset_entity,
            assets_map=assets_map,
            validator=sample_validator
        )
        
        assert result is not None
        check_type, column_id, check_obj, occurrences, total = result
        assert check_type == "format"
        assert column_id == "column-asset-id-123"
        assert isinstance(check_obj, FormatCheck)
        assert occurrences == 10
        assert total == 100


class TestCreateCheckAndIssue:
    """Test _create_check_and_issue method"""
    
    def test_create_check_and_issue_success(self, reporter, sample_validator):
        """Test successful check and issue creation."""
        # Mock handle_parent to return a parent check dict
        reporter.handle_parent = Mock(return_value={"id": "parent-check-id", "type": "format"})
        reporter.create_check = Mock(return_value={
            "id": "check-id-123",
            "name": "Format check",
            "type": "format"
        })
        reporter.issues_provider.create_issue = Mock()
        
        format_check = IssueReporter.get_check_from_validator(
            sample_validator, "email", "format_check"
        )
        
        assets_map = {
            "email": {
                "id": "column-asset-id",
                "name": "email",
                "type": "column"
            }
        }
        
        result = reporter._create_check_and_issue(
            asset_id="asset-id",
            column_name="email",
            column_id="column-asset-id",
            check_name="format_check",
            check_obj=format_check,
            number_of_occurrences=10,
            total_records=100,
            project_id="project-123",
            assets_map=assets_map
        )
        
        assert result is True
        reporter.handle_parent.assert_called_once()
        reporter.create_check.assert_called_once()
        reporter.issues_provider.create_issue.assert_called_once_with(
            dq_check_id="check-id-123",
            reported_for_id="column-asset-id",
            number_of_occurrences=10,
            number_of_tested_records=100,
            project_id="project-123",
            catalog_id=None
        )
    
    def test_create_check_and_issue_409_conflict_update_success(self, reporter, sample_validator):
        """Test handling 409 conflict by updating existing check."""
        # Mock handle_parent to return a parent check dict
        reporter.handle_parent = Mock(return_value={"id": "parent-check-id", "type": "format"})
        # First call raises 409, then get_checks returns existing check
        reporter.create_check = Mock(
            side_effect=ValueError("409 Conflict: Check already exists")
        )
        reporter.check_provider.get_checks = Mock(return_value=[
            {"id": "existing-check-id", "type": "format", "native_id": "asset-id/email/format"}
        ])
        reporter.issues_provider.update_issue_metrics = Mock()
        
        format_check = IssueReporter.get_check_from_validator(
            sample_validator, "email", "format_check"
        )
        
        assets_map = {
            "email": {
                "id": "column-asset-id",
                "name": "email",
                "type": "column"
            }
        }
        
        result = reporter._create_check_and_issue(
            asset_id="asset-id",
            column_name="email",
            column_id="column-asset-id",
            check_name="format_check",
            check_obj=format_check,
            number_of_occurrences=10,
            total_records=100,
            project_id="project-123",
            assets_map=assets_map
        )
        
        assert result is True
        reporter.check_provider.get_checks.assert_called_once_with(
            dq_asset_id="column-asset-id",
            check_type="format",
            project_id="project-123"
        )
        reporter.issues_provider.update_issue_metrics.assert_called_once()
    
    def test_create_check_and_issue_409_conflict_check_not_found(self, reporter, sample_validator):
        """Test handling 409 conflict when existing check cannot be found."""
        reporter.handle_parent = Mock(return_value=None)
        reporter.create_check = Mock(
            side_effect=ValueError("409 Conflict: Check already exists")
        )
        reporter.check_provider.get_checks = Mock(return_value=[
            {"id": "other-check-id", "type": "completeness"}  # Different type
        ])
        
        format_check = IssueReporter.get_check_from_validator(
            sample_validator, "email", "format_check"
        )
        
        assets_map = {
            "email": {
                "id": "column-asset-id",
                "name": "email",
                "type": "column"
            }
        }
        
        result = reporter._create_check_and_issue(
            asset_id="asset-id",
            column_name="email",
            column_id="column-asset-id",
            check_name="format_check",
            check_obj=format_check,
            number_of_occurrences=10,
            total_records=100,
            project_id="project-123",
            assets_map=assets_map
        )
        
        assert result is False
    
    def test_create_check_and_issue_non_409_error(self, reporter, sample_validator):
        """Test handling non-409 errors."""
        reporter.handle_parent = Mock(return_value=None)
        reporter.create_check = Mock(
            side_effect=ValueError("500 Internal Server Error")
        )
        
        format_check = IssueReporter.get_check_from_validator(
            sample_validator, "email", "format_check"
        )
        
        assets_map = {
            "email": {
                "id": "column-asset-id",
                "name": "email",
                "type": "column"
            }
        }
        
        result = reporter._create_check_and_issue(
            asset_id="asset-id",
            column_name="email",
            column_id="column-asset-id",
            check_name="format_check",
            check_obj=format_check,
            number_of_occurrences=10,
            total_records=100,
            project_id="project-123",
            assets_map=assets_map
        )
        
        assert result is False
    
    def test_create_check_and_issue_unmapped_check_type(self, reporter, sample_validator):
        """Test handling unmapped check type."""
        # Create a mock check with unknown type
        unknown_check = Mock()
        unknown_check.get_check_name = Mock(return_value="unknown_check")
        
        assets_map = {
            "email": {
                "id": "column-asset-id",
                "name": "email",
                "type": "column"
            }
        }
        
        result = reporter._create_check_and_issue(
            asset_id="asset-id",
            column_name="email",
            column_id="column-asset-id",
            check_name="unknown_check",
            check_obj=unknown_check,
            number_of_occurrences=10,
            total_records=100,
            project_id="project-123",
            assets_map=assets_map
        )
        
        assert result is False


class TestHandleParent:
    """Test handle_parent method"""
    
    def test_handle_parent_found_existing(self, reporter, sample_validator):
        """Test finding existing parent check."""
        format_check = IssueReporter.get_check_from_validator(
            sample_validator, "email", "format_check"
        )
        
        # Mock search_provider to return existing check
        reporter.search_provider.search_dq_check = Mock(return_value={
            "id": "parent-check-id",
            "native_id": "asset-id/format/Accuracy",
            "type": "format"
        })
        
        result = reporter.handle_parent(
            asset_id="asset-id",
            check_obj=format_check,
            project_id="project-123"
        )
        
        assert result is not None
        assert result["id"] == "parent-check-id"
        assert "_newly_created" not in result
        reporter.search_provider.search_dq_check.assert_called_once()
    
    def test_handle_parent_not_found_creates_new(self, reporter, sample_validator):
        """Test creating new parent check when not found."""
        format_check = IssueReporter.get_check_from_validator(
            sample_validator, "email", "format_check"
        )
        
        # Mock search to raise exception (not found)
        reporter.search_provider.search_dq_check = Mock(
            side_effect=Exception("Check not found")
        )
        
        # Mock create_check to return new check
        reporter.create_check = Mock(return_value={
            "id": "new-parent-check-id",
            "native_id": "asset-id/format/Accuracy",
            "type": "format"
        })
        
        result = reporter.handle_parent(
            asset_id="asset-id",
            check_obj=format_check,
            project_id="project-123"
        )
        
        assert result is not None
        assert result["id"] == "new-parent-check-id"
        assert result["_newly_created"] is True
        reporter.create_check.assert_called_once_with(
            asset_id="asset-id",
            column_name=None,
            check_obj=format_check,
            project_id="project-123",
            catalog_id=None,
            parent_id=None
        )
    
    def test_handle_parent_creation_fails(self, reporter, sample_validator):
        """Test when both search and creation fail - should raise RuntimeError."""
        format_check = IssueReporter.get_check_from_validator(
            sample_validator, "email", "format_check"
        )
        
        # Mock search to raise exception
        reporter.search_provider.search_dq_check = Mock(
            side_effect=Exception("Check not found")
        )
        
        # Mock create_check to also raise exception
        reporter.create_check = Mock(
            side_effect=Exception("Creation failed")
        )
        
        # Should raise RuntimeError when parent creation fails
        with pytest.raises(RuntimeError) as exc_info:
            reporter.handle_parent(
                asset_id="asset-id",
                check_obj=format_check,
                project_id="project-123"
            )
        
        assert "Failed to create parent check" in str(exc_info.value)
        assert "Creation failed" in str(exc_info.value)
    
    def test_handle_parent_with_catalog_id(self, reporter, sample_validator):
        """Test handle_parent with catalog_id."""
        format_check = IssueReporter.get_check_from_validator(
            sample_validator, "email", "format_check"
        )
        
        reporter.search_provider.search_dq_check = Mock(return_value={
            "id": "parent-check-id",
            "native_id": "asset-id/format/Validity",
            "type": "format"
        })
        
        result = reporter.handle_parent(
            asset_id="asset-id",
            check_obj=format_check,
            project_id=None,
            catalog_id="catalog-123"
        )
        
        assert result is not None
        reporter.search_provider.search_dq_check.assert_called_once_with(
            native_id="asset-id/format/Validity",
            check_type="format",
            project_id=None,
            catalog_id="catalog-123",
            include_children=False
        )


class TestCreateBulkIssues:
    """Test create_bulk_issues method"""
    
    def test_create_bulk_issues_success(self, reporter):
        """Test successful bulk issue creation."""
        parent_check = {
            "id": "parent-check-id",
            "native_id": "asset-id/format/Accuracy",
            "type": "format"
        }
        
        child_check = {
            "id": "child-check-id",
            "native_id": "asset-id/email/format",
            "type": "format"
        }
        
        assets_map = {
            "email": {
                "id": "column-asset-id",
                "name": "email",
                "type": "column",
                "native_id": "schema.table.email",
                "parent": {
                    "id": "parent-asset-id"
                },
                "weight": 1
            },
            "table": {
                "id": "parent-asset-id",
                "name": "table",
                "type": "data_asset",
                "native_id": "schema.table",
                "weight": 1
            }
        }
        
        reporter.issues_provider.create_issues_bulk = Mock(return_value={
            "created": 2
        })
        
        result = reporter.create_bulk_issues(
            parent_check=parent_check,
            child_check=child_check,
            column_name="email",
            assets_map=assets_map,
            number_of_occurrences=10,
            total_records=100,
            project_id="project-123"
        )
        
        assert result is not None
        reporter.issues_provider.create_issues_bulk.assert_called_once()
        
        # Verify the payload structure
        call_args = reporter.issues_provider.create_issues_bulk.call_args
        payload = call_args.kwargs["payload"]
        
        assert len(payload["issues"]) == 2
        assert len(payload["assets"]) == 2
        assert len(payload["existing_checks"]) == 2
        assert payload["issues"][0]["status"] == "aggregation"
        assert payload["issues"][1]["status"] == "actual"
    
    def test_create_bulk_issues_column_not_found(self, reporter):
        """Test when column asset not found in assets_map."""
        parent_check = {"id": "parent-check-id"}
        child_check = {"id": "child-check-id"}
        assets_map = {}
        
        with pytest.raises(ValueError, match="Column asset not found"):
            reporter.create_bulk_issues(
                parent_check=parent_check,
                child_check=child_check,
                column_name="email",
                assets_map=assets_map,
                number_of_occurrences=10,
                total_records=100,
                project_id="project-123"
            )
    
    def test_create_bulk_issues_parent_id_not_found(self, reporter):
        """Test when parent asset ID not found in column asset."""
        parent_check = {"id": "parent-check-id"}
        child_check = {"id": "child-check-id"}
        assets_map = {
            "email": {
                "id": "column-asset-id",
                "name": "email",
                "type": "column"
                # Missing parent
            }
        }
        
        with pytest.raises(ValueError, match="Parent asset ID not found"):
            reporter.create_bulk_issues(
                parent_check=parent_check,
                child_check=child_check,
                column_name="email",
                assets_map=assets_map,
                number_of_occurrences=10,
                total_records=100,
                project_id="project-123"
            )
    
    def test_create_bulk_issues_parent_asset_not_in_map(self, reporter):
        """Test when parent asset not found in assets_map."""
        parent_check = {"id": "parent-check-id"}
        child_check = {"id": "child-check-id"}
        assets_map = {
            "email": {
                "id": "column-asset-id",
                "name": "email",
                "type": "column",
                "parent": {
                    "id": "parent-asset-id"
                }
            }
            # Parent asset not in map
        }
        
        with pytest.raises(ValueError, match="Parent asset not found in assets_map"):
            reporter.create_bulk_issues(
                parent_check=parent_check,
                child_check=child_check,
                column_name="email",
                assets_map=assets_map,
                number_of_occurrences=10,
                total_records=100,
                project_id="project-123"
            )
    
    def test_create_bulk_issues_parent_native_id_missing(self, reporter):
        """Test when parent asset native_id is missing."""
        parent_check = {"id": "parent-check-id"}
        child_check = {"id": "child-check-id"}
        assets_map = {
            "email": {
                "id": "column-asset-id",
                "name": "email",
                "type": "column",
                "parent": {
                    "id": "parent-asset-id"
                }
            },
            "table": {
                "id": "parent-asset-id",
                "name": "table",
                "type": "data_asset"
                # Missing native_id
            }
        }
        
        with pytest.raises(ValueError, match="Parent asset native_id not found"):
            reporter.create_bulk_issues(
                parent_check=parent_check,
                child_check=child_check,
                column_name="email",
                assets_map=assets_map,
                number_of_occurrences=10,
                total_records=100,
                project_id="project-123"
            )
    
    def test_create_bulk_issues_api_failure(self, reporter):
        """Test when bulk API call fails."""
        parent_check = {
            "id": "parent-check-id",
            "native_id": "asset-id/format/Accuracy",
            "type": "format"
        }
        
        child_check = {
            "id": "child-check-id",
            "native_id": "asset-id/email/format",
            "type": "format"
        }
        
        assets_map = {
            "email": {
                "id": "column-asset-id",
                "name": "email",
                "type": "column",
                "native_id": "schema.table.email",
                "parent": {
                    "id": "parent-asset-id"
                },
                "weight": 1
            },
            "table": {
                "id": "parent-asset-id",
                "name": "table",
                "type": "data_asset",
                "native_id": "schema.table",
                "weight": 1
            }
        }
        
        reporter.issues_provider.create_issues_bulk = Mock(
            side_effect=Exception("API Error")
        )
        
        with pytest.raises(Exception, match="API Error"):
            reporter.create_bulk_issues(
                parent_check=parent_check,
                child_check=child_check,
                column_name="email",
                assets_map=assets_map,
                number_of_occurrences=10,
                total_records=100,
                project_id="project-123"
            )


class TestHelperMethods:
    """Test refactored helper methods"""
    
    def test_find_existing_check_success(self, reporter):
        """Test successfully finding an existing check."""
        reporter.check_provider.get_checks = Mock(return_value=[
            {"id": "check-1", "type": "format", "native_id": "asset/email/format"},
            {"id": "check-2", "type": "completeness", "native_id": "asset/email/completeness"}
        ])
        
        result = reporter._find_existing_check(
            column_id="column-asset-id",
            check_type="format",
            project_id="project-123"
        )
        
        assert result is not None
        assert result[0] == "check-1"
        assert result[1] == "asset/email/format"
    
    def test_find_existing_check_not_found(self, reporter):
        """Test when check type doesn't match."""
        reporter.check_provider.get_checks = Mock(return_value=[
            {"id": "check-1", "type": "completeness"}
        ])
        
        result = reporter._find_existing_check(
            column_id="column-asset-id",
            check_type="format",
            project_id="project-123"
        )
        
        assert result is None
    
    def test_find_existing_check_api_error(self, reporter):
        """Test when API call fails."""
        reporter.check_provider.get_checks = Mock(
            side_effect=ValueError("API Error")
        )
        
        result = reporter._find_existing_check(
            column_id="column-asset-id",
            check_type="format",
            project_id="project-123"
        )
        
        assert result is None
    
    def test_update_existing_check_metrics_success(self, reporter):
        """Test successful metric update."""
        reporter.issues_provider.update_issue_metrics = Mock()
        
        result = reporter._update_existing_check_metrics(
            existing_check_native_id="asset/email/format",
            number_of_occurrences=10,
            total_records=100,
            column_name="email",
            check_type="format",
            project_id="project-123"
        )
        
        assert result is True
        reporter.issues_provider.update_issue_metrics.assert_called_once()
    
    def test_update_existing_check_metrics_failure(self, reporter):
        """Test when metric update fails."""
        reporter.issues_provider.update_issue_metrics = Mock(
            side_effect=ValueError("Update failed")
        )
        
        result = reporter._update_existing_check_metrics(
            existing_check_native_id="asset/email/format",
            number_of_occurrences=10,
            total_records=100,
            column_name="email",
            check_type="format",
            project_id="project-123"
        )
        
        assert result is False
    
    def test_handle_409_conflict_success(self, reporter):
        """Test successful 409 conflict handling."""
        reporter._find_existing_check = Mock(return_value=("check-id", "native-id"))
        reporter._update_existing_check_metrics = Mock(return_value=True)
        
        result = reporter._handle_409_conflict(
            column_id="column-asset-id",
            check_type="format",
            number_of_occurrences=10,
            total_records=100,
            column_name="email",
            check_name="format_check",
            asset_id="asset-id",
            project_id="project-123"
        )
        
        assert result is True
    
    def test_handle_409_conflict_check_not_found(self, reporter):
        """Test 409 conflict when check not found."""
        reporter._find_existing_check = Mock(return_value=None)
        
        result = reporter._handle_409_conflict(
            column_id="column-asset-id",
            check_type="format",
            number_of_occurrences=10,
            total_records=100,
            column_name="email",
            check_name="format_check",
            asset_id="asset-id",
            project_id="project-123"
        )
        
        assert result is False
    
    def test_handle_409_conflict_update_fails_fallback(self, reporter):
        """Test 409 conflict when update fails but fallback succeeds."""
        reporter._find_existing_check = Mock(return_value=("check-id", "native-id"))
        reporter._update_existing_check_metrics = Mock(return_value=False)
        reporter._handle_update_failure = Mock()
        
        result = reporter._handle_409_conflict(
            column_id="column-asset-id",
            check_type="format",
            number_of_occurrences=10,
            total_records=100,
            column_name="email",
            check_name="format_check",
            asset_id="asset-id",
            project_id="project-123"
        )
        
        assert result is True
        reporter._handle_update_failure.assert_called_once()


class TestHandleUpdateFailure:
    """Test _handle_update_failure method"""
    
    def test_handle_update_failure_issue_not_found_creates_issue(self, reporter):
        """Test creating issue when update fails with 'Issue not found'."""
        reporter.get_check_id = Mock(return_value="check-id-123")
        reporter.issues_provider.create_issue = Mock()
        
        error = ValueError("Issue not found for check")
        
        result = reporter._handle_update_failure(
            error=error,
            asset_id="asset-id",
            check_type="format",
            column_name="email",
            column_id="column-asset-id",
            number_of_occurrences=10,
            total_records=100,
            project_id="project-123",
            check_id="check-id"
        )
        
        assert result is True
        reporter.get_check_id.assert_called_once_with(
            check_native_id="asset-id/check-id",
            check_type="format",
            project_id="project-123"
        )
        reporter.issues_provider.create_issue.assert_called_once()
    
    def test_handle_update_failure_issue_id_not_found(self, reporter):
        """Test creating issue when update fails with 'Issue ID not found'."""
        reporter.get_check_id = Mock(return_value="check-id-456")
        reporter.issues_provider.create_issue = Mock()
        
        error = ValueError("Issue ID not found in response")
        
        result = reporter._handle_update_failure(
            error=error,
            asset_id="asset-id",
            check_type="completeness",
            column_name="name",
            column_id="column-asset-id",
            number_of_occurrences=5,
            total_records=50,
            project_id="project-123",
            check_id="check-id"
        )
        
        assert result is True
        reporter.issues_provider.create_issue.assert_called_once()
    
    def test_handle_update_failure_check_id_not_found(self, reporter):
        """Test when check_id cannot be found."""
        reporter.get_check_id = Mock(return_value=None)
        
        error = ValueError("Issue not found")
        
        result = reporter._handle_update_failure(
            error=error,
            asset_id="asset-id",
            check_type="format",
            column_name="email",
            column_id="column-asset-id",
            number_of_occurrences=10,
            total_records=100,
            project_id="project-123",
            check_id="check-id"
        )
        
        assert result is True
        reporter.get_check_id.assert_called_once()
    
    def test_handle_update_failure_different_error(self, reporter):
        """Test handling different error types."""
        error = ValueError("Different error message")
        
        result = reporter._handle_update_failure(
            error=error,
            asset_id="asset-id",
            check_type="format",
            column_name="email",
            column_id="column-asset-id",
            number_of_occurrences=10,
            total_records=100,
            project_id="project-123",
            check_id="check-id"
        )
        
        assert result is True


class TestHandleExistingCheck:
    """Test _handle_existing_check method"""
    
    def test_handle_existing_check_success(self, reporter):
        """Test successful handling of existing check."""
        column_info = Mock()
        check = Mock()
        check.metadata = Mock()
        check.metadata.type = "format"
        check.metadata.check_id = "check-id-123"
        column_info.column_checks = [check]
        
        reporter.issues_provider.update_issue_metrics = Mock()
        
        result = reporter._handle_existing_check(
            column_info=column_info,
            check_type="format",
            asset_id="asset-id",
            column_name="email",
            column_id="column-asset-id",
            number_of_occurrences=10,
            total_records=100,
            project_id="project-123"
        )
        
        assert result is True
        reporter.issues_provider.update_issue_metrics.assert_called_once_with(
            asset_id="asset-id",
            check_id="check-id-123",
            occurrences=10,
            tested_records=100,
            column_name="email",
            check_type="format",
            project_id="project-123",
            asset_type="column",
            operation="add"
        )
    
    def test_handle_existing_check_type_mismatch(self, reporter):
        """Test when check type doesn't match."""
        column_info = Mock()
        check = Mock()
        check.metadata = Mock()
        check.metadata.type = "completeness"  # Different type
        check.metadata.check_id = "check-id-123"
        column_info.column_checks = [check]
        
        result = reporter._handle_existing_check(
            column_info=column_info,
            check_type="format",  # Looking for format
            asset_id="asset-id",
            column_name="email",
            column_id="column-asset-id",
            number_of_occurrences=10,
            total_records=100,
            project_id="project-123"
        )
        
        assert result is False
    
    def test_handle_existing_check_no_check_id(self, reporter):
        """Test when check has no check_id."""
        column_info = Mock()
        check = Mock()
        check.metadata = Mock()
        check.metadata.type = "format"
        check.metadata.check_id = None  # No check_id
        column_info.column_checks = [check]
        
        result = reporter._handle_existing_check(
            column_info=column_info,
            check_type="format",
            asset_id="asset-id",
            column_name="email",
            column_id="column-asset-id",
            number_of_occurrences=10,
            total_records=100,
            project_id="project-123"
        )
        
        assert result is False
    
    def test_handle_existing_check_update_failure(self, reporter):
        """Test handling update failure."""
        column_info = Mock()
        check = Mock()
        check.metadata = Mock()
        check.metadata.type = "format"
        check.metadata.check_id = "check-id-123"
        column_info.column_checks = [check]
        
        reporter.issues_provider.update_issue_metrics = Mock(
            side_effect=ValueError("Update failed")
        )
        reporter._handle_update_failure = Mock(return_value=True)
        
        result = reporter._handle_existing_check(
            column_info=column_info,
            check_type="format",
            asset_id="asset-id",
            column_name="email",
            column_id="column-asset-id",
            number_of_occurrences=10,
            total_records=100,
            project_id="project-123"
        )
        
        assert result is True
        reporter._handle_update_failure.assert_called_once()


class TestReportIssues:
    """Test update_issues method"""
    
    def test_report_issues_success(self, reporter, sample_validator):
        """Test successful update of issues."""
        # Mock dependencies
        reporter.cams_provider.get_asset_by_id = Mock()
        data_asset = Mock()
        data_asset_entity = Mock()
        column_info = Mock()
        column_info.column_checks = []
        data_asset_entity.column_info = {"email": column_info}
        data_asset.entity = data_asset_entity
        reporter.cams_provider.get_asset_by_id.return_value = data_asset
        
        reporter.asset_provider.get_assets = Mock(return_value={
            "assets": [{"name": "email", "id": "column-asset-id"}]
        })
        
        reporter._create_check_and_issue = Mock(return_value=True)
        
        # Create combined stats in nested dict format
        combined_stats = {
            "email": {
                "format_check": {"failed": 10, "total": 100}
            }
        }
        
        reporter.report_issues(
            asset_id="asset-id",
            stats=combined_stats,
            validator=sample_validator
        )
        
        reporter._create_check_and_issue.assert_called_once()
    
    def test_report_issues_with_existing_checks(self, reporter, sample_validator):
        """Test update with existing checks."""
        # Mock dependencies
        reporter.cams_provider.get_asset_by_id = Mock()
        data_asset = Mock()
        data_asset_entity = Mock()
        column_info = Mock()
        check = Mock()
        check.metadata = Mock()
        check.metadata.type = "format"
        check.metadata.check_id = "check-id-123"
        column_info.column_checks = [check]
        data_asset_entity.column_info = {"email": column_info}
        data_asset.entity = data_asset_entity
        reporter.cams_provider.get_asset_by_id.return_value = data_asset
        
        reporter.asset_provider.get_assets = Mock(return_value={
            "assets": [{"name": "email", "id": "column-asset-id"}]
        })
        
        reporter._handle_existing_check = Mock(return_value=True)
        
        # Create combined stats in nested dict format
        combined_stats = {
            "email": {
                "format_check": {"failed": 10, "total": 100}
            }
        }
        
        reporter.report_issues(
            asset_id="asset-id",
            stats=combined_stats,
            validator=sample_validator
        )
        
        reporter._handle_existing_check.assert_called_once()
    
    def test_report_issues_check_not_handled_creates_new(self, reporter, sample_validator):
        """Test creating new check when existing check not handled."""
        # Mock dependencies
        reporter.cams_provider.get_asset_by_id = Mock()
        data_asset = Mock()
        data_asset_entity = Mock()
        column_info = Mock()
        check = Mock()
        check.metadata = Mock()
        check.metadata.type = "completeness"  # Different type
        check.metadata.check_id = "check-id-123"
        column_info.column_checks = [check]
        data_asset_entity.column_info = {"email": column_info}
        data_asset.entity = data_asset_entity
        reporter.cams_provider.get_asset_by_id.return_value = data_asset
        
        reporter.asset_provider.get_assets = Mock(return_value={
            "assets": [{"name": "email", "id": "column-asset-id"}]
        })
        
        reporter._handle_existing_check = Mock(return_value=False)
        reporter._create_check_and_issue = Mock(return_value=True)
        
        # Create combined stats in nested dict format
        combined_stats = {
            "email": {
                "format_check": {"failed": 10, "total": 100}
            }
        }
        
        reporter.report_issues(
            asset_id="asset-id",
            stats=combined_stats,
            validator=sample_validator
        )
        
        reporter._handle_existing_check.assert_called_once()
        reporter._create_check_and_issue.assert_called_once()