# Copyright 2026 IBM Corporation
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0);
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# See the LICENSE file in the project root for license information.

"""
CEL Context Builder - Converts validation data into CEL-compatible context.

OVERVIEW:
This module transforms raw validation data (arrays of values) into structured
dictionaries that CEL expressions can evaluate. It enables both simple and
explicit syntax for accessing column values in CEL expressions.

KEY CONCEPTS:
1. Context Dictionary: A dict containing all variables available to CEL expressions
2. Record Array: List of values in column order, e.g., [1001, 'John', 75000]
3. Metadata: Column definitions that map array positions to column names
4. Dual Syntax Support: Allows both 'min_salary' and 'record.min_salary'

EXAMPLE TRANSFORMATION:
    Input:
        - value: 75000 (current column being validated)
        - column_name: 'salary'
        - record: [1001, 'John', 75000, 60000]
        - metadata: columns=['emp_id', 'name', 'salary', 'min_salary']
    
    Output Context:
        {
            'value': 75000,              # Current value being validated
            'column_name': 'salary',     # Name of current column
            'record_index': 0,           # Position in batch
            'record': {                  # All columns as dict
                'emp_id': 1001,
                'name': 'John',
                'salary': 75000,
                'min_salary': 60000
            },
            # SIMPLE SYNTAX: Direct column access (added for convenience)
            'emp_id': 1001,
            'name': 'John',
            'salary': 75000,
            'min_salary': 60000
        }
    
    This allows CEL expressions to use either:
        - Simple: 'value > min_salary'
        - Explicit: 'value > record.min_salary'
"""

from typing import Any, Dict, List, Optional
from .metadata import AssetMetadata

try:
    import celpy
except ImportError:
    celpy = None


