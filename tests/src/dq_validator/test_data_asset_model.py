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
Test suite for DataAsset model
"""

import json
import pytest
from pathlib import Path
from wxdi.dq_validator.provider.data_asset_model import DataAsset


class TestDataAssetModel:
    """Test cases for DataAsset Pydantic model"""

    @pytest.fixture
    def data_asset_json(self):
        """Load the data asset response JSON"""
        json_path = Path(__file__).parent.parent.parent / "data" / "data_asset_response.json"
        with open(json_path, "r") as f:
            return json.load(f)

    def test_parse_data_asset_response(self, data_asset_json):
        """Test parsing the complete data asset response"""
        data_asset = DataAsset.from_dict(data_asset_json)
        
        assert data_asset is not None
        assert isinstance(data_asset, DataAsset)

    def test_metadata_fields(self, data_asset_json):
        """Test metadata fields are correctly parsed"""
        data_asset = DataAsset.from_dict(data_asset_json)
        
        assert data_asset.metadata.asset_id == "6862f3ba-81f5-4122-8286-62bb4c5d6543"
        assert data_asset.metadata.name == "DEPARTMENT"
        assert data_asset.metadata.asset_type == "data_asset"
        assert data_asset.metadata.project_id == "72d21c1d-499b-4784-a3c7-6f84507f9a20"

    def test_columns_parsed(self, data_asset_json):
        """Test that columns are correctly parsed"""
        data_asset = DataAsset.from_dict(data_asset_json)
        
        columns = data_asset.entity.data_asset.columns
        assert len(columns) == 5
        
        # Check first column
        assert columns[0].name == "DEPTNO"
        assert columns[0].type.type == "char"
        assert columns[0].type.length == 3
        assert columns[0].type.nullable is False

    def test_column_info_parsed(self, data_asset_json):
        """Test that column_info is correctly parsed"""
        data_asset = DataAsset.from_dict(data_asset_json)
        
        column_info = data_asset.entity.column_info
        assert "DEPTNO" in column_info
        assert "MGRNO" in column_info
        assert "LOCATION" in column_info

    def test_column_checks_parsed(self, data_asset_json):
        """Test that column checks are correctly parsed"""
        data_asset = DataAsset.from_dict(data_asset_json)
        
        # DEPTNO has 4 checks
        deptno_info = data_asset.entity.column_info["DEPTNO"]
        assert len(deptno_info.column_checks) == 4
        
        # Check types
        check_types = [check.metadata.type for check in deptno_info.column_checks]
        assert "format" in check_types
        assert "uniqueness" in check_types
        assert "completeness" in check_types
        assert "data_class" in check_types

    def test_data_class_info(self, data_asset_json):
        """Test data class information"""
        data_asset = DataAsset.from_dict(data_asset_json)
        
        deptno_info = data_asset.entity.column_info["DEPTNO"]
        assert deptno_info.data_class.selected_data_class.name == "ICD-10"
        assert len(deptno_info.data_class.suggested_classes) == 2

    def test_inferred_type(self, data_asset_json):
        """Test inferred type information"""
        data_asset = DataAsset.from_dict(data_asset_json)
        
        mgrno_info = data_asset.entity.column_info["MGRNO"]
        assert mgrno_info.inferred_type.type == "INT8"
        assert mgrno_info.inferred_type.display_name == "tinyint"
        assert mgrno_info.inferred_type.precision == 3

    def test_column_without_checks(self, data_asset_json):
        """Test column without any checks (LOCATION)"""
        data_asset = DataAsset.from_dict(data_asset_json)
        
        location_info = data_asset.entity.column_info["LOCATION"]
        assert len(location_info.column_checks) == 0
        assert location_info.data_class.selected_data_class.name == "NoClassDetected"

    def test_asset_properties(self, data_asset_json):
        """Test asset properties"""
        data_asset = DataAsset.from_dict(data_asset_json)
        
        properties = data_asset.entity.data_asset.properties
        assert len(properties) == 2
        
        schema_prop = next(p for p in properties if p.name == "schema_name")
        assert schema_prop.value == "DB2INST1"
        
        table_prop = next(p for p in properties if p.name == "table_name")
        assert table_prop.value == "DEPARTMENT"

    def test_check_constraint_details(self, data_asset_json):
        """Test detailed check constraint information"""
        data_asset = DataAsset.from_dict(data_asset_json)
        
        # Get format check from MGRNO
        mgrno_info = data_asset.entity.column_info["MGRNO"]
        format_check = next(
            c for c in mgrno_info.column_checks 
            if c.metadata.type == "format"
        )
        
        assert len(format_check.check) == 1
        assert format_check.check[0].name == "formats"
        assert format_check.check[0].list_value == ["999999"]

    def test_completeness_check(self, data_asset_json):
        """Test completeness check parsing"""
        data_asset = DataAsset.from_dict(data_asset_json)
        
        deptno_info = data_asset.entity.column_info["DEPTNO"]
        completeness_check = next(
            c for c in deptno_info.column_checks 
            if c.metadata.type == "completeness"
        )
        
        assert len(completeness_check.check) == 1
        assert completeness_check.check[0].name == "missing_values_allowed"
        assert completeness_check.check[0].boolean_value is False

    def test_range_check(self, data_asset_json):
        """Test range check parsing"""
        data_asset = DataAsset.from_dict(data_asset_json)
        
        mgrno_info = data_asset.entity.column_info["MGRNO"]
        range_check = next(
            c for c in mgrno_info.column_checks 
            if c.metadata.type == "range"
        )
        
        assert len(range_check.check) == 2
        range_type = next(c for c in range_check.check if c.name == "range_type")
        assert range_type.value == "number"
        
        min_value = next(c for c in range_check.check if c.name == "min")
        assert min_value.numeric_value == 0

    def test_case_check(self, data_asset_json):
        """Test case check parsing"""
        data_asset = DataAsset.from_dict(data_asset_json)
        
        deptname_info = data_asset.entity.column_info["DEPTNAME"]
        case_check = next(
            c for c in deptname_info.column_checks 
            if c.metadata.type == "case"
        )
        
        assert len(case_check.check) == 1
        assert case_check.check[0].name == "case_type"
        assert case_check.check[0].value == "UpperCase"

# Made with Bob
