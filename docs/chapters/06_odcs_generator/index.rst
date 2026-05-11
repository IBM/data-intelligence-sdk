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

.. _odcs_generator:

ODCS Generator
==============

Tools to automatically generate ODCS (Open Data Contract Standard) v3.1.0 compliant YAML files from data catalog metadata.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   collibra_integration
   informatica_integration
   examples

Overview
--------

The ``odcs_generator`` module provides automated generation of Open Data Contract Standard (ODCS) files from enterprise data catalogs. It extracts metadata from catalog systems and transforms it into standardized data contracts.

Key Features
------------

**Multi-Catalog Support**
   Generate ODCS files from Collibra and Informatica CDGC data catalogs.

**Automatic Metadata Extraction**
   Fetch asset details, attributes, relations, and classifications automatically.

**Column Discovery**
   Automatically discover and document table columns through catalog relations.

**Data Type Mapping**
   Intelligent mapping of catalog data types to ODCS standard types.

**Classification Support**
   Extract and include data classifications and sensitivity labels.

**ODCS v3.1.0 Compliance**
   Generate fully compliant ODCS YAML files ready for use.

Quick Start
-----------

**Collibra Integration**

.. code-block:: python

    from wxdi.odcs_generator.generate_odcs_from_collibra import CollibraClient, ODCSGenerator

    # Initialize client
    client = CollibraClient(
        base_url="https://your-instance.collibra.com",
        username="your_username",
        password="your_password"
    )

    # Create generator
    generator = ODCSGenerator(client)

    # Generate ODCS
    odcs_data = generator.generate_odcs("asset-id")
    
    # Save to file
    generator.save_to_yaml(odcs_data, "output.yaml")

**Informatica Integration**

.. code-block:: python

    from wxdi.odcs_generator.generate_odcs_from_informatica import InformaticaClient, ODCSGenerator

    # Initialize client
    client = InformaticaClient(
        base_url="https://your-informatica-instance.com",
        username="your_username",
        password="your_password"
    )

    # Create generator
    generator = ODCSGenerator(client)

    # Generate ODCS
    odcs_data = generator.generate_odcs("asset-id")

Use Cases
---------

**Data Contract Automation**
   Automatically generate data contracts from existing catalog metadata.

**Catalog Migration**
   Export catalog metadata to standardized ODCS format for migration.

**Documentation Generation**
   Create comprehensive data documentation from catalog assets.

**Compliance Reporting**
   Generate standardized contracts for compliance and governance.

**Data Product Onboarding**
   Accelerate data product creation with automated contract generation.

Supported Catalogs
------------------

**Collibra**
   - Asset metadata extraction
   - Column discovery via relations
   - Data classifications via GraphQL
   - Tag integration
   - Custom attributes

**Informatica CDGC**
   - Asset metadata extraction
   - Column schema discovery
   - System attributes
   - Technical metadata
   - Business glossary terms

What is ODCS?
-------------

The Open Data Contract Standard (ODCS) is an open-source specification for defining data contracts. It provides:

- **Standardized Format**: Common structure for data contracts across organizations
- **Schema Definition**: Detailed column-level metadata and constraints
- **Quality Rules**: Data quality expectations and validation rules
- **Service Level Agreements**: Performance and availability commitments
- **Governance**: Data ownership, stewardship, and compliance information

ODCS v3.1.0 Structure
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    id: unique-contract-id
    kind: DataContract
    apiVersion: v3.1.0
    domain: domain-name
    dataProduct: product-name
    version: 1.0.0
    name: contract-name
    status: active
    description:
      authoritativeDefinitions:
        - type: source-system
          url: source-url
    schema:
      - id: table-id
        name: table-name
        columns:
          - id: column-id
            name: column-name
            logicalType: string
            physicalType: VARCHAR(255)
            description: column description
            classification: PII
    quality:
      - id: rule-id
        name: rule-name
        type: completeness
        column: column-name

Next Steps
----------

- :ref:`odcs_generator_collibra` - Collibra integration guide
- :ref:`odcs_generator_informatica` - Informatica integration guide
- :ref:`odcs_generator_examples` - Complete code examples
- :ref:`api_odcs_generator` - API reference

.. Made with Bob
