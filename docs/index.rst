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

IBM watsonx.data intelligence SDK for Python
============================================

The ``IBM watsonx.data intelligence SDK`` for Python is a comprehensive toolkit for data intelligence operations, providing modular components for data quality validation, authentication, and more.

This SDK is designed with a modular architecture, allowing different teams to contribute specialized functionality while sharing common components like authentication. Currently, the SDK includes:

* **Common Modules**: Shared authentication and configuration for all SDK modules
* **DQ Validator**: In-memory data quality validation for streaming data, Pandas DataFrames, and PySpark DataFrames

The ``IBM watsonx.data intelligence SDK`` is supported on Python 3.8+.

Key Features
------------

**Data Quality Validation**
   Comprehensive validation framework with 9 check types, support for array-based records and DataFrames, and integration with IBM Cloud Pak for Data.

**Multi-Environment Authentication**
   Unified authentication supporting IBM Cloud, AWS Cloud, Government Cloud, and on-premises deployments.

**Modular Architecture**
   Extensible design allowing teams to add new modules while sharing common functionality.

**Type Safety**
   Full type hints throughout the SDK for better IDE support and code quality.

.. toctree::
   :maxdepth: 3
   :hidden:

   chapters/01_welcome/index
   chapters/02_overview/index
   chapters/03_common_modules/index
   chapters/04_dq_validator/index
   chapters/05_future_modules/index
   api/index

.. Made with Bob
