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

.. _data_contracts_usage:

Usage Guide
===========

This guide covers the full lifecycle of managing data contracts through the SDK — from initial setup to running tests.

Setup
-----

The :class:`~wxdi.data_contracts.DataContractsProvider` requires a
:class:`~wxdi.dq_validator.provider.config.ProviderConfig` with the CPD base URL and a
Bearer token:

.. code-block:: python

    from wxdi.data_contracts import DataContractsProvider
    from wxdi.dq_validator.provider import ProviderConfig

    config = ProviderConfig(
        url="https://your-cpd-host.example.com",
        auth_token="Bearer <your-token>",
    )
    provider = DataContractsProvider(config)

.. tip::
   You can also supply an ``auth_config`` (``AuthConfig``) to ``ProviderConfig`` for
   automatic token management. See :ref:`Authentication<api_common_auth>` for details.

Validating a Contract
---------------------

Before persisting a contract, validate it against the ODCS schema. The HTTP 200 response
means the validation *process* completed — inspect ``response.valid`` to determine whether
the contract content itself is valid.

**Project-scoped**

.. code-block:: python

    from wxdi.data_contracts import DataContractValidationRequest

    body = DataContractValidationRequest(data_contract_content=MY_YAML_STRING)
    result = provider.validate_project_data_contract("my-project-id", body)

    if result.valid:
        print("Contract is valid")
    else:
        print(f"{result.error_count} error(s):")
        for err in result.errors:
            print(f"  [{err.type}] {err.property}: {err.message}")

**Catalog-scoped**

.. code-block:: python

    result = provider.validate_catalog_data_contract("my-catalog-id", body)

Creating a Contract
-------------------

Use :class:`~wxdi.data_contracts.DataContractPrototypeYaml` for inline YAML or
:class:`~wxdi.data_contracts.DataContractPrototypeJson` for a Python dict payload.
Both are accepted by every create/replace method.

.. code-block:: python

    from wxdi.data_contracts import DataContractPrototypeYaml, DataContractPrototypeJson

    # --- YAML variant ---
    yaml_body = DataContractPrototypeYaml(
        name="My Banking Contract",
        contract_yaml=MY_YAML_STRING,
    )
    contract = provider.create_project_data_contract("my-project-id", yaml_body)
    print(f"Created: id={contract.id}  name={contract.name}")

    # --- JSON / dict variant ---
    json_body = DataContractPrototypeJson(
        name="My Banking Contract",
        contract_json=MY_CONTRACT_DICT,
    )
    contract = provider.create_catalog_data_contract("my-catalog-id", json_body)

Both methods accept an optional ``validate=False`` keyword argument to skip ODCS
schema validation (useful for draft contracts that are not yet ODCS-compliant).

.. code-block:: python

    contract = provider.create_project_data_contract(
        "my-project-id", yaml_body, validate=False
    )

Listing Contracts
-----------------

.. code-block:: python

    collection = provider.list_project_data_contracts("my-project-id", limit=50)
    print(f"Total: {collection.total_count}")
    for dc in collection.data_contracts:
        print(f"  {dc.id}  {dc.name}")

    # Catalog equivalent
    collection = provider.list_catalog_data_contracts("my-catalog-id")

Retrieving a Single Contract
----------------------------

.. code-block:: python

    contract = provider.get_project_data_contract("my-project-id", "contract-id")
    print(contract.contract_yaml)          # raw YAML string
    print(contract.server_mappings)        # List[ServerMapping]

Replacing (Updating) a Contract
--------------------------------

``replace_*`` performs a full replacement (HTTP PUT). Supply a new
:class:`~wxdi.data_contracts.DataContractPrototype` to overwrite all contract content.

.. code-block:: python

    updated_body = DataContractPrototypeYaml(
        name="My Banking Contract",
        contract_yaml=UPDATED_YAML_STRING,
    )
    contract = provider.replace_project_data_contract(
        "my-project-id", "contract-id", updated_body
    )

