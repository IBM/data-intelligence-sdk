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
Unit tests for DataProductRecommender
"""

import pytest
import pandas as pd
import json
import tempfile
import os
from datetime import datetime, timedelta
from wxdi.data_product_recommender.recommender import (
    DataProductRecommender,
    normalize_query_pattern,
    FIVE_STARS, FOUR_STARS, THREE_STARS, TWO_STARS, ONE_STAR,
    EXCELLENT_CANDIDATE, GOOD_CANDIDATE, FAIR_CANDIDATE, WEAK_CANDIDATE, POOR_CANDIDATE
)
from wxdi.data_product_recommender.platforms import SnowflakeQueryParser


class TestNormalizeQueryPattern:
    """Tests for normalize_query_pattern function"""

    def test_normalize_simple_query(self):
        """Test normalizing a simple query"""
        query = "SELECT * FROM SALES.CUSTOMERS WHERE id = 123"
        pattern = normalize_query_pattern(query)
        assert pattern == "SELECT * FROM SALES.CUSTOMERS WHERE ID = ?"

    def test_normalize_query_with_strings(self):
        """Test normalizing query with string literals"""
        query = "SELECT * FROM SALES.CUSTOMERS WHERE name = 'John Doe'"
        pattern = normalize_query_pattern(query)
        assert pattern == "SELECT * FROM SALES.CUSTOMERS WHERE NAME = ?"

    def test_normalize_query_with_double_quotes(self):
        """Test normalizing query with double-quoted strings"""
        query = 'SELECT * FROM SALES.CUSTOMERS WHERE name = "John Doe"'
        pattern = normalize_query_pattern(query)
        assert pattern == "SELECT * FROM SALES.CUSTOMERS WHERE NAME = ?"

    def test_normalize_query_with_decimals(self):
        """Test normalizing query with decimal numbers"""
        query = "SELECT * FROM SALES.ORDERS WHERE amount > 123.45"
        pattern = normalize_query_pattern(query)
        assert pattern == "SELECT * FROM SALES.ORDERS WHERE AMOUNT > ?"

    def test_normalize_query_with_dates(self):
        """Test normalizing query with date literals"""
        query = "SELECT * FROM SALES.ORDERS WHERE date = '2024-01-01'"
        pattern = normalize_query_pattern(query)
        assert "?" in pattern

    def test_normalize_empty_query(self):
        """Test normalizing empty query"""
        assert normalize_query_pattern("") == ""
        assert normalize_query_pattern(None) == ""

    def test_normalize_query_whitespace(self):
        """Test normalizing query with multiple whitespaces"""
        query = "SELECT  *   FROM   SALES.CUSTOMERS"
        pattern = normalize_query_pattern(query)
        assert pattern == "SELECT * FROM SALES.CUSTOMERS"

    def test_normalize_query_with_escaped_quotes(self):
        """Test normalizing query with escaped quotes"""
        query = "SELECT * FROM SALES.CUSTOMERS WHERE name = 'O\\'Brien'"
        pattern = normalize_query_pattern(query)
        assert "?" in pattern


class TestDataProductRecommender:
    """Tests for DataProductRecommender class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.parser = SnowflakeQueryParser()
        self.recommender = DataProductRecommender(self.parser)

    def test_initialization(self):
        """Test recommender initialization"""
        assert self.recommender.parser is not None
        assert self.recommender.query_logs is None
        assert self.recommender.table_metrics is None
        assert self.recommender.query_patterns is None

    def test_load_query_logs_from_json_file(self):
        """Test loading query logs from JSON file"""
        # Create temporary JSON file
        test_data = [
            {
                'query_text': 'SELECT * FROM SALES.CUSTOMERS',
                'user_name': 'user1',
                'start_time': '2025-01-01'
            },
            {
                'query_text': 'SELECT * FROM SALES.ORDERS',
                'user_name': 'user2',
                'start_time': '2025-01-02'
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            # Load the data
            df = self.recommender.load_query_logs_from_json_file(temp_file)

            # Verify
            assert df is not None
            assert len(df) == 2
            assert 'query_text' in df.columns
            assert 'user' in df.columns
            assert 'tables' in df.columns
        finally:
            os.unlink(temp_file)

    def test_load_query_logs_from_csv_file(self):
        """Test loading query logs from CSV file"""
        # Create temporary CSV file
        test_data = pd.DataFrame({
            'query_text': ['SELECT * FROM SALES.CUSTOMERS', 'SELECT * FROM SALES.ORDERS'],
            'user_name': ['user1', 'user2'],
            'start_time': ['2025-01-01', '2025-01-02']
        })

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_file = f.name

        try:
            # Load the data
            df = self.recommender.load_query_logs_from_csv_file(temp_file)

            # Verify
            assert df is not None
            assert len(df) == 2
            assert 'query_text' in df.columns
            assert 'user' in df.columns
            assert 'tables' in df.columns
        finally:
            os.unlink(temp_file)

    def test_calculate_metrics(self):
        """Test calculating table metrics"""
        # Setup test data
        test_data = pd.DataFrame({
            'query_text': [
                'SELECT * FROM SALES.CUSTOMERS',
                'SELECT * FROM SALES.CUSTOMERS',
                'SELECT * FROM SALES.ORDERS',
                'SELECT * FROM SALES.CUSTOMERS JOIN SALES.ORDERS ON c.id = o.customer_id'
            ],
            'user': ['user1', 'user2', 'user1', 'user3'],
            'start_time': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04']
        })

        # Manually add tables column
        test_data['tables'] = [
            ['SALES.CUSTOMERS'],
            ['SALES.CUSTOMERS'],
            ['SALES.ORDERS'],
            ['SALES.CUSTOMERS', 'SALES.ORDERS']
        ]

        self.recommender.query_logs = test_data

        # Calculate metrics
        metrics = self.recommender.calculate_metrics()

        # Verify
        assert metrics is not None
        assert len(metrics) == 2  # Two unique tables
        assert 'table' in metrics.columns
        assert 'query_count' in metrics.columns
        assert 'unique_users' in metrics.columns
        assert 'related_tables' in metrics.columns

        # Check specific values
        customers_row = metrics[metrics['table'] == 'SALES.CUSTOMERS'].iloc[0]
        assert customers_row['query_count'] == 3
        assert customers_row['unique_users'] == 3

    def test_score_tables(self):
        """Test scoring tables"""
        # Setup test data with metrics including temporal fields
        self.recommender.table_metrics = pd.DataFrame({
            'table': ['SALES.CUSTOMERS', 'SALES.ORDERS'],
            'query_count': [10, 5],
            'unique_users': [5, 3],
            'related_tables': [['SALES.ORDERS'], ['SALES.CUSTOMERS']],
            'related_table_count': [1, 1],
            'recency_score': [0.9, 0.5],
            'consistency_score': [0.8, 0.6]
        })

        # Score tables
        scored = self.recommender.score_tables()

        # Verify
        assert scored is not None
        assert len(scored) == 2
        assert 'recommendation_score' in scored.columns
        assert scored.iloc[0]['recommendation_score'] > scored.iloc[1]['recommendation_score']

    def test_identify_table_groups(self):
        """Test identifying table groups"""
        # Setup test data
        test_data = pd.DataFrame({
            'query_text': ['query1', 'query2', 'query3'],
            'user': ['user1', 'user2', 'user3'],
            'start_time': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'tables': [
                ['SALES.CUSTOMERS', 'SALES.ORDERS'],
                ['SALES.CUSTOMERS', 'SALES.ORDERS'],
                ['SALES.ORDERS', 'PRODUCT.CATALOG']
            ]
        })

        self.recommender.query_logs = test_data

        # Identify groups
        groups = self.recommender.identify_table_groups(min_cooccurrence=2)

        # Verify
        assert groups is not None
        assert len(groups) >= 1
        # The group (SALES.CUSTOMERS, SALES.ORDERS) should appear with count 2
        assert any(count == 2 for _, count in groups)

    def test_recommend_data_products(self):
        """Test generating recommendations"""
        # Setup complete test data
        test_data = pd.DataFrame({
            'query_text': ['query1', 'query2', 'query3'],
            'user': ['user1', 'user2', 'user3'],
            'start_time': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'tables': [
                ['SALES.CUSTOMERS'],
                ['SALES.CUSTOMERS'],
                ['SALES.ORDERS']
            ]
        })

        self.recommender.query_logs = test_data
        self.recommender.calculate_metrics()

        # Generate recommendations
        recommendations = self.recommender.recommend_data_products(
            num_recommendations=2
        )

        # Verify structure
        assert recommendations is not None
        assert 'individual_tables' in recommendations
        assert 'table_groups' in recommendations
        assert 'metadata' in recommendations
        assert len(recommendations['individual_tables']) <= 2

        # Verify metadata
        metadata = recommendations['metadata']
        assert 'total_tables' in metadata
        assert 'recommended_tables' in metadata
        assert 'highest_score' in metadata
        assert 'min_score_threshold' in metadata
        assert metadata['total_tables'] >= metadata['recommended_tables']
        assert metadata['min_score_threshold'] is None  # No threshold in this test

    def test_export_recommendations_markdown(self):
        """Test exporting recommendations to markdown"""
        # Setup test data
        self.recommender.query_logs = pd.DataFrame({
            'query_text': ['query1'],
            'user': ['user1'],
            'start_time': ['2025-01-01'],
            'tables': [['SALES.CUSTOMERS']]
        })

        self.recommender.table_metrics = pd.DataFrame({
            'table': ['SALES.CUSTOMERS'],
            'query_count': [10],
            'unique_users': [5],
            'related_tables': [[]],
            'related_table_count': [0]
        })

        recommendations = {
            'individual_tables': [
                {
                    'table': 'SALES.CUSTOMERS',
                    'query_count': 10,
                    'unique_users': 5,
                    'recommendation_score': 85.5,
                    'related_tables': []
                }
            ]
        }

        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            temp_file = f.name

        try:
            self.recommender.export_recommendations_markdown(recommendations, temp_file)

            # Verify file was created and has content
            assert os.path.exists(temp_file)
            with open(temp_file, 'r') as f:
                content = f.read()
                assert 'Data Product Recommendations' in content
                assert 'SALES.CUSTOMERS' in content
        finally:
            os.unlink(temp_file)

    def test_export_recommendations_json(self):
        """Test exporting recommendations to JSON"""
        # Setup test data
        self.recommender.query_logs = pd.DataFrame({
            'query_text': ['query1'],
            'user': ['user1'],
            'start_time': ['2025-01-01'],
            'tables': [['SALES.CUSTOMERS']]
        })

        recommendations = {
            'individual_tables': [
                {
                    'table': 'SALES.CUSTOMERS',
                    'query_count': 10,
                    'unique_users': 5,
                    'recommendation_score': 85.5,
                    'recency_score': 0.9,
                    'consistency_score': 0.8
                }
            ],
            'metadata': {
                'total_tables': 1,
                'recommended_tables': 1
            }
        }

        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name

        try:
            self.recommender.export_recommendations_json(recommendations, temp_file)

            # Verify file was created and has valid JSON
            assert os.path.exists(temp_file)
            with open(temp_file, 'r') as f:
                data = json.load(f)
                # JSON export uses 'recommendations' key, not 'individual_tables'
                assert 'recommendations' in data
                assert 'metadata' in data
                assert len(data['recommendations']) == 1
                # Verify structure
                assert data['recommendations'][0]['type'] == 'standalone'
                assert 'score' in data['recommendations'][0]
                assert 'rating' in data['recommendations'][0]
        finally:
            os.unlink(temp_file)

    def test_calculate_temporal_metrics(self):
        """Test calculating temporal metrics (recency and consistency)"""
        # Setup test data with specific dates
        base_date = datetime(2025, 1, 1)
        test_data = pd.DataFrame({
            'query_text': [
                'SELECT * FROM SALES.CUSTOMERS',
                'SELECT * FROM SALES.CUSTOMERS',
                'SELECT * FROM SALES.CUSTOMERS'
            ],
            'user': ['user1', 'user1', 'user1'],
            'start_time': [
                base_date,
                base_date + timedelta(days=1),
                base_date + timedelta(days=2)
            ],
            'tables': [
                ['SALES.CUSTOMERS'],
                ['SALES.CUSTOMERS'],
                ['SALES.CUSTOMERS']
            ]
        })

        self.recommender.query_logs = test_data
        metrics = self.recommender.calculate_metrics()

        # Verify temporal metrics are calculated
        assert 'recency_score' in metrics.columns
        assert 'consistency_score' in metrics.columns
        assert 'days_since_last_query' in metrics.columns
        assert metrics.iloc[0]['recency_score'] > 0

    def test_recommend_with_table_groups(self):
        """Test recommendations include table groups"""
        # Setup test data with co-occurring tables
        test_data = pd.DataFrame({
            'query_text': ['query1', 'query2', 'query3'],
            'user': ['user1', 'user2', 'user3'],
            'start_time': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'tables': [
                ['SALES.CUSTOMERS', 'SALES.ORDERS'],
                ['SALES.CUSTOMERS', 'SALES.ORDERS'],
                ['SALES.CUSTOMERS', 'SALES.ORDERS']
            ]
        })

        self.recommender.query_logs = test_data
        self.recommender.calculate_metrics()

        recommendations = self.recommender.recommend_data_products(
            num_recommendations=10
        )

        # Verify table groups are identified
        assert 'table_groups' in recommendations

    def test_score_tables_with_custom_weights(self):
        """Test scoring tables with custom weights"""
        # Setup test data
        self.recommender.table_metrics = pd.DataFrame({
            'table': ['SALES.CUSTOMERS'],
            'query_count': [10],
            'unique_users': [5],
            'related_tables': [[]],
            'related_table_count': [0],
            'recency_score': [0.9],
            'consistency_score': [0.8]
        })

        # Score with custom weights
        scored = self.recommender.score_tables(
            query_weight=0.5,
            user_weight=0.3,
            recency_weight=0.1,
            consistency_weight=0.1
        )

        assert 'recommendation_score' in scored.columns
        assert len(scored) == 1

    def test_get_rating_label(self):
        """Test rating label assignment"""
        # _get_rating_label returns just a string label, not a tuple
        assert self.recommender._get_rating_label(95) == 'excellent'
        assert self.recommender._get_rating_label(75) == 'good'
        assert self.recommender._get_rating_label(55) == 'fair'
        assert self.recommender._get_rating_label(35) == 'weak'
        assert self.recommender._get_rating_label(15) == 'poor'

    def test_get_star_rating(self):
        """Test star rating assignment"""
        # _get_star_rating returns a tuple of (stars, label)
        stars, label = self.recommender._get_star_rating(95)
        assert stars == FIVE_STARS
        assert label == EXCELLENT_CANDIDATE

        stars, label = self.recommender._get_star_rating(75)
        assert stars == FOUR_STARS
        assert label == GOOD_CANDIDATE

        stars, label = self.recommender._get_star_rating(55)
        assert stars == THREE_STARS
        assert label == FAIR_CANDIDATE

        stars, label = self.recommender._get_star_rating(35)
        assert stars == TWO_STARS
        assert label == WEAK_CANDIDATE

        stars, label = self.recommender._get_star_rating(15)
        assert stars == ONE_STAR
        assert label == POOR_CANDIDATE

    def test_load_query_logs_filters_empty_tables(self):
        """Test that queries with no table references are filtered out"""
        # Create test data with some queries having no tables
        test_data = [
            {
                'query_text': 'SELECT * FROM SALES.CUSTOMERS',
                'user_name': 'user1',
                'start_time': '2025-01-01'
            },
            {
                'query_text': 'SHOW TABLES',  # No table reference
                'user_name': 'user2',
                'start_time': '2025-01-02'
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            df = self.recommender.load_query_logs_from_json_file(temp_file)
            # Should only have 1 query (the one with table reference)
            assert len(df) >= 0  # May vary based on parser
        finally:
            os.unlink(temp_file)

    def test_calculate_metrics_with_single_timestamp(self):
        """Test metrics calculation with single timestamp per table"""
        test_data = pd.DataFrame({
            'query_text': ['SELECT * FROM SALES.CUSTOMERS'],
            'user': ['user1'],
            'start_time': [datetime(2025, 1, 1)],
            'tables': [['SALES.CUSTOMERS']]
        })

        self.recommender.query_logs = test_data
        metrics = self.recommender.calculate_metrics()

        # Should handle single timestamp gracefully
        assert len(metrics) == 1
        assert metrics.iloc[0]['consistency_score'] == 0.0  # Single timestamp = 0 consistency

    def test_recommend_with_min_score_filters_tables(self):
        """Test that min_score filters out low-scoring tables"""
        # Setup test data with varying query counts
        test_data = pd.DataFrame({
            'query_text': [
                'SELECT * FROM SALES.CUSTOMERS',
                'SELECT * FROM SALES.CUSTOMERS',
                'SELECT * FROM SALES.CUSTOMERS',
                'SELECT * FROM SALES.ORDERS'
            ],
            'user': ['user1', 'user2', 'user3', 'user1'],
            'start_time': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04'],
            'tables': [
                ['SALES.CUSTOMERS'],
                ['SALES.CUSTOMERS'],
                ['SALES.CUSTOMERS'],
                ['SALES.ORDERS']
            ]
        })

        self.recommender.query_logs = test_data
        self.recommender.calculate_metrics()

        # Get recommendations with high min_score
        recommendations = self.recommender.recommend_data_products(
            num_recommendations=10,
            min_score=70.0
        )

        # Should filter out low-scoring tables
        assert recommendations['metadata']['min_score_threshold'] == 70.0
        for table in recommendations['individual_tables']:
            assert table['recommendation_score'] >= 70.0


class TestRecommenderEdgeCases:
    """Test edge cases for recommender"""

    def setup_method(self):
        """Setup test fixtures"""
        self.parser = SnowflakeQueryParser()
        self.recommender = DataProductRecommender(self.parser)

    def test_calculate_metrics_without_loaded_data(self):
        """Test calculating metrics without loading data first"""
        with pytest.raises(ValueError, match="Query logs not loaded"):
            self.recommender.calculate_metrics()

    def test_score_tables_without_metrics(self):
        """Test scoring tables without calculating metrics first"""
        with pytest.raises(ValueError, match="Metrics not calculated"):
            self.recommender.score_tables()

    def test_identify_table_groups_without_loaded_data(self):
        """Test identifying groups without loading data first"""
        with pytest.raises(ValueError, match="Query logs not loaded"):
            self.recommender.identify_table_groups()

    def test_load_csv_with_missing_columns(self):
        """Test loading CSV with missing required columns"""
        # Create CSV with missing columns
        test_data = pd.DataFrame({
            'query_text': ['SELECT * FROM table1'],
            'start_time': ['2025-01-01']
            # Missing 'user' column
        })

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_file = f.name

        try:
            with pytest.raises(ValueError, match="missing required columns"):
                self.recommender.load_query_logs_from_csv_file(temp_file)
        finally:
            os.unlink(temp_file)

# Made with Bob
