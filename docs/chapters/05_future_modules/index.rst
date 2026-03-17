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

.. _future_modules:

Future Modules
==============

The ``IBM watsonx.data intelligence SDK`` is designed with a modular architecture that allows different teams to contribute specialized functionality while sharing common components like authentication.

Architecture for Extensibility
-------------------------------

The SDK's modular design enables:

* **Independent Development**: Teams can develop modules independently
* **Shared Infrastructure**: All modules use common authentication and configuration
* **Consistent API**: Modules follow the same design patterns
* **Easy Integration**: New modules integrate seamlessly with existing ones

Adding New Modules
------------------

Teams adding new modules should:

1. **Use Common Authentication**: Leverage the ``common.auth`` module for authentication
2. **Follow Naming Conventions**: Use clear, descriptive module names
3. **Provide Documentation**: Include comprehensive documentation following this structure
4. **Include Examples**: Provide working code examples
5. **Add Tests**: Include unit and integration tests

Documentation Structure for New Modules
----------------------------------------

When adding a new module, create documentation following this pattern:

.. code-block:: text

    docs/chapters/0X_module_name/
    ├── index.rst              # Module overview
    ├── core_concepts.rst      # Key concepts
    ├── usage.rst              # Usage guide
    ├── examples.rst           # Code examples
    └── api_reference.rst      # API documentation

API Reference Structure
~~~~~~~~~~~~~~~~~~~~~~~

Add API reference documentation:

.. code-block:: text

    docs/api/module_name/
    ├── index.rst              # API overview
    ├── classes.rst            # Main classes
    └── utilities.rst          # Utility functions

Planned Modules
---------------

While specific modules are still being defined, potential areas include:

* Data profiling and statistics
* Data lineage tracking
* Data catalog integration
* Additional data quality features
* Custom analytics capabilities

Contact
-------

If your team is planning to add a module to the SDK:

* Review the existing module structure (``dq_validator``)
* Follow the authentication patterns in ``common.auth``
* Coordinate with the SDK maintainers
* Submit documentation along with your module

For questions or to propose a new module:

* Email: data-intelligence-sdk@ibm.com
* GitHub: Open an issue or discussion

Contributing
------------

See the CONTRIBUTING.md file in the repository for detailed guidelines on:

* Code style and standards
* Testing requirements
* Documentation requirements
* Pull request process

We look forward to growing the SDK with contributions from teams across IBM!

.. Made with Bob
