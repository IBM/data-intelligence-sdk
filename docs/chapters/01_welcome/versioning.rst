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

.. _versioning:

Versioning Policy
=================

The ``IBM watsonx.data intelligence SDK`` follows `Semantic Versioning 2.0.0 <https://semver.org/>`_.

Version Format
--------------

Version numbers are in the format ``MAJOR.MINOR.PATCH``, for example: ``0.5.0``

* **MAJOR** version: Incremented for incompatible API changes
* **MINOR** version: Incremented for new functionality in a backward-compatible manner
* **PATCH** version: Incremented for backward-compatible bug fixes

Pre-release Versions
--------------------

Pre-release versions may include additional labels:

* **Alpha** (``0.5.0-alpha.1``): Early development, API may change significantly
* **Beta** (``0.5.0-beta.1``): Feature complete, but may have bugs
* **Release Candidate** (``0.5.0-rc.1``): Final testing before release

Deprecation Policy
------------------

When we need to remove or change functionality:

1. **Deprecation Warning**: The feature is marked as deprecated in the current MINOR version
2. **Documentation**: Deprecation is documented in release notes with migration guidance
3. **Removal**: The feature is removed in the next MAJOR version

Example:

* Version 0.5.0: Feature X is marked as deprecated
* Version 0.6.0: Feature X still works but shows deprecation warnings
* Version 1.0.0: Feature X is removed

Backward Compatibility
----------------------

Within a MAJOR version:

* **MINOR** updates are backward compatible
* **PATCH** updates are backward compatible
* Existing code should continue to work without modifications

Breaking Changes
----------------

Breaking changes only occur in MAJOR version updates. When upgrading across MAJOR versions:

* Review the migration guide in the release notes
* Update your code to use new APIs
* Test thoroughly before deploying to production

Module Versioning
-----------------

The SDK uses a unified version number across all modules:

* **Common modules** (authentication, configuration)
* **DQ Validator module** (data quality validation)
* **Future modules** (as they are added)

All modules share the same version number to ensure compatibility.

Version History
---------------

See :ref:`Release Notes<release_notes>` for detailed version history and changes.

Checking Your Version
---------------------

To check your installed version:

.. code-block:: console

    $ pip show data-intelligence-sdk

Or in Python:

.. code-block:: python

    >>> import wxdi.dq_validator
    >>> print(dq_validator.__version__)
    0.5.0

Support Policy
--------------

* **Current Version**: Full support with bug fixes and new features
* **Previous MINOR Version**: Security fixes and critical bug fixes for 6 months
* **Older Versions**: No active support (upgrade recommended)

We recommend always using the latest version for the best experience and security.

.. Made with Bob
