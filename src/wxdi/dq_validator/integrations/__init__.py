# Copyright 2026 IBM Corporation
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0);
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# See the LICENSE file in the project root for license information.

"""
DataFrame Integration Module for Data Quality Validator

This module provides integration with popular DataFrame libraries:
- Pandas: For in-memory data analysis
- PySpark: For distributed big data processing

Both implementations provide consistent APIs and memory-efficient validation.
"""

# Import base classes (always available)
from .base import DataFrameValidator
from ...version import __version__

# Conditional imports for optional dependencies
try:
    from .pandas_validator import PandasValidator
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    PandasValidator = None

try:
    from .spark_validator import SparkValidator
    SPARK_AVAILABLE = True
except ImportError:
    SPARK_AVAILABLE = False
    SparkValidator = None

__all__ = [
    'DataFrameValidator',
    'PandasValidator',
    'SparkValidator',
    'PANDAS_AVAILABLE',
    'SPARK_AVAILABLE',
]
