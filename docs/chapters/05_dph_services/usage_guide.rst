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

.. _dph_services_usage:

Usage Guide
===========

This guide provides detailed instructions for using the Data Product Hub Services module.

Installation
------------

Install the data-intelligence-sdk package:

.. code-block:: bash

    pip install -e .

Or install from PyPI (when available):

.. code-block:: bash

    pip install data-intelligence-sdk

Setup and Configuration
-----------------------

Initialize the Service
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from wxdi.dph_services import DphV1
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

    # Create authenticator
    authenticator = IAMAuthenticator('your-api-key')

    # Initialize service
    dph_service = DphV1(authenticator=authenticator)
    dph_service.set_service_url('https://your-dph-instance.com')

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

You can also configure using environment variables:

.. code-block:: bash

    export DPH_APIKEY=your-api-key
    export DPH_URL=https://your-dph-instance.com

.. code-block:: python

    from wxdi.dph_services import DphV1
    
    # Automatically uses environment variables
    dph_service = DphV1.new_instance()

Container Operations
--------------------

Initialize Container
~~~~~~~~~~~~~~~~~~~~

Initialize a new container with default settings:

.. code-block:: python

    response = dph_service.initialize(
        include=[
            'delivery_methods',
            'data_product_samples',
            'domains_multi_industry'
        ]
    )
    
    print(f"Container ID: {response.result['container']['id']}")

Check Initialization Status
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    status = dph_service.get_initialize_status()
    
    if status.result['status'] == 'SUCCEEDED':
        print("Container is ready")
    elif status.result['status'] == 'IN_PROGRESS':
        print("Initialization in progress")
    else:
        print(f"Status: {status.result['status']}")

Get Service Credentials
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    credentials = dph_service.get_service_id_credentials()
    print(f"Service ID: {credentials.result['service_id']}")

Data Product Management
-----------------------

Create a Data Product
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    data_product = dph_service.create_data_product(
        drafts=[{
            'version': '1.0.0',
            'name': 'Customer Analytics Dataset',
            'description': 'Comprehensive customer behavior analytics',
            'asset': {
                'id': 'asset-123',
                'container': {'id': 'container-456'}
            },
            'domain': {
                'id': 'domain-789',
                'name': 'Customer Analytics'
            },
            'parts_out': [{
                'asset': {
                    'id': 'asset-123',
                    'container': {'id': 'container-456'}
                },
                'delivery_methods': [{
                    'id': 'method-001',
                    'container': {'id': 'container-456'}
                }]
            }]
        }]
    )
    
    product_id = data_product.result['id']
    print(f"Created data product: {product_id}")

List Data Products
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # List with pagination
    response = dph_service.list_data_products(limit=50)
    
    for product in response.result['data_products']:
        print(f"- {product['name']} (v{product['version']})")
    
    # Use pager for all results
    all_products = []
    pager = dph_service.list_data_products_with_pager(limit=50)
    
    for page in pager:
        all_products.extend(page['data_products'])

Get Data Product Details
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    product = dph_service.get_data_product(data_product_id=product_id)
    
    print(f"Name: {product.result['name']}")
    print(f"Version: {product.result['version']}")
    print(f"Description: {product.result['description']}")
    print(f"Status: {product.result['state']}")

Update Data Product
~~~~~~~~~~~~~~~~~~~

Use JSON Patch operations for updates:

.. code-block:: python

    updated = dph_service.update_data_product(
        data_product_id=product_id,
        json_patch_instructions=[
            {
                'op': 'replace',
                'path': '/description',
                'value': 'Updated comprehensive customer analytics'
            },
            {
                'op': 'add',
                'path': '/tags/-',
                'value': 'analytics'
            }
        ]
    )

Delete Data Product
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    dph_service.delete_data_product(data_product_id=product_id)
    print("Data product deleted")

Draft Management
----------------

Create a Draft
~~~~~~~~~~~~~~

