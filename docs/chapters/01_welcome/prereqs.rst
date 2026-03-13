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

.. _prerequisites:

Prerequisites
=============

Before installing the ``IBM watsonx.data intelligence SDK``, ensure your environment meets the following requirements:

Python Version
--------------

The SDK requires **Python 3.8 or higher**. We recommend using Python 3.10 or later for the best experience.

To check your Python version:

.. code-block:: console

    $ python --version
    Python 3.10.0

Core Dependencies
-----------------

The SDK has the following core dependencies that will be automatically installed:

* **pydantic** (>=2.12.0) - Data validation and settings management
* **requests** (>=2.28.0) - HTTP library for API calls
* **regex** (>=2023.0.0) - Advanced regular expression support
* **ibm-cloud-sdk-core** (>=3.24.4) - IBM Cloud SDK core functionality

Optional Dependencies
---------------------

Depending on your use case, you may want to install additional dependencies:

For Pandas DataFrame Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    $ pip install pandas>=1.3.0

For PySpark DataFrame Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    $ pip install pyspark>=3.0.0

For Development
~~~~~~~~~~~~~~~

If you plan to contribute to the SDK or run tests:

.. code-block:: console

    $ pip install pytest>=7.0.0 pytest-cov>=4.0.0 pytest-mock>=3.7.0
    $ pip install black>=23.0.0 mypy>=1.0.0 flake8>=6.0.0

Environment Setup
-----------------

Virtual Environment (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We strongly recommend using a virtual environment to avoid dependency conflicts:

.. code-block:: console

    $ python -m venv venv
    $ source venv/bin/activate  # On Windows: venv\Scripts\activate

IBM Cloud Account (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you plan to use the REST API integration features with IBM Cloud Pak for Data, you'll need:

* An IBM Cloud account or on-premises IBM Cloud Pak for Data installation
* Appropriate API credentials (API key, username/password, or Zen API key)
* Network access to your IBM Cloud Pak for Data instance

Next Steps
----------

Once you've verified the prerequisites, proceed to :ref:`Installation and Versioning<installation>` to install the SDK.

.. Made with Bob
