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

.. _api_common_auth:

Authentication API
==================

The authentication module provides a unified framework for authenticating with multiple cloud environments.

.. currentmodule:: common.auth

Configuration
-------------

AuthConfig
~~~~~~~~~~

.. autoclass:: common.auth.auth_config.AuthConfig
   :members:
   :undoc-members:
   :show-inheritance:

EnvironmentType
~~~~~~~~~~~~~~~

.. autoclass:: common.auth.auth_config.EnvironmentType
   :members:
   :undoc-members:
   :show-inheritance:

Authentication Provider
-----------------------

AuthProvider
~~~~~~~~~~~~

.. autoclass:: common.auth.auth_provider.AuthProvider
   :members:
   :undoc-members:
   :show-inheritance:

Government Cloud Authenticator
-------------------------------

GovCloudAuthenticator
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: common.auth.gov_cloud_authenticator.GovCloudAuthenticator
   :members:
   :undoc-members:
   :show-inheritance:

GovCloudTokenManager
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: common.auth.gov_cloud_token_manager.GovCloudTokenManager
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

See :ref:`Authentication Guide<authentication>` for detailed usage examples.

.. Made with Bob
