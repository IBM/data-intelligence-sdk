#!/usr/bin/env python
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
Setup configuration for IBM watsonx.data intelligence SDK
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="data-intelligence-sdk",
    version="0.5.3",
    author="IBM",
    author_email="Data_Intelligence_SDK@wwpdl.vnet.ibm.com",
    description="A Python SDK for performing data quality validations on streaming data records and DataFrames",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IBM/data-intelligence-sdk",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.12.0",
        "requests>=2.28.0",
        "regex>=2023.0.0",
        # Pinned to exact version to avoid CRA bom-generate pip resolver conflict.
        # CRA sees ibm-cloud-sdk-core from both setup.py and requirements.txt and
        # fails with ResolutionImpossible when constraints differ (bare vs >=).
        "ibm-cloud-sdk-core==3.24.4",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.7.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
        "pandas": [
            "pandas>=1.3.0",
        ],
        "spark": [
            "pyspark>=3.0.0",
        ],
        "dataframes": [
            "pandas>=1.3.0",
            "pyspark>=3.0.0",
        ],
        "all": [
            "pandas>=1.3.0",
            "pyspark>=3.0.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.7.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            # Add CLI tools here if needed
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
