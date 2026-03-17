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

.. _faq:

Frequently Asked Questions
==========================

General Questions
-----------------

What is the IBM watsonx.data intelligence SDK?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The IBM watsonx.data intelligence SDK is a comprehensive Python toolkit for data intelligence operations. It provides modular components for data quality validation, authentication, and other data-related tasks. The SDK is designed with a modular architecture that allows different teams to contribute specialized functionality.

Which Python versions are supported?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SDK supports Python 3.8 and higher. We recommend using Python 3.10 or later for the best experience.

Is the SDK open source?
~~~~~~~~~~~~~~~~~~~~~~~~

Yes, the SDK is open source and available under the Apache 2.0 license. You can find the source code on GitHub.

Installation and Setup
----------------------

How do I install the SDK?
~~~~~~~~~~~~~~~~~~~~~~~~~~

You can install the SDK using pip:

.. code-block:: console

    $ pip install data-intelligence-sdk

Or from source:

.. code-block:: console

    $ git clone https://github.com/IBM/data-intelligence-sdk.git
    $ cd data-intelligence-sdk
    $ pip install -e .

See :ref:`Installation<installation>` for more details.

Do I need to install optional dependencies?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It depends on your use case:

* For Pandas DataFrame support: ``pip install -e ".[pandas]"``
* For PySpark DataFrame support: ``pip install -e ".[spark]"``
* For both: ``pip install -e ".[dataframes]"``
* For everything: ``pip install -e ".[all]"``

Authentication
--------------

Which authentication methods are supported?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SDK supports multiple authentication methods:

* **IBM Cloud**: IAM authentication with API keys
* **AWS Cloud**: AWS-specific authentication
* **Government Cloud**: Specialized government authentication
* **On-Premises**: Username/password or Zen API key

See :ref:`Authentication<authentication>` for detailed examples.

How do I authenticate with IBM Cloud?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``AuthProvider`` with your IBM Cloud credentials:

.. code-block:: python

    from wxdi.common.auth import AuthProvider, AuthConfig, CloudEnvironment

    config = AuthConfig(
        base_url="https://api.dataplatform.cloud.ibm.com",
        username="your-username",
        api_key="your-api-key",
        environment=CloudEnvironment.IBM_CLOUD
    )
    
    auth_provider = AuthProvider(config)

Can I use the SDK without IBM Cloud?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes! The DQ Validator module works completely independently for in-memory validation. You only need authentication if you want to use the REST API integration features with IBM Cloud Pak for Data.

Data Quality Validation
-----------------------

What types of data can I validate?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SDK supports three types of data:

1. **Array-based records**: Lists of values (optimized for streaming)
2. **Pandas DataFrames**: In-memory DataFrames
3. **PySpark DataFrames**: Distributed DataFrames

What validation checks are available?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SDK provides 9 validation check types:

1. LengthCheck - String length validation
2. ValidValuesCheck - Allowed values validation
3. ComparisonCheck - Value comparison
4. CaseCheck - Character case validation
5. CompletenessCheck - Non-null validation
6. RangeCheck - Numeric range validation
7. RegexCheck - Regular expression matching
8. FormatCheck - Format validation (dates, emails, etc.)
9. DataTypeCheck - Data type validation

Can I create custom validation checks?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes! Extend the ``BaseCheck`` class to create custom validation logic:

.. code-block:: python

    from wxdi.dq_validator.base import BaseCheck, ValidationError
    from wxdi.dq_validator.data_quality_dimension import DataQualityDimension

    class MyCustomCheck(BaseCheck):
        def __init__(self):
            super().__init__(DataQualityDimension.VALIDITY)
        
        def validate(self, value, context):
            # Your validation logic here
            if not my_validation_logic(value):
                return ValidationError(
                    check_name="MyCustomCheck",
                    column_name=context.get("column_name"),
                    value=value,
                    message="Validation failed"
                )
            return None

DataFrame Integration
---------------------

How does Pandas integration work?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SDK processes Pandas DataFrames in chunks for memory efficiency:

.. code-block:: python

    from wxdi.dq_validator.integrations import PandasValidator

    validator = PandasValidator(metadata)
    validator.add_rule(rule)
    
    result_df = validator.validate_dataframe(df, chunk_size=1000)

The result is a new DataFrame with a validation result column.

Can I use the SDK with large DataFrames?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes! The SDK is designed for large datasets:

* **Pandas**: Chunked processing handles millions of rows efficiently
* **PySpark**: Distributed processing scales to billions of rows

How do I handle validation results?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Validation results are returned as a struct column containing:

* ``validation_score``: Overall score (0-100)
* ``pass_rate``: Percentage of checks passed
* ``total_checks``: Number of checks performed
* ``passed_checks``: Number of checks passed
* ``failed_checks``: Number of checks failed
* ``errors``: List of validation errors

REST API Integration
--------------------

What is the REST API integration for?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The REST API integration allows you to:

* Fetch data quality rules from IBM Cloud Pak for Data glossary
* Load data asset metadata from CAMS
* Report validation issues back to the platform
* Search for data quality checks and assets

Do I need REST API integration?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No, it's optional. The core validation functionality works independently. Use REST API integration if you want to integrate with IBM Cloud Pak for Data.

Performance
-----------

How fast is the validation?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Performance depends on:

* Number of validation rules
* Complexity of checks
* Data size
* Hardware resources

Typical performance:

* **Array records**: 10,000+ records/second
* **Pandas**: 100,000+ rows/second (chunked)
* **PySpark**: Scales linearly with cluster size

How can I improve performance?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Use appropriate chunk sizes for Pandas (default: 1000)
2. Use PySpark for very large datasets
3. Minimize the number of validation rules
4. Use simpler checks when possible
5. Consider parallel processing for multiple datasets

Troubleshooting
---------------

I'm getting import errors
~~~~~~~~~~~~~~~~~~~~~~~~~~

Make sure you've installed the SDK and any required optional dependencies:

.. code-block:: console

    $ pip install data-intelligence-sdk
    $ pip install pandas  # If using Pandas
    $ pip install pyspark  # If using PySpark

My validation is slow
~~~~~~~~~~~~~~~~~~~~~

Try these optimizations:

1. Reduce chunk size for Pandas
2. Use PySpark for large datasets
3. Profile your validation rules
4. Check for expensive regex patterns
5. Consider caching metadata

I'm getting authentication errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check:

1. Your credentials are correct
2. You have network access to the API endpoint
3. Your API key hasn't expired
4. SSL verification settings (for on-premises)

Where can I get help?
~~~~~~~~~~~~~~~~~~~~~

* Check the :ref:`API Reference<api_ref>` documentation
* Review the code examples in the repository
* Open an issue on GitHub
* Contact the development team

Contributing
------------

Can I contribute to the SDK?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes! We welcome contributions. Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

See the CONTRIBUTING.md file in the repository for detailed guidelines.

How do I report bugs?
~~~~~~~~~~~~~~~~~~~~~

Please open an issue on GitHub with:

* Description of the bug
* Steps to reproduce
* Expected vs actual behavior
* Python version and SDK version
* Any relevant error messages

Can I request features?
~~~~~~~~~~~~~~~~~~~~~~~~

Yes! Open a feature request on GitHub with:

* Description of the feature
* Use case and benefits
* Any implementation ideas

Still Have Questions?
---------------------

If your question isn't answered here:

* Check the :ref:`API Reference<api_ref>`
* Review the code examples
* Open an issue on GitHub
* Contact: data-intelligence-sdk@ibm.com

.. Made with Bob
