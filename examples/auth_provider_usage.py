"""
   Copyright 2026 IBM Corporation

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
"""
AuthProvider Usage Examples

This file demonstrates how to use the AuthProvider class with different
environment configurations (IBM_CLOUD, AWS_CLOUD, GOV_CLOUD, ON_PREM).

AuthConfig Optional Parameters:
================================
- url: Optional[str] = None
    The authentication or API endpoint URL
    Not required for production environments - default production URLs are used automatically
    Provide url only for non-production environments
    Trailing slashes are automatically stripped
    Default production URLs:
        IBM_CLOUD: https://iam.cloud.ibm.com/identity/token
        AWS_CLOUD: https://account-iam.platform.saas.ibm.com
        GOV_CLOUD: https://dai.ibmforusgov.com/api/rest/mcsp/apikeys/token
        ON_PREM:   Must always be provided (no default)

- api_key: Optional[str] = None
    API key for authentication
    Required for: IBM_CLOUD, AWS_CLOUD, GOV_CLOUD
    Optional for: ON_PREM (can use password instead)

- username: Optional[str] = None
    Username for authentication
    Required for: ON_PREM
    Not used for: IBM_CLOUD, AWS_CLOUD, GOV_CLOUD

- password: Optional[str] = None
    Password for authentication
    Optional for: ON_PREM (alternative to api_key)
    Not used for: IBM_CLOUD, AWS_CLOUD, GOV_CLOUD

- account_id: Optional[str] = None
    Account ID for AWS environment
    Required for: AWS_CLOUD
    Not used for: IBM_CLOUD, GOV_CLOUD, ON_PREM

- disable_ssl_verification: bool = True
    Whether to disable SSL certificate verification (default: True)
    Set to False to enable SSL verification for production environments
    Applies to all authenticators
