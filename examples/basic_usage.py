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
Basic usage example for Data Quality functionality of IBM watsonx.data intelligence SDK
Demonstrates all 9 validation checks
"""

from wxdi.dq_validator import (
    AssetMetadata, ColumnMetadata, DataType,
    Validator, ValidationRule, ValidationResult,
    ComparisonCheck, ComparisonOperator, ValidValuesCheck, LengthCheck,
    CaseCheck, ColumnCaseEnum, CompletenessCheck, RangeCheck, RegexCheck,
    DataTypeCheck, FormatCheck, FormatConstraintType,
    DateTimeFormats  # Import DateTimeFormats for readable format constants
)
from wxdi.dq_validator.datatypes import DataType as DType, DataTypeEnum


def main():
    # Step 1: Define asset metadata
    print("=" * 60)
    print("IBM watsonx.data intelligence SDK - Basic Usage Example")
    print("=" * 60)

    metadata = AssetMetadata(
        table_name='employee_data',
        columns=[
            ColumnMetadata('emp_id', DataType.INTEGER),
            ColumnMetadata('name', DataType.STRING, length=100),
            ColumnMetadata('email', DataType.STRING, length=255),
            ColumnMetadata('age', DataType.INTEGER),
            ColumnMetadata('department', DataType.STRING, length=50),
            ColumnMetadata('salary', DataType.DECIMAL, precision=10, scale=2),
            ColumnMetadata('min_salary', DataType.DECIMAL, precision=10, scale=2),
            ColumnMetadata('phone', DataType.STRING, length=20),
            ColumnMetadata('status', DataType.STRING, length=20),
            ColumnMetadata('bonus', DataType.DECIMAL, precision=10, scale=2),
            ColumnMetadata('hire_date', DataType.DATE),
            ColumnMetadata('employee_code', DataType.STRING, length=10)
        ]
    )

    print(f"\nAsset: {metadata.table_name}")
    print(f"Columns: {len(metadata.columns)}")

    # Step 2: Create validator with rules
    validator = Validator(metadata)

    # Add length check for name (works with any type)
    validator.add_rule(
        ValidationRule('name')
            .add_check(LengthCheck(min_length=2, max_length=100))
    )

    # Add length check for emp_id (integer converted to string)
    validator.add_rule(
        ValidationRule('emp_id')
            .add_check(LengthCheck(min_length=4, max_length=6))
    )

    # Add valid values check for department (case-insensitive)
    validator.add_rule(
        ValidationRule('department')
            .add_check(ValidValuesCheck(
                ['Engineering', 'Sales', 'HR', 'Finance'],
                case_sensitive=False
            ))
    )

    # Add comparison checks using enum
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
        ValidationRule('salary')
            .add_check(ComparisonCheck(
                operator=ComparisonOperator.GREATER_THAN,
                target_column='min_salary'
            ))
    )

    # Add CaseCheck for email (must be lowercase)
    validator.add_rule(
        ValidationRule('email')
            .add_check(CaseCheck(case_type=ColumnCaseEnum.LOWER_CASE))
    )

    # Add CompletenessCheck for name (required field)
    validator.add_rule(
        ValidationRule('name')
            .add_check(CompletenessCheck(missing_values_allowed=False))
    )

    # Add RangeCheck for bonus (0 to 50000)
    validator.add_rule(
        ValidationRule('bonus')
            .add_check(RangeCheck(min_value=0, max_value=50000))
    )

    # Add RegexCheck for phone (format: XXX-XXX-XXXX)
    validator.add_rule(
        ValidationRule('phone')
            .add_check(RegexCheck(pattern=r'^\d{3}-\d{3}-\d{4}$'))
    )

    # Add CaseCheck for status (must be NameCase)
    validator.add_rule(
        ValidationRule('status')
            .add_check(CaseCheck(case_type=ColumnCaseEnum.NAME_CASE))
    )

    # Add DataTypeCheck for age (must be INTEGER)
    validator.add_rule(
        ValidationRule('age')
            .add_check(DataTypeCheck(expected_type=DType(dtype=DataTypeEnum.INT32)))
    )

    # Add FormatCheck for hire_date (must be valid date format)
    # NEW: Using DateTimeFormats constants for readable format names
    validator.add_rule(
        ValidationRule('hire_date')
            .add_check(FormatCheck(
                constraint_type=FormatConstraintType.ValidFormats,
                formats={
                    DateTimeFormats.ISO_DATE,        # 2020-01-15
                    DateTimeFormats.UK_DATE_SLASH,   # 01/12/2021
                    DateTimeFormats.UK_DATE          # 15-03-2023
                }
            ))
    )

    print(f"\nValidator configured with {len(validator.rules)} rules")
    print("Checks included:")
    print("  - LengthCheck (name, emp_id)")
    print("  - ValidValuesCheck (department)")
    print("  - ComparisonCheck (age, salary)")
    print("  - CaseCheck (email, status)")
    print("  - CompletenessCheck (name)")
    print("  - RangeCheck (bonus)")
    print("  - RegexCheck (phone)")
    print("  - DataTypeCheck (age)")
    print("  - FormatCheck (hire_date)")

    # Step 3: Validate records
    print("\n" + "=" * 60)
    print("Validating Records")
    print("=" * 60)

    records = [
        # [emp_id, name, email, age, department, salary, min_salary, phone, status, bonus, hire_date, employee_code]
        [1001, 'John Doe', 'john@company.com', 30, 'engineering', 75000.00, 60000.00, '555-123-4567', 'Active', 5000.00, '2020-01-15', 'EMP001'],
        [12, 'Jane Smith', 'jane@company.com', 25, 'SALES', 65000.00, 55000.00, '555-234-5678', 'Active', 3000.00, '01/15/2021', 'EMP002'],
        [1003, 'Bob Smith', 'Bob@Company.com', '17', 'hr', 50000.00, 45000.00, '555-345-6789', 'Active', 2000.00, '2022-03-20', 'EMP003'],  # Email not lowercase, age as string
        [1004, 'Alice Johnson', 'alice@company.com', 35, 'Marketing', 80000.00, 70000.00, '555-456-789', 'active', 60000.00, '15-13-2023', 'EMP004'],  # Invalid phone, status not NameCase, bonus too high, invalid date
        [1005, 'Charlie Brown', 'charlie@company.com', 40, 'Finance', 55000.00, 60000.00, '555-567-8901', 'Active', 4000.00, '2023-06-10', 'EMP005'],
        [1006, None, 'test@company.com', 28, 'Engineering', 70000.00, 65000.00, '555-678-9012', 'Active', 3500.00, '07/20/2024', 'EMP006'],  # Name is None (completeness check)
    ]

    results = validator.validate_batch(records)

    # Step 4: Display results
    for idx, result in enumerate(results):
        status_symbol = '[PASS]' if result.is_valid else '[FAIL]'

        print(f"\nRecord {idx + 1}: {status_symbol} (Score: {result.score}, Pass Rate: {result.pass_rate:.1f}%)")

        if not result.is_valid:
            for error in result.errors:
                print(f"  - {error.column_name}: {error.message}")

    # Step 5: Summary statistics
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    total_records = len(results)
    valid_records = sum(1 for r in results if r.is_valid)
    invalid_records = total_records - valid_records
    overall_pass_rate = (valid_records / total_records) * 100

    print(f"Total Records: {total_records}")
    print(f"Valid Records: {valid_records}")
    print(f"Invalid Records: {invalid_records}")
    print(f"Overall Pass Rate: {overall_pass_rate:.1f}%")

    # Step 6: Detailed validation result for first failed record
    print("\n" + "=" * 60)
    print("Detailed Result Example (First Failed Record)")
    print("=" * 60)

    failed_result = next((r for r in results if not r.is_valid), None)
    if failed_result:
        print(f"\nRecord Index: {failed_result.record_index}")
        print(f"Record Data: {failed_result.record}")
        print(f"Total Checks: {failed_result.total_checks}")
        print(f"Passed Checks: {failed_result.passed_checks}")
        print(f"Failed Checks: {failed_result.failed_checks}")
        print(f"\nErrors:")
        for error in failed_result.errors:
            print(f"  - Column: {error.column_name}")
            print(f"    Check: {error.check_name}")
            print(f"    Message: {error.message}")
            print(f"    Value: {error.value}")
            if error.expected:
                print(f"    Expected: {error.expected}")
            print()


if __name__ == '__main__':
    main()

