<!--
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
-->
# IBM watsonx.data intelligence SDK Version 1.0.0

A comprehensive Python SDK for performing data quality validations on streaming data records (arrays), Pandas DataFrames, and PySpark DataFrames with complete REST API integration for IBM Cloud Pak for Data.

## Features

### Core Validation
- **Array-based Records**: Optimized for streaming data where records are arrays of values
- **Metadata-driven**: Define table structure and column mappings once
- **Fluent API**: Chainable method calls for intuitive rule definition
- **Score-based Results**: Each validation returns detailed scores and pass rates
- **Data Quality Dimensions**: Track validation checks by 8 standard DQ dimensions (Accuracy, Completeness, Conformity, Consistency, Coverage, Timeliness, Uniqueness, Validity)
- **Nine Validation Checks**: Comprehensive validation coverage
  - **LengthCheck**: Validates length of any value (converts to string)
  - **ValidValuesCheck**: Validates against allowed list with case-insensitive option
  - **ComparisonCheck**: Compares values using operators, supports all types
  - **CaseCheck**: Validates character case (upper, lower, name, sentence)
  - **CompletenessCheck**: Validates presence (non-null) of values
  - **RangeCheck**: Validates values within min/max range
  - **RegexCheck**: Validates values match regular expression patterns
  - **FormatCheck**: Validates value formats using intelligent format detection
  - **DataTypeCheck**: Validates data types with intelligent type inference
- **Type Safety**: Full type hints throughout
- **Extensible**: Easy to add new checks via BaseCheck

### DataFrame Integration
- **Pandas Support**: Memory-efficient chunked processing for large DataFrames
- **PySpark Support**: Distributed validation using Spark UDFs
- **Consistent API**: Same interface for both Pandas and PySpark
- **Struct Column Output**: Single validation result column containing all metrics
- **Scalable**: Handles DataFrames from thousands to billions of rows

### REST API Integration
- **GlossaryProvider**: Fetch glossary terms and data quality constraints from IBM Cloud Pak for Data
- **CamsProvider**: Fetch data assets from CAMS (Catalog Asset Management System)
- **IssuesProvider**: Manage data quality issues (occurrences, tested records, ignored status)
- **DQSearchProvider**: Search for DQ checks and assets by native ID
- **Thread-Safe**: Concurrent access support with thread-local sessions

### Authentication
- **Multi-Environment Support**: IBM Cloud, AWS Cloud, Government Cloud, and On-Premises
- **Automatic Protocol Handling**: Environment-specific authentication methods
- **Type-Safe Configuration**: Full type hints and validation
- **SSL Control**: Configurable SSL verification for on-premises

## Installation

### From Source

```bash
git clone https://github.com/IBM/data-intelligence-sdk.git
cd data-intelligence-sdk
pip install -e .
```

### With DataFrame Support

```bash
# Install with Pandas support
pip install -e ".[pandas]"

# Install with PySpark support
pip install -e ".[spark]"

# Install with both Pandas and PySpark
pip install -e ".[dataframes]"

# Install everything (including dev dependencies)
pip install -e ".[all]"
```

### For Development

```bash
pip install -e ".[dev]"
```

## Quick Start

### Array-based Validation

```python
from wxdi.dq_validator import (
    AssetMetadata, ColumnMetadata, DataType,
    Validator, ValidationRule,
    ComparisonCheck, ComparisonOperator, ValidValuesCheck, LengthCheck
)

# 1. Define asset metadata
metadata = AssetMetadata(
    table_name='employee_data',
    columns=[
        ColumnMetadata('emp_id', DataType.INTEGER),
        ColumnMetadata('name', DataType.STRING, length=100),
        ColumnMetadata('age', DataType.INTEGER),
        ColumnMetadata('department', DataType.STRING, length=50),
        ColumnMetadata('salary', DataType.DECIMAL, precision=10, scale=2),
    ]
)

# 2. Create validator with rules
validator = Validator(metadata)

# Add validation rules
validator.add_rule(
    ValidationRule('name')
        .add_check(LengthCheck(min_length=2, max_length=100))
)

validator.add_rule(
    ValidationRule('department')
        .add_check(ValidValuesCheck(
            ['Engineering', 'Sales', 'HR', 'Finance'],
            case_sensitive=False  # Default is False
        ))
)

validator.add_rule(
    ValidationRule('age')
        .add_check(ComparisonCheck(
            operator=ComparisonOperator.GREATER_THAN_OR_EQUAL,
            target_value=18
        ))
)

# 3. Validate records (arrays)
records = [
    [1001, 'John Doe', 30, 'Engineering', 75000.00],
    [1002, 'J', 25, 'SALES', 65000.00],  # Will fail: name too short
    [1003, 'Bob Smith', 17, 'HR', 50000.00],  # Will fail: age < 18
]

results = validator.validate_batch(records)

# 4. Check results
for idx, result in enumerate(results):
    if result.is_valid:
        print(f"Record {idx}: ✓ PASS (Score: {result.score})")
    else:
        print(f"Record {idx}: ✗ FAIL (Score: {result.score})")
        for error in result.errors:
            print(f"  - {error.column_name}: {error.message}")
```

