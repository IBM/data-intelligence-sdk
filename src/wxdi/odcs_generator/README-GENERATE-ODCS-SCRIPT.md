<!--
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
-->

# Generate ODCS - Script Documentation

## Overview

The `odcs_generator` module provides tools to automatically generate ODCS (Open Data Contract Standard) v3.1.0 compliant YAML files from data catalog metadata. It supports multiple data catalog sources:

- **Collibra**: Extracts table/view definitions, column schemas, data types, classifications, and custom properties
- **Informatica CDGC**: Fetches asset metadata including table definitions, column schemas, and system attributes

**Scripts:**
- `wxdi.odcs_generator.generate_odcs_from_collibra` - Generate ODCS from Collibra assets
- `wxdi.odcs_generator.generate_odcs_from_informatica` - Generate ODCS from Informatica CDGC assets

---

# Table of Contents

1. [Collibra Integration](#collibra-integration)
2. [Informatica Integration](#informatica-integration)
3. [Common Features](#common-features)
4. [Related Documentation](#related-documentation)

---

# Collibra Integration

## Location
`wxdi.odcs_generator.generate_odcs_from_collibra`

## Features

- ✅ **Automatic Metadata Extraction**: Fetches asset details, attributes, and relations from Collibra REST API
- ✅ **Column Discovery**: Automatically discovers columns through asset relations
- ✅ **Data Type Mapping**: Maps Collibra logical and technical data types to ODCS standards
- ✅ **Classification Support**: Extracts data classifications using Collibra GraphQL API
- ✅ **Tag Integration**: Includes Collibra tags at both asset and column levels
- ✅ **Custom Properties**: Preserves Collibra attributes as custom properties
- ✅ **ODCS v3.1.0 Compliance**: Generates fully compliant ODCS YAML files

## Requirements

### Python Dependencies

Install all dependencies from the project root:

```bash
pip install -r requirements.txt
```

**Required packages:**
- `requests` >= 2.32.4 - HTTP library for Collibra API calls
- `pyyaml` >= 5.4.0 - YAML file generation
- `urllib3` >= 2.6.3 - HTTP client library
- `python_dateutil` >= 2.5.3 - Date/time utilities
- `ibm_cloud_sdk_core` >= 3.16.7 - IBM Cloud SDK core

### Collibra Access

- Valid Collibra instance URL
- User account with read access to assets, attributes, and relations
- Network connectivity to Collibra REST API and GraphQL endpoints

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd data-product-python-sdk
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables (see Configuration section)

## Directory Structure

```
data-product-python-sdk/
├── odcs_generator/
│   ├── __init__.py
│   ├── generate_odcs_from_collibra.py    # Main script
│   └── README-GENERATE-ODCS-SCRIPT.md    # This file
├── examples/
│   ├── __init__.py
│   └── odcs_generator_example.py         # Usage examples
├── requirements.txt                       # Python dependencies
└── ...
```

## Configuration

### Environment Variables

Set the following environment variables before running the script:

```bash
export COLLIBRA_URL="https://your-instance.collibra.com"
export COLLIBRA_USERNAME="myuser"
export COLLIBRA_PASSWORD="mypassword"
```

**Alternative**: Pass credentials via command-line arguments (see Usage section)

### Collibra Permissions Required

The user account needs the following permissions:
- Read access to assets
- Read access to attributes
- Read access to relations
- Access to GraphQL API (for classifications)
- Read access to tags

## Usage

### Command-Line Usage

Run the script directly from the `odcs_generator` directory:

```bash
python odcs_generator/generate_odcs_from_collibra.py <asset_id>
```

**Example:**
```bash
python odcs_generator/generate_odcs_from_collibra.py 019a57f9-62d2-7aa0-9f22-4fa2cea1180b
```

This generates a file named `<asset-name>-odcs.yaml` in the current directory.

### Programmatic Usage

Import and use the module in your Python code:

```python
from odcs_generator import CollibraClient, ODCSGenerator

# Initialize client
client = CollibraClient(
    base_url="https://your-instance.collibra.com",
    username="your_username",
    password="your_pswd"
)

# Create generator
generator = ODCSGenerator(client)

# Generate ODCS
odcs_data = generator.generate_odcs("asset_id")
```

See `examples/odcs_generator_example.py` for complete examples.

### Command-Line Options

```bash
python odcs_generator/generate_odcs_from_collibra.py <asset_id> [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `asset_id` | Collibra asset ID (required) | - |
| `-o, --output` | Output YAML file path | `<asset-name>-odcs.yaml` |
| `--url` | Collibra base URL | `$COLLIBRA_URL` |
| `-u, --username` | Collibra username | `$COLLIBRA_USERNAME` |
| `-p, --password` | Collibra password | `$COLLIBRA_PASSWORD` |
| `-h, --help` | Show help message | - |

### Examples

**Generate with custom output file:**
```bash
python odcs_generator/generate_odcs_from_collibra.py 019a57f9-62d2-7aa0-9f22-4fa2cea1180b -o my-contract.yaml
```

**Pass credentials via command line:**
```bash
python odcs_generator/generate_odcs_from_collibra.py 019a57f9-62d2-7aa0-9f22-4fa2cea1180b \
  --url https://acme.collibra.com \
  -u myuser \
  -p mypassword
```

**Using environment variables:**
```bash
export COLLIBRA_URL="https://acme.collibra.com"
export COLLIBRA_USERNAME="myuser"
export COLLIBRA_PASSWORD="mypassword"

python odcs_generator/generate_odcs_from_collibra.py 019a57f9-62d2-7aa0-9f22-4fa2cea1180b
```

## Example Scripts

The `examples/` directory contains comprehensive usage examples:

### Basic Usage Example
```bash
python examples/odcs_generator_example.py
```

This example demonstrates:
- Connecting to Collibra using environment variables
- Generating ODCS from a single asset
- Saving the output to a YAML file

### Custom Processing Example
Shows how to:
- Generate ODCS programmatically
- Customize contract metadata (dataProduct, version, name)
- Add quality rules
- Update server configuration

### Batch Processing Example
Demonstrates:
- Processing multiple assets in a loop
- Error handling for failed assets
- Generating summary reports

See `examples/odcs_generator_example.py` for complete code and additional examples.

## How It Works

### 1. Asset Metadata Extraction

The script fetches the following from Collibra:

- **Asset Details**: Name, display name, type, domain, creation date
- **Attributes**: All custom attributes (Description, Data Type, etc.)
- **Relations**: Source and target relations to discover columns
- **Tags**: Direct tags assigned to the asset
- **Classifications**: Data classifications via GraphQL API

### 2. Column Discovery

Columns are discovered through asset relations:
- Processes both source and target relations
- Identifies assets with "column" in their type name
- Fetches column attributes and classifications
- Deduplicates columns by name

### 3. Data Type Mapping

**Logical Types** (Collibra → ODCS):
- `text` → `string`
- `whole number` → `integer`
- `decimal number` → `number`
- `date time` → `timestamp`
- `true/false` → `boolean`
- `geographical` → `string`

**Physical Types** (with size/precision/scale):
- `VARCHAR(255)`
- `DECIMAL(10,2)`
- `NUMBER(18,4)`

### 4. ODCS Generation

Creates a complete ODCS v3.1.0 structure:

```yaml
id: <asset-id>
kind: DataContract
apiVersion: v3.1.0
domain: <domain-name>
dataProduct: Sample data product
version: 1.0.0
name: Sample contract
status: active
contractCreatedTs: <iso-timestamp>
description:
  authoritativeDefinitions:
    - type: collibra-asset
      url: <collibra-asset-url>
tags: [...]
schema:
  - id: <asset-id>
    name: <asset-name>
    physicalName: <display-name>
    physicalType: table|view
    description: <description>
    properties: [...]
servers:
  - id: <generated-id>
    server: CONFIGURE_SERVER_HOSTNAME  # ⚠️ Manual config required
    type: DEFINE_SERVER_TYPE  # ⚠️ Manual config required
```

### 5. Manual Configuration Comments

The script adds inline comments to guide manual configuration:

```yaml
servers:
  # ============================================
  # ⚠️  MANUAL CONFIGURATION REQUIRED
  # ============================================
  # Please update the following fields:
  - id: server-79f2fd7b
    server: CONFIGURE_SERVER_HOSTNAME  # ⚠️ UPDATE: e.g., prod.snowflake.acme.com
    type: DEFINE_SERVER_TYPE  # ⚠️ UPDATE: e.g., snowflake, postgres, bigquery, redshift
```

## Output Structure

### Generated ODCS File

The script generates a YAML file with the following structure:

```yaml
id: <asset-id>
kind: DataContract
apiVersion: v3.1.0
domain: <domain>
dataProduct: <product-name>
version: 1.0.0
name: <contract-name>
status: active
contractCreatedTs: <timestamp>
description:
  authoritativeDefinitions:
    - type: collibra-asset
      url: <collibra-url>
tags: [...]
schema:
  - id: <schema-id>
    name: <table-name>
    physicalName: <physical-name>
    physicalType: table|view
    description: <description>
    customProperties: [...]
    properties:
      - name: <column-name>
        physicalName: <physical-column-name>
        logicalType: string|integer|number|...
        physicalType: VARCHAR(255)|DECIMAL(10,2)|...
        description: <column-description>
        required: true|false
        primaryKey: true|false
        classification: <security-class>
        tags: [...]
servers:
  - id: <server-id>
    server: CONFIGURE_SERVER_HOSTNAME
    type: DEFINE_SERVER_TYPE
```

### Console Output

The script provides detailed progress information:

```
Connecting to Collibra at https://acme.collibra.com...
Generating ODCS for asset: 019a57f9-62d2-7aa0-9f22-4fa2cea1180b

=== Processing asset: 019a57f9-62d2-7aa0-9f22-4fa2cea1180b ===
Fetching asset details...
Fetching asset attributes...
Fetching asset relations (as source)...
Fetching asset relations (as target)...
Found 15 relations where asset is target
Extracting column information from all relations...
Total relations found: 20
  Found column (source): name='customer_id', type='Column'
  Found column (target): name='transaction_date', type='Column'
Found 12 unique columns from relations

Writing ODCS to customer-transactions-odcs.yaml...
✓ Successfully generated ODCS file: customer-transactions-odcs.yaml
```

## Collibra Attribute Mapping

### Asset-Level Attributes

| Collibra Attribute | ODCS Field | Notes |
|-------------------|------------|-------|
| Name | `schema.name` | Full asset name |
| Display Name | `schema.physicalName` | Physical name |
| Description | `schema.description` | Asset description |
| Domain | `domain` | Domain name |
| Created On | `contractCreatedTs` | ISO timestamp |
| Table Type | `schema.physicalType` | table or view |
| Tags | `tags` | Array of tag names |
| Other attributes | `schema.customProperties` | Preserved as custom properties |

### Column-Level Attributes

| Collibra Attribute | ODCS Field | Notes |
|-------------------|------------|-------|
| Name / Display Name | `properties.name` | Column name |
| Original Name / Physical Name | `properties.physicalName` | Physical column name |
| Description / Definition | `properties.description` | Column description |
| Data Type | `properties.logicalType` | Mapped to ODCS types |
| Technical Data Type | `properties.physicalType` | With size/precision/scale |
| Is Nullable / Nullable | `properties.required` | Boolean |
| Is Primary Key / Primary Key | `properties.primaryKey` | Boolean |
| Security Classification | `properties.classification` | Security class |
| PII / Personally Identifiable Information | `properties.tags` | Adds "PII" tag |
| Size / Length | `properties.physicalType` | Appended to type |
| Precision | `properties.physicalType` | For numeric types |
| Scale / Number Of Fractional Digits | `properties.physicalType` | For numeric types |
| Classifications (GraphQL) | `properties.tags` | As `data_classification:*` |
| Tags | `properties.tags` | Column-level tags |

## Error Handling

### Common Errors

**1. Missing Environment Variables**
```
Error: Collibra URL is required. Set COLLIBRA_URL environment variable or use --url
```
**Solution**: Set required environment variables or pass via command line

**2. Authentication Failure**
```
Error: HTTP 401 - Unauthorized
```
**Solution**: Verify username and password are correct

**3. Asset Not Found**
```
Error: HTTP 404 - Asset not found
```
**Solution**: Verify the asset ID exists and you have access

**4. Network Issues**
```
Error: Connection refused
```
**Solution**: Check network connectivity and Collibra URL

### Warnings

The script may display warnings for non-critical issues:

```
Warning: Could not fetch tags: <error-message>
Warning: No columns found in Collibra.
```

These warnings indicate missing data but don't prevent ODCS generation.

## Validation

After generating the ODCS file, validate it against the ODCS specification:

1. **Manual Review**: Check the generated YAML for completeness
2. **YAML Syntax**: Ensure valid YAML format
3. **ODCS Compliance**: Verify against ODCS v3.1.0 specification
4. **Required Fields**: Confirm all mandatory fields are present
5. **Server Configuration**: Complete fields marked with ⚠️ warnings

## Limitations

## Script-Specific Limitations

1. **Server Connection Details**: Collibra doesn't store actual server hostnames or connection strings
2. **Server Type**: May need manual verification/correction
3. **Additional Server Parameters**: Account, environment, roles, etc.
4. **Contract Metadata**: Data product name, version, contract name (uses defaults)
5. **Quality Rules**: Not extracted from Collibra
6. **SLA Terms**: Not available in Collibra metadata
7. **Stakeholder Information**: Requires manual addition

### Collibra-Specific Limitations

- Column discovery depends on proper relation setup in Collibra
- Data type mapping may need adjustment for custom types
- Classification extraction requires GraphQL API access
- Some attributes may have different names in your Collibra instance

## Customization

### Modifying Attribute Mappings

Edit the `_build_attribute_map()` method to change which Collibra attributes are extracted:

```python
# Add custom attribute mapping
custom_attr = attr_map.get('Your Custom Attribute', '')
```

### Changing Data Type Mappings

Update the `LOGICAL_TYPE_MAPPING` dictionary:

```python
LOGICAL_TYPE_MAPPING = {
    'your_custom_type': 'odcs_type',
    # ... existing mappings
}
```

### Adding Custom Properties

Modify the `_extract_custom_properties()` method to include/exclude specific attributes:

```python
EXCLUDED_ATTRIBUTES = {'Description', 'Your Excluded Attr'}
```

## Best Practices

1. **Verify Asset ID**: Ensure you're using the correct Collibra asset ID
2. **Check Relations**: Verify columns are properly related to tables in Collibra
3. **Review Output**: Always review the generated YAML before using
4. **Manual Configuration**: Complete all fields marked with ⚠️ warnings
5. **Validate**: Validate the YAML before finalizing

## Troubleshooting

### No Columns Generated

**Problem**: Schema has no properties (columns)

**Possible Causes**:
- Columns not properly related to table in Collibra
- Relation types not recognized
- Column assets have incorrect type

**Solution**:
1. Check Collibra relations for the asset

---

# Informatica Integration

## Overview

`generate_odcs_from_informatica.py` is a Python script that automatically generates ODCS (Open Data Contract Standard) v3.1.0 compliant YAML files from Informatica CDGC (Cloud Data Governance and Catalog) asset metadata. It extracts table definitions, column schemas, data types, and system attributes from Informatica and transforms them into standardized data contracts.

**Location**: `odcs_generator/generate_odcs_from_informatica.py`

## Features

- ✅ **Automatic Metadata Extraction**: Fetches asset details from Informatica CDGC REST API
- ✅ **Column Discovery**: Automatically discovers columns through asset hierarchy
- ✅ **Concurrent Processing**: Fetches column details in parallel for better performance
- ✅ **System Attributes**: Preserves Informatica system attributes as custom properties
- ✅ **Server Type Detection**: Automatically maps Informatica resource types to ODCS server types
- ✅ **ODCS v3.1.0 Compliance**: Generates fully compliant ODCS YAML files

## Requirements

### Python Dependencies

```bash
pip install requests pyyaml
```

**Required packages:**
- `requests` >= 2.25.0 - HTTP library for Informatica API calls
- `pyyaml` >= 5.4.0 - YAML file generation

### Informatica Access

- Valid Informatica CDGC instance URL
- User account with read access to assets and metadata
- Network connectivity to Informatica CDGC REST API and Identity Service endpoints

## Configuration

### Environment Variables

Set the following environment variables before running the script:

```bash
export INFORMATICA_CDGC_URL="https://cdgc.dm-us.informaticacloud.com"
export INFORMATICA_USERNAME="myuser"
export INFORMATICA_PASSWORD="mypassword"
```

**Alternative**: Pass credentials via command-line arguments (see Usage section)

### Informatica Permissions Required

The user account needs the following permissions:
- Read access to CDGC assets
- Access to asset metadata and attributes
- Access to Identity Service for authentication
- Read access to asset hierarchy (columns)

## Usage

### Basic Usage

```bash
python odcs_generator/generate_odcs_from_informatica.py <asset_id>
```

**Example:**
```bash
python odcs_generator/generate_odcs_from_informatica.py 1b5fc805-252d-4ba2-bd90-e943103e411b
```

This generates a file named `<asset-name>-odcs.yaml` in the current directory.

### Command-Line Options

```bash
python odcs_generator/generate_odcs_from_informatica.py <asset_id> [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `asset_id` | Informatica asset ID (required) | - |
| `-o, --output` | Output YAML file path | `<asset-name>-odcs.yaml` |
| `--cdgc-url` | Informatica CDGC URL | `$INFORMATICA_CDGC_URL` |
| `-u, --username` | Informatica username | `$INFORMATICA_USERNAME` |
| `-p, --password` | Informatica password | `$INFORMATICA_PASSWORD` |
| `-h, --help` | Show help message | - |

### Examples

**Generate with custom output file:**
```bash
python odcs_generator/generate_odcs_from_informatica.py 1b5fc805-252d-4ba2-bd90-e943103e411b -o my-contract.yaml
```

**Pass credentials via command line:**
```bash
python odcs_generator/generate_odcs_from_informatica.py 1b5fc805-252d-4ba2-bd90-e943103e411b \
  --cdgc-url https://cdgc.dm-us.informaticacloud.com \
  -u myuser \
  -p mypassword
```

**Using environment variables:**
```bash
export INFORMATICA_CDGC_URL="https://cdgc.dm-us.informaticacloud.com"
export INFORMATICA_USERNAME="myuser"
export INFORMATICA_PASSWORD="mypswrd"

python odcs_generator/generate_odcs_from_informatica.py 1b5fc805-252d-4ba2-bd90-e943103e411b
```

## How It Works

### 1. Authentication

The script performs a two-step authentication process:

1. **Session ID**: Obtains a session ID from Identity Service using username/password
2. **JWT Token**: Exchanges session ID for a JWT token used for API calls
3. **Token Caching**: Caches the JWT token to avoid repeated authentication

### 2. Asset Metadata Extraction

The script fetches the following from Informatica CDGC:

- **Asset Details**: Name, business name, type, resource type
- **System Attributes**: Schema, catalog source, row count, origin, timestamps
- **Hierarchy**: Column IDs from asset hierarchy
- **Column Details**: Data types, length, scale, precision, nullable, primary key

### 3. Column Discovery

Columns are discovered through the asset hierarchy:
- Extracts column IDs from the `hierarchy` array
- Fetches detailed metadata for each column concurrently (up to 10 parallel requests)
- Sorts columns by position for correct ordering
- Handles missing or incomplete column data gracefully

### 4. Data Type Mapping

**Physical Types** (with size/precision/scale):
- `VARCHAR(255)`
- `DECIMAL(10,2)`
- `NUMBER(18,4)`
- `CHAR(10)`
- `TIMESTAMP`

The script automatically constructs physical types based on:
- Base data type from `com.infa.odin.models.relational.Datatype`
- Length from `com.infa.odin.models.relational.DatatypeLength`
- Scale from `com.infa.odin.models.relational.DatatypeScale`

### 5. Server Type Detection

Automatically maps Informatica resource types to ODCS server types:

| Informatica Resource Type | ODCS Server Type |
|---------------------------|------------------|
| SqlServer | sqlserver |
| Oracle | oracle |
| PostgreSQL | postgresql |
| MySQL | mysql |
| Snowflake | snowflake |
| Redshift | redshift |
| BigQuery | bigquery |
| Databricks | databricks |
| Synapse | synapse |
| DB2 | db2 |
| Hive | hive |
| Impala | impala |
| Teradata | custom |

### 6. ODCS Generation

Creates a complete ODCS v3.1.0 structure:

```yaml
id: <asset-id>
kind: DataContract
apiVersion: v3.1.0
domain: Sample Domain
dataProduct: Sample data product
version: 1.0.0
name: Sample contract
status: active
contractCreatedTs: <iso-timestamp>
description:
  authoritativeDefinitions:
    - type: informatica-asset
      url: <informatica-asset-url>
schema:
  - id: <asset-id>
    name: <table-name>
    physicalName: <schema>/<table-name>
    physicalType: Table
    description: <description>
    properties: [...]
customProperties: [...]
servers:
  - id: <generated-id>
    server: CONFIGURE_SERVER_HOSTNAME  # ⚠️ Manual config may be required
    type: <detected-type>  # Auto-detected from Informatica
    schema: <schema-name>  # Extracted from Informatica
```

### 7. Manual Configuration Comments

The script adds inline comments to guide manual configuration where needed:

```yaml
servers:
  # ============================================
  # ⚠️  MANUAL CONFIGURATION REQUIRED
  # ============================================
  # Please add/update the required server info:
  - id: server-1b5fc805
    server: CONFIGURE_SERVER_HOSTNAME  # ⚠️ UPDATE: e.g., prod.snowflake.acme.com
    type: snowflake  # Auto-detected from Informatica
    schema: PUBLIC  # Extracted from Informatica
```

## Output Structure

### Generated ODCS File

The script generates a YAML file with the following structure:

```yaml
id: <asset-id>
kind: DataContract
apiVersion: v3.1.0
domain: <domain>
dataProduct: <product-name>
version: 1.0.0
name: <contract-name>
status: active
contractCreatedTs: <timestamp>
description:
  authoritativeDefinitions:
    - type: informatica-asset
      url: <informatica-url>
schema:
  - id: <schema-id>
    name: <table-name>
    physicalName: <schema>/<table-name>
    physicalType: Table
    description: <description>
    properties:
      - name: <column-name>
        physicalType: VARCHAR(255)|DECIMAL(10,2)|...
        description: <column-description>
        required: true|false
        primaryKey: true|false
customProperties:
  - property: <property-name>
    value: <property-value>
servers:
  - id: <server-id>
    server: CONFIGURE_SERVER_HOSTNAME
    type: <detected-type>
    schema: <schema-name>
```

### Console Output

The script provides detailed progress information:

```
Fetching asset details for 1b5fc805-252d-4ba2-bd90-e943103e411b...
Fetching column details...
  Fetched column 1/12...
  Fetched column 2/12...
  ...
  Fetched column 12/12...
Generating ODCS YAML...

Writing ODCS to customer-transactions-odcs.yaml...
✓ Successfully generated ODCS file: customer-transactions-odcs.yaml
```

## Informatica Attribute Mapping

### Asset-Level Attributes

| Informatica Attribute | ODCS Field | Notes |
|----------------------|------------|-------|
| core.name | `schema.name` | Table name |
| core.businessName | `schema.name` | Preferred if available |
| core.description | `schema.description` | Asset description |
| com.infa.odin.models.relational.Owner | `schema.physicalName`, `servers.schema` | Schema name |
| core.resourceType | `servers.type` | Mapped to ODCS type |
| core.identity | `id`, `schema.id` | Asset ID |

### Column-Level Attributes

| Informatica Attribute | ODCS Field | Notes |
|----------------------|------------|-------|
| core.name | `properties.name` | Column name |
| com.infa.odin.models.relational.Datatype | `properties.physicalType` | Base data type |
| com.infa.odin.models.relational.DatatypeLength | `properties.physicalType` | Appended to type |
| com.infa.odin.models.relational.DatatypeScale | `properties.physicalType` | For numeric types |
| core.description | `properties.description` | Column description |
| com.infa.odin.models.relational.Nullable | `properties.required` | Inverted boolean |
| com.infa.odin.models.relational.PrimaryKeyColumn | `properties.primaryKey` | Boolean |
| core.Position | - | Used for sorting columns |

### System Attributes (Custom Properties)

| Informatica Attribute | Custom Property Name | Description |
|----------------------|---------------------|-------------|
| core.resourceName | Catalog Source Name | Source catalog name |
| com.infa.odin.models.relational.NumberOfRows | Number of rows | Row count |
| core.origin | Origin | Data origin |
| com.infa.odin.models.relational.Owner | Schema | Schema name |
| core.sourceCreatedBy | Source Created By | Creator |
| core.sourceCreatedOn | Source Created On | Creation timestamp |
| core.sourceModifiedBy | Source Modified By | Last modifier |
| core.sourceModifiedOn | Source Modified On | Last modified timestamp |

## Error Handling

### Common Errors

**1. Missing Environment Variables**
```
Error: Informatica CDGC URL is required. Set INFORMATICA_CDGC_URL environment variable or use --cdgc-url
Example: --cdgc-url https://cdgc.dm-us.informaticacloud.com
```
**Solution**: Set required environment variables or pass via command line

**2. Authentication Failure**
```
✗ HTTP Error: 401
  Authentication failed. Please check your credentials.
```
**Solution**: Verify username and password are correct

**3. Asset Not Found**
```
✗ HTTP Error: 404
  Asset 1b5fc805-252d-4ba2-bd90-e943103e411b not found.
```
**Solution**: Verify the asset ID exists and you have access

**4. Connection Issues**
```
✗ Connection Error: Unable to connect to Informatica CDGC at https://cdgc.dm-us.informaticacloud.com
  Please check your network connection and CDGC URL.
```
**Solution**: Check network connectivity and CDGC URL format

**5. Timeout Error**
```
✗ Timeout Error: Request timed out
  The server took too long to respond. Please try again.
```
**Solution**: Retry the request or check server status

**6. Data Structure Error**
```
✗ Data Error: Missing expected field 'summary'
  The asset data structure may be incomplete or invalid.
```
**Solution**: Verify the asset has complete metadata in Informatica

**7. Asset Type Validation Error**
```
✗ Validation Error: Asset 'MY_SCHEMA' is not a type 'Table'. This script only processes table assets. Please provide a table asset ID.
```
**Solution**: The provided asset ID is not a table (it may be a schema, database, or other asset type). Use the Informatica catalog to find the correct table asset ID. Only table and view assets are supported.

### Warnings

The script may display warnings for non-critical issues:

```
Warning: Failed to fetch column <column-id>: <error-message>
```

These warnings indicate missing column data but don't prevent ODCS generation. The script will continue processing other columns.

## Customization

### Modifying Resource Type Mappings

Edit the `RESOURCE_TYPE_MAPPING` dictionary to add or change server type mappings:

```python
RESOURCE_TYPE_MAPPING = {
    'YourCustomType': 'custom',
    # ... existing mappings
}
```

### Changing System Attributes

Update the `SYSTEM_ATTRIBUTES_MAPPING` dictionary to include/exclude specific attributes:

```python
SYSTEM_ATTRIBUTES_MAPPING = {
    'your.custom.attribute': 'Custom Property Name',
    # ... existing mappings
}
```

## Best Practices

1. **Verify Asset ID**: Ensure you're using the correct Informatica asset ID
2. **Check Hierarchy**: Verify columns are properly associated with tables in Informatica
3. **Review Output**: Always review the generated YAML before using
4. **Manual Configuration**: Complete server hostname if not auto-detected
5. **Validate**: Validate the YAML before finalizing

## Troubleshooting

### No Columns Generated

**Problem**: Schema has no properties (columns)

**Possible Causes**:
- Asset hierarchy is empty in Informatica
- Columns not properly associated with table
- Insufficient permissions to read column metadata

**Solution**:
1. Check asset hierarchy in Informatica CDGC
2. Verify column associations
3. Review console output for column fetch errors
4. Check user permissions

### Incorrect Data Types

**Problem**: Physical types don't match expectations

**Solution**:
1. Check Informatica attribute values for data type, length, scale
2. Verify the asset has complete metadata
3. Manually correct in generated YAML if needed

### Missing System Attributes

**Problem**: Custom properties are empty or incomplete

**Solution**:
1. Verify system attributes are populated in Informatica
2. Check if attributes are available for the asset type
3. Update `SYSTEM_ATTRIBUTES_MAPPING` if using custom attributes

### Authentication Token Expiry

**Problem**: Script fails midway with authentication errors

**Solution**:
1. The script caches tokens - this shouldn't happen normally
2. If it does, re-run the script (it will get a fresh token)
3. Check if your session timeout is very short

---

# Common Features

Both Collibra and Informatica integrations share these common features:

## ODCS v3.1.0 Compliance

Both scripts generate fully compliant ODCS v3.1.0 YAML files with:
- Required metadata fields (id, kind, apiVersion, domain, etc.)
- Schema definitions with properties
- Custom properties preservation
- Server configuration sections
- Authoritative definitions linking back to source

## Manual Configuration Guidance

Both scripts add helpful comments to guide manual configuration:
- Server hostname configuration
- Server type specification (when not auto-detected)
- Schema/database name configuration

## Error Handling

Comprehensive error handling for:
- Authentication failures
- Network connectivity issues
- Missing or invalid assets
- Incomplete metadata

## Validation Support

Generated YAML files can be validated using standard YAML validators and ODCS schema validators.

2. Verify column assets have "column" in their type name
3. Review console output for relation processing messages

### Incorrect Data Types

**Problem**: Logical or physical types don't match expectations

**Solution**:
1. Check Collibra attribute values for "Data Type" and "Technical Data Type"
2. Update `LOGICAL_TYPE_MAPPING` if needed
3. Manually correct in generated YAML

### Missing Classifications

**Problem**: Data classifications not included

**Solution**:
1. Verify GraphQL API access
2. Check if classifications are assigned in Collibra
3. Ensure classifications have "ACCEPTED" status


## Related Documentation

- [ODCS Specification v3.1.0](https://github.com/bitol-io/open-data-contract-standard)
- [Project README](../README.md) - Main project documentation
- [Build Guide](../BUILD_GUIDE.md) - Build and development instructions
- [Examples](../examples/odcs_generator_example.py) - Usage examples

## Project Structure

This script is part of the `data-product-python-sdk` project:

```
data-product-python-sdk/
├── dph_services/              # Data Product Hub services
├── odcs_generator/            # ODCS generator module (this script)
├── examples/                  # Usage examples
├── test/                      # Test suites
│   ├── integration/          # Integration tests
│   └── unit/                 # Unit tests
├── requirements.txt          # Python dependencies
└── setup.py                  # Package setup
```

## Support

For issues or questions:

1. **Check Console Output**: Review error messages and warnings
2. **Verify Configuration**: Ensure environment variables are set correctly
3. **Test Connectivity**: Verify access to Collibra API
4. **Review Examples**: Check `examples/odcs_generator_example.py` for usage patterns
5. **Review Logs**: Check for detailed error information
6. **Consult Documentation**: Review this README and related docs