.. code-block:: python

    draft = dph_service.create_data_product_draft(
        data_product_id=product_id,
        asset={'id': 'asset-123', 'container': {'id': 'container-456'}},
        version='1.1.0',
        name='Customer Analytics Dataset v1.1',
        description='Enhanced version with additional metrics'
    )
    
    draft_id = draft.result['id']

List Drafts
~~~~~~~~~~~

.. code-block:: python

    drafts = dph_service.list_data_product_drafts(
        data_product_id=product_id,
        limit=50
    )
    
    for draft in drafts.result['drafts']:
        print(f"- Draft {draft['version']}: {draft['state']}")

Update Draft
~~~~~~~~~~~~

.. code-block:: python

    updated_draft = dph_service.update_data_product_draft(
        data_product_id=product_id,
        draft_id=draft_id,
        json_patch_instructions=[
            {
                'op': 'replace',
                'path': '/description',
                'value': 'Updated draft description'
            }
        ]
    )

Publish Draft
~~~~~~~~~~~~~

.. code-block:: python

    # Publish draft to create a release
    release = dph_service.publish_data_product_draft(
        data_product_id=product_id,
        draft_id=draft_id
    )
    
    print(f"Published release: {release.result['id']}")

Delete Draft
~~~~~~~~~~~~

.. code-block:: python

    dph_service.delete_data_product_draft(
        data_product_id=product_id,
        draft_id=draft_id
    )

Contract Terms Management
-------------------------

Create Contract Terms Document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    doc = dph_service.create_draft_contract_terms_document(
        data_product_id=product_id,
        draft_id=draft_id,
        contract_terms_id=terms_id,
        type='terms_and_conditions',
        name='Terms and Conditions',
        url='https://example.com/terms.pdf',
        attachment={
            'id': 'attachment-123'
        }
    )

Get Contract Terms
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    terms = dph_service.get_data_product_draft_contract_terms(
        data_product_id=product_id,
        draft_id=draft_id
    )
    
    for doc in terms.result['documents']:
        print(f"- {doc['name']}: {doc['type']}")

Update Contract Terms Document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    updated_doc = dph_service.update_draft_contract_terms_document(
        data_product_id=product_id,
        draft_id=draft_id,
        contract_terms_id=terms_id,
        document_id=doc_id,
        json_patch_instructions=[
            {
                'op': 'replace',
                'path': '/url',
                'value': 'https://example.com/updated-terms.pdf'
            }
        ]
    )

Delete Contract Terms Document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    dph_service.delete_draft_contract_terms_document(
        data_product_id=product_id,
        draft_id=draft_id,
        contract_terms_id=terms_id,
        document_id=doc_id
    )

Release Management
------------------

List Releases
~~~~~~~~~~~~~

.. code-block:: python

    releases = dph_service.list_data_product_releases(
        data_product_id=product_id,
        state=['available', 'retired']
    )
    
    for release in releases.result['releases']:
        print(f"- v{release['version']}: {release['state']}")

Get Release Details
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    release = dph_service.get_data_product_release(
        data_product_id=product_id,
        release_id=release_id
    )
    
    print(f"Version: {release.result['version']}")
    print(f"State: {release.result['state']}")
    print(f"Published: {release.result['created_at']}")

Update Release
~~~~~~~~~~~~~~

.. code-block:: python

    updated_release = dph_service.update_data_product_release(
        data_product_id=product_id,
        release_id=release_id,
        json_patch_instructions=[
            {
                'op': 'replace',
                'path': '/description',
                'value': 'Updated release description'
            }
        ]
    )

Retire Release
~~~~~~~~~~~~~~

.. code-block:: python

    retired = dph_service.retire_data_product_release(
        data_product_id=product_id,
        release_id=release_id
    )
    
    print(f"Release retired: {retired.result['state']}")

Domain Management
-----------------

List Domains
~~~~~~~~~~~~

.. code-block:: python

    domains = dph_service.list_data_product_domains(limit=50)
    
    for domain in domains.result['domains']:
        print(f"- {domain['name']}: {domain['description']}")

