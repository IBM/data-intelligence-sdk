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
Table-Level CEL (Common Expression Language) Validation Example

This example demonstrates how to use table-level CEL expressions for
cross-column validation and complex business rules that span multiple fields.

KEY DIFFERENCES FROM COLUMN-LEVEL CEL:
- Column-level: Validates individual column values (e.g., 'value > 0')
- Table-level: Validates entire records (e.g., 'salary > min_salary && age >= 18')

WHEN TO USE TABLE-LEVEL CEL:
- Cross-column validation (start_date < end_date)
- Complex business rules spanning multiple fields
- Conditional logic based on multiple columns
- Record-level consistency checks
"""

from wxdi.dq_validator import (
    AssetMetadata, ColumnMetadata, DataType,
    Validator, ValidationRule, TableValidationRule,
    CELCheck, TableCELCheck, CompletenessCheck
)


def main():
    print("=" * 70)
    print("Table-Level CEL Validation Example")
    print("=" * 70)
    
    # Step 1: Define asset metadata
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
            ColumnMetadata('start_date', DataType.STRING, length=10),
            ColumnMetadata('end_date', DataType.STRING, length=10),
        ]
    )
    
    print(f"\nAsset: {metadata.table_name}")
    print(f"Columns: {len(metadata.columns)}")
    
    # Step 2: Create validator with table-level CEL checks
    validator = Validator(metadata)
    
    # Example 1: Multi-column comparison
    print("\n" + "=" * 70)
    print("Example 1: Multi-Column Salary Validation")
    print("=" * 70)
    print("Rule: Salary must exceed minimum salary")
    print("Table CEL: 'salary > min_salary'")
    
    validator.add_table_rule(
        TableValidationRule('salary_check')
            .add_check(TableCELCheck(
                'salary > min_salary',
                error_message='Salary must exceed minimum salary'
            ))
    )
    
    # Example 2: Complex age-based business rules
    print("\n" + "=" * 70)
    print("Example 2: Age-Based Salary Requirements")
    print("=" * 70)
    print("Rule: Senior employees (age > 40) must earn at least $80,000")
    print("      Junior employees (age <= 40) must earn at least $50,000")
    print("Table CEL: 'age > 40 ? salary >= 80000 : salary >= 50000'")
    
    validator.add_table_rule(
        TableValidationRule('age_salary_check')
            .add_check(TableCELCheck(
                'age > 40 ? salary >= 80000 : salary >= 50000',
                error_message='Salary does not meet age-based requirements'
            ))
    )
    
    # Example 3: Department-specific rules
    print("\n" + "=" * 70)
    print("Example 3: Department-Specific Validation")
    print("=" * 70)
    print("Rule: Sales employees must be at least 21 years old")
    print("Table CEL: 'department == \"Sales\" ? age >= 21 : true'")
    
    validator.add_table_rule(
        TableValidationRule('sales_age_check')
            .add_check(TableCELCheck(
                'department == "Sales" ? age >= 21 : true',
                error_message='Sales employees must be at least 21 years old'
            ))
    )
    
    # Example 4: Bonus limits by department
    print("\n" + "=" * 70)
    print("Example 4: Department-Based Bonus Limits")
    print("=" * 70)
    print("Rule: Sales can have bonus up to $20K, others up to $10K")
    print("Table CEL: 'department == \"Sales\" ? bonus <= 20000 : bonus <= 10000'")
    
    validator.add_table_rule(
        TableValidationRule('bonus_limit_check')
            .add_check(TableCELCheck(
                'department == "Sales" ? bonus <= 20000 : bonus <= 10000',
                error_message='Bonus exceeds department limit'
            ))
    )
    
    # Example 5: Date consistency
    print("\n" + "=" * 70)
    print("Example 5: Date Consistency Check")
    print("=" * 70)
    print("Rule: Start date must be before end date")
    print("Table CEL: 'start_date < end_date'")
    
    validator.add_table_rule(
        TableValidationRule('date_consistency')
            .add_check(TableCELCheck(
                'start_date < end_date',
                error_message='Start date must be before end date'
            ))
    )
    
    # Example 6: Complex multi-field validation
    print("\n" + "=" * 70)
    print("Example 6: Complex Multi-Field Validation")
    print("=" * 70)
    print("Rule: Total compensation (salary + bonus) must be reasonable")
    print("Table CEL: 'salary + bonus <= min_salary * 2.5'")
    
    validator.add_table_rule(
        TableValidationRule('total_comp_check')
            .add_check(TableCELCheck(
                'salary + bonus <= min_salary * 2.5',
                error_message='Total compensation exceeds 2.5x minimum salary'
            ))
    )
    
    # Example 7: Combining column-level and table-level rules
    print("\n" + "=" * 70)
    print("Example 7: Combining Column and Table Rules")
    print("=" * 70)
    print("Column Rule: Email must not be null")
    print("Table Rule: Email domain must match department")
    
    # Column-level: Basic completeness check
    validator.add_rule(
        ValidationRule('email')
            .add_check(CompletenessCheck(missing_values_allowed=False))
    )
    
    # Table-level: Cross-field validation
    validator.add_table_rule(
        TableValidationRule('email_domain_check')
            .add_check(TableCELCheck(
                'department == "Sales" ? email.endsWith("@sales.company.com") : email.endsWith("@company.com")',
                error_message='Email domain does not match department'
            ))
    )
    
    print(f"\nValidator configured with:")
    print(f"  - {len(validator.rules)} column-level rules")
    print(f"  - {len(validator.table_rules)} table-level rules")
    
    # Step 3: Test with sample records
    print("\n" + "=" * 70)
    print("Validating Sample Records")
    print("=" * 70)
    
    records = [
        # [emp_id, name, email, age, department, salary, min_salary, bonus, start_date, end_date]
        [1001, 'John Doe', 'john@company.com', 30, 'Engineering', 75000.00, 60000.00, 5000.00, '2020-01-01', '2025-12-31'],
        [1002, 'Jane Smith', 'jane@sales.company.com', 45, 'Sales', 85000.00, 70000.00, 18000.00, '2019-06-15', '2024-06-15'],
        [1003, 'Bob Wilson', 'bob@sales.company.com', 20, 'Sales', 55000.00, 50000.00, 8000.00, '2021-03-01', '2026-03-01'],
        [1004, 'Alice Brown', 'alice@company.com', 50, 'Engineering', 70000.00, 60000.00, 12000.00, '2018-09-01', '2023-09-01'],
        [1005, 'Charlie Davis', 'charlie@sales.company.com', 35, 'Sales', 90000.00, 70000.00, 25000.00, '2020-11-01', '2025-11-01'],
        [1006, 'Eve Martinez', 'eve@company.com', 28, 'HR', 62000.00, 55000.00, 7000.00, '2022-01-15', '2027-01-15'],
        [1007, 'Frank Lee', 'frank@company.com', 42, 'Engineering', 95000.00, 75000.00, 9000.00, '2017-04-01', '2022-04-01'],
        [1008, 'Grace Kim', 'grace@company.com', 38, 'Finance', 78000.00, 65000.00, 8500.00, '2025-01-01', '2024-01-01'],  # Invalid: end_date < start_date
    ]
    
    results = validator.validate_batch(records)
    
    # Step 4: Display results
    for idx, result in enumerate(results):
        record = records[idx]
        status_symbol = '[PASS]' if result.is_valid else '[FAIL]'
        
        print(f"\nRecord {idx + 1}: {status_symbol}")
        print(f"  Employee: {record[1]} ({record[4]})")
        print(f"  Age: {record[3]}, Salary: ${record[5]:,.2f}, Bonus: ${record[7]:,.2f}")
        print(f"  Dates: {record[8]} to {record[9]}")
        print(f"  Score: {result.score}, Pass Rate: {result.pass_rate:.1f}%")
        
        if not result.is_valid:
            print(f"  Errors ({len(result.errors)}):")
            for error in result.errors:
                print(f"    - {error.column_name}: {error.message}")
    
    # Step 5: Summary statistics
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    
    total_records = len(results)
    valid_records = sum(1 for r in results if r.is_valid)
    invalid_records = total_records - valid_records
    overall_pass_rate = (valid_records / total_records) * 100
    
    print(f"Total Records: {total_records}")
    print(f"Valid Records: {valid_records}")
    print(f"Invalid Records: {invalid_records}")
    print(f"Overall Pass Rate: {overall_pass_rate:.1f}%")
    
    # Step 6: Key Takeaways
    print("\n" + "=" * 70)
    print("Key Takeaways: Table-Level vs Column-Level CEL")
    print("=" * 70)
    print("""
