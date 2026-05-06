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

.. _data_product_recommender_usage:

Usage Guide
===========

Installation
------------

.. code-block:: bash

    pip install -e .

CLI Usage
---------

.. code-block:: bash

    python -m wxdi.data_product_recommender.cli \
      --platform snowflake \
      --input-file query_logs.csv \
      --output output \
      --num-recommendations 20 \
      --min-score 60.0

Options
~~~~~~~

- ``--platform`` - Database platform (snowflake, databricks, bigquery, watsonxdata)
- ``--input-file`` - Path to CSV or JSON query log file
- ``--output`` - Output directory (default: output)
- ``--output-format`` - Output format: markdown or json (default: markdown)
- ``--num-recommendations`` - Number of recommendations (default: 20)
- ``--min-score`` - Minimum score threshold 0-100

Python API
----------

.. code-block:: python

    from wxdi.data_product_recommender.platforms import SnowflakeQueryParser
    from wxdi.data_product_recommender.recommender import DataProductRecommender

    # Initialize
    parser = SnowflakeQueryParser()
    recommender = DataProductRecommender(parser)

    # Load query logs
    recommender.load_query_logs_from_csv_file('query_logs.csv')

    # Calculate metrics
    recommender.calculate_metrics()

    # Get recommendations
    recommendations = recommender.recommend_data_products(
        num_recommendations=20,
        min_score=60.0
    )

    # Export results
    recommender.export_recommendations_markdown(recommendations, 'output/recommendations.md')
    recommender.export_recommendations_json(recommendations, 'output/recommendations.json')

See Also
--------

- :ref:`data_product_recommender_examples` - Complete examples
- :ref:`api_data_product_recommender` - API reference
