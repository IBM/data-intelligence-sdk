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

The ``IBM watsonx.data intelligence SDK`` for Python is a comprehensive toolkit for data intelligence operations, providing modular components for data quality validation, data product management, ODCS generation, and intelligent recommendations.

This SDK is designed with a modular architecture, allowing different teams to contribute specialized functionality while sharing common components like authentication. Currently, the SDK includes:

* **Common Modules**: Shared authentication and configuration for all SDK modules
* **DQ Validator**: In-memory data quality validation for streaming data, Pandas DataFrames, and PySpark DataFrames
* **DPH Services**: Python client for IBM Data Product Hub API
* **ODCS Generator**: Generate Open Data Contract Standard files from data catalogs
* **Data Product Recommender**: Analyze query logs to identify high-value data products

The ``IBM watsonx.data intelligence SDK`` is supported on Python 3.8+.

Key Features
------------

**Data Quality Validation**
   Comprehensive validation framework with 9 check types, support for array-based records and DataFrames, and integration with IBM Cloud Pak for Data.

**Data Product Hub Integration**
   Complete Python SDK for managing data products, drafts, releases, contract terms, and domains.

**ODCS Generation**
   Automated generation of ODCS v3.1.0 compliant YAML files from Collibra and Informatica catalogs.

**Intelligent Recommendations**
   Query log analysis to identify high-value tables and logical groupings for data product prioritization.

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
   chapters/05_dph_services/index
   chapters/06_odcs_generator/index
   chapters/07_data_product_recommender/index
   chapters/08_future_modules/index
   api/index

.. Made with Bob
