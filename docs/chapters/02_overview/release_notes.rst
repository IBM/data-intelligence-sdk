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

.. _release_notes:

Release Notes
=============

This page documents the release history and changes for the ``IBM watsonx.data intelligence SDK``.

Version 0.5.0 (Current)
-----------------------

*Release Date: March 2026*

This is the initial public release of the IBM watsonx.data intelligence SDK.

New Features
~~~~~~~~~~~~

**Common Modules**

* Multi-environment authentication support (IBM Cloud, AWS Cloud, Government Cloud, On-Premises)
* Type-safe authentication configuration with Pydantic models
* Automatic token management and refresh
* Thread-safe session handling
* SSL verification control for on-premises deployments

**DQ Validator Module**

* Core validation engine for array-based records
* Metadata-driven validation with AssetMetadata and ColumnMetadata
* Nine comprehensive validation check types:
  
  * LengthCheck
  * ValidValuesCheck
  * ComparisonCheck
  * CaseCheck
  * CompletenessCheck
  * RangeCheck
  * RegexCheck
  * FormatCheck
  * DataTypeCheck

* Data quality dimension tracking (8 standard dimensions)
* Pandas DataFrame integration with chunked processing
* PySpark DataFrame integration with distributed validation
* REST API integration with IBM Cloud Pak for Data:
  
  * GlossaryProvider
  * CamsProvider
  * AssetsProvider
  * DimensionsProvider
  * ChecksProvider
  * IssuesProvider
  * DQSearchProvider

* Result consolidation and aggregation
* Issue reporting and tracking
* Comprehensive type hints throughout

Documentation
~~~~~~~~~~~~~

* Complete API reference documentation
* User guides for all modules
* Code examples for common use cases
* Installation and setup guides

Known Issues
~~~~~~~~~~~~

See :ref:`Known Issues<known_issues>` for current limitations.

Previous Versions
-----------------

Version 0.4.0 (Beta)
~~~~~~~~~~~~~~~~~~~~

*Release Date: February 2026*

* Beta release for internal testing
* Core validation engine implementation
* Basic DataFrame integration
* Initial REST API providers

Version 0.3.0 (Alpha)
~~~~~~~~~~~~~~~~~~~~~

*Release Date: January 2026*

* Alpha release for early adopters
* Prototype validation checks
* Authentication framework

Version 0.2.0 (Alpha)
~~~~~~~~~~~~~~~~~~~~~

*Release Date: December 2025*

* Initial alpha release
* Basic validation framework
* Proof of concept

Version 0.1.0 (Pre-Alpha)
~~~~~~~~~~~~~~~~~~~~~~~~~

*Release Date: November 2025*

* Initial development version
* Project structure and architecture

Upgrade Guide
-------------

From 0.4.x to 0.5.0
~~~~~~~~~~~~~~~~~~~

**Breaking Changes**

* Authentication configuration now uses Pydantic models instead of dictionaries
* ValidationResult structure has been enhanced with additional fields
* Some provider method signatures have changed for consistency

**Migration Steps**

1. Update authentication configuration:

   .. code-block:: python

       # Old (0.4.x)
       config = {
           'base_url': 'https://api.example.com',
           'username': 'user',
           'api_key': 'key'
       }

       # New (0.5.0)
       from wxdi.common.auth import AuthConfig
       config = AuthConfig(
           base_url='https://api.example.com',
           username='user',
           api_key='key'
       )

2. Update ValidationResult usage:

   .. code-block:: python

       # Old (0.4.x)
       score = result.score

       # New (0.5.0)
       score = result.validation_score
       pass_rate = result.pass_rate  # New field

3. Review provider method signatures in the API documentation

Deprecation Notices
-------------------

No features are currently deprecated. Future deprecations will be announced here with migration guidance.

Future Releases
---------------

Planned for Version 0.6.0
~~~~~~~~~~~~~~~~~~~~~~~~~

* Enhanced error messages with suggestions
* Performance optimizations for large datasets
* Additional validation check types
* Improved documentation with more examples

Planned for Version 1.0.0
~~~~~~~~~~~~~~~~~~~~~~~~~

* Stable API with backward compatibility guarantees
* Additional modules from partner teams
* Enhanced integration capabilities
* Production-ready performance and reliability

Stay Updated
------------

* Check this page regularly for new releases
* Subscribe to the GitHub repository for notifications
* Join the IBM watsonx.data intelligence community for discussions

Feedback
--------

We welcome your feedback! Please report issues or suggest features through:

* GitHub Issues: https://github.com/IBM/data-intelligence-sdk/issues
* Email: data-intelligence-sdk@ibm.com

.. Made with Bob
