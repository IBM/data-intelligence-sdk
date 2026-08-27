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

.. _api_data_contracts:

Data Contracts Reference
========================

The Data Contracts module provides a client and Pydantic models for managing Open Data Contract Standard (ODCS) compliant contracts via the IBM Data Quality REST API.

.. currentmodule:: wxdi.data_contracts

Provider
--------

DataContractsProvider
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.provider.DataContractsProvider
   :members:
   :undoc-members:
   :show-inheritance:

Request Models
--------------

DataContractPrototypeYaml
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractPrototypeYaml
   :members:
   :undoc-members:
   :show-inheritance:

DataContractPrototypeJson
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractPrototypeJson
   :members:
   :undoc-members:
   :show-inheritance:

DataContractValidationRequest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractValidationRequest
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestRequest
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestRequest
   :members:
   :undoc-members:
   :show-inheritance:

Response Models
---------------

DataContract
~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContract
   :members:
   :undoc-members:
   :show-inheritance:

DataContractCollection
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractCollection
   :members:
   :undoc-members:
   :show-inheritance:

DataContractValidationResponse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractValidationResponse
   :members:
   :undoc-members:
   :show-inheritance:

DataContractValidationError
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractValidationError
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResponse
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResponse
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResponseCollection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResponseCollection
   :members:
   :undoc-members:
   :show-inheritance:

Supporting Models
-----------------

ConnectionInfo
~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.ConnectionInfo
   :members:
   :undoc-members:
   :show-inheritance:

ServerMapping
~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.ServerMapping
   :members:
   :undoc-members:
   :show-inheritance:

DataContractInfo
~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractInfo
   :members:
   :undoc-members:
   :show-inheritance:

LogEntry
~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.LogEntry
   :members:
   :undoc-members:
   :show-inheritance:

CheckResult
~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.CheckResult
   :members:
   :undoc-members:
   :show-inheritance:

.. Made with Bob
