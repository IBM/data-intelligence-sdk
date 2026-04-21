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
Extended usage example for IBM watsonx.data intelligence SDK
Demonstrates ValidationResultConsolidated for detailed statistics by column and check type
Extends basic_usage.py with consolidation features
"""

from wxdi.dq_validator import (
    AssetMetadata, ColumnMetadata, DataType,
    Validator, ValidationRule, ValidationResultConsolidated,
    ComparisonCheck, ComparisonOperator, ValidValuesCheck, LengthCheck,
    CaseCheck, ColumnCaseEnum, CompletenessCheck, RangeCheck, RegexCheck,
    DataTypeCheck, FormatCheck, FormatConstraintType,
    DateTimeFormats
)
from wxdi.dq_validator.data_quality_dimension import DataQualityDimension
from wxdi.dq_validator.datatypes import DataType as DType, DataTypeEnum


def main():
    # Step 1: Define asset metadata (same as basic_usage.py)
    print("=" * 70)
    print("IBM watsonx.data intelligence SDK - Consolidation Usage Example")
    print("=" * 70)

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

    # Step 2: Create validator with rules (same as basic_usage.py)
    validator = Validator(metadata)

    validator.add_rule(
        ValidationRule('name')
            .add_check(LengthCheck(min_length=2, max_length=100))
            .add_check(CompletenessCheck(missing_values_allowed=False))
    )

    validator.add_rule(
        ValidationRule('emp_id')
            .add_check(LengthCheck(min_length=4, max_length=6))
    )

    validator.add_rule(
        ValidationRule('department')
            .add_check(ValidValuesCheck(
                ['Engineering', 'Sales', 'HR', 'Finance'],
                case_sensitive=False
            ))
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
            .add_check(DataTypeCheck(expected_type=DType(dtype=DataTypeEnum.INT32)))
    )

    validator.add_rule(
        ValidationRule('salary')
            .add_check(ComparisonCheck(
                operator=ComparisonOperator.GREATER_THAN,
                target_column='min_salary'
            ))
    )

    validator.add_rule(
        ValidationRule('email')
            .add_check(CaseCheck(case_type=ColumnCaseEnum.LOWER_CASE))
    )

    validator.add_rule(
        ValidationRule('bonus')
            .add_check(RangeCheck(min_value=0, max_value=50000))
    )

    validator.add_rule(
        ValidationRule('phone')
            .add_check(RegexCheck(pattern=r'^\d{3}-\d{3}-\d{4}$'))
    )

    validator.add_rule(
        ValidationRule('status')
            .add_check(CaseCheck(case_type=ColumnCaseEnum.NAME_CASE))
    )

    validator.add_rule(
        ValidationRule('hire_date')
            .add_check(FormatCheck(
                constraint_type=FormatConstraintType.ValidFormats,
                formats={
                    DateTimeFormats.ISO_DATE,
                    DateTimeFormats.UK_DATE_SLASH,
                    DateTimeFormats.UK_DATE
                }
            ))
    )

    print(f"\nValidator configured with {len(validator.rules)} rules")

    # Step 3: Validate records
    print("\n" + "=" * 70)
    print("Validating Records")
    print("=" * 70)

    records = [
        [1001, 'John Doe', 'john@company.com', 30, 'engineering', 75000.00, 60000.00, '555-123-4567', 'Active', 5000.00, '2020-01-15', 'EMP001'],
        [12, 'Jane Smith', 'jane@company.com', 25, 'SALES', 65000.00, 55000.00, '555-234-5678', 'Active', 3000.00, '01/15/2021', 'EMP002'],
        [1003, 'Bob Smith', 'Bob@Company.com', '17', 'hr', 50000.00, 45000.00, '555-345-6789', 'Active', 2000.00, '2022-03-20', 'EMP003'],
        [1004, 'Alice Johnson', 'alice@company.com', 35, 'Marketing', 80000.00, 70000.00, '555-456-789', 'active', 60000.00, '15-13-2023', 'EMP004'],
        [1005, 'Charlie Brown', 'charlie@company.com', 40, 'Finance', 55000.00, 60000.00, '555-567-8901', 'Active', 4000.00, '2023-06-10', 'EMP005'],
        [1006, None, 'test@company.com', 28, 'Engineering', 70000.00, 65000.00, '555-678-9012', 'Active', 3500.00, '07/20/2024', 'EMP006'],
    ]

    results = validator.validate_batch(records)

    # Display basic results
    for idx, result in enumerate(results):
        status_symbol = '[PASS]' if result.is_valid else '[FAIL]'
        print(f"Record {idx + 1}: {status_symbol} (Score: {result.score})")

    # Step 4: NEW - Use ValidationResultConsolidated for detailed statistics
    print("\n" + "=" * 70)
    print("Consolidated Statistics (NEW FEATURE)")
    print("=" * 70)

    # Create consolidator with error storage enabled
    consolidator = ValidationResultConsolidated(validator=validator, store_errors=True)
    consolidator.add_results(results)

    # Overall statistics
    print("\n[Overall Statistics]")
    overall = consolidator.get_overall_statistics()
    print(f"  Total Records: {overall['total_records']}")
    print(f"  Valid Records: {overall['valid_records']}")
    print(f"  Invalid Records: {overall['invalid_records']}")
    print(f"  Pass Rate: {overall['pass_rate']:.1f}%")
    print(f"  Total Errors: {overall['total_errors']}")

    # Statistics by column
    print("\n[Statistics by Column]")
    print(f"  {'Column':<20} {'Passed':<10} {'Failed':<10} {'Total':<10}")
    print(f"  {'-'*20} {'-'*10} {'-'*10} {'-'*10}")

    for column in sorted(consolidator.get_columns()):
        stats = consolidator.get_column_statistics(column)
        print(f"  {column:<20} {stats['passed']:<10} {stats['failed']:<10} {stats['total']:<10}")

    # Statistics by check type
    print("\n[Statistics by Check Type]")
    print(f"  {'Check Type':<30} {'Passed':<10} {'Failed':<10} {'Total':<10}")
    print(f"  {'-'*30} {'-'*10} {'-'*10} {'-'*10}")

    for check in sorted(consolidator.get_checks()):
        stats = consolidator.get_check_statistics(check)
        print(f"  {check:<30} {stats['passed']:<10} {stats['failed']:<10} {stats['total']:<10}")

    # Combined statistics (column + check)
    print("\n[Combined Statistics (Column + Check Type)]")
    combined = consolidator.get_combined_statistics()

    for column in sorted(combined.keys()):
        print(f"\n  {column}:")
        for check, stats in sorted(combined[column].items()):
            print(f"    {check:<28} Failed: {stats['failed']}  Passed: {stats['passed']}")

    # Error details for specific columns
    print("\n" + "=" * 70)
    print("Error Details by Column")
    print("=" * 70)

    # Show errors for columns with failures
    columns_with_errors = [col for col in consolidator.get_columns()
                          if consolidator.get_column_statistics(col)['failed'] > 0]

    for column in sorted(columns_with_errors)[:3]:  # Show first 3 columns with errors
        errors = consolidator.get_errors_by_column(column)
        print(f"\n[X] {column} ({len(errors)} error(s)):")
        for error in errors[:2]:  # Show first 2 errors per column
            print(f"  Record {error['record_index']}: {error['message']}")
            print(f"    Value: {error['value']}")
            if error['expected']:
                print(f"    Expected: {error['expected']}")

    # Error details by check type
    print("\n" + "=" * 70)
    print("Error Details by Check Type")
    print("=" * 70)

    # Show errors for specific check types
    check_types_with_errors = [check for check in consolidator.get_checks()
                               if consolidator.get_check_statistics(check)['failed'] > 0]

    for check in sorted(check_types_with_errors)[:3]:  # Show first 3 check types
        errors = consolidator.get_errors_by_check(check)
        print(f"\n[Check: {check}] ({len(errors)} error(s)):")
        for error in errors[:2]:  # Show first 2 errors per check
            print(f"  Column '{error['column']}' at record {error['record_index']}: {error['message']}")

    # Specific column + check combination
    print("\n" + "=" * 70)
    print("Specific Column + Check Combination")
    print("=" * 70)

    # Example: Get all case_check errors for email column
    if 'email' in consolidator.get_columns() and 'case_check' in consolidator.get_checks():
        email_case_errors = consolidator.get_errors_by_column_and_check('email', 'case_check')
        print(f"\n[Email Case Check Errors]: {len(email_case_errors)}")
        for error in email_case_errors:
            print(f"  Record {error['record_index']}: {error['message']}")
            print(f"    Value: '{error['value']}'")

    # Issues by Data Quality Dimension
    print("\n" + "=" * 70)
    print("Issues by Data Quality Dimension")
    print("=" * 70)

    # 1. Get issues for all dimensions
    print("\n[All Dimensions]")
    print(f"  {'Dimension':<20} {'Issues':<10}")
    print(f"  {'-'*20} {'-'*10}")

    all_dimension_issues = consolidator.get_all_dimension_issues()
    for dimension_name, issue_count in sorted(all_dimension_issues.items()):
        print(f"  {dimension_name:<20} {issue_count:<10}")

    # 2. Get issues for only the VALIDITY dimension
    print("\n[VALIDITY Dimension Only]")
    validity_issues = consolidator.get_issues_by_dimension(DataQualityDimension.VALIDITY)
    print(f"  VALIDITY: {validity_issues} issue(s)")

    # Step 5: Report Issues to CPD (Optional)
    print("\n" + "=" * 70)
    print("Reporting Issues to CPD (Optional)")
    print("=" * 70)

    # Uncomment and configure the following section to report issues to CAMS
    from wxdi.dq_validator.provider import ProviderConfig
    from wxdi.dq_validator.issue_reporting import IssueReporter

    # Configure provider
    config = ProviderConfig(
        url="https://your-cpd-instance.com",
        auth_token="Bearer your-token-here",
        project_id="your-project-id-here"
    )

    # Initialize IssueReporter
    reporter = IssueReporter(config)
    print("\n[IssueReporter Initialized]")
    print("  ✓ CheckProvider ready")
    print("  ✓ IssuesProvider ready")
    print("  ✓ DimensionProvider ready")
    print("  ✓ AssetProvider ready")

    # Report issues
    cams_asset_id = "your-asset-id-here"

    print(f"\n[Configuration]")
    print(f"  Asset ID: {cams_asset_id}")
    print(f"  Project ID: {config.project_id}")

    try:
        reporter.report_issues(
            stats=combined,
            asset_id=cams_asset_id,
            validator=validator
        )
        print("\n[SUCCESS] Issues reported to CPD successfully!")

    except Exception as e:
        print(f"\n[ERROR] Failed to report issues: {str(e)}")

    print("\n[Note] Issue reporting to CPD is optional and requires:")
    print("  1. Valid CPD instance URL")
    print("  2. Authentication token")
    print("  3. CAMS asset ID")
    print("  4. Project ID or Catalog ID")
    print("  Uncomment the code above and configure to enable.")

    # Export to dictionary
    print("\n" + "=" * 70)
    print("Export Consolidated Data")
    print("=" * 70)

    consolidated_dict = consolidator.to_dict()
    print(f"\n[Consolidated data structure]")
    print(f"  - Overall statistics: {len(consolidated_dict['overall'])} metrics")
    print(f"  - Columns tracked: {len(consolidated_dict['columns'])}")
    print(f"  - Check types tracked: {len(consolidated_dict['checks'])}")
    print(f"  - Total errors stored: {consolidated_dict['error_count']}")

    # Memory-efficient mode demonstration
    print("\n" + "=" * 70)
    print("Memory-Efficient Mode (No Error Storage)")
    print("=" * 70)

    # Create consolidator without error storage
    consolidator_lite = ValidationResultConsolidated(validator=validator, store_errors=False)
    consolidator_lite.add_results(results)

    print("\n[Memory-efficient consolidator]")
    print(f"  Total Records: {consolidator_lite.total_records}")
    print(f"  Valid Records: {consolidator_lite.valid_records}")
    print(f"  Statistics available: YES")
    print(f"  Error details available: NO (memory efficient)")

    # Try to access error details (will raise error)
    try:
        consolidator_lite.get_errors_by_column('email')
    except RuntimeError as e:
        print(f"\n  Expected error when accessing error details: {str(e)[:50]}...")

    print("\n" + "=" * 70)
    print("[SUCCESS] Consolidation example completed!")
    print("=" * 70)


if __name__ == '__main__':
    main()