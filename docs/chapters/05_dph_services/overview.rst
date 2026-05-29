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

.. _dph_services_overview:

DPH Services Overview
=====================

The Data Product Hub Services module provides a comprehensive Python SDK for managing data products in IBM Data Product Hub.

Architecture
------------

The module is built on top of the IBM Cloud SDK Core and provides:

- **Type-safe API**: Full type hints for better IDE support
- **Error handling**: Comprehensive exception handling with detailed error messages
- **Pagination support**: Built-in pagination for large result sets
- **Authentication**: Seamless integration with IBM Cloud authentication

Core Components
---------------

Container Management
~~~~~~~~~~~~~~~~~~~~

Containers are the foundation of Data Product Hub, providing:

- Delivery method configurations
- Sample data products
- Domain structures
- Service credentials

Data Products
~~~~~~~~~~~~~

Data products represent packaged data assets with:

- Metadata and descriptions
- Version control
- Asset references
- Domain associations
- Contract terms

Drafts and Releases
~~~~~~~~~~~~~~~~~~~

**Drafts**: Work-in-progress versions that can be edited and updated

**Releases**: Published versions that are immutable and available for consumption

Contract Terms
~~~~~~~~~~~~~~

Legal and business terms governing data product usage:

- Terms and conditions documents
- Service level agreements
- Usage restrictions
- Compliance requirements

Domains
~~~~~~~

Organizational structure for categorizing data products:

- Top-level domains (e.g., Finance, Marketing)
- Subdomains for finer categorization
- Multi-industry domain support

Data Flow
---------

1. **Initialize Container**: Set up the data product hub environment
2. **Create Draft**: Define a new data product version
3. **Add Contract Terms**: Attach legal and business terms
4. **Publish Draft**: Convert draft to a release
5. **Manage Lifecycle**: Update, version, or retire releases

Authentication
--------------

The module supports multiple authentication methods:

**IAM Authentication** (Recommended)

.. code-block:: python

    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
    
    authenticator = IAMAuthenticator('your-api-key')
    dph_service = DphV1(authenticator=authenticator)

**Bearer Token Authentication**

.. code-block:: python

    from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator
    
    authenticator = BearerTokenAuthenticator('your-bearer-token')
    dph_service = DphV1(authenticator=authenticator)

**Cloud Pak for Data Authentication**

.. code-block:: python

    from ibm_cloud_sdk_core.authenticators import CloudPakForDataAuthenticator
    
    authenticator = CloudPakForDataAuthenticator(
        username='your-username',
        password='your-password',
        url='https://your-cpd-instance.com'
    )
    dph_service = DphV1(authenticator=authenticator)

Error Handling
--------------

The SDK uses standard IBM Cloud SDK exceptions:

.. code-block:: python

    from ibm_cloud_sdk_core import ApiException
    
    try:
        response = dph_service.get_data_product(data_product_id='invalid-id')
    except ApiException as e:
        print(f"Error Code: {e.code}")
        print(f"Error Message: {e.message}")
        print(f"HTTP Status: {e.http_response.status_code}")

Common error codes:

- **400**: Bad Request - Invalid parameters
- **401**: Unauthorized - Authentication failed
- **403**: Forbidden - Insufficient permissions
- **404**: Not Found - Resource doesn't exist
- **409**: Conflict - Resource already exists
- **500**: Internal Server Error - Service error

Best Practices
--------------

**Use Pagination for Large Datasets**

.. code-block:: python

    # Use pager for automatic pagination
    pager = dph_service.list_data_products_with_pager(limit=50)
    for page in pager:
        for product in page['data_products']:
            process_product(product)

**Implement Retry Logic**

.. code-block:: python

    import time
    from ibm_cloud_sdk_core import ApiException
    
    def create_with_retry(dph_service, drafts, max_retries=3):
        for attempt in range(max_retries):
            try:
                return dph_service.create_data_product(drafts=drafts)
            except ApiException as e:
                if e.code == 429 or e.code >= 500:  # Rate limit or server error
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                raise

**Validate Before Publishing**

.. code-block:: python

    def validate_draft(draft):
        """Validate draft before publishing"""
        required_fields = ['name', 'version', 'asset', 'domain']
        for field in required_fields:
            if field not in draft or not draft[field]:
                raise ValueError(f"Missing required field: {field}")
        return True

**Use JSON Patch for Updates**

.. code-block:: python

    # Efficient updates using JSON Patch
    patch_operations = [
        {'op': 'replace', 'path': '/description', 'value': 'Updated description'},
        {'op': 'add', 'path': '/tags/-', 'value': 'new-tag'}
    ]
    
    dph_service.update_data_product(
        data_product_id=product_id,
        json_patch_instructions=patch_operations
    )

Performance Considerations
--------------------------

**Batch Operations**

When creating multiple data products, consider batching to reduce API calls:

.. code-block:: python

    # Create multiple drafts in a single data product
    dph_service.create_data_product(
        drafts=[draft1, draft2, draft3]
    )

**Caching**

Cache frequently accessed data to reduce API calls:

.. code-block:: python

    from functools import lru_cache
    
    @lru_cache(maxsize=100)
    def get_domain_cached(domain_id):
        return dph_service.get_domain(domain_id=domain_id)

**Parallel Processing**

Use concurrent requests for independent operations:

.. code-block:: python

    from concurrent.futures import ThreadPoolExecutor
    
    def get_product(product_id):
        return dph_service.get_data_product(data_product_id=product_id)
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        products = list(executor.map(get_product, product_ids))

Requirements
------------

- Python 3.8 or higher
- ibm-cloud-sdk-core >= 3.16.7
- requests >= 2.32.4
- python-dateutil >= 2.5.3

See Also
--------

- :ref:`dph_services_usage` - Detailed usage guide
- :ref:`dph_services_examples` - Code examples
- :ref:`api_dph_services` - API reference

.. Made with Bob