### Pandas DataFrame Validation

```python
import pandas as pd
from wxdi.dq_validator import AssetMetadata, ColumnMetadata, DataType, Validator, ValidationRule
from wxdi.dq_validator.checks import LengthCheck, ValidValuesCheck
from wxdi.dq_validator.integrations import PandasValidator

# Define metadata and validator (same as array-based validation)
metadata = AssetMetadata(
    table_name='employees',
    columns=[
        ColumnMetadata('emp_id', DataType.INTEGER),
        ColumnMetadata('name', DataType.STRING, length=100),
        ColumnMetadata('department', DataType.STRING, length=50),
    ]
)

validator = Validator(metadata)
validator.add_rule(ValidationRule('name').add_check(LengthCheck(min_length=2)))
validator.add_rule(ValidationRule('department').add_check(
    ValidValuesCheck(['Engineering', 'Sales', 'HR'], case_sensitive=False)
))

# Create DataFrame
df = pd.DataFrame({
    'emp_id': [1001, 1002, 1003],
    'name': ['John Doe', 'J', 'Alice'],
    'department': ['Engineering', 'SALES', 'Marketing']
})

# Create Pandas validator
pandas_validator = PandasValidator(validator, chunk_size=10000)

# Get summary statistics (memory efficient)
summary = pandas_validator.get_summary_statistics(df)
print(f"Pass Rate: {summary['pass_rate']:.2f}%")

# Add validation column (returns DataFrame with struct column)
df_validated = pandas_validator.add_validation_column(df)
print(df_validated['dq_validation_result'])

# Get invalid rows
invalid_df = pandas_validator.get_invalid_rows(df)
print(f"Found {len(invalid_df)} invalid rows")

# Expand validation column into separate columns
df_expanded = pandas_validator.expand_validation_column(df_validated)
print(df_expanded[['name', 'dq_is_valid', 'dq_score', 'dq_pass_rate']])
```

### PySpark DataFrame Validation

```python
from pyspark.sql import SparkSession
from wxdi.dq_validator import AssetMetadata, ColumnMetadata, DataType, Validator, ValidationRule
from wxdi.dq_validator.checks import LengthCheck, ValidValuesCheck
from wxdi.dq_validator.integrations import SparkValidator

# Initialize Spark
spark = SparkSession.builder.appName("DataQuality").getOrCreate()

# Define metadata and validator (same as above)
metadata = AssetMetadata(
    table_name='employees',
    columns=[
        ColumnMetadata('emp_id', DataType.INTEGER),
        ColumnMetadata('name', DataType.STRING, length=100),
        ColumnMetadata('department', DataType.STRING, length=50),
    ]
)

validator = Validator(metadata)
validator.add_rule(ValidationRule('name').add_check(LengthCheck(min_length=2)))
validator.add_rule(ValidationRule('department').add_check(
    ValidValuesCheck(['Engineering', 'Sales', 'HR'], case_sensitive=False)
))

# Create DataFrame
df = spark.createDataFrame([
    (1001, 'John Doe', 'Engineering'),
    (1002, 'J', 'SALES'),
    (1003, 'Alice', 'Marketing')
], ['emp_id', 'name', 'department'])

# Create Spark validator
spark_validator = SparkValidator(validator)

# Get summary statistics (distributed aggregation)
summary = spark_validator.get_summary_statistics(df)
print(f"Pass Rate: {summary['pass_rate']:.2f}%")

# Add validation column (returns DataFrame with struct column)
df_validated = spark_validator.add_validation_column(df)
df_validated.select('name', 'dq_validation_result').show()

# Get invalid rows (distributed filtering)
invalid_df = spark_validator.get_invalid_rows(df)
print(f"Found {invalid_df.count()} invalid rows")

# Expand validation column
df_expanded = spark_validator.expand_validation_column(df_validated)
df_expanded.select('name', 'dq_is_valid', 'dq_score', 'dq_pass_rate').show()

# Write validation report
spark_validator.write_validation_report(df, output_path='validation_report', format='parquet')
```

