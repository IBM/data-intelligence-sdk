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
Provider module for external integrations.

This module provides integration with external systems like IBM Cloud Pak for Data
glossary terms, CAMS (Catalog Asset Management System), data quality issues, checks, dimensions, assets, and DQ search.

Classes:
    ProviderConfig: Configuration for provider connections
    GlossaryProvider: Provider for fetching glossary terms and data quality constraints
    CamsProvider: Provider for fetching data assets
    IssuesProvider: Provider for managing data quality issues
    ChecksProvider: Provider for managing data quality checks
    DimensionsProvider: Provider for managing data quality dimensions
    DQAssetsProvider: Provider for managing data quality assets
    DQSearchProvider: Provider for searching DQ checks and assets
    GlossaryTerm: Response model for glossary term artifacts
    DataAsset: Response model for data asset artifacts
    DataQualityConstraint: Model for data quality constraints
    CheckType: Enumeration of check types

Functions:
    get_request_headers: Generate request headers with authentication
    get_url_with_query_params: Add query parameters to URLs

Example:
    >>> from dq_validator.provider import (
    ...     ProviderConfig, GlossaryProvider, IssuesProvider,
    ...     ChecksProvider, DimensionsProvider, DQAssetsProvider, DQSearchProvider
    ... )
    >>> config = ProviderConfig(
    ...     url="https://your-instance.com",
    ...     auth_token="Bearer your-token"
    ... )
    >>> provider = GlossaryProvider(config)
    >>> term = provider.get_published_artifact_by_id("term-id")
    >>>
    >>> issues_provider = IssuesProvider(config)
    >>> issues_provider.update_issue_occurrences("issue-123", 767)
    >>>
    >>> checks_provider = ChecksProvider(config)
    >>> check_id = checks_provider.create_check("check_name", "dimension-id", "asset-id/check-id", project_id="project-id")
    >>>
    >>> dimensions_provider = DimensionsProvider(config)
    >>> dimension_id = dimensions_provider.search_dimension("Completeness")
    >>>
    >>> dq_search = DQSearchProvider(config)
    >>> check = dq_search.search_dq_check("native-id", "format", "project-id")
"""

from .config import ProviderConfig
from .glossary import GlossaryProvider
from .response_model import GlossaryTerm
from .cams import CamsProvider
from .data_asset_model import DataAsset
from .issues import IssuesProvider
from .dq_search import DQSearchProvider
from .checks import ChecksProvider
from .dimensions import DimensionsProvider
from .assets import DQAssetsProvider
from .constraint_model import (
    DataQualityConstraint,
    CheckType,
    CheckConstraint,
    ConstraintMetadata,
)

__all__ = [
    'ProviderConfig',
    'GlossaryProvider',
    'GlossaryTerm',
    'CamsProvider',
    'DataAsset',
    'IssuesProvider',
    'DQSearchProvider',
    'ChecksProvider',
    'DimensionsProvider',
    'DQAssetsProvider',
    'DataQualityConstraint',
    'CheckType',
    'CheckConstraint',
    'ConstraintMetadata',
]

# Made with Bob
