..
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

.. _authentication:

Authentication
==============

The ``IBM watsonx.data intelligence SDK`` provides a unified authentication framework that supports multiple cloud environments. All SDK modules use the same authentication infrastructure, ensuring consistent behavior across different components.

Overview
--------

The authentication system consists of two main components:

* **AuthConfig**: Type-safe configuration for authentication credentials
* **AuthProvider**: Factory for creating environment-specific authenticators

Supported Environments
----------------------

The SDK supports four environment types:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Environment
     - Authenticator
     - Use Case
   * - IBM_CLOUD
     - IAMAuthenticator
     - IBM Cloud standard deployments
   * - AWS_CLOUD
     - MCSPV2Authenticator
     - AWS-hosted IBM services
   * - GOV_CLOUD
     - GovCloudAuthenticator
     - Government cloud deployments
   * - ON_PREM
     - CloudPakForDataAuthenticator
     - On-premises installations

Quick Start
-----------

Basic authentication example:

.. code-block:: python

    from wxdi.common.auth import AuthConfig, AuthProvider, EnvironmentType

    # Create configuration
    config = AuthConfig(
        environment_type=EnvironmentType.IBM_CLOUD,
        api_key="your-api-key"
    )

    # Create provider and get token
    provider = AuthProvider(config)
    token = provider.get_token()

IBM Cloud Authentication
------------------------

For IBM Cloud deployments, use IAM authentication with an API key.

Configuration
~~~~~~~~~~~~~

.. code-block:: python

    from wxdi.common.auth import AuthConfig, AuthProvider, EnvironmentType

    config = AuthConfig(
        environment_type=EnvironmentType.IBM_CLOUD,
        api_key="your-ibm-cloud-api-key"
    )

    provider = AuthProvider(config)
    token = provider.get_token()

**Required Parameters:**

* ``environment_type``: Must be ``EnvironmentType.IBM_CLOUD``
* ``api_key``: Your IBM Cloud API key

**Optional Parameters:**

