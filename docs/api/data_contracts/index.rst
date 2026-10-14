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

DataContractTestResultPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultPrototype
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

DataContractTestResult
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResult
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultCollection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultCollection
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

DataContractType
~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractType
   :members:
   :undoc-members:
   :show-inheritance:

Test Result Sub-Models
----------------------

Nested models used inside :class:`~wxdi.data_contracts.models.DataContractTestResult`.

DataContractTestResultJobRun
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultJobRun
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultJobInfo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultJobInfo
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultSchemaValidationSummary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultSchemaValidationSummary
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultDataQualitySummary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultDataQualitySummary
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultSummary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultSummary
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultPhysicalTypeCheck
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultPhysicalTypeCheck
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultColumnsSummary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultColumnsSummary
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultAssetSchemaValidation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultAssetSchemaValidation
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultColumnTypeCheck
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultColumnTypeCheck
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultRequiredCheck
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultRequiredCheck
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultPrimaryKeyCheck
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultPrimaryKeyCheck
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultUniqueCheck
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultUniqueCheck
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultColumnSchemaValidation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultColumnSchemaValidation
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultDqCheckResults
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultDqCheckResults
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultDqRuleJobRun
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultDqRuleJobRun
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultDqRuleJob
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultDqRuleJob
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultDqRuleRef
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultDqRuleRef
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultDqCheck
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultDqCheck
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultColumnResult
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultColumnResult
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultDataAsset
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultDataAsset
   :members:
   :undoc-members:
   :show-inheritance:

Test Result Prototype Sub-Models
--------------------------------

Nested models used inside :class:`~wxdi.data_contracts.models.DataContractTestResultPrototype`.

DataContractTestResultJobRunPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultJobRunPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultJobInfoPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultJobInfoPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultSchemaValidationSummaryPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultSchemaValidationSummaryPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultDataQualitySummaryPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultDataQualitySummaryPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultSummaryPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultSummaryPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultPhysicalTypeCheckPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultPhysicalTypeCheckPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultColumnsSummaryPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultColumnsSummaryPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultAssetSchemaValidationPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultAssetSchemaValidationPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultColumnTypeCheckPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultColumnTypeCheckPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultRequiredCheckPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultRequiredCheckPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultPrimaryKeyCheckPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultPrimaryKeyCheckPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultUniqueCheckPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultUniqueCheckPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultColumnSchemaValidationPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultColumnSchemaValidationPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultDqCheckResultsPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultDqCheckResultsPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultDqRuleJobRunPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultDqRuleJobRunPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultDqRuleJobPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultDqRuleJobPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultDqRuleRefPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultDqRuleRefPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultDqCheckPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultDqCheckPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultColumnResultPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultColumnResultPrototype
   :members:
   :undoc-members:
   :show-inheritance:

DataContractTestResultDataAssetPrototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wxdi.data_contracts.models.DataContractTestResultDataAssetPrototype
   :members:
   :undoc-members:
   :show-inheritance:

.. Made with Bob
