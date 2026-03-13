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
Example usage of DimensionsProvider for managing data quality dimensions.

This example demonstrates:

search_dimension(): Search for a data quality dimension ID by name
   - Requires: name (dimension name, case-insensitive)
   - Returns: The dimension ID
   - Common dimension names: "Completeness", "Accuracy", "Consistency", "Validity", "Uniqueness", "Timeliness"
"""

from wxdi.dq_validator.provider import ProviderConfig, DimensionsProvider


def main():
    """Main function demonstrating DimensionsProvider usage."""
    
    print("=" * 70)
    print("DimensionsProvider - Usage Examples")
    print("=" * 70)
    
    # Step 1: Configure the provider with your instance URL and authentication token
    config = ProviderConfig(
        url="https://your-instance.cloud.ibm.com",
        auth_token="Bearer your-auth-token-here"
    )
    
    print("\nConfiguration:")
    print(f"  URL: {config.url}")
    print(f"  Auth Token: {config.auth_token[:50]}...")
    
    # Step 2: Create a DimensionsProvider instance
    dimension_provider = DimensionsProvider(config)
    print("\n✓ DimensionsProvider initialized")
    
    # =========================================================================
    # Example 1: Get Completeness dimension
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 1: Get Completeness Dimension")
    print("=" * 70)
    
    try:
        dimension_name = "Completeness"
        dimension_id = dimension_provider.search_dimension(dimension_name)
        
        print(f"\n✓ Successfully retrieved dimension: {dimension_name}")
        print(f"  Dimension ID: {dimension_id}")
        
    except ValueError as e:
        print(f"\n✗ Error getting dimension: {e}")
    
    # =========================================================================
    # Example 2: Get Accuracy dimension
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 2: Get Accuracy Dimension")
    print("=" * 70)
    
    try:
        dimension_name = "Accuracy"
        dimension_id = dimension_provider.search_dimension(dimension_name)
        
        print(f"\n✓ Successfully retrieved dimension: {dimension_name}")
        print(f"  Dimension ID: {dimension_id}")
        
    except ValueError as e:
        print(f"\n✗ Error getting dimension: {e}")
    
    # =========================================================================
    # Example 3: Get Consistency dimension
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 3: Get Consistency Dimension")
    print("=" * 70)
    
    try:
        dimension_name = "Consistency"
        dimension_id = dimension_provider.search_dimension(dimension_name)
        
        print(f"\n✓ Successfully retrieved dimension: {dimension_name}")
        print(f"  Dimension ID: {dimension_id}")
        
    except ValueError as e:
        print(f"\n✗ Error getting dimension: {e}")
    
    # =========================================================================
    # Example 4: Test case-insensitive matching
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 4: Case-Insensitive Matching (lowercase 'completeness')")
    print("=" * 70)
    
    try:
        dimension_name = "completeness"  # lowercase
        dimension_id = dimension_provider.search_dimension(dimension_name)
        
        print(f"\n✓ Successfully retrieved dimension with lowercase name")
        print(f"  Dimension Name: {dimension_name}")
        print(f"  Dimension ID: {dimension_id}")
        
    except ValueError as e:
        print(f"\n✗ Error getting dimension: {e}")
    
    # =========================================================================
    # Example 5: Get multiple dimensions in a loop
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 5: Get Multiple Dimensions")
    print("=" * 70)
    
    dimension_names = ["Completeness", "Accuracy", "Consistency"]
    
    print("\nRetrieving multiple dimensions:")
    for idx, dim_name in enumerate(dimension_names, 1):
        try:
            dim_id = dimension_provider.search_dimension(dim_name)
            print(f"{idx}. ✓ {dim_name}: {dim_id}")
        except ValueError as e:
            print(f"{idx}. ✗ {dim_name}: Failed - {e}")
    
    # =========================================================================
    # Example 6: Try to get a non-existent dimension (error handling)
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 6: Error Handling - Non-existent Dimension")
    print("=" * 70)
    
    try:
        dimension_name = "NonExistentDimension"
        dimension_id = dimension_provider.search_dimension(dimension_name)
        
        print(f"\n✓ Retrieved dimension: {dimension_name}")
        print(f"  Dimension ID: {dimension_id}")
        
    except ValueError as e:
        print(f"\n✗ Expected error for non-existent dimension:")
        print(f"  Error: {e}")
    
    print("\n" + "=" * 70)
    print("Examples Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()