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
Integration tests for Data Product Recommender

These tests verify end-to-end functionality using sample data files.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path

from wxdi.data_product_recommender.platforms import (
    SnowflakeQueryParser,
    DatabricksQueryParser,
    BigQueryQueryParser,
    WatsonxDataQueryParser
)
from wxdi.data_product_recommender.recommender import DataProductRecommender


class TestSnowflakeIntegration:
    """Integration tests for Snowflake platform"""

    @pytest.fixture
    def sample_csv_file(self):
        """Path to sample Snowflake CSV file"""
        return 'input_samples/synthetic_snowflake_business_logs_1000.csv'

    @pytest.fixture
    def sample_json_file(self):
        """Path to sample Snowflake JSON file"""
        return 'input_samples/synthetic_snowflake_business_logs_1000.json'

    @pytest.fixture
    def output_dir(self):
        """Create temporary output directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_end_to_end_csv_workflow(self, sample_csv_file, output_dir):
        """Test complete workflow with CSV input"""
        # Skip if sample file doesn't exist
        if not os.path.exists(sample_csv_file):
            pytest.skip(f"Sample file not found: {sample_csv_file}")

        # Initialize
        parser = SnowflakeQueryParser()
        recommender = DataProductRecommender(parser)

        # Load data
        recommender.load_query_logs_from_csv_file(sample_csv_file)
        assert recommender.query_logs is not None
        assert len(recommender.query_logs) > 0

        # Calculate metrics
        recommender.calculate_metrics()
        assert recommender.table_metrics is not None
        assert len(recommender.table_metrics) > 0

        # Generate recommendations
        recommendations = recommender.recommend_data_products(num_recommendations=10)
        assert 'individual_tables' in recommendations
        assert len(recommendations['individual_tables']) > 0

        # Export markdown
        md_file = os.path.join(output_dir, 'test_recommendations.md')
        recommender.export_recommendations_markdown(recommendations, md_file)
        assert os.path.exists(md_file)
        assert os.path.getsize(md_file) > 0

        # Export JSON
        json_file = os.path.join(output_dir, 'test_recommendations.json')
        recommender.export_recommendations_json(recommendations, json_file)
        assert os.path.exists(json_file)
        assert os.path.getsize(json_file) > 0

    def test_end_to_end_json_workflow(self, sample_json_file, output_dir):
        """Test complete workflow with JSON input"""
        # Skip if sample file doesn't exist
        if not os.path.exists(sample_json_file):
            pytest.skip(f"Sample file not found: {sample_json_file}")

        # Initialize
        parser = SnowflakeQueryParser()
        recommender = DataProductRecommender(parser)

        # Load data
        recommender.load_query_logs_from_json_file(sample_json_file)
        assert recommender.query_logs is not None
        assert len(recommender.query_logs) > 0

        # Calculate metrics
        recommender.calculate_metrics()
        assert recommender.table_metrics is not None

        # Generate recommendations
        recommendations = recommender.recommend_data_products(num_recommendations=10)
        assert 'individual_tables' in recommendations

    def test_recommendations_with_min_score(self, sample_csv_file):
        """Test recommendations with minimum score threshold"""
        if not os.path.exists(sample_csv_file):
            pytest.skip(f"Sample file not found: {sample_csv_file}")

        parser = SnowflakeQueryParser()
        recommender = DataProductRecommender(parser)

        recommender.load_query_logs_from_csv_file(sample_csv_file)
        recommender.calculate_metrics()

        # Get recommendations with high threshold
        recommendations = recommender.recommend_data_products(
            num_recommendations=20,
            min_score=70.0
        )

        # Verify all recommendations meet threshold
        for table in recommendations['individual_tables']:
            assert table['recommendation_score'] >= 70.0


class TestDatabricksIntegration:
    """Integration tests for Databricks platform"""

    @pytest.fixture
    def sample_csv_file(self):
        """Path to sample Databricks CSV file"""
        return 'input_samples/synthetic_databricks_healthcare_logs_1000.csv'

    @pytest.fixture
    def sample_json_file(self):
        """Path to sample Databricks JSON file"""
        return 'input_samples/synthetic_databricks_healthcare_logs_1000.json'

    def test_databricks_csv_workflow(self, sample_csv_file):
        """Test Databricks workflow with CSV input"""
        if not os.path.exists(sample_csv_file):
            pytest.skip(f"Sample file not found: {sample_csv_file}")

        parser = DatabricksQueryParser()
        recommender = DataProductRecommender(parser)

        recommender.load_query_logs_from_csv_file(sample_csv_file)
        assert recommender.query_logs is not None

        recommender.calculate_metrics()
        assert recommender.table_metrics is not None

        recommendations = recommender.recommend_data_products(num_recommendations=10)
        assert 'individual_tables' in recommendations

    def test_databricks_json_workflow(self, sample_json_file):
        """Test Databricks workflow with JSON input"""
        if not os.path.exists(sample_json_file):
            pytest.skip(f"Sample file not found: {sample_json_file}")

        parser = DatabricksQueryParser()
        recommender = DataProductRecommender(parser)

        recommender.load_query_logs_from_json_file(sample_json_file)
        assert recommender.query_logs is not None

        recommender.calculate_metrics()
        recommendations = recommender.recommend_data_products(num_recommendations=10)
        assert 'individual_tables' in recommendations


class TestBigQueryIntegration:
    """Integration tests for BigQuery platform"""

    @pytest.fixture
    def sample_csv_file(self):
        """Path to sample BigQuery CSV file"""
        return 'input_samples/synthetic_bigquery_retail_logs_1000.csv'

    @pytest.fixture
    def sample_json_file(self):
        """Path to sample BigQuery JSON file"""
        return 'input_samples/synthetic_bigquery_retail_logs_1000.json'

    def test_bigquery_csv_workflow(self, sample_csv_file):
        """Test BigQuery workflow with CSV input"""
        if not os.path.exists(sample_csv_file):
            pytest.skip(f"Sample file not found: {sample_csv_file}")

        parser = BigQueryQueryParser()
        recommender = DataProductRecommender(parser)

        recommender.load_query_logs_from_csv_file(sample_csv_file)
        assert recommender.query_logs is not None

        recommender.calculate_metrics()
        assert recommender.table_metrics is not None

        recommendations = recommender.recommend_data_products(num_recommendations=10)
        assert 'individual_tables' in recommendations

    def test_bigquery_json_workflow(self, sample_json_file):
        """Test BigQuery workflow with JSON input"""
        if not os.path.exists(sample_json_file):
            pytest.skip(f"Sample file not found: {sample_json_file}")

        parser = BigQueryQueryParser()
        recommender = DataProductRecommender(parser)

        recommender.load_query_logs_from_json_file(sample_json_file)
        assert recommender.query_logs is not None

        recommender.calculate_metrics()
        recommendations = recommender.recommend_data_products(num_recommendations=10)
        assert 'individual_tables' in recommendations


class TestWatsonxDataIntegration:
    """Integration tests for watsonx.data platform"""

    @pytest.fixture
    def sample_csv_file(self):
        """Path to sample watsonx.data CSV file"""
        return 'input_samples/synthetic_watsonx_telecom_logs_1000.csv'

    @pytest.fixture
    def sample_json_file(self):
        """Path to sample watsonx.data JSON file"""
        return 'input_samples/synthetic_watsonx_telecom_logs_1000.json'

    def test_watsonxdata_csv_workflow(self, sample_csv_file):
        """Test watsonx.data workflow with CSV input"""
        if not os.path.exists(sample_csv_file):
            pytest.skip(f"Sample file not found: {sample_csv_file}")

        parser = WatsonxDataQueryParser()
        recommender = DataProductRecommender(parser)

        recommender.load_query_logs_from_csv_file(sample_csv_file)
        assert recommender.query_logs is not None

        recommender.calculate_metrics()
        assert recommender.table_metrics is not None

        recommendations = recommender.recommend_data_products(num_recommendations=10)
        assert 'individual_tables' in recommendations

    def test_watsonxdata_json_workflow(self, sample_json_file):
        """Test watsonx.data workflow with JSON input"""
        if not os.path.exists(sample_json_file):
            pytest.skip(f"Sample file not found: {sample_json_file}")

        parser = WatsonxDataQueryParser()
        recommender = DataProductRecommender(parser)

        recommender.load_query_logs_from_json_file(sample_json_file)
        assert recommender.query_logs is not None

        recommender.calculate_metrics()
        recommendations = recommender.recommend_data_products(num_recommendations=10)
        assert 'individual_tables' in recommendations


class TestTableGrouping:
    """Integration tests for table grouping functionality"""

    @pytest.fixture
    def sample_file(self):
        """Path to sample file with table relationships"""
        return 'input_samples/synthetic_snowflake_business_logs_1000.csv'

    def test_table_grouping_detection(self, sample_file):
        """Test that table groups are detected correctly"""
        if not os.path.exists(sample_file):
            pytest.skip(f"Sample file not found: {sample_file}")

        parser = SnowflakeQueryParser()
        recommender = DataProductRecommender(parser)

        recommender.load_query_logs_from_csv_file(sample_file)
        recommender.calculate_metrics()

        recommendations = recommender.recommend_data_products(
            num_recommendations=20,
            min_frequency_threshold=0.05  # 5% threshold
        )

        # Check if table groups were identified
        if 'table_groups' in recommendations and len(recommendations['table_groups']) > 0:
            # Verify group structure
            for group in recommendations['table_groups']:
                assert 'tables' in group
                assert 'group_score' in group  # Changed from 'score' to 'group_score'
                assert len(group['tables']) >= 2  # Groups should have at least 2 tables


class TestOutputFormats:
    """Integration tests for output format generation"""

    @pytest.fixture
    def sample_file(self):
        return 'input_samples/synthetic_snowflake_business_logs_1000.csv'

    @pytest.fixture
    def output_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_markdown_output_structure(self, sample_file, output_dir):
        """Test that markdown output has correct structure"""
        if not os.path.exists(sample_file):
            pytest.skip(f"Sample file not found: {sample_file}")

        parser = SnowflakeQueryParser()
        recommender = DataProductRecommender(parser)

        recommender.load_query_logs_from_csv_file(sample_file)
        recommender.calculate_metrics()
        recommendations = recommender.recommend_data_products(num_recommendations=10)

        md_file = os.path.join(output_dir, 'test_output.md')
        recommender.export_recommendations_markdown(recommendations, md_file)

        # Read and verify markdown content
        with open(md_file, 'r') as f:
            content = f.read()
            assert '# Data Product Recommendations' in content
            assert '## Summary Statistics' in content
            # Check that content has data product information (tables or metrics)
            assert ('ANALYTICS.' in content or 'SALES.' in content or 'PRODUCT.' in content)

    def test_json_output_structure(self, sample_file, output_dir):
        """Test that JSON output has correct structure"""
        if not os.path.exists(sample_file):
            pytest.skip(f"Sample file not found: {sample_file}")

        parser = SnowflakeQueryParser()
        recommender = DataProductRecommender(parser)

        recommender.load_query_logs_from_csv_file(sample_file)
        recommender.calculate_metrics()
        recommendations = recommender.recommend_data_products(num_recommendations=10)

        json_file = os.path.join(output_dir, 'test_output.json')
        recommender.export_recommendations_json(recommendations, json_file)

        # Read and verify JSON structure
        import json
        with open(json_file, 'r') as f:
            data = json.load(f)
            assert 'recommendations' in data
            assert 'metadata' in data
            assert 'generated_at' in data['metadata']
            assert 'total_queries_analyzed' in data['metadata']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

# Made with Bob
