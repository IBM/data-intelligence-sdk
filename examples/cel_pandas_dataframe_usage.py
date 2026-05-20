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
CEL Validation with Pandas DataFrames Example

This example demonstrates how to use CEL (Common Expression Language) 
expressions for custom validation logic with Pandas DataFrames.

CEL provides flexible, safe expression evaluation for complex business rules
that go beyond the capabilities of predefined validation checks.

Key Features Demonstrated:
- CEL expressions with pandas DataFrames
- Simple syntax for column references (e.g., 'salary > min_salary')
- Complex multi-column business rules
- Memory-efficient chunked processing
- Validation result analysis and filtering
"""

import pandas as pd
from wxdi.dq_validator import (
    AssetMetadata, ColumnMetadata, DataType,
    Validator, ValidationRule,
    CELCheck, CompletenessCheck
)
from wxdi.dq_validator.integrations import PandasValidator


def main():
    print("=" * 80)
    print("CEL Validation with Pandas DataFrames Example")
    print("=" * 80)
    
    # Step 1: Define asset metadata
    print("\n[Step 1] Defining Asset Metadata")
    print("-" * 80)
    
    metadata = AssetMetadata(
        table_name='employees',
        columns=[
            ColumnMetadata('emp_id', DataType.INTEGER),
            ColumnMetadata('name', DataType.STRING, length=100),
            ColumnMetadata('email', DataType.STRING, length=255),
            ColumnMetadata('age', DataType.INTEGER),
            ColumnMetadata('department', DataType.STRING, length=50),
            ColumnMetadata('salary', DataType.DECIMAL, precision=10, scale=2),
            ColumnMetadata('min_salary', DataType.DECIMAL, precision=10, scale=2),
            ColumnMetadata('bonus', DataType.DECIMAL, precision=10, scale=2),
            ColumnMetadata('status', DataType.STRING, length=20),
            ColumnMetadata('years_experience', DataType.INTEGER),
        ]
    )
    
    print(f"Asset: {metadata.table_name}")
    print(f"Columns: {len(metadata.columns)}")
    
    # Step 2: Create validator with CEL-based business rules
    print("\n[Step 2] Configuring CEL Validation Rules")
    print("-" * 80)
    
    validator = Validator(metadata)
    
    # Rule 1: Salary must be positive
    print("\n[OK] Rule 1: Salary must be positive")
    print("  CEL: 'value > 0'")
    validator.add_rule(
        ValidationRule('salary')
            .add_check(CELCheck(
                expression='value > 0',
                error_message='Salary must be positive'
            ))
    )
    
    # Rule 2: Salary must exceed minimum salary
    print("\n[OK] Rule 2: Salary must exceed minimum salary")
    print("  CEL: 'value > min_salary'")
    validator.add_rule(
        ValidationRule('salary')
            .add_check(CELCheck(
                expression='value > min_salary',
                error_message='Salary must exceed minimum salary'
            ))
    )
    
    # Rule 3: Age-based salary requirements
    print("\n[OK] Rule 3: Age-based salary requirements")
    print("  CEL: 'age > 40 ? value >= 80000 : value >= 50000'")
    print("  (Senior employees must earn >=$80K, junior >=$50K)")
    validator.add_rule(
        ValidationRule('salary')
            .add_check(CELCheck(
                expression='age > 40 ? value >= 80000 : value >= 50000',
                error_message='Salary does not meet age-based requirements'
            ))
    )
    
    # Rule 4: Email domain validation
    print("\n[OK] Rule 4: Email must be from company domain")
    print("  CEL: 'value.endsWith(\"@company.com\")'")
    validator.add_rule(
        ValidationRule('email')
            .add_check(CompletenessCheck(missing_values_allowed=False))
            .add_check(CELCheck(
                expression='value.endsWith("@company.com")',
                error_message='Email must be from company domain (@company.com)'
            ))
    )
    
    # Rule 5: Status validation
    print("\n[OK] Rule 5: Status must be Active, Pending, or Approved")
    print("  CEL: 'value in [\"Active\", \"Pending\", \"Approved\"]'")
    validator.add_rule(
        ValidationRule('status')
            .add_check(CELCheck(
                expression='value in ["Active", "Pending", "Approved"]',
                error_message='Invalid status value'
            ))
    )
    
    # Rule 6: Department-based bonus limits
    print("\n[OK] Rule 6: Department-based bonus limits")
    print("  CEL: 'department == \"Sales\" ? value <= 20000 : value <= 10000'")
    print("  (Sales: <=$20K, Others: <=$10K)")
    validator.add_rule(
        ValidationRule('bonus')
            .add_check(CELCheck(
                expression='department == "Sales" ? value <= 20000 : value <= 10000',
                error_message='Bonus exceeds department limit'
            ))
    )
    
    # Rule 7: Experience-based salary validation
    print("\n[OK] Rule 7: Salary must match experience level")
    print("  CEL: 'value >= 40000 + (years_experience * 5000)'")
    print("  (Base $40K + $5K per year of experience)")
    validator.add_rule(
        ValidationRule('salary')
            .add_check(CELCheck(
                expression='value >= 40000 + (years_experience * 5000)',
                error_message='Salary too low for experience level'
            ))
    )
    
    # Rule 8: Sales age requirement
    print("\n[OK] Rule 8: Sales employees must be at least 21")
    print("  CEL: 'value >= 21 || department != \"Sales\"'")
    validator.add_rule(
        ValidationRule('age')
            .add_check(CELCheck(
                expression='value >= 21 || department != "Sales"',
                error_message='Sales employees must be at least 21 years old'
            ))
    )
    
    print(f"\n[OK] Validator configured with {len(validator.rules)} rules")
    
    # Step 3: Create sample DataFrame
    print("\n[Step 3] Creating Sample DataFrame")
    print("-" * 80)
    
    df = pd.DataFrame({
        'emp_id': [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008],
        'name': [
            'John Doe', 'Jane Smith', 'Bob Wilson', 'Alice Brown',
            'Charlie Davis', 'Eve Martinez', 'Frank Lee', 'Grace Kim'
        ],
        'email': [
            'john@company.com', 'jane@other.com', 'bob@company.com', 'alice@company.com',
            'charlie@company.com', 'eve@company.com', 'frank@company.com', 'grace@company.com'
        ],
        'age': [30, 45, 20, 50, 35, 28, 42, 38],
        'department': [
            'Engineering', 'Sales', 'Sales', 'Engineering',
            'Sales', 'HR', 'Engineering', 'Finance'
        ],
        'salary': [75000.00, 85000.00, 55000.00, 70000.00, 90000.00, 62000.00, 95000.00, 78000.00],
        'min_salary': [60000.00, 70000.00, 50000.00, 60000.00, 70000.00, 55000.00, 75000.00, 65000.00],
        'bonus': [5000.00, 18000.00, 8000.00, 12000.00, 25000.00, 7000.00, 9000.00, 8500.00],
        'status': ['Active', 'Active', 'Pending', 'Inactive', 'Active', 'Approved', 'Active', 'Pending'],
        'years_experience': [5, 15, 2, 20, 10, 4, 12, 8]
    })
    
    print(f"\nDataFrame created with {len(df)} rows and {len(df.columns)} columns")
    print("\nSample data (first 3 rows):")
    print(df.head(3).to_string(index=False))
    
    # Step 4: Create Pandas validator
    print("\n[Step 4] Creating Pandas Validator")
    print("-" * 80)
    
    pandas_validator = PandasValidator(validator, chunk_size=1000)
    print(f"[OK] {pandas_validator}")
    
    # Step 5: Get summary statistics
    print("\n[Step 5] Validation Summary Statistics")
    print("-" * 80)
    
    summary = pandas_validator.get_summary_statistics(df)
    print(f"\nTotal Rows:      {summary['total_rows']}")
    print(f"Valid Rows:      {summary['valid_rows']} ({summary['pass_rate']:.1f}%)")
    print(f"Invalid Rows:    {summary['invalid_rows']}")
    print(f"Total Checks:    {summary['total_checks']}")
    print(f"Passed Checks:   {summary['passed_checks']}")
    print(f"Failed Checks:   {summary['failed_checks']}")
    
    # Step 6: Add validation column
    print("\n[Step 6] Adding Validation Results to DataFrame")
    print("-" * 80)
    
    df_validated = pandas_validator.add_validation_column(df)
    
    print(f"\n[OK] Validation column added: '{pandas_validator.result_column_name}'")
    print(f"[OK] Total columns: {len(df_validated.columns)}")
    
    # Display validation results
    print("\nValidation Results by Row:")
    print("-" * 80)
    for idx, row in df_validated.iterrows():
        result = row['dq_validation_result']
        is_valid = bool(result['is_valid'])
        status = "[PASS]" if is_valid else "[FAIL]"
        print(f"Row {idx}: {status} | {row['name']:20s} | Score: {str(result['score']):>6s} | "
              f"Pass Rate: {result['pass_rate']:6.1f}% | Errors: {result['error_count']}")
    
    # Step 7: Analyze invalid rows
    print("\n[Step 7] Analyzing Invalid Rows")
    print("-" * 80)
    
    invalid_df = pandas_validator.get_invalid_rows(df)
    
    if len(invalid_df) > 0:
        print(f"\nFound {len(invalid_df)} invalid row(s):\n")
        
        for idx, row in invalid_df.iterrows():
            validation = row['dq_validation_result']
            print(f"Row {idx}: {row['name']} ({row['department']})")
            print(f"  Age: {row['age']}, Salary: ${row['salary']:,.2f}, Bonus: ${row['bonus']:,.2f}")
            print(f"  Email: {row['email']}, Status: {row['status']}")
            print(f"  Validation Score: {validation['score']} ({validation['pass_rate']:.1f}%)")
            print(f"  Failed Checks: {validation['failed_checks']}/{validation['total_checks']}")
            
            # Parse and display errors
            import json
            errors = validation['errors']
            error_count = len(errors) if isinstance(errors, list) else 0
            if error_count > 0:
                print(f"  Errors:")
                for error_json in errors:
                    error = json.loads(error_json)
                    print(f"    - {error['column']}: {error['message']}")
            print()
    else:
        print("\n[OK] All rows passed validation!")
    
    # Step 8: Expand validation columns for analysis
    print("\n[Step 8] Expanding Validation Columns")
    print("-" * 80)
    
    df_expanded = pandas_validator.expand_validation_column(df_validated)
    
    print(f"\n[OK] Validation struct expanded into separate columns")
    print(f"[OK] New columns: {[c for c in df_expanded.columns if c.startswith('dq_')]}")
    
    # Show expanded validation data
    print("\nExpanded Validation Data:")
    validation_cols = ['name', 'department', 'dq_is_valid', 'dq_score', 
                       'dq_pass_rate', 'dq_error_count']
    print(df_expanded[validation_cols].to_string(index=False))
    
    # Step 9: Filter and analyze by department
    print("\n[Step 9] Department-Level Analysis")
    print("-" * 80)
    
    dept_analysis = df_expanded.groupby('department').agg({
        'dq_is_valid': ['sum', 'count'],
        'dq_pass_rate': 'mean',
        'dq_error_count': 'sum'
    }).round(2)
    
    dept_analysis.columns = ['Valid_Rows', 'Total_Rows', 'Avg_Pass_Rate', 'Total_Errors']
    dept_analysis['Pass_Rate_%'] = (dept_analysis['Valid_Rows'] / dept_analysis['Total_Rows'] * 100).round(1)
    
    print("\nValidation Statistics by Department:")
    print(dept_analysis.to_string())
    
    # Step 10: Get detailed statistics
    print("\n[Step 10] Detailed Validation Statistics")
    print("-" * 80)
    
    consolidator = pandas_validator.get_detailed_statistics(df)
    
    print("\nOverall Statistics:")
    overall = consolidator.get_overall_statistics()
    print(f"  Total Records: {overall['total_records']}")
    print(f"  Valid Records: {overall['valid_records']} ({overall['pass_rate']:.1f}%)")
    print(f"  Invalid Records: {overall['invalid_records']}")
    print(f"  Total Errors: {overall['total_errors']}")
    
    print("\nStatistics by Column:")
    for column in consolidator.get_columns():
        stats = consolidator.get_column_statistics(column)
        if stats['total'] > 0:
            pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0.0
            print(f"  {column:20s}: {stats['passed']:2d}/{stats['total']:2d} passed "
                  f"({pass_rate:5.1f}%) - {stats['failed']} failed")
    
    print("\nStatistics by Check Type:")
    for check in consolidator.get_checks():
        stats = consolidator.get_check_statistics(check)
        if stats['total'] > 0:
            pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0.0
            print(f"  {check:30s}: {stats['passed']:2d}/{stats['total']:2d} passed "
                  f"({pass_rate:5.1f}%)")
    
    # Step 11: Save results
    print("\n[Step 11] Saving Results")
    print("-" * 80)
    
    # Save invalid rows
    if len(invalid_df) > 0:
        invalid_df.to_csv('cel_invalid_employees.csv', index=False)
        print("[OK] Saved invalid rows to: cel_invalid_employees.csv")
    
    # Save expanded results
    df_expanded.to_csv('cel_validation_results.csv', index=False)
    print("[OK] Saved validation results to: cel_validation_results.csv")
    
    # Save department analysis
    dept_analysis.to_csv('cel_department_analysis.csv')
    print("[OK] Saved department analysis to: cel_department_analysis.csv")
    
    # Step 12: CEL Expression Tips
    print("\n" + "=" * 80)
    print("CEL Expression Tips for Pandas DataFrames")
    print("=" * 80)
    print("""
