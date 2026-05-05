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

.. _odcs_generator_informatica:

Informatica Integration
========================

Generate ODCS files from Informatica CDGC (Cloud Data Governance and Catalog) assets.

Overview
--------

The Informatica integration extracts metadata from Informatica CDGC and generates ODCS v3.1.0 compliant YAML files.

Features
--------

- ✅ Asset metadata extraction via REST API
- ✅ Column schema discovery
- ✅ System attribute handling
- ✅ Technical metadata extraction
- ✅ Business glossary term integration

Installation
------------

.. code-block:: bash

    pip install -e .

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    export INFORMATICA_URL="https://your-informatica-instance.com"
    export INFORMATICA_USERNAME="your_username"
    export INFORMATICA_PASSWORD="your_password"

Usage
-----

Command Line
~~~~~~~~~~~~

.. code-block:: bash

    python -m wxdi.odcs_generator.generate_odcs_from_informatica <asset_id>

Python API
~~~~~~~~~~

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

    # Save to file
    generator.save_to_yaml(odcs_data, "output.yaml")

See Also
--------

- :ref:`odcs_generator_examples` - Complete examples
- :ref:`api_odcs_generator` - API reference