## Core Concepts

### AssetMetadata

Defines the structure of your data asset (table) with column information:

```python
metadata = AssetMetadata(
    table_name='my_table',
    columns=[
        ColumnMetadata('id', DataType.INTEGER),
        ColumnMetadata('name', DataType.STRING, length=100),
        ColumnMetadata('amount', DataType.DECIMAL, precision=10, scale=2),
    ]
)
```

### ValidationRule

Defines validation rules for a specific column:

```python
rule = ValidationRule('column_name')
rule.add_check(LengthCheck(min_length=5, max_length=50))
rule.add_check(ValidValuesCheck(['value1', 'value2']))
```

### Validator

Orchestrates validation across all rules:

```python
validator = Validator(metadata)
validator.add_rule(rule1)
validator.add_rule(rule2)

result = validator.validate(record)  # Single record
results = validator.validate_batch(records)  # Multiple records
```
### Data Quality Dimensions

Each validation check is associated with a **Data Quality Dimension** that categorizes the type of quality issue it addresses. The SDK supports 8 standard data quality dimensions:

```python
from wxdi.dq_validator.data_quality_dimension import DataQualityDimension

# Available dimensions:
DataQualityDimension.ACCURACY      # Data correctly represents real-world values
DataQualityDimension.COMPLETENESS  # All required data is present
DataQualityDimension.CONFORMITY    # Data conforms to specified formats
DataQualityDimension.CONSISTENCY   # Data is consistent across systems
DataQualityDimension.COVERAGE      # Data covers the required scope
DataQualityDimension.TIMELINESS    # Data is available when needed
DataQualityDimension.UNIQUENESS    # No duplicate records exist
DataQualityDimension.VALIDITY      # Data values are valid and reasonable
```

**Default Dimensions by Check:**
- `LengthCheck` → VALIDITY
- `ValidValuesCheck` → VALIDITY
- `ComparisonCheck` → VALIDITY
- `CaseCheck` → CONSISTENCY
- `CompletenessCheck` → COMPLETENESS
- `RangeCheck` → VALIDITY
- `RegexCheck` → VALIDITY
- `FormatCheck` → VALIDITY
- `DataTypeCheck` → VALIDITY

**Getting and Setting Dimensions:**

```python
from wxdi.dq_validator.checks import LengthCheck
from wxdi.dq_validator.data_quality_dimension import DataQualityDimension

# Create a check (uses default dimension)
check = LengthCheck(min_length=5, max_length=50)

# Get the current dimension
dimension = check.get_dimension()
print(dimension)  # DataQualityDimension.VALIDITY

# Change the dimension
check.set_dimension(DataQualityDimension.CONFORMITY)

# Verify the change
print(check.get_dimension())  # DataQualityDimension.CONFORMITY
```

**Use Cases:**
- **Categorize validation failures** by dimension for better reporting
- **Track dimension-specific metrics** (e.g., completeness rate, validity rate)
- **Prioritize remediation efforts** based on dimension criticality
- **Align with data governance frameworks** that use dimension-based quality metrics


## Validation Checks

### 1. LengthCheck

Validates the length of any value (converted to string).

```python
# String length
LengthCheck(min_length=3, max_length=20)

# Works with any type (converts to string)
LengthCheck(min_length=5)  # Integer 12345 → "12345" (length=5)
```

**Parameters:**
- `min_length` (int, optional): Minimum allowed length (inclusive)
- `max_length` (int, optional): Maximum allowed length (inclusive)

**Edge Cases:**
- None values: Returns error
- Any type: Converts to string using `str(value)`
- At least one of min_length or max_length must be specified

### 2. ValidValuesCheck

Validates that a value is in a predefined list of allowed values.

