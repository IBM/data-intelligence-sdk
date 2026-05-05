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

.. _odcs_generator_overview:

ODCS Generator Overview
=======================

The ODCS Generator module automates the creation of Open Data Contract Standard (ODCS) v3.1.0 compliant YAML files from enterprise data catalog metadata.

Architecture
------------

The module uses a modular architecture with catalog-specific clients and a common generator:

.. code-block:: text

    ┌─────────────────────────────────────────┐
    │         ODCS Generator Module           │
    ├─────────────────────────────────────────┤
    │                                         │
    │  ┌──────────────┐   ┌───────────────┐  │
    │  │   Collibra   │   │  Informatica  │  │
    │  │    Client    │   │     Client    │  │
    │  └──────┬───────┘   └───────┬───────┘  │
    │         │                   │          │
    │         └───────┬───────────┘          │
    │                 │                      │
    │         ┌───────▼────────┐             │
    │         │ ODCS Generator │             │
    │         └───────┬────────┘             │
    │                 │                      │
    │         ┌───────▼────────┐             │
    │         │  YAML Output   │             │
    │         └────────────────┘             │
    └─────────────────────────────────────────┘

Core Components
---------------

Catalog Clients
~~~~~~~~~~~~~~~

**CollibraClient**
   - REST API integration
   - GraphQL API for classifications
   - Asset, attribute, and relation extraction
   - Tag and classification support

**InformaticaClient**
   - REST API integration
   - Asset metadata extraction
   - Column schema discovery
   - System attribute handling

ODCS Generator
~~~~~~~~~~~~~~

The generator transforms catalog metadata into ODCS format:

1. **Metadata Extraction**: Fetch asset details from catalog
2. **Column Discovery**: Identify and extract column information
3. **Type Mapping**: Convert catalog types to ODCS types
4. **Classification Mapping**: Extract data classifications
5. **YAML Generation**: Create compliant ODCS YAML file

Data Type Mapping
-----------------

Logical Type Mapping
~~~~~~~~~~~~~~~~~~~~

Catalog types are mapped to ODCS logical types:

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Catalog Type
     - ODCS Logical Type
     - Description
   * - text, string, varchar
     - string
     - Text data
   * - whole number, int, integer
     - integer
     - Whole numbers
   * - decimal number, float, double
     - number
     - Decimal numbers
   * - date time, timestamp
     - timestamp
     - Date and time
   * - true/false, boolean
     - boolean
     - Boolean values
   * - geographical, geo
     - string
     - Geographic data

Physical Type Mapping
~~~~~~~~~~~~~~~~~~~~~

Physical types preserve database-specific information:

- ``VARCHAR(255)`` - Variable character with length
- ``DECIMAL(10,2)`` - Decimal with precision and scale
- ``NUMBER(18,4)`` - Numeric with precision and scale
- ``TIMESTAMP(6)`` - Timestamp with precision

Classification Support
----------------------

The generator extracts and maps data classifications:

**Collibra Classifications**
   - Extracted via GraphQL API
   - Mapped to ODCS classification field
   - Supports custom classification schemes

**Informatica Classifications**
   - Extracted from asset attributes
   - Mapped to ODCS tags and classifications
   - Supports data sensitivity labels

Common Classifications
~~~~~~~~~~~~~~~~~~~~~~

- **PII** - Personally Identifiable Information
- **PHI** - Protected Health Information
- **Confidential** - Confidential business data
- **Public** - Publicly available data
- **Internal** - Internal use only

ODCS Structure
--------------

Generated ODCS files follow this structure:

Contract Metadata
~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    id: unique-contract-id
    kind: DataContract
    apiVersion: v3.1.0
    domain: domain-name
    dataProduct: product-name
    version: 1.0.0
    name: contract-name
    status: active
    contractCreatedTs: 2026-04-16T06:00:00Z

Description Section
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    description:
      purpose: Purpose of the data
      authoritativeDefinitions:
        - type: collibra-asset
          url: https://collibra.com/asset/123
      limitations: Usage limitations
      usage: Intended usage

Schema Section
~~~~~~~~~~~~~~

.. code-block:: yaml

    schema:
      - id: table-id
        name: table_name
        physicalName: PHYSICAL_TABLE_NAME
        physicalType: table
        description: Table description
        tags:
          - customer-data
          - analytics
        columns:
          - id: column-id
            name: column_name
            logicalType: string
            physicalType: VARCHAR(255)
            description: Column description
            isNullable: false
            isPrimaryKey: false
            classification: PII
            tags:
              - sensitive

Quality Section
~~~~~~~~~~~~~~~

.. code-block:: yaml

    quality:
      - id: rule-001
        name: completeness-check
        type: completeness
        column: customer_id
        dimension: completeness
        threshold: 0.95

Service Level Agreement
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    sla:
      interval: daily
      uptime: 99.9%
      responseTime: 100ms

Best Practices
--------------

**Validate Catalog Connectivity**

.. code-block:: python

    try:
        client = CollibraClient(base_url, username, password)
        # Test connection
        asset = client.get_asset("test-id")
    except Exception as e:
        print(f"Connection failed: {e}")

**Handle Missing Metadata**

.. code-block:: python

    # Provide defaults for missing fields
    odcs_data = generator.generate_odcs(
        asset_id,
        defaults={
            'dataProduct': 'Default Product',
            'version': '1.0.0',
            'status': 'draft'
        }
    )

**Batch Processing**

.. code-block:: python

    asset_ids = ['id1', 'id2', 'id3']
    
    for asset_id in asset_ids:
        try:
            odcs_data = generator.generate_odcs(asset_id)
            generator.save_to_yaml(odcs_data, f"{asset_id}-odcs.yaml")
        except Exception as e:
            print(f"Failed for {asset_id}: {e}")

**Customize Output**

.. code-block:: python

    # Generate ODCS
    odcs_data = generator.generate_odcs(asset_id)
    
    # Customize before saving
    odcs_data['dataProduct'] = 'My Data Product'
    odcs_data['version'] = '2.0.0'
    odcs_data['quality'] = [
        {
            'id': 'custom-rule',
            'name': 'Custom Quality Rule',
            'type': 'accuracy'
        }
    ]
    
    # Save customized ODCS
    generator.save_to_yaml(odcs_data, 'custom-odcs.yaml')

Error Handling
--------------

Common errors and solutions:

**Authentication Errors**

.. code-block:: python

    from requests.exceptions import HTTPError
    
    try:
        client = CollibraClient(url, username, password)
    except HTTPError as e:
        if e.response.status_code == 401:
            print("Invalid credentials")
        elif e.response.status_code == 403:
            print("Insufficient permissions")

**Asset Not Found**

.. code-block:: python

    try:
        odcs_data = generator.generate_odcs(asset_id)
    except ValueError as e:
        print(f"Asset not found: {e}")

**Missing Columns**

.. code-block:: python

    odcs_data = generator.generate_odcs(asset_id)
    
    if not odcs_data.get('schema', [{}])[0].get('columns'):
        print("Warning: No columns found for asset")

Requirements
------------

- Python 3.8 or higher
- requests >= 2.32.4
- pyyaml >= 5.4.0
- urllib3 >= 2.6.3
- python-dateutil >= 2.5.3

See Also
--------

- :ref:`odcs_generator_collibra` - Collibra integration
- :ref:`odcs_generator_informatica` - Informatica integration
- :ref:`odcs_generator_examples` - Code examples
- :ref:`api_odcs_generator` - API reference

.. Made with Bob
