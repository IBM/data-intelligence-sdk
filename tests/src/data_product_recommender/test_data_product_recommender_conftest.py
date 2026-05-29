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
Pytest configuration and shared fixtures
"""

import pytest
import pandas as pd
import json
import tempfile
import os


@pytest.fixture
def sample_query_logs():
    """Sample query logs for testing"""
    return pd.DataFrame({
        'query_text': [
            'SELECT * FROM SALES.CUSTOMERS',
            'SELECT * FROM SALES.CUSTOMERS WHERE active = true',
            'SELECT * FROM SALES.ORDERS',
            'SELECT * FROM SALES.CUSTOMERS c JOIN SALES.ORDERS o ON c.id = o.customer_id',
            'SELECT * FROM PRODUCT.CATALOG'
        ],
        'user': ['user1', 'user2', 'user1', 'user3', 'user2'],
        'start_time': [
            '2025-01-01 10:00:00',
            '2025-01-01 11:00:00',
            '2025-01-01 12:00:00',
            '2025-01-01 13:00:00',
            '2025-01-01 14:00:00'
        ]
    })


@pytest.fixture
def sample_query_logs_with_tables():
    """Sample query logs with tables already extracted"""
    return pd.DataFrame({
        'query_text': [
            'SELECT * FROM SALES.CUSTOMERS',
            'SELECT * FROM SALES.CUSTOMERS WHERE active = true',
            'SELECT * FROM SALES.ORDERS',
            'SELECT * FROM SALES.CUSTOMERS c JOIN SALES.ORDERS o ON c.id = o.customer_id',
            'SELECT * FROM PRODUCT.CATALOG'
        ],
        'user': ['user1', 'user2', 'user1', 'user3', 'user2'],
        'start_time': [
            '2025-01-01 10:00:00',
            '2025-01-01 11:00:00',
            '2025-01-01 12:00:00',
            '2025-01-01 13:00:00',
            '2025-01-01 14:00:00'
        ],
        'tables': [
            ['SALES.CUSTOMERS'],
            ['SALES.CUSTOMERS'],
            ['SALES.ORDERS'],
            ['SALES.CUSTOMERS', 'SALES.ORDERS'],
            ['PRODUCT.CATALOG']
        ]
    })


@pytest.fixture
def sample_table_metrics():
    """Sample table metrics for testing"""
    return pd.DataFrame({
        'table': ['SALES.CUSTOMERS', 'SALES.ORDERS', 'PRODUCT.CATALOG'],
        'query_count': [10, 5, 2],
        'unique_users': [5, 3, 1],
        'related_tables': [
            ['SALES.ORDERS', 'PRODUCT.CATALOG'],
            ['SALES.CUSTOMERS'],
            []
        ],
        'related_table_count': [2, 1, 0]
    })


@pytest.fixture
def temp_json_file(sample_query_logs):
    """Create a temporary JSON file with sample data"""
    data = sample_query_logs.to_dict('records')

    # Rename columns to match raw format
    for record in data:
        record['user_name'] = record.pop('user')

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        temp_file = f.name

    yield temp_file

    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def temp_csv_file(sample_query_logs):
    """Create a temporary CSV file with sample data"""
    # Rename columns to match raw format
    df = sample_query_logs.copy()
    df = df.rename(columns={'user': 'user_name'})

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        temp_file = f.name

    yield temp_file

    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir

    # Cleanup
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

# Made with Bob
