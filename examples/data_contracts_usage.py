"""
Usage examples for the Data Contracts SDK against a live CPD server.

Each function exercises one API endpoint. Run them individually or together.

Usage:
    python examples/data_contracts_usage.py

Configuration:
    Edit the CONFIG block below before running.
"""

import io
import json
import traceback

from wxdi.data_contracts import DataContractsProvider
from wxdi.data_contracts.models import (
    DataContractPrototypeYaml,
    DataContractPrototypeJson,
    DataContractValidationRequest,
    DataContractTestRequest,
)
from wxdi.dq_validator.provider import ProviderConfig

# ---------------------------------------------------------------------------
# CONFIG — edit these before running
# ---------------------------------------------------------------------------

CPD_URL      = "https://cpd-wkc.apps.dqqa540dev-10.cp.fyre.ibm.com"
BEARER_TOKEN = "Bearer <token>"
PROJECT_ID   = "6ce47397-abfd-4c4a-8a98-d9db02ca6937"
CATALOG_ID   = "019fcbf3-d49d-7481-a3dd-15505acd20b8"
CONNECTION_ID = "019fd738-ffce-7799-8720-32deb3447685"

# Filled in automatically as the smoke tests run
_created_project_contract_id: str | None = None
_created_catalog_contract_id: str | None = None

SAMPLE_CONTRACT_YAML = f"""\
version: 1.0.0
apiVersion: v3.1.0
kind: DataContract
id: Bank_contract_001
name: BANK_transaction_contract
status: active
domain: 'Accounting and Finance: Financial Reporting'
tenant: banking_department
servers:
  - server: banking-db
    type: db2
    description: DB2 production database for client accounts
    environment: prod
    host: 169.44.151.75
    port: 50000
    database: BANK
    schema: BANK1
    customProperties:
      - property: database
        value: BANK
      - property: schema
        value: BANK1
dataProduct: BankingDataProduct
schema:
  - name: BANK_CLIENTS
    physicalName: BANK1/BANK_CLIENTS
    physicalType: table
    logicalType: object
    quality:
      - name: table_row_count
        type: sql
        query: SELECT * FROM BANK1.BANK_CLIENTS;
        mustBe: 5112
        dimension: completeness
      - name: Marital status inconsistent with age
        type: sql
        query: >-
          SELECT AGE, MARITAL_STATUS FROM BANK1.BANK_CLIENTS WHERE AGE < 16 AND
          MARITAL_STATUS IN ('married','divorced','widowed');
        mustBeLessThan: 5
      - name: Contact preference but no phone number
        type: sql
        query: 'SELECT * FROM BANK1.BANK_CLIENTS WHERE REGEXP_LIKE(PHONE1, ''[0-9]'');'
        dimension: conformity
        mustBeLessThan: 5220
    properties:
      - name: ACCOUNT_ID
        physicalName: ACCOUNT_ID
        logicalType: string
        quality:
          - name: Null Value Check for CCN
            type: sql
            query: SELECT * FROM BANK1.BANK_CLIENTS WHERE CCN IS NULL;
            dimension: accuracy
            mustBeGreaterThan: 200
          - name: Missing Values for Customer IDs
            type: library
            metric: missingValues
            arguments:
              missingValues:
                - ''
                - n/a
                - N/A
                - 'null'
                - 'NULL'
            mustBeLessThan: 5
          - name: Duplicate customer IDs via library check
            type: library
            metric: duplicateValues
            mustBe: 2
        primaryKey: false
        unique: true
        required: true
      - name: ZIP
        physicalName: ZIP
        logicalType: string
        quality:
          - name: Invalid ZIP format
            type: sql
            query: >-
              SELECT ZIP FROM BANK1.BANK_CLIENTS WHERE ZIP IS NOT NULL AND NOT
              REGEXP_LIKE(TRIM(ZIP),'^[0-9]{5}$');
            mustBeLessThan: 3005
          - name: Invalid ZIP format via Library check
            type: library
            metric: invalidValues
            arguments:
              pattern: '^[0-9]{5}$'
            mustBeLessThan: 2995
        primaryKey: false
        unique: true
        required: true
      - name: AGE
        physicalName: AGE
        logicalType: string
        quality:
          - name: Implausible customer ages
            type: sql
            query: >-
              SELECT AGE FROM BANK1.BANK_CLIENTS WHERE AGE IS NULL OR AGE < 18
              OR AGE > 100;
            mustBeLessThan: 389
        primaryKey: false
        unique: true
        required: true
      - name: EMAIL
        physicalName: EMAIL
        logicalType: string
        quality:
          - name: Invalid email address format
            type: sql
            query: >-
              SELECT EMAIL FROM BANK1.BANK_CLIENTS WHERE EMAIL IS NOT NULL AND
              NOT
              REGEXP_LIKE(TRIM(EMAIL),'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$');
            mustBeLessThan: 5
        primaryKey: false
        unique: true
        required: true
      - name: GENDER
        physicalName: GENDER
        logicalType: string
        quality:
          - name: Invalid gender
            type: sql
            query: >-
              SELECT GENDER FROM BANK1.BANK_CLIENTS WHERE GENDER NOT IN
              ('L','F');
            mustBeLessThan: 3540
          - name: Invalid gender via library check
            type: library
            metric: invalidValues
            arguments:
              validValues:
                - M
                - B
            mustBeLessThan: 5119
        primaryKey: false
        unique: true
        required: true
      - name: MARITAL_STATUS
        physicalName: MARITAL_STATUS
        logicalType: string
        quality:
          - name: Invalid marital status codes
            type: sql
            query: >-
              SELECT MARITAL_STATUS FROM BANK1.BANK_CLIENTS WHERE MARITAL_STATUS
              NOT IN ('single','married','divorced','separated','unknown');
            mustBeBetween:
              - 765
              - 890
        primaryKey: false
        unique: true
        required: true
customProperties:
  - property: connectionIds
    value:
      - {CONNECTION_ID}
"""

