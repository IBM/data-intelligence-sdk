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
CEL (Common Expression Language) Validation Example

This example demonstrates how to use CEL expressions for custom validation
logic in the IBM watsonx.data Intelligence SDK.

CEL provides flexible, safe expression evaluation for complex business rules
that go beyond the capabilities of predefined validation checks.

SYNTAX OPTIONS:
- Simple Syntax (RECOMMENDED): 'value > min_salary', 'age > 40'
  Column names can be referenced directly without 'record.' prefix
  
- Explicit Syntax (still supported): 'value > record.min_salary', 'record.age > 40'
  Use 'record.' prefix for explicit column access

Both syntaxes work identically and can be mixed in the same validation rules.
"""

from wxdi.dq_validator import (
    AssetMetadata, ColumnMetadata, DataType,
    Validator, ValidationRule,
    CELCheck, RangeCheck, CompletenessCheck
)


def main():
    print("=" * 70)
    print("CEL (Common Expression Language) Validation Example")
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
            ColumnMetadata('status', DataType.STRING, length=20),
        ]
    )
    
    print(f"\nAsset: {metadata.table_name}")
    print(f"Columns: {len(metadata.columns)}")
    
    # Step 2: Create validator with CEL checks
    validator = Validator(metadata)
    
    # Example 1: Simple value validation
    print("\n" + "=" * 70)
    print("Example 1: Simple Value Validation")
    print("=" * 70)
    print("Rule: Salary must be positive")
    print("CEL Expression: 'value > 0'")
    
    validator.add_rule(
        ValidationRule('salary')
            .add_check(CELCheck(
                expression='value > 0',
                error_message='Salary must be positive'
            ))
    )
    
    # Example 2: Multi-column comparison (SIMPLE SYNTAX)
    print("\n" + "=" * 70)
    print("Example 2: Multi-Column Comparison (Simple Syntax)")
    print("=" * 70)
    print("Rule: Salary must be greater than minimum salary")
    print("Simple Syntax: 'value > min_salary'")
    print("(Also works: 'value > record.min_salary')")
    
    validator.add_rule(
        ValidationRule('salary')
            .add_check(CELCheck(
                expression='value > min_salary',  # Simple syntax
                error_message='Salary must exceed minimum salary'
            ))
    )
    
    # Example 3: Complex business logic with conditional (SIMPLE SYNTAX)
    print("\n" + "=" * 70)
    print("Example 3: Age-Based Salary Requirements (Simple Syntax)")
    print("=" * 70)
    print("Rule: Senior employees (age > 40) must earn at least $80,000")
    print("      Junior employees (age <= 40) must earn at least $50,000")
    print("Simple Syntax: 'age > 40 ? value >= 80000 : value >= 50000'")
    print("(Also works: 'record.age > 40 ? value >= 80000 : value >= 50000')")
    
    validator.add_rule(
        ValidationRule('salary')
            .add_check(CELCheck(
                expression='age > 40 ? value >= 80000 : value >= 50000',  # Simple syntax
                error_message='Salary does not meet age-based requirements'
            ))
    )
    
    # Example 4: String operations
    print("\n" + "=" * 70)
    print("Example 4: Email Domain Validation")
    print("=" * 70)
    print("Rule: Email must be from company domain")
    print("CEL Expression: 'value.endsWith(\"@company.com\")'")
    
    validator.add_rule(
        ValidationRule('email')
            .add_check(CELCheck(
                expression='value.endsWith("@company.com")',
                error_message='Email must be from company domain (@company.com)'
            ))
    )
    
    # Example 5: List membership
    print("\n" + "=" * 70)
    print("Example 5: Status Validation")
    print("=" * 70)
    print("Rule: Status must be one of: Active, Pending, Approved")
    print("CEL Expression: 'value in [\"Active\", \"Pending\", \"Approved\"]'")
    
    validator.add_rule(
        ValidationRule('status')
            .add_check(CELCheck(
                expression='value in ["Active", "Pending", "Approved"]',
                error_message='Invalid status value'
            ))
    )
    
    # Example 6: Department-based bonus limits (SIMPLE SYNTAX)
    print("\n" + "=" * 70)
    print("Example 6: Department-Based Bonus Limits (Simple Syntax)")
    print("=" * 70)
    print("Rule: Sales can have bonus up to $20K, others up to $10K")
    print("Simple Syntax: 'department == \"Sales\" ? value <= 20000 : value <= 10000'")
    print("(Also works: 'record.department == \"Sales\" ? value <= 20000 : value <= 10000')")
    
    validator.add_rule(
        ValidationRule('bonus')
            .add_check(CELCheck(
                expression='department == "Sales" ? value <= 20000 : value <= 10000',  # Simple syntax
                error_message='Bonus exceeds department limit'
            ))
    )
    
    # Example 7: Arithmetic with simple syntax
    print("\n" + "=" * 70)
    print("Example 7: Arithmetic Operations (Simple Syntax)")
    print("=" * 70)
    print("Rule: Salary must be at least 20% above minimum")
    print("Simple Syntax: 'value >= min_salary * 1.2'")
    
    validator.add_rule(
        ValidationRule('salary')
            .add_check(CELCheck(
                expression='value >= min_salary * 1.2',  # Simple syntax
                error_message='Salary must be at least 20% above minimum'
            ))
    )
    
    # Example 8: Combining CEL with other checks (SIMPLE SYNTAX)
    print("\n" + "=" * 70)
    print("Example 8: Combining CEL with Other Checks")
    print("=" * 70)
    print("Combining: CompletenessCheck + RangeCheck + CELCheck")
    print("Simple Syntax: 'value >= 21 || department != \"Sales\"'")
    
    validator.add_rule(
        ValidationRule('age')
            .add_check(CompletenessCheck(missing_values_allowed=False))
            .add_check(RangeCheck(min_value=18, max_value=65))
            .add_check(CELCheck(
                expression='value >= 21 || department != "Sales"',  # Simple syntax
                error_message='Sales employees must be at least 21 years old'
            ))
    )
    
    print(f"\nValidator configured with {len(validator.rules)} rules")
    
    # Step 3: Test with sample records
    print("\n" + "=" * 70)
    print("Validating Sample Records")
    print("=" * 70)
    
    records = [
        # [emp_id, name, email, age, department, salary, min_salary, bonus, status]
        [1001, 'John Doe', 'john@company.com', 30, 'Engineering', 75000.00, 60000.00, 5000.00, 'Active'],
        [1002, 'Jane Smith', 'jane@other.com', 45, 'Sales', 85000.00, 70000.00, 18000.00, 'Active'],
        [1003, 'Bob Wilson', 'bob@company.com', 20, 'Sales', 55000.00, 50000.00, 8000.00, 'Pending'],
        [1004, 'Alice Brown', 'alice@company.com', 50, 'Engineering', 70000.00, 60000.00, 12000.00, 'Inactive'],
        [1005, 'Charlie Davis', 'charlie@company.com', 35, 'Sales', 90000.00, 70000.00, 25000.00, 'Active'],
    ]
    
    results = validator.validate_batch(records)
    
    # Step 4: Display results
    for idx, result in enumerate(results):
        record = records[idx]
        status_symbol = '[PASS]' if result.is_valid else '[FAIL]'
        
        print(f"\nRecord {idx + 1}: {status_symbol}")
        print(f"  Employee: {record[1]} ({record[4]})")
        print(f"  Age: {record[3]}, Salary: ${record[5]:,.2f}, Bonus: ${record[7]:,.2f}")
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
    
    # Step 6: CEL Expression Tips
    print("\n" + "=" * 70)
    print("CEL Expression Tips")
    print("=" * 70)
    print("""
