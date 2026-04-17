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
End-to-End Data Quality Validation Example

This comprehensive example demonstrates the complete workflow:
1. Generate authentication token for IBM Cloud environment
2. Load asset metadata from CAMS API using DQAssetsProvider
3. Load data from a CSV file using Pandas DataFrame
4. Add additional validation rules (e.g., range check)
5. Run validation on the DataFrame
6. Print and analyze the results

Prerequisites:
- IBM Cloud API key
- Project ID or Catalog ID
- Asset ID from CAMS
- CSV file matching the asset metadata
- pandas library installed
"""

import pandas as pd
from wxdi.common.auth import AuthConfig, EnvironmentType, AuthProvider
from wxdi.dq_validator.provider import ProviderConfig
from wxdi.dq_validator.provider.cams import CamsProvider
from wxdi.dq_validator.rule_loader import RuleLoader
from wxdi.dq_validator import ValidationRule, RangeCheck, ComparisonCheck, ComparisonOperator
from wxdi.dq_validator.integrations import PandasValidator


def main():
    """
    Main function demonstrating end-to-end data quality validation workflow.
    """
    print("=" * 80)
    print("END-TO-END DATA QUALITY VALIDATION EXAMPLE")
    print("=" * 80)

    # =========================================================================
    # Step 1: Generate Authentication Token for IBM Cloud
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 1: Generate Authentication Token")
    print("=" * 80)

    # Configure authentication for IBM Cloud environment
    # Replace with your actual IBM Cloud API key
    auth_config = AuthConfig(
        environment_type=EnvironmentType.IBM_CLOUD,
        api_key='your-ibm-cloud-api-key-here',
        url='https://iam.test.cloud.ibm.com',  # Optional, default URL is used if not provided

        # url is optional for production IBM Cloud (default URL is used)
        # disable_ssl_verification=True  # Optional, default is True
    )

    print(f"\nEnvironment Type: {auth_config.environment_type.value}")
    print(f"Authentication URL: {auth_config.url}")

    # Create auth provider and get token
    auth_provider = AuthProvider(auth_config)
    print(f"Authenticator Type: {type(auth_provider.authenticator).__name__}")

    # Get the authentication token
    # Uncomment the following lines when you have valid credentials
    # try:
    #     auth_token = auth_provider.get_token()
    #     print(f"✓ Token generated successfully: {auth_token[:20]}...")
    # except Exception as e:
    #     print(f"✗ Error generating token: {e}")
    #     return

    # For demonstration purposes, using a placeholder token
    auth_token = "Bearer your-auth-token-here"
    print(f"✓ Using token: {auth_token[:30]}...")

    # =========================================================================
    # Step 2: Load Asset Metadata from CAMS API
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 2: Load Asset Metadata from CAMS")
    print("=" * 80)

    # Configure the provider with your instance URL and authentication
    base_url = "https://your-instance.cloud.ibm.com"
    project_id = "your-project-id-here"  # Or use catalog_id instead
    asset_id = "your-asset-id-here"

    print(f"\nConfiguration:")
    print(f"  Base URL: {base_url}")
    print(f"  Project ID: {project_id}")
    print(f"  Asset ID: {asset_id}")

    # Create provider configuration
    provider_config = ProviderConfig(
        url=base_url,
        auth_token=auth_token,
        project_id=project_id
    )

    # Create CAMS provider
    cams_provider = CamsProvider(provider_config)
    print(f"\n✓ CAMS Provider initialized")

    # Load asset metadata and validation rules from CAMS
    # Uncomment the following lines when you have valid credentials
    # try:
    #     data_asset = cams_provider.get_asset_by_id(asset_id)
    #     print(f"✓ Asset loaded: {data_asset.metadata.name}")
    #     print(f"  Asset Type: {data_asset.metadata.asset_type}")
    #     print(f"  Columns: {len(data_asset.entity.data_asset.columns)}")
    #
    #     # Use RuleLoader to extract metadata and validation rules
    #     rule_loader = RuleLoader(base_url, auth_token)
    #     validator = rule_loader.load_from_data_asset(data_asset)
    #     print(f"✓ Validator created with {len(validator.rules)} rules from CAMS")
    # except Exception as e:
    #     print(f"✗ Error loading asset: {e}")
    #     return

    # For demonstration, create sample metadata manually
    from wxdi.dq_validator import AssetMetadata, ColumnMetadata, DataType, Validator

    metadata = AssetMetadata(
        table_name='customer_data',
        columns=[
            ColumnMetadata('customer_id', DataType.INTEGER),
            ColumnMetadata('name', DataType.STRING, length=100),
            ColumnMetadata('email', DataType.STRING, length=255),
            ColumnMetadata('age', DataType.INTEGER),
            ColumnMetadata('account_balance', DataType.DECIMAL, precision=10, scale=2),
            ColumnMetadata('registration_date', DataType.DATE),
            ColumnMetadata('status', DataType.STRING, length=20),
        ]
    )

    print(f"\n✓ Using sample metadata:")
    print(f"  Table: {metadata.table_name}")
    print(f"  Columns: {len(metadata.columns)}")
    for col in metadata.columns:
        print(f"    - {col.name} ({col.data_type.value})")

    # Create validator with metadata
    validator = Validator(metadata)
    print(f"\n✓ Validator initialized")

    # =========================================================================
    # Step 3: Load Data from CSV File using Pandas
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 3: Load Data from CSV File")
    print("=" * 80)

    # For demonstration, create sample data that matches the metadata
    # In production, you would load from an actual CSV file:
    # df = pd.read_csv('customer_data.csv')

    sample_data = {
        'customer_id': [1001, 1002, 1003, 1004, 1005, 1006],
        'name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Williams', 'Charlie Brown', 'Diana Prince'],
        'email': ['john@example.com', 'jane@example.com', 'bob@invalid', 'alice@example.com', 'charlie@example.com', 'diana@example.com'],
        'age': [25, 30, 17, 45, 35, 28],  # Note: 17 is below typical minimum age
        'account_balance': [1500.50, 2500.75, 500.00, 5000.00, 3500.25, 1200.00],
        'registration_date': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05', '2023-05-12', '2023-06-18'],
        'status': ['active', 'active', 'pending', 'active', 'inactive', 'active']
    }

    df = pd.DataFrame(sample_data)

    print(f"\n✓ Data loaded from CSV (sample data)")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {list(df.columns)}")
    print(f"\nFirst 3 rows:")
    print(df.head(3).to_string(index=False))

    # =========================================================================
    # Step 4: Add Additional Validation Rules
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 4: Add Additional Validation Rules")
    print("=" * 80)

    # Add range check for age (must be between 18 and 100)
    age_rule = ValidationRule('age')
    age_rule.add_check(RangeCheck(min_value=18, max_value=100))
    validator.add_rule(age_rule)
    print(f"\n✓ Added range check for 'age' column (18-100)")

    # Add range check for account_balance (must be >= 1000)
    balance_rule = ValidationRule('account_balance')
    balance_rule.add_check(ComparisonCheck(
        operator=ComparisonOperator.GREATER_THAN_OR_EQUAL,
        target_value=1000.00
    ))
    validator.add_rule(balance_rule)
    print(f"✓ Added comparison check for 'account_balance' column (>= 1000)")

    # Add valid values check for status
    from wxdi.dq_validator import ValidValuesCheck
    status_rule = ValidationRule('status')
    status_rule.add_check(ValidValuesCheck(
        valid_values=['active', 'inactive', 'suspended'],
        case_sensitive=False
    ))
    validator.add_rule(status_rule)
    print(f"✓ Added valid values check for 'status' column")

    print(f"\n✓ Total validation rules: {len(validator.rules)}")
    for rule in validator.rules:
        print(f"  - {rule.column_name}: {len(rule.checks)} check(s)")

    # =========================================================================
    # Step 5: Run Validation on DataFrame
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 5: Run Validation")
    print("=" * 80)

    # Create Pandas validator
    pandas_validator = PandasValidator(validator, chunk_size=1000)
    print(f"\n✓ Pandas Validator created (chunk_size=1000)")

    # Get summary statistics
    print(f"\nRunning validation...")
    summary = pandas_validator.get_summary_statistics(df)

    print(f"\n✓ Validation completed!")

    # =========================================================================
    # Step 6: Print and Analyze Results
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 6: Validation Results")
    print("=" * 80)

    # Print summary statistics
    print(f"\n{'SUMMARY STATISTICS':^80}")
    print("-" * 80)
    print(f"Total Rows:        {summary['total_rows']:>10}")
    print(f"Valid Rows:        {summary['valid_rows']:>10}")
    print(f"Invalid Rows:      {summary['invalid_rows']:>10}")
    print(f"Pass Rate:         {summary['pass_rate']:>9.2f}%")
    print("-" * 80)
    print(f"Total Checks:      {summary['total_checks']:>10}")
    print(f"Passed Checks:     {summary['passed_checks']:>10}")
    print(f"Failed Checks:     {summary['failed_checks']:>10}")
    print("-" * 80)

    # Add validation column to DataFrame
    df_validated = pandas_validator.add_validation_column(df)

    # Print detailed results for each row
    print(f"\n{'DETAILED VALIDATION RESULTS':^80}")
    print("-" * 80)

    for idx, row in df_validated.iterrows():
        validation = row['dq_validation_result']
        is_valid = bool(validation['is_valid'])
        status_icon = "✓" if is_valid else "✗"
        status_text = "PASS" if is_valid else "FAIL"
        row_num = idx + 1 if isinstance(idx, int) else idx  # type: ignore[operator]

        print(f"\nRow {row_num}: {status_icon} {status_text}")
        print(f"  Customer: {row['name']} (ID: {row['customer_id']})")
        print(f"  Age: {row['age']}, Balance: ${row['account_balance']:.2f}, Status: {row['status']}")
        print(f"  Validation Score: {validation['score']} ({validation['pass_rate']:.1f}%)")

        if not is_valid:
            print(f"  Errors: {validation['error_count']}")
            errors = validation['errors']
            if errors is not None and len(errors) > 0:
                for error in validation['errors'][:3]:  # Show first 3 errors
                    print(f"    - {error['column']}: {error['message']}")

    # Get and display invalid rows
    print(f"\n{'INVALID ROWS DETAILS':^80}")
    print("-" * 80)

    invalid_df = pandas_validator.get_invalid_rows(df)

    if len(invalid_df) > 0:
        print(f"\nFound {len(invalid_df)} invalid row(s):\n")

        for idx, row in invalid_df.iterrows():
            validation = row['dq_validation_result']
            row_num = idx + 1 if isinstance(idx, int) else idx  # type: ignore[operator]
            print(f"Row {row_num}:")
            print(f"  Customer ID: {row['customer_id']}")
            print(f"  Name: {row['name']}")
            print(f"  Age: {row['age']}")
            print(f"  Balance: ${row['account_balance']:.2f}")
            print(f"  Status: {row['status']}")
            print(f"  Validation Score: {validation['score']} ({validation['pass_rate']:.1f}%)")
            print(f"  Failed Checks: {validation['error_count']}")

            errors = validation['errors']
            if errors is not None and len(errors) > 0:
                print(f"  Errors:")
                for error in validation['errors']:
                    print(f"    - Column '{error['column']}': {error['message']}")
                    if error.get('value') is not None:
                        print(f"      Value: {error['value']}")
                    if error.get('expected') is not None:
                        print(f"      Expected: {error['expected']}")
            print()
    else:
        print("\n✓ All rows passed validation!")

    # Expand validation columns for analysis
    print(f"\n{'EXPANDED VALIDATION COLUMNS':^80}")
    print("-" * 80)

    df_expanded = pandas_validator.expand_validation_column(df_validated)

    # Show key validation columns
    validation_cols = ['customer_id', 'name', 'dq_is_valid', 'dq_score', 'dq_pass_rate', 'dq_error_count']
    print(f"\nValidation Summary by Row:")
    print(df_expanded[validation_cols].to_string(index=False))

    # Save results to files
    print(f"\n{'SAVING RESULTS':^80}")
    print("-" * 80)

    # Save invalid rows
    if len(invalid_df) > 0:
        invalid_df.to_csv('invalid_customers.csv', index=False)
        print(f"\n✓ Saved {len(invalid_df)} invalid rows to: invalid_customers.csv")

    # Save full validation results
    df_expanded.to_csv('validation_results.csv', index=False)
    print(f"✓ Saved full validation results to: validation_results.csv")

    # Save summary report
    with open('validation_summary.txt', 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("DATA QUALITY VALIDATION SUMMARY REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Asset: {metadata.table_name}\n")
        f.write(f"Total Rows: {summary['total_rows']}\n")
        f.write(f"Valid Rows: {summary['valid_rows']}\n")
        f.write(f"Invalid Rows: {summary['invalid_rows']}\n")
        f.write(f"Pass Rate: {summary['pass_rate']:.2f}%\n\n")
        f.write(f"Total Checks: {summary['total_checks']}\n")
        f.write(f"Passed Checks: {summary['passed_checks']}\n")
        f.write(f"Failed Checks: {summary['failed_checks']}\n\n")
        f.write("Validation Rules Applied:\n")
        for rule in validator.rules:
            f.write(f"  - {rule.column_name}: {len(rule.checks)} check(s)\n")

    print(f"✓ Saved summary report to: validation_summary.txt")

    # =========================================================================
    # Completion
    # =========================================================================
    print("\n" + "=" * 80)
    print("END-TO-END VALIDATION COMPLETE!")
    print("=" * 80)

    print(f"\nKey Takeaways:")
    print(f"  • Authenticated with IBM Cloud using API key")
    print(f"  • Loaded asset metadata from CAMS (or created sample)")
    print(f"  • Loaded {len(df)} rows from CSV file")
    print(f"  • Applied {len(validator.rules)} validation rules")
    print(f"  • Validated data with {summary['pass_rate']:.1f}% pass rate")
    print(f"  • Identified {summary['invalid_rows']} invalid row(s)")
    print(f"  • Saved results to CSV files for further analysis")

    print(f"\nNext Steps:")
    print(f"  1. Review invalid_customers.csv for data quality issues")
    print(f"  2. Analyze validation_results.csv for detailed insights")
    print(f"  3. Update source data or adjust validation rules as needed")
    print(f"  4. Re-run validation to verify improvements")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    try:
        main()
    except ImportError as e:
        print(f"Error: {e}")
        print("\nTo run this example, install required dependencies:")
        print("  pip install pandas")
        print("Or install with all dependencies:")
        print("  pip install wxdi[pandas]")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

# Made with Bob
