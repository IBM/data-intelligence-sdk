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

from requests import Session
import threading

from .config import ProviderConfig


class BaseProvider:
    """Base provider class with shared functionality for all providers.
    
    This class provides common functionality like thread-local session management
    that is shared across all provider implementations.
    
    Attributes:
        config (ProviderConfig): Configuration containing URL and authentication token
    """
    
    def __init__(self, config: ProviderConfig):
        """Initialize the BaseProvider with configuration.
        
        Args:
            config (ProviderConfig): Provider configuration with URL and auth token
        """
        self.config = config
        self._local = threading.local()
    
    @property
    def session(self) -> Session:
        """Get or create a thread-local session instance.
        
        Returns:
            Session: A requests Session object unique to the current thread
        """
        if not hasattr(self._local, 'session'):
            self._local.session = Session()
        return self._local.session