Create Domain
~~~~~~~~~~~~~

.. code-block:: python

    domain = dph_service.create_data_product_domain(
        name='Customer Analytics',
        description='Customer-related data products and analytics',
        container={'id': 'container-123'}
    )
    
    domain_id = domain.result['id']

Create Subdomain
~~~~~~~~~~~~~~~~

.. code-block:: python

    subdomain = dph_service.create_data_product_subdomain(
        domain_id=domain_id,
        name='Customer Segmentation',
        description='Customer segmentation and clustering datasets'
    )

Get Domain
~~~~~~~~~~

.. code-block:: python

    domain = dph_service.get_domain(domain_id=domain_id)
    
    print(f"Name: {domain.result['name']}")
    print(f"Subdomains: {len(domain.result.get('subdomains', []))}")

Update Domain
~~~~~~~~~~~~~

.. code-block:: python

    updated_domain = dph_service.update_data_product_domain(
        domain_id=domain_id,
        json_patch_instructions=[
            {
                'op': 'replace',
                'path': '/description',
                'value': 'Updated domain description'
            }
        ]
    )

Delete Domain
~~~~~~~~~~~~~

.. code-block:: python

    dph_service.delete_domain(domain_id=domain_id)

Asset Visualization
-------------------

Create Visualization
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    visualization = dph_service.create_data_asset_visualization(
        container={'id': 'container-123'},
        assets=[
            {'id': 'asset-1', 'container': {'id': 'container-123'}},
            {'id': 'asset-2', 'container': {'id': 'container-123'}},
            {'id': 'asset-3', 'container': {'id': 'container-123'}}
        ]
    )
    
    print(f"Visualization created: {visualization.result['id']}")

Reinitiate Visualization
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    reinitiated = dph_service.reinitiate_data_asset_visualization(
        container={'id': 'container-123'},
        assets=[
            {'id': 'asset-1', 'container': {'id': 'container-123'}},
            {'id': 'asset-4', 'container': {'id': 'container-123'}}
        ]
    )

Contract Templates
------------------

Create Template
~~~~~~~~~~~~~~~

.. code-block:: python

    template = dph_service.create_contract_template(
        name='Standard Data Sharing Agreement',
        description='Standard terms for data product sharing',
        contract_terms_documents=[{
            'type': 'terms_and_conditions',
            'name': 'Standard Terms',
            'url': 'https://example.com/standard-terms.pdf'
        }]
    )
    
    template_id = template.result['id']

List Templates
~~~~~~~~~~~~~~

.. code-block:: python

    templates = dph_service.list_data_product_contract_template(limit=50)
    
    for template in templates.result['contract_templates']:
        print(f"- {template['name']}")

Get Template
~~~~~~~~~~~~

.. code-block:: python

    template = dph_service.get_contract_template(
        contract_template_id=template_id
    )

Update Template
~~~~~~~~~~~~~~~

.. code-block:: python

    updated_template = dph_service.update_data_product_contract_template(
        contract_template_id=template_id,
        json_patch_instructions=[
            {
                'op': 'replace',
                'path': '/description',
                'value': 'Updated template description'
            }
        ]
    )

Delete Template
~~~~~~~~~~~~~~~

.. code-block:: python

    dph_service.delete_data_product_contract_template(
        contract_template_id=template_id
    )

Advanced Topics
---------------

Custom Headers
~~~~~~~~~~~~~~

Add custom headers to requests:

.. code-block:: python

    response = dph_service.get_data_product(
        data_product_id=product_id,
        headers={
            'Custom-Header': 'value',
            'X-Request-ID': 'unique-id'
        }
    )

Timeout Configuration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    dph_service.set_http_config({
        'timeout': 60  # 60 seconds
    })

Disable SSL Verification (Development Only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    dph_service.set_disable_ssl_verification(True)

See Also
--------

- :ref:`dph_services_examples` - Complete code examples
- :ref:`api_dph_services` - API reference
- :ref:`dph_services_overview` - Architecture overview

.. Made with Bob
