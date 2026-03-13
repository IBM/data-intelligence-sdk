# Copyright 2026 IBM Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Auth Config module for authentication.

This module defines the supported cloud environment types and configuration
for authentication with comprehensive validation and type safety.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Final, Optional


class EnvironmentType(Enum):
    """
    Enumeration of supported cloud environment types.
    
    Attributes:
        IBM_CLOUD: IBM Cloud standard environment
        AWS_CLOUD: Amazon Web Services cloud environment
        GOV_CLOUD: Government cloud environment
        ON_PREM: On-premises installation
    """
    IBM_CLOUD = "ibm_cloud"
    AWS_CLOUD = "aws_cloud"
    GOV_CLOUD = "gov_cloud"
    ON_PREM = "on_prem"


# Constants for default URLs - immutable and type-safe
_DEFAULT_URLS: Final[dict[EnvironmentType, str]] = {
    EnvironmentType.IBM_CLOUD: "https://iam.cloud.ibm.com/identity/token",
    EnvironmentType.AWS_CLOUD: "https://account-iam.platform.saas.ibm.com",
    EnvironmentType.GOV_CLOUD: "https://dai.ibmforusgov.com/api/rest/mcsp/apikeys/token",
    EnvironmentType.ON_PREM: "",  # No default for on-prem, must be provided
}

# Constants for URL patterns
_ON_PREM_AUTH_PATH: Final[str] = "/icp4d-api/v1/authorize"


@dataclass
class AuthConfig:
    """
    Configuration for cloud environment authentication.
    
    This class holds the configuration details needed to authenticate
    with different cloud environments. It provides comprehensive validation
    and automatic configuration based on environment type.
    
    Attributes:
        environment_type: The type of environment (IBM_CLOUD, AWS_CLOUD, etc.)
        url: The authentication or API endpoint URL (optional, uses default if not provided)
        api_key: API key for authentication (optional)
        username: Username for authentication (optional)
        password: Password for authentication (optional)
        account_id: Account ID for AWS environment (optional, required for AWS_CLOUD)
        disable_ssl_verification: Whether to disable SSL verification (default: True)
    
    Raises:
        TypeError: If environment_type is not an EnvironmentType instance
        ValueError: If required fields are missing for the specified environment type
    """
    
    environment_type: EnvironmentType
    url: Optional[str] = None
    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    account_id: Optional[str] = None
    disable_ssl_verification: bool = True
    
    def __post_init__(self) -> None:
        """
        Validate and initialize the configuration after initialization.
        
        This method performs comprehensive validation and auto-configuration:
        - Validates environment_type is correct type
        - Normalizes URL (strips trailing slashes)
        - Sets default URLs based on environment type
        - Validates required fields for each environment type
        - Auto-configures AWS-specific parameters
        
        Raises:
            TypeError: If environment_type is not an EnvironmentType instance
            ValueError: If required fields are missing or invalid
        """
        self._validate_environment_type()
        self._normalize_url()
        self._set_default_url()
        self._configure_on_prem_url()
        self._validate_authentication()
    
    
    def _validate_environment_type(self) -> None:
        """Validate that environment_type is an EnvironmentType instance."""
        if not isinstance(self.environment_type, EnvironmentType):
            raise TypeError(
                f"environment_type must be an instance of EnvironmentType, "
                f"got {type(self.environment_type).__name__}"
            )
    
    def _normalize_url(self) -> None:
        """Strip trailing slashes from URL if provided."""
        if self.url:
            self.url = self.url.rstrip('/')
    
    def _set_default_url(self) -> None:
        """
        Set default URL if not provided based on environment type.
        
        Uses predefined default URLs for each environment type.
        
        Raises:
            ValueError: If URL is required but not provided (ON_PREM case)
        """
        if self.url:
            return
        
        if self.environment_type == EnvironmentType.ON_PREM:
            raise ValueError("URL must be specified for ON_PREM environment type")
        
        self.url = _DEFAULT_URLS.get(self.environment_type, "")
        
        if not self.url:
            raise ValueError(
                f"URL must be specified for {self.environment_type.value} environment type"
            )
    
    def _configure_on_prem_url(self) -> None:
        """Append authentication path to ON_PREM URL if not already present."""
        if self.environment_type == EnvironmentType.ON_PREM and self.url:
            if _ON_PREM_AUTH_PATH not in self.url:
                self.url += _ON_PREM_AUTH_PATH
    
    def _validate_authentication(self) -> None:
        """
        Validate authentication credentials based on environment type.
        
        Each environment type has specific requirements:
        - ON_PREM: username + (api_key OR password)
        - AWS_CLOUD: api_key + account_id
        - Others: api_key
        
        Raises:
            ValueError: If required authentication fields are missing
        """
        if self.environment_type == EnvironmentType.ON_PREM:
            self._validate_on_prem_auth()
        elif self.environment_type == EnvironmentType.AWS_CLOUD:
            self._validate_aws_auth()
        else:
            self._validate_api_key_auth()
    
    def _validate_on_prem_auth(self) -> None:
        """Validate ON_PREM authentication requirements."""
        if not self.username:
            raise ValueError("Username must be provided for ON_PREM environment type")
        
        if not self.api_key and not self.password:
            raise ValueError(
                "Either api_key or password must be provided for ON_PREM environment type"
            )
    
    def _validate_aws_auth(self) -> None:
        """Validate AWS_CLOUD authentication requirements."""
        if not self.api_key:
            raise ValueError("API key must be provided for AWS_CLOUD environment type")
        
        if not self.account_id:
            raise ValueError("Account ID must be provided for AWS_CLOUD environment type")
    
    def _validate_api_key_auth(self) -> None:
        """Validate API key authentication for IBM_CLOUD and GOV_CLOUD."""
        if not self.api_key:
            raise ValueError(
                f"API key must be provided for {self.environment_type.value} environment type"
            )