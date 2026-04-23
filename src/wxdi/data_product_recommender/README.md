<!--
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
-->

# Data Product Recommender

A tool that analyzes database query logs from files to identify high-value tables and logical groupings that should be prioritized as data products in a data marketplace.

## Purpose

**Accelerate data product onboarding** by leveraging existing usage patterns rather than starting from scratch.

Organizations often have valuable data assets already in active use across various teams and use cases. Instead of building new data pipelines or guessing which tables to promote, this tool analyzes actual query patterns to identify:

- **High-value tables**: Frequently queried by diverse user groups
- **Logical groupings**: Tables that are commonly used together
- **Proven assets**: Tables with demonstrated business value through real usage

## Features

- **Multi-platform support**: Snowflake, Databricks, BigQuery, watsonx.data query log formats
- **File-based input**: Supports CSV and JSON query log files (no direct database connection required)
- **Intelligent scoring**: Combines query frequency, user diversity, recency, and consistency
- **Table grouping**: Identifies tables frequently used together
- **Query pattern analysis**: Shows common query patterns for each recommendation
- **Multiple output formats**: Markdown (human-readable) and JSON (agent-consumable)
- **CLI and Python API**: Use from command line or integrate into your applications

## Installation

From the data-intelligence-sdk repository:

```bash
# Install the package with dependencies
pip install -e .
```

## Quick Start

### Command Line Interface

```bash
# Analyze Snowflake query logs from CSV
python -m wxdi.data_product_recommender.cli \
  --platform snowflake \
  --input-file samples/query_logs.csv \
  --output output \
  --num-recommendations 20

# Analyze with minimum score threshold
python -m wxdi.data_product_recommender.cli \
  --platform databricks \
  --input-file samples/query_logs.json \
  --min-score 60.0 \
  --output-format json
```

### Python API

```python
from data_product_recommender.platforms import SnowflakeQueryParser
from data_product_recommender.recommender import DataProductRecommender

# Initialize with platform-specific parser
parser = SnowflakeQueryParser()
recommender = DataProductRecommender(parser)

# Load and analyze query logs from file
recommender.load_query_logs_from_csv_file('query_logs.csv')
recommender.calculate_metrics()
recommendations = recommender.recommend_data_products(num_recommendations=20)

# Export results
recommender.export_recommendations_markdown(recommendations, 'output/recommendations.md')
recommender.export_recommendations_json(recommendations, 'output/recommendations.json')
```

## Methodology

### Individual Table Scoring (0-100)

- **37.5%** Query Count - Volume of usage
- **37.5%** User Diversity - Breadth of usage across teams
- **15%** Recency - Recent activity (prioritizes currently active tables)
- **10%** Consistency - Regular usage patterns (identifies stable, ongoing value)

### Table Group Scoring (0-100)

- **30%** Cohesion - How tightly tables are connected
- **20%** Usage - Relative usage compared to other groups
- **15%** User Reach - Percentage of users querying the group
- **20%** Recency - Recent activity across tables
- **10%** Consistency - Regular usage patterns
- **5%** Size - Number of tables in the group

### Star Rating Scale

- ⭐⭐⭐⭐⭐ **Excellent (80-100)**: Implement immediately
- ⭐⭐⭐⭐ **Good (60-79)**: Medium priority
- ⭐⭐⭐ **Fair (40-59)**: Consider splitting or implement later
- ⭐⭐ **Weak (20-39)**: Reconsider grouping
- ⭐ **Poor (0-19)**: Do not implement

## CLI Options

```
--platform              Database platform (snowflake, databricks, bigquery, watsonxdata)
--input-file           Path to CSV or JSON query log file
--output               Output directory (default: output)
--output-format        Output format: markdown or json (default: markdown)
--num-recommendations  Number of recommendations (default: 20)
--min-score           Minimum score threshold 0-100 (filters low-scoring tables)
```

## Output Formats

### Markdown (Human-Readable)
- Rich formatting with tables and collapsible sections
- Star ratings and detailed explanations
- Query pattern examples with syntax highlighting
- Comprehensive coverage statistics

### JSON (Agent-Consumable)
- Clean, parseable structure
- All metrics as numeric values
- Rating labels (excellent, good, fair, weak, poor)
- Suitable for AI agents and automated workflows

## Platform Support

This tool supports query log files from the following platforms:

- ✅ **Snowflake** - Export from `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`
- ✅ **Databricks** - Export from `system.query.history` (Unity Catalog)
- ✅ **BigQuery** - Export from `INFORMATION_SCHEMA.JOBS_BY_PROJECT`
- ✅ **watsonx.data** - Export from `system.runtime.queries` (Presto)

**Note**: This tool requires pre-exported query log files in CSV or JSON format. It does not connect directly to databases.

## Examples

See the `examples/` directory for detailed usage examples:

- `data_product_recommender_example.py` - Basic usage with different platforms
- Custom scoring weights
- JSON and CSV input formats

## Testing

```bash
# Run unit tests
pytest tests/src/data_product_recommender/ -v

# Run with coverage
pytest tests/src/data_product_recommender/ --cov=wxdi.data_product_recommender --cov-report=html
```

## Architecture

The tool uses an extensible design with abstract base classes:

```
QueryLogParser (Abstract)
├── SnowflakeQueryParser
├── DatabricksQueryParser
├── BigQueryQueryParser
└── WatsonxDataQueryParser

DataProductRecommender
└── Uses parser for platform-specific query log formats
```

## Important Notes

### Query Log Export

To use this tool, you need to export query logs from your data platform:

**Snowflake Example:**
```sql
SELECT query_text, user_name, start_time, end_time, execution_status
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
```

**Databricks Example:**
```sql
SELECT statement_text, user_name, start_time, end_time, status
FROM system.query.history
WHERE start_time >= current_timestamp() - INTERVAL 30 DAYS
```

### Required Columns

Query log files must contain these columns (column names will be normalized by the parser):
- `query_text` - The SQL query text
- `user` - User who executed the query
- `start_time` - Query execution timestamp

### Data Privacy

Query logs may contain sensitive information including user identities, table names, and query patterns. Ensure proper data handling and security measures are in place.

## License

Apache License 2.0 - See LICENSE file in the root directory.