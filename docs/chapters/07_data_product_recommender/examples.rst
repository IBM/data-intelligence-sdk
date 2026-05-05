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

.. _data_product_recommender_examples:

Examples
========

Basic Example
-------------

.. code-block:: python

    from wxdi.data_product_recommender.platforms import SnowflakeQueryParser
    from wxdi.data_product_recommender.recommender import DataProductRecommender

    # Initialize with Snowflake parser
    parser = SnowflakeQueryParser()
    recommender = DataProductRecommender(parser)

    # Load and analyze query logs
    recommender.load_query_logs_from_csv_file('query_logs.csv')
    recommender.calculate_metrics()

    # Get top 20 recommendations
    recommendations = recommender.recommend_data_products(num_recommendations=20)

    # Export to Markdown
    recommender.export_recommendations_markdown(recommendations, 'output/recommendations.md')

    # Export to JSON
    recommender.export_recommendations_json(recommendations, 'output/recommendations.json')

Multi-Platform Example
----------------------

.. code-block:: python

    from wxdi.data_product_recommender.platforms import (
        SnowflakeQueryParser,
        DatabricksQueryParser,
        BigQueryQueryParser
    )
    from wxdi.data_product_recommender.recommender import DataProductRecommender

    # Snowflake
    snowflake_parser = SnowflakeQueryParser()
    snowflake_recommender = DataProductRecommender(snowflake_parser)
    snowflake_recommender.load_query_logs_from_csv_file('snowflake_logs.csv')

    # Databricks
    databricks_parser = DatabricksQueryParser()
    databricks_recommender = DataProductRecommender(databricks_parser)
    databricks_recommender.load_query_logs_from_csv_file('databricks_logs.csv')

    # BigQuery
    bigquery_parser = BigQueryQueryParser()
    bigquery_recommender = DataProductRecommender(bigquery_parser)
    bigquery_recommender.load_query_logs_from_csv_file('bigquery_logs.csv')

Custom Scoring Weights
----------------------

.. code-block:: python

    from wxdi.data_product_recommender.platforms import SnowflakeQueryParser
    from wxdi.data_product_recommender.recommender import DataProductRecommender

    parser = SnowflakeQueryParser()
    recommender = DataProductRecommender(parser)

    # Customize scoring weights
    recommender.weights = {
        'query_count': 0.5,      # Emphasize query volume
        'user_diversity': 0.3,   # Moderate user diversity
        'recency': 0.1,          # Less emphasis on recency
        'consistency': 0.1       # Less emphasis on consistency
    }

    recommender.load_query_logs_from_csv_file('query_logs.csv')
    recommender.calculate_metrics()
    recommendations = recommender.recommend_data_products(num_recommendations=20)

See Also
--------

- :ref:`data_product_recommender_usage` - Usage guide
- :ref:`api_data_product_recommender` - API reference
