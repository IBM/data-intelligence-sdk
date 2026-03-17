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

from wxdi.common.auth.auth_config import AuthConfig
from wxdi.common.auth.auth_provider import AuthProvider

class ProviderConfig:
    def __init__(self, url: str, auth_token: Optional[str] = None, project_id: Optional[str] = None, catalog_id: Optional[str] = None,
            auth_config: Optional[AuthConfig] = None):
        self.url = url
        self._auth_token = auth_token
        self.project_id = project_id
        self.catalog_id = catalog_id
        if auth_config:
            self.auth_provider = AuthProvider(auth_config)
        else:
            self.auth_provider = None

    @property
    def auth_token(self) -> str:
        try:
            return self.get_auth_token()
        except ValueError:
            return ""

    def get_auth_token(self) -> str:
        if self.auth_provider:
            return self.auth_provider.get_token()
        if self._auth_token:
            return self._auth_token
        raise ValueError("No authentication token provided")