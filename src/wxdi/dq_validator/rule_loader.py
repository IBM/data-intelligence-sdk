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

from typing import List, Optional
from wxdi.dq_validator.metadata import AssetMetadata, ColumnMetadata, DataType
from wxdi.dq_validator.provider.cams import CamsProvider
from wxdi.dq_validator.provider.data_asset_model import DataAsset, DataAssetEntity
from wxdi.dq_validator.provider.response_model import GlossaryTerm
from wxdi.dq_validator.rule import ValidationRule
from .validator import Validator
from .provider.glossary import GlossaryProvider
from .provider.config import ProviderConfig

# some definitions from connectivity parameters
CAMS_TYPE_TO_DATA_TYPE = {
    "char": DataType.STRING,
    "varchar": DataType.STRING,
    "sqlxml": DataType.STRING,
    "string": DataType.STRING,
    "clob": DataType.STRING,
    "longnvarchar": DataType.STRING,
    "wlongvarchar": DataType.STRING,
    "longvarchar": DataType.STRING,
    "nchar": DataType.STRING,
    "wchar": DataType.STRING,
    "nvarchar": DataType.STRING,
    "wvarchar": DataType.STRING,
    "nclob": DataType.STRING,
    "dbclob": DataType.STRING,
    "bigint": DataType.INTEGER,
    "int8": DataType.INTEGER,
    "int16": DataType.INTEGER,
    "int32": DataType.INTEGER,
    "int64": DataType.INTEGER,
    "integer": DataType.INTEGER,
    "smallint": DataType.INTEGER,
    "tinyint": DataType.INTEGER,
    "float": DataType.FLOAT,
    "double": DataType.FLOAT,
    "date": DataType.DATE,
    "decimal": DataType.DECIMAL,
    "numeric": DataType.DECIMAL,
    "real": DataType.DECIMAL,
    "time": DataType.DATETIME,
    "time_with_timezone": DataType.DATETIME,
    "timestamp": DataType.DATETIME,
    "timestamp_with_timezone": DataType.DATETIME,
}


class RuleLoader(object):
    def __init__(self, base_url: str, auth_token: str):
        """
        Docstring for __init__

        :param self:
        :param base_url: the base URL to make the calls
        :type base_url: str
        :param auth_token: the auth token to be used to make calls
        :type auth_token: str
        """
        self.base_url = base_url
        self.auth_token = auth_token

    def load_from_glossary(
        self, term_id: str, column_name: str, metadata: AssetMetadata
    ) -> Validator:
        """
        Load validation rules from a glossary term

        :param term_id: the term id containing the data quality checks
        :type term_id: str
        :param column_name: the column name to apply the data quality checks to
        :type column_name: str
        :param metadata: the asset metadata
        :type metadata: AssetMetadata
        :return: the Validator with the data quality checks from the glossary term
        :rtype: Validator
        """
        latest_version_details = self.get_glossary_term_with_dq_checks(term_id)

        return self.load_from_glossary_term(
            latest_version_details, column_name, metadata
        )

    def get_glossary_term_with_dq_checks(
        self, term_id: str, version_id: Optional[str] = None
    ) -> GlossaryTerm:
        """
        Load glossary term including DQ checks; if no version specified, get the latest version

        :param term_id: the term id containing the data quality checks
        :type term_id: str
        :param term_id: the version id of the glossary term containing the data quality checks
        :type version_id: Optional[str]
        :return: the glossary term with the data quality checks
        :rtype: GlossaryTerm
        """
        provider = GlossaryProvider(ProviderConfig(self.base_url, self.auth_token))
        if version_id is None:
            latest_version = provider.get_published_artifact_by_id(term_id)
            version_id = latest_version.metadata.version_id
        if not version_id:
            raise ValueError("No version_id found in glossary term")
        extended_attribute_groups = {
            "included_extended_attribute_groups": "dq_constraints"
        }
        latest_version_details = provider.get_term_by_version_id(
            term_id, version_id, extended_attribute_groups
        )
        return latest_version_details

    def load_from_glossary_term(
        self, term: GlossaryTerm, column_name: str, metadata: AssetMetadata
    ):
        """
        Load validation rules from a glossary term

        :param term: the term containing the data quality checks
        :type term: GlossaryTerm
        :param column_name: the column name to apply the data quality checks to
        :type column_name: str
        :param metadata: the asset metadata
        :type metadata: AssetMetadata
        :return: the Validator with the data quality checks from the glossary term
        :rtype: Validator
        """

        # Get DQ constraints if they exist
        dq_constraints = []
        if term.entity.extended_attribute_groups:
            dq_constraints = term.entity.extended_attribute_groups.dq_constraints

        dq_checks = [
            c
            for c in [constraint.to_check() for constraint in dq_constraints]
            if c is not None
        ]

        validator = Validator(metadata)
        if dq_checks:
            rule = ValidationRule(column_name=column_name)
            for check in dq_checks:
                rule.add_check(check)
            validator.add_rule(rule)
        return validator

    def load_from_cams(
        self, asset_id: str, project_id: str, metadata: Optional[AssetMetadata] = None
    ) -> Validator:
        """
        Docstring for load_from_cams

        :param self:
        :param asset_id: the data asset id containing the data rules
        :type asset_id: str
        :param project_id: the project id of data asset
        :type project_id: str
        :return: the Validator with the data quality checks from the glossary term
        :rtype: Validator
        """
        provider = CamsProvider(
            ProviderConfig(self.base_url, self.auth_token, project_id=project_id)
        )
        data_asset = provider.get_asset_by_id(asset_id)
        return self.load_from_data_asset(data_asset, metadata)

    def load_from_data_asset(
        self, data_asset: DataAsset, metadata: Optional[AssetMetadata] = None
    ) -> Validator:
        if metadata is None:
            metadata = AssetMetadata(
                data_asset.metadata.name, RuleLoader._extract_columns(data_asset)
            )
        column_info = data_asset.entity.column_info
        validator = Validator(metadata)
        for column_metadata in metadata.columns:
            column_name = column_metadata.name
            if column_info and column_name in column_info:
                info = column_info[column_name]
                col_checks = info.column_checks
                if col_checks:
                    rule = ValidationRule(column_name)
                    checks = [c.to_check() for c in col_checks]
                    valid_checks = [c for c in checks if c is not None]
                    for check in valid_checks:
                        rule.add_check(check)
                    if rule.checks:
                        validator.add_rule(rule)
        return validator

    @staticmethod
    def _extract_columns(data_asset: DataAsset) -> List[ColumnMetadata]:
        column_list = []
        column_info = data_asset.entity.column_info
        for column in data_asset.entity.data_asset.columns:
            inferred = None
            if column_info and column.name in column_info:
                inferred = column_info[column.name].inferred_type
            
            if inferred:
                cmeta = ColumnMetadata(
                    column.name,
                    RuleLoader._convert_to_data_type(inferred.type),
                    inferred.length,
                    inferred.scale,
                    inferred.precision,
                    column.type.nullable if column.type.nullable is not None else True,
                )
            else:
                cmeta = ColumnMetadata(
                    column.name,
                    RuleLoader._convert_to_data_type(column.type.type),
                    column.type.length,
                    column.type.scale,
                    None,
                    column.type.nullable if column.type.nullable is not None else True,
                )
            column_list.append(cmeta)
        return column_list

    @staticmethod
    def _convert_to_data_type(cams_type: str) -> DataType:
        cams_type = cams_type.lower()
        return (
            CAMS_TYPE_TO_DATA_TYPE[cams_type]
            if cams_type in CAMS_TYPE_TO_DATA_TYPE
            else DataType[cams_type.upper()]
        )
