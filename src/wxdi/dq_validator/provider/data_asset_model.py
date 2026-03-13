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
Pydantic models for Data Asset API responses
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from .constraint_model import DataQualityConstraint


class AssetMetadata(BaseModel):
    """Metadata for data asset"""

    project_id: str
    name: str
    catalog_id: str
    tags: Optional[List[str]] = []
    asset_type: Optional[str] = None
    created: Optional[int] = None
    created_at: Optional[str] = None
    owner_id: Optional[str] = None
    size: Optional[int] = None
    version: Optional[int] = None
    asset_state: Optional[str] = None
    asset_attributes: Optional[List[str]] = []
    asset_id: Optional[str] = None
    asset_category: Optional[str] = None
    creator_id: Optional[str] = None


class ColumnType(BaseModel):
    """Column type information"""

    type: str
    scale: Optional[int] = None
    length: Optional[int] = None
    signed: Optional[bool] = None
    nullable: Optional[bool] = True
    native_type: Optional[str] = None


class Column(BaseModel):
    """Column definition in data asset"""

    name: str
    type: ColumnType
    columnProperties: Optional[Dict[str, Any]] = Field(default_factory=dict)


class Property(BaseModel):
    """Property key-value pair"""

    name: str
    value: str


class DataAssetInfo(BaseModel):
    """Data asset information"""

    columns: List[Column]
    dataset: bool
    mime_type: Optional[str] = None
    properties: Optional[List[Property]] = []


class DataClass(BaseModel):
    """Data class information"""

    id: str
    name: Optional[str] = None
    setByUser: Optional[bool] = False
    confidence: Optional[float] = None


class DataClassInfo(BaseModel):
    """Data class information for a column"""

    suggested_classes: Optional[List[DataClass]] = None
    selected_data_class: Optional[DataClass] = None


class InferredType(BaseModel):
    """Inferred type information"""

    type: str
    scale: Optional[int] = None
    length: Optional[int] = None
    precision: Optional[int] = None
    display_name: Optional[str] = None


class ColumnInfo(BaseModel):
    """Column information including checks and data class"""

    data_class: Optional[DataClassInfo] = None
    column_checks: Optional[List[DataQualityConstraint]] = []
    inferred_type: Optional[InferredType] = None
    rejected_checks: Optional[List[Any]] = []
    suggested_checks: Optional[List[Any]] = []


class RecordInfo(BaseModel):
    """Record information"""

    computed: bool
    approximated: bool
    number_of_records: int


class ExtendedMetadata(BaseModel):
    """Extended metadata item"""

    name: str
    value: str


class AssetDataQualityConstraint(BaseModel):
    """Asset-level data quality constraints"""

    asset_checks: Optional[List[Any]] = []
    rejected_checks: Optional[List[Any]] = []
    suggested_checks: Optional[List[Any]] = []


class DataAssetEntity(BaseModel):
    """Entity containing all data asset information"""

    data_asset: DataAssetInfo
    column_info: Optional[Dict[str, ColumnInfo]] = None
    asset_data_quality_constraint: Optional[AssetDataQualityConstraint] = None


class DataAsset(BaseModel):
    """Root model for data asset response"""

    metadata: AssetMetadata
    entity: DataAssetEntity

    @classmethod
    def from_dict(cls, data: Dict) -> "DataAsset":
        """Create DataAsset instance from dictionary"""
        return cls(**data)


# Made with Bob
