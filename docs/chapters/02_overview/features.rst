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

.. _features:

Features
========

The ``IBM watsonx.data intelligence SDK`` provides a comprehensive set of features organized into modular components.

Common Modules
--------------

Authentication
~~~~~~~~~~~~~~

Unified authentication framework supporting multiple environments:

* **IBM Cloud**: IAM authentication with API keys
* **AWS Cloud**: AWS-specific authentication protocols
* **Government Cloud**: Specialized authentication for government deployments
* **On-Premises**: Username/password and Zen API key authentication

Key features:

* Automatic token management and refresh
* Thread-safe session handling
* SSL verification control for on-premises deployments
* Type-safe configuration with full validation

See :ref:`Authentication<authentication>` for detailed usage.

DQ Validator Module
-------------------

The Data Quality Validator module provides comprehensive in-memory validation capabilities for streaming data and DataFrames.

Core Validation Engine
~~~~~~~~~~~~~~~~~~~~~~

* **Array-based Records**: Optimized for streaming data where records are arrays of values
* **Metadata-driven**: Define table structure and column mappings once, reuse across validations
* **Fluent API**: Chainable method calls for intuitive rule definition
* **Score-based Results**: Each validation returns detailed scores, pass rates, and error details
* **Type Safety**: Full type hints throughout for better IDE support

Data Quality Dimensions
~~~~~~~~~~~~~~~~~~~~~~~

Track validation checks by 8 standard data quality dimensions:

* **Accuracy**: Data correctly represents real-world values
* **Completeness**: Required data is present
* **Conformity**: Data conforms to specified formats
* **Consistency**: Data is consistent across systems
* **Coverage**: Data covers the required scope
* **Timeliness**: Data is up-to-date
* **Uniqueness**: Data has no duplicates where required
* **Validity**: Data is valid according to business rules

Validation Checks
~~~~~~~~~~~~~~~~~

Nine comprehensive validation check types:

1. **LengthCheck**: Validates string length (min, max, exact)
2. **ValidValuesCheck**: Validates against allowed list with case-insensitive option
3. **ComparisonCheck**: Compares values using operators (==, !=, <, >, <=, >=)
4. **CaseCheck**: Validates character case (upper, lower, name, sentence)
5. **CompletenessCheck**: Validates presence (non-null) of values
6. **RangeCheck**: Validates numeric values within min/max range
7. **RegexCheck**: Validates values match regular expression patterns
8. **FormatCheck**: Validates value formats using intelligent format detection
9. **DataTypeCheck**: Validates data types with intelligent type inference

DataFrame Integration
~~~~~~~~~~~~~~~~~~~~~

**Pandas Support**:

* Memory-efficient chunked processing for large DataFrames
* Configurable chunk sizes for optimal performance
* Single validation result column containing all metrics
* Handles DataFrames from thousands to millions of rows

**PySpark Support**:

* Distributed validation using Spark UDFs
* Scalable to billions of rows
* Consistent API with Pandas integration
* Struct column output with all validation metrics

REST API Integration
~~~~~~~~~~~~~~~~~~~~

Integration with IBM Cloud Pak for Data:

* **GlossaryProvider**: Fetch glossary terms and data quality constraints
* **CamsProvider**: Fetch data assets from Catalog Asset Management System
* **AssetsProvider**: Manage data assets and their metadata
* **DimensionsProvider**: Manage data quality dimensions
* **ChecksProvider**: Manage data quality checks
* **IssuesProvider**: Track and manage data quality issues
* **DQSearchProvider**: Search for DQ checks and assets by native ID

Features:

* Thread-safe concurrent access
* Automatic retry with exponential backoff
* Comprehensive error handling
* Type-safe request/response models

Result Consolidation
~~~~~~~~~~~~~~~~~~~~

Aggregate and analyze validation results:

* Overall statistics across all validations
* Per-column statistics and error tracking
* Per-check statistics and pass rates
* Combined statistics with filtering
* Dimension-based issue tracking
* Error retrieval by column, check, or both

Extensibility
~~~~~~~~~~~~~

* **BaseCheck**: Easy to extend with custom validation checks
* **Modular Architecture**: Add new modules without affecting existing functionality
* **Plugin System**: Future support for third-party extensions

Performance
~~~~~~~~~~~

* **Optimized for Speed**: Efficient validation algorithms
* **Memory Efficient**: Chunked processing for large datasets
* **Scalable**: From single records to billions of rows
* **Parallel Processing**: Support for distributed validation with PySpark

