# Copyright 2026 IBM Corporation
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0);
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# See the LICENSE file in the project root for license information.

from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, field_serializer

from .constraint_model import DataQualityConstraint

class Metadata(BaseModel):
    """Base metadata model for artifacts"""

    @field_serializer('effective_start_date','created_at','modified_at', when_used='json-unless-none')
    def to_iso(self, dt: datetime):
        return dt.isoformat()

    artifact_type: str
    artifact_id: str
    version_id: str
    source_repository_id: str
    global_id: str
    is_target_draft: Optional[bool] = None
    effective_start_date: datetime
    created_by: str
    created_at: datetime
    modified_by: str
    modified_at: datetime
    revision: str
    state: str
    read_only: Optional[bool] = None
    draft_ancestor_id: Optional[str] = None
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    steward_ids: Optional[List[str]] = None
    steward_group_ids: Optional[List[str]] = None
    user_access: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "Metadata":
        """Create Metadata instance from dictionary"""
        return cls(**data)


class ExtendedAttributeGroups(BaseModel):
    """Extended attribute groups containing data quality constraints"""

    dq_constraints: List[DataQualityConstraint]

    @classmethod
    def from_dict(cls, data: Dict) -> "ExtendedAttributeGroups":
        """Create ExtendedAttributeGroups instance from dictionary"""
        return cls(
            dq_constraints=[
                DataQualityConstraint.from_dict(c) for c in data["dq_constraints"]
            ]
        )


class GlossaryTermEntity(BaseModel):
    """Main entity model for glossary term"""

    extended_attribute_groups: Optional[ExtendedAttributeGroups] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "GlossaryTermEntity":
        """Create GlossaryTermEntity instance from dictionary"""
        ext_attrs = data.get("extended_attribute_groups")

        return cls(
            extended_attribute_groups=(
                ExtendedAttributeGroups.from_dict(ext_attrs) if ext_attrs else None
            )
        )


