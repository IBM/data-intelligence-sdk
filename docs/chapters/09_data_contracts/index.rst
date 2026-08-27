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

.. _data_contracts:

Data Contracts Module
=====================

The **Data Contracts** module provides a Python client for managing Open Data Contract Standard (ODCS) compliant data contracts via the IBM Data Quality REST API.

It covers all project-scoped and catalog-scoped endpoints under:

* ``/data_quality/v4/projects/{project_id}/data_contracts``
* ``/data_quality/v4/catalogs/{catalog_id}/data_contracts``

Key Capabilities
----------------

**CRUD Operations**
   Create, retrieve, replace (full update), and delete data contracts in both projects and catalogs.

**ODCS Schema Validation**
   Validate raw contract content against the Open Data Contract Standard schema before persisting it.

**File Upload**
   Upload YAML or JSON contract files using multipart form upload.

**Test Execution**
   Trigger data contract test runs and retrieve detailed results including logs and per-check outcomes.

**Pydantic Models**
   Fully typed request and response models for all API payloads, with automatic normalisation of the nested CAMS asset response shape.

Architecture
------------

.. code-block:: text

    wxdi/
    └── data_contracts/
        ├── __init__.py        # Public re-exports
        ├── models.py          # Pydantic request/response models
        └── provider.py        # DataContractsProvider (all API calls)

The :class:`~wxdi.data_contracts.DataContractsProvider` extends ``BaseProvider``
and re-uses the shared :class:`~wxdi.dq_validator.provider.config.ProviderConfig`
for authentication and base URL configuration.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   usage_guide
   examples

Next Steps
----------

- :ref:`data_contracts_overview` - Architecture and design decisions
- :ref:`data_contracts_usage` - Step-by-step usage guide
- :ref:`data_contracts_examples` - Runnable code examples
- :ref:`api_data_contracts` - Complete API reference

.. Made with Bob
