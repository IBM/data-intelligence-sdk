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
Platform-specific query log parsers for Snowflake, Databricks, BigQuery, and watsonx.data

Note: This module only provides query parsing functionality.
Database connections are not supported - use file-based input instead.
"""

import re
from typing import List
import pandas as pd

from .base import QueryLogParser

# Regex pattern for extracting schema.table from FROM/JOIN clauses
TABLE_PATTERN = r'(?:FROM|JOIN)\s+([\w]+\.[\w]+)(?:\s+[a-zA-Z])?'


# ============================================================================
# SNOWFLAKE QUERY PARSER
# ============================================================================

class SnowflakeQueryParser(QueryLogParser):
    """Snowflake-specific query parser"""

    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize Snowflake column names"""
        return df.rename(columns={
            'query_text': 'query_text',
            'user_name': 'user',
            'start_time': 'start_time'
        })

    def extract_tables(self, query_text: str) -> List[str]:
        """Extract table names from SQL query using regex patterns"""
        if not query_text or not isinstance(query_text, str):
            return []

        query_upper = query_text.upper()
        tables = set()

        # Pattern: Match FROM and JOIN clauses with schema.table format
        matches = re.findall(TABLE_PATTERN, query_upper)
        tables.update(matches)

        return list(tables)


# ============================================================================
# DATABRICKS QUERY PARSER
# ============================================================================

class DatabricksQueryParser(QueryLogParser):
    """Databricks-specific query parser"""

    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize Databricks column names"""
        return df.rename(columns={
            'statement_text': 'query_text',
            'executed_by': 'user',
            'start_time': 'start_time'
        })

    def extract_tables(self, query_text: str) -> List[str]:
        """Extract table names from SQL query using regex patterns"""
        if not query_text or not isinstance(query_text, str):
            return []

        query_upper = query_text.upper()
        tables = set()

        # Pattern: Match FROM and JOIN clauses with schema.table format
        matches = re.findall(TABLE_PATTERN, query_upper)
        tables.update(matches)

        return list(tables)


# ============================================================================
# BIGQUERY QUERY PARSER
# ============================================================================

class BigQueryQueryParser(QueryLogParser):
    """BigQuery-specific query parser"""

    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize BigQuery column names"""
        return df.rename(columns={
            'query': 'query_text',
            'user_email': 'user',
            'start_time': 'start_time'
        })

    def extract_tables(self, query_text: str) -> List[str]:
        """Extract table names from BigQuery SQL query using regex patterns"""
        if not query_text or not isinstance(query_text, str):
            return []

        query_upper = query_text.upper()
        tables = set()

        # BigQuery pattern: Match backtick-quoted tables with project.dataset.table format
        # Example: `retailco-project.PRODUCT.CATALOG`
        pattern1 = r'`([\w-]+\.[\w]+\.[\w]+)`'
        matches1 = re.findall(pattern1, query_text)  # Use original case for project names

        # Simplify to DATASET.TABLE format (remove project prefix)
        for match in matches1:
            parts = match.split('.')
            if len(parts) == 3:
                # Keep only dataset.table
                simplified = f"{parts[1]}.{parts[2]}"
                tables.add(simplified.upper())

        # Also try standard pattern for dataset.table without backticks
        matches2 = re.findall(TABLE_PATTERN, query_upper)
        tables.update(matches2)

        return list(tables)


# ============================================================================
# WATSONX.DATA (PRESTO) QUERY PARSER
# ============================================================================

class WatsonxDataQueryParser(QueryLogParser):
    """watsonx.data-specific query parser"""

    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize watsonx.data column names"""
        return df.rename(columns={
            'query': 'query_text',
            'user': 'user',
            'created': 'start_time'
        })

    def extract_tables(self, query_text: str) -> List[str]:
        """Extract table names from SQL query using regex patterns"""
        if not query_text or not isinstance(query_text, str):
            return []

        query_upper = query_text.upper()
        tables = set()

        # Pattern: Match FROM and JOIN clauses with schema.table format
        matches = re.findall(TABLE_PATTERN, query_upper)
        tables.update(matches)

        return list(tables)


# Made with Bob