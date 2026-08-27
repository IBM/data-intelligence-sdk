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

.. _data_contracts_examples:

Examples
========

The file ``examples/data_contracts_usage.py`` contains runnable end-to-end examples for
every API endpoint. The snippets below are drawn from that file.

.. tip::
   Edit the ``CONFIG`` block at the top of ``examples/data_contracts_usage.py`` with your
   CPD URL, bearer token, project ID, catalog ID, and connection ID before running.

Provider Initialisation
-----------------------

.. code-block:: python

    from wxdi.data_contracts import DataContractsProvider
    from wxdi.dq_validator.provider import ProviderConfig

    config = ProviderConfig(
        url="https://cpd-wkc.apps.example.com",
        auth_token="Bearer <token>",
    )
    provider = DataContractsProvider(config)

Validating a Contract (Project)
--------------------------------

.. code-block:: python

    from wxdi.data_contracts.models import DataContractValidationRequest

    body = DataContractValidationRequest(data_contract_content=SAMPLE_CONTRACT_YAML)
    result = provider.validate_project_data_contract(PROJECT_ID, body)

    print(f"valid={result.valid}  error_count={result.error_count}")
    if not result.valid:
        for err in result.errors:
            print(f"  [{err.type}] {err.property}: {err.message}")

Creating a Contract with YAML (Project)
----------------------------------------

.. code-block:: python

    from wxdi.data_contracts.models import DataContractPrototypeYaml

    body = DataContractPrototypeYaml(
        name="BANK_transaction_contract",
        contract_yaml=SAMPLE_CONTRACT_YAML,
    )
    contract = provider.create_project_data_contract(PROJECT_ID, body)
    print(f"created id={contract.id}  name={contract.name}")

Creating a Contract with JSON (Project)
----------------------------------------

.. code-block:: python

    from wxdi.data_contracts.models import DataContractPrototypeJson

    body = DataContractPrototypeJson(
        name="BANK_transaction_contract_json",
        contract_json=SAMPLE_CONTRACT_DICT,
    )
    contract = provider.create_project_data_contract(PROJECT_ID, body)
    print(f"created id={contract.id}  name={contract.name}")

Listing Contracts (Project)
----------------------------

.. code-block:: python

    result = provider.list_project_data_contracts(PROJECT_ID, limit=5)
    print(f"total={result.total_count}  returned={len(result.data_contracts)}")
    for dc in result.data_contracts:
        print(f"  id={dc.id}  name={dc.name}")

Getting a Contract (Project)
-----------------------------

.. code-block:: python

    contract = provider.get_project_data_contract(PROJECT_ID, contract_id)
    print(f"id={contract.id}  name={contract.name}")

Replacing a Contract (Project)
-------------------------------

.. code-block:: python

    updated_yaml = SAMPLE_CONTRACT_YAML.replace(
        "name: BANK_transaction_contract",
        "name: BANK_transaction_contract_v2",
    )
    body = DataContractPrototypeYaml(
        name="BANK_transaction_contract",
        contract_yaml=updated_yaml,
    )
    contract = provider.replace_project_data_contract(PROJECT_ID, contract_id, body)
    print(f"id={contract.id}  name={contract.name}")

Uploading a Contract File (Project)
------------------------------------

.. code-block:: python

    import io

    file_bytes = SAMPLE_CONTRACT_YAML.encode()
    contract = provider.upload_project_data_contract_file(
        PROJECT_ID,
        io.BytesIO(file_bytes),
        name="BANK_transaction_contract_upload",
    )
    print(f"id={contract.id}  name={contract.name}")

Running a Test (Project)
-------------------------

.. code-block:: python

    from wxdi.data_contracts.models import DataContractTestRequest

    body = DataContractTestRequest(retain_dq_objects=False)
    result = provider.test_project_data_contract(PROJECT_ID, contract_id, body)
    print(f"test_run_id={result.id}  status={result.status}")

Listing Test Results (Project)
-------------------------------

.. code-block:: python

    collection = provider.list_project_data_contract_test_results(
        PROJECT_ID, contract_id
    )
    for run in collection.test_results:
        print(f"  run_id={run.id}  status={run.status}")

Getting a Single Test Result (Project)
---------------------------------------

.. code-block:: python

    # Fetch the first available run ID
    collection = provider.list_project_data_contract_test_results(
        PROJECT_ID, contract_id
    )
    run_id = collection.test_results[0].id

    run = provider.get_project_data_contract_test_result(
        PROJECT_ID, contract_id, run_id
    )
    print(f"run_id={run.id}  status={run.status}  run_by={run.run_by}")

Deleting Test Results (Project)
--------------------------------

.. code-block:: python

    provider.delete_project_data_contract_test_results(PROJECT_ID, contract_id)
    print("All test results deleted")

Deleting Contracts (Project)
-----------------------------

.. code-block:: python

    provider.delete_project_data_contracts(
        PROJECT_ID, data_contract_ids=contract_id
    )
    print(f"Deleted {contract_id}")

Catalog-Scoped Examples
------------------------

All project-scoped methods have catalog equivalents. Replace ``project_id`` with
``catalog_id`` and the method prefix ``project`` with ``catalog``:

.. code-block:: python

    # Validate
    result = provider.validate_catalog_data_contract(CATALOG_ID, body)

    # Create
    contract = provider.create_catalog_data_contract(CATALOG_ID, body)

    # List
    collection = provider.list_catalog_data_contracts(CATALOG_ID, limit=10)

    # Get
    contract = provider.get_catalog_data_contract(CATALOG_ID, contract_id)

    # Replace
    contract = provider.replace_catalog_data_contract(CATALOG_ID, contract_id, body)

    # Upload
    contract = provider.upload_catalog_data_contract_file(
        CATALOG_ID, io.BytesIO(file_bytes), name="My Contract"
    )

    # Delete
    provider.delete_catalog_data_contracts(
        CATALOG_ID, data_contract_ids=contract_id
    )

Running All Examples
--------------------

The ``examples/data_contracts_usage.py`` script can be run directly after configuring
the ``CONFIG`` block:

.. code-block:: bash

    python examples/data_contracts_usage.py

The script executes all project-scoped and catalog-scoped examples in sequence,
printing pass/fail status for each. It automatically cleans up any contracts or
test results it creates.

.. Made with Bob
