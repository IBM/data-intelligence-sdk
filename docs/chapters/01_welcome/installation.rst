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

.. _installation:

Installation and Versioning
============================

Installation of the ``IBM watsonx.data intelligence SDK`` for Python is managed through pip or from source.

Installation via pip
--------------------

Once the package is published to PyPI, you can install the latest release:

.. code-block:: console

    $ pip install data-intelligence-sdk

Installation from Source
-------------------------

To install the SDK from source (recommended for development or pre-release versions):

.. code-block:: console

    $ git clone https://github.com/IBM/data-intelligence-sdk.git
    $ cd data-intelligence-sdk
    $ pip install -e .

Installing with Optional Dependencies
--------------------------------------

The SDK supports optional dependencies for different use cases:

Pandas Support
~~~~~~~~~~~~~~

To use the SDK with Pandas DataFrames:

.. code-block:: console

    $ pip install -e ".[pandas]"

PySpark Support
~~~~~~~~~~~~~~~

To use the SDK with PySpark DataFrames:

.. code-block:: console

    $ pip install -e ".[spark]"

Both DataFrame Libraries
~~~~~~~~~~~~~~~~~~~~~~~~~

To install support for both Pandas and PySpark:

.. code-block:: console

    $ pip install -e ".[dataframes]"

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~

To install all dependencies including development tools:

.. code-block:: console

    $ pip install -e ".[dev]"

Complete Installation
~~~~~~~~~~~~~~~~~~~~~

To install everything (all optional dependencies and development tools):

.. code-block:: console

    $ pip install -e ".[all]"

Verifying Installation
----------------------

To verify that the SDK is installed correctly:

.. code-block:: python

    >>> import wxdi.dq_validator
    >>> from wxdi.common.auth import AuthProvider
    >>> print(dq_validator.__version__)
    0.5.0

Versioning
----------

The ``IBM watsonx.data intelligence SDK`` for Python adheres to `Semantic Versioning <https://semver.org/>`_.

Version numbers follow the format ``MAJOR.MINOR.PATCH``:

* **MAJOR** version increments indicate incompatible API changes
* **MINOR** version increments add functionality in a backward-compatible manner
* **PATCH** version increments include backward-compatible bug fixes

Current Version
~~~~~~~~~~~~~~~

The current version of the SDK is **0.5.0**.

Checking Your Version
~~~~~~~~~~~~~~~~~~~~~

To check which version of the SDK you have installed:

.. code-block:: console

    $ pip show data-intelligence-sdk

Or programmatically:

.. code-block:: python

    >>> import wxdi.dq_validator
    >>> print(dq_validator.__version__)
    0.5.0

Upgrading
---------

To upgrade to the latest version:

.. code-block:: console

    $ pip install --upgrade data-intelligence-sdk

Or if installing from source:

.. code-block:: console

    $ cd data-intelligence-sdk
    $ git pull
    $ pip install -e . --upgrade

Uninstalling
------------

To uninstall the SDK:

.. code-block:: console

    $ pip uninstall data-intelligence-sdk

Next Steps
----------

Now that you have the SDK installed, check out the :ref:`Overview<overview>` section to learn about the SDK's features, or jump straight to the :ref:`Common Modules<common_modules>` section to set up authentication.

.. Made with Bob
