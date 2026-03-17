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

.. _api_ref:

API Reference
=============

The ``IBM watsonx.data intelligence SDK`` for Python provides comprehensive APIs organized by module.

This API reference documentation is auto-generated from the source code docstrings and provides detailed information about all classes, methods, and functions.

.. toctree::
   :maxdepth: 2

   common/index
   dq_validator/index

Module Organization
-------------------

Common Modules
~~~~~~~~~~~~~~

Shared functionality used across all SDK modules:

* :ref:`Authentication<api_common_auth>` - Multi-environment authentication

DQ Validator Module
~~~~~~~~~~~~~~~~~~~

In-memory data quality validation:

* :ref:`Core Classes<api_dq_validator_core>` - Validator, ValidationRule, ValidationResult
* :ref:`Metadata<api_dq_validator_metadata>` - AssetMetadata, ColumnMetadata, DataType
* :ref:`Validation Checks<api_dq_validator_checks>` - All 9 validation check types
* :ref:`DataFrame Integration<api_dq_validator_integrations>` - Pandas and PySpark validators
* :ref:`REST API Providers<api_dq_validator_providers>` - IBM Cloud Pak for Data integration
* :ref:`Result Consolidation<api_dq_validator_results>` - Result aggregation and analysis

Navigation Tips
---------------

* Use the search function to find specific classes or methods
* Click on class names to see detailed documentation
* Method signatures include type hints for parameters and return values
* Examples are provided where applicable

Conventions
-----------

**Type Hints**

All APIs include comprehensive type hints:

.. code-block:: python

    def validate(self, record: List[Any], record_index: int = 0) -> ValidationResult:
        """Validate a single record."""
        pass

**Optional Parameters**

Optional parameters are indicated with ``Optional[Type]``:

.. code-block:: python

    def __init__(self, url: Optional[str] = None):
        """Initialize with optional URL."""
        pass

**Return Types**

Return types are clearly documented:

.. code-block:: python

    def get_token(self) -> str:
        """
        Returns:
            str: The authentication token
        """
        pass

.. Made with Bob
