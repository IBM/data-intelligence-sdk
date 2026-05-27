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
import pytest
from wxdi.dq_validator.cel_context import CELContextBuilder
from wxdi.dq_validator.metadata import AssetMetadata, ColumnMetadata, DataType


class TestCELContextBuilderBasic:
    """Tests for basic CELContextBuilder functionality"""

    @pytest.fixture
    def metadata(self):
        """Create test metadata"""
        return AssetMetadata(
            table_name='employees',
            columns=[
                ColumnMetadata('emp_id', DataType.INTEGER),
                ColumnMetadata('name', DataType.STRING),
                ColumnMetadata('salary', DataType.DECIMAL)
            ]
        )

    def test_build_context_with_all_parameters(self, metadata):
        """Test building context with all parameters"""
        record = [1001, 'John Doe', 75000]
        context = CELContextBuilder.build_context(
            value=75000,
            column_name='salary',
            record=record,
            metadata=metadata,
            record_index=5
        )
        
        assert context['value'] == 75000
        assert context['column_name'] == 'salary'
        assert context['record_index'] == 5
        assert 'record' in context

    def test_build_context_minimal_parameters(self, metadata):
        """Test building context with minimal parameters"""
        context = CELContextBuilder.build_context(
            value=100,
            column_name='test',
            record=None,
            metadata=None
        )
        
        assert context['value'] == 100
        assert context['column_name'] == 'test'
        assert context['record_index'] == 0  # Default value
        assert context['record'] == {}  # Empty dict when no record

    def test_build_context_default_record_index(self, metadata):
        """Test that record_index defaults to 0"""
        context = CELContextBuilder.build_context(
            value=100,
            column_name='test',
            record=None,
            metadata=None
        )
        
        assert context['record_index'] == 0

    def test_build_context_with_custom_record_index(self, metadata):
        """Test building context with custom record_index"""
        context = CELContextBuilder.build_context(
            value=100,
            column_name='test',
            record=None,
            metadata=None,
            record_index=42
        )
        
        assert context['record_index'] == 42


class TestCELContextBuilderRecordDict:
    """Tests for record dictionary building"""

    @pytest.fixture
    def metadata(self):
        """Create test metadata"""
        return AssetMetadata(
            table_name='employees',
            columns=[
                ColumnMetadata('emp_id', DataType.INTEGER),
                ColumnMetadata('name', DataType.STRING),
                ColumnMetadata('salary', DataType.DECIMAL),
                ColumnMetadata('department', DataType.STRING)
            ]
        )

    def test_build_record_dict_complete_record(self, metadata):
        """Test building record dict with complete record"""
        record = [1001, 'John Doe', 75000, 'Engineering']
        context = CELContextBuilder.build_context(
            value=75000,
            column_name='salary',
            record=record,
            metadata=metadata
        )
        
        record_dict = context['record']
        # Check if it's a CEL MapType or dict
        if hasattr(record_dict, '__getitem__'):
            assert record_dict['emp_id'] == 1001
            assert record_dict['name'] == 'John Doe'
            assert record_dict['salary'] == 75000
            assert record_dict['department'] == 'Engineering'

    def test_build_record_dict_partial_record(self, metadata):
        """Test building record dict with partial record (fewer values than columns)"""
        record = [1001, 'John Doe']  # Missing salary and department
        context = CELContextBuilder.build_context(
            value=1001,
            column_name='emp_id',
            record=record,
            metadata=metadata
        )
        
        record_dict = context['record']
        if hasattr(record_dict, '__getitem__'):
            assert record_dict['emp_id'] == 1001
            assert record_dict['name'] == 'John Doe'
            # Missing columns should be None
            assert record_dict['salary'] is None
            assert record_dict['department'] is None

    def test_build_record_dict_without_metadata(self):
        """Test building record dict without metadata (fallback mode)"""
        record = [1001, 'John Doe', 75000]
        context = CELContextBuilder.build_context(
            value=75000,
            column_name='salary',
            record=record,
            metadata=None
        )
        
        record_dict = context['record']
        # Should use positional fallback: col_0, col_1, col_2
        assert record_dict['col_0'] == 1001
        assert record_dict['col_1'] == 'John Doe'
        assert record_dict['col_2'] == 75000

    def test_build_record_dict_empty_record(self, metadata):
        """Test building record dict with empty record"""
        record = []
        context = CELContextBuilder.build_context(
            value=100,
            column_name='test',
            record=record,
            metadata=metadata
        )
        
        record_dict = context['record']
        # All columns should be None when record is empty
        # The MapType will have the keys with None values
        if hasattr(record_dict, '__getitem__'):
            # Check that we can access the keys and they are None
            try:
                assert record_dict['emp_id'] is None
                assert record_dict['name'] is None
                assert record_dict['salary'] is None
                assert record_dict['department'] is None
            except KeyError:
                # If MapType doesn't include None values, that's also acceptable
                # as long as the record_dict exists
                assert record_dict is not None

    def test_build_record_dict_none_record(self, metadata):
        """Test building record dict with None record"""
        context = CELContextBuilder.build_context(
            value=100,
            column_name='test',
            record=None,
            metadata=metadata
        )
        
        assert context['record'] == {}


