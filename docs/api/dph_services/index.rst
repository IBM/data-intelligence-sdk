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

.. _api_dph_services:

DPH Services API
================

API reference for the Data Product Hub Services module.

.. toctree::
   :maxdepth: 2

   core

Main Service Class
------------------

.. currentmodule:: wxdi.dph_services

.. autoclass:: DphV1
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Container Operations
--------------------

.. automethod:: DphV1.initialize
.. automethod:: DphV1.get_initialize_status
.. automethod:: DphV1.get_service_id_credentials
.. automethod:: DphV1.manage_api_keys

Data Product Operations
-----------------------

.. automethod:: DphV1.create_data_product
.. automethod:: DphV1.list_data_products
.. automethod:: DphV1.list_data_products_with_pager
.. automethod:: DphV1.get_data_product
.. automethod:: DphV1.update_data_product
.. automethod:: DphV1.delete_data_product

Draft Operations
----------------

.. automethod:: DphV1.create_data_product_draft
.. automethod:: DphV1.list_data_product_drafts
.. automethod:: DphV1.get_data_product_draft
.. automethod:: DphV1.update_data_product_draft
.. automethod:: DphV1.delete_data_product_draft
.. automethod:: DphV1.publish_data_product_draft

Release Operations
------------------

.. automethod:: DphV1.list_data_product_releases
.. automethod:: DphV1.get_data_product_release
.. automethod:: DphV1.update_data_product_release
.. automethod:: DphV1.retire_data_product_release

Contract Terms Operations
-------------------------

.. automethod:: DphV1.create_draft_contract_terms_document
.. automethod:: DphV1.get_data_product_draft_contract_terms
.. automethod:: DphV1.update_draft_contract_terms_document
.. automethod:: DphV1.delete_draft_contract_terms_document

Domain Operations
-----------------

.. automethod:: DphV1.list_data_product_domains
.. automethod:: DphV1.create_data_product_domain
.. automethod:: DphV1.create_data_product_subdomain
.. automethod:: DphV1.get_domain
.. automethod:: DphV1.update_data_product_domain
.. automethod:: DphV1.delete_domain

Asset Visualization Operations
-------------------------------

.. automethod:: DphV1.create_data_asset_visualization
.. automethod:: DphV1.reinitiate_data_asset_visualization

Contract Template Operations
----------------------------

.. automethod:: DphV1.create_contract_template
.. automethod:: DphV1.list_data_product_contract_template
.. automethod:: DphV1.get_contract_template
.. automethod:: DphV1.update_data_product_contract_template
.. automethod:: DphV1.delete_data_product_contract_template

.. Made with Bob