Uploading a Contract File
-------------------------

Use the upload endpoint to create or update a contract from a file object or raw bytes.
This uses multipart form upload — do **not** set ``Content-Type`` manually; it is set
automatically.

.. code-block:: python

    import io

    with open("my_contract.yaml", "rb") as f:
        contract = provider.upload_project_data_contract_file(
            "my-project-id",
            f,
            name="My Banking Contract",
        )

    # From bytes
    contract = provider.upload_project_data_contract_file(
        "my-project-id",
        io.BytesIO(yaml_bytes),
        name="My Banking Contract",
    )

To **update** an existing contract via upload, pass ``data_contract_id``:

.. code-block:: python

    contract = provider.upload_project_data_contract_file(
        "my-project-id",
        io.BytesIO(yaml_bytes),
        name="My Banking Contract",
        data_contract_id="existing-contract-id",
    )

Server Mappings
---------------

Server mappings link the logical server names defined in the ODCS contract to
actual connection assets in IBM Cloud Pak for Data. They can be provided at
create/replace/upload time.

.. code-block:: python

    from wxdi.data_contracts import ServerMapping, ConnectionInfo

    mappings = [
        ServerMapping(
            server="banking-db",
            connection=ConnectionInfo(id="019fd738-ffce-7799-8720-32deb3447685"),
        )
    ]

    body = DataContractPrototypeYaml(
        name="My Banking Contract",
        contract_yaml=MY_YAML_STRING,
        server_mappings=mappings,
    )
    contract = provider.create_project_data_contract("my-project-id", body)

For file upload, serialize mappings as a JSON string:

.. code-block:: python

    import json

    sm_json = json.dumps([{"server": "banking-db", "connection": {"id": "conn-id"}}])
    contract = provider.upload_project_data_contract_file(
        "my-project-id",
        io.BytesIO(yaml_bytes),
        name="My Banking Contract",
        server_mappings=sm_json,
    )

Running a Test
--------------

.. note::
   Test endpoints are only available for project-scoped contracts (not catalogs).
   They are internal/experimental endpoints that may require additional server configuration.

.. code-block:: python

    from wxdi.data_contracts import DataContractTestRequest

    test_body = DataContractTestRequest(retain_dq_objects=False)
    test_run = provider.test_project_data_contract(
        "my-project-id", "contract-id", test_body
    )
    print(f"Test run: id={test_run.id}  status={test_run.status}")

Retrieving Test Results
-----------------------

.. code-block:: python

    # List all test runs for a contract
    collection = provider.list_project_data_contract_test_results(
        "my-project-id", "contract-id", include_all_details=True
    )
    for run in collection.test_results:
        print(f"  run={run.id}  status={run.status}  start={run.start}")
        for check in run.check_results:
            status = "✓" if check.passed else "✗"
            print(f"    {status} {check.check_name}: {check.message}")

    # Retrieve a specific test run
    run = provider.get_project_data_contract_test_result(
        "my-project-id", "contract-id", run_id, include_all_details=True
    )

Deleting Contracts
------------------

Delete operations accept a comma-separated string of contract IDs:

.. code-block:: python

    # Delete a single contract
    provider.delete_project_data_contracts(
        "my-project-id", data_contract_ids="contract-id"
    )

    # Delete multiple contracts in one call
    provider.delete_project_data_contracts(
        "my-project-id",
        data_contract_ids="id-one,id-two,id-three",
    )

    # Catalog equivalent
    provider.delete_catalog_data_contracts(
        "my-catalog-id", data_contract_ids="contract-id"
    )

Error Handling
--------------

All provider methods raise :class:`ValueError` when the server returns a non-2xx
HTTP status code. The exception message includes the status code and response body:

.. code-block:: python

    try:
        contract = provider.get_project_data_contract("my-project-id", "bad-id")
    except ValueError as exc:
        print(f"API error: {exc}")

.. Made with Bob
