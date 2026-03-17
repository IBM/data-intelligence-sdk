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

.. _dq_validator_rest_api_integration:

REST API Integration
====================

The DQ Validator module integrates with IBM Cloud Pak for Data through REST API providers.

.. note::
   This section provides an overview. Detailed API documentation is available in the :ref:`API Reference<api_ref>`.

Available Providers
-------------------

* **GlossaryProvider** - Fetch glossary terms and DQ constraints
* **CamsProvider** - Fetch data assets from CAMS
* **AssetsProvider** - Manage data assets
* **DimensionsProvider** - Manage DQ dimensions
* **ChecksProvider** - Manage DQ checks
* **IssuesProvider** - Track and manage DQ issues
* **DQSearchProvider** - Search for DQ checks and assets

Example Usage
-------------

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

    # Use provider
    provider_config = ProviderConfig(
        base_url="https://api.dataplatform.cloud.ibm.com",
        auth_token=token
    )
    glossary_provider = GlossaryProvider(provider_config)

For detailed usage examples and API documentation, see the :ref:`API Reference<api_ref>`.

.. Made with Bob
