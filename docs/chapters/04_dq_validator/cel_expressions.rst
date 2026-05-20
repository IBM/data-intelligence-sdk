CEL Expression Validation
==========================

Overview
--------

The Data Intelligence SDK supports **CEL (Common Expression Language)** for defining custom validation rules. CEL is a non-Turing complete expression language developed by Google that provides a safe, fast way to evaluate expressions without the security risks of arbitrary code execution.

CEL expressions allow you to:

- Define complex validation logic without writing Python code
- Reference multiple columns in a single validation rule
- Use conditional logic (ternary operators) for context-dependent validation
- Perform string operations, arithmetic, and logical comparisons
- Validate data against business rules that span multiple fields

.. warning::
   **Column Names are CASE-SENSITIVE**
   
   CEL expressions use exact string matching for column names. ``birth_date`` and ``Birth_date`` are different columns.
   ``firstName`` and ``First_Name`` are different columns. Always use the exact column name as defined in your metadata.
   
   **Examples:**
   
   - ✅ Correct: ``birth_date != null`` (matches metadata column ``birth_date``)
   - ❌ Wrong: ``Birth_date != null`` (case mismatch)
   - ❌ Wrong: ``BIRTH_DATE != null`` (case mismatch)
   - ❌ Wrong: ``birthDate != null`` (different name)

Installation
------------

CEL support requires the ``cel-python`` package:

.. code-block:: bash

   pip install cel-python>=0.5.0

Or install the full SDK which includes CEL support:

.. code-block:: bash

   pip install data-intelligence-sdk
Complete Examples
-----------------

For complete working examples, see:

- ``examples/cel_usage.py`` - CEL expressions with batch validation
- ``examples/cel_pandas_dataframe_usage.py`` - CEL expressions with Pandas DataFrames

- ``examples/table_cel_usage.py`` - Table-level CEL expressions for cross-column validation

CEL Validation Types
--------------------

The SDK supports two types of CEL validation:

**Column-Level CEL (CELCheck)**
   Validates individual column values. Has access to the ``value`` variable representing the current column being validated.
   
   Use for: Single-column validation, value range checks, format validation.

**Table-Level CEL (TableCELCheck)**
   Validates entire records for cross-column business logic. Does NOT have a ``value`` variable since it validates the whole record.
   
   Use for: Cross-column validation, multi-field business rules, date consistency checks.

.. code-block:: python

   from wxdi.dq_validator import (
       Validator, ValidationRule, TableValidationRule,
       CELCheck, TableCELCheck
   )
   
   validator = Validator(metadata)
   
   # Column-level: Validates 'salary' column
   validator.add_rule(
       ValidationRule('salary')
           .add_check(CELCheck('value > 0'))
   )
   
   # Table-level: Validates entire record
   validator.add_table_rule(
       TableValidationRule('salary_check')
           .add_check(TableCELCheck('salary > min_salary && age >= 18'))
   )


Basic Usage
-----------

Simple Value Validation
~~~~~~~~~~~~~~~~~~~~~~~

The most basic CEL expression validates a single value:

.. code-block:: python

   from wxdi.dq_validator import Validator, ValidationRule, CELCheck
   
   # Create validator
   validator = Validator(metadata)
   
   # Add CEL check for positive values
   validator.add_rule(
       ValidationRule('salary')
           .add_check(CELCheck(
               expression='value > 0',
               error_message='Salary must be positive'
           ))
   )

Multi-Column Validation
~~~~~~~~~~~~~~~~~~~~~~~

CEL expressions can reference other columns in the same record directly by column name:

.. code-block:: python

   # Salary must exceed minimum salary (SIMPLE SYNTAX - RECOMMENDED)
   validator.add_rule(
       ValidationRule('salary')
           .add_check(CELCheck(
               expression='value > min_salary',
               error_message='Salary below minimum threshold'
           ))
   )
   
   # Alternative: Explicit syntax with 'record.' prefix (also supported)
   validator.add_rule(
       ValidationRule('salary')
           .add_check(CELCheck(
               expression='value > record.min_salary',
               error_message='Salary below minimum threshold'
           ))
   )

.. note::
   **Both syntaxes work identically!** The simple syntax (``min_salary``) is recommended for better readability,
   especially for clients who may not be familiar with CEL. The explicit syntax (``record.min_salary``) is still
   supported for advanced users who prefer namespace clarity.

Available Variables
-------------------

