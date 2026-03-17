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

.. _api_dq_validator_providers:

REST API Providers
==================

The providers module integrates with IBM Cloud Pak for Data REST APIs.

.. currentmodule:: wxdi.dq_validator.provider

Configuration
-------------

ProviderConfig
~~~~~~~~~~~~~~

.. autoclass:: wxdi.dq_validator.provider.config.ProviderConfig
   :members:
   :undoc-members:
   :show-inheritance:

Base Provider
-------------

.. autoclass:: wxdi.dq_validator.provider.base_provider.BaseProvider
   :members:
   :undoc-members:
   :show-inheritance:

Glossary Provider
-----------------

.. autoclass:: wxdi.dq_validator.provider.glossary.GlossaryProvider
   :members:
   :undoc-members:
   :show-inheritance:

CAMS Provider
-------------

.. autoclass:: wxdi.dq_validator.provider.cams.CamsProvider
   :members:
   :undoc-members:
   :show-inheritance:

Assets Provider
---------------

.. autoclass:: wxdi.dq_validator.provider.assets.DQAssetsProvider
   :members:
   :undoc-members:
   :show-inheritance:

Dimensions Provider
-------------------

.. autoclass:: wxdi.dq_validator.provider.dimensions.DimensionsProvider
   :members:
   :undoc-members:
   :show-inheritance:

Checks Provider
---------------

.. autoclass:: wxdi.dq_validator.provider.checks.ChecksProvider
   :members:
   :undoc-members:
   :show-inheritance:

Issues Provider
---------------

.. autoclass:: wxdi.dq_validator.provider.issues.IssuesProvider
   :members:
   :undoc-members:
   :show-inheritance:

DQ Search Provider
------------------

.. autoclass:: wxdi.dq_validator.provider.dq_search.DQSearchProvider
   :members:
   :undoc-members:
   :show-inheritance:

Data Models
-----------

DataAsset
~~~~~~~~~

.. automodule:: wxdi.dq_validator.provider.data_asset_model
   :members:
   :undoc-members:
   :show-inheritance:

Constraint Models
~~~~~~~~~~~~~~~~~

.. automodule:: wxdi.dq_validator.provider.constraint_model
   :members:
   :undoc-members:
   :show-inheritance:

Response Models
~~~~~~~~~~~~~~~

.. automodule:: wxdi.dq_validator.provider.response_model
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

See :ref:`REST API Integration<dq_validator_rest_api_integration>` for detailed usage examples.

.. Made with Bob
