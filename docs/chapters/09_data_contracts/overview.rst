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

.. _data_contracts_overview:

Overview
========

The Data Contracts module is a thin, typed Python wrapper around the IBM Data Quality Data Contracts REST API. Its goals are:

* Expose every endpoint as a well-documented, type-hinted method.
* Accept and return Pydantic models so callers get IDE auto-completion and runtime validation.
* Normalise inconsistencies in the server response shape transparently.

What is a Data Contract?
------------------------

A *data contract* is a formal, machine-readable agreement between a data producer and a data consumer. It is written according to the `Open Data Contract Standard (ODCS) <https://github.com/datacontract/datacontract-specification>`_ and describes:

* **Schema** – table and column definitions with logical and physical types.
* **Quality rules** – SQL or library-based checks that must pass.
* **Servers** – database or service endpoints the contract applies to.
* **Metadata** – domain, tenant, status, and versioning information.

IBM Data Quality stores contracts as first-class assets in CAMS (Catalog Asset Management System), scoped to either a *project* or a *catalog*.

Module Components
-----------------

DataContractsProvider
~~~~~~~~~~~~~~~~~~~~~

The central class for all API interactions. It extends the shared ``BaseProvider`` and groups methods by scope:

**Project-scoped endpoints**

+---------------------------------------------------+------------------------------------------+
| Method                                            | HTTP endpoint                            |
+===================================================+==========================================+
| ``validate_project_data_contract``                | POST …/data_contracts_validation         |
+---------------------------------------------------+------------------------------------------+
| ``list_project_data_contracts``                   | GET  …/data_contracts                    |
+---------------------------------------------------+------------------------------------------+
| ``create_project_data_contract``                  | POST …/data_contracts                    |
+---------------------------------------------------+------------------------------------------+
| ``delete_project_data_contracts``                 | DELETE …/data_contracts                  |
+---------------------------------------------------+------------------------------------------+
| ``get_project_data_contract``                     | GET  …/data_contracts/{id}               |
+---------------------------------------------------+------------------------------------------+
| ``replace_project_data_contract``                 | PUT  …/data_contracts/{id}               |
+---------------------------------------------------+------------------------------------------+
| ``upload_project_data_contract_file``             | POST …/data_contracts_upload             |
+---------------------------------------------------+------------------------------------------+
| ``test_project_data_contract``                    | POST …/data_contracts/{id}/test          |
+---------------------------------------------------+------------------------------------------+
| ``list_project_data_contract_test_results``       | GET  …/data_contracts/{id}/test_results  |
+---------------------------------------------------+------------------------------------------+
| ``delete_project_data_contract_test_results``     | DELETE …/test_results                    |
+---------------------------------------------------+------------------------------------------+
| ``get_project_data_contract_test_result``         | GET  …/test_results/{run_id}             |
+---------------------------------------------------+------------------------------------------+

**Catalog-scoped endpoints**

The catalog surface mirrors the project surface (without test endpoints):
``validate_catalog_data_contract``, ``list_catalog_data_contracts``,
``create_catalog_data_contract``, ``delete_catalog_data_contracts``,
``get_catalog_data_contract``, ``replace_catalog_data_contract``,
``upload_catalog_data_contract_file``.

Pydantic Models
~~~~~~~~~~~~~~~

All request bodies and response payloads are represented as Pydantic v2 models.

**Request models**

* :class:`~wxdi.data_contracts.DataContractPrototypeYaml` – create/replace using inline YAML.
* :class:`~wxdi.data_contracts.DataContractPrototypeJson` – create/replace using a Python dict.
* :class:`~wxdi.data_contracts.DataContractValidationRequest` – raw contract content to validate.
* :class:`~wxdi.data_contracts.DataContractTestRequest` – test configuration (server mappings, ``retain_dq_objects``).

**Response models**

* :class:`~wxdi.data_contracts.DataContract` – a persisted contract asset.
* :class:`~wxdi.data_contracts.DataContractCollection` – paginated list of contracts.
* :class:`~wxdi.data_contracts.DataContractValidationResponse` – validation result with error details.
* :class:`~wxdi.data_contracts.DataContractTestResponse` – a single test-run result.
* :class:`~wxdi.data_contracts.DataContractTestResponseCollection` – list of test-run results.

**Sub-models**

* :class:`~wxdi.data_contracts.ConnectionInfo` – reference to a connection asset.
* :class:`~wxdi.data_contracts.ServerMapping` – maps a logical server name to a connection.
* :class:`~wxdi.data_contracts.DataContractValidationError` – a single ODCS schema error.
* :class:`~wxdi.data_contracts.DataContractInfo` – brief contract reference embedded in test results.
* :class:`~wxdi.data_contracts.LogEntry` – a single log line from a test run.
* :class:`~wxdi.data_contracts.CheckResult` – outcome of one quality check in a test run.

Response Shape Normalisation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The IBM Data Quality API may return contracts in two different shapes:

**Flat shape** (per OpenAPI spec)::

    {"id": "...", "name": "...", "contract_yaml": "...", "server_mappings": [...]}

**Nested CAMS shape** (actual API responses)::

    {
      "metadata": {"asset_id": "...", "name": "..."},
      "entity":   {"ibm_data_contract": {...}},
      "href": "..."
    }

:class:`~wxdi.data_contracts.DataContract` uses a Pydantic ``model_validator`` to promote
``metadata.asset_id`` → ``id`` and ``metadata.name`` → ``name`` transparently, so callers
can always use ``contract.id`` and ``contract.name`` regardless of which shape the server returned.

.. Made with Bob
