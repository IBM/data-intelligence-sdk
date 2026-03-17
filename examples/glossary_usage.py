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
Example usage of GlossaryProvider for managing glossary terms.

This example demonstrates:

get_published_artifact_by_id(): Retrieve a published glossary term by artifact ID
   - Requires: artifact_id
   - Optional: options (dict with query parameters)
   - Returns: GlossaryTerm object

get_term_by_version_id(): Retrieve a specific version of a glossary term
   - Requires: artifact_id, version_id
   - Optional: options (dict with query parameters)
   - Returns: GlossaryTerm object
"""

from wxdi.dq_validator.provider import ProviderConfig, GlossaryProvider
from wxdi.common.auth import AuthConfig, EnvironmentType


def main():
    """Main function demonstrating GlossaryProvider usage."""
    PARAMETERS_HEADER = "\nParameters:"
    TERM_DETAILS_HEADER = "\nTerm Details:"

    print("=" * 70)
    print("GlossaryProvider - Usage Examples")
    print("=" * 70)
    
    # =========================================================================
    # Configuration Option 1: Using static auth token
    # =========================================================================
    print("\n" + "-" * 70)
    print("Configuration Option 1: Using Static Auth Token")
    print("-" * 70)
    
    config_with_token = ProviderConfig(
        url="https://your-instance.cloud.ibm.com",
        auth_token="Bearer your-auth-token-here"
    )
    
    print("\nConfiguration:")
    print(f"  URL: {config_with_token.url}")
    print(f"  Auth Token: {config_with_token.auth_token[:50]}...")
    
    # =========================================================================
    # Configuration Option 2: Using AuthConfig (recommended)
    # =========================================================================
    print("\n" + "-" * 70)
    print("Configuration Option 2: Using AuthConfig (Recommended)")
    print("-" * 70)
    
    # Example with IBM Cloud
    auth_config = AuthConfig(
        environment_type=EnvironmentType.IBM_CLOUD,
        api_key="your-api-key-here"
    )
    
    config_with_auth = ProviderConfig(
        url="https://your-instance.cloud.ibm.com",
        auth_config=auth_config
    )
    
    print("\nConfiguration:")
    print(f"  URL: {config_with_auth.url}")
    print(f"  Environment: {auth_config.environment_type.value}")
    print( "  Auth Provider: Configured")
    
    # For the examples below, we'll use config_with_token
    # In production, use config_with_auth for automatic token management
    config = config_with_token
    
    # Step 2: Create a GlossaryProvider instance
    glossary_provider = GlossaryProvider(config)
    print("\n✓ GlossaryProvider initialized")
    
    # Define IDs that will be used throughout the examples
    artifact_id = "your-artifact-id-here"  # Replace with your actual artifact ID
    version_id = "your-version-id-here"    # Replace with your actual version ID
    
    # =========================================================================
    # Example 1: Get published glossary term by artifact ID
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 1: Get Published Glossary Term by Artifact ID")
    print("=" * 70)
    
    try:
        print(PARAMETERS_HEADER)
        print(f"  artifact_id: {artifact_id}")
        
        term = glossary_provider.get_published_artifact_by_id(artifact_id)
        
        print( "\n✓ Successfully retrieved glossary term")
        
        print(TERM_DETAILS_HEADER)
        print(f"  Name: {term.metadata.name}")
        print(f"  Artifact Type: {term.metadata.artifact_type}")
        print(f"  State: {term.metadata.state}")
        print(f"  Artifact ID: {term.metadata.artifact_id}")
        print(f"  Version ID: {term.metadata.version_id}")
        print(f"  Created At: {term.metadata.created_at}")
        print(f"  Modified At: {term.metadata.modified_at}")
        
        if term.metadata.tags:
            print(f"  Tags: {', '.join(term.metadata.tags)}")
        
        # Display entity information if available
        if hasattr(term.entity, 'extended_attribute_groups') and term.entity.extended_attribute_groups:
            dq_constraints = term.entity.extended_attribute_groups.dq_constraints
            print(f"  Data Quality Constraints: {len(dq_constraints)}")
        
    except ValueError as e:
        print(f"\n✗ Error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
    
    # =========================================================================
    # Example 2: Get published term with additional options
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 2: Get Published Term with Additional Options")
    print("=" * 70)
    
    try:
        print(PARAMETERS_HEADER)
        print(f"  artifact_id: {artifact_id}")
        
        # Options can include query parameters like 'include', 'limit', etc.
        options = {
            "include": "relationships"
        }
        print(f"  options: {options}")
        
        term = glossary_provider.get_published_artifact_by_id(
            artifact_id,
            options=options
        )
        
        print( "\n✓ Successfully retrieved glossary term with options")
        
        print(TERM_DETAILS_HEADER)
        print(f"  Name: {term.metadata.name}")
        print(f"  State: {term.metadata.state}")
        print(f"  Revision: {term.metadata.revision}")
        
    except ValueError as e:
        print(f"\n✗ Error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
    
    # =========================================================================
    # Example 3: Get specific version of a glossary term
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 3: Get Specific Version of a Glossary Term")
    print("=" * 70)
    
    try:
        print(PARAMETERS_HEADER)
        print(f"  artifact_id: {artifact_id}")
        print(f"  version_id: {version_id}")
        
        term = glossary_provider.get_term_by_version_id(
            artifact_id,
            version_id
        )
        
        print( "\n✓ Successfully retrieved glossary term version")
        
        print(TERM_DETAILS_HEADER)
        print(f"  Name: {term.metadata.name}")
        print(f"  Version ID: {term.metadata.version_id}")
        print(f"  State: {term.metadata.state}")
        print(f"  Effective Start Date: {term.metadata.effective_start_date}")
        print(f"  Created By: {term.metadata.created_by}")
        print(f"  Modified By: {term.metadata.modified_by}")
        
        if term.metadata.draft_ancestor_id:
            print(f"  Draft Ancestor ID: {term.metadata.draft_ancestor_id}")
        
    except ValueError as e:
        print(f"\n✗ Error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
    
    # =========================================================================
    # Example 4: Get term version with options
    # =========================================================================
    print("\n" + "=" * 70)
    print("Example 4: Get Term Version with Options")
    print("=" * 70)
    
    try:
        print(PARAMETERS_HEADER)
        print(f"  artifact_id: {artifact_id}")
        print(f"  version_id: {version_id}")
        
        options = {
            "include": "all"
        }
        print(f"  options: {options}")
        
        term = glossary_provider.get_term_by_version_id(
            artifact_id,
            version_id,
            options=options
        )
        
        print( "\n✓ Successfully retrieved glossary term version with options")
        
        print(TERM_DETAILS_HEADER)
        print(f"  Name: {term.metadata.name}")
        print(f"  Version ID: {term.metadata.version_id}")
        print(f"  State: {term.metadata.state}")
        print(f"  Global ID: {term.metadata.global_id}")
        print(f"  Source Repository ID: {term.metadata.source_repository_id}")
        
        # Display steward information if available
        if term.metadata.steward_ids:
            print(f"  Steward IDs: {', '.join(term.metadata.steward_ids)}")
        if term.metadata.steward_group_ids:
            print(f"  Steward Group IDs: {', '.join(term.metadata.steward_group_ids)}")
        
    except ValueError as e:
        print(f"\n✗ Error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
    
    print("\n" + "=" * 70)
    print("Examples Complete!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  1. Use AuthConfig for automatic token management")
    print("  2. GlossaryProvider supports multiple authentication methods")
    print("  3. Options parameter allows flexible query customization")
    print("  4. Version-specific retrieval enables historical term access")
    print("  5. Term metadata includes name, state, timestamps, and stewards")
    print("  6. Entity may contain data quality constraints")
    print("=" * 70)


if __name__ == "__main__":
    main()

# Made with Bob
