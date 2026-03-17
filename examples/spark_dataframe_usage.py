"""
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
"""
"""
PySpark DataFrame Validation Example

This example demonstrates how to use the Data Quality feature of the
IBM watsonx.data intelligence SDK with PySpark DataFrames for distributed data validation.
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DecimalType

from wxdi.dq_validator import (
    AssetMetadata, ColumnMetadata, DataType,
    Validator, ValidationRule,
    LengthCheck, ValidValuesCheck, ComparisonCheck, ComparisonOperator
)
from wxdi.dq_validator.integrations import SparkValidator


def main():
    print("=" * 70)
    print("PySpark DataFrame Validation Example")
    print("=" * 70)
    
    # Step 1: Initialize Spark Session
    spark = SparkSession.builder \
        .appName("DataQualityValidation") \
        .master("local[*]") \
        .getOrCreate()
    
    print(f"\nSpark Version: {spark.version}")
    print(f"Spark Master: {spark.sparkContext.master}")
    
    # Step 2: Define metadata
    metadata = AssetMetadata(
        table_name='employees',
        columns=[
            ColumnMetadata('emp_id', DataType.INTEGER),
            ColumnMetadata('name', DataType.STRING, length=100),
            ColumnMetadata('age', DataType.INTEGER),
            ColumnMetadata('department', DataType.STRING, length=50),
            ColumnMetadata('salary', DataType.DECIMAL, precision=10, scale=2),
            ColumnMetadata('min_salary', DataType.DECIMAL, precision=10, scale=2),
        ]
    )
    
    print(f"\nAsset: {metadata.table_name}")
    print(f"Columns: {len(metadata.columns)}")
    
    # Step 3: Create validator with rules
    validator = Validator(metadata)
    
    # Add validation rules
    validator.add_rule(
        ValidationRule('emp_id')
            .add_check(LengthCheck(min_length=4, max_length=6))
    )
    
    validator.add_rule(
        ValidationRule('name')
            .add_check(LengthCheck(min_length=2, max_length=100))
    )
    
    validator.add_rule(
        ValidationRule('age')
            .add_check(ComparisonCheck(
                operator=ComparisonOperator.GREATER_THAN_OR_EQUAL,
                target_value=18
            ))
            .add_check(ComparisonCheck(
                operator=ComparisonOperator.LESS_THAN_OR_EQUAL,
                target_value=65
            ))
    )
    
    validator.add_rule(
        ValidationRule('department')
            .add_check(ValidValuesCheck(
                ['Engineering', 'Sales', 'HR', 'Finance'],
                case_sensitive=False
            ))
    )
    
    validator.add_rule(
        ValidationRule('salary')
            .add_check(ComparisonCheck(
                operator=ComparisonOperator.GREATER_THAN,
                target_column='min_salary'
            ))
    )
    
    print(f"\nValidator configured with {len(validator.rules)} rules")
    
    # Step 4: Create sample DataFrame
    schema = StructType([
        StructField('emp_id', IntegerType(), True),
        StructField('name', StringType(), True),
        StructField('age', IntegerType(), True),
        StructField('department', StringType(), True),
        StructField('salary', DecimalType(10, 2), True),
        StructField('min_salary', DecimalType(10, 2), True),
    ])
    
    data = [
        (1001, 'John Doe', 30, 'Engineering', 75000.00, 60000.00),
        (12, 'Jane Smith', 25, 'SALES', 65000.00, 55000.00),
        (1003, 'Bob Smith', 17, 'HR', 50000.00, 45000.00),
        (1004, 'Alice Johnson', 35, 'Marketing', 80000.00, 70000.00),
        (1005, 'Charlie Brown', 40, 'Finance', 55000.00, 60000.00),
    ]
    
    df = spark.createDataFrame(data, schema)
    
    print(f"\nOriginal DataFrame ({df.count()} rows):")
    df.show(truncate=False)
    
    # Step 5: Create Spark validator
    spark_validator = SparkValidator(validator)
    
    print(f"\nSpark Validator: {spark_validator}")
    
    # Step 6: Get summary statistics (distributed aggregation)
    print("\n" + "=" * 70)
    print("Validation Summary Statistics")
    print("=" * 70)
    
    summary = spark_validator.get_summary_statistics(df)
    print(f"Total Rows: {summary['total_rows']}")
    print(f"Valid Rows: {summary['valid_rows']}")
    print(f"Invalid Rows: {summary['invalid_rows']}")
    print(f"Pass Rate: {summary['pass_rate']:.2f}%")
    print(f"Total Checks: {summary['total_checks']}")
    print(f"Passed Checks: {summary['passed_checks']}")
    print(f"Failed Checks: {summary['failed_checks']}")
    
    # Step 7: Add validation column
    print("\n" + "=" * 70)
    print("DataFrame with Validation Column")
    print("=" * 70)
    
    df_validated = spark_validator.add_validation_column(df)
    
    print(f"\nColumns: {df_validated.columns}")
    print(f"\nSchema of validation column:")
    df_validated.select('dq_validation_result').printSchema()
    
    print(f"\nValidation results (struct column):")
    df_validated.select('name', 'dq_validation_result').show(truncate=False)
    
    # Step 8: Get invalid rows
    print("\n" + "=" * 70)
    print("Invalid Rows")
    print("=" * 70)
    
    invalid_df = spark_validator.get_invalid_rows(df)
    print(f"\nFound {invalid_df.count()} invalid rows:")
    invalid_df.show(truncate=False)
    
    # Step 9: Expand validation column
    print("\n" + "=" * 70)
    print("Expanded Validation Columns")
    print("=" * 70)
    
    df_expanded = spark_validator.expand_validation_column(df_validated)
    
    expanded_cols = [c for c in df_expanded.columns if c.startswith('dq_')]
    print(f"\nExpanded columns: {expanded_cols}")
    print(f"\nSample of expanded data:")
    df_expanded.select('name', 'dq_is_valid', 'dq_score', 'dq_pass_rate', 'dq_error_count').show(truncate=False)
    
    # Step 10: Get error samples
    print("\n" + "=" * 70)
    print("Error Samples")
    print("=" * 70)
    
    error_samples = spark_validator.get_error_sample(df, limit=10)
    print(f"\nFound {len(error_samples)} error samples:")
    for i, errors in enumerate(error_samples, 1):
        print(f"\n{i}. Error count: {len(errors)}")
        print(f"   Errors:")
        for error in errors:
            print(f"     - {error}")
    
    # Step 11: Write validation report
    print("\n" + "=" * 70)
    print("Writing Validation Report")
    print("=" * 70)
    
    output_path = "validation_report"
    spark_validator.write_validation_report(
        df,
        output_path=output_path,
        format='parquet'
    )
    print(f"✓ Validation report written to: {output_path}")
    
    # Step 12: Save results
    print("\n" + "=" * 70)
    print("Saving Results")
    print("=" * 70)
    
    # Save invalid rows
    invalid_df.write.mode('overwrite').parquet('invalid_employees_spark')
    print("✓ Saved invalid rows to: invalid_employees_spark/")
    
    # Save expanded results
    df_expanded.write.mode('overwrite').parquet('validation_results_spark')
    print("✓ Saved validation results to: validation_results_spark/")
    
    # Step 13: Performance demonstration with larger dataset
    print("\n" + "=" * 70)
    print("Performance Test with Larger Dataset")
    print("=" * 70)
    
    # Create a larger dataset by repeating the data
    large_df = df
    for _ in range(10):  # 5 * 2^10 = 5,120 rows
        large_df = large_df.union(df)
    
    print(f"\nLarge DataFrame: {large_df.count()} rows")
    
    # Validate large dataset (distributed processing)
    import time
    start_time = time.time()
    
    large_summary = spark_validator.get_summary_statistics(large_df)
    
    elapsed_time = time.time() - start_time
    
    print(f"\nValidation completed in {elapsed_time:.2f} seconds")
    print(f"Total Rows: {large_summary['total_rows']}")
    print(f"Valid Rows: {large_summary['valid_rows']}")
    print(f"Invalid Rows: {large_summary['invalid_rows']}")
    print(f"Pass Rate: {large_summary['pass_rate']:.2f}%")
    print(f"Throughput: {large_summary['total_rows'] / elapsed_time:.0f} rows/second")
    
    print("\n" + "=" * 70)
    print("Example Complete!")
    print("=" * 70)
    
    # Stop Spark session
    spark.stop()


if __name__ == '__main__':
    try:
        main()
    except ImportError as e:
        print(f"Error: {e}")
        print("\nTo run this example, install PySpark:")
        print("  pip install pyspark")
        print("Or install with DataFrame support:")
        print("  pip install dq-validator[spark]")