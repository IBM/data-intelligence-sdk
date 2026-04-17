# coding: utf-8

# Copyright 2026 IBM Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Example usage of Data Product Recommender

This example demonstrates how to use the Data Product Recommender to analyze
query logs and generate recommendations for data products.
"""

from wxdi.data_product_recommender.platforms import SnowflakeQueryParser
from wxdi.data_product_recommender.recommender import DataProductRecommender


def main():
    """Example: Analyze Snowflake query logs from a CSV file"""

    # Initialize platform-specific parser
    print("Initializing Snowflake query parser...")
    parser = SnowflakeQueryParser()

    # Initialize recommender
    recommender = DataProductRecommender(parser)

    # Load query logs from CSV file
    # Replace with your actual query log file path
    csv_file_path = 'path/to/your/query_logs.csv'

    print(f"\nLoading query logs from: {csv_file_path}")
    try:
        recommender.load_query_logs_from_csv_file(csv_file_path)
    except FileNotFoundError:
        print(f"Error: File not found: {csv_file_path}")
        print("Please update the csv_file_path variable with your actual query log file.")
        return

    # Calculate metrics
    print("\nCalculating table metrics...")
    recommender.calculate_metrics()

    # Generate recommendations
    print("\nGenerating recommendations...")
    recommendations = recommender.recommend_data_products(
        num_recommendations=20,
        min_score=50.0  # Only include tables with score >= 50
    )

    # Export recommendations as Markdown (human-readable)
    output_file_md = 'output/recommendations_example.md'
    print(f"\nExporting recommendations to: {output_file_md}")
    recommender.export_recommendations_markdown(recommendations, output_file_md)

    # Export recommendations as JSON (agent-consumable)
    output_file_json = 'output/recommendations_example.json'
    print(f"Exporting recommendations to: {output_file_json}")
    recommender.export_recommendations_json(recommendations, output_file_json)

    # Print summary
    print("\n✓ Analysis complete!")
    print(f"  - Queries analyzed: {len(recommender.query_logs):,}")
    print(f"  - Tables identified: {len(recommender.table_metrics)}")
    print(f"  - Recommendations: {len(recommendations['individual_tables'])}")
    if 'table_groups' in recommendations:
        print(f"  - Table groups: {len(recommendations['table_groups'])}")
    print(f"  - Markdown output: {output_file_md}")
    print(f"  - JSON output: {output_file_json}")


def example_with_json_input():
    """Example: Analyze query logs from a JSON file"""

    from wxdi.data_product_recommender.platforms import DatabricksQueryParser

    # Initialize for Databricks
    parser = DatabricksQueryParser()
    recommender = DataProductRecommender(parser)

    # Load from JSON file
    json_file_path = 'path/to/your/query_logs.json'
    recommender.load_query_logs_from_json_file(json_file_path)

    # Calculate and generate recommendations
    recommender.calculate_metrics()
    recommendations = recommender.recommend_data_products(num_recommendations=15)

    # Export
    recommender.export_recommendations_markdown(recommendations, 'output/databricks_recommendations.md')


def example_with_custom_scoring():
    """Example: Use custom scoring weights"""

    from wxdi.data_product_recommender.platforms import BigQueryQueryParser

    parser = BigQueryQueryParser()
    recommender = DataProductRecommender(parser)

    # Load data
    recommender.load_query_logs_from_csv_file('path/to/query_logs.csv')
    recommender.calculate_metrics()

    # Score tables with custom weights
    # Emphasize user diversity over query frequency
    scored_tables = recommender.score_tables(
        query_weight=0.25,      # 25% weight on query frequency
        user_weight=0.50,       # 50% weight on user diversity
        recency_weight=0.15,    # 15% weight on recency
        consistency_weight=0.10 # 10% weight on consistency
    )

    print("\nTop 10 tables by custom scoring:")
    print(scored_tables[['table', 'recommendation_score', 'query_count', 'unique_users']].head(10))


if __name__ == '__main__':
    # Run the main example
    main()

    # Uncomment to run other examples:
    # example_with_json_input()
    # example_with_custom_scoring()

# Made with Bob
