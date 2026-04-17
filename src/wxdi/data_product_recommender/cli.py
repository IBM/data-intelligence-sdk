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
Command-line interface for the Data Product Recommender
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

from .platforms import (
    SnowflakeQueryParser,
    DatabricksQueryParser,
    BigQueryQueryParser,
    WatsonxDataQueryParser
)
from .recommender import DataProductRecommender


def main():
    parser = argparse.ArgumentParser(
        description='Analyze query logs to recommend data products'
    )

    # Platform selection
    parser.add_argument(
        '--platform',
        choices=['snowflake', 'databricks', 'bigquery', 'watsonxdata'],
        required=True,
        help='Data platform to analyze'
    )

    # Input source (file-based only)
    parser.add_argument(
        '--input-file',
        type=str,
        required=True,
        help='Path to CSV or JSON file containing query logs'
    )

    # Output options
    parser.add_argument(
        '--output',
        type=str,
        default='output',
        help='Output directory for recommendations (default: output)'
    )

    parser.add_argument(
        '--output-format',
        choices=['markdown', 'json'],
        default='markdown',
        help='Output format: markdown (human-readable) or json (agent-consumable) (default: markdown)'
    )

    parser.add_argument(
        '--num-recommendations',
        type=int,
        default=20,
        help='Number of recommendations to generate (default: 20)'
    )

    parser.add_argument(
        '--min-score',
        type=float,
        default=None,
        help='Minimum recommendation score threshold (0-100). Tables below this score will be excluded.'
    )

    args = parser.parse_args()

    # Initialize platform-specific parser
    print(f"Initializing {args.platform} query parser...")

    if args.platform == 'snowflake':
        parser = SnowflakeQueryParser()
    elif args.platform == 'databricks':
        parser = DatabricksQueryParser()
    elif args.platform == 'bigquery':
        parser = BigQueryQueryParser()
    elif args.platform == 'watsonxdata':
        parser = WatsonxDataQueryParser()

    # Initialize recommender
    recommender = DataProductRecommender(parser)

    # Load query logs from file
    print(f"Loading query logs from file: {args.input_file}")

    if args.input_file.lower().endswith('.json'):
        recommender.load_query_logs_from_json_file(args.input_file)
    elif args.input_file.lower().endswith('.csv'):
        recommender.load_query_logs_from_csv_file(args.input_file)
    else:
        raise ValueError("Invalid --input-file type. Supported file types are JSON and CSV.")

    # Calculate metrics
    print("\nCalculating metrics...")
    recommender.calculate_metrics()

    # Generate recommendations
    print("\nGenerating recommendations...")
    recommendations = recommender.recommend_data_products(
        num_recommendations=args.num_recommendations,
        min_score=args.min_score
    )

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate output filename based on format
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    input_name = Path(args.input_file).stem if args.input_file else 'database'
    file_extension = 'json' if args.output_format == 'json' else 'md'
    output_file = output_dir / f"recommendations_{input_name}_{timestamp}.{file_extension}"

    # Export recommendations in selected format
    print(f"\nExporting recommendations to {output_file}...")
    if args.output_format == 'json':
        recommender.export_recommendations_json(recommendations, str(output_file))
    else:
        recommender.export_recommendations_markdown(recommendations, str(output_file))

    print("\n✓ Analysis complete!")
    print(f"  - Queries analyzed: {len(recommender.query_logs):,}")
    print(f"  - Tables identified: {len(recommender.table_metrics)}")
    print(f"  - Recommendations: {len(recommendations['individual_tables'])}")
    if 'table_groups' in recommendations:
        print(f"  - Table groups: {len(recommendations['table_groups'])}")
    print(f"  - Output file: {output_file}")


if __name__ == '__main__':
    main()

# Made with Bob