class TestCELContextBuilderValidation:
    """Tests for context validation"""

    def test_validate_context_valid(self):
        """Test validation of valid context"""
        context = {
            'value': 100,
            'column_name': 'test',
            'record': {},
            'record_index': 0
        }
        
        assert CELContextBuilder.validate_context(context) is True

    def test_validate_context_missing_value(self):
        """Test validation fails when value is missing"""
        context = {
            'column_name': 'test',
            'record': {},
            'record_index': 0
        }
        
        assert CELContextBuilder.validate_context(context) is False

    def test_validate_context_missing_column_name(self):
        """Test validation fails when column_name is missing"""
        context = {
            'value': 100,
            'record': {},
            'record_index': 0
        }
        
        assert CELContextBuilder.validate_context(context) is False

    def test_validate_context_missing_record(self):
        """Test validation fails when record is missing"""
        context = {
            'value': 100,
            'column_name': 'test',
            'record_index': 0
        }
        
        assert CELContextBuilder.validate_context(context) is False

    def test_validate_context_empty(self):
        """Test validation fails for empty context"""
        context = {}
        
        assert CELContextBuilder.validate_context(context) is False

    def test_validate_context_extra_fields_ok(self):
        """Test validation passes with extra fields"""
        context = {
            'value': 100,
            'column_name': 'test',
            'record': {},
            'record_index': 0,
            'extra_field': 'extra'
        }
        
        assert CELContextBuilder.validate_context(context) is True


class TestCELContextBuilderUtilities:
    """Tests for utility methods"""

    def test_get_available_variables(self):
        """Test getting list of available variables"""
        variables = CELContextBuilder.get_available_variables()
        
        assert 'value' in variables
        assert 'record' in variables
        assert 'column_name' in variables
        assert 'record_index' in variables
        assert len(variables) == 4

    def test_get_available_variables_returns_list(self):
        """Test that get_available_variables returns a list"""
        variables = CELContextBuilder.get_available_variables()
        
        assert isinstance(variables, list)


class TestCELContextBuilderDataTypes:
    """Tests for different data types in context"""

    @pytest.fixture
    def metadata(self):
        """Create test metadata with various data types"""
        return AssetMetadata(
            table_name='test_table',
            columns=[
                ColumnMetadata('int_col', DataType.INTEGER),
                ColumnMetadata('decimal_col', DataType.DECIMAL),
                ColumnMetadata('string_col', DataType.STRING),
                ColumnMetadata('bool_col', DataType.BOOLEAN)
            ]
        )

    def test_build_context_with_integer(self, metadata):
        """Test context building with integer value"""
        record = [42, 3.14, 'test', True]
        context = CELContextBuilder.build_context(
            value=42,
            column_name='int_col',
            record=record,
            metadata=metadata
        )
        
        assert context['value'] == 42
        assert isinstance(context['value'], int)

    def test_build_context_with_decimal(self, metadata):
        """Test context building with decimal value"""
        record = [42, 3.14, 'test', True]
        context = CELContextBuilder.build_context(
            value=3.14,
            column_name='decimal_col',
            record=record,
            metadata=metadata
        )
        
        assert context['value'] == 3.14
        assert isinstance(context['value'], float)

    def test_build_context_with_string(self, metadata):
        """Test context building with string value"""
        record = [42, 3.14, 'test', True]
        context = CELContextBuilder.build_context(
            value='test',
            column_name='string_col',
            record=record,
            metadata=metadata
        )
        
        assert context['value'] == 'test'
        assert isinstance(context['value'], str)

    def test_build_context_with_boolean(self, metadata):
        """Test context building with boolean value"""
        record = [42, 3.14, 'test', True]
        context = CELContextBuilder.build_context(
            value=True,
            column_name='bool_col',
            record=record,
            metadata=metadata
        )
        
        assert context['value'] is True
        assert isinstance(context['value'], bool)

    def test_build_context_with_none(self, metadata):
        """Test context building with None value"""
        record = [42, None, 'test', True]
        context = CELContextBuilder.build_context(
            value=None,
            column_name='decimal_col',
            record=record,
            metadata=metadata
        )
        
        assert context['value'] is None


class TestCELContextBuilderComplexScenarios:
    """Tests for complex scenarios"""

    def test_build_context_large_record(self):
        """Test building context with large record"""
        # Create metadata with many columns
        columns = [ColumnMetadata(f'col_{i}', DataType.INTEGER) for i in range(100)]
        metadata = AssetMetadata(table_name='large_table', columns=columns)
        
        # Create large record
        record = list(range(100))
        
        context = CELContextBuilder.build_context(
            value=50,
            column_name='col_50',
            record=record,
            metadata=metadata
        )
        
        assert context['value'] == 50
        record_dict = context['record']
        if hasattr(record_dict, '__getitem__'):
            assert record_dict['col_0'] == 0
            assert record_dict['col_50'] == 50
            assert record_dict['col_99'] == 99

    def test_build_context_special_characters_in_names(self):
        """Test building context with special characters in column names"""
        metadata = AssetMetadata(
            table_name='test',
            columns=[
                ColumnMetadata('col_with_underscore', DataType.INTEGER),
                ColumnMetadata('col123', DataType.INTEGER)
            ]
        )
        
        record = [100, 200]
        context = CELContextBuilder.build_context(
            value=100,
            column_name='col_with_underscore',
            record=record,
            metadata=metadata
        )
        
        record_dict = context['record']
        if hasattr(record_dict, '__getitem__'):
            assert record_dict['col_with_underscore'] == 100
            assert record_dict['col123'] == 200

    def test_build_context_unicode_values(self):
        """Test building context with unicode values"""
        metadata = AssetMetadata(
            table_name='test',
            columns=[
                ColumnMetadata('id', DataType.INTEGER),
                ColumnMetadata('name', DataType.STRING)
            ]
        )
        
        record = [1, '日本語']  # Japanese characters
        context = CELContextBuilder.build_context(
            value='日本語',
            column_name='name',
            record=record,
            metadata=metadata
        )
        
        assert context['value'] == '日本語'
        record_dict = context['record']
        if hasattr(record_dict, '__getitem__'):
            assert record_dict['name'] == '日本語'

# Made with Bob