CEL expressions have access to the following variables:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Variable
     - Description
   * - ``value``
     - The current column value being validated
   * - ``column_name`` (any)
     - **Direct column access**: Reference any column by name (e.g., ``min_salary``, ``age``, ``department``)
   * - ``record``
     - Dictionary-like object for explicit access (e.g., ``record.min_salary``) - optional, use for clarity
   * - ``column_name``
     - Name of the column being validated (string)
   * - ``record_index``
     - Position of the record in the batch (integer, 0-based)

**Syntax Options:**

You can reference other columns in two ways:

1. **Simple Syntax (Recommended):** ``min_salary``, ``age``, ``department``
   
   - More intuitive for clients
   - Cleaner, easier to read
   - No namespace prefix needed

2. **Explicit Syntax (Optional):** ``record.min_salary``, ``record.age``, ``record.department``
   
   - Provides namespace clarity
   - Useful when you want to be explicit
   - Required for columns with reserved names (see below)

.. warning::
   **Reserved Column Names:** If your data has columns named ``value``, ``column_name``, ``record_index``, or ``record``,
   you **must** use the explicit syntax (``record.value``) to access them. The simple syntax won't work for these
   reserved names to avoid conflicts with CEL's built-in variables.
   
   Example: If you have a column named "value", use ``record.value`` instead of just ``value``.

Supported Operators
-------------------

Comparison Operators
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Equal to
   CELCheck('value == 100')
   
   # Not equal to
   CELCheck('value != 0')
   
   # Greater than
   CELCheck('value > 50')
   
   # Greater than or equal
   CELCheck('value >= 50')
   
   # Less than
   CELCheck('value < 100')
   
   # Less than or equal
   CELCheck('value <= 100')

Logical Operators
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # AND operator
   CELCheck('value > 0 && value < 100')
   
   # OR operator
   CELCheck('value < 0 || value > 100')
   
   # NOT operator
   CELCheck('!(value == 0)')

Arithmetic Operators
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Addition
   CELCheck('value == record.base_salary + record.bonus')
   
   # Subtraction
   CELCheck('value == record.total - record.deductions')
   
   # Multiplication
   CELCheck('value == record.price * record.quantity')
   
   # Division
   CELCheck('value == record.total / record.count')
   
   # Modulo
   CELCheck('value % 10 == 0')  # Must be multiple of 10

String Operations
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Starts with
   CELCheck('value.startsWith("admin_")')
   
   # Ends with
   CELCheck('value.endsWith("@company.com")')
   
   # Contains (using 'in' operator)
   CELCheck('"@" in value')

List Operations
~~~~~~~~~~~~~~~

.. code-block:: python

   # Value in list
   CELCheck('value in ["Active", "Pending", "Approved"]')
   
   # Value not in list
   CELCheck('!(value in ["Deleted", "Archived"])')

Conditional Logic
-----------------

Ternary Operator
~~~~~~~~~~~~~~~~

CEL supports ternary (conditional) expressions using the ``? :`` syntax:

.. code-block:: python

   # Age-based salary requirements
   validator.add_rule(
       ValidationRule('salary')
           .add_check(CELCheck(
               expression='record.age > 40 ? value >= 80000 : value >= 50000',
               error_message='Salary does not meet age-based requirements'
           ))
   )

This expression reads as: "If age > 40, then salary must be >= 80000, otherwise salary must be >= 50000"

Complex Conditions
~~~~~~~~~~~~~~~~~~

You can nest conditions and combine them with logical operators:

.. code-block:: python

   # Department-based bonus limits
   validator.add_rule(
       ValidationRule('bonus')
           .add_check(CELCheck(
               expression='record.department == "Sales" ? value <= 20000 : value <= 10000',
               error_message='Bonus exceeds department limit'
           ))
   )

Advanced Examples
-----------------

Range Validation
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Value must be between two columns
   CELCheck('value >= record.min_value && value <= record.max_value')

Business Rule Validation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Sales employees must be at least 21
   validator.add_rule(
       ValidationRule('age')
           .add_check(CELCheck(
               expression='value >= 21 || record.department != "Sales"',
               error_message='Sales employees must be at least 21 years old'
           ))
   )

Email Domain Validation
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Email must be from company domain
   validator.add_rule(
       ValidationRule('email')
           .add_check(CELCheck(
               expression='value.endsWith("@company.com")',
               error_message='Email must be from company domain'
           ))
   )

Status Validation
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Status must be one of allowed values
   validator.add_rule(
       ValidationRule('status')
           .add_check(CELCheck(
               expression='value in ["Active", "Pending", "Approved"]',
               error_message='Invalid status value'
           ))
   )

Combining with Other Checks
----------------------------

CEL checks can be combined with other validation checks:

