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

from .response_model import GlossaryTerm
from .config import ProviderConfig
from ..utils import get_request_headers, get_url_with_query_params
import json


class GlossaryProvider (BaseProvider):
    def __init__(self, config: ProviderConfig):
        super().__init__(config)

    def get_published_artifact_by_id(
        self, artifact_id: str, options: Optional[dict] = None
    ) -> GlossaryTerm:
        url = f"{self.config.url}/v3/governance_artifact_types/glossary_term/{artifact_id}"
        url = get_url_with_query_params(url, options)
        headers = get_request_headers(self.config.auth_token)
        response = self.session.get(url, headers=headers, verify=False)
        if not response.ok:
            raise ValueError(f"Cannot get artifact {artifact_id}")
        return GlossaryTerm.from_json(response.text)

    def get_term_by_version_id(
        self, artifact_id: str, version_id: str, options: Optional[dict] = None
    ) -> GlossaryTerm:
        url = f"{self.config.url}/v3/glossary_terms/{artifact_id}/versions/{version_id}"
        url = get_url_with_query_params(url, options)
        headers = get_request_headers(self.config.auth_token)
        response = self.session.get(url, headers=headers, verify=False)
        if not response.ok:
            raise ValueError(
                f"Cannot get artifact {artifact_id} with version {version_id}"
            )
        return GlossaryTerm.from_json(response.text)
