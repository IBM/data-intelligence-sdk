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

.. _data_product_recommender:

Data Product Recommender
=========================

Analyze database query logs to identify high-value tables and logical groupings for data product prioritization.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   usage_guide
   examples

Overview
--------

The ``data_product_recommender`` module analyzes query log files to identify which tables should be prioritized as data products in a data marketplace.

Key Features
------------

**Multi-Platform Support**
   Supports Snowflake, Databricks, BigQuery, and watsonx.data query log formats.

**File-Based Input**
   Works with CSV and JSON query log files (no direct database connection required).

**Intelligent Scoring**
   Combines query frequency, user diversity, recency, and consistency metrics.

**Table Grouping**
   Identifies tables frequently used together for logical data product groupings.

**Multiple Output Formats**
   Generates both Markdown (human-readable) and JSON (agent-consumable) reports.

**CLI and Python API**
   Use from command line or integrate into applications.

Quick Start
-----------

Command Line
~~~~~~~~~~~~

.. code-block:: bash

    python -m wxdi.data_product_recommender.cli \
      --platform snowflake \
      --input-file query_logs.csv \
      --output output \
      --num-recommendations 20

Python API
~~~~~~~~~~

.. code-block:: python

    from wxdi.data_product_recommender.platforms import SnowflakeQueryParser
    from wxdi.data_product_recommender.recommender import DataProductRecommender

    # Initialize
    parser = SnowflakeQueryParser()
    recommender = DataProductRecommender(parser)

    # Load and analyze
    recommender.load_query_logs_from_csv_file('query_logs.csv')
    recommender.calculate_metrics()
    recommendations = recommender.recommend_data_products(num_recommendations=20)

    # Export
    recommender.export_recommendations_markdown(recommendations, 'output/recommendations.md')

Use Cases
---------

**Accelerate Data Product Onboarding**
   Leverage existing usage patterns rather than starting from scratch.

**Identify High-Value Assets**
   Find tables with demonstrated business value through real usage.

**Discover Logical Groupings**
   Identify tables commonly used together for cohesive data products.

**Prioritize Catalog Promotion**
   Focus efforts on tables with highest user demand and diversity.

Next Steps
----------

- :ref:`data_product_recommender_usage` - Detailed usage guide
- :ref:`data_product_recommender_examples` - Code examples
- :ref:`api_data_product_recommender` - API reference