.. code-block:: python

   from wxdi.dq_validator import CompletenessCheck, RangeCheck
   
   validator.add_rule(
       ValidationRule('salary')
           .add_check(CompletenessCheck())  # Must not be null
           .add_check(RangeCheck(min_value=0, max_value=1000000))  # Range check
           .add_check(CELCheck('value > record.min_salary'))  # CEL check
   )

Error Handling
--------------

Compilation Errors
~~~~~~~~~~~~~~~~~~

CEL expressions are compiled at initialization. If an expression has syntax errors, a ``CELCompilationError`` is raised immediately:

.. code-block:: python

   from wxdi.dq_validator.cel_exceptions import CELCompilationError
   
   try:
       check = CELCheck('value >')  # Incomplete expression
   except CELCompilationError as e:
       print(f"Invalid CEL expression: {e}")

Runtime Errors
~~~~~~~~~~~~~~

If an error occurs during evaluation (e.g., type mismatch, null reference), the check returns a ``ValidationError`` rather than raising an exception:

.. code-block:: python

   # This will handle null values gracefully
   check = CELCheck('value != null')
   
   # Validation will return an error if evaluation fails
   error = check.validate(None, context)
   if error:
       print(error.message)

Best Practices
--------------

1. **Keep Expressions Simple**
   
   - Prefer simple, readable expressions over complex nested logic
   - Break complex rules into multiple checks when possible

2. **Use Descriptive Error Messages**
   
   .. code-block:: python
   
      CELCheck(
          expression='value > 0',
          error_message='Salary must be a positive number'
      )

3. **Test Expressions with Sample Data**
   
   - Verify expressions work with your actual data before deployment
   - Test edge cases (null values, boundary conditions)

4. **Consider Performance**
   
   - CEL expressions are compiled once and reused
   - Evaluation is very fast (~10-100 microseconds per record)
   - Suitable for high-throughput validation

5. **Document Complex Logic**
   
   .. code-block:: python
   
      # Senior employees (age > 40) must earn at least $80,000
      # Junior employees must earn at least $50,000
      CELCheck(
          expression='record.age > 40 ? value >= 80000 : value >= 50000',
          description='Age-based salary requirements'
      )

Integration with DataFrames
----------------------------

CEL checks work seamlessly with both Pandas and Spark DataFrames:

Pandas Integration
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wxdi.dq_validator import PandasValidator
   import pandas as pd
   
   # Create DataFrame
   df = pd.DataFrame({
       'emp_id': [1001, 1002],
       'salary': [75000, 85000],
       'min_salary': [60000, 70000]
   })
   
   # Validate with CEL
   validator = PandasValidator(metadata)
   validator.add_rule(
       ValidationRule('salary')
           .add_check(CELCheck('value > record.min_salary'))
   )
   
   results = validator.validate(df)

Spark Integration
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wxdi.dq_validator import SparkValidator
   from pyspark.sql import SparkSession
   
   # Create Spark DataFrame
   spark = SparkSession.builder.getOrCreate()
   df = spark.createDataFrame([
       (1001, 75000, 60000),
       (1002, 85000, 70000)
   ], ['emp_id', 'salary', 'min_salary'])
   
   # Validate with CEL
   validator = SparkValidator(metadata)
   validator.add_rule(
       ValidationRule('salary')
           .add_check(CELCheck('value > record.min_salary'))
   )
   
   results = validator.validate(df)

Limitations
-----------

1. **Non-Turing Complete**
   
   - CEL does not support loops or recursion
   - Cannot define custom functions
   - This is by design for security and performance

2. **Expression Length**
   
   - Maximum expression length: 1000 characters
   - This prevents abuse and ensures reasonable performance

3. **Type Safety**
   
   - CEL expressions must return boolean values
   - Type mismatches are caught at runtime and reported as validation errors

4. **No Side Effects**
   
   - CEL expressions cannot modify data
   - They can only read values and return boolean results

API Reference
-------------

CELCheck Class
~~~~~~~~~~~~~~

.. code-block:: python

   class CELCheck(BaseCheck):
       def __init__(
           self,
           expression: str,
           error_message: Optional[str] = None,
           dimension: DataQualityDimension = DataQualityDimension.VALIDITY,
           description: Optional[str] = None
       )

**Parameters:**

- ``expression`` (str): CEL expression that must evaluate to boolean
- ``error_message`` (str, optional): Custom error message for validation failures
- ``dimension`` (DataQualityDimension, optional): Data quality dimension (default: VALIDITY)
- ``description`` (str, optional): Human-readable description of the check

**Methods:**

- ``validate(value, context)``: Validate a value using the CEL expression
- ``get_expression()``: Get the CEL expression string
- ``get_description()``: Get the check description

