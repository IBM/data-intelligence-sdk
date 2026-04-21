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
Data Product Recommender - Core recommendation engine
"""

import json
import re
import pandas as pd
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional

from .base import QueryLogParser

# Star rating constants
FIVE_STARS = "⭐⭐⭐⭐⭐"
FOUR_STARS = "⭐⭐⭐⭐"
THREE_STARS = "⭐⭐⭐"
TWO_STARS = "⭐⭐"
ONE_STAR = "⭐"

EXCELLENT_CANDIDATE = "Excellent Candidate"
GOOD_CANDIDATE = "Good Candidate"
FAIR_CANDIDATE = "Fair Candidate"
WEAK_CANDIDATE = "Weak Candidate"
POOR_CANDIDATE = "Poor Candidate"

# Report section headers
QUERY_LOG_METRICS_HEADER = "**Query Log Metrics:**\n"
TABLES_IN_GROUP_HEADER = "**Tables in Group:**\n\n"
TABLES_IN_GROUP_SIMPLE = "**Tables in Group:**\n"
TABLE_HEADER_ROW = "| Table | Individual Score | Queries | Users | Recency | Consistency |\n"
TABLE_SEPARATOR_ROW = "|-------|-----------------|---------|-------|---------|-------------|\n"

# SQL code block markers
SQL_CODE_BLOCK_START = "   ```sql\n"
SQL_CODE_BLOCK_END = "   ```\n"
SQL_EXAMPLE_LABEL = "   - Example:\n"
SQL_EXAMPLE_CODE_START = "     ```sql\n"
SQL_EXAMPLE_CODE_END = "     ```\n"

# HTML collapsible section markers
DETAILS_START = "<details>\n"
DETAILS_SUMMARY = "<summary><b>Frequent Query Patterns</b> (click to expand)</summary>\n\n"
DETAILS_END = "</details>\n\n"


def normalize_query_pattern(query_text: str) -> str:
    """
    Normalize a SQL query into a pattern by replacing literals with placeholders.

    This helps group similar queries together by removing variable parts like:
    - Numbers (123 -> ?)
    - Quoted strings ('value' -> ?)
    - Date literals ('2024-01-01' -> ?)

    Args:
        query_text: The SQL query text to normalize

    Returns:
        Normalized query pattern with literals replaced by ?
    """
    if not query_text or not isinstance(query_text, str):
        return ""

    # Convert to uppercase for consistency
    pattern = query_text.upper()

    # Replace quoted strings (both single and double quotes)
    # Handles escaped quotes within strings
    pattern = re.sub(r"'(?:[^'\\]|\\.)*'", "?", pattern)
    pattern = re.sub(r'"(?:[^"\\]|\\.)*"', "?", pattern)

    # Replace numbers (integers and decimals)
    pattern = re.sub(r'\b\d+\.?\d*\b', '?', pattern)

    # Replace date/timestamp patterns that might remain
    # Format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    pattern = re.sub(r'\b\?-\?-\?\b', '?', pattern)
    pattern = re.sub(r'\b\? \?:\?:\?\b', '?', pattern)

    # Normalize whitespace (multiple spaces/tabs/newlines to single space)
    pattern = re.sub(r'\s+', ' ', pattern)

    # Trim leading/trailing whitespace
    pattern = pattern.strip()

    return pattern


class DataProductRecommender:
    """Analyzes query logs and recommends data products"""

    # Error message constants
    ERROR_QUERY_LOGS_NOT_LOADED = "Query logs not loaded"

    def __init__(self, parser: QueryLogParser):
        self.parser = parser
        self.query_logs = None
        self.table_metrics = None
        self.query_patterns = None  # Store query pattern information

    def load_query_logs_from_json_file(self, file_path: str):
        """Load and normalize query logs from JSON file"""
        print(f"Reading query logs from {file_path}...")
        with open(file_path, 'r') as f:
            data = json.load(f)

        df = pd.DataFrame(data)
        df = self.parser.normalize_columns(df)

        print("Extracting table names from queries...")
        df['tables'] = df['query_text'].apply(self.parser.extract_tables)
        df = df[df['tables'].apply(len) > 0]

        print("Normalizing query patterns...")
        df['query_pattern'] = df['query_text'].apply(normalize_query_pattern)

        self.query_logs = df
        print(f"Processed {len(df):,} queries with table references")
        return df

    def load_query_logs_from_csv_file(self, file_path: str):
        """Load and normalize query logs from CSV or JSON file"""
        print(f"Reading query logs from {file_path}...")

        # Read file based on extension
        if file_path.lower().endswith('.json'):
            df = pd.read_json(file_path)
        else:
            df = pd.read_csv(file_path)

        # Normalize column names based on platform
        df = self.parser.normalize_columns(df)

        # Verify required columns exist
        required_cols = ['query_text', 'user', 'start_time']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"CSV file missing required columns after normalization: {missing_cols}")

        print("Extracting table names from queries...")
        df['tables'] = df['query_text'].apply(self.parser.extract_tables)

        # Filter out queries with no table references
        df = df[df['tables'].apply(len) > 0]

        print("Normalizing query patterns...")
        df['query_pattern'] = df['query_text'].apply(normalize_query_pattern)

        self.query_logs = df
        print(f"Processed {len(df):,} queries with table references")
        return df

    def _calculate_table_query_counts(self) -> Counter:
        """Calculate query count per table"""
        table_query_count = Counter()
        for tables in self.query_logs['tables']:
            table_query_count.update(tables)
        return table_query_count

    def _calculate_table_users(self) -> dict:
        """Calculate user diversity per table"""
        table_users = defaultdict(set)
        for _, row in self.query_logs.iterrows():
            for table in row['tables']:
                table_users[table].add(row['user'])
        return table_users

    def _calculate_table_cooccurrence(self) -> dict:
        """Calculate table co-occurrence"""
        table_cooccurrence = defaultdict(Counter)
        for tables in self.query_logs['tables']:
            for table1 in tables:
                for table2 in tables:
                    if table1 != table2:
                        table_cooccurrence[table1][table2] += 1
        return table_cooccurrence

    def _calculate_table_timestamps(self) -> dict:
        """Calculate temporal metrics per table"""
        table_timestamps = defaultdict(list)
        for _, row in self.query_logs.iterrows():
            for table in row['tables']:
                table_timestamps[table].append(row['start_time'])
        return table_timestamps

    def _calculate_recency_score(self, timestamps: list, reference_time) -> tuple:
        """Calculate recency score and days since last query"""
        days_since_last_query = max(0, (reference_time - max(timestamps)).days)
        recency_score = 1.0 / (1.0 + days_since_last_query)
        return recency_score, days_since_last_query

    def _calculate_consistency_score(self, timestamps: list) -> float:
        """Calculate consistency score based on query intervals"""
        if len(timestamps) <= 1:
            return 0.0

        sorted_times = sorted(timestamps)
        intervals = [(sorted_times[i+1] - sorted_times[i]).days
                   for i in range(len(sorted_times)-1)]
        total_interval = sum(intervals)

        if len(intervals) == 0 or total_interval == 0:
            return 0.5

        mean_interval = total_interval / len(intervals)
        std_interval = (sum((x - mean_interval)**2 for x in intervals) / len(intervals))**0.5
        cv = std_interval / mean_interval if mean_interval > 0 else 0
        return 1.0 / (1.0 + cv)

    def calculate_metrics(self) -> pd.DataFrame:
        """Calculate metrics for each table"""
        if self.query_logs is None:
            raise ValueError(self.ERROR_QUERY_LOGS_NOT_LOADED)

        print("Calculating table metrics...")

        # Convert start_time to datetime if it's not already
        self.query_logs['start_time'] = pd.to_datetime(self.query_logs['start_time'])

        # Calculate all base metrics
        table_query_count = self._calculate_table_query_counts()
        table_users = self._calculate_table_users()
        table_cooccurrence = self._calculate_table_cooccurrence()
        table_timestamps = self._calculate_table_timestamps()

        # Use the most recent query in the dataset as reference for recency calculations
        reference_time = self.query_logs['start_time'].max()

        # Build metrics dataframe
        metrics = []
        for table, query_count in table_query_count.items():
            user_count = len(table_users[table])
            related_tables = [t for t, c in table_cooccurrence[table].most_common(10)]
            timestamps = table_timestamps[table]

            recency_score, days_since_last_query = self._calculate_recency_score(timestamps, reference_time)
            consistency_score = self._calculate_consistency_score(timestamps)

            metrics.append({
                'table': table,
                'query_count': query_count,
                'unique_users': user_count,
                'related_tables': related_tables,
                'related_table_count': len(related_tables),
                'recency_score': recency_score,
                'consistency_score': consistency_score,
                'days_since_last_query': days_since_last_query,
                'first_query_date': min(timestamps),
                'last_query_date': max(timestamps)
            })

        self.table_metrics = pd.DataFrame(metrics)
        print(f"Calculated metrics for {len(self.table_metrics):,} tables")
        return self.table_metrics

    def score_tables(self,
                     query_weight=0.375,
                     user_weight=0.375,
                     recency_weight=0.15,
                     consistency_weight=0.10):
        """
        Score tables based on weighted metrics

        Args:
            query_weight: Weight for query frequency (default 0.375)
            user_weight: Weight for user diversity (default 0.375)
            recency_weight: Weight for recent activity (default 0.15)
            consistency_weight: Weight for consistent usage over time (default 0.10)

        Returns:
            DataFrame with scored tables sorted by recommendation_score

        Note:
            Relationship metrics are not included as standalone tables are packaged
            in isolation without their related tables.
        """
        if self.table_metrics is None:
            raise ValueError("Metrics not calculated")

        # Validate weights sum to 1.0
        total_weight = query_weight + user_weight + recency_weight + consistency_weight
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")

        df = self.table_metrics.copy()

        # Normalize metrics to 0-1 scale, handling edge cases
        max_queries = df['query_count'].max()
        max_users = df['unique_users'].max()

        df['query_score'] = df['query_count'] / max_queries if max_queries > 0 else 0
        df['user_score'] = df['unique_users'] / max_users if max_users > 0 else 0

        # Temporal scores are already 0-1, but ensure no NaN values
        df['recency_score'] = df['recency_score'].fillna(0)
        df['consistency_score'] = df['consistency_score'].fillna(0)

        # Calculate weighted score
        df['recommendation_score'] = (
            df['query_score'] * query_weight +
            df['user_score'] * user_weight +
            df['recency_score'] * recency_weight +
            df['consistency_score'] * consistency_weight
        ) * 100

        return df.sort_values('recommendation_score', ascending=False)
    def get_top_query_patterns(self, tables: List[str], top_n: int = 5) -> List[Dict]:
        """
        Get the most frequent query patterns for a set of tables.

        Args:
            tables: List of table names to analyze
            top_n: Number of top patterns to return (default 5)

        Returns:
            List of dictionaries with pattern info:
            - pattern: The normalized query pattern
            - count: Number of times this pattern appears
            - example: An actual query text example
            - tables_used: Tables from the group that appear in this pattern
        """
        if self.query_logs is None:
            raise ValueError(self.ERROR_QUERY_LOGS_NOT_LOADED)

        if 'query_pattern' not in self.query_logs.columns:
            raise ValueError("Query patterns not computed. Reload query logs.")

        # Filter queries that reference any of the specified tables
        relevant_queries = self.query_logs[
            self.query_logs['tables'].apply(
                lambda query_tables: any(t in tables for t in query_tables)
            )
        ].copy()

        if len(relevant_queries) == 0:
            return []

        # Count pattern frequencies
        pattern_counts = Counter(relevant_queries['query_pattern'])

        # Get top N patterns
        top_patterns = []
        for pattern, count in pattern_counts.most_common(top_n):
            # Find an example query for this pattern
            example_row = relevant_queries[relevant_queries['query_pattern'] == pattern].iloc[0]
            example_query = example_row['query_text']

            # Determine which tables from the group are used in this pattern
            tables_in_pattern = [t for t in tables if t in example_row['tables']]

            top_patterns.append({
                'pattern': pattern,
                'count': count,
                'example': example_query,
                'tables_used': tables_in_pattern
            })

        return top_patterns


    def _count_group_queries(self, table_group: tuple) -> int:
        """Count queries involving any table in the group"""
        if self.query_logs is None:
            return 1  # Avoid division by zero

        count = sum(1 for tables_in_query in self.query_logs['tables']
                    if any(t in tables_in_query for t in table_group))
        return max(count, 1)  # Ensure at least 1 to avoid division by zero

    def _get_pairwise_frequencies(self, table_group: tuple, table_pair_counts: dict,
                                   group_query_count: int) -> tuple:
        """Get pairwise join frequencies and percentages for a table group"""
        frequencies = []
        percentages = []

        for i, table1 in enumerate(table_group):
            for table2 in table_group[i+1:]:
                pair = tuple(sorted([table1, table2]))
                freq = table_pair_counts.get(pair, 0)
                frequencies.append(freq)
                percentages.append(freq / group_query_count)

        return frequencies, percentages

    def _calculate_group_cohesion(self, table_group: tuple, table_pair_counts: dict) -> dict:
        """
        Calculate cohesion metrics for a table group

        Args:
            table_group: Tuple of table names in the group
            table_pair_counts: Dictionary mapping (table1, table2) -> count

        Returns:
            Dictionary with cohesion metrics including:
            - avg_join_frequency: Average absolute co-occurrence count
            - avg_join_percentage: Average co-occurrence as percentage of group queries (0-1)
            - min_join_frequency: Minimum co-occurrence count
            - max_join_frequency: Maximum co-occurrence count
            - total_pairs: Number of table pairs in the group
        """
        if len(table_group) < 2:
            return {
                'avg_join_frequency': 0,
                'avg_join_percentage': 0,
                'min_join_frequency': 0,
                'max_join_frequency': 0,
                'total_pairs': 0
            }

        group_query_count = self._count_group_queries(table_group)
        frequencies, percentages = self._get_pairwise_frequencies(
            table_group, table_pair_counts, group_query_count
        )

        return {
            'avg_join_frequency': sum(frequencies) / len(frequencies) if frequencies else 0,
            'avg_join_percentage': sum(percentages) / len(percentages) if percentages else 0,
            'min_join_frequency': min(frequencies) if frequencies else 0,
            'max_join_frequency': max(frequencies) if frequencies else 0,
            'total_pairs': len(frequencies)
        }

    def _count_table_occurrences(self) -> Counter:
        """Count how many times each table appears in queries"""
        table_query_counts = Counter()
        for tables in self.query_logs['tables']:
            table_query_counts.update(tables)
        return table_query_counts

    def _count_table_pairs(self) -> Counter:
        """Count pairwise co-occurrences of tables"""
        table_pair_counts = Counter()
        for tables in self.query_logs['tables']:
            if len(tables) >= 2:
                for i, table1 in enumerate(tables):
                    for table2 in tables[i+1:]:
                        pair = tuple(sorted([table1, table2]))
                        table_pair_counts[pair] += 1
        return table_pair_counts

    def _build_strong_connections(self, table_pair_counts: Counter, table_query_counts: Counter,
                                   min_frequency_threshold: float) -> dict:
        """Build adjacency list of strong table connections"""
        strong_connections = defaultdict(set)

        for (table1, table2), count in table_pair_counts.items():
            freq1 = count / table_query_counts[table1] if table_query_counts[table1] > 0 else 0
            freq2 = count / table_query_counts[table2] if table_query_counts[table2] > 0 else 0
            min_freq = min(freq1, freq2)

            if min_freq >= min_frequency_threshold:
                strong_connections[table1].add(table2)
                strong_connections[table2].add(table1)

        return strong_connections

    def _find_best_candidate(self, candidates: set, cluster: set, strong_connections: dict) -> tuple:
        """Find the best candidate to add to a cluster"""
        best_candidate = None
        best_connection_count = 0

        for candidate in candidates:
            connection_count = len(cluster & strong_connections[candidate])
            if connection_count > best_connection_count:
                best_candidate = candidate
                best_connection_count = connection_count

        return best_candidate, best_connection_count

    def _grow_cluster(self, core_table: str, strong_connections: dict, visited: set,
                      max_group_size: int) -> set:
        """Grow a cluster starting from a core table"""
        cluster = {core_table}
        candidates = strong_connections[core_table] - visited

        while candidates and len(cluster) < max_group_size:
            best_candidate, best_connection_count = self._find_best_candidate(
                candidates, cluster, strong_connections
            )

            if best_candidate and best_connection_count > 0:
                cluster.add(best_candidate)
                candidates.remove(best_candidate)
                candidates.update(strong_connections[best_candidate] - visited - cluster)
            else:
                break

        return cluster

    def _create_cluster_dict(self, cluster_tuple: tuple, table_pair_counts: Counter) -> dict:
        """Create a cluster dictionary with cohesion metrics"""
        cohesion = self._calculate_group_cohesion(cluster_tuple, table_pair_counts)

        return {
            'tables': list(cluster_tuple),
            'size': len(cluster_tuple),
            'avg_join_frequency': cohesion['avg_join_frequency'],
            'avg_join_percentage': cohesion['avg_join_percentage'],
            'min_join_frequency': cohesion['min_join_frequency'],
            'max_join_frequency': cohesion['max_join_frequency']
        }

    def _build_frequency_clusters(self, min_frequency_threshold=0.10, min_group_size=2, max_group_size=10):
        """
        Build table clusters using frequency-based threshold approach

        Args:
            min_frequency_threshold: Minimum join frequency as percentage (0.0-1.0).
                                   Tables must join together in at least this % of queries
                                   where either table appears.
            min_group_size: Minimum number of tables in a group
            max_group_size: Maximum number of tables in a group

        Returns:
            List of dictionaries with cluster information
        """
        if self.query_logs is None:
            raise ValueError(self.ERROR_QUERY_LOGS_NOT_LOADED)

        print(f"Building frequency-based clusters (threshold: {min_frequency_threshold*100:.1f}%)...")

        table_query_counts = self._count_table_occurrences()
        table_pair_counts = self._count_table_pairs()
        strong_connections = self._build_strong_connections(
            table_pair_counts, table_query_counts, min_frequency_threshold
        )

        visited = set()
        clusters = []

        sorted_tables = sorted(strong_connections.keys(),
                             key=lambda t: len(strong_connections[t]),
                             reverse=True)

        for core_table in sorted_tables:
            if core_table in visited:
                continue

            cluster = self._grow_cluster(core_table, strong_connections, visited, max_group_size)

            if len(cluster) >= min_group_size:
                visited.update(cluster)
                cluster_tuple = tuple(sorted(cluster))
                clusters.append(self._create_cluster_dict(cluster_tuple, table_pair_counts))

        clusters.sort(key=lambda x: x['avg_join_frequency'], reverse=True)

        print(f"Built {len(clusters)} frequency-based clusters")
        return clusters

    def _calculate_cluster_query_counts(self, clusters: list) -> list:
        """Calculate query counts for all clusters"""
        cluster_query_counts = []
        for cluster in clusters:
            tables = cluster['tables']
            queries_with_group = sum(
                1 for tables_in_query in self.query_logs['tables']
                if any(t in tables_in_query for t in tables)
            )
            cluster_query_counts.append(queries_with_group)
        return cluster_query_counts

    def _get_cluster_users(self, tables: list) -> set:
        """Get unique users querying a cluster"""
        users_querying_group = set()
        for _, row in self.query_logs.iterrows():
            if any(t in row['tables'] for t in tables):
                users_querying_group.add(row['user'])
        return users_querying_group

    def _get_temporal_scores(self, tables: list) -> tuple:
        """Extract temporal metrics for tables in a cluster"""
        recency_scores = []
        consistency_scores = []

        for table in tables:
            table_data = self.table_metrics[self.table_metrics['table'] == table]
            if not table_data.empty:
                recency_scores.append(table_data['recency_score'].values[0])
                consistency_scores.append(table_data['consistency_score'].values[0])

        avg_recency = sum(recency_scores) / len(recency_scores) if recency_scores else 0.0
        avg_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.0

        return avg_recency, avg_consistency

    def _calculate_normalized_scores(self, cluster: dict, queries_with_group: int,
                                      users_count: int, max_queries: int, max_group_size: int) -> dict:
        """Calculate normalized scores for a cluster"""
        cohesion_score = cluster['avg_join_percentage']
        usage_score = queries_with_group / max_queries if max_queries > 0 else 0
        total_users = self.query_logs['user'].nunique()
        user_score = users_count / total_users if total_users > 0 else 0
        size_score = cluster['size'] / max_group_size if max_group_size > 0 else 0

        return {
            'cohesion_score': cohesion_score,
            'usage_score': usage_score,
            'user_score': user_score,
            'size_score': size_score
        }

    def _calculate_group_score(self, scores: dict, avg_recency: float, avg_consistency: float) -> float:
        """Calculate weighted group score (0-100 scale)"""
        return (
            scores['cohesion_score'] * 0.30 +
            scores['usage_score'] * 0.20 +
            scores['user_score'] * 0.15 +
            avg_recency * 0.20 +
            avg_consistency * 0.10 +
            scores['size_score'] * 0.05
        ) * 100

    def _score_table_groups(self, clusters: list) -> list:
        """
        Calculate group-specific scores for table clusters

        Args:
            clusters: List of cluster dictionaries from _build_frequency_clusters

        Returns:
            List of clusters with added 'group_score' field
        """
        if self.query_logs is None or self.table_metrics is None:
            raise ValueError("Query logs and table metrics must be loaded")

        max_group_size = max((c['size'] for c in clusters), default=1)
        cluster_query_counts = self._calculate_cluster_query_counts(clusters)
        max_queries = max(cluster_query_counts) if cluster_query_counts else 1

        scored_clusters = []
        for i, cluster in enumerate(clusters):
            tables = cluster['tables']
            queries_with_group = cluster_query_counts[i]

            users_querying_group = self._get_cluster_users(tables)
            avg_recency, avg_consistency = self._get_temporal_scores(tables)

            scores = self._calculate_normalized_scores(
                cluster, queries_with_group, len(users_querying_group),
                max_queries, max_group_size
            )

            group_score = self._calculate_group_score(scores, avg_recency, avg_consistency)

            scored_clusters.append({
                **cluster,
                'group_score': group_score,
                'total_queries': queries_with_group,
                'unique_users': len(users_querying_group),
                'avg_recency_score': avg_recency,
                'avg_consistency_score': avg_consistency,
                'cohesion_score': scores['cohesion_score'] * 100,
                'usage_score': scores['usage_score'] * 100,
                'user_score': scores['user_score'] * 100,
                'size_score': scores['size_score'] * 100
            })

        scored_clusters.sort(key=lambda x: x['group_score'], reverse=True)
        return scored_clusters

    def identify_table_groups(self, min_cooccurrence=None):
        """
        Identify groups of frequently co-occurring tables

        Args:
            min_cooccurrence: Minimum number of times tables must appear together.
                            If None, automatically calculated as 0.01% of total queries
                            (minimum 2, maximum 100)

        Returns:
            List of tuples: (table_group, count) sorted by count descending
        """
        if self.query_logs is None:
            raise ValueError(self.ERROR_QUERY_LOGS_NOT_LOADED)

        print("Identifying table groups...")

        # Calculate dynamic threshold if not provided
        if min_cooccurrence is None:
            total_queries = len(self.query_logs)
            # Use 0.01% of queries as threshold (1 in 10,000)
            min_cooccurrence = max(2, min(100, int(total_queries * 0.0001)))
            print(f"Auto-calculated co-occurrence threshold: {min_cooccurrence} (based on {total_queries:,} queries)")

        table_groups = Counter()
        for tables in self.query_logs['tables']:
            if len(tables) >= 2:
                # Sort tables to ensure consistent grouping
                table_groups[tuple(sorted(tables))] += 1

        # Filter by minimum co-occurrence
        filtered_groups = [(group, count) for group, count in table_groups.items()
                          if count >= min_cooccurrence]

        # Sort by count descending
        filtered_groups.sort(key=lambda x: x[1], reverse=True)

        print(f"Found {len(filtered_groups)} table groups with {min_cooccurrence}+ co-occurrences")
        return filtered_groups

    def recommend_data_products(self,
                              num_recommendations=10,
                              min_score=None,
                              min_frequency_threshold=0.10,
                              min_group_size=2,
                              max_group_size=10):
        """
        Generate final data product recommendations using frequency-based clustering

        Args:
            num_recommendations: Maximum number of top recommendations to return
            min_score: Minimum recommendation score threshold (0-100).
                      Tables below this score will be excluded from all recommendations.
                      Also used to filter standalone (unclustered) tables.
                      If None, no score filtering is applied.
            min_frequency_threshold: Minimum join frequency for clustering (0.0-1.0)
            min_group_size: Minimum tables in a cluster
            max_group_size: Maximum tables in a cluster

        Returns:
            Dictionary with 'individual_tables', 'table_groups', and optionally 'standalone_tables'
        """
        scored_tables = self.score_tables()

        # Store metadata before filtering
        total_tables = len(scored_tables)
        highest_score = scored_tables['recommendation_score'].max() if len(scored_tables) > 0 else 0

        # Apply score threshold if specified
        if min_score is not None:
            scored_tables = scored_tables[scored_tables['recommendation_score'] >= min_score]
            print(f"Applied score threshold: {min_score} (kept {len(scored_tables)} tables)")

        # Limit to top N
        top_tables = scored_tables.head(num_recommendations)

        recommendations = {
            'individual_tables': top_tables.to_dict('records'),
            'metadata': {
                'total_tables': total_tables,
                'recommended_tables': len(top_tables),
                'highest_score': highest_score,
                'min_score_threshold': min_score,
                'clustering_enabled': True  # Always enabled now
            }
        }

        # Build frequency-based clusters
        clusters = self._build_frequency_clusters(
            min_frequency_threshold=min_frequency_threshold,
            min_group_size=min_group_size,
            max_group_size=max_group_size
        )
        scored_clusters = self._score_table_groups(clusters)

        # Track which tables are in clusters
        tables_in_clusters = set()
        for cluster in scored_clusters:
            tables_in_clusters.update(cluster['tables'])

        # Add individual table details to each group
        for cluster in scored_clusters[:num_recommendations]:
            cluster['table_details'] = []
            for table_name in cluster['tables']:
                table_info = scored_tables[scored_tables['table'] == table_name]
                if not table_info.empty:
                    cluster['table_details'].append(table_info.iloc[0].to_dict())

        recommendations['table_groups'] = scored_clusters[:num_recommendations]

        # Identify high-value standalone tables (not in any cluster)
        # Use the same min_score threshold if provided
        standalone_threshold = min_score if min_score is not None else 0
        standalone_tables = scored_tables[
            (~scored_tables['table'].isin(tables_in_clusters)) &
            (scored_tables['recommendation_score'] >= standalone_threshold)
        ]

        if len(standalone_tables) > 0:
            recommendations['standalone_tables'] = standalone_tables.head(num_recommendations).to_dict('records')
            recommendations['metadata']['standalone_tables_count'] = len(standalone_tables)

        return recommendations

    def _write_markdown_header(self, f):
        """Write markdown file header"""
        f.write("# Data Product Recommendations\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    def _write_summary_stats(self, f):
        """Write summary statistics section"""
        f.write("## Summary Statistics\n\n")
        if self.query_logs is not None:
            f.write(f"- Total queries analyzed: {len(self.query_logs):,}\n")
            f.write(f"- Unique users: {self.query_logs['user'].nunique()}\n")
        if self.table_metrics is not None:
            f.write(f"- Unique tables: {len(self.table_metrics)}\n")

    def _calculate_clustering_stats(self, recommendations: dict, metadata: dict) -> dict:
        """Calculate statistics for clustering mode"""
        num_groups = len(recommendations['table_groups'])
        total_tables = metadata['total_tables']

        tables_in_groups = set()
        for group in recommendations['table_groups']:
            tables_in_groups.update(group['tables'])

        tables_standalone = set()
        num_standalone = 0
        if 'standalone_tables' in recommendations:
            num_standalone = len(recommendations['standalone_tables'])
            tables_standalone = {t['table'] for t in recommendations['standalone_tables']}

        total_recommended = len(tables_in_groups) + len(tables_standalone)

        return {
            'num_groups': num_groups,
            'num_standalone': num_standalone,
            'tables_in_groups_count': len(tables_in_groups),
            'tables_standalone_count': len(tables_standalone),
            'total_recommended': total_recommended,
            'total_tables': total_tables
        }

    def _write_clustering_stats(self, f, stats: dict, metadata: dict):
        """Write clustering statistics"""
        total_coverage_pct = (stats['total_recommended'] / stats['total_tables'] * 100) if stats['total_tables'] > 0 else 0
        groups_coverage_pct = (stats['tables_in_groups_count'] / stats['total_tables'] * 100) if stats['total_tables'] > 0 else 0
        standalone_coverage_pct = (stats['tables_standalone_count'] / stats['total_tables'] * 100) if stats['total_tables'] > 0 else 0

        f.write(f"- Total data products recommended: {stats['num_groups'] + stats['num_standalone']}\n")
        f.write(f"  - Multi-table products: {stats['num_groups']}\n")
        f.write(f"  - Single-table products: {stats['num_standalone']}\n")
        f.write(f"- Recommendation coverage: {stats['total_recommended']} of {stats['total_tables']} ({total_coverage_pct:.1f}%)\n")
        f.write(f"  - In groups: {stats['tables_in_groups_count']} ({groups_coverage_pct:.1f}%)\n")
        f.write(f"  - Standalone: {stats['tables_standalone_count']} ({standalone_coverage_pct:.1f}%)\n")

        if metadata.get('min_score_threshold') is not None:
            f.write(f"- Minimum score threshold: {metadata['min_score_threshold']:.1f}\n")

    def _write_non_clustering_stats(self, f, metadata: dict):
        """Write non-clustering statistics"""
        total = metadata['total_tables']
        recommended = metadata['recommended_tables']
        percentage = (recommended / total * 100) if total > 0 else 0
        f.write(f"- Total recommended tables: {recommended} ({percentage:.1f}% of all tables)\n")
        f.write(f"- Highest table score: {metadata['highest_score']:.1f}\n")
        if metadata.get('min_score_threshold') is not None:
            f.write(f"- Minimum score threshold: {metadata['min_score_threshold']:.1f}\n")

    def _write_recommendation_stats(self, f, recommendations: dict):
        """Write recommendation statistics section"""
        if 'metadata' not in recommendations:
            return

        metadata = recommendations['metadata']

        if metadata.get('clustering_enabled', False) and 'table_groups' in recommendations:
            stats = self._calculate_clustering_stats(recommendations, metadata)
            self._write_clustering_stats(f, stats, metadata)
        else:
            self._write_non_clustering_stats(f, metadata)

        f.write("\n")

    def _write_individual_tables_header(self, f):
        """Write individual tables section header"""
        f.write("## Top Recommended Tables\n\n")
        f.write("| Rank | Table | Score | Queries | Users | Recency | Consistency | Last Query | Related Tables |\n")
        f.write("|------|-------|-------|---------|-------|---------|-------------|------------|----------------|\n")

    def _format_table_row(self, i: int, table: dict) -> str:
        """Format a single table row for markdown"""
        related = ', '.join(table['related_tables'][:3]) if table['related_tables'] else 'None'
        recency_pct = f"{table.get('recency_score', 0)*100:.0f}%"
        consistency_pct = f"{table.get('consistency_score', 0)*100:.0f}%"
        days_ago = table.get('days_since_last_query', 'N/A')
        days_ago_str = f"{days_ago}d ago" if isinstance(days_ago, (int, float)) else days_ago

        return (f"| {i} | {table['table']} | {table['recommendation_score']:.1f} | "
                f"{table['query_count']} | {table['unique_users']} | "
                f"{recency_pct} | {consistency_pct} | {days_ago_str} | {related} |\n")

    def _write_table_metric_definitions(self, f):
        """Write table metric definitions"""
        f.write("\n### Metric Definitions\n\n")
        f.write("- **Score**: Overall recommendation score (0-100)\n")
        f.write("- **Queries**: Total number of queries referencing this table\n")
        f.write("- **Users**: Number of unique users querying this table\n")
        f.write("- **Recency**: How recently the table was queried (100% = queried today)\n")
        f.write("- **Consistency**: How consistently the table is queried over time (100% = perfectly regular)\n")
        f.write("- **Last Query**: Days since the most recent query\n")
        f.write("- **Related Tables**: Tables frequently queried together with this one\n")
        f.write("\n")

    def _write_individual_tables_section(self, f, recommendations: dict):
        """Write individual tables section"""
        self._write_individual_tables_header(f)

        for i, table in enumerate(recommendations['individual_tables'], 1):
            f.write(self._format_table_row(i, table))

        self._write_table_metric_definitions(f)

    def _write_data_product_metric_definitions(self, f):
        """Write data product metric definitions"""
        f.write("\n### Data Product Metric Definitions\n\n")
        f.write("- **Score**: Overall recommendation score for the data product (0-100)\n")
        f.write("  - Star Rating Scale:\n")
        f.write(f"    - {FIVE_STARS} {EXCELLENT_CANDIDATE} (80-100): Strong data product candidate, implement immediately\n")
        f.write(f"    - {FOUR_STARS} {GOOD_CANDIDATE} (60-79): Solid candidate, implement as medium priority\n")
        f.write(f"    - {THREE_STARS} {FAIR_CANDIDATE} (40-59): Consider splitting or implement later\n")
        f.write(f"    - {TWO_STARS} {WEAK_CANDIDATE} (20-39): Reconsider grouping\n")
        f.write(f"    - {ONE_STAR} {POOR_CANDIDATE} (0-19): Do not implement as data product\n")
        f.write("- **General Metrics:**\n")
        f.write("  - **Total Queries**: Total number of queries that touched the table(s)\n")
        f.write("  - **Unique Users**: Number of distinct users who queried the table(s)\n")
        f.write("- **Table Metrics:**\n")
        f.write("  - **Recency Score**: How recently the table was queried (relative to dataset's most recent query)\n")
        f.write("  - **Consistency Score**: What % of days (in the log timespan) the table was queried\n")
        f.write("- **Table Group Metrics:**\n")
        f.write("  - **Group Cohesion Score**: What % of queries join multiple tables from the group together\n")
        f.write("  - **Avg Join Frequency**: Average number of times per day tables in the group are joined together\n")

    def _get_star_rating(self, score: float) -> tuple:
        """Get star rating and label for a score"""
        if score >= 80:
            return FIVE_STARS, EXCELLENT_CANDIDATE
        elif score >= 60:
            return FOUR_STARS, GOOD_CANDIDATE
        elif score >= 40:
            return THREE_STARS, FAIR_CANDIDATE
        elif score >= 20:
            return TWO_STARS, WEAK_CANDIDATE
        else:
            return ONE_STAR, POOR_CANDIDATE

    def _merge_and_sort_products(self, recommendations: dict) -> list:
        """Merge groups and standalone tables, sorted by score"""
        all_products = []

        if 'table_groups' in recommendations:
            for group in recommendations['table_groups']:
                all_products.append({
                    'type': 'group',
                    'score': group['group_score'],
                    'data': group
                })

        if 'standalone_tables' in recommendations:
            for table in recommendations['standalone_tables']:
                all_products.append({
                    'type': 'standalone',
                    'score': table['recommendation_score'],
                    'data': table
                })

        all_products.sort(key=lambda x: x['score'], reverse=True)
        return all_products

    def _write_group_metrics(self, f, group: dict):
        """Write group-level metrics"""
        f.write(QUERY_LOG_METRICS_HEADER)
        f.write(f"- Total Queries: {group['total_queries']:,}\n")
        f.write(f"- Unique Users: {group['unique_users']}\n")
        f.write(f"- Tables in Group: {group['size']}\n")
        f.write("- Group Metrics:\n")
        f.write(f"  - Cohesion Score: {group['cohesion_score']:.1f}%\n")
        f.write(f"  - Average Join Frequency: {group['avg_join_frequency']:.1f}\n")
        f.write("\n")

    def _write_group_tables(self, f, group: dict):
        """Write tables in group section"""
        if 'table_details' in group and group['table_details']:
            f.write(TABLES_IN_GROUP_HEADER)
            f.write(TABLE_HEADER_ROW)
            f.write(TABLE_SEPARATOR_ROW)

            for table in group['table_details']:
                recency_pct = f"{table.get('recency_score', 0)*100:.0f}%"
                consistency_pct = f"{table.get('consistency_score', 0)*100:.0f}%"
                f.write(f"| {table['table']} | {table['recommendation_score']:.1f} | "
                       f"{table['query_count']} | {table['unique_users']} | "
                       f"{recency_pct} | {consistency_pct} |\n")
        else:
            f.write(TABLES_IN_GROUP_SIMPLE)
            for table in group['tables']:
                f.write(f"- {table}\n")
        f.write("\n")

    def _truncate_text(self, text: str, max_length: int = 200) -> str:
        """Truncate text if too long"""
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text

    def _write_query_pattern(self, f, idx: int, pattern_info: dict):
        """Write a single query pattern"""
        f.write(f"{idx}. **Pattern** (used {pattern_info['count']} times):\n")
        f.write(SQL_CODE_BLOCK_START)
        f.write(f"   {self._truncate_text(pattern_info['pattern'])}\n")
        f.write(SQL_CODE_BLOCK_END)

        if 'tables_used' in pattern_info:
            f.write(f"   - Tables used: {', '.join(pattern_info['tables_used'])}\n")

        f.write(SQL_EXAMPLE_LABEL)
        f.write(SQL_EXAMPLE_CODE_START)
        f.write(f"     {self._truncate_text(pattern_info['example'])}\n")
        f.write(SQL_EXAMPLE_CODE_END)
        f.write("\n")

    def _write_query_patterns(self, f, tables: list, product_id: int):
        """Write query patterns section"""
        try:
            top_patterns = self.get_top_query_patterns(tables, top_n=5)
            if top_patterns:
                f.write(DETAILS_START)
                f.write(DETAILS_SUMMARY)
                for idx, pattern_info in enumerate(top_patterns, 1):
                    self._write_query_pattern(f, idx, pattern_info)
                f.write(DETAILS_END)
        except Exception as e:
            print(f"Warning: Could not generate query patterns for product {product_id}: {e}")
        f.write("\n")

    def _write_group_product(self, f, i: int, group: dict):
        """Write a group data product"""
        score = group['group_score']
        stars, rating = self._get_star_rating(score)

        f.write(f"### Data Product {i} - Score: {score:.1f} {stars} ({rating})\n\n")
        self._write_group_metrics(f, group)
        self._write_group_tables(f, group)
        self._write_query_patterns(f, group['tables'], i)

    def _write_standalone_product(self, f, i: int, table: dict):
        """Write a standalone table data product"""
        score = table['recommendation_score']
        stars, rating = self._get_star_rating(score)

        f.write(f"### Data Product {i} - Score: {score:.1f} {stars} ({rating})\n\n")

        f.write(QUERY_LOG_METRICS_HEADER)
        f.write(f"- Total Queries: {table['query_count']:,}\n")
        f.write(f"- Unique Users: {table['unique_users']}\n")
        f.write("- Tables in Group: 1\n")
        f.write("\n")

        recency_pct = f"{table.get('recency_score', 0)*100:.0f}%"
        consistency_pct = f"{table.get('consistency_score', 0)*100:.0f}%"

        f.write(TABLES_IN_GROUP_HEADER)
        f.write(TABLE_HEADER_ROW)
        f.write(TABLE_SEPARATOR_ROW)
        f.write(f"| {table['table']} | {table['recommendation_score']:.1f} | "
               f"{table['query_count']} | {table['unique_users']} | "
               f"{recency_pct} | {consistency_pct} |\n")
        f.write("\n")

        self._write_query_patterns(f, [table['table']], i)

    def _write_clustered_products(self, f, recommendations: dict):
        """Write clustered data products section"""
        f.write("\n## Recommended Data Products\n\n")
        f.write("*Sorted by recommendation score (descending). Groups identified using frequency-based clustering.*\n\n")
        f.write("*Note: Group scores and individual table scores use different weighting formulas and are not directly comparable, but both indicate relative value within their category.*\n\n")

        all_products = self._merge_and_sort_products(recommendations)

        for i, product in enumerate(all_products, 1):
            if product['type'] == 'group':
                self._write_group_product(f, i, product['data'])
            else:
                self._write_standalone_product(f, i, product['data'])

    def _write_original_groups(self, f, recommendations: dict):
        """Write original co-occurrence format groups"""
        f.write("\n## Recommended Table Groups\n\n")
        f.write("Tables that are frequently queried together:\n\n")

        for i, group in enumerate(recommendations['table_groups'], 1):
            f.write(f"### Group {i} (Co-occurrence: {group['co_occurrence_count']})\n\n")
            for table in group['tables']:
                f.write(f"- {table}\n")
            f.write("\n")

    def export_recommendations_markdown(self, recommendations: dict, output_file: str):
        """Export recommendations to markdown file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            self._write_markdown_header(f)
            self._write_summary_stats(f)
            self._write_recommendation_stats(f, recommendations)

            clustering_enabled = recommendations.get('metadata', {}).get('clustering_enabled', False)

            if not clustering_enabled:
                self._write_individual_tables_section(f, recommendations)

            if 'table_groups' in recommendations:
                self._write_data_product_metric_definitions(f)

                if clustering_enabled:
                    self._write_clustered_products(f, recommendations)
                else:
                    self._write_original_groups(f, recommendations)


    def _build_json_metadata(self, recommendations: dict) -> dict:
        """Build metadata section for JSON export"""
        from datetime import datetime
        return {
            "generated_at": datetime.now().isoformat(),
            "total_queries_analyzed": len(self.query_logs) if self.query_logs is not None else 0,
            "unique_users": int(self.query_logs['user'].nunique()) if self.query_logs is not None else 0,
            "unique_tables": len(self.table_metrics) if self.table_metrics is not None else 0,
            "platform": self.parser.__class__.__name__.replace('QueryParser', '').lower(),
            "clustering_enabled": recommendations.get('metadata', {}).get('clustering_enabled', False),
            "min_score_threshold": recommendations.get('metadata', {}).get('min_score_threshold')
        }

    def _add_table_details_to_product(self, product: dict, group: dict):
        """Add table details to a group product"""
        if 'table_details' in group and group['table_details']:
            for table_info in group['table_details']:
                product["table_details"].append({
                    "table": table_info['table'],
                    "score": round(table_info['recommendation_score'], 1),
                    "queries": table_info['query_count'],
                    "users": table_info['unique_users'],
                    "recency_score": round(table_info.get('recency_score', 0), 2),
                    "consistency_score": round(table_info.get('consistency_score', 0), 2)
                })

    def _add_query_patterns_to_product(self, product: dict, tables: list, include_tables_used: bool = True):
        """Add query patterns to a product"""
        try:
            patterns = self.get_top_query_patterns(tables, top_n=5)
            for pattern_info in patterns:
                pattern_dict = {
                    "pattern": pattern_info['pattern'],
                    "count": pattern_info['count'],
                    "example": pattern_info['example']
                }
                if include_tables_used and 'tables_used' in pattern_info:
                    pattern_dict["tables_used"] = pattern_info['tables_used']
                product["query_patterns"].append(pattern_dict)
        except Exception:
            pass  # Skip patterns if error

    def _create_group_product_json(self, idx: int, group: dict) -> dict:
        """Create JSON product for a group"""
        product = {
            "id": f"dp_{idx:03d}",
            "type": "group",
            "score": round(group['group_score'], 1),
            "rating": self._get_rating_label(group['group_score']),
            "tables": group['tables'],
            "metrics": {
                "total_queries": group['total_queries'],
                "unique_users": group['unique_users'],
                "table_count": group['size'],
                "cohesion_score": round(group['cohesion_score'], 1),
                "avg_join_frequency": round(group['avg_join_frequency'], 1),
                "recency_score": round(group.get('avg_recency_score', 0), 2),
                "consistency_score": round(group.get('avg_consistency_score', 0), 2)
            },
            "table_details": [],
            "query_patterns": []
        }

        self._add_table_details_to_product(product, group)
        self._add_query_patterns_to_product(product, group['tables'], include_tables_used=True)

        return product

    def _create_standalone_product_json(self, idx: int, table: dict) -> dict:
        """Create JSON product for a standalone table"""
        product = {
            "id": f"dp_{idx:03d}",
            "type": "standalone",
            "score": round(table['recommendation_score'], 1),
            "rating": self._get_rating_label(table['recommendation_score']),
            "tables": [table['table']],
            "metrics": {
                "total_queries": table['query_count'],
                "unique_users": table['unique_users'],
                "table_count": 1,
                "recency_score": round(table.get('recency_score', 0), 2),
                "consistency_score": round(table.get('consistency_score', 0), 2)
            },
            "query_patterns": []
        }

        self._add_query_patterns_to_product(product, [table['table']], include_tables_used=False)

        return product

    def _process_clustered_recommendations(self, recommendations: dict) -> list:
        """Process recommendations in clustering mode"""
        all_products = []

        if 'table_groups' in recommendations:
            for idx, group in enumerate(recommendations['table_groups'], 1):
                product = self._create_group_product_json(idx, group)
                all_products.append(product)

        if 'standalone_tables' in recommendations:
            start_idx = len(all_products) + 1
            for idx, table in enumerate(recommendations['standalone_tables'], start_idx):
                product = self._create_standalone_product_json(idx, table)
                all_products.append(product)

        all_products.sort(key=lambda x: x['score'], reverse=True)
        return all_products

    def _process_non_clustered_recommendations(self, recommendations: dict) -> list:
        """Process recommendations in non-clustering mode"""
        products = []

        if 'individual_tables' in recommendations:
            for idx, table in enumerate(recommendations['individual_tables'], 1):
                product = self._create_standalone_product_json(idx, table)
                # Add tables_used for non-clustered mode
                try:
                    patterns = self.get_top_query_patterns([table['table']], top_n=5)
                    product["query_patterns"] = []
                    for pattern_info in patterns:
                        product["query_patterns"].append({
                            "pattern": pattern_info['pattern'],
                            "count": pattern_info['count'],
                            "tables_used": pattern_info.get('tables_used', []),
                            "example": pattern_info['example']
                        })
                except Exception:
                    pass

                products.append(product)

        return products

    def export_recommendations_json(self, recommendations: dict, output_file: str):
        """Export recommendations to JSON file for agent consumption"""
        import json

        output = {
            "recommendations": [],
            "metadata": self._build_json_metadata(recommendations)
        }

        clustering_enabled = recommendations.get('metadata', {}).get('clustering_enabled', False)

        if clustering_enabled:
            output["recommendations"] = self._process_clustered_recommendations(recommendations)
        else:
            output["recommendations"] = self._process_non_clustered_recommendations(recommendations)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

    def _get_rating_label(self, score: float) -> str:
        """Convert numeric score to rating label"""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        elif score >= 20:
            return "weak"
        else:
            return "poor"

# Made with Bob
