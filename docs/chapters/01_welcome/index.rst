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

.. _welcome:

Welcome
=======

Welcome to the ``IBM watsonx.data intelligence SDK`` for Python documentation!

If you're new to the SDK or installing it for the first time, be sure to check out the :ref:`Prerequisites<prerequisites>` and :ref:`Installation and Versioning<installation>` sections for help setting up and installing the SDK.

You can find details on the latest releases, FAQs, known issues, and more in the :ref:`Overview<overview>` section.

SDK Modules
-----------

The SDK provides several powerful modules for data intelligence and governance:

**Data Quality Validator**
   Comprehensive data quality validation framework with support for multiple check types, integration with Pandas and PySpark DataFrames, and CEL (Common Expression Language) for complex validation rules. See :ref:`DQ Validator<dq_validator>` for details.

**Data Product Hub Services**
   Python client library for IBM Data Product Hub API, enabling programmatic management of data products, containers, contract terms, and the complete data product lifecycle from creation to retirement. See :ref:`Data Product Hub Services<dph_services>` for details.

**ODCS Generator**
   Automated generation of Open Data Contract Standard (ODCS) v3.1.0 compliant YAML files from enterprise data catalogs including Collibra and Informatica CDGC. Streamlines data contract creation by extracting and transforming catalog metadata. See :ref:`ODCS Generator<odcs_generator>` for details.

**Data Product Recommender**
   Intelligent analysis of database query logs to identify high-value tables and logical groupings for data product prioritization. Supports multiple platforms (Snowflake, Databricks, BigQuery, watsonx.data) and provides actionable recommendations based on usage patterns. See :ref:`Data Product Recommender<data_product_recommender>` for details.

Getting Started
---------------

If you already have the SDK installed and are looking to get started using it, please refer to the :ref:`Common Modules<common_modules>` section for authentication setup, and explore the individual module documentation for specific use cases.

Looking for documentation on the SDK's interfaces and abstractions? Please check out our :ref:`API Reference Documentation<api_ref>` for an in-depth breakdown of all the SDK's classes, properties, and methods - including detailed descriptions of any required or optional parameters.

.. toctree::
   :maxdepth: 3
   :hidden:

   prereqs
   installation
   versioning

.. Made with Bob
