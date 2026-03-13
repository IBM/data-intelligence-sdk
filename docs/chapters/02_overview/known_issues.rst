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

.. _known_issues:

Known Issues and Limitations
=============================

This page documents known issues, limitations, and workarounds for the ``IBM watsonx.data intelligence SDK``.

Current Known Issues
--------------------

Version 0.5.0
~~~~~~~~~~~~~

**Performance**

* **Large Regex Patterns**: Complex regex patterns in RegexCheck may impact performance on large datasets
  
  * *Workaround*: Simplify regex patterns or use FormatCheck for common formats
  * *Status*: Performance optimization planned for v0.6.0

* **PySpark Broadcast Variables**: Very large metadata objects may cause memory issues when broadcast to workers
  
  * *Workaround*: Keep metadata objects minimal, avoid unnecessary column definitions
  * *Status*: Investigating optimization strategies

**DataFrame Integration**

* **Pandas Chunk Size**: Default chunk size (1000) may not be optimal for all datasets
  
  * *Workaround*: Experiment with different chunk sizes based on your data and memory
  * *Status*: Working on adaptive chunk sizing

* **PySpark Struct Columns**: Nested struct columns in validation results may be difficult to query
  
  * *Workaround*: Use ``explode()`` or ``select()`` to access nested fields
  * *Status*: Considering flattened output option

**REST API Integration**

* **Token Refresh**: In rare cases, token refresh may fail during long-running operations
  
  * *Workaround*: Implement retry logic in your application
  * *Status*: Improving token management in v0.6.0

* **Rate Limiting**: No built-in rate limiting for API calls
  
  * *Workaround*: Implement your own rate limiting if making many concurrent requests
  * *Status*: Planned for v0.7.0

**Type Inference**

* **Ambiguous Formats**: Some date/time formats may be ambiguous (e.g., MM/DD vs DD/MM)
  
  * *Workaround*: Use explicit format specifications in FormatCheck
  * *Status*: Considering locale-aware format detection

Current Limitations
-------------------

Platform Support
~~~~~~~~~~~~~~~~

* **Operating Systems**: Tested on Linux, macOS, and Windows. Some features may behave differently on Windows
* **Python Versions**: Python 3.8+ supported, but some type hints require 3.10+
* **Architecture**: Primarily tested on x86_64, limited testing on ARM

DataFrame Support
~~~~~~~~~~~~~~~~~

* **Pandas Versions**: Tested with Pandas 1.3.0+, some features may not work with older versions
* **PySpark Versions**: Tested with PySpark 3.0.0+, older versions not supported
* **Dask**: Not currently supported (planned for future release)
* **Polars**: Not currently supported (under consideration)

Validation Checks
~~~~~~~~~~~~~~~~~

* **Custom Checks**: Limited documentation for creating complex custom checks
* **Check Combinations**: No built-in support for combining multiple checks with AND/OR logic
* **Conditional Validation**: No built-in support for conditional validation rules

REST API Integration
~~~~~~~~~~~~~~~~~~~~

* **API Versions**: Tested with specific IBM Cloud Pak for Data versions, compatibility with older versions not guaranteed
* **Batch Operations**: Limited support for batch operations (creating multiple checks at once)
* **Async Operations**: No async/await support for API calls

Data Types
~~~~~~~~~~

* **Complex Types**: Limited support for complex nested data types
* **Binary Data**: No validation support for binary data types
* **JSON/XML**: No built-in validation for JSON or XML structure

Workarounds and Best Practices
-------------------------------

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

For large datasets:

.. code-block:: python

    # Use appropriate chunk sizes
    validator.validate_dataframe(df, chunk_size=5000)  # Adjust based on memory
    
    # Or use PySpark for very large datasets
    from wxdi.dq_validator.integrations import SparkValidator
    spark_validator = SparkValidator(metadata)
    result_df = spark_validator.validate_dataframe(spark_df)

Memory Management
~~~~~~~~~~~~~~~~~

For memory-constrained environments:

.. code-block:: python

    # Process in smaller chunks
    for chunk in pd.read_csv('large_file.csv', chunksize=1000):
        results = validator.validate_dataframe(chunk)
        # Process results immediately
        process_results(results)

Error Handling
~~~~~~~~~~~~~~

Implement robust error handling:

.. code-block:: python

    from requests.exceptions import RequestException
    
    try:
        provider = GlossaryProvider(config)
        terms = provider.get_glossary_terms()
    except RequestException as e:
        # Handle network errors
        logger.error(f"API call failed: {e}")
        # Implement retry logic or fallback

Type Checking
~~~~~~~~~~~~~

For better type safety:

.. code-block:: python

    # Use type hints and mypy
    from typing import List
    from wxdi.dq_validator import ValidationResult
    
    def process_results(results: List[ValidationResult]) -> None:
        # Your code here with full type checking
        pass

Reporting Issues
----------------

If you encounter an issue not listed here:

1. **Check GitHub Issues**: Search existing issues to see if it's already reported
2. **Verify Your Setup**: Ensure you're using supported versions of Python and dependencies
3. **Create Minimal Reproduction**: Prepare a minimal code example that reproduces the issue
4. **Report the Issue**: Open a new issue on GitHub with:
   
   * Clear description of the problem
   * Steps to reproduce
   * Expected vs actual behavior
   * Environment details (Python version, OS, SDK version)
   * Error messages and stack traces

Planned Improvements
--------------------

Version 0.6.0
~~~~~~~~~~~~~

* Performance optimizations for regex validation
* Improved token management
* Adaptive chunk sizing for Pandas
* Enhanced error messages

Version 0.7.0
~~~~~~~~~~~~~

* Rate limiting for API calls
* Batch operations support
* Async/await support for API calls
* Additional DataFrame backends (Dask consideration)

Version 1.0.0
~~~~~~~~~~~~~

* Stable API with backward compatibility guarantees
* Comprehensive test coverage
* Production-ready performance
* Full documentation with advanced examples

Compatibility Matrix
--------------------

Tested Configurations
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 20 20

   * - Python
     - Pandas
     - PySpark
     - OS
     - Status
   * - 3.8
     - 1.3.x
     - 3.0.x
     - Linux
     - ✓ Supported
   * - 3.9
     - 1.4.x
     - 3.1.x
     - Linux
     - ✓ Supported
   * - 3.10
     - 1.5.x
     - 3.2.x
     - Linux/macOS
     - ✓ Supported
   * - 3.11
     - 2.0.x
     - 3.3.x
     - Linux/macOS
     - ✓ Supported
   * - 3.12
     - 2.1.x
     - 3.4.x
     - Linux/macOS/Windows
     - ✓ Supported

Untested Configurations
~~~~~~~~~~~~~~~~~~~~~~~

The following configurations may work but are not officially tested:

* Python 3.7 (end of life)
* Pandas < 1.3.0
* PySpark < 3.0.0
* ARM architecture
* BSD operating systems

Getting Help
------------

If you're experiencing issues:

* Review the :ref:`FAQ<faq>` for common questions
* Check the :ref:`API Reference<api_ref>` for detailed documentation
* Search GitHub issues for similar problems
* Open a new issue with detailed information
* Contact: data-intelligence-sdk@ibm.com

We appreciate your patience as we continue to improve the SDK!

.. Made with Bob
