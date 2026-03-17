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
Metadata classes for defining data asset structure.
"""

from enum import Enum
from typing import List, Dict, Any, Optional


class DataType(Enum):
    """Supported data types for columns"""
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    DECIMAL = "decimal"


class ColumnMetadata:
    """Metadata for a single column"""
    
    def __init__(
        self,
        name: str,
        data_type: DataType,
        length: Optional[int] = None,
        scale: Optional[int] = None,
        precision: Optional[int] = None,
        nullable: bool = True
    ):
        """
        Initialize column metadata
        
        Args:
            name: Column name
            data_type: Data type from DataType enum
            length: Maximum length (for strings)
            scale: Number of digits after decimal (for decimals)
            precision: Total number of digits (for decimals)
            nullable: Whether column can be null
        """
        self.name = name
        self.data_type = data_type
        self.length = length
        self.scale = scale
        self.precision = precision
        self.nullable = nullable
    
    def __repr__(self) -> str:
        return f"ColumnMetadata(name='{self.name}', data_type={self.data_type.value})"


class AssetMetadata:
    """Metadata for a data asset (table)"""
    
    def __init__(self, table_name: str, columns: List[ColumnMetadata]):
        """
        Initialize asset metadata
        
        Args:
            table_name: Name of the table/asset
            columns: List of column metadata in order
        
        Raises:
            ValueError: If columns list is empty or contains duplicate names
        """
        if not columns:
            raise ValueError("columns list cannot be empty")
        
        self.table_name = table_name
        self.columns = columns
        
        # Build column index map for O(1) lookup
        self._column_index_map: Dict[str, int] = {}
        for idx, col in enumerate(columns):
            if col.name in self._column_index_map:
                raise ValueError(f"Duplicate column name: '{col.name}'")
            self._column_index_map[col.name] = idx
    
    def get_column_index(self, column_name: str) -> int:
        """
        Get array index for a column name
        
        Args:
            column_name: Name of the column
        
        Returns:
            Index of the column in the record array
        
        Raises:
            ValueError: If column name not found
        """
        if column_name not in self._column_index_map:
            raise ValueError(f"Column '{column_name}' not found in metadata")
        return self._column_index_map[column_name]
    
    def get_column(self, column_name: str) -> ColumnMetadata:
        """
        Get column metadata by name
        
        Args:
            column_name: Name of the column
        
        Returns:
            ColumnMetadata object
        
        Raises:
            ValueError: If column name not found
        """
        idx = self.get_column_index(column_name)
        return self.columns[idx]
    
    def get_value(self, record: List[Any], column_name: str) -> Any:
        """
        Extract value from record array by column name
        
        Args:
            record: The record array
            column_name: Name of the column
        
        Returns:
            Value at the column's position
        
        Raises:
            ValueError: If column not found or record too short
        """
        idx = self.get_column_index(column_name)
        if idx >= len(record):
            raise ValueError(
                f"Record has {len(record)} values, but column '{column_name}' "
                f"is at index {idx}"
            )
        return record[idx]
    
    def __repr__(self) -> str:
        return f"AssetMetadata(table_name='{self.table_name}', columns={len(self.columns)})"