```python
# Case-insensitive (default)
ValidValuesCheck(['active', 'inactive', 'pending'], case_sensitive=False)

# Case-sensitive
ValidValuesCheck(['Active', 'Inactive'], case_sensitive=True)
```

**Parameters:**
- `valid_values` (list): List of allowed values
- `case_sensitive` (bool, default=False): If False, string comparisons are case-insensitive

**Edge Cases:**
- None values: Returns error
- Case-insensitive: 'ACTIVE' matches 'active' when case_sensitive=False
- Non-string types: Always exact match (case_sensitive ignored)

### 3. ComparisonCheck

Validates that a value satisfies a comparison operation.

```python
# Column vs constant
ComparisonCheck(
    operator=ComparisonOperator.GREATER_THAN,
    target_value=18
)

# Column vs column
ComparisonCheck(
    operator=ComparisonOperator.GREATER_THAN,
    target_column='min_salary'
)

# Using string operator
ComparisonCheck(operator='>=', target_value=0)
```

**Operators:**
- `ComparisonOperator.GREATER_THAN` or `'>'`
- `ComparisonOperator.LESS_THAN` or `'<'`
- `ComparisonOperator.GREATER_THAN_OR_EQUAL` or `'>='`
- `ComparisonOperator.LESS_THAN_OR_EQUAL` or `'<='`
- `ComparisonOperator.EQUAL` or `'=='`
- `ComparisonOperator.NOT_EQUAL` or `'!='`

**Parameters:**
- `operator` (ComparisonOperator or str): Comparison operator
- `target_column` (str, optional): Column name to compare against
- `target_value` (any, optional): Constant value to compare against

**Supported Types:**
- Numbers (int, float, Decimal)
- Strings (lexicographic comparison)
- Dates and datetimes
- Booleans
- Any comparable type

### 4. CaseCheck

Validates the character case of string values.

```python
from wxdi.dq_validator import CaseCheck, ColumnCaseEnum

# Upper case
CaseCheck(case_type=ColumnCaseEnum.UPPER_CASE)

# Lower case
CaseCheck(case_type=ColumnCaseEnum.LOWER_CASE)

# Name case (Title Case)
CaseCheck(case_type=ColumnCaseEnum.NAME_CASE)

# Sentence case
CaseCheck(case_type=ColumnCaseEnum.SENTENCE_CASE)
```

**Parameters:**
- `case_type` (ColumnCaseEnum): Type of case validation

**Case Types:**
- `ANY_CASE`: Any case is valid
- `UPPER_CASE`: All uppercase (ABC)
- `LOWER_CASE`: All lowercase (abc)
- `NAME_CASE`: Title case (John Doe)
- `SENTENCE_CASE`: First letter uppercase (Hello world)

### 5. CompletenessCheck

Validates presence (non-null) of values.

```python
# Require non-null values
CompletenessCheck(missing_values_allowed=False)

# Allow null values
CompletenessCheck(missing_values_allowed=True)
```

**Parameters:**
- `missing_values_allowed` (bool): Whether None/null values are allowed

### 6. RangeCheck

Validates values within min/max range.

```python
# Numeric range
RangeCheck(min_value=0, max_value=100)

# Date range
from datetime import date
RangeCheck(min_value=date(2020, 1, 1), max_value=date(2025, 12, 31))

# String range (lexicographic)
RangeCheck(min_value='A', max_value='Z')
```

**Parameters:**
- `min_value` (any, optional): Minimum allowed value (inclusive)
- `max_value` (any, optional): Maximum allowed value (inclusive)

**Supported Types:**
- Numeric types (int, float, Decimal)
- Date and datetime
- Strings (lexicographic comparison)

### 7. RegexCheck

Validates values match regular expression patterns.

```python
# Phone number pattern
RegexCheck(pattern=r'^\d{3}-\d{3}-\d{4}$')

# Email pattern (case-insensitive)
RegexCheck(pattern=r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$', case_sensitive=False)
```

**Parameters:**
- `pattern` (str): Regular expression pattern
- `case_sensitive` (bool, default=True): Whether pattern matching is case-sensitive

### 8. FormatCheck

Validates value formats using intelligent format detection.