1. Simple Syntax (Recommended):
   - Direct column access: 'salary > min_salary'
   - No 'record.' prefix needed: 'age > 40'
   - Cleaner and more readable

2. Available Variables:
   - value: Current column value being validated
   - Column names: Direct access to any column (e.g., age, salary, department)
   - column_name: Name of the column being validated
   - record_index: Position of the record in the batch

3. Supported Operations:
   - Comparisons: ==, !=, <, <=, >, >=
   - Logical: &&, ||, !
   - Arithmetic: +, -, *, /, %
   - Ternary: condition ? true_value : false_value
   - String: .startsWith(), .endsWith(), .contains()
   - List: in, not in

4. Complex Business Rules:
   - Multi-column: 'salary > min_salary && bonus < salary * 0.3'
   - Conditional: 'age > 40 ? salary >= 80000 : salary >= 50000'
   - Department-based: 'department == "Sales" ? value <= 20000 : value <= 10000'

5. Performance Optimization:
   - CEL automatically extracts only required columns from wide tables
   - Chunked processing handles large DataFrames efficiently
   - Memory usage: O(chunk_size) instead of O(n)

6. Case Sensitivity:
   WARNING: Column names are CASE-SENSITIVE
   - 'salary' != 'Salary' != 'SALARY'
   - Use exact column names from metadata
""")
    
    print("\n" + "=" * 80)
    print("Example Complete!")
    print("=" * 80)


if __name__ == '__main__':
    try:
        main()
    except ImportError as e:
        print(f"Error: {e}")
        print("\nTo run this example, install required dependencies:")
        print("  pip install pandas cel-python")
        print("Or install with all integrations:")
        print("  pip install wxdi[pandas]")

# Made with Bob
