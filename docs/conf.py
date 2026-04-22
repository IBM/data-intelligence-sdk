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

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
from pathlib import Path

# Add the project root to the path so we can import the package
cwd = os.getcwd()
project_root = os.path.dirname(cwd)
sys.path.insert(0, str(Path(project_root).resolve()))
sys.path.insert(0, os.path.join(project_root, 'src'))

project = "IBM watsonx.data intelligence SDK"
copyright = "2026, IBM"
author = "IBM"

# The version info for the project you're documenting, acts as replacement
# for |version| and |release|, also used in various other places throughout
# the built documents.
#
# The short X.Y version.
version = "2.0.0"
# The full version, including alpha/beta/rc tags.
release = "2.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # napoleon extension must be loaded prior than `sphinx_autodoc_typehints`
    "sphinx_autodoc_typehints",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_favicon",
    # "sphinxcontrib.autodoc_pydantic",  # Optional - for enhanced Pydantic model documentation
    "sphinx.ext.githubpages",  # auto-generates a .nojekyll file to prevent github pages from overriding our CSS
]

# Mock imports for external dependencies that aren't needed for documentation
autodoc_mock_imports = [
    "ibm_cloud_sdk_core",
    "ibm_watson",
    "requests",
    "pandas",
    "pyspark",
    "numpy",
    "pydantic",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_logo = "_static/images/ibm_data_intelligence_logo.svg"
html_css_files = ["css/theme.css"]

show_navbar_depth = 2

# Theme options are theme-specific and customize the look and feel of a
# theme further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "use_fullscreen_button": False,
    "toc_title": "Section Contents",
    "use_download_button": False,
    "logo": {
        "text": f"IBM watsonx.data intelligence SDK for Python Version {version}",
    },
}

# -- sphinx_favicon configuration --------------------------------------------
# https://sphinx-favicon.readthedocs.io/en/stable/quickstart.html#quickstart

favicons = [
    "images/favicon.ico",
]

# -- sphinx.ext.autodoc configuration ----------------------------------------
autoclass_content = "both"  # make docs based on class docstring and __init__
autodoc_member_order = "bysource"  # keep the order as in source code
autodoc_typehints = "description"  # show type hints in description

# -- sphinx_autodoc_typehints configuration ----------------------------------
typehints_use_signature = True
typehints_defaults = "comma"

# -- sphinx.ext.intersphinx configuration ------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "pyspark": ("https://spark.apache.org/docs/latest/api/python/", None),
}

# -- sphinx_copybutton configuration -----------------------------------------
# forces copy button to ignore python prompts like `>>>` and `...`
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# -- sphinxcontrib.autodoc_pydantic configuration ----------------------------
# Commented out - extension is optional
# autodoc_pydantic_model_show_json = False
# autodoc_pydantic_model_show_config_summary = False
# autodoc_pydantic_model_show_validator_summary = False
# autodoc_pydantic_model_show_field_summary = False
# autodoc_pydantic_field_list_validators = False

# Made with Bob