```python
from wxdi.dq_validator import FormatCheck, FormatConstraintType

# Valid formats
FormatCheck(
    constraint_type=FormatConstraintType.ValidFormats,
    formats={'%Y-%m-%d', '%d/%m/%Y', '%m-%d-%Y'}
)

# Invalid formats
FormatCheck(
    constraint_type=FormatConstraintType.InvalidFormats,
    formats={'%Y%m%d'}  # Reject this format
)
```

**Parameters:**
- `constraint_type` (FormatConstraintType): ValidFormats or InvalidFormats
- `formats` (set): Set of format strings

**Features:**
- Intelligent format detection using InferredTypeEngine
- Supports date, time, and timestamp formats
- UTF-16 compatible format matching

### 9. DataTypeCheck

Validates data types with intelligent type inference.

```python
from wxdi.dq_validator import DataTypeCheck, DataType

# Integer type
DataTypeCheck(expected_type=DataType.INTEGER)

# Date type
DataTypeCheck(expected_type=DataType.DATE)

# Decimal type
DataTypeCheck(expected_type=DataType.DECIMAL)
```

**Parameters:**
- `expected_type` (DataType): Expected data type

**Supported Types:**
- INTEGER, FLOAT, DECIMAL
- STRING, BOOLEAN
- DATE, TIME, DATETIME, TIMESTAMP

**Features:**
- Intelligent type inference
- Handles numeric formats (US and DE)
- Date/time format detection

## DataFrame Integration

### Features

- **Pandas Support**: Memory-efficient chunked processing for large DataFrames
- **PySpark Support**: Distributed validation using Spark UDFs
- **Consistent API**: Same interface for both Pandas and PySpark
- **Struct Column Output**: Single validation result column containing all metrics
- **Column Prefix**: Configurable `dq_` prefix to prevent column name conflicts
- **Summary Statistics**: Aggregated validation metrics without collecting data
- **Invalid Row Filtering**: Extract rows that failed validation
- **Column Expansion**: Expand struct column into individual columns

### PandasValidator

```python
PandasValidator(validator: Validator, chunk_size: int = 10000, column_prefix: str = "dq_")
```

**Methods:**
- `get_summary_statistics(df: pd.DataFrame) -> Dict[str, Any]`: Get aggregated validation metrics
- `add_validation_column(df: pd.DataFrame) -> pd.DataFrame`: Add struct column with validation results
- `get_invalid_rows(df: pd.DataFrame) -> pd.DataFrame`: Filter rows that failed validation
- `get_valid_rows(df: pd.DataFrame) -> pd.DataFrame`: Filter rows that passed validation
- `expand_validation_column(df: pd.DataFrame) -> pd.DataFrame`: Expand struct into separate columns

**Memory Efficiency:**
- Processes data in chunks (default: 10,000 rows)
- O(chunk_size) memory complexity
- Suitable for DataFrames larger than available RAM

### SparkValidator

```python
SparkValidator(validator: Validator, column_prefix: str = "dq_")
```

**Methods:**
- `get_summary_statistics(df: DataFrame) -> Dict[str, Any]`: Distributed aggregation of validation metrics
- `add_validation_column(df: DataFrame) -> DataFrame`: Add struct column using UDF
- `get_invalid_rows(df: DataFrame) -> DataFrame`: Distributed filtering of invalid rows
- `get_valid_rows(df: DataFrame) -> DataFrame`: Distributed filtering of valid rows
- `expand_validation_column(df: DataFrame) -> DataFrame`: Expand struct into separate columns
- `write_validation_report(df: DataFrame, output_path: str, format: str = 'parquet', mode: str = 'overwrite')`: Write validation results
- `get_error_sample(df: DataFrame, limit: int = 100) -> List[Dict]`: Collect sample of errors

**Distributed Processing:**
- All operations use Spark's distributed computing
- O(1) driver memory for aggregations
- Scales to billions of rows

### Validation Result Structure

The `dq_validation_result` struct column contains:

```python
{
    'is_valid': bool,           # True if all checks passed
    'score': str,               # "5/5" format (passed/total)
    'pass_rate': float,         # Percentage (0-100)
    'total_checks': int,        # Total number of checks
    'passed_checks': int,       # Number of passed checks
    'failed_checks': int,       # Number of failed checks
    'error_count': int,         # Number of errors
    'errors': List[str]         # List of error messages
}
```

## REST API Integration

### Provider Configuration

ProviderConfig supports two authentication methods:

**Option 1: Static Auth Token**
```python
from wxdi.dq_validator.provider import ProviderConfig

config = ProviderConfig(
    url="https://your-instance.cloud.ibm.com",
    auth_token="Bearer your-token",
    project_id="your-project-id"  # or catalog_id
)
```

**Option 2: AuthConfig (Recommended for automatic token management)**
```python
from wxdi.dq_validator.provider import ProviderConfig
from wxdi.common.auth import AuthConfig, EnvironmentType

# Create AuthConfig for your environment
auth_config = AuthConfig(
    environment_type=EnvironmentType.IBM_CLOUD,
    api_key="your-api-key"
)

# Pass AuthConfig to ProviderConfig
config = ProviderConfig(
    url="https://your-instance.cloud.ibm.com",
    auth_config=auth_config,
    project_id="your-project-id"
)

# Token is automatically retrieved when needed
token = config.auth_token  # Calls AuthProvider.get_token() internally
```

The `auth_config` parameter enables automatic token management across all providers. When both `auth_token` and `auth_config` are provided, `auth_config` takes precedence for token retrieval.

### GlossaryProvider

Fetch glossary terms and data quality constraints from IBM Cloud Pak for Data.

```python
from wxdi.dq_validator.provider import GlossaryProvider

glossary = GlossaryProvider(config)

# Get published artifact by ID
term = glossary.get_published_artifact_by_id("term-id")

# Get term by version ID
term = glossary.get_term_by_version_id("version-id")
```

### CamsProvider

Fetch data assets from CAMS (Catalog Asset Management System).

```python
from wxdi.dq_validator.provider import CamsProvider

cams = CamsProvider(config)

# Get asset by ID
asset = cams.get_asset_by_id(
    asset_id="asset-id",
    options={"hide_deprecated_response_fields": "false"}
)

# Access column information
for column in asset.column_info:
    print(f"Column: {column.name}, Type: {column.data_type}")
```

### IssuesProvider

Manage data quality issues (occurrences, tested records, ignored status).

```python
from wxdi.dq_validator.provider import IssuesProvider

issues = IssuesProvider(config)

# Update issue occurrences
issues.update_issue_occurrences(issue_id="issue-123", occurrences=767)

# Update tested records
issues.update_tested_records(issue_id="issue-123", tested_records=1000)

# Set ignored status
issues.set_issue_ignored(issue_id="issue-123", ignored=True)

# Update multiple metrics at once
issues.update_issue_metrics(
    issue_id="issue-123",
    occurrences=767,
    tested_records=1000
)
```

### DQSearchProvider

Search for DQ checks and assets by native ID.

```python
from wxdi.dq_validator.provider import DQSearchProvider

dq_search = DQSearchProvider(config)

# Search DQ check
check = dq_search.search_dq_check(
    native_id="asset-id/check-id",
    check_type="format",
    project_id="project-id"
)

# Search DQ asset
asset = dq_search.search_dq_asset(
    native_id="asset-id/column-name",
    asset_type="column",
    project_id="project-id"
)
```

### DQAssetsProvider

Retrieve data assets from CAMS with filtering and pagination support.

```python
from wxdi.dq_validator.provider import DQAssetsProvider

assets = DQAssetsProvider(config)

# Get assets by project ID
assets_list = assets.get_assets(
    project_id="project-id",
    include_children=True,
    asset_type="table"
)

# Get assets by catalog ID
assets_list = assets.get_assets(
    catalog_id="catalog-id",
    limit=100,
    start_token="next-page-token"
)
```

### ChecksProvider

Create and manage data quality checks in CAMS.

```python
from wxdi.dq_validator.provider import ChecksProvider

checks = ChecksProvider(config)

# Create a new check
check_id = checks.create_check(
    native_id="asset-id/column-name",
    check_type="format",
    dimension_id="dimension-id",
    project_id="project-id"
)

# Get existing checks
checks_list = checks.get_checks(
    native_id="asset-id/column-name",
    project_id="project-id",
    include_children=True
)
```

### DimensionsProvider

Search for data quality dimensions by name.

```python
from wxdi.dq_validator.provider import DimensionsProvider

dimensions = DimensionsProvider(config)

# Search for a dimension by name (case-insensitive)
dimension_id = dimensions.search_dimension("Completeness")
```

## Authentication Module

The SDK includes a comprehensive authentication module for generating Bearer tokens across different IBM Cloud environments and on-premises installations.

### Supported Environments

| Environment | Enum Value | Auth Method | Required Credentials |
|-------------|------------|-------------|---------------------|
| **IBM Cloud Standard** | `EnvironmentType.IBM_CLOUD` | POST (form-encoded) | API Key |
| **AWS Cloud (MCSP)** | `EnvironmentType.AWS_CLOUD` | POST (header-based) | API Key |
| **IBM Government Cloud** | `EnvironmentType.GOV_CLOUD` | POST (JSON) | API Key |
| **On-Premises** | `EnvironmentType.ON_PREM` | GET (headers) | User ID + Password |

### Quick Start - Authentication

```python
from wxdi.dq_validator import EnvironmentType, AuthConfig, TokenGenerator

# IBM Cloud Standard (Production)
config = AuthConfig(
    url="https://iam.cloud.ibm.com/identity/token",
    environment=EnvironmentType.IBM_CLOUD,
    api_key="your-api-key-here"
)

generator = TokenGenerator(config)
token = generator.generate_token()
print(token)  # Bearer eyJhbGc...
```

### Authentication Examples

#### 1. IBM Cloud Standard

```python
config = AuthConfig(
    url="https://iam.cloud.ibm.com/identity/token",
    environment=EnvironmentType.IBM_CLOUD,
    api_key="your-api-key"
)

generator = TokenGenerator(config)
token = generator.generate_token()
# Returns: "Bearer {access_token}"
```

#### 2. AWS Cloud (MCSP)

```python
config = AuthConfig(
    url="https://account-iam.platform.test.saas.ibm.com/api/2.0/accounts/your-account-id/apikeys/token",
    environment=EnvironmentType.AWS_CLOUD,
    api_key="your-aws-cloud-api-key"
)

generator = TokenGenerator(config)
token = generator.generate_token()
```

#### 3. IBM Government Cloud

```python
config = AuthConfig(
    url="https://dai.ibmforusgov.com/api/rest/mcsp/apikeys/token",
    environment=EnvironmentType.GOV_CLOUD,
    api_key="your-gov-api-key"
)

generator = TokenGenerator(config)
token = generator.generate_token()
```

#### 4. On-Premises Installation

```python
config = AuthConfig(
    url="https://localhost:8443/v1/preauth/validateAuth",
    environment=EnvironmentType.ON_PREM,
    user_id="admin",
    password="your-password"
)

generator = TokenGenerator(config)
token = generator.generate_token()
```

### Using Generated Tokens

```python
import requests

# Generate token
config = AuthConfig(
    url="https://iam.cloud.ibm.com/identity/token",
    environment=EnvironmentType.IBM_CLOUD,
    api_key="your-api-key"
)
generator = TokenGenerator(config)
token = generator.generate_token()

# Use token in API requests
headers = {
    'Authorization': token,  # Already in "Bearer {token}" format
    'Content-Type': 'application/json'
}

response = requests.get('https://api.example.com/endpoint', headers=headers)
```

## ValidationResult

Each validation returns a `ValidationResult` object:

```python
result = validator.validate(record)

# Properties
result.is_valid          # bool: True if no errors
result.score             # str: "5/5" (passed/total)
result.pass_rate         # float: 100.0 (percentage)
result.total_checks      # int: Total number of checks
result.passed_checks     # int: Number of passed checks
result.failed_checks     # int: Number of failed checks
result.errors            # List[ValidationError]: List of errors

# Convert to dictionary
result_dict = result.to_dict()
```

## ValidationError

Each error contains detailed information:

```python
error = result.errors[0]

error.column_name   # str: Name of the column
error.check_name    # str: Type of check that failed
error.message       # str: Human-readable error message
error.value         # any: The value that failed
error.expected      # any: Expected value/constraint

# Convert to dictionary
error_dict = error.to_dict()
```

## Examples

