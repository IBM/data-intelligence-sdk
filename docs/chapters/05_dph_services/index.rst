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

.. _dph_services:

Data Product Hub Services
==========================

Python client library for IBM Data Product Hub API, providing programmatic access to data product management, container operations, contract terms, and asset visualization.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   usage_guide
   examples

Overview
--------

The ``dph_services`` module provides a complete Python SDK for interacting with IBM Data Product Hub services. It enables developers to programmatically manage the entire data product lifecycle, from initialization to publication and retirement.

Key Features
------------

**Container Management**
   Initialize and configure data product containers with delivery methods, samples, and domain structures.

**Data Product Lifecycle**
   Create, update, publish, and retire data products with full version control and draft management.

**Contract Terms**
   Manage contract terms, documents, and templates for data product agreements.

**Asset Visualization**
   Create and manage data asset visualizations for better data discovery.

**Domain Organization**
   Organize data products into domains and subdomains for better categorization.

**Release Management**
   Handle data product releases with versioning and retirement capabilities.

Quick Start
-----------

.. code-block:: python

    from wxdi.dph_services import DphV1
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

    # Initialize authenticator
    authenticator = IAMAuthenticator('your-api-key')

    # Create service instance
    dph_service = DphV1(authenticator=authenticator)
    dph_service.set_service_url('https://your-dph-instance.com')

    # Initialize container
    response = dph_service.initialize(
        include=['delivery_methods', 'data_product_samples', 'domains_multi_industry']
    )

    # Create a data product
    data_product = dph_service.create_data_product(
        drafts=[{
            'version': '1.0.0',
            'name': 'Customer Analytics Data Product',
            'description': 'Comprehensive customer analytics dataset',
            'asset': {
                'id': 'asset-123',
                'container': {'id': 'container-456'}
            }
        }]
    )

Use Cases
---------

**Data Product Onboarding**
   Automate the creation and configuration of new data products in your data marketplace.

**Lifecycle Automation**
   Build workflows that automatically promote drafts to releases based on quality checks.

**Contract Management**
   Programmatically manage data sharing agreements and terms of use.

**Catalog Integration**
   Integrate with data catalogs to automatically create data products from existing assets.

**Governance Workflows**
   Implement approval workflows and governance policies for data product publication.

Next Steps
----------

- :ref:`dph_services_usage` - Detailed usage guide with examples
- :ref:`dph_services_examples` - Practical code examples
- :ref:`api_dph_services` - Complete API reference

.. Made with Bob