CEL Exceptions
~~~~~~~~~~~~~~

.. code-block:: python

   from wxdi.dq_validator.cel_exceptions import (
       CELError,              # Base exception
       CELCompilationError,   # Syntax errors at initialization
       CELEvaluationError     # Runtime errors during evaluation
   )

Table-Level CEL Validation
---------------------------

Table-level CEL validation enables cross-column business rules and complex validation logic that spans multiple fields.

Overview
~~~~~~~~

Unlike column-level CEL (``CELCheck``) which validates individual column values, table-level CEL (``TableCELCheck``) validates entire records. This is essential for:

- Cross-column validation (e.g., ``start_date < end_date``)
- Complex business rules spanning multiple fields
- Conditional logic based on multiple columns
- Record-level consistency checks

Key Differences
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Column-Level CEL (CELCheck)
     - Table-Level CEL (TableCELCheck)
   * - Validates single column value
     - Validates entire record
   * - Has ``value`` variable
     - NO ``value`` variable
   * - Use: ``ValidationRule('column')``
     - Use: ``TableValidationRule('rule_name')``
   * - Example: ``value > 0``
     - Example: ``salary > min_salary``

Basic Table-Level Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wxdi.dq_validator import (
       Validator, TableValidationRule, TableCELCheck
   )
   
   validator = Validator(metadata)
   
   # Simple cross-column comparison
   validator.add_table_rule(
       TableValidationRule('salary_check')
           .add_check(TableCELCheck(
               'salary > min_salary',
               error_message='Salary must exceed minimum'
           ))
   )

Complex Business Rules
~~~~~~~~~~~~~~~~~~~~~~

Table-level CEL excels at complex, multi-field business logic:

.. code-block:: python

   # Age-based salary requirements
   validator.add_table_rule(
       TableValidationRule('age_salary_check')
           .add_check(TableCELCheck(
               'age > 40 ? salary >= 80000 : salary >= 50000',
               error_message='Salary does not meet age-based requirements'
           ))
   )
   
   # Department-specific rules
   validator.add_table_rule(
       TableValidationRule('dept_rules')
           .add_check(TableCELCheck(
               'department == "Sales" ? (salary >= 50000 && age >= 21) : salary >= 40000',
               error_message='Department requirements not met'
           ))
   )
   
   # Date consistency
   validator.add_table_rule(
       TableValidationRule('date_check')
           .add_check(TableCELCheck(
               'start_date < end_date',
               error_message='Start date must be before end date'
           ))
   )

Multiple Table Rules
~~~~~~~~~~~~~~~~~~~~

You can combine multiple table-level rules for comprehensive validation:

.. code-block:: python

   validator = Validator(metadata)
   
   # Rule 1: Salary validation
   validator.add_table_rule(
       TableValidationRule('salary_check')
           .add_check(TableCELCheck('salary > min_salary'))
   )
   
   # Rule 2: Age validation
   validator.add_table_rule(
       TableValidationRule('age_check')
           .add_check(TableCELCheck('age >= 18 && age <= 65'))
   )
   
   # Rule 3: Bonus limits
   validator.add_table_rule(
       TableValidationRule('bonus_check')
           .add_check(TableCELCheck('bonus <= salary * 0.3'))
   )

Combining Column and Table Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For comprehensive validation, combine both column-level and table-level rules:

.. code-block:: python

   validator = Validator(metadata)
   
   # Column-level: Individual field validation
   validator.add_rule(
       ValidationRule('email')
           .add_check(CompletenessCheck())
           .add_check(FormatCheck('email'))
   )
   
   validator.add_rule(
       ValidationRule('age')
           .add_check(RangeCheck(min_value=0, max_value=120))
   )
   
   # Table-level: Cross-field business rules
   validator.add_table_rule(
       TableValidationRule('business_rules')
           .add_check(TableCELCheck(
               'salary > min_salary && age >= 18',
               error_message='Invalid salary/age combination'
           ))
   )

Available Variables
~~~~~~~~~~~~~~~~~~~

Table-level CEL expressions have access to:

- **Column names**: Direct access to any column (e.g., ``salary``, ``age``, ``department``)
- **record**: Dictionary of all column values (e.g., ``record.salary``, ``record.age``)
- **record_index**: Position of the record in the batch

**Note:** Unlike column-level CEL, there is NO ``value`` or ``column_name`` variable.

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

Table-level CEL automatically optimizes for wide tables by extracting only required columns from the expression:

.. code-block:: python

   # Expression: 'salary > min_salary && age >= 18'
   # Only adds: salary, min_salary, age to context
   # Not all 100+ columns
   
   check = TableCELCheck('salary > min_salary && age >= 18')
   # check._required_columns = {'salary', 'min_salary', 'age'}

This optimization is critical for assets with many columns (100+) to reduce memory usage and improve performance.

Column Reference Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Validate column references before runtime:

.. code-block:: python

   check = TableCELCheck('salary > max_salary')  # max_salary doesn't exist
   
   # Validate against metadata
   try:
       check.validate_column_references([c.name for c in metadata.columns])
   except ValueError as e:
       print(e)
       # CEL expression references non-existent column(s):
       #   - 'max_salary' not found
       # 
       # ⚠️  Column names are CASE-SENSITIVE.
       # Available columns: 'salary', 'min_salary', 'age', ...

Best Practices
~~~~~~~~~~~~~~

1. **Use table-level for cross-column validation**: When validation depends on multiple fields
2. **Use column-level for single-field checks**: When validating individual column values
3. **Combine both approaches**: For comprehensive validation coverage
4. **Keep expressions readable**: Break complex logic into multiple rules
5. **Use descriptive rule names**: For better error tracking and debugging
6. **Validate column references**: Call ``validate_column_references()`` after initialization

Complete Table-Level Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See ``examples/table_cel_usage.py`` for a complete working example demonstrating:

- Multi-column comparisons
- Complex business rules
- Department-specific validation
- Date consistency checks
- Combining column and table rules


Complete Example
----------------

Here's a complete example demonstrating various CEL features:

.. code-block:: python

   from wxdi.dq_validator import (
       Validator, ValidationRule, CELCheck,
       AssetMetadata, ColumnMetadata, DataType
   )
   
   # Define metadata
   metadata = AssetMetadata(
       table_name='employees',
       columns=[
           ColumnMetadata('emp_id', DataType.INTEGER),
           ColumnMetadata('name', DataType.STRING),
           ColumnMetadata('email', DataType.STRING),
           ColumnMetadata('age', DataType.INTEGER),
           ColumnMetadata('department', DataType.STRING),
           ColumnMetadata('salary', DataType.DECIMAL),
           ColumnMetadata('min_salary', DataType.DECIMAL),
           ColumnMetadata('bonus', DataType.DECIMAL),
           ColumnMetadata('status', DataType.STRING)
       ]
   )
   
   # Create validator with CEL checks
   validator = Validator(metadata)
   
   # Simple value validation
   validator.add_rule(
       ValidationRule('salary')
           .add_check(CELCheck('value > 0'))
   )
   
   # Multi-column comparison (SIMPLE SYNTAX)
   validator.add_rule(
       ValidationRule('salary')
           .add_check(CELCheck('value > min_salary'))
   )
   
   # Conditional logic (SIMPLE SYNTAX)
   validator.add_rule(
       ValidationRule('salary')
           .add_check(CELCheck(
               'age > 40 ? value >= 80000 : value >= 50000',
               error_message='Salary does not meet age-based requirements'
           ))
   )
   
   # String validation
   validator.add_rule(
       ValidationRule('email')
           .add_check(CELCheck(
               'value.endsWith("@company.com")',
               error_message='Email must be from company domain'
           ))
   )
   
   # List membership
   validator.add_rule(
       ValidationRule('status')
           .add_check(CELCheck(
               'value in ["Active", "Pending", "Approved"]',
               error_message='Invalid status value'
           ))
   )
   
   # Department-based rules (SIMPLE SYNTAX)
   validator.add_rule(
       ValidationRule('bonus')
           .add_check(CELCheck(
               'department == "Sales" ? value <= 20000 : value <= 10000',
               error_message='Bonus exceeds department limit'
           ))
   )
   
   # Validate records
   records = [
       [1001, 'John Doe', 'john@company.com', 30, 'Engineering', 75000, 60000, 5000, 'Active'],
       [1002, 'Jane Smith', 'jane@company.com', 45, 'Sales', 85000, 70000, 18000, 'Active']
   ]
   
   results = validator.validate_batch(records)
   
   # Process results
   for idx, result in enumerate(results):
       if result.is_valid:
           print(f"Record {idx + 1}: PASS")
       else:
           print(f"Record {idx + 1}: FAIL")
           for error in result.errors:
               print(f"  - {error.column_name}: {error.message}")

See Also
--------

- :doc:`validation_checks` - Overview of all validation check types
- :doc:`core_concepts` - Core concepts of the DQ Validator
- :doc:`examples` - More examples and use cases
- `CEL Specification <https://github.com/google/cel-spec>`_ - Official CEL language specification

.. Made with Bob