1. Available Variables:
   - value: Current column value
   - record: Dictionary of all column values (e.g., record.age, record.salary)
   - column_name: Name of the column being validated
   - record_index: Position of the record in the batch

2. Supported Operators:
   - Comparison: ==, !=, <, <=, >, >=
   - Logical: &&, ||, !
   - Arithmetic: +, -, *, /, %
   - String: contains, startsWith, endsWith, matches
   - List: in, size, all, exists
   - Ternary: condition ? true_value : false_value

3. Best Practices:
   - Keep expressions simple and readable
   - Use descriptive error messages
   - Test expressions with sample data
   - Combine with other checks for comprehensive validation
   - Use ternary operator for conditional logic

4. Performance:
   - Expressions are compiled once at initialization
   - Evaluation is fast (~10-100 microseconds per record)
   - Suitable for high-throughput validation
    """)
    
    print("\n" + "=" * 70)
    
    # Example 9: Variable Bindings for Reusable Templates
    print("\n" + "=" * 70)
    print("Example 9: Variable Bindings (Reusable Templates)")
    print("=" * 70)
    print("Create reusable validation templates with generic variable names")
    print("that map to actual column names via bindings.")
    
    # Create a reusable template
    range_template = 'current > minimum'
    
    # Apply to salary
    validator.add_rule(
        ValidationRule('salary')
            .add_check(CELCheck(
                expression=range_template,
                bindings={'current': 'salary', 'minimum': 'min_salary'},
                error_message='Salary below minimum'
            ))
    )
    
    # Apply same template to bonus with different bindings
    # (Note: This would need a min_bonus column in real usage)
    print("\nSame template, different columns:")
    print("  Salary check: bindings={'current': 'salary', 'minimum': 'min_salary'}")
    print("  Bonus check:  bindings={'current': 'bonus', 'minimum': 'min_bonus'}")
    print("\nBenefits:")
    print("  - Write validation logic once, reuse many times")
    print("  - Update template in one place, affects all uses")
    print("  - Generic names make intent clearer")
    print("  - Backward compatible (bindings are optional)")
    print("Example Complete!")
    print("=" * 70)


if __name__ == '__main__':
    try:
        main()
    except ImportError as e:
        print(f"Error: {e}")
        print("\nTo run this example, install cel-python:")
        print("  pip install cel-python>=0.5.0")
        print("Or install the full SDK:")
        print("  pip install data-intelligence-sdk")

# Made with Bob
