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

# Data Product Hub Services (DPH Services)

Python client library for IBM Data Product Hub API, providing programmatic access to data product management, container operations, contract terms, and asset visualization.

## Overview

The `dph_services` module provides a complete Python SDK for interacting with IBM Data Product Hub services. It enables developers to:

- Initialize and manage data product containers
- Create, update, and publish data products
- Manage data product drafts and releases
- Handle contract terms and documents
- Create and manage data asset visualizations
- Manage domains and subdomains
- Work with contract templates

## Installation

The module is included in the data-intelligence-sdk package:

```bash
pip install -e .
```

## Quick Start

### Basic Setup

```python
from wxdi.dph_services import DphV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Initialize authenticator
authenticator = IAMAuthenticator('your-api-key')

# Create service instance
dph_service = DphV1(authenticator=authenticator)
dph_service.set_service_url('https://your-dph-instance.com')
```

### Initialize a Container

```python
# Initialize container with default settings
response = dph_service.initialize(
    include=['delivery_methods', 'data_product_samples', 'domains_multi_industry']
)

print(f"Container initialized: {response.result}")
```

### Create a Data Product

```python
# Create a new data product with a draft
data_product = dph_service.create_data_product(
    drafts=[{
        'version': '1.0.0',
        'name': 'Customer Analytics Data Product',
        'description': 'Comprehensive customer analytics dataset',
        'asset': {
            'id': 'asset-123',
            'container': {'id': 'container-456'}
        },
        'domain': {
            'id': 'domain-789',
            'name': 'Customer Analytics'
        }
    }]
)

print(f"Data product created: {data_product.result['id']}")
```

### List Data Products

```python
# List all data products
response = dph_service.list_data_products(limit=50)

for product in response.result['data_products']:
    print(f"- {product['name']} (v{product['version']})")
```

### Get a Specific Data Product

```python
# Get data product by ID
data_product_id = 'your-data-product-id'
response = dph_service.get_data_product(data_product_id=data_product_id)

print(f"Data Product: {response.result['name']}")
print(f"Description: {response.result['description']}")
```

## Core Features

### 1. Container Management

Initialize and manage data product containers:

```python
# Initialize container
response = dph_service.initialize(
    include=['delivery_methods', 'data_product_samples']
)

# Get initialization status
status = dph_service.get_initialize_status()
print(f"Status: {status.result['status']}")
```

### 2. Data Product Operations

Complete lifecycle management:

```python
# Create data product
product = dph_service.create_data_product(drafts=[...])

# Update data product
updated = dph_service.update_data_product(
    data_product_id=product_id,
    json_patch_instructions=[
        {'op': 'replace', 'path': '/description', 'value': 'Updated description'}
    ]
)

# Delete data product (if needed)
dph_service.delete_data_product(data_product_id=product_id)
```

### 3. Draft Management

Work with data product drafts:

```python
# Create a draft
draft = dph_service.create_data_product_draft(
    data_product_id=product_id,
    asset={'id': 'asset-123', 'container': {'id': 'container-456'}},
    version='1.1.0',
    name='Updated Version'
)

# List drafts
drafts = dph_service.list_data_product_drafts(data_product_id=product_id)

# Get specific draft
draft_detail = dph_service.get_data_product_draft(
    data_product_id=product_id,
    draft_id=draft_id
)

# Update draft
updated_draft = dph_service.update_data_product_draft(
    data_product_id=product_id,
    draft_id=draft_id,
    json_patch_instructions=[...]
)

# Publish draft
published = dph_service.publish_data_product_draft(
    data_product_id=product_id,
    draft_id=draft_id
)
```

### 4. Contract Terms Management

Manage contract terms and documents:

```python
# Create contract terms document
doc = dph_service.create_draft_contract_terms_document(
    data_product_id=product_id,
    draft_id=draft_id,
    contract_terms_id=terms_id,
    type='terms_and_conditions',
    name='Terms and Conditions',
    url='https://example.com/terms.pdf'
)

# Get contract terms
terms = dph_service.get_data_product_draft_contract_terms(
    data_product_id=product_id,
    draft_id=draft_id
)

# Update contract terms document
updated_doc = dph_service.update_draft_contract_terms_document(
    data_product_id=product_id,
    draft_id=draft_id,
    contract_terms_id=terms_id,
    document_id=doc_id,
    json_patch_instructions=[...]
)

# Delete contract terms document
dph_service.delete_draft_contract_terms_document(
    data_product_id=product_id,
    draft_id=draft_id,
    contract_terms_id=terms_id,
    document_id=doc_id
)
```

### 5. Release Management

Manage data product releases:

