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

.. _api_dq_validator:

DQ Validator Module API
========================

The DQ Validator module provides comprehensive in-memory data quality validation.

.. toctree::
   :maxdepth: 2

   core
   metadata
   checks
   integrations
   providers
   results

Overview
--------

The DQ Validator module includes:

* **Core Classes** - Validator, ValidationRule, BaseCheck
* **Metadata** - AssetMetadata, ColumnMetadata, DataType
* **Validation Checks** - Nine comprehensive check types
* **DataFrame Integration** - Pandas and PySpark validators
* **REST API Providers** - IBM Cloud Pak for Data integration
* **Result Consolidation** - Result aggregation and analysis

Module Organization
-------------------

The module is organized into several sub-packages:

* ``dq_validator`` - Core validation engine
* ``dq_validator.checks`` - Validation check implementations
* ``dq_validator.integrations`` - DataFrame validators
* ``dq_validator.provider`` - REST API providers

.. Made with Bob