See complete working examples in the `examples/` directory:
- `basic_usage.py` - Array-based validation example
- `pandas_dataframe_usage.py` - Pandas DataFrame validation example
- `spark_dataframe_usage.py` - PySpark DataFrame validation example
- `consolidation_usage.py` - Consolidated statistics and dimension-based reporting
- `auth_usage.py` - Authentication examples (296 lines)
- `assets_usage.py` - DQAssetsProvider usage examples (210 lines)
- `glossary_usage.py` - GlossaryProvider usage examples (250 lines)
- `checks_usage.py` - ChecksProvider usage examples (272 lines)
- `dimensions_usage.py` - DimensionsProvider usage examples (146 lines)
- `issues_usage.py` - IssuesProvider usage examples (124 lines)
- `dq_workflow_usage.py` - Complete DQ workflow (317 lines)

## Project Structure

```
data-intelligence-sdk/
├── src/
│   └── wxdi/
│       ├── __init__.py
│       ├── common/
│       │   ├── __init__.py
│       │   └── auth/
│       │       ├── __init__.py
│       │       ├── auth_config.py
│       │       ├── auth_provider.py
│       │       ├── gov_cloud_authenticator.py
│       │       └── gov_cloud_token_manager.py
│       └── dq_validator/
│           ├── __init__.py
│           ├── metadata.py               # DataType, ColumnMetadata, AssetMetadata
│           ├── datatypes.py              # DataType enum
│           ├── data_quality_dimension.py # DataQualityDimension enum
│           ├── base.py                   # BaseCheck, ValidationError
│           ├── result.py                 # ValidationResult
│           ├── rule.py                   # ValidationRule
│           ├── validator.py              # Validator
│           ├── rule_loader.py            # RuleLoader for external providers
│           ├── inferred_engine.py        # InferredTypeEngine
│           ├── format_engine.py          # FormatEngine
│           ├── issue_reporting.py        # Issue reporter utility
│           ├── datetime_formats.py       # Date/time format definitions
│           ├── utils.py                  # Utility functions
│           ├── version.py                # Version information
│           ├── result_consolidator.py    # Result consolidation
│           ├── checks/
│           │   ├── __init__.py
│           │   ├── length_check.py
│           │   ├── valid_values_check.py
│           │   ├── comparison_check.py
│           │   ├── case_check.py
│           │   ├── completeness_check.py
│           │   ├── range_check.py
│           │   ├── regex_check.py
│           │   ├── format_check.py
│           │   └── datatype_check.py
│           ├── integrations/
│           │   ├── __init__.py
│           │   ├── base.py
│           │   ├── pandas_validator.py
│           │   └── spark_validator.py
│           └── provider/
│               ├── __init__.py
│               ├── base_provider.py
│               ├── config.py
│               ├── glossary.py
│               ├── cams.py
│               ├── assets.py
│               ├── checks.py
│               ├── dimensions.py
│               ├── issues.py
│               ├── dq_search.py
│               ├── constraint_model.py
│               ├── data_asset_model.py
│               └── response_model.py
├── examples/
│   ├── basic_usage.py
│   ├── pandas_dataframe_usage.py
│   ├── spark_dataframe_usage.py
│   ├── auth_usage.py
│   ├── assets_usage.py
│   ├── checks_usage.py
│   ├── dimensions_usage.py
│   ├── issues_usage.py
│   └── dq_workflow_usage.py
├── setup.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

Apache License 2.0 - see LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Documentation

- **README.md**: This file - comprehensive user guide

## Key Features Summary

✅ **9 Validation Checks** - Comprehensive validation coverage  
✅ **DataFrame Support** - Pandas and PySpark integration  
✅ **REST API Integration** - Complete provider module  
✅ **Multi-Environment Auth** - 4 cloud environments supported  
✅ **Memory Efficient** - Chunked processing for Pandas  
✅ **Distributed Processing** - Spark UDF-based validation  
✅ **Thread-Safe** - Concurrent access support  
✅ **Type-Safe** - Full type hints throughout  
✅ **Extensible** - Easy to add new checks  
✅ **Production Ready** - 400+ tests, fully documented

## Python Support

- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

## Dependencies

**Core:**
- pydantic >= 2.12.0
- requests >= 2.28.0
- regex >= 2023.0.0

**Optional:**
- pandas >= 1.3.0 (for Pandas support)
- pyspark >= 3.0.0 (for PySpark support)

**Development:**
- pytest >= 7.0.0
- pytest-cov >= 4.0.0
- pytest-mock >= 3.7.0
- black >= 23.0.0
- mypy >= 1.0.0
- flake8 >= 6.0.0
