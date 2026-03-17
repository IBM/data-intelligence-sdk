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

.. _api_dq_validator_integrations:

DataFrame Integration API
=========================

The integrations module provides DataFrame validators for Pandas and PySpark.

.. currentmodule:: wxdi.dq_validator.integrations

Base Integration
----------------

.. autoclass:: wxdi.dq_validator.integrations.base.DataFrameValidator
   :members:
   :undoc-members:
   :show-inheritance:

Pandas Integration
------------------

.. autoclass:: wxdi.dq_validator.integrations.pandas_validator.PandasValidator
   :members:
   :undoc-members:
   :show-inheritance:

PySpark Integration
-------------------

.. autoclass:: wxdi.dq_validator.integrations.spark_validator.SparkValidator
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

See :ref:`DataFrame Integration<dq_validator_dataframe_integration>` for detailed usage examples.

.. Made with Bob
