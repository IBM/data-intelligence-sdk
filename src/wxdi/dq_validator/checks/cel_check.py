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
CEL (Common Expression Language) validation check.

This module provides the CELCheck class which allows customers to define
custom validation logic using Google's Common Expression Language (CEL).

Package: cel-python (from cel-expr-python project)
GitHub: https://github.com/cel-expr/cel-python
PyPI: https://pypi.org/project/cel-python/
"""

import warnings
from typing import Any, Dict, Optional
from ..base import BaseCheck, ValidationError
from ..data_quality_dimension import DataQualityDimension
from ..cel_context import CELContextBuilder
from ..cel_exceptions import CELCompilationError, CELEvaluationError

# Import celpy from cel-python package (Google's official CEL implementation)
# Package name: cel-python
# Import name: celpy
# Source: https://github.com/cel-expr/cel-python
try:
    import celpy
except ImportError as e:
    raise ImportError(
        "cel-python is required for CELCheck. "
        "This is a Python implementation of Google's Common Expression Language (CEL). "
        "Install it with: pip install cel-python>=0.5.0"
    ) from e


class CELCheck(BaseCheck):
    """
    Validates data using CEL (Common Expression Language) expressions.
    
    OVERVIEW:
    CEL is a non-Turing complete expression language designed for safe,
    fast evaluation. This check allows customers to define custom validation
    logic without modifying code.
    
    This implementation uses Google's official CEL Python implementation
    from the cel-expr-python project (package: cel-python, import: celpy).
    
    ⚠️ IMPORTANT - CASE SENSITIVITY:
    Column names are CASE-SENSITIVE. 'birth_date' and 'Birth_date' are different.
    'firstName' and 'First_Name' are different. Use exact column names from metadata.
    
    SYNTAX OPTIONS:
    CEL expressions support two syntax styles for accessing column values:
    
    1. SIMPLE SYNTAX (RECOMMENDED):
       - Direct column access: 'min_salary', 'age', 'department'
       - More intuitive for clients
       - Examples: 'value > min_salary', 'age > 40', 'department == "Sales"'
    
    2. EXPLICIT SYNTAX (STILL SUPPORTED):
       - Prefixed access: 'record.min_salary', 'record.age', 'record.department'
       - Required for columns with reserved names (value, column_name, record_index, record)
       - Examples: 'value > record.min_salary', 'record.age > 40'
    
    Both syntaxes work identically and can be mixed in the same expression.
    
    AVAILABLE VARIABLES:
    ┌─────────────────┬──────────────────────────────────────────────────────┐
    │ Variable        │ Description                                          │
    ├─────────────────┼──────────────────────────────────────────────────────┤
    │ value           │ Current column value being validated                 │
    │ column_name     │ Name of the column being validated                   │
    │ record_index    │ Position of record in batch (0-based)                │
    │ record          │ Dict of all columns: {'col1': val1, 'col2': val2}    │
    │ <column_names>  │ Direct access to each column (e.g., min_salary)      │
    └─────────────────┴──────────────────────────────────────────────────────┘
    
    SUPPORTED OPERATORS:
    - Comparison: ==, !=, <, <=, >, >=
    - Logical: &&, ||, !
    - Arithmetic: +, -, *, /, %
    - String: contains, startsWith, endsWith, matches
    - List: in, size, all, exists
    - Ternary: condition ? true_value : false_value
    
    EXAMPLES:
        Simple value check:
        >>> check = CELCheck('value > 0')
        
        Multi-column comparison (SIMPLE SYNTAX):
        >>> check = CELCheck('value > min_salary')
        
        Multi-column comparison (EXPLICIT SYNTAX):
        >>> check = CELCheck('value > record.min_salary')
        
        Complex business logic with simple syntax:
        >>> check = CELCheck(
        ...     expression='age > 40 ? value >= 80000 : value >= 50000',
        ...     error_message='Salary does not meet age-based requirements'
        ... )
        
        String operations:
        >>> check = CELCheck('value.endsWith("@company.com")')
        
        List operations:
        >>> check = CELCheck('value in ["Active", "Pending", "Approved"]')
        
        Department-based validation:
        >>> check = CELCheck('department == "Sales" ? value <= 20000 : value <= 10000')
        
        Arithmetic operations:
        >>> check = CELCheck('value >= min_salary * 1.2')
    
    RESERVED NAMES:
    If your data has columns named 'value', 'column_name', 'record_index', or 'record',
    you must use explicit syntax: 'record.value' instead of 'value'.
    
    PERFORMANCE:
    CEL expressions are compiled once at initialization and reused for all
    validations, providing excellent performance (~10-100 microseconds per record).
    """
    
    # Maximum expression length to prevent abuse
    MAX_EXPRESSION_LENGTH = 1000
    
    def __init__(
        self,
        expression: str,
        error_message: Optional[str] = None,
        dimension: DataQualityDimension = DataQualityDimension.VALIDITY,
        description: Optional[str] = None,
        bindings: Optional[Dict[str, str]] = None
    ):
        """
        Initialize CEL validation check.
        
        WHAT THIS DOES:
        Compiles the CEL expression at initialization (fail-fast approach).
        If the expression has syntax errors, CELCompilationError is raised
        immediately rather than during validation.
        
        PARAMETERS:
            expression: CEL expression that must evaluate to boolean.
                       Supports both simple ('min_salary') and explicit ('record.min_salary') syntax.
                       Available variables: value, column_name, record_index, record, <column_names>
                       
                       With bindings, you can use generic variable names that map to actual columns.
            
            error_message: Custom error message (optional).
                          If not provided, generates: "CEL validation failed: <expression>"
            
            dimension: Data quality dimension (default: VALIDITY).
                      Options: COMPLETENESS, VALIDITY, CONSISTENCY, ACCURACY, etc.
            
            description: Human-readable description of the check (optional).
                        If not provided, uses: "CEL: <expression>"
            
            bindings: Variable name to column name mapping (optional).
                     Allows generic expressions with placeholder variables.
                     Example: {'current_value': 'salary', 'minimum': 'min_salary'}
                     Expression: 'current_value > minimum'
                     Maps to columns: salary > min_salary
        
        RAISES:
            ValueError: If expression is empty, whitespace-only, or exceeds 1000 characters
            CELCompilationError: If expression has syntax errors or invalid CEL syntax
        
        EXAMPLES:
            Basic usage:
            >>> check = CELCheck('value > 0')
            
            Simple syntax (recommended):
            >>> check = CELCheck('value > min_salary')
            
            Explicit syntax:
            >>> check = CELCheck('value > record.min_salary')
            
            Complex validation with custom message:
            >>> check = CELCheck(
            ...     expression='age > 40 ? value >= 80000 : value >= 50000',
            ...     error_message='Salary does not meet age-based requirements',
            ...     dimension=DataQualityDimension.VALIDITY,
            ...     description='Age-based salary validation'
            ... )
            
            String validation:
            >>> check = CELCheck(
            ...     expression='value.endsWith("@company.com")',
            ...     error_message='Email must be from company domain'
            ... )
            
            Variable binding (generic expressions):
            >>> check = CELCheck(
            ...     expression='current_value > minimum && person_age >= 18',
            ...     bindings={
            ...         'current_value': 'salary',
            ...         'minimum': 'min_salary',
            ...         'person_age': 'age'
            ...     },
            ...     error_message='Salary and age requirements not met'
            ... )
            
            Reusable template with bindings:
            >>> # Same expression, different columns
            >>> salary_check = CELCheck(
            ...     expression='current > minimum',
            ...     bindings={'current': 'salary', 'minimum': 'min_salary'}
            ... )
            >>> bonus_check = CELCheck(
            ...     expression='current > minimum',
            ...     bindings={'current': 'bonus', 'minimum': 'min_bonus'}
            ... )
        """
        super().__init__(dimension)
        
        # Validate and set expression
        self.expression = self._validate_expression(expression)
        
        # Set metadata
        self.error_message = error_message
        self.description = description or f"CEL: {self.expression}"
        
        # Validate and set bindings
        self.bindings = self._validate_bindings(bindings or {})
        
        # Compile CEL expression
        self._env, self._ast, self._program = self._compile_expression()
        
        # Extract required columns for optimization
        self._required_columns = self._extract_column_references()
    
    def _validate_expression(self, expression: str) -> str:
        """Validate and normalize the CEL expression."""
        if not expression or not expression.strip():
            raise ValueError("CEL expression cannot be empty")
        
        normalized = expression.strip()
        
        if len(normalized) > self.MAX_EXPRESSION_LENGTH:
            raise ValueError(
                f"CEL expression too long: {len(normalized)} characters "
                f"(max: {self.MAX_EXPRESSION_LENGTH})"
            )
        
        return normalized
    
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
    
    def _compile_expression(self):
        """Compile the CEL expression and return environment, AST, and program."""
        try:
            env = celpy.Environment()
            ast = env.compile(self.expression)
            program = env.program(ast)
            return env, ast, program
        except Exception as e:
            raise CELCompilationError(
                f"Failed to compile CEL expression '{self.expression}': {str(e)}"
            ) from e
    
    def _extract_column_references(self) -> Optional[set]:
        """
        Extract column names referenced in the CEL expression from compiled AST.
        
        OPTIMIZATION PURPOSE:
        For assets with many columns (e.g., 100+ columns), adding all columns
        to the CEL context is wasteful. This method attempts to extract only
        the columns actually used from the compiled CEL AST.
        
        FALLBACK STRATEGY:
        If AST traversal fails or is unreliable, returns None to indicate
        that ALL columns should be included in the context. This ensures
        correctness over optimization, especially for non-standard column names.
        
        EXTRACTION STRATEGY:
        1. Traverse the compiled CEL AST to find variable references
        2. Filter out reserved names (value, column_name, record_index, record)
        3. If traversal fails, return None (use all columns)
        
        EXAMPLES:
            Expression: 'value > min_salary'
            Returns: {'min_salary'}
            
            Expression: 'record.age > 40 ? value >= 80000 : value >= 50000'
            Returns: {'age'}
            
            Expression: 'department == "Sales" && value > min_salary'
            Returns: {'department', 'min_salary'}
            
            If AST traversal fails:
            Returns: None (caller should use all columns)
        
        RETURNS:
            Set of column names, or None if all columns should be used
        """
        RESERVED = {'value', 'column_name', 'record_index', 'record'}
        
        try:
            required_columns = set()
            self._extract_identifiers_from_node(self._ast, required_columns, RESERVED)
            return required_columns if required_columns else None
        except (AttributeError, TypeError, RuntimeError):
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
                continue
    
    def validate_column_references(self, available_columns: list) -> None:
        """
        Validate that column references in expression exist in the provided list.
        
        ⚠️ OPTIONAL VALIDATION:
        This method provides early validation of column references. Call it after
        initialization if you want to catch column name errors before runtime.
        
        WHAT THIS DOES:
        Checks if columns referenced in the CEL expression exist in the provided
        list of available columns. Raises ValueError with helpful error message
        if any columns are missing.
        
        WHEN TO USE:
        - After creating CELCheck, before adding to validator
        - When you have metadata and want early error detection
        - To catch typos or case mismatches before validation runs
        
        PARAMETERS:
            available_columns: List of valid column names (e.g., from metadata.columns)
        
        RAISES:
            ValueError: If expression references columns not in available_columns.
                       Error message includes:
                       - List of missing columns
                       - Case sensitivity reminder
                       - List of available columns
        
        EXAMPLES:
            Basic usage:
            >>> metadata = AssetMetadata(columns=[
            ...     ColumnMetadata('birth_date', DataType.DATE),
            ...     ColumnMetadata('first_name', DataType.STRING)
            ... ])
            >>> check = CELCheck('birth_date != null')
            >>> check.validate_column_references([c.name for c in metadata.columns])
            >>> # No error - column exists
            
            Catch case mismatch:
            >>> check = CELCheck('Birth_date != null')  # Wrong case
            >>> check.validate_column_references(['birth_date', 'first_name'])
            ValueError: CEL expression references non-existent column(s):
              - 'Birth_date' not found
            
            Note: Column names are CASE-SENSITIVE.
            Available columns: 'birth_date', 'first_name'
            
            Multiple missing columns:
            >>> check = CELCheck('Birth_date != null && LastName != null')
            >>> check.validate_column_references(['birth_date', 'first_name'])
            ValueError: CEL expression references non-existent column(s):
              - 'Birth_date' not found
              - 'LastName' not found
            
            Note: Column names are CASE-SENSITIVE.
            Available columns: 'birth_date', 'first_name'
        """
        if not self._required_columns:
            # Could not extract columns from AST - issue warning and skip validation
            warnings.warn(
                f"Unable to validate column references for CEL expression '{self.expression}'. "
                "Column extraction from AST failed. Validation will occur at runtime.",
                UserWarning,
                stacklevel=2
            )
            return
        
        if not available_columns:
            # No columns provided - skip validation
            return
        
        # Find missing columns
        missing = [col for col in self._required_columns if col not in available_columns]
        
        if missing:
            error_parts = [
                "CEL expression references non-existent column(s):"
            ]
            for col_name in sorted(missing):
                error_parts.append(f"\n  - '{col_name}' not found")
            
            error_parts.append(
                "\n\n⚠️  Column names are CASE-SENSITIVE. "
                "'birth_date' and 'Birth_date' are different."
            )
            error_parts.append(
                f"\nAvailable columns: {', '.join(repr(c) for c in sorted(available_columns))}"
            )
            
            raise ValueError(''.join(error_parts))
    
    def get_check_name(self) -> str:
        """
        Return the name of this check type.
        
        Returns:
            'cel_check'
        """
        return "cel_check"
    
    def validate(
        self,
        value: Any,
        context: Dict[str, Any]
    ) -> Optional[ValidationError]:
        """
        Validate value using CEL expression.
        
        This method:
        1. Builds CEL evaluation context from validation context
        2. Evaluates the compiled CEL expression
        3. Checks that result is boolean
        4. Returns ValidationError if expression evaluates to False
        
        Args:
            value: The value to validate
            context: Validation context containing:
                - column_name: Name of the column being validated
                - record: Full record array
                - metadata: AssetMetadata object
                - record_index: Record position (optional)
        
        Returns:
            ValidationError if validation fails, None if passes
        
        Example:
            >>> check = CELCheck('value > 100')
            >>> context = {
            ...     'column_name': 'age',
            ...     'record': [1001, 'John', 25],
            ...     'metadata': metadata,
            ...     'record_index': 0
            ... }
            >>> error = check.validate(25, context)
            >>> if error:
            ...     print(error.message)  # "CEL validation failed: value > 100"
        """
        column_name = context.get('column_name', 'unknown')
        
        try:
            # Build CEL context and evaluate expression
            cel_context = self._build_cel_context(value, column_name, context)
            result = self._program.evaluate(cel_context)
            
            # Convert result to boolean and validate
            return self._process_evaluation_result(result, value, column_name)
            
        except CELEvaluationError as e:
            return self._create_evaluation_error(column_name, value, str(e))
        except Exception as e:
            return self._create_unexpected_error(column_name, value, str(e))
    
    def _build_cel_context(self, value: Any, column_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build CEL evaluation context from validation context."""
        return CELContextBuilder.build_context(
            value=value,
            column_name=column_name,
            record=context.get('record'),
            metadata=context.get('metadata'),
            record_index=context.get('record_index', 0),
            required_columns=self._required_columns,
            bindings=self.bindings
        )
    
    def _process_evaluation_result(
        self,
        result: Any,
        value: Any,
        column_name: str
    ) -> Optional[ValidationError]:
        """Process CEL evaluation result and return ValidationError if needed."""
        # Convert celpy BoolType to Python bool
        result_bool = self._convert_to_bool(result)
        
        if result_bool is None:
            # Expression didn't return boolean
            return ValidationError(
                column_name=column_name,
                check_name=self.get_check_name(),
                message=(
                    f"CEL expression must return boolean, got {type(result).__name__}. "
                    f"Expression: '{self.expression}'"
                ),
                value=value
            )
        
        # Check validation result
        if not result_bool:
            error_msg = self.error_message or f"CEL validation failed: {self.expression}"
            return ValidationError(
                column_name=column_name,
                check_name=self.get_check_name(),
                message=error_msg,
                value=value,
                expected=f"Expression '{self.expression}' to be true"
            )
        
        return None
    
    def _convert_to_bool(self, result: Any) -> Optional[bool]:
        """Convert CEL result to Python bool, or None if not boolean."""
        if hasattr(result, '__bool__'):
            return bool(result)
        elif isinstance(result, bool):
            return result
        return None
    
    def _create_evaluation_error(self, column_name: str, value: Any, error_msg: str) -> ValidationError:
        """Create ValidationError for CEL evaluation errors."""
        return ValidationError(
            column_name=column_name,
            check_name=self.get_check_name(),
            message=f"CEL evaluation error: {error_msg}",
            value=value
        )
    
    def _create_unexpected_error(self, column_name: str, value: Any, error_msg: str) -> ValidationError:
        """Create ValidationError for unexpected errors."""
        return ValidationError(
            column_name=column_name,
            check_name=self.get_check_name(),
            message=f"Unexpected error in CEL validation: {error_msg}",
            value=value
        )
    
    def __repr__(self) -> str:
        """
        String representation of the check.
        
        Returns:
            String showing the CEL expression
        
        Example:
            >>> check = CELCheck('value > 100')
            >>> print(check)
            CELCheck(expression='value > 100')
        """
        return f"CELCheck(expression='{self.expression}')"
    
    def get_expression(self) -> str:
        """
        Get the CEL expression.
        
        Returns:
            The CEL expression string
        
        Example:
            >>> check = CELCheck('value > 100')
            >>> print(check.get_expression())
            value > 100
        """
        return self.expression
    
    def get_description(self) -> str:
        """
        Get the check description.
        
        Returns:
            Human-readable description of the check
        
        Example:
            >>> check = CELCheck('value > 100', description='Age must exceed 100')
            >>> print(check.get_description())
            Age must exceed 100
        """
        return self.description

# Made with Bob
