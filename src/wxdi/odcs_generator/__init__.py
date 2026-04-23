# coding: utf-8
# Copyright 2026 IBM Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""ODCS Generator - Generate ODCS YAML files from Collibra and Informatica assets"""

from .generate_odcs_from_collibra import (
    CollibraClient,
    ODCSGenerator,
    parse_arguments as collibra_parse_arguments,
    validate_arguments as collibra_validate_arguments,
    determine_output_file as collibra_determine_output_file,
    write_yaml_file as collibra_write_yaml_file,
    main as collibra_main
)

from .generate_odcs_from_informatica import (
    InformaticaClient,
    parse_arguments as informatica_parse_arguments,
    validate_arguments as informatica_validate_arguments,
    determine_output_file as informatica_determine_output_file,
    write_yaml_file as informatica_write_yaml_file,
    main as informatica_main
)

__all__ = [
    # Collibra exports
    'CollibraClient',
    'ODCSGenerator',
    'collibra_parse_arguments',
    'collibra_validate_arguments',
    'collibra_determine_output_file',
    'collibra_write_yaml_file',
    'collibra_main',
    # Informatica exports
    'InformaticaClient',
    'informatica_parse_arguments',
    'informatica_validate_arguments',
    'informatica_determine_output_file',
    'informatica_write_yaml_file',
    'informatica_main'
]

__version__ = '1.0.0'
