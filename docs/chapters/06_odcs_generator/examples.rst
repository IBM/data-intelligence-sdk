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

.. _odcs_generator_examples:

Examples
========

Complete examples for ODCS Generator module.

Collibra Example
----------------

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
    odcs_data = generator.generate_odcs("019a57f9-62d2-7aa0-9f22-4fa2cea1180b")

    # Customize
    odcs_data['dataProduct'] = 'Customer Data Product'
    odcs_data['version'] = '2.0.0'

    # Save to file
    generator.save_to_yaml(odcs_data, "customer-data-odcs.yaml")

Informatica Example
-------------------

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
    odcs_data = generator.generate_odcs("asset-id-123")

    # Save to file
    generator.save_to_yaml(odcs_data, "output.yaml")

Batch Processing
----------------

.. code-block:: python

    from wxdi.odcs_generator.generate_odcs_from_collibra import CollibraClient, ODCSGenerator

    client = CollibraClient(base_url, username, password)
    generator = ODCSGenerator(client)

    asset_ids = ['id1', 'id2', 'id3']

    for asset_id in asset_ids:
        try:
            odcs_data = generator.generate_odcs(asset_id)
            generator.save_to_yaml(odcs_data, f"{asset_id}-odcs.yaml")
            print(f"✅ Generated ODCS for {asset_id}")
        except Exception as e:
            print(f"❌ Failed for {asset_id}: {e}")

See Also
--------

- :ref:`odcs_generator_collibra` - Collibra integration
- :ref:`odcs_generator_informatica` - Informatica integration
- :ref:`api_odcs_generator` - API reference
