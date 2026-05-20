..
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

.. _dq_validator_validation_checks:

Validation Checks
=================

The DQ Validator module provides ten comprehensive validation check types.

.. note::
   This section provides an overview. Detailed API documentation with all parameters is available in the :ref:`API Reference<api_ref>`.

Available Checks
----------------

1. **LengthCheck** - Validates string length
2. **ValidValuesCheck** - Validates against allowed values
3. **ComparisonCheck** - Compares values using operators
4. **CaseCheck** - Validates character case
5. **CompletenessCheck** - Validates non-null values
6. **RangeCheck** - Validates numeric ranges
7. **RegexCheck** - Validates regex patterns
8. **FormatCheck** - Validates value formats
9. **DataTypeCheck** - Validates data types
10. **CELCheck** - Validates using CEL (Common Expression Language) expressions

CEL Expression Check
--------------------

The **CELCheck** enables custom validation logic using Google's Common Expression Language (CEL). This powerful check type allows you to:

- Define complex validation rules without writing Python code
- Reference multiple columns in a single expression
- Use conditional logic for context-dependent validation
- Perform string operations, arithmetic, and logical comparisons

Quick Example
~~~~~~~~~~~~~

.. code-block:: python

   from wxdi.dq_validator import CELCheck
   
   # Simple value check
   check = CELCheck('value > 0')
   
   # Multi-column comparison
   check = CELCheck('value > record.min_salary')
   
   # Conditional logic
   check = CELCheck('record.age > 40 ? value >= 80000 : value >= 50000')

For comprehensive documentation on CEL expressions, see :doc:`cel_expressions`.

For detailed usage examples and API documentation, see the :ref:`API Reference<api_ref>`.

.. Made with Bob
