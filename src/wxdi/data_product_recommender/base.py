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
Abstract base class for query log parsers.
"""

from abc import ABC, abstractmethod
from typing import List
import pandas as pd


class QueryLogParser(ABC):
    """Abstract base class for parsing query logs"""

    @abstractmethod
    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to standard format"""
        pass

    @abstractmethod
    def extract_tables(self, query_text: str) -> List[str]:
        """Extract table names from SQL query"""
        pass