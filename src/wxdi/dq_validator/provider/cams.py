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

from typing import Optional
from requests import Session

from wxdi.dq_validator.provider.base_provider import BaseProvider
from wxdi.dq_validator.provider.data_asset_model import DataAsset

from .config import ProviderConfig
from ..utils import get_request_headers, get_url_with_query_params
import json


class CamsProvider (BaseProvider):
    def __init__(self, config: ProviderConfig):
        super().__init__(config)

    def get_asset_by_id(
        self, asset_id: str, options: Optional[dict] = None
    ) -> DataAsset:
        url = f"{self.config.url}/v2/assets/{asset_id}"
        if options is None:
            options = {}
        query_options = dict(options)
        
        # Use either project_id or catalog_id
        context = ""
        context_type = ""
        if self.config.project_id:
            query_options["project_id"] = self.config.project_id
            context = self.config.project_id
            context_type = "project"
        elif self.config.catalog_id:
            query_options["catalog_id"] = self.config.catalog_id
            context = self.config.catalog_id
            context_type = "catalog"
        
        url = get_url_with_query_params(url, query_options)
        headers = get_request_headers(self.config.auth_token)
        response = self.session.get(url, headers=headers, verify=False)
        if not response.ok:
            raise ValueError(
                f"Could not find data asset {asset_id} in {context_type} {context}"
            )
        response_json = json.loads(response.text)
        return DataAsset(**response_json)
