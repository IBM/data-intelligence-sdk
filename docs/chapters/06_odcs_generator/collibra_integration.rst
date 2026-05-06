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

.. _odcs_generator_collibra:

Collibra Integration
====================

Generate ODCS files from Collibra data catalog assets.

Overview
--------

The Collibra integration extracts metadata from Collibra assets and generates ODCS v3.1.0 compliant YAML files.

Features
--------

- ✅ Automatic metadata extraction via REST API
- ✅ Column discovery through asset relations
- ✅ Data type mapping (logical and physical)
- ✅ Classification support via GraphQL API
- ✅ Tag integration at asset and column levels
- ✅ Custom attribute preservation

Installation
------------

.. code-block:: bash

    pip install -e .

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    export COLLIBRA_URL="https://your-instance.collibra.com"
    export COLLIBRA_USERNAME="your_username"
    export COLLIBRA_PASSWORD="your_password"

Required Permissions
~~~~~~~~~~~~~~~~~~~~

- Read access to assets
- Read access to attributes
- Read access to relations
- Access to GraphQL API
- Read access to tags

Usage
-----

Command Line
~~~~~~~~~~~~

.. code-block:: bash

    python -m wxdi.odcs_generator.generate_odcs_from_collibra <asset_id>

With options:

.. code-block:: bash

    python -m wxdi.odcs_generator.generate_odcs_from_collibra <asset_id> \
      --output my-contract.yaml \
      --url https://collibra.com \
      --username myuser \
      --password mypass

Python API
~~~~~~~~~~

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

See Also
--------

- :ref:`odcs_generator_examples` - Complete examples
- :ref:`api_odcs_generator` - API reference
