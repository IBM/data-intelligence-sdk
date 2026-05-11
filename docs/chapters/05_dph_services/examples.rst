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

.. _dph_services_examples:

Examples
========

Complete examples demonstrating common use cases for the Data Product Hub Services module.

Complete Workflow Example
--------------------------

This example demonstrates the complete lifecycle of a data product:

.. code-block:: python

    from wxdi.dph_services import DphV1
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
    from ibm_cloud_sdk_core import ApiException

    # Initialize service
    authenticator = IAMAuthenticator('your-api-key')
    dph_service = DphV1(authenticator=authenticator)
    dph_service.set_service_url('https://your-dph-instance.com')

    # Step 1: Initialize container
    print("Initializing container...")
    init_response = dph_service.initialize(
        include=['delivery_methods', 'data_product_samples', 'domains_multi_industry']
    )
    container_id = init_response.result['container']['id']
    print(f"Container initialized: {container_id}")

    # Step 2: Create a domain
    print("\nCreating domain...")
    domain = dph_service.create_data_product_domain(
        name='Customer Analytics',
        description='Customer behavior and analytics data products',
        container={'id': container_id}
    )
    domain_id = domain.result['id']
    print(f"Domain created: {domain_id}")

    # Step 3: Create data product with draft
    print("\nCreating data product...")
    data_product = dph_service.create_data_product(
        drafts=[{
            'version': '1.0.0',
            'name': 'Customer Purchase History',
            'description': 'Historical customer purchase data for analytics',
            'asset': {
                'id': 'asset-12345',
                'container': {'id': container_id}
            },
            'domain': {
                'id': domain_id,
                'name': 'Customer Analytics'
            },
            'parts_out': [{
                'asset': {
                    'id': 'asset-12345',
                    'container': {'id': container_id}
                },
                'delivery_methods': [{
                    'id': 'delivery-method-001',
                    'container': {'id': container_id}
                }]
            }]
        }]
    )
    
    product_id = data_product.result['id']
    draft_id = data_product.result['drafts'][0]['id']
    print(f"Data product created: {product_id}")
    print(f"Draft created: {draft_id}")

    # Step 4: Add contract terms
    print("\nAdding contract terms...")
    contract_terms = dph_service.get_data_product_draft_contract_terms(
        data_product_id=product_id,
        draft_id=draft_id
    )
    
    terms_id = contract_terms.result['id']
    
    doc = dph_service.create_draft_contract_terms_document(
        data_product_id=product_id,
        draft_id=draft_id,
        contract_terms_id=terms_id,
        type='terms_and_conditions',
        name='Data Usage Terms',
        url='https://example.com/terms.pdf'
    )
    print(f"Contract document added: {doc.result['id']}")

    # Step 5: Publish the draft
    print("\nPublishing draft...")
    release = dph_service.publish_data_product_draft(
        data_product_id=product_id,
        draft_id=draft_id
    )
    release_id = release.result['id']
    print(f"Release published: {release_id}")

    # Step 6: Create a new version
    print("\nCreating new version...")
    new_draft = dph_service.create_data_product_draft(
        data_product_id=product_id,
        asset={'id': 'asset-12345', 'container': {'id': container_id}},
        version='1.1.0',
        name='Customer Purchase History v1.1',
        description='Enhanced with additional purchase metrics'
    )
    new_draft_id = new_draft.result['id']
    print(f"New draft created: {new_draft_id}")

    print("\n✅ Complete workflow executed successfully!")

Batch Operations Example
-------------------------

Create multiple data products efficiently:

.. code-block:: python

    from wxdi.dph_services import DphV1
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

    # Initialize service
    authenticator = IAMAuthenticator('your-api-key')
    dph_service = DphV1(authenticator=authenticator)
    dph_service.set_service_url('https://your-dph-instance.com')

    # Define multiple data products
    products_to_create = [
        {
            'name': 'Customer Demographics',
            'description': 'Customer demographic information',
            'asset_id': 'asset-001'
        },
        {
            'name': 'Transaction History',
            'description': 'Historical transaction records',
            'asset_id': 'asset-002'
        },
        {
            'name': 'Product Catalog',
            'description': 'Complete product catalog data',
            'asset_id': 'asset-003'
        }
    ]

    # Create all products
    created_products = []
    
    for product_info in products_to_create:
        try:
            product = dph_service.create_data_product(
                drafts=[{
                    'version': '1.0.0',
                    'name': product_info['name'],
                    'description': product_info['description'],
                    'asset': {
                        'id': product_info['asset_id'],
                        'container': {'id': 'container-123'}
                    }
                }]
            )
            created_products.append(product.result)
            print(f"✅ Created: {product_info['name']}")
        except Exception as e:
            print(f"❌ Failed to create {product_info['name']}: {e}")

    print(f"\nTotal products created: {len(created_products)}")

Pagination Example
------------------

Handle large datasets with pagination:

.. code-block:: python

    from wxdi.dph_services import DphV1
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

    # Initialize service
    authenticator = IAMAuthenticator('your-api-key')
    dph_service = DphV1(authenticator=authenticator)
    dph_service.set_service_url('https://your-dph-instance.com')

    # Method 1: Using pager (recommended)
    print("Fetching all data products using pager...")
    all_products = []
    pager = dph_service.list_data_products_with_pager(limit=50)

    for page in pager:
        all_products.extend(page['data_products'])
        print(f"Fetched {len(page['data_products'])} products...")

    print(f"Total products: {len(all_products)}")

    # Method 2: Manual pagination
    print("\nManual pagination example...")
    all_products_manual = []
    start = None
    
    while True:
        response = dph_service.list_data_products(
            limit=50,
            start=start
        )
        
        products = response.result['data_products']
        all_products_manual.extend(products)
        
        # Check if there are more pages
        if 'next' not in response.result or not response.result['next']:
            break
            
        # Extract start token from next link
        start = response.result['next'].get('start')

    print(f"Total products (manual): {len(all_products_manual)}")

Error Handling Example
----------------------

Robust error handling for production use:

.. code-block:: python

    from wxdi.dph_services import DphV1
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
    from ibm_cloud_sdk_core import ApiException
    import time

    # Initialize service
    authenticator = IAMAuthenticator('your-api-key')
    dph_service = DphV1(authenticator=authenticator)
    dph_service.set_service_url('https://your-dph-instance.com')

    def create_data_product_with_retry(dph_service, drafts, max_retries=3):
        """Create data product with retry logic"""
        for attempt in range(max_retries):
            try:
                response = dph_service.create_data_product(drafts=drafts)
                return response
            except ApiException as e:
                if e.code == 429:  # Rate limit
                    wait_time = 2 ** attempt
                    print(f"Rate limited. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                elif e.code >= 500:  # Server error
                    if attempt < max_retries - 1:
                        print(f"Server error. Retrying... (attempt {attempt + 1})")
                        time.sleep(2 ** attempt)
                    else:
                        raise
                elif e.code == 404:
                    print(f"Resource not found: {e.message}")
                    raise
                elif e.code == 401:
                    print("Authentication failed. Check your credentials.")
                    raise
                elif e.code == 403:
                    print("Insufficient permissions.")
                    raise
                else:
                    print(f"API Error {e.code}: {e.message}")
                    raise
        
        raise Exception("Max retries exceeded")

    # Use the retry function
    try:
        drafts = [{
            'version': '1.0.0',
            'name': 'Test Product',
            'description': 'Test description',
            'asset': {'id': 'asset-123', 'container': {'id': 'container-456'}}
        }]
        
        product = create_data_product_with_retry(dph_service, drafts)
        print(f"✅ Product created: {product.result['id']}")
    except Exception as e:
        print(f"❌ Failed to create product: {e}")

Search and Filter Example
--------------------------

Find specific data products:

.. code-block:: python

    from wxdi.dph_services import DphV1
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

    # Initialize service
    authenticator = IAMAuthenticator('your-api-key')
    dph_service = DphV1(authenticator=authenticator)
    dph_service.set_service_url('https://your-dph-instance.com')

    # Get all products and filter
    all_products = []
    pager = dph_service.list_data_products_with_pager(limit=100)
    
    for page in pager:
        all_products.extend(page['data_products'])

    # Filter by name pattern
    customer_products = [
        p for p in all_products 
        if 'customer' in p['name'].lower()
    ]
    print(f"Found {len(customer_products)} customer-related products")

    # Filter by domain
    analytics_products = [
        p for p in all_products
        if p.get('domain', {}).get('name') == 'Customer Analytics'
    ]
    print(f"Found {len(analytics_products)} analytics products")

    # Filter by version
    v1_products = [
        p for p in all_products
        if p['version'].startswith('1.')
    ]
    print(f"Found {len(v1_products)} v1.x products")

Contract Template Example
--------------------------

Create and use contract templates:

.. code-block:: python

    from wxdi.dph_services import DphV1
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

    # Initialize service
    authenticator = IAMAuthenticator('your-api-key')
    dph_service = DphV1(authenticator=authenticator)
    dph_service.set_service_url('https://your-dph-instance.com')

    # Create a reusable contract template
    template = dph_service.create_contract_template(
        name='Standard Data Sharing Agreement',
        description='Standard terms for internal data sharing',
        contract_terms_documents=[
            {
                'type': 'terms_and_conditions',
                'name': 'Terms and Conditions',
                'url': 'https://example.com/standard-terms.pdf'
            },
            {
                'type': 'sla',
                'name': 'Service Level Agreement',
                'url': 'https://example.com/sla.pdf'
            }
        ]
    )
    
    template_id = template.result['id']
    print(f"Template created: {template_id}")

    # Use template when creating data products
    data_product = dph_service.create_data_product(
        drafts=[{
            'version': '1.0.0',
            'name': 'Sales Data',
            'description': 'Monthly sales data',
            'asset': {'id': 'asset-123', 'container': {'id': 'container-456'}},
            'contract_terms': {
                'template_id': template_id
            }
        }]
    )
    
    print(f"Data product created with template: {data_product.result['id']}")

Domain Hierarchy Example
------------------------

Create and manage domain hierarchies:

.. code-block:: python

    from wxdi.dph_services import DphV1
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

    # Initialize service
    authenticator = IAMAuthenticator('your-api-key')
    dph_service = DphV1(authenticator=authenticator)
    dph_service.set_service_url('https://your-dph-instance.com')

    # Create parent domain
    parent_domain = dph_service.create_data_product_domain(
        name='Customer Data',
        description='All customer-related data products',
        container={'id': 'container-123'}
    )
    parent_id = parent_domain.result['id']
    print(f"Parent domain created: {parent_id}")

    # Create subdomains
    subdomains = [
        {'name': 'Demographics', 'description': 'Customer demographic data'},
        {'name': 'Behavior', 'description': 'Customer behavior analytics'},
        {'name': 'Transactions', 'description': 'Customer transaction history'}
    ]

    for subdomain_info in subdomains:
        subdomain = dph_service.create_data_product_subdomain(
            domain_id=parent_id,
            name=subdomain_info['name'],
            description=subdomain_info['description']
        )
        print(f"Subdomain created: {subdomain_info['name']}")

    # List all domains with hierarchy
    domains = dph_service.list_data_product_domains(limit=100)
    
    for domain in domains.result['domains']:
        print(f"\n{domain['name']}")
        if 'subdomains' in domain:
            for subdomain in domain['subdomains']:
                print(f"  └─ {subdomain['name']}")

Monitoring and Reporting Example
---------------------------------

Generate reports on data product usage:

.. code-block:: python

    from wxdi.dph_services import DphV1
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
    from collections import defaultdict
    from datetime import datetime

    # Initialize service
    authenticator = IAMAuthenticator('your-api-key')
    dph_service = DphV1(authenticator=authenticator)
    dph_service.set_service_url('https://your-dph-instance.com')

    # Collect all data products
    all_products = []
    pager = dph_service.list_data_products_with_pager(limit=100)
    
    for page in pager:
        all_products.extend(page['data_products'])

    # Generate statistics
    stats = {
        'total_products': len(all_products),
        'by_domain': defaultdict(int),
        'by_version': defaultdict(int),
        'by_state': defaultdict(int)
    }

    for product in all_products:
        # Count by domain
        domain_name = product.get('domain', {}).get('name', 'Unknown')
        stats['by_domain'][domain_name] += 1
        
        # Count by version
        version = product.get('version', 'Unknown')
        major_version = version.split('.')[0] if '.' in version else version
        stats['by_version'][f"v{major_version}.x"] += 1
        
        # Count by state
        state = product.get('state', 'Unknown')
        stats['by_state'][state] += 1

    # Print report
    print("=" * 50)
    print("DATA PRODUCT REPORT")
    print("=" * 50)
    print(f"\nTotal Data Products: {stats['total_products']}")
    
    print("\nBy Domain:")
    for domain, count in sorted(stats['by_domain'].items()):
        print(f"  {domain}: {count}")
    
    print("\nBy Version:")
    for version, count in sorted(stats['by_version'].items()):
        print(f"  {version}: {count}")
    
    print("\nBy State:")
    for state, count in sorted(stats['by_state'].items()):
        print(f"  {state}: {count}")

See Also
--------

- :ref:`dph_services_usage` - Detailed usage guide
- :ref:`api_dph_services` - API reference
- :ref:`dph_services_overview` - Architecture overview

.. Made with Bob