```python
# List releases
releases = dph_service.list_data_product_releases(
    data_product_id=product_id
)

# Get specific release
release = dph_service.get_data_product_release(
    data_product_id=product_id,
    release_id=release_id
)

# Update release
updated_release = dph_service.update_data_product_release(
    data_product_id=product_id,
    release_id=release_id,
    json_patch_instructions=[...]
)

# Retire release
retired = dph_service.retire_data_product_release(
    data_product_id=product_id,
    release_id=release_id
)
```

### 6. Asset Visualization

Create and manage data asset visualizations:

```python
# Create visualization
visualization = dph_service.create_data_asset_visualization(
    container={'id': 'container-123'},
    assets=[
        {'id': 'asset-1', 'container': {'id': 'container-123'}},
        {'id': 'asset-2', 'container': {'id': 'container-123'}}
    ]
)

# Reinitiate visualization
reinitiated = dph_service.reinitiate_data_asset_visualization(
    container={'id': 'container-123'},
    assets=[...]
)
```

### 7. Domain Management

Organize data products by domains:

```python
# List domains
domains = dph_service.list_data_product_domains(limit=50)

# Create domain
domain = dph_service.create_data_product_domain(
    name='Customer Analytics',
    description='Customer-related data products',
    container={'id': 'container-123'}
)

# Create subdomain
subdomain = dph_service.create_data_product_subdomain(
    domain_id=domain_id,
    name='Customer Segmentation',
    description='Customer segmentation datasets'
)

# Get domain
domain_detail = dph_service.get_domain(domain_id=domain_id)

# Update domain
updated_domain = dph_service.update_data_product_domain(
    domain_id=domain_id,
    json_patch_instructions=[...]
)

# Delete domain
dph_service.delete_domain(domain_id=domain_id)
```

### 8. Contract Templates

Manage reusable contract templates:

```python
# Create contract template
template = dph_service.create_contract_template(
    name='Standard Terms Template',
    description='Standard contract terms for data products',
    contract_terms_documents=[...]
)

# List templates
templates = dph_service.list_data_product_contract_template(limit=50)

# Get template
template_detail = dph_service.get_contract_template(
    contract_template_id=template_id
)

# Update template
updated_template = dph_service.update_data_product_contract_template(
    contract_template_id=template_id,
    json_patch_instructions=[...]
)

# Delete template
dph_service.delete_data_product_contract_template(
    contract_template_id=template_id
)
```

## Advanced Usage

### Pagination

Handle large result sets with pagination:

```python
# Using pager for data products
all_products = []
pager = dph_service.list_data_products_with_pager(limit=50)

for page in pager:
    all_products.extend(page['data_products'])

print(f"Total products: {len(all_products)}")
```

### Error Handling

```python
from ibm_cloud_sdk_core import ApiException

try:
    response = dph_service.get_data_product(data_product_id='invalid-id')
except ApiException as e:
    print(f"Error: {e.code} - {e.message}")
```

### Custom Headers

```python
# Add custom headers to requests
response = dph_service.get_data_product(
    data_product_id=product_id,
    headers={'Custom-Header': 'value'}
)
```

## API Reference

### Main Classes

- **`DphV1`**: Main service class for Data Product Hub operations
- **`DataProduct`**: Data product model
- **`DataProductDraft`**: Draft model
- **`ContractTerms`**: Contract terms model
- **`Domain`**: Domain model

### Key Methods

#### Container Operations
- `initialize()` - Initialize container
- `get_initialize_status()` - Get initialization status
- `get_service_id_credentials()` - Get service credentials
- `manage_api_keys()` - Manage API keys

#### Data Product Operations
- `create_data_product()` - Create new data product
- `list_data_products()` - List all data products
- `get_data_product()` - Get specific data product
- `update_data_product()` - Update data product
- `delete_data_product()` - Delete data product

#### Draft Operations
- `create_data_product_draft()` - Create draft
- `list_data_product_drafts()` - List drafts
- `get_data_product_draft()` - Get draft details
- `update_data_product_draft()` - Update draft
- `delete_data_product_draft()` - Delete draft
- `publish_data_product_draft()` - Publish draft

#### Release Operations
- `list_data_product_releases()` - List releases
- `get_data_product_release()` - Get release details
- `update_data_product_release()` - Update release
- `retire_data_product_release()` - Retire release

## Examples

See the `examples/test_dph_v1_examples.py` file for comprehensive usage examples.

## Testing

Run the unit tests:

```bash
pytest tests/src/dph_services/ -v
```

Run integration tests (requires service credentials):

```bash
pytest tests/src/integration/test_dph_v1.py -v
```

## Requirements

- Python 3.8+
- ibm-cloud-sdk-core >= 3.16.7
- requests >= 2.32.4
- python-dateutil >= 2.5.3

## License

Apache License 2.0

## Support

For issues and questions:
- GitHub Issues: https://github.com/IBM/data-intelligence-sdk/issues
- Documentation: See main README.md

## Related Modules

- **dq_validator**: Data quality validation
- **odcs_generator**: ODCS file generation
- **data_product_recommender**: Query log analysis