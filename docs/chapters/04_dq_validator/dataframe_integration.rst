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

.. _dq_validator_dataframe_integration:

DataFrame Integration
=====================

The DQ Validator module provides seamless integration with Pandas and PySpark DataFrames.

.. note::
   This section provides an overview. Detailed API documentation is available in the :ref:`API Reference<api_ref>`.

Pandas Integration
------------------

Memory-efficient chunked processing for Pandas DataFrames:

.. code-block:: python

    from wxdi.dq_validator.integrations import PandasValidator

    validator = PandasValidator(metadata)
    validator.add_rule(rule)
    
    result_df = validator.validate_dataframe(df, chunk_size=1000)

PySpark Integration
-------------------

Distributed validation using Spark UDFs:

.. code-block:: python

    from wxdi.dq_validator.integrations import SparkValidator

    validator = SparkValidator(metadata)
    validator.add_rule(rule)
    
    result_df = validator.validate_dataframe(spark_df)

For detailed usage examples and API documentation, see the :ref:`API Reference<api_ref>`.

.. Made with Bob