class GlossaryTerm(BaseModel):
    """Root model for glossary term artifact"""

    metadata: Metadata
    entity: GlossaryTermEntity

    @classmethod
    def from_dict(cls, data: Dict) -> "GlossaryTerm":
        """Create GlossaryTerm instance from dictionary"""
        return cls(
            metadata=Metadata.from_dict(data["metadata"]),
            entity=GlossaryTermEntity.from_dict(data["entity"]),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "GlossaryTerm":
        """Create GlossaryTerm instance from JSON string"""
        import json

        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_dict(self) -> Dict:
        """Convert GlossaryTerm instance to dictionary"""
        return self.model_dump()

    def to_json(self, indent: Optional[int] = None) -> str:
        """Convert GlossaryTerm instance to JSON string"""
        return self.model_dump_json(indent=indent)


# ============================================================================
# USAGE EXAMPLES
# ============================================================================


def example_usage():
    """Demonstrates how to use the GlossaryTerm model classes"""
    import json

    # Sample JSON data
    sample_json = """{
  "metadata": {
    "artifact_type": "glossary_term",
    "artifact_id": "30d1b847-0aa9-4840-a182-dd157fe977a0",
    "version_id": "bdeef8cc-d9ab-4822-b3df-cef82b4de538_0",
    "source_repository_id": "1be893e3-d512-4fd8-b449-c953abeedb6c",
    "global_id": "1be893e3-d512-4fd8-b449-c953abeedb6c_30d1b847-0aa9-4840-a182-dd157fe977a0",
    "is_target_draft": false,
    "draft_ancestor_id": "90774b3c-16c6-4dcf-8c81-407d2e440baa",
    "effective_start_date": "2026-01-09T09:01:15.648Z",
    "created_by": "IBMid-0600012F5M",
    "created_at": "2026-01-09T09:01:15.648Z",
    "modified_by": "IBMid-0600012F5M",
    "modified_at": "2026-01-09T09:01:15.648Z",
    "revision": "0",
    "name": "mango",
    "state": "PUBLISHED",
    "tags": [],
    "steward_ids": [],
    "steward_group_ids": [],
    "read_only": false
  },
  "entity": {
    "parent_category": {
      "resources": [{
        "metadata": {
          "artifact_type": "relationship",
          "artifact_id": "97b2a3df-94cf-446c-9338-ba8c664bc09a",
          "version_id": "2728caaf-714b-4440-8558-b1d97077d34e_0",
          "source_repository_id": "1be893e3-d512-4fd8-b449-c953abeedb6c",
          "global_id": "1be893e3-d512-4fd8-b449-c953abeedb6c_97b2a3df-94cf-446c-9338-ba8c664bc09a",
          "is_target_draft": false,
          "effective_start_date": "2026-01-09T09:01:15.567Z",
          "created_by": "IBMid-0600012F5M",
          "created_at": "2026-01-09T09:01:15.567Z",
          "modified_by": "IBMid-0600012F5M",
          "modified_at": "2026-01-09T09:01:15.567Z",
          "revision": "0",
          "state": "PUBLISHED",
          "read_only": false,
          "user_access": true
        },
        "entity": {
          "child_href": "/v3/glossary_terms/30d1b847-0aa9-4840-a182-dd157fe977a0/versions?status=ACTIVE",
          "parent_enabled": true,
          "relationship_type": "parent_category",
          "source_type": "glossary_term",
          "target_type": "category",
          "reference_copy": false,
          "parent_href": "/v3/categories/e39ada11-8338-3704-90e3-681a71e7c839",
          "parent_name": "[uncategorized]",
          "parent_global_id": "1be893e3-d512-4fd8-b449-c953abeedb6c_e39ada11-8338-3704-90e3-681a71e7c839",
          "parent_version_id": "0b9f1be1-e076-3203-9d65-a8df62cbdbeb_0",
          "parent_id": "e39ada11-8338-3704-90e3-681a71e7c839",
          "parent_description": "This is the system default if a standard category is not assigned.",
          "child_id": "30d1b847-0aa9-4840-a182-dd157fe977a0",
          "child_global_id": "1be893e3-d512-4fd8-b449-c953abeedb6c_30d1b847-0aa9-4840-a182-dd157fe977a0",
          "child_name": "mango"
        }
      }],
      "offset": 0,
      "set_uri": false,
      "limit": 5,
      "count": 1
    },
    "custom_relationships": [],
    "abbreviations": [],
    "extended_attribute_groups": {
      "dq_constraints": [{
        "metadata": {"type": "data_type", "confirmed": false, "hidden": false},
        "origin": [],
        "check": [
          {"name": "data_type", "value": "STRING"},
          {"name": "length", "numeric_value": 80}
        ]
      }, {
        "metadata": {"type": "length", "confirmed": false, "hidden": false},
        "origin": [],
        "check": [
          {"name": "min", "numeric_value": 3},
          {"name": "max", "numeric_value": 80}
        ]
      }]
    },
    "state": "PUBLISHED",
    "default_locale_id": "en-US",
    "reference_copy": false,
    "steward_ids": [],
    "steward_group_ids": [],
    "custom_attributes": []
  }
}"""

    print("=" * 70)
    print("METHOD 1: Using Pydantic's built-in parsing (RECOMMENDED)")
    print("=" * 70)

    # Method 1: Direct parsing with Pydantic (simplest and recommended)
    data = json.loads(sample_json)
    glossary_term = GlossaryTerm(**data)

    print("✓ Model validated successfully!")
    print(f"  Term name: {glossary_term.metadata.name}")
    print(f"  State: {glossary_term.entity.state}")

    print("\n" + "=" * 70)
    print("METHOD 2: Using from_json() class method")
    print("=" * 70)

    # Method 2: Using the from_json class method
    glossary_term2 = GlossaryTerm.from_json(sample_json)
    print("✓ Model created from JSON string!")
    print(f"  Term name: {glossary_term2.metadata.name}")

    print("\n" + "=" * 70)
    print("METHOD 3: Using from_dict() class method")
    print("=" * 70)

    # Method 3: Using the from_dict class method
    data_dict = json.loads(sample_json)
    glossary_term3 = GlossaryTerm.from_dict(data_dict)
    print("✓ Model created from dictionary!")
    print(f"  Term name: {glossary_term3.metadata.name}")

    print("\n" + "=" * 70)
    print("CONVERTING BACK TO JSON/DICT")
    print("=" * 70)

    # Convert back to dictionary
    result_dict = glossary_term.to_dict()
    print(f"✓ Converted to dict with {len(result_dict)} top-level keys")

    # Convert back to JSON string
    result_json = glossary_term.to_json(indent=2)
    print(f"✓ Converted to JSON string ({len(result_json)} characters)")
    print("\nFirst 200 characters of JSON output:")
    print(result_json[:200] + "...")

    print("\n" + "=" * 70)
    print("ACCESSING NESTED DATA")
    print("=" * 70)

    # Access nested data
    print(f"Artifact ID: {glossary_term.metadata.artifact_id}")
    print(f"Created at: {glossary_term.metadata.created_at}")
    print(
        f"Number of DQ constraints: {len(glossary_term.entity.extended_attribute_groups.dq_constraints)}"
    )

    # Access first constraint
    first_constraint = glossary_term.entity.extended_attribute_groups.dq_constraints[0]
    print(f"First constraint type: {first_constraint.metadata.type}")
    print(f"First constraint checks: {len(first_constraint.check)}")


if __name__ == "__main__":
    example_usage()

# Made with Bob
