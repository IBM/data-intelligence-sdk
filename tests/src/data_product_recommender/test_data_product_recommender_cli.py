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
Unit tests for Data Product Recommender CLI
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd

from wxdi.data_product_recommender.cli import main
from wxdi.data_product_recommender.platforms import SnowflakeQueryParser


class TestCLI:
    """Tests for CLI functionality"""

    def test_cli_with_csv_snowflake(self):
        """Test CLI with CSV file and Snowflake platform"""
        # Create temporary CSV file
        test_data = pd.DataFrame({
            'query_text': ['SELECT * FROM SALES.CUSTOMERS', 'SELECT * FROM SALES.ORDERS'],
            'user_name': ['user1', 'user2'],
            'start_time': ['2025-01-01', '2025-01-02']
        })

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            csv_file = f.name

        with tempfile.TemporaryDirectory() as output_dir:
            try:
                test_args = [
                    'cli.py',
                    '--platform', 'snowflake',
                    '--input-file', csv_file,
                    '--output', output_dir,
                    '--num-recommendations', '5'
                ]

                with patch('sys.argv', test_args):
                    main()

                # Verify output file was created
                output_files = list(Path(output_dir).glob('recommendations_*.md'))
                assert len(output_files) == 1

            finally:
                os.unlink(csv_file)

    def test_cli_with_json_databricks(self):
        """Test CLI with JSON file and Databricks platform"""
        # Create temporary JSON file
        test_data = [
            {
                'statement_text': 'SELECT * FROM CLINICAL.PATIENTS',
                'executed_by': 'user1',
                'start_time': '2025-01-01'
            },
            {
                'statement_text': 'SELECT * FROM CLINICAL.VISITS',
                'executed_by': 'user2',
                'start_time': '2025-01-02'
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            json_file = f.name

        with tempfile.TemporaryDirectory() as output_dir:
            try:
                test_args = [
                    'cli.py',
                    '--platform', 'databricks',
                    '--input-file', json_file,
                    '--output', output_dir,
                    '--output-format', 'json',
                    '--num-recommendations', '10'
                ]

                with patch('sys.argv', test_args):
                    main()

                # Verify JSON output file was created
                output_files = list(Path(output_dir).glob('recommendations_*.json'))
                assert len(output_files) == 1

                # Verify JSON is valid
                with open(output_files[0], 'r') as f:
                    recommendations = json.load(f)
                    # JSON export uses 'recommendations' key, not 'individual_tables'
                    assert 'recommendations' in recommendations
                    assert 'metadata' in recommendations

            finally:
                os.unlink(json_file)

    def test_cli_with_bigquery(self):
        """Test CLI with BigQuery platform"""
        # Create temporary CSV file
        test_data = pd.DataFrame({
            'query': ['SELECT * FROM PRODUCT.CATALOG', 'SELECT * FROM PRODUCT.INVENTORY'],
            'user_email': ['user1@example.com', 'user2@example.com'],
            'start_time': ['2025-01-01', '2025-01-02']
        })

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            csv_file = f.name

        with tempfile.TemporaryDirectory() as output_dir:
            try:
                test_args = [
                    'cli.py',
                    '--platform', 'bigquery',
                    '--input-file', csv_file,
                    '--output', output_dir
                ]

                with patch('sys.argv', test_args):
                    main()

                # Verify output was created
                output_files = list(Path(output_dir).glob('recommendations_*.md'))
                assert len(output_files) == 1

            finally:
                os.unlink(csv_file)

    def test_cli_with_watsonxdata(self):
        """Test CLI with watsonx.data platform"""
        # Create temporary CSV file
        test_data = pd.DataFrame({
            'query': ['SELECT * FROM NETWORK.SUBSCRIBERS', 'SELECT * FROM NETWORK.USAGE'],
            'user': ['user1', 'user2'],
            'created': ['2025-01-01', '2025-01-02']
        })

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            csv_file = f.name

        with tempfile.TemporaryDirectory() as output_dir:
            try:
                test_args = [
                    'cli.py',
                    '--platform', 'watsonxdata',
                    '--input-file', csv_file,
                    '--output', output_dir
                ]

                with patch('sys.argv', test_args):
                    main()

                # Verify output was created
                output_files = list(Path(output_dir).glob('recommendations_*.md'))
                assert len(output_files) == 1

            finally:
                os.unlink(csv_file)

    def test_cli_with_min_score_threshold(self):
        """Test CLI with minimum score threshold"""
        # Create temporary CSV file with multiple queries
        test_data = pd.DataFrame({
            'query_text': [
                'SELECT * FROM SALES.CUSTOMERS',
                'SELECT * FROM SALES.CUSTOMERS',
                'SELECT * FROM SALES.CUSTOMERS',
                'SELECT * FROM SALES.ORDERS'
            ],
            'user_name': ['user1', 'user2', 'user3', 'user1'],
            'start_time': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04']
        })

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            csv_file = f.name

        with tempfile.TemporaryDirectory() as output_dir:
            try:
                test_args = [
                    'cli.py',
                    '--platform', 'snowflake',
                    '--input-file', csv_file,
                    '--output', output_dir,
                    '--min-score', '50.0'
                ]

                with patch('sys.argv', test_args):
                    main()

                # Verify output was created
                output_files = list(Path(output_dir).glob('recommendations_*.md'))
                assert len(output_files) == 1

            finally:
                os.unlink(csv_file)

    def test_cli_invalid_file_type(self):
        """Test CLI with invalid file type"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("invalid file")
            txt_file = f.name

        try:
            test_args = [
                'cli.py',
                '--platform', 'snowflake',
                '--input-file', txt_file,
                '--output', 'output'
            ]

            with patch('sys.argv', test_args):
                with pytest.raises(ValueError, match="Invalid --input-file type"):
                    main()
        finally:
            os.unlink(txt_file)

    def test_cli_creates_output_directory(self):
        """Test that CLI creates output directory if it doesn't exist"""
        # Create temporary CSV file
        test_data = pd.DataFrame({
            'query_text': ['SELECT * FROM SALES.CUSTOMERS'],
            'user_name': ['user1'],
            'start_time': ['2025-01-01']
        })

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            csv_file = f.name

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / 'nested' / 'output' / 'dir'

            try:
                test_args = [
                    'cli.py',
                    '--platform', 'snowflake',
                    '--input-file', csv_file,
                    '--output', str(output_dir)
                ]

                with patch('sys.argv', test_args):
                    main()

                # Verify directory was created
                assert output_dir.exists()
                assert output_dir.is_dir()

            finally:
                os.unlink(csv_file)

    def test_cli_markdown_output_format(self):
        """Test CLI with explicit markdown output format"""
        test_data = pd.DataFrame({
            'query_text': ['SELECT * FROM SALES.CUSTOMERS'],
            'user_name': ['user1'],
            'start_time': ['2025-01-01']
        })

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            csv_file = f.name

        with tempfile.TemporaryDirectory() as output_dir:
            try:
                test_args = [
                    'cli.py',
                    '--platform', 'snowflake',
                    '--input-file', csv_file,
                    '--output', output_dir,
                    '--output-format', 'markdown'
                ]

                with patch('sys.argv', test_args):
                    main()

                # Verify markdown file was created
                output_files = list(Path(output_dir).glob('recommendations_*.md'))
                assert len(output_files) == 1

            finally:
                os.unlink(csv_file)


# Made with Bob