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

.. _dq_validator:

DQ Validator Module
===================

The **DQ Validator** module provides comprehensive in-memory data quality validation capabilities for streaming data records, Pandas DataFrames, and PySpark DataFrames.

This module is designed for high-performance validation with support for:

* **Array-based Records**: Optimized for streaming data
* **Pandas DataFrames**: Memory-efficient chunked processing
* **PySpark DataFrames**: Distributed validation at scale
* **REST API Integration**: Integration with IBM Cloud Pak for Data

Key Capabilities
----------------

**Validation Engine**
   Core validation framework with metadata-driven rules and fluent API

**Nine Check Types**
   Comprehensive validation coverage including length, format, datatype, range, regex, and more

**Data Quality Dimensions**
   Track validations across 8 standard DQ dimensions (Accuracy, Completeness, Conformity, etc.)

**Result Consolidation**
   Aggregate and analyze validation results with detailed statistics

**REST API Integration**
   Fetch rules from glossary, report issues, and integrate with IBM Cloud Pak for Data

.. toctree::
   :maxdepth: 3
   :hidden:

   core_concepts
   validation_checks
   dataframe_integration
   rest_api_integration
   examples

.. note::
   This documentation is under active development. More detailed content will be added in upcoming releases.

.. Made with Bob
