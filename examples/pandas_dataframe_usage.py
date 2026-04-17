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
Pandas DataFrame Validation Example

This example demonstrates how to use the Data Quality feature of the
Data Intelliegence SDK with Pandas DataFrames for in-memory data validation.
"""

import pandas as pd
from wxdi.dq_validator import (
    AssetMetadata, ColumnMetadata, DataType,
    Validator, ValidationRule,
    LengthCheck, ValidValuesCheck, ComparisonCheck, ComparisonOperator
)
from wxdi.dq_validator.integrations import PandasValidator


def main():
    print("=" * 70)
    print("Pandas DataFrame Validation Example")
    print("=" * 70)

    # Step 1: Define metadata
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

    # Step 2: Create validator with rules
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

    # Step 3: Create sample DataFrame
    df = pd.DataFrame({
        'emp_id': [1001, 12, 1003, 1004, 1005],
        'name': ['John Doe', 'Jane Smith', 'Bob Smith', 'Alice Johnson', 'Charlie Brown'],
        'age': [30, 25, 17, 35, 40],
        'department': ['Engineering', 'SALES', 'HR', 'Marketing', 'Finance'],
        'salary': [75000.00, 65000.00, 50000.00, 80000.00, 55000.00],
        'min_salary': [60000.00, 55000.00, 45000.00, 70000.00, 60000.00]
    })

    print(f"\nOriginal DataFrame ({len(df)} rows):")
    print(df.to_string(index=False))

    # Step 4: Create Pandas validator
    pandas_validator = PandasValidator(validator, chunk_size=1000)

    print(f"\nPandas Validator: {pandas_validator}")

    # Step 5: Get summary statistics (memory efficient)
    print("\n" + "=" * 70)
    print("Validation Summary Statistics")
    print("=" * 70)

    summary = pandas_validator.get_summary_statistics(df)
    print(f"Total Rows: {summary['total_rows']}")
    print(f"Valid Rows: {summary['valid_rows']}")
    print(f"Invalid Rows: {summary['invalid_rows']}")
    print(f"Pass Rate: {summary['pass_rate']:.2f}%")
    print(f"Total Checks: {summary['total_checks']}")
    print(f"Passed Checks: {summary['passed_checks']}")
    print(f"Failed Checks: {summary['failed_checks']}")

    # Step 6: Add validation column
    print("\n" + "=" * 70)
    print("DataFrame with Validation Column")
    print("=" * 70)

    df_validated = pandas_validator.add_validation_column(df)

    print(f"\nColumns: {list(df_validated.columns)}")
    print(f"\nValidation results (struct column):")
    for idx, result in enumerate(df_validated['dq_validation_result']):
        status = "✓ PASS" if result['is_valid'] else "✗ FAIL"
        print(f"Row {idx}: {status} - Score: {result['score']}, Pass Rate: {result['pass_rate']:.1f}%")
        if not result['is_valid']:
            print(f"  Errors: {result['error_count']}")

    # Step 7: Get invalid rows
    print("\n" + "=" * 70)
    print("Invalid Rows")
    print("=" * 70)

    invalid_df = pandas_validator.get_invalid_rows(df)
    print(f"\nFound {len(invalid_df)} invalid rows:")

    for idx, row in invalid_df.iterrows():
        print(f"\nRow {idx}:")
        print(f"  emp_id: {row['emp_id']}")
        print(f"  name: {row['name']}")
        print(f"  age: {row['age']}")
        print(f"  department: {row['department']}")
        validation = row['dq_validation_result']
        print(f"  Validation: {validation['score']} ({validation['pass_rate']:.1f}%)")
        print(f"  Errors: {validation['error_count']}")

    # Step 8: Expand validation column
    print("\n" + "=" * 70)
    print("Expanded Validation Columns")
    print("=" * 70)

    df_expanded = pandas_validator.expand_validation_column(df_validated)

    print(f"\nExpanded columns: {[c for c in df_expanded.columns if c.startswith('dq_')]}")
    print(f"\nSample of expanded data:")
    print(df_expanded[['name', 'dq_is_valid', 'dq_score', 'dq_pass_rate', 'dq_error_count']].to_string(index=False))

    # Step 9: Save results
    print("\n" + "=" * 70)
    print("Saving Results")
    print("=" * 70)

    # Save invalid rows
    invalid_df.to_csv('invalid_employees.csv', index=False)
    print("✓ Saved invalid rows to: invalid_employees.csv")

    # Save expanded results
    df_expanded.to_csv('validation_results.csv', index=False)
    print("✓ Saved validation results to: validation_results.csv")

    print("\n" + "=" * 70)
    print("Example Complete!")
    print("=" * 70)


if __name__ == '__main__':
    try:
        main()
    except ImportError as e:
        print(f"Error: {e}")
        print("\nTo run this example, install pandas:")
        print("  pip install pandas")
        print("Or install with DataFrame support:")
        print("  pip install dq-validator[pandas]")