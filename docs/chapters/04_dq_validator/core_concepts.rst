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

.. _dq_validator_core_concepts:

Core Concepts
=============

The DQ Validator module is built around several core concepts that work together to provide comprehensive data quality validation.

.. note::
   This section provides an overview of core concepts. Detailed API documentation is available in the :ref:`API Reference<api_ref>`.

Metadata
--------

Metadata defines the structure of your data and is the foundation of validation.

AssetMetadata
~~~~~~~~~~~~~

Represents a data asset (table) with its columns:

.. code-block:: python

    from wxdi.dq_validator import AssetMetadata, ColumnMetadata, DataType

    metadata = AssetMetadata(
        table_name="customers",
        columns=[
            ColumnMetadata(name="customer_id", data_type=DataType.INTEGER, position=0),
            ColumnMetadata(name="email", data_type=DataType.STRING, position=1),
            ColumnMetadata(name="age", data_type=DataType.INTEGER, position=2)
        ]
    )

ColumnMetadata
~~~~~~~~~~~~~~

Defines individual column properties:

* ``name``: Column name
* ``data_type``: Expected data type
* ``position``: Position in the record array (0-based)

Validator
---------

The main validation engine that applies rules to records.

.. code-block:: python

    from wxdi.dq_validator import Validator

    validator = Validator(metadata)
    validator.add_rule(rule1)
    validator.add_rule(rule2)
    
    result = validator.validate(record)

ValidationRule
--------------

Defines validation logic for a specific column.

.. code-block:: python

    from wxdi.dq_validator import ValidationRule
    from wxdi.dq_validator.checks import CompletenessCheck, LengthCheck

    rule = ValidationRule("email")
    rule.add_check(CompletenessCheck())
    rule.add_check(LengthCheck(min_length=5, max_length=100))

Validation Checks
-----------------

Individual validation checks that can be added to rules. See :ref:`Validation Checks<dq_validator_validation_checks>` for details.

ValidationResult
----------------

Contains the results of validating a single record:

.. code-block:: python

    result = validator.validate(record)
    
    print(f"Score: {result.validation_score}")
    print(f"Pass Rate: {result.pass_rate}%")
    print(f"Errors: {len(result.errors)}")

Data Quality Dimensions
-----------------------

Validation checks are categorized by 8 standard data quality dimensions:

* **Accuracy**: Data correctly represents real-world values
* **Completeness**: Required data is present
* **Conformity**: Data conforms to specified formats
* **Consistency**: Data is consistent across systems
* **Coverage**: Data covers the required scope
* **Timeliness**: Data is up-to-date
* **Uniqueness**: Data has no duplicates where required
* **Validity**: Data is valid according to business rules

For more information, see the :ref:`API Reference<api_ref>`.

.. Made with Bob
