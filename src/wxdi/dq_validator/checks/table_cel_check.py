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
Table-level CEL (Common Expression Language) validation check.

Unlike CELCheck which validates a single column value, TableCELCheck validates
the entire record for cross-column business logic.
"""

import warnings
from typing import Any, Optional, Dict, Set
try:
    import celpy
except ImportError:
    raise ImportError(
        "cel-python is required for CEL expression support. "
        "Install it with: pip install cel-python>=0.5.0"
    )

from ..base import BaseCheck, ValidationError
from ..data_quality_dimension import DataQualityDimension
from ..cel_context import CELContextBuilder
from ..cel_exceptions import CELCompilationError, CELEvaluationError


class TableCELCheck(BaseCheck):
    """
    CEL expression check for table-level validation.
    
    Unlike CELCheck which validates a single column value, TableCELCheck validates
    the entire record. This enables:
    - Cross-column validation (e.g., start_date < end_date)
    - Complex business rules spanning multiple fields
    - Conditional logic based on multiple columns
    
    ⚠️ IMPORTANT - CASE SENSITIVITY:
    Column names are CASE-SENSITIVE. 'birth_date' and 'Birth_date' are different.
    'firstName' and 'First_Name' are different. Use exact column names from metadata.
    
    Available Variables in CEL Expression:
    - Column names: Direct access to any column (e.g., salary, age, department)
    - record: Dictionary of all column values (e.g., record.salary, record.age)
    - record_index: Position of the record in the batch
    
    Note: Unlike CELCheck, there is NO 'value' or 'column_name' variable since
    we're validating the entire record, not a specific column.
    
    Example:
        >>> from wxdi.dq_validator import TableValidationRule, TableCELCheck
        >>> 
        >>> # Multi-column validation
        >>> rule = TableValidationRule('salary_check')
        >>> rule.add_check(TableCELCheck(
        ...     'salary > min_salary && age >= 18',
        ...     error_message='Invalid salary/age combination'
        ... ))
        >>> 
        >>> # Complex business rules
        >>> rule = TableValidationRule('department_rules')
        >>> rule.add_check(TableCELCheck(
        ...     'department == "Sales" ? salary >= 50000 : salary >= 40000',
        ...     error_message='Salary does not meet department requirements'
        ... ))
        >>> 
        >>> # Cross-column consistency
        >>> rule = TableValidationRule('date_check')
        >>> rule.add_check(TableCELCheck(
        ...     'start_date < end_date',
        ...     error_message='Start date must be before end date'
        ... ))
    """
    
    def __init__(
        self,
        expression: str,
        error_message: Optional[str] = None,
        dimension: DataQualityDimension = DataQualityDimension.VALIDITY,
        bindings: Optional[Dict[str, str]] = None
    ):
        """
        Initialize table-level CEL check.
        
        Args:
            expression: CEL expression that evaluates to boolean
                       Can reference any column by name (e.g., 'salary > min_salary')
                       With bindings, can use generic variable names
            error_message: Custom error message (optional)
            dimension: Data quality dimension (default: VALIDITY)
            bindings: Variable name to column name mapping (optional)
                     Example: {'current': 'salary', 'minimum': 'min_salary'}
                     Expression: 'current > minimum' maps to 'salary > min_salary'
        
        Raises:
            CELCompilationError: If expression cannot be compiled
        
        Example:
            >>> check = TableCELCheck(
            ...     'salary > min_salary && age >= 18',
            ...     error_message='Invalid salary/age combination'
            ... )
            
            >>> # With bindings
            >>> check = TableCELCheck(
            ...     'current > minimum && person_age >= 18',
            ...     bindings={'current': 'salary', 'minimum': 'min_salary', 'person_age': 'age'},
            ...     error_message='Invalid salary/age combination'
            ... )
        """
        super().__init__(dimension)
        self.expression = expression
        self.error_message = error_message or f"Table-level CEL check failed: {expression}"
        
        # Validate and set bindings
        self.bindings = self._validate_bindings(bindings or {})
        
        # Compile CEL expression
        self._ast, self._program = self._compile_expression(expression)
        
        # Extract required columns for performance optimization
        self._required_columns = self._extract_column_references()
    
    def _validate_bindings(self, bindings: Dict[str, str]) -> Dict[str, str]:
        """Validate the bindings dictionary."""
        if not bindings:
            return {}
        
        if not isinstance(bindings, dict):
            raise ValueError("bindings must be a dictionary")
        
        for var_name, col_name in bindings.items():
            if not isinstance(var_name, str) or not isinstance(col_name, str):
                raise ValueError("binding keys and values must be strings")
            if not var_name or not col_name:
                raise ValueError("binding keys and values cannot be empty")
        
        return bindings
    
    def _compile_expression(self, expression: str):
        """Compile the CEL expression and return AST and program."""
        try:
            env = celpy.Environment()
            ast = env.compile(expression)
            program = env.program(ast)
            return ast, program
        except Exception as e:
            raise CELCompilationError(
                f"Failed to compile CEL expression '{expression}': {e}"
            )
    
    def _extract_column_references(self) -> Optional[Set[str]]:
        """
        Extract column names referenced in the CEL expression from compiled AST.
        
        This enables performance optimization by only adding required columns
        to the CEL context, which is critical for wide tables (100+ columns).
        
        Returns:
            Set of column names, or None if extraction fails (safe fallback)
        """
        RESERVED = {'record', 'record_index', 'true', 'false', 'null'}
        
        try:
            required_columns = set()
            self._extract_identifiers_from_node(self._ast, required_columns, RESERVED)
            return required_columns if required_columns else None
        except Exception:
            # AST traversal failed - return None to indicate all columns should be used
            return None
    
    def _extract_identifiers_from_node(self, node: Any, columns: set, reserved: set) -> None:
        """Helper method to recursively extract identifiers from AST node."""
        if node is None:
            return
        
        # Check if this is an identifier node
        if hasattr(node, 'name') and isinstance(node.name, str):
            if node.name not in reserved:
                columns.add(node.name)
        
        # Check for select expressions (record.field)
        if hasattr(node, 'operand') and hasattr(node, 'field'):
            if hasattr(node.field, 'name') and isinstance(node.field.name, str):
                columns.add(node.field.name)
        
        # Recursively process child nodes
        self._process_child_nodes(node, columns, reserved)
    
    def _process_child_nodes(self, node: Any, columns: set, reserved: set) -> None:
        """Helper method to process child nodes of an AST node."""
        for attr_name in dir(node):
            if attr_name.startswith('_'):
                continue
            try:
                attr = getattr(node, attr_name, None)
                if attr is None or callable(attr):
                    continue
                if isinstance(attr, list):
                    for item in attr:
                        self._extract_identifiers_from_node(item, columns, reserved)
                elif hasattr(attr, '__dict__'):
                    self._extract_identifiers_from_node(attr, columns, reserved)
            except (AttributeError, TypeError):
                # Ignore errors during AST traversal
                continue
    
    def validate(self, value: Any, context: Dict[str, Any]) -> Optional[ValidationError]:
        """
        Validate entire record using CEL expression.
        
        Args:
            value: Ignored for table-level checks (always None)
            context: Must contain 'record', 'metadata', and 'rule_name'
        
        Returns:
            ValidationError if validation fails, None if passes
        
        Raises:
            ValueError: If required context keys are missing
            CELEvaluationError: If CEL evaluation fails
        """
        record = context.get('record')
        metadata = context.get('metadata')
        rule_name = context.get('rule_name', 'table_rule')
        record_index = context.get('record_index', 0)
        
        if record is None or metadata is None:
            raise ValueError(
                "Table-level CEL check requires 'record' and 'metadata' in context"
            )
        
        # Build CEL context (no 'value', only record columns)
        # Apply bindings if provided to map generic variable names to actual columns
        cel_context = CELContextBuilder.build_table_context(
            record=record,
            metadata=metadata,
            record_index=record_index,
            required_columns=self._required_columns,
            bindings=self.bindings
        )
        
        # Evaluate CEL expression
        try:
            result = self._program.evaluate(cel_context)
            
            # Convert CEL result to Python bool
            # CEL returns BoolType, IntType, etc., not native Python types
            try:
                result_bool = bool(result)
            except (TypeError, ValueError) as e:
                # Catch specific exceptions when converting to bool
                raise CELEvaluationError(
                    f"CEL expression must return boolean-compatible value, got {type(result).__name__}: {result}"
                ) from e
            
            # If expression evaluates to False, validation failed
            if not result_bool:
                return ValidationError(
                    column_name=rule_name,  # Use rule name instead of column
                    check_name=self.get_check_name(),
                    message=self.error_message,
                    value=record
                )
            
            return None
            
        except CELEvaluationError:
            raise
        except Exception as e:
            raise CELEvaluationError(
                f"CEL evaluation failed for expression '{self.expression}': {e}"
            )
    
    def get_check_name(self) -> str:
        """Return the name of this check type"""
        return "table_cel_check"
    
    def validate_column_references(self, available_columns: list) -> None:
        """
        Validate that all column references in the expression exist in metadata.
        
        This is an optional validation step that can be called after initialization
        to catch column name errors early (before runtime evaluation).
        
        Args:
            available_columns: List of valid column names from metadata
        
        Raises:
            ValueError: If expression references non-existent columns
        
        Example:
            >>> metadata = AssetMetadata(columns=[
            ...     ColumnMetadata('salary', DataType.DECIMAL),
            ...     ColumnMetadata('age', DataType.INTEGER)
            ... ])
            >>> check = TableCELCheck('salary > min_salary')
            >>> check.validate_column_references([c.name for c in metadata.columns])
            ValueError: CEL expression references non-existent column(s): 'min_salary'
        """
        if self._required_columns is None:
            # Could not extract columns from AST - issue warning and skip validation
            warnings.warn(
                f"Unable to validate column references for table CEL expression '{self.expression}'. "
                "Column extraction from AST failed. Validation will occur at runtime.",
                UserWarning,
                stacklevel=2
            )
            return
        
        available_set = set(available_columns)
        missing_columns = self._required_columns - available_set
        
        if missing_columns:
            missing_list = "', '".join(sorted(missing_columns))
            available_list = "', '".join(sorted(available_columns))
            
            raise ValueError(
                f"CEL expression references non-existent column(s):\n"
                f"  - '{missing_list}' not found\n"
                f"\n"
                f"⚠️  Column names are CASE-SENSITIVE.\n"
                f"Available columns: '{available_list}'"
            )
    
    def __repr__(self) -> str:
        return f"TableCELCheck(expression='{self.expression}')"

# Made with Bob