* ``url``: Custom authentication URL (defaults to ``https://iam.cloud.ibm.com/identity/token``)
* ``disable_ssl_verification``: SSL verification control (default: ``True``)

Obtaining an API Key
~~~~~~~~~~~~~~~~~~~~

1. Log in to IBM Cloud: https://cloud.ibm.com
2. Navigate to **Manage** → **Access (IAM)** → **API keys**
3. Click **Create an IBM Cloud API key**
4. Provide a name and description
5. Copy the API key (it won't be shown again)

AWS Cloud Authentication
------------------------

For AWS-hosted IBM services, use MCSP V2 authentication.

Configuration
~~~~~~~~~~~~~

.. code-block:: python

    from wxdi.common.auth import AuthConfig, AuthProvider, EnvironmentType

    config = AuthConfig(
        environment_type=EnvironmentType.AWS_CLOUD,
        api_key="your-aws-api-key",
        account_id="your-aws-account-id"
    )

    provider = AuthProvider(config)
    token = provider.get_token()

**Required Parameters:**

* ``environment_type``: Must be ``EnvironmentType.AWS_CLOUD``
* ``api_key``: Your AWS API key
* ``account_id``: Your AWS account ID

**Optional Parameters:**

* ``url``: Custom authentication URL (defaults to ``https://account-iam.platform.saas.ibm.com``)
* ``disable_ssl_verification``: SSL verification control (default: ``True``)

Government Cloud Authentication
--------------------------------

For government cloud deployments with specialized security requirements.

Configuration
~~~~~~~~~~~~~

.. code-block:: python

    from wxdi.common.auth import AuthConfig, AuthProvider, EnvironmentType

    config = AuthConfig(
        environment_type=EnvironmentType.GOV_CLOUD,
        api_key="your-gov-cloud-api-key"
    )

    provider = AuthProvider(config)
    token = provider.get_token()

**Required Parameters:**

* ``environment_type``: Must be ``EnvironmentType.GOV_CLOUD``
* ``api_key``: Your Government Cloud API key

**Optional Parameters:**

* ``url``: Custom authentication URL (defaults to ``https://dai.ibmforusgov.com/api/rest/mcsp/apikeys/token``)
* ``disable_ssl_verification``: SSL verification control (default: ``True``)

On-Premises Authentication
---------------------------

For on-premises Cloud Pak for Data installations.

Authentication with API Key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from wxdi.common.auth import AuthConfig, AuthProvider, EnvironmentType

    config = AuthConfig(
        environment_type=EnvironmentType.ON_PREM,
        url="https://your-cp4d-instance.example.com",
        username="your-username",
        api_key="your-cp4d-api-key"
    )

    provider = AuthProvider(config)
    token = provider.get_token()

Authentication with Username/Password
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from wxdi.common.auth import AuthConfig, AuthProvider, EnvironmentType

    config = AuthConfig(
        environment_type=EnvironmentType.ON_PREM,
        url="https://your-cp4d-instance.example.com",
        username="your-username",
        password="your-password"
    )

    provider = AuthProvider(config)
    token = provider.get_token()

**Required Parameters:**

* ``environment_type``: Must be ``EnvironmentType.ON_PREM``
* ``url``: Your Cloud Pak for Data instance URL
* ``username``: Your username
* ``api_key`` OR ``password``: One of these is required

**Optional Parameters:**

* ``disable_ssl_verification``: SSL verification control (default: ``True``)

.. note::
   The authentication path ``/icp4d-api/v1/authorize`` is automatically appended to the URL if not present.

Configuration Reference
-----------------------

AuthConfig Class
~~~~~~~~~~~~~~~~

.. py:class:: AuthConfig

   Type-safe configuration for authentication.

   :param environment_type: The cloud environment type
   :type environment_type: EnvironmentType
   :param url: Authentication endpoint URL (optional for most environments)
   :type url: Optional[str]
   :param api_key: API key for authentication
   :type api_key: Optional[str]
   :param username: Username (required for ON_PREM)
   :type username: Optional[str]
   :param password: Password (alternative to api_key for ON_PREM)
   :type password: Optional[str]
   :param account_id: Account ID (required for AWS_CLOUD)
   :type account_id: Optional[str]
   :param disable_ssl_verification: Disable SSL verification
   :type disable_ssl_verification: bool

   **Validation:**

   The configuration is validated automatically on creation:

   * Environment type must be valid
   * Required fields must be present for each environment
   * URLs are normalized (trailing slashes removed)
   * Default URLs are applied when not specified

EnvironmentType Enum
~~~~~~~~~~~~~~~~~~~~

.. py:class:: EnvironmentType

   Enumeration of supported cloud environments.

   .. py:attribute:: IBM_CLOUD

      IBM Cloud standard environment

   .. py:attribute:: AWS_CLOUD

      Amazon Web Services cloud environment

   .. py:attribute:: GOV_CLOUD

      Government cloud environment

   .. py:attribute:: ON_PREM

      On-premises installation

AuthProvider Class
~~~~~~~~~~~~~~~~~~

.. py:class:: AuthProvider

   Factory for creating environment-specific authenticators.

   :param config: Authentication configuration
   :type config: AuthConfig

   .. py:method:: get_token() -> str

      Generate and return an authentication token.

      :returns: Authentication token
      :rtype: str
      :raises ValueError: If authenticator is invalid
      :raises Exception: If token generation fails

Advanced Usage
--------------

Custom URLs for Non-Production
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For staging, development, or testing environments:

.. code-block:: python

    config = AuthConfig(
        environment_type=EnvironmentType.IBM_CLOUD,
        url="https://staging-iam.example.com/identity/token",
        api_key="your-api-key"
    )

SSL Verification Control
~~~~~~~~~~~~~~~~~~~~~~~~~

Enable SSL verification for production environments:

.. code-block:: python

    config = AuthConfig(
        environment_type=EnvironmentType.ON_PREM,
        url="https://your-cp4d-instance.example.com",
        username="your-username",
        api_key="your-api-key",
        disable_ssl_verification=False  # Enable SSL verification
    )

Token Refresh
~~~~~~~~~~~~~

Tokens are automatically refreshed when expired:

.. code-block:: python

    provider = AuthProvider(config)
    
    # First call - generates new token
    token1 = provider.get_token()
    
    # Subsequent calls - reuses token if not expired
    token2 = provider.get_token()
    
    # After expiration - automatically refreshes
    token3 = provider.get_token()

Error Handling
--------------

Configuration Errors
~~~~~~~~~~~~~~~~~~~~

Handle configuration validation errors:

.. code-block:: python

    from wxdi.common.auth import AuthConfig, EnvironmentType

    try:
        config = AuthConfig(
            environment_type=EnvironmentType.IBM_CLOUD
            # Missing api_key
        )
    except ValueError as e:
        print(f"Configuration error: {e}")
        # Output: API key must be provided for ibm_cloud environment type

Authentication Errors
~~~~~~~~~~~~~~~~~~~~~

Handle token generation errors:

.. code-block:: python

    from wxdi.common.auth import AuthProvider

    try:
        provider = AuthProvider(config)
        token = provider.get_token()
    except Exception as e:
        print(f"Authentication failed: {e}")
        # Handle error (retry, log, etc.)

Best Practices
--------------

1. **Secure Credentials**

   Never hardcode credentials in source code:

   .. code-block:: python

       import os

       config = AuthConfig(
           environment_type=EnvironmentType.IBM_CLOUD,
           api_key=os.environ.get("IBM_CLOUD_API_KEY")
       )

2. **Reuse AuthProvider**

   Create one AuthProvider instance and reuse it:

   .. code-block:: python

       # Good - reuse provider
       provider = AuthProvider(config)
       token1 = provider.get_token()
       token2 = provider.get_token()

       # Avoid - creating multiple providers
       token1 = AuthProvider(config).get_token()
       token2 = AuthProvider(config).get_token()

3. **Enable SSL in Production**

   Always enable SSL verification for production:

   .. code-block:: python

       config = AuthConfig(
           environment_type=EnvironmentType.ON_PREM,
           url="https://production.example.com",
           username="user",
           api_key="key",
           disable_ssl_verification=False  # Production setting
       )

4. **Handle Errors Gracefully**

   Implement retry logic for transient failures:

   .. code-block:: python

       import time

       def get_token_with_retry(provider, max_retries=3):
           for attempt in range(max_retries):
               try:
                   return provider.get_token()
               except Exception as e:
                   if attempt == max_retries - 1:
                       raise
                   time.sleep(2 ** attempt)  # Exponential backoff

Using Authentication with SDK Modules
--------------------------------------

DQ Validator REST API Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use authentication with data quality providers:

.. code-block:: python

    from wxdi.common.auth import AuthConfig, AuthProvider, EnvironmentType
    from wxdi.dq_validator.provider import ProviderConfig, GlossaryProvider

    # Set up authentication
    auth_config = AuthConfig(
        environment_type=EnvironmentType.IBM_CLOUD,
        api_key="your-api-key"
    )
    auth_provider = AuthProvider(auth_config)
    token = auth_provider.get_token()

    # Use with provider
    provider_config = ProviderConfig(
        base_url="https://api.dataplatform.cloud.ibm.com",
        auth_token=token
    )
    glossary_provider = GlossaryProvider(provider_config)

Future Modules
~~~~~~~~~~~~~~

All future SDK modules will use the same authentication infrastructure:

.. code-block:: python

    # Authentication works the same for all modules
    auth_provider = AuthProvider(config)
    token = auth_provider.get_token()

    # Use with any SDK module
    # module_client = SomeModule(token=token)

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Issue: "API key must be provided"**

* Ensure you're passing the ``api_key`` parameter
* Check that the API key is not empty or None

**Issue: "URL must be specified for ON_PREM"**

* ON_PREM environment requires explicit URL
* Provide the full URL to your Cloud Pak for Data instance

**Issue: "Account ID must be provided for AWS_CLOUD"**

* AWS_CLOUD requires both ``api_key`` and ``account_id``
* Obtain account ID from your AWS administrator

**Issue: SSL certificate verification failed**

* For development: Set ``disable_ssl_verification=True``
* For production: Ensure valid SSL certificates are installed

Next Steps
----------

* Learn about :ref:`DQ Validator<dq_validator>` module
* Explore :ref:`API Reference<api_ref>` for detailed documentation
* Check :ref:`FAQ<faq>` for common questions

.. Made with Bob