COLUMN-LEVEL CEL (CELCheck):
- Validates individual column values
- Has access to 'value' variable (current column)
- Example: CELCheck('value > 0')
- Use for: Single-column validation

TABLE-LEVEL CEL (TableCELCheck):
- Validates entire records
- NO 'value' variable (no single column focus)
- Direct access to all columns
- Example: TableCELCheck('salary > min_salary && age >= 18')
- Use for: Cross-column validation, complex business rules

WHEN TO USE EACH:
+------------------------------------------------------------------+
| Column-Level CEL                | Table-Level CEL                |
+----------------------------------+--------------------------------+
| - Single column validation      | - Cross-column validation      |
| - Value range checks            | - Multi-field business rules   |
| - Format validation             | - Conditional logic            |
| - Simple comparisons            | - Date consistency             |
|                                 | - Complex calculations         |
+----------------------------------+--------------------------------+

BEST PRACTICES:
1. Use column-level for simple, single-field checks
2. Use table-level for cross-field validation
3. Combine both for comprehensive validation
4. Keep expressions readable and maintainable
5. Use descriptive rule names for error tracking
""")
    
    # Example 8: Variable Bindings for Reusable Table Rules
    print("\n" + "=" * 70)
    print("Example 8: Variable Bindings (Reusable Table Rules)")
    print("=" * 70)
    print("Create reusable table-level validation templates with generic")
    print("variable names that map to actual column names via bindings.")
    
    # Create a reusable template for age-based validation
    age_based_template = 'person_age >= min_age && compensation > minimum'
    
    # Apply with bindings
    validator.add_table_rule(
        TableValidationRule('eligibility_check')
            .add_check(TableCELCheck(
                expression=age_based_template,
                bindings={
                    'person_age': 'age',
                    'min_age': 'age',  # Could map to different column in other contexts
                    'compensation': 'salary',
                    'minimum': 'min_salary'
                },
                error_message='Employee does not meet eligibility requirements'
            ))
    )
    
    print("\nTemplate: 'person_age >= min_age && compensation > minimum'")
    print("Bindings: {'person_age': 'age', 'compensation': 'salary', ...}")
    print("\nBenefits:")
    print("  - Reusable across different data contexts")
    print("  - Generic names clarify business intent")
    print("  - Same template for different column combinations")
    print("  - Backward compatible (bindings are optional)")
    
    print("\n" + "=" * 70)
    print("Example Complete!")
    print("=" * 70)


if __name__ == '__main__':
    try:
        main()
    except ImportError as e:
        print(f"Error: {e}")
        print("\nTo run this example, install required dependencies:")
        print("  pip install cel-python>=0.5.0")

# Made with Bob
