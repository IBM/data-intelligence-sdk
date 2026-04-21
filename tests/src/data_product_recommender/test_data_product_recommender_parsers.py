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
Unit tests for query log parsers
"""

import pytest
import pandas as pd
from wxdi.data_product_recommender.platforms import (
    SnowflakeQueryParser,
    DatabricksQueryParser,
    BigQueryQueryParser,
    WatsonxDataQueryParser
)


class TestSnowflakeQueryParser:
    """Tests for Snowflake query parser"""

    def setup_method(self):
        """Setup test fixtures"""
        self.parser = SnowflakeQueryParser()

    def test_normalize_columns(self):
        """Test column normalization"""
        df = pd.DataFrame({
            'query_text': ['SELECT * FROM table1'],
            'user_name': ['user1'],
            'start_time': ['2025-01-01']
        })

        result = self.parser.normalize_columns(df)

        assert 'query_text' in result.columns
        assert 'user' in result.columns
        assert 'start_time' in result.columns

    def test_extract_tables_simple(self):
        """Test extracting tables from simple query"""
        query = "SELECT * FROM SALES.CUSTOMERS"
        tables = self.parser.extract_tables(query)

        assert len(tables) == 1
        assert 'SALES.CUSTOMERS' in tables

    def test_extract_tables_with_join(self):
        """Test extracting tables from query with JOIN"""
        query = "SELECT * FROM SALES.ORDERS o JOIN SALES.CUSTOMERS c ON o.customer_id = c.id"
        tables = self.parser.extract_tables(query)

        assert len(tables) == 2
        assert 'SALES.ORDERS' in tables
        assert 'SALES.CUSTOMERS' in tables

    def test_extract_tables_multiple_joins(self):
        """Test extracting tables from query with multiple JOINs"""
        query = """
        SELECT * FROM SALES.ORDERS o
        LEFT JOIN SALES.CUSTOMERS c ON o.customer_id = c.id
        INNER JOIN PRODUCT.CATALOG p ON o.product_id = p.id
        """
        tables = self.parser.extract_tables(query)

        assert len(tables) == 3
        assert 'SALES.ORDERS' in tables
        assert 'SALES.CUSTOMERS' in tables
        assert 'PRODUCT.CATALOG' in tables

    def test_extract_tables_empty_query(self):
        """Test extracting tables from empty query"""
        tables = self.parser.extract_tables("")
        assert len(tables) == 0

    def test_extract_tables_none_query(self):
        """Test extracting tables from None query"""
        tables = self.parser.extract_tables(None)
        assert len(tables) == 0


class TestDatabricksQueryParser:
    """Tests for Databricks query parser"""

    def setup_method(self):
        """Setup test fixtures"""
        self.parser = DatabricksQueryParser()

    def test_normalize_columns(self):
        """Test column normalization"""
        df = pd.DataFrame({
            'statement_text': ['SELECT * FROM table1'],
            'executed_by': ['user1'],
            'start_time': ['2025-01-01']
        })

        result = self.parser.normalize_columns(df)

        assert 'query_text' in result.columns
        assert 'user' in result.columns
        assert 'start_time' in result.columns

    def test_extract_tables_simple(self):
        """Test extracting tables from simple query"""
        query = "SELECT * FROM CLINICAL.PATIENTS"
        tables = self.parser.extract_tables(query)

        assert len(tables) == 1
        assert 'CLINICAL.PATIENTS' in tables


class TestBigQueryQueryParser:
    """Tests for BigQuery query parser"""

    def setup_method(self):
        """Setup test fixtures"""
        self.parser = BigQueryQueryParser()

    def test_normalize_columns(self):
        """Test column normalization"""
        df = pd.DataFrame({
            'query': ['SELECT * FROM table1'],
            'user_email': ['user1@example.com'],
            'start_time': ['2025-01-01']
        })

        result = self.parser.normalize_columns(df)

        assert 'query_text' in result.columns
        assert 'user' in result.columns
        assert 'start_time' in result.columns

    def test_extract_tables_with_backticks(self):
        """Test extracting tables from BigQuery query with backticks"""
        query = "SELECT * FROM `project-id.PRODUCT.CATALOG`"
        tables = self.parser.extract_tables(query)

        assert len(tables) == 1
        assert 'PRODUCT.CATALOG' in tables

    def test_extract_tables_multiple_with_backticks(self):
        """Test extracting multiple tables with project IDs"""
        query = """
        SELECT * FROM `project-id.SALES.ORDERS` o
        JOIN `project-id.CUSTOMER.PROFILES` c ON o.customer_id = c.id
        """
        tables = self.parser.extract_tables(query)

        assert len(tables) == 2
        assert 'SALES.ORDERS' in tables
        assert 'CUSTOMER.PROFILES' in tables


class TestWatsonxDataQueryParser:
    """Tests for watsonx.data query parser"""

    def setup_method(self):
        """Setup test fixtures"""
        self.parser = WatsonxDataQueryParser()

    def test_normalize_columns(self):
        """Test column normalization"""
        df = pd.DataFrame({
            'query': ['SELECT * FROM table1'],
            'user': ['user1'],
            'created': ['2025-01-01']
        })

        result = self.parser.normalize_columns(df)

        assert 'query_text' in result.columns
        assert 'user' in result.columns
        assert 'start_time' in result.columns

    def test_extract_tables_simple(self):
        """Test extracting tables from simple query"""
        query = "SELECT * FROM NETWORK.SUBSCRIBERS"
        tables = self.parser.extract_tables(query)

        assert len(tables) == 1
        assert 'NETWORK.SUBSCRIBERS' in tables


class TestParserEdgeCases:
    """Test edge cases across all parsers"""

    @pytest.mark.parametrize("parser_class", [
        SnowflakeQueryParser,
        DatabricksQueryParser,
        BigQueryQueryParser,
        WatsonxDataQueryParser
    ])
    def test_extract_tables_with_subquery(self, parser_class):
        """Test extracting tables from query with subquery"""
        parser = parser_class()
        query = """
        SELECT * FROM SALES.ORDERS
        WHERE customer_id IN (SELECT id FROM SALES.CUSTOMERS WHERE active = true)
        """
        tables = parser.extract_tables(query)

        # Should extract both tables
        assert len(tables) >= 2

    @pytest.mark.parametrize("parser_class", [
        SnowflakeQueryParser,
        DatabricksQueryParser,
        BigQueryQueryParser,
        WatsonxDataQueryParser
    ])
    def test_extract_tables_case_insensitive(self, parser_class):
        """Test that table extraction is case-insensitive"""
        parser = parser_class()
        query_upper = "SELECT * FROM SALES.ORDERS"
        query_lower = "select * from sales.orders"

        tables_upper = parser.extract_tables(query_upper)
        tables_lower = parser.extract_tables(query_lower)

        # Both should extract the same table (normalized to uppercase)
        assert len(tables_upper) == 1
        assert len(tables_lower) == 1

# Made with Bob