Type Safety
~~~~~~~~~~~

* Full type hints throughout the SDK
* Pydantic models for data validation
* IDE autocomplete and type checking support
* Runtime type validation

DPH Services Module
-------------------

Python client library for IBM Data Product Hub API, providing programmatic access to data product management.

Container Management
~~~~~~~~~~~~~~~~~~~~

* Initialize and configure data product containers
* Manage delivery methods and domain structures
* Service credential management
* API key operations

Data Product Lifecycle
~~~~~~~~~~~~~~~~~~~~~~

* Create, update, and delete data products
* Draft management with version control
* Publish drafts to releases
* Retire releases when needed
* Pagination support for large datasets

Contract Terms
~~~~~~~~~~~~~~

* Manage contract terms and documents
* Create reusable contract templates
* Attach terms and conditions to data products
* Service level agreement management

Domain Organization
~~~~~~~~~~~~~~~~~~~

* Create and manage domains and subdomains
* Organize data products by business area
* Multi-industry domain support
* Hierarchical domain structures

Asset Visualization
~~~~~~~~~~~~~~~~~~~

* Create data asset visualizations
* Reinitiate visualizations with updated assets
* Support for multiple assets per visualization

ODCS Generator Module
---------------------

Automated generation of Open Data Contract Standard (ODCS) v3.1.0 compliant YAML files from data catalog metadata.

Multi-Catalog Support
~~~~~~~~~~~~~~~~~~~~~

* **Collibra Integration**: Extract metadata from Collibra data catalog
* **Informatica CDGC**: Extract metadata from Informatica Cloud Data Governance and Catalog
* Extensible architecture for additional catalog sources

Metadata Extraction
~~~~~~~~~~~~~~~~~~~

* Automatic asset metadata extraction via REST APIs
* Column discovery through catalog relations
* Data type mapping (logical and physical)
* Classification support via GraphQL (Collibra)
* Tag integration at asset and column levels
* Custom attribute preservation

ODCS Generation
~~~~~~~~~~~~~~~

* ODCS v3.1.0 compliant YAML output
* Complete schema definition with column metadata
* Data quality rules integration
* Service level agreement specifications
* Governance and ownership information

Data Type Mapping
~~~~~~~~~~~~~~~~~

* Intelligent mapping of catalog types to ODCS types
* Support for logical types (string, integer, number, timestamp, boolean)
* Physical type preservation with precision and scale
* Custom type mapping support

Data Product Recommender Module
--------------------------------

Analyze database query logs to identify high-value tables and logical groupings for data product prioritization.

Multi-Platform Support
~~~~~~~~~~~~~~~~~~~~~~

* **Snowflake**: Query log analysis from ACCOUNT_USAGE.QUERY_HISTORY
* **Databricks**: Query log analysis from system.query.history
* **BigQuery**: Query log analysis from INFORMATION_SCHEMA.JOBS_BY_PROJECT
* **watsonx.data**: Query log analysis from system.runtime.queries

Intelligent Scoring
~~~~~~~~~~~~~~~~~~~

* Query frequency analysis (37.5% weight)
* User diversity metrics (37.5% weight)
* Recency scoring (15% weight)
* Consistency patterns (10% weight)
* Customizable scoring weights

Table Grouping
~~~~~~~~~~~~~~

* Identify tables frequently used together
* Cohesion analysis for logical groupings
* User reach metrics across groups
* Group scoring with multiple factors

Output Formats
~~~~~~~~~~~~~~

* **Markdown**: Human-readable reports with tables and formatting
* **JSON**: Machine-readable format for automation and AI agents
* Star ratings (1-5 stars) for quick assessment
* Detailed metrics and query pattern analysis

CLI and Python API
~~~~~~~~~~~~~~~~~~

* Command-line interface for quick analysis
* Python API for programmatic integration
* File-based input (CSV and JSON)
* Configurable output directory and format

Future Modules
--------------

The SDK's modular architecture is designed to accommodate additional modules from different teams:

* Data profiling and statistics
* Data lineage tracking
* Data catalog integration
* Additional data quality features
* Custom team-specific functionality

Each module can leverage the common authentication and configuration infrastructure while maintaining independence.

Next Steps
----------

* Learn about recent changes in :ref:`Release Notes<release_notes>`
* Find answers to common questions in :ref:`FAQ<faq>`
* Check :ref:`Known Issues<known_issues>` for current limitations
* Start using the SDK with :ref:`Authentication<authentication>`

.. Made with Bob