"""

from ibm_cloud_sdk_core.authenticators import authenticator
from wxdi.common.auth import AuthConfig, EnvironmentType, AuthProvider


def example_ibm_cloud():
    """
    Example: IBM Cloud authentication using IAMAuthenticator
    
    Requirements:
    - api_key: Your IBM Cloud API key
    - url: Not required for production. Provide only for non-production environments.
    """
    print("=" * 60)
    print("IBM CLOUD AUTHENTICATION")
    print("=" * 60)
    
    # Create environment configuration
    # Required: environment_type, api_key
    # url: Not required for production
    #      Provide url only for non-production environments (e.g., staging, preprod)
    # disable_ssl_verification (default: True)
    config = AuthConfig(
        environment_type=EnvironmentType.IBM_CLOUD,
        api_key='your-ibm-cloud-api-key-here',
        # url='https://host_name',  # This is not required for production env. For non-default custom add this property.
        # disable_ssl_verification=True  # Optional, default is True
    )
    
    print(f"Environment Type: {config.environment_type.value}")
    print(f"URL: {config.url}")
    
    # Create auth provider
    auth_provider = AuthProvider(config)
    print(f"Authenticator: {type(auth_provider.authenticator).__name__}")
    
    # Get token (uncomment when you have valid credentials)
    # try:
    #     token = auth_provider.get_token()
    #     print(f"Token obtained successfully: {token[:20]}...")
    # except Exception as e:
    #     print(f"Error getting token: {e}")
    
    print()


def example_aws_cloud():
    """
    Example: AWS Cloud authentication using MCSPV2Authenticator
    
    Requirements:
    - api_key: Your AWS API key
    - account_id: Your AWS account ID
    - url: Not required for production. Provide only for non-production environments.
    """
    print("=" * 60)
    print("AWS CLOUD AUTHENTICATION")
    print("=" * 60)
    
    # Create environment configuration
    # Required: environment_type, api_key, account_id
    # url: Not required for production
    #      Provide url only for non-production environments
    # disable_ssl_verification (default: True)
    config = AuthConfig(
        environment_type=EnvironmentType.AWS_CLOUD,
        api_key='your-aws-api-key-here',
        account_id='your-aws-account-id',
        # url='https://host_name',  # This is not required for production env. For non-default custom add this property.
        # disable_ssl_verification=True  # Optional, default is True
    )
    
    print(f"Environment Type: {config.environment_type.value}")
    print(f"URL: {config.url}")
    print(f"Account ID: {config.account_id}")
    
    # Create auth provider
    auth_provider = AuthProvider(config)
    print(f"Authenticator: {type(auth_provider.authenticator).__name__}")
    
    # Get token (uncomment when you have valid credentials)
    # try:
    #     token = auth_provider.get_token()
    #     print(f"Token obtained successfully: {token[:20]}...")
    # except Exception as e:
    #     print(f"Error getting token: {e}")
    
    print()


def example_gov_cloud():
    """
    Example: Government Cloud authentication using GovCloudAuthenticator
    
    Requirements:
    - api_key: Your Government Cloud API key
    - url: Not required for production. Provide only for non-production environments.
    """
    print("=" * 60)
    print("GOVERNMENT CLOUD AUTHENTICATION")
    print("=" * 60)
    
    # Create environment configuration
    # Required: environment_type, api_key
    # url: Not required for production environments
    #      Provide url only for non-production environments (e.g., preprod)
    # disable_ssl_verification (default: True)
    config = AuthConfig(
        environment_type=EnvironmentType.GOV_CLOUD,
        api_key='your-gov-cloud-api-key-here',
        # url='https://host_name',  # This is not required for production env. For non-default custom add this property.
        # disable_ssl_verification=True  # Optional, default is True
    )
    
    print(f"Environment Type: {config.environment_type.value}")
    print(f"URL: {config.url}")
    
    # Create auth provider
    auth_provider = AuthProvider(config)
    print(f"Authenticator: {type(auth_provider.authenticator).__name__}")
    
    # Get token (uncomment when you have valid credentials)
    # try:
    #     token = auth_provider.get_token()
    #     print(f"Token obtained successfully: {token[:20]}...")
    # except Exception as e:
    #     print(f"Error getting token: {e}")
    
    print()


def example_on_prem_with_apikey():
    """
    Example: On-Premises authentication using CloudPakForDataAuthenticator with API key
    
    Requirements:
    - url: Your on-premises CP4D URL (required)
    - username: Your username
    - api_key: Your API key
    
    Note: When using api_key, username is required but password should NOT be provided.
    """
    print("=" * 60)
    print("ON-PREMISES AUTHENTICATION (with API Key)")
    print("=" * 60)
    
    # Create environment configuration
    # Required: environment_type, url, username, api_key (or password)
    # Optional: disable_ssl_verification (default: True)
    # Note: URL path '/icp4d-api/v1/authorize' is automatically appended if not present
    config = AuthConfig(
        environment_type=EnvironmentType.ON_PREM,
        url='https://your-cp4d-instance.example.com',  # Path will be auto-appended
        username='your-username',
        api_key='your-cp4d-api-key-here'
        # disable_ssl_verification=True  # Optional, default is True
    )
    
    print(f"Environment Type: {config.environment_type.value}")
    print(f"URL: {config.url}")
    print(f"Username: {config.username}")
    print(f"Authentication Method: API Key")
    
    # Create auth provider
    auth_provider = AuthProvider(config)
    print(f"Authenticator: {type(auth_provider.authenticator).__name__}")
    
    # Get token (uncomment when you have valid credentials)
    # try:
    #     token = auth_provider.get_token()
    #     print(f"Token obtained successfully: {token[:20]}...")
    # except Exception as e:
    #     print(f"Error getting token: {e}")
    
    print()


def example_on_prem_with_password():
    """
    Example: On-Premises authentication using CloudPakForDataAuthenticator with password
    
    Requirements:
    - url: Your on-premises CP4D URL (required)
    - username: Your username
    - password: Your password
    
    Note: When using password, api_key should NOT be provided.
    """
    print("=" * 60)
    print("ON-PREMISES AUTHENTICATION (with Username/Password)")
    print("=" * 60)
    
    # Create environment configuration
    # Required: environment_type, url, username, password (or api_key)
    # Optional: disable_ssl_verification (default: True)
    config = AuthConfig(
        environment_type=EnvironmentType.ON_PREM,
        url='https://your-cp4d-instance.example.com',  # Path will be auto-appended
        username='your-username',
        password='your-password',
        # disable_ssl_verification=True  # Optional, default is True
    )
    
    print(f"Environment Type: {config.environment_type.value}")
    print(f"URL: {config.url}")
    print(f"Username: {config.username}")
    print(f"Authentication Method: Username/Password")
    
    # Create auth provider
    auth_provider = AuthProvider(config)
    print(f"Authenticator: {type(auth_provider.authenticator).__name__}")
    
    # Get token (uncomment when you have valid credentials)
    # try:
    #     token = auth_provider.get_token()
    #     print(f"Token obtained successfully: {token[:20]}...")
    # except Exception as e:
    #     print(f"Error getting token: {e}")
    
    print()


def example_custom_url():
    """
    Example: Using custom URL for non-production environments
    
    Provide url only for non-production environments (staging, preprod, dev).
    For production, omit url and the default production URL will be used automatically.
    """
    print("=" * 60)
    print("NON-production CUSTOM URL EXAMPLE")
    print("=" * 60)
    
    # Provide url only for non-production environments
    # For production, omit url - the default production URL is used automatically
    # Trailing slashes are automatically stripped
    config = AuthConfig(
        environment_type=EnvironmentType.IBM_CLOUD,
        url='https://your-custom-host.example.com/identity/token',  # Non-production URL
        api_key='your-api-key-here',
        # disable_ssl_verification=True  # Optional, default is True
    )
    
    print(f"Environment Type: {config.environment_type.value}")
    print(f"Custom URL: {config.url}")
    
    # Create auth provider
    auth_provider = AuthProvider(config)
    print(f"Authenticator: {type(auth_provider.authenticator).__name__}")
    
    # Get token (uncomment when you have valid credentials)
    # try:
    #     token = auth_provider.get_token()
    #     print(f"Token obtained successfully: {token[:20]}...")
    # except Exception as e:
    #     print(f"Error getting token: {e}")

    print()


def example_error_handling():
    """
    Example: Error handling and validation
    
    The AuthConfig validates required fields based on environment type.
    """
    print("=" * 60)
    print("ERROR HANDLING EXAMPLES")
    print("=" * 60)
    
    # Example 1: Missing API key for IBM_CLOUD
    print("\n1. Missing API key for IBM_CLOUD:")
    try:
        config = AuthConfig(
            environment_type=EnvironmentType.IBM_CLOUD
            # Missing api_key
        )
    except ValueError as e:
        print(f"   ✓ Caught error: {e}")
    
    # Example 2: Missing account_id for AWS_CLOUD
    print("\n2. Missing account_id for AWS_CLOUD:")
    try:
        config = AuthConfig(
            environment_type=EnvironmentType.AWS_CLOUD,
            api_key='test-key'
            # Missing account_id
        )
    except ValueError as e:
        print(f"   ✓ Caught error: {e}")
    
    # Example 3: Missing username for ON_PREM
    print("\n3. Missing username for ON_PREM:")
    try:
        config = AuthConfig(
            environment_type=EnvironmentType.ON_PREM,
            url='https://example.com',
            api_key='test-key'
            # Missing username
        )
    except ValueError as e:
        print(f"   ✓ Caught error: {e}")
    
    # Example 4: Missing URL for ON_PREM
    print("\n4. Missing URL for ON_PREM:")
    try:
        config = AuthConfig(
            environment_type=EnvironmentType.ON_PREM,
            username='admin',
            password='secret'
            # Missing url
        )
    except ValueError as e:
        print(f"   ✓ Caught error: {e}")
    
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AUTHPROVIDER USAGE EXAMPLES")
    print("=" * 60 + "\n")
    
    # Run all examples
    example_ibm_cloud()
    example_aws_cloud()
    example_gov_cloud()
    example_on_prem_with_apikey()
    example_on_prem_with_password()
    example_custom_url()
    example_error_handling()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)