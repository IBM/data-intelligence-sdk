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

.. _data_product_recommender_overview:

Overview
========

The Data Product Recommender analyzes query logs to identify high-value tables for data product creation.

Scoring Methodology
-------------------

Individual Table Scoring (0-100)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **37.5%** Query Count - Volume of usage
- **37.5%** User Diversity - Breadth of usage across teams
- **15%** Recency - Recent activity
- **10%** Consistency - Regular usage patterns

Table Group Scoring (0-100)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **30%** Cohesion - How tightly tables are connected
- **20%** Usage - Relative usage compared to other groups
- **15%** User Reach - Percentage of users querying the group
- **20%** Recency - Recent activity across tables
- **10%** Consistency - Regular usage patterns
- **5%** Size - Number of tables in the group

Star Rating Scale
~~~~~~~~~~~~~~~~~

- ⭐⭐⭐⭐⭐ **Excellent (80-100)**: Implement immediately
- ⭐⭐⭐⭐ **Good (60-79)**: Medium priority
- ⭐⭐⭐ **Fair (40-59)**: Consider splitting or implement later
- ⭐⭐ **Weak (20-39)**: Reconsider grouping
- ⭐ **Poor (0-19)**: Do not implement

Platform Support
----------------

- ✅ **Snowflake** - Export from SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
- ✅ **Databricks** - Export from system.query.history
- ✅ **BigQuery** - Export from INFORMATION_SCHEMA.JOBS_BY_PROJECT
- ✅ **watsonx.data** - Export from system.runtime.queries

See Also
--------

- :ref:`data_product_recommender_usage` - Usage guide
- :ref:`data_product_recommender_examples` - Examples