SAMPLE_CONTRACT_JSON = {
    "version": "1.0.0",
    "apiVersion": "v3.1.0",
    "kind": "DataContract",
    "id": "Bank_contract_001",
    "name": "BANK_transaction_contract",
    "status": "active",
    "domain": "Accounting and Finance: Financial Reporting",
    "tenant": "banking_department",
    "servers": [
        {
            "server": "banking-db",
            "type": "db2",
            "description": "DB2 production database for client accounts",
            "environment": "prod",
            "host": "169.44.151.75",
            "port": 50000,
            "database": "BANK",
            "schema": "BANK1",
            "customProperties": [
                {
                    "property": "database",
                    "value": "BANK"
                },
                {
                    "property": "schema",
                    "value": "BANK1"
                }
            ]
        }
    ],
    "dataProduct": "BankingDataProduct",
    "schema": [
        {
            "name": "BANK_CLIENTS",
            "physicalName": "BANK1/BANK_CLIENTS",
            "physicalType": "table",
            "logicalType": "object",
            "quality": [
                {
                    "name": "table_row_count",
                    "type": "sql",
                    "query": "SELECT * FROM BANK1.BANK_CLIENTS;",
                    "mustBe": 5112,
                    "dimension": "completeness"
                },
                {
                    "name": "Marital status inconsistent with age",
                    "type": "sql",
                    "query": "SELECT AGE, MARITAL_STATUS FROM BANK1.BANK_CLIENTS WHERE AGE < 16 AND MARITAL_STATUS IN ('married','divorced','widowed');",
                    "mustBeLessThan": 5
                },
                {
                    "name": "Contact preference but no phone number",
                    "type": "sql",
                    "query": "SELECT * FROM BANK1.BANK_CLIENTS WHERE REGEXP_LIKE(PHONE1, '[0-9]');",
                    "dimension": "conformity",
                    "mustBeLessThan": 5220
                }
            ],
            "properties": [
                {
                    "name": "ACCOUNT_ID",
                    "physicalName": "ACCOUNT_ID",
                    "logicalType": "string",
                    "quality": [
                        {
                            "name": "Null Value Check for CCN",
                            "type": "sql",
                            "query": "SELECT * FROM BANK1.BANK_CLIENTS WHERE CCN IS NULL;",
                            "dimension": "accuracy",
                            "mustBeGreaterThan": 200
                        },
                        {
                            "name": "Missing Values for Customer IDs",
                            "type": "library",
                            "metric": "missingValues",
                            "arguments": {
                                "missingValues": [
                                    "",
                                    "n/a",
                                    "N/A",
                                    "null",
                                    "NULL"
                                ]
                            },
                            "mustBeLessThan": 5
                        },
                        {
                            "name": "Duplicate customer IDs via library check",
                            "type": "library",
                            "metric": "duplicateValues",
                            "mustBe": 2
                        }
                    ],
                    "primaryKey": False,
                    "unique": True,
                    "required": True
                },
                {
                    "name": "ZIP",
                    "physicalName": "ZIP",
                    "logicalType": "string",
                    "quality": [
                        {
                            "name": "Invalid ZIP format",
                            "type": "sql",
                            "query": "SELECT ZIP FROM BANK1.BANK_CLIENTS WHERE ZIP IS NOT NULL AND NOT REGEXP_LIKE(TRIM(ZIP),'^[0-9]{5}$');",
                            "mustBeLessThan": 3005
                        },
                        {
                            "name": "Invalid ZIP format via Library check",
                            "type": "library",
                            "metric": "invalidValues",
                            "arguments": {
                                "pattern": "^[0-9]{5}$"
                            },
                            "mustBeLessThan": 2995
                        }
                    ],
                    "primaryKey": False,
                    "unique": True,
                    "required": True
                },
                {
                    "name": "AGE",
                    "physicalName": "AGE",
                    "logicalType": "string",
                    "quality": [
                        {
                            "name": "Implausible customer ages",
                            "type": "sql",
                            "query": "SELECT AGE FROM BANK1.BANK_CLIENTS WHERE AGE IS NULL OR AGE < 18 OR AGE > 100;",
                            "mustBeLessThan": 389
                        }
                    ],
                    "primaryKey": False,
                    "unique": True,
                    "required": True
                },
                {
                    "name": "EMAIL",
                    "physicalName": "EMAIL",
                    "logicalType": "string",
                    "quality": [
                        {
                            "name": "Invalid email address format",
                            "type": "sql",
                            "query": "SELECT EMAIL FROM BANK1.BANK_CLIENTS WHERE EMAIL IS NOT NULL AND NOT REGEXP_LIKE(TRIM(EMAIL),'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}$');",
                            "mustBeLessThan": 5
                        }
                    ],
                    "primaryKey": False,
                    "unique": True,
                    "required": True
                },
                {
                    "name": "GENDER",
                    "physicalName": "GENDER",
                    "logicalType": "string",
                    "quality": [
                        {
                            "name": "Invalid gender",
                            "type": "sql",
                            "query": "SELECT GENDER FROM BANK1.BANK_CLIENTS WHERE GENDER NOT IN ('L','F');",
                            "mustBeLessThan": 3540
                        },
                        {
                            "name": "Invalid gender via library check",
                            "type": "library",
                            "metric": "invalidValues",
                            "arguments": {
                                "validValues": [
                                    "M",
                                    "B"
                                ]
                            },
                            "mustBeLessThan": 5119
                        }
                    ],
                    "primaryKey": False,
                    "unique": True,
                    "required": True
                },
                {
                    "name": "MARITAL_STATUS",
                    "physicalName": "MARITAL_STATUS",
                    "logicalType": "string",
                    "quality": [
                        {
                            "name": "Invalid marital status codes",
                            "type": "sql",
                            "query": "SELECT MARITAL_STATUS FROM BANK1.BANK_CLIENTS WHERE MARITAL_STATUS NOT IN ('single','married','divorced','separated','unknown');",
                            "mustBeBetween": [
                                765,
                                890
                            ]
                        }
                    ],
                    "primaryKey": False,
                    "unique": True,
                    "required": True
                }
            ]
        }
    ],
    "customProperties": [
        {
            "property": "connectionIds",
            "value": [
                CONNECTION_ID
            ]
        }
    ]
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _provider() -> DataContractsProvider:
    config = ProviderConfig(url=CPD_URL, auth_token=BEARER_TOKEN)
    return DataContractsProvider(config)


def _run(label: str, fn):
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print(f"{'=' * 60}")
    try:
        fn()
        print(f"  ✓ PASSED")
    except Exception as exc:
        print(f"  ✗ FAILED: {exc}")
        traceback.print_exc()


# ===========================================================================
# PROJECT-SCOPED EXAMPLES
# ===========================================================================

def validate_project_data_contract():
    """POST /data_quality/v4/projects/{project_id}/data_contracts_validation"""
    provider = _provider()
    body = DataContractValidationRequest(data_contract_content=SAMPLE_CONTRACT_YAML)
    result = provider.validate_project_data_contract(PROJECT_ID, body)
    print(f"  valid={result.valid}  error_count={result.error_count}")
    if not result.valid:
        for err in result.errors:
            print(f"    - [{err.type}] {err.property}: {err.message}")


def create_project_data_contract_yaml():
    """POST /data_quality/v4/projects/{project_id}/data_contracts  (YAML body)"""
    global _created_project_contract_id
    provider = _provider()
    body = DataContractPrototypeYaml(
        name="Smoke_Test_Project_Contract_YAML",
        contract_yaml=SAMPLE_CONTRACT_YAML,
    )
    contract = provider.create_project_data_contract(PROJECT_ID, body)
    _created_project_contract_id = contract.id
    print(f"  created id={contract.id}  name={contract.name}")


def create_project_data_contract_json():
    """POST /data_quality/v4/projects/{project_id}/data_contracts  (JSON body)"""
    provider = _provider()
    body = DataContractPrototypeJson(
        name="Smoke_Test_Project_Contract_JSON",
        contract_json=SAMPLE_CONTRACT_JSON,
    )
    contract = provider.create_project_data_contract(PROJECT_ID, body)
    print(f"  created id={contract.id}  name={contract.name}")
    # Clean up immediately so we don't litter the project
    if contract.id:
        provider.delete_project_data_contracts(PROJECT_ID, data_contract_ids=contract.id)
        print(f"  cleaned up id={contract.id}")


def list_project_data_contracts():
    """GET /data_quality/v4/projects/{project_id}/data_contracts"""
    provider = _provider()
    result = provider.list_project_data_contracts(PROJECT_ID, limit=5)
    print(f"  total_count={result.total_count}  returned={len(result.data_contracts)}")
    for dc in result.data_contracts:
        print(f"    id={dc.id}  name={dc.name}")


def get_project_data_contract():
    """GET /data_quality/v4/projects/{project_id}/data_contracts/{id}"""
    if not _created_project_contract_id:
        print("  SKIPPED — no contract created yet (run create first)")
        return
    provider = _provider()
    contract = provider.get_project_data_contract(PROJECT_ID, _created_project_contract_id)
    print(f"  id={contract.id}  name={contract.name}")


def replace_project_data_contract():
    """PUT /data_quality/v4/projects/{project_id}/data_contracts/{id}"""
    if not _created_project_contract_id:
        print("  SKIPPED — no contract created yet (run create first)")
        return
    provider = _provider()
    updated_yaml = SAMPLE_CONTRACT_YAML.replace(
        "name: BANK_transaction_contract",
        "name: BANK_transaction_contract_updated",
    )
    body = DataContractPrototypeYaml(
        name="Smoke_Test_Project_Contract_YAML",
        contract_yaml=updated_yaml,
    )
    contract = provider.replace_project_data_contract(
        PROJECT_ID, _created_project_contract_id, body
    )
    print(f"  id={contract.id}  name={contract.name}")


def upload_project_data_contract_file():
    """POST /data_quality/v4/projects/{project_id}/data_contracts_upload"""
    provider = _provider()
    file_bytes = SAMPLE_CONTRACT_YAML.encode()
    contract = provider.upload_project_data_contract_file(
        PROJECT_ID,
        io.BytesIO(file_bytes),
        name="Smoke_Test_Upload_Project",
    )
    print(f"  id={contract.id}  name={contract.name}")
    # Clean up
    if contract.id:
        provider.delete_project_data_contracts(PROJECT_ID, data_contract_ids=contract.id)
        print(f"  cleaned up id={contract.id}")


def test_project_data_contract():
    """POST /data_quality/v4/projects/{project_id}/data_contracts/{id}/test  (Internal)"""
    if not _created_project_contract_id:
        print("  SKIPPED — no contract created yet (run create first)")
        return
    provider = _provider()
    body = DataContractTestRequest(
        retain_dq_objects=False,
    )
    try:
        result = provider.test_project_data_contract(
            PROJECT_ID, _created_project_contract_id, body
        )
        print(f"  test_run_id={result.id}  status={result.status}")
    except ValueError as exc:
        print(f"  SKIPPED (server pre-condition not met): {exc}")


def list_project_data_contract_test_results():
    """GET /data_quality/v4/projects/{project_id}/data_contracts/{id}/test_results  (Internal)"""
    if not _created_project_contract_id:
        print("  SKIPPED — no contract created yet (run create first)")
        return
    provider = _provider()
    try:
        result = provider.list_project_data_contract_test_results(
            PROJECT_ID, _created_project_contract_id
        )
        print(f"  test_result_count={len(result.test_results)}")
        for r in result.test_results:
            print(f"    run_id={r.id}  status={r.status}")
    except ValueError as exc:
        # 404 is returned when no test runs exist yet — not an SDK bug.
        print(f"  SKIPPED (no test results yet): {exc}")


def get_project_data_contract_test_result():
    """GET /data_quality/v4/projects/{project_id}/data_contracts/{id}/test_results/{run_id}  (Internal)"""
    if not _created_project_contract_id:
        print("  SKIPPED — no contract created yet (run create first)")
        return
    provider = _provider()
    # Fetch the list first to get a real run ID
    collection = provider.list_project_data_contract_test_results(
        PROJECT_ID, _created_project_contract_id
    )
    if not collection.test_results:
        print("  SKIPPED — no test runs found")
        return
    run_id = collection.test_results[0].id
    result = provider.get_project_data_contract_test_result(
        PROJECT_ID, _created_project_contract_id, run_id
    )
    print(f"  run_id={result.id}  status={result.status}  run_by={result.run_by}")


def delete_project_data_contract_test_results():
    """DELETE /data_quality/v4/projects/{project_id}/data_contracts/{id}/test_results  (Internal)"""
    if not _created_project_contract_id:
        print("  SKIPPED — no contract created yet (run create first)")
        return
    provider = _provider()
    provider.delete_project_data_contract_test_results(
        PROJECT_ID, _created_project_contract_id
    )
    print("  deleted all test results")


def delete_project_data_contracts():
    """DELETE /data_quality/v4/projects/{project_id}/data_contracts"""
    if not _created_project_contract_id:
        print("  SKIPPED — no contract to delete")
        return
    provider = _provider()
    provider.delete_project_data_contracts(
        PROJECT_ID, data_contract_ids=_created_project_contract_id
    )
    print(f"  deleted id={_created_project_contract_id}")


# ===========================================================================
# CATALOG-SCOPED EXAMPLES
# ===========================================================================

def validate_catalog_data_contract():
    """POST /data_quality/v4/catalogs/{catalog_id}/data_contracts_validation"""
    provider = _provider()
    body = DataContractValidationRequest(data_contract_content=SAMPLE_CONTRACT_YAML)
    result = provider.validate_catalog_data_contract(CATALOG_ID, body)
    print(f"  valid={result.valid}  error_count={result.error_count}")
    if not result.valid:
        for err in result.errors:
            print(f"    - [{err.type}] {err.property}: {err.message}")


def create_catalog_data_contract():
    """POST /data_quality/v4/catalogs/{catalog_id}/data_contracts"""
    global _created_catalog_contract_id
    provider = _provider()
    body = DataContractPrototypeYaml(
        name="Smoke_Test_Catalog_Contract",
        contract_yaml=SAMPLE_CONTRACT_YAML,
    )
    contract = provider.create_catalog_data_contract(CATALOG_ID, body)
    _created_catalog_contract_id = contract.id
    print(f"  created id={contract.id}  name={contract.name}")


def list_catalog_data_contracts():
    """GET /data_quality/v4/catalogs/{catalog_id}/data_contracts"""
    provider = _provider()
    result = provider.list_catalog_data_contracts(CATALOG_ID, limit=5)
    print(f"  total_count={result.total_count}  returned={len(result.data_contracts)}")
    for dc in result.data_contracts:
        print(f"    id={dc.id}  name={dc.name}")


def get_catalog_data_contract():
    """GET /data_quality/v4/catalogs/{catalog_id}/data_contracts/{id}"""
    if not _created_catalog_contract_id:
        print("  SKIPPED — no catalog contract created yet (run create first)")
        return
    provider = _provider()
    contract = provider.get_catalog_data_contract(CATALOG_ID, _created_catalog_contract_id)
    print(f"  id={contract.id}  name={contract.name}")


def replace_catalog_data_contract():
    """PUT /data_quality/v4/catalogs/{catalog_id}/data_contracts/{id}"""
    if not _created_catalog_contract_id:
        print("  SKIPPED — no catalog contract created yet (run create first)")
        return
    provider = _provider()
    updated_yaml = SAMPLE_CONTRACT_YAML.replace(
        "name: BANK_transaction_contract",
        "name: BANK_transaction_contract_catalog_updated",
    )
    body = DataContractPrototypeYaml(
        name="Smoke_Test_Catalog_Contract",
        contract_yaml=updated_yaml,
    )
    contract = provider.replace_catalog_data_contract(
        CATALOG_ID, _created_catalog_contract_id, body
    )
    print(f"  id={contract.id}  name={contract.name}")


def upload_catalog_data_contract_file():
    """POST /data_quality/v4/catalogs/{catalog_id}/data_contracts_upload"""
    provider = _provider()
    file_bytes = SAMPLE_CONTRACT_YAML.encode()
    contract = provider.upload_catalog_data_contract_file(
        CATALOG_ID,
        io.BytesIO(file_bytes),
        name="Smoke_Test_Upload_Catalog",
    )
    print(f"  id={contract.id}  name={contract.name}")
    # Clean up
    if contract.id:
        provider.delete_catalog_data_contracts(CATALOG_ID, data_contract_ids=contract.id)
        print(f"  cleaned up id={contract.id}")


def delete_catalog_data_contracts():
    """DELETE /data_quality/v4/catalogs/{catalog_id}/data_contracts"""
    if not _created_catalog_contract_id:
        print("  SKIPPED — no catalog contract to delete")
        return
    provider = _provider()
    provider.delete_catalog_data_contracts(
        CATALOG_ID, data_contract_ids=_created_catalog_contract_id
    )
    print(f"  deleted id={_created_catalog_contract_id}")


# ===========================================================================
# RUNNER
# ===========================================================================

if __name__ == "__main__":
    print("\n" + "#" * 60)
    print("  DATA CONTRACTS EXAMPLES — PROJECT-SCOPED")
    print("#" * 60)

    _run("validate_project_data_contract", validate_project_data_contract)
    _run("create_project_data_contract (YAML)", create_project_data_contract_yaml)
    _run("create_project_data_contract (JSON)", create_project_data_contract_json)
    _run("list_project_data_contracts", list_project_data_contracts)
    _run("get_project_data_contract", get_project_data_contract)
    _run("replace_project_data_contract", replace_project_data_contract)
    _run("upload_project_data_contract_file", upload_project_data_contract_file)
    _run("test_project_data_contract [Internal]", test_project_data_contract)
    _run("list_project_data_contract_test_results [Internal]",
         list_project_data_contract_test_results)
    _run("get_project_data_contract_test_result [Internal]",
         get_project_data_contract_test_result)
    _run("delete_project_data_contract_test_results [Internal]",
         delete_project_data_contract_test_results)
    _run("delete_project_data_contracts", delete_project_data_contracts)

    print("\n" + "#" * 60)
    print("  DATA CONTRACTS EXAMPLES — CATALOG-SCOPED")
    print("#" * 60)

    _run("validate_catalog_data_contract", validate_catalog_data_contract)
    _run("create_catalog_data_contract", create_catalog_data_contract)
    _run("list_catalog_data_contracts", list_catalog_data_contracts)
    _run("get_catalog_data_contract", get_catalog_data_contract)
    _run("replace_catalog_data_contract", replace_catalog_data_contract)
    _run("upload_catalog_data_contract_file", upload_catalog_data_contract_file)
    _run("delete_catalog_data_contracts", delete_catalog_data_contracts)

    print("\n" + "#" * 60)
    print("  EXAMPLES COMPLETE")
    print("#" * 60 + "\n")