class CELContextBuilder:
    """
    Builds CEL evaluation context from validation data.
    
    PURPOSE:
    Transforms raw validation data into a structured dictionary that CEL
    expressions can evaluate. Supports both simple ('min_salary') and
    explicit ('record.min_salary') syntax for accessing column values.
    
    CONTEXT VARIABLES PROVIDED:
    ┌─────────────────┬──────────────────────────────────────────────────────┐
    │ Variable        │ Description                                          │
    ├─────────────────┼──────────────────────────────────────────────────────┤
    │ value           │ Current column value being validated                 │
    │ column_name     │ Name of the column being validated                   │
    │ record_index    │ Position of record in batch (0-based)                │
    │ record          │ Dict of all columns: {'col1': val1, 'col2': val2}    │
    │ <column_names>  │ Direct access to each column (e.g., min_salary)      │
    └─────────────────┴──────────────────────────────────────────────────────┘
    
    RESERVED NAMES (cannot be used as column names with simple syntax):
    - value, column_name, record_index, record
    If your data has columns with these names, use explicit syntax:
    'record.value' instead of 'value'
    
    USAGE EXAMPLE:
        >>> from wxdi.dq_validator import AssetMetadata, ColumnMetadata, DataType
        >>> from wxdi.dq_validator.cel_context import CELContextBuilder
        >>>
        >>> # Define metadata
        >>> metadata = AssetMetadata(
        ...     table_name='employees',
        ...     columns=[
        ...         ColumnMetadata('emp_id', DataType.INTEGER),
        ...         ColumnMetadata('salary', DataType.DECIMAL),
        ...         ColumnMetadata('min_salary', DataType.DECIMAL)
        ...     ]
        ... )
        >>>
        >>> # Build context from record data
        >>> record = [1001, 75000.00, 60000.00]
        >>> context = CELContextBuilder.build_context(
        ...     value=75000.00,
        ...     column_name='salary',
        ...     record=record,
        ...     metadata=metadata,
        ...     record_index=0
        ... )
        >>>
        >>> # Context now contains:
        >>> # - value: 75000.00
        >>> # - column_name: 'salary'
        >>> # - record_index: 0
        >>> # - record: {'emp_id': 1001, 'salary': 75000.00, 'min_salary': 60000.00}
        >>> # - emp_id: 1001 (direct access)
        >>> # - salary: 75000.00 (direct access)
        >>> # - min_salary: 60000.00 (direct access)
    """
    
    @staticmethod
    def _init_base_context(value: Any, column_name: str, record_index: int) -> Dict[str, Any]:
        """Initialize base context with required variables."""
        return {
            'value': value,
            'column_name': column_name,
            'record_index': record_index
        }
    
    @staticmethod
    def _add_record_with_metadata(
        context: Dict[str, Any],
        record: List[Any],
        metadata: AssetMetadata,
        required_columns: Optional[set],
        bindings: Optional[Dict[str, str]]
    ) -> None:
        """Add record data with metadata to context."""
        RESERVED_NAMES = {'value', 'column_name', 'record_index', 'record'}
        
        # Convert array to named dictionary
        record_dict = CELContextBuilder._build_record_dict(record, metadata)
        context['record'] = record_dict
        
        # Add columns directly to context for simple syntax
        CELContextBuilder._add_columns_to_context(
            context, record_dict, RESERVED_NAMES, required_columns
        )
        
        # Apply variable bindings if provided
        CELContextBuilder._apply_bindings(context, record_dict, bindings)
    
    @staticmethod
    def _add_record_without_metadata(context: Dict[str, Any], record: List[Any]) -> None:
        """Add record data without metadata (positional columns)."""
        positional_dict = {f'col_{i}': val for i, val in enumerate(record)}
        context['record'] = positional_dict
        context.update(positional_dict)
    
    @staticmethod
    def _should_add_column(key: str, reserved_names: set, required_columns: Optional[set]) -> bool:
        """Check if column should be added to context."""
        if key in reserved_names:
            return False
        return required_columns is None or key in required_columns
    
    @staticmethod
    def _add_dict_columns(
        context: Dict[str, Any],
        record_dict: dict,
        reserved_names: set,
        required_columns: Optional[set]
    ) -> None:
        """Add columns from a dict to context."""
        for key, val in record_dict.items():
            if CELContextBuilder._should_add_column(key, reserved_names, required_columns):
                context[key] = val
    
    @staticmethod
    def _add_maptype_columns(
        context: Dict[str, Any],
        record_dict: Any,
        reserved_names: set,
        required_columns: Optional[set]
    ) -> None:
        """Add columns from CEL MapType to context."""
        try:
            for key in record_dict:
                if CELContextBuilder._should_add_column(key, reserved_names, required_columns):
                    context[key] = record_dict[key]
        except (TypeError, AttributeError):
            # If iteration fails (not iterable or no __iter__),
            # simple syntax won't work but explicit 'record.column' will
            pass
    
    @staticmethod
    def _add_columns_to_context(
        context: Dict[str, Any],
        record_dict: Any,
        reserved_names: set,
        required_columns: Optional[set]
    ) -> None:
        """Add columns from record_dict to context, respecting filters."""
        if isinstance(record_dict, dict):
            CELContextBuilder._add_dict_columns(context, record_dict, reserved_names, required_columns)
        else:
            # CEL MapType object - may not support iteration
            CELContextBuilder._add_maptype_columns(context, record_dict, reserved_names, required_columns)
    
    @staticmethod
    def _apply_bindings(
        context: Dict[str, Any],
        record_dict: Any,
        bindings: Optional[Dict[str, str]]
    ) -> None:
        """Apply variable bindings to context."""
        if bindings and isinstance(record_dict, dict):
            for var_name, col_name in bindings.items():
                if col_name in record_dict:
                    context[var_name] = record_dict[col_name]
    @staticmethod
    def _add_table_record_with_metadata(
        context: Dict[str, Any],
        record: List[Any],
        metadata: AssetMetadata,
        required_columns: Optional[set],
        bindings: Optional[Dict[str, str]]
    ) -> None:
        """Add record data with metadata to table context."""
        RESERVED_NAMES = {'record', 'record_index'}
        
        # Convert array to named dictionary
        record_dict = CELContextBuilder._build_record_dict(record, metadata)
        context['record'] = record_dict
        
        # Add columns directly to context for simple syntax
        CELContextBuilder._add_columns_to_context(
            context, record_dict, RESERVED_NAMES, required_columns
        )
        
        # Apply variable bindings if provided
        CELContextBuilder._apply_bindings(context, record_dict, bindings)
    
    
    @staticmethod
    def build_context(
        value: Any,
        column_name: str,
        record: Optional[List[Any]],
        metadata: Optional[AssetMetadata],
        record_index: int = 0,
        required_columns: Optional[set] = None,
        bindings: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Build CEL evaluation context from validation data.
        
        WHAT THIS DOES:
        Converts raw validation data into a structured dictionary that CEL
        expressions can evaluate. The context includes both required variables
        (value, column_name, etc.) and optional column access for convenience.
        
        OPTIMIZATION FOR WIDE TABLES:
        When required_columns is provided, only those specific columns are added
        directly to the context (in addition to the full record dict). This is
        critical for assets with many columns (e.g., 100+) to:
        - Reduce memory usage (avoid copying all column values)
        - Improve performance (less data to process)
        - Maintain correctness (record dict still has all columns)
        
        VARIABLE BINDINGS:
        When bindings are provided, generic variable names in the expression are
        mapped to actual column names. This allows reusable validation templates.
        
        PARAMETERS:
            value: The specific column value being validated (e.g., 75000)
            
            column_name: Name of the column being validated (e.g., 'salary')
            
            record: Complete record as array (e.g., [1001, 'John', 75000, 60000])
            
            metadata: Column definitions for mapping array positions to names
            
            record_index: Position of this record in the batch (default: 0)
            
            required_columns: Set of column names to include in context (optional).
                            - If None: ALL columns are added directly to context
                            - If set: ONLY these columns are added directly to context
                            - The record dict always contains ALL columns regardless
                            
                            Example: {'min_salary', 'department'}
                            This adds only min_salary and department as top-level
                            variables, but record dict still has all columns.
            
            bindings: Variable name to column name mapping (optional).
                     Maps generic variable names to actual column names.
                     Example: {'current_value': 'salary', 'minimum': 'min_salary'}
                     Expression 'current_value > minimum' becomes 'salary > min_salary'
        
        RETURNS:
            Dictionary with CEL variables. Structure depends on required_columns:
            
            Without required_columns (all columns added):
            {
                'value': 75000,
                'column_name': 'salary',
                'record_index': 0,
                'record': {'emp_id': 1001, 'name': 'John', 'salary': 75000, 'min_salary': 60000},
                'emp_id': 1001,        # All columns added
                'name': 'John',        # All columns added
                'salary': 75000,       # All columns added
                'min_salary': 60000    # All columns added
            }
            
            With required_columns={'min_salary'}:
            {
                'value': 75000,
                'column_name': 'salary',
                'record_index': 0,
                'record': {'emp_id': 1001, 'name': 'John', 'salary': 75000, 'min_salary': 60000},
                'min_salary': 60000    # Only required column added
            }
            Note: record dict still has all columns, but only min_salary is
            added as a top-level variable for simple syntax access.
        
        USAGE IN CEL EXPRESSIONS:
            After building context, you can use either syntax:
            - Simple: 'value > min_salary' (if min_salary in required_columns or None)
            - Explicit: 'value > record.min_salary' (always works)
            Both work identically!
        
        EXAMPLES:
            Basic usage (all columns):
            >>> context = CELContextBuilder.build_context(
            ...     value=75000,
            ...     column_name='salary',
            ...     record=[1001, 75000, 60000],
            ...     metadata=metadata,
            ...     record_index=5
            ... )
            >>> # All columns available: min_salary, emp_id, etc.
            
            Optimized usage (specific columns only):
            >>> context = CELContextBuilder.build_context(
            ...     value=75000,
            ...     column_name='salary',
            ...     record=[1001, 75000, 60000],
            ...     metadata=metadata,
            ...     record_index=5,
            ...     required_columns={'min_salary'}
            ... )
            >>> # Only min_salary available as top-level variable
            >>> # But record.emp_id still works via record dict
        """
        # Initialize context with required variables
        context = CELContextBuilder._init_base_context(value, column_name, record_index)
        
        # Add record data and columns
        if metadata and record:
            CELContextBuilder._add_record_with_metadata(
                context, record, metadata, required_columns, bindings
            )
        elif record:
            CELContextBuilder._add_record_without_metadata(context, record)
        else:
            context['record'] = {}
        
        return context
    
    @staticmethod
    def build_table_context(
        record: List[Any],
        metadata: AssetMetadata,
        record_index: int = 0,
        required_columns: Optional[set] = None,
        bindings: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Build CEL evaluation context for table-level validation.
        
        WHAT THIS DOES:
        Unlike build_context() which validates a single column value, this method
        builds context for validating the entire record. It does NOT include
        'value' or 'column_name' variables since we're not focused on a specific column.
        
        KEY DIFFERENCES FROM build_context():
        - NO 'value' variable (no single column being validated)
        - NO 'column_name' variable (validating entire record)
        - YES 'record' dict (all columns)
        - YES direct column access (e.g., salary, age, department)
        - YES 'record_index' (position in batch)
        
        OPTIMIZATION FOR WIDE TABLES:
        When required_columns is provided, only those specific columns are added
        directly to the context. This is critical for assets with many columns
        (e.g., 100+) to reduce memory usage and improve performance.
        
        VARIABLE BINDINGS:
        When bindings are provided, generic variable names in the expression are
        mapped to actual column names for reusable validation templates.
        
        PARAMETERS:
            record: Complete record as array (e.g., [1001, 'John', 75000, 60000])
            
            metadata: Column definitions for mapping array positions to names
            
            record_index: Position of this record in the batch (default: 0)
            
            required_columns: Set of column names to include in context (optional).
                            - If None: ALL columns are added directly to context
                            - If set: ONLY these columns are added directly to context
                            - The record dict always contains ALL columns regardless
            
            bindings: Variable name to column name mapping (optional).
                     Maps generic variable names to actual column names.
                     Example: {'current': 'salary', 'minimum': 'min_salary'}
        
        RETURNS:
            Dictionary with CEL variables for table-level validation:
            {
                'record_index': 0,
                'record': {'emp_id': 1001, 'name': 'John', 'salary': 75000, 'min_salary': 60000},
                'emp_id': 1001,        # Direct column access (if in required_columns or None)
                'name': 'John',        # Direct column access (if in required_columns or None)
                'salary': 75000,       # Direct column access (if in required_columns or None)
                'min_salary': 60000    # Direct column access (if in required_columns or None)
            }
        
        USAGE IN CEL EXPRESSIONS:
            After building context, you can use:
            - Simple: 'salary > min_salary && age >= 18'
            - Explicit: 'record.salary > record.min_salary && record.age >= 18'
            Both work identically!
        
        EXAMPLES:
            Basic usage (all columns):
            >>> context = CELContextBuilder.build_table_context(
            ...     record=[1001, 75000, 60000],
            ...     metadata=metadata,
            ...     record_index=5
            ... )
            >>> # All columns available: emp_id, salary, min_salary
            
            Optimized usage (specific columns only):
            >>> context = CELContextBuilder.build_table_context(
            ...     record=[1001, 75000, 60000],
            ...     metadata=metadata,
            ...     record_index=5,
            ...     required_columns={'salary', 'min_salary'}
            ... )
            >>> # Only salary and min_salary available as top-level variables
            >>> # But record.emp_id still works via record dict
        """
        # Initialize context with record_index
        context: Dict[str, Any] = {'record_index': record_index}
        
        # Add record data and columns
        if metadata and record:
            CELContextBuilder._add_table_record_with_metadata(
                context, record, metadata, required_columns, bindings
            )
        else:
            context['record'] = {}
        
        return context
    
    
    @staticmethod
    def _build_record_dict(
        record: List[Any],
        metadata: AssetMetadata
    ) -> Any:
        """
        Convert record array to CEL-compatible object using metadata.
        
        This method maps array positions to column names, creating an
        object that can be used in CEL expressions like:
        'value > record.min_salary'
        
        For celpy, we need to use celpy.json_to_cel() to create proper
        CEL objects that support field selection.
        
        Args:
            record: Record array with values in metadata column order
            metadata: Asset metadata with column definitions
        
        Returns:
            CEL-compatible object (celpy MapType) or dict as fallback
        
        Example:
            >>> record = [1001, 'John', 75000]
            >>> record_obj = CELContextBuilder._build_record_dict(record, metadata)
            >>> # Can now use: record.emp_id, record.name, record.salary
        """
        record_dict = {}
        
        # Map each column to its value
        for idx, column in enumerate(metadata.columns):
            if idx < len(record):
                record_dict[column.name] = record[idx]
            else:
                # Column exists in metadata but not in record
                # Set to None to avoid KeyError in CEL expressions
                record_dict[column.name] = None
        
        # Convert to CEL-compatible object if celpy is available
        # celpy's celtypes.MapType can handle dict-like access
        if celpy:
            try:
                # Use celpy's celtypes to create a proper map
                from celpy import celtypes
                return celtypes.MapType(record_dict)
            except (ImportError, AttributeError, TypeError):
                # Fallback to dict if:
                # - ImportError: celtypes module not available
                # - AttributeError: MapType not found in celtypes
                # - TypeError: MapType constructor fails
                return record_dict
        
        return record_dict
    
    @staticmethod
    def validate_context(context: Dict[str, Any]) -> bool:
        """
        Validate that context has required fields for CEL evaluation.
        
        WHAT THIS DOES:
        Checks if a context dictionary contains all required variables
        before passing it to CEL for evaluation. Prevents runtime errors.
        
        REQUIRED FIELDS:
            - value: The column value being validated
            - column_name: Name of the column
            - record: Dictionary of all column values
        
        OPTIONAL FIELDS (not checked):
            - record_index: Position in batch
            - <column_names>: Direct column access variables
        
        PARAMETERS:
            context: Dictionary to validate
        
        RETURNS:
            True if all required fields present, False otherwise
        
        USE CASE:
            Use this before CEL evaluation to catch missing variables early
            and provide better error messages to users.
        
        EXAMPLES:
            >>> # Valid context
            >>> context = {'value': 100, 'column_name': 'age', 'record': {}}
            >>> is_valid = CELContextBuilder.validate_context(context)
            >>> print(is_valid)  # True
            >>>
            >>> # Invalid context (missing 'record')
            >>> incomplete_context = {'value': 100, 'column_name': 'age'}
            >>> is_valid = CELContextBuilder.validate_context(incomplete_context)
            >>> print(is_valid)  # False
        """
        # Define minimum required fields for CEL evaluation
        required_fields = ['value', 'column_name', 'record']
        
        # Check if all required fields are present in context
        return all(field in context for field in required_fields)
    
    @staticmethod
    def get_available_variables() -> List[str]:
        """
        Get list of core variables available in CEL context.
        
        WHAT THIS RETURNS:
        A list of the standard variables that are always available in
        CEL expressions, regardless of the data being validated.
        
        CORE VARIABLES:
            - value: Current column value being validated
            - record: Dictionary of all column values
            - column_name: Name of the column being validated
            - record_index: Position of record in batch
        
        NOTE: In addition to these core variables, column names are also
        available directly (e.g., 'min_salary', 'age') when metadata is
        provided. This method only returns the core variables.
        
        USE CASES:
            - Documentation generation
            - Error messages showing available variables
            - IDE autocomplete suggestions
            - Validation of CEL expressions
        
        RETURNS:
            List of core variable names
        
        EXAMPLE:
            >>> variables = CELContextBuilder.get_available_variables()
            >>> print(variables)
            >>> # ['value', 'record', 'column_name', 'record_index']
            >>>
            >>> # Use in error message:
            >>> print(f"Available variables: {', '.join(variables)}")
            >>> # Available variables: value, record, column_name, record_index
        """
        return ['value', 'record', 'column_name', 'record_index']

# Made with Bob
