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

from typing import Optional, TypeVar
from urllib.parse import urlencode

_T = TypeVar("_T")

def get_request_headers(
    auth_token: str, content_type: str = "application/json"
) -> dict:
    headers = {}
    if auth_token:
        headers["Authorization"] = auth_token
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def get_url_with_query_params(url: str, params: Optional[dict]) -> str:
    if params:
        query = urlencode(params)
        return f"{url}?{query}"
    return url

def get_or_default(value: Optional[_T], default: _T) -> _T:
    return value if value is not None else default
