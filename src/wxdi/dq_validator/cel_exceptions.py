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
Custom exceptions for CEL (Common Expression Language) validation.
"""


class CELError(Exception):
    """
    Base exception for CEL-related errors.
    
    This is the parent class for all CEL-specific exceptions.
    """
    pass


class CELCompilationError(CELError):
    """
    Raised when a CEL expression fails to compile.
    
    This indicates a syntax error in the CEL expression and is raised
    during CELCheck initialization (fail-fast approach).
    
    Examples of compilation errors:
    - Invalid syntax: 'value >'
    - Undefined variable: 'unknown_var > 0'
    - Invalid operator: 'value === 100'
    - Mismatched parentheses: 'value > (100'
    
    Example:
        >>> from wxdi.dq_validator import CELCheck
        >>> try:
        ...     check = CELCheck('value >')  # Invalid syntax
        ... except CELCompilationError as e:
        ...     print(f"Compilation failed: {e}")
    """
    pass


class CELEvaluationError(CELError):
    """
    Raised when a CEL expression fails during evaluation.
    
    This indicates a runtime error such as:
    - Type mismatch: 'value + "string"' when value is numeric
    - Null reference: 'record.missing_field > 0'
    - Division by zero: 'value / record.zero_field'
    - Invalid operation: 'value.contains(123)' when value is not a string
    
    Note: This exception is typically caught and converted to a
    ValidationError rather than propagated to the caller.
    
    Example:
        >>> from wxdi.dq_validator import CELCheck
        >>> check = CELCheck('value + record.missing_field')
        >>> # During validation, this will return ValidationError
        >>> # rather than raising CELEvaluationError
    """
    pass

# Made with Bob
