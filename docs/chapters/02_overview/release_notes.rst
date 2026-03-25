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

Version 1.0.0 (Current)
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

There are no previous versions.

Upgrade Guide
-------------

There are no upgrades.

Deprecation Notices
-------------------

No features are currently deprecated. Future deprecations will be announced here with migration guidance.

Future Releases
---------------

We have plans to extend functionality 

Stay Updated
------------

* Check this page regularly for new releases
* Subscribe to the GitHub repository for notifications
* Join the IBM watsonx.data intelligence community for discussions

Feedback
--------

We welcome your feedback! Please report issues or suggest features through:

* GitHub Issues: https://github.com/IBM/data-intelligence-sdk/issues
* Email: Data_Intelligence_SDK@wwpdl.vnet.ibm.com

.. Made with Bob
