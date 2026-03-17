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

"""
Data Quality Dimensions - defines standard data quality dimensions and their descriptions.
"""

from enum import Enum


class DataQualityDimension(Enum):
    """
    Standard data quality dimensions with their definitions.
    
    Each dimension represents a key aspect of data quality that can be measured
    and validated to ensure data meets business requirements.
    """
    
    ACCURACY = "The degree to which data correctly describes the real world object or event being described."
    COMPLETENESS = "The proportion of data stored against the potential for 100%."
    CONFORMITY = "The degree to which data adheres to defined standards, formats, and permissible values."
    CONSISTENCY = "The absence of difference, when comparing two or more representations of a thing against a definition."
    COVERAGE = "The extent to which the expected dataset is represented, typically measured by record counts or population completeness."
    TIMELINESS = "The degree to which data represent reality from the required point in time."
    UNIQUENESS = "No entity instance (thing) will be recorded more than once based upon how that thing is identified."
    VALIDITY = "Data is valid if it conforms to the syntax of its definition."
    
    @property
    def description(self) -> str:
        """Returns the description of the dimension"""
        return self.value
    
    @classmethod
    def get_all_dimensions(cls) -> dict:
        """
        Returns all dimensions as a dictionary.
        
        Returns:
            dict: Dictionary mapping dimension names to their descriptions
        """
        return {dimension.name: dimension.value for dimension in cls}