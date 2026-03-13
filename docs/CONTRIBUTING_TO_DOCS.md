<!--
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
-->
# Contributing to Documentation

This guide explains how module owners should update documentation when adding new modules or features to the IBM watsonx.data intelligence SDK.

## Documentation Update Responsibility

**Module owners are responsible for:**
1. Writing docstrings in their Python code (auto-generates API docs)
2. Creating user guide documentation for their module
3. Adding their module to the documentation structure
4. Providing examples and usage guides

## What Updates Automatically vs. Manually

### ✅ Automatic Updates (via Sphinx autodoc)

These are **automatically generated** from your Python code docstrings:

- **API Reference documentation** - Classes, methods, parameters, return types
- **Type hints** - Automatically extracted and displayed
- **Method signatures** - Auto-generated from code

**What you need to do:**
- Write comprehensive docstrings in your Python code following Google/NumPy style
- Include parameter descriptions, return types, and examples in docstrings

**Example:**
```python
class MyNewModule:
    """
    Brief description of the module.
    
    This module provides functionality for...
    
    Args:
        config (Config): Configuration object
        timeout (int, optional): Timeout in seconds. Defaults to 30.
    
    Example:
        >>> module = MyNewModule(config)
        >>> result = module.process()
    """
    
    def process(self, data: List[str]) -> Dict[str, Any]:
        """
        Process the input data.
        
        Args:
            data: List of strings to process
            
        Returns:
            Dictionary containing processed results with keys:
            - 'status': Processing status
            - 'count': Number of items processed
            
        Raises:
            ValueError: If data is empty
        """
        pass
```

### 📝 Manual Updates Required

These require **manual documentation updates** by module owners:

1. **User Guides** - Conceptual documentation, tutorials, workflows
2. **Examples** - Practical usage examples and code samples
3. **Module Overview** - High-level description and use cases
4. **Integration Guides** - How to integrate with other modules
5. **Navigation Structure** - Adding your module to the docs menu

## Adding a New Module to Documentation

### Step 1: Create Module Documentation Directory

```bash
# Create directory for your module
mkdir -p docs/chapters/06_your_module_name/

# Create documentation files
touch docs/chapters/06_your_module_name/index.rst
touch docs/chapters/06_your_module_name/core_concepts.rst
touch docs/chapters/06_your_module_name/usage_guide.rst
touch docs/chapters/06_your_module_name/examples.rst
```

### Step 2: Create Module Index File

**File:** `docs/chapters/06_your_module_name/index.rst`

```rst
.. _your_module_name:

Your Module Name
================

Brief description of what your module does.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   core_concepts
   usage_guide
   examples

Overview
--------

Detailed overview of your module, its purpose, and key features.

Key Features
------------

* Feature 1
* Feature 2
* Feature 3

Quick Start
-----------

.. code-block:: python

    from your_module import YourClass
    
    # Quick example
    obj = YourClass()
    result = obj.do_something()
```

### Step 3: Create API Reference Files

**File:** `docs/api/your_module/index.rst`

```rst
.. _api_your_module:

Your Module API
===============

API reference for Your Module.

.. toctree::
   :maxdepth: 2

   core
   utilities

Core Classes
------------

.. currentmodule:: your_module

.. autoclass:: your_module.core.YourMainClass
   :members:
   :undoc-members:
   :show-inheritance:
```

### Step 4: Update Main Documentation Index

**File:** `docs/index.rst`

Add your module to the main table of contents:

```rst
.. toctree::
   :maxdepth: 2
   :caption: Documentation:

   chapters/01_welcome/index
   chapters/02_overview/index
   chapters/03_common_modules/index
   chapters/04_dq_validator/index
   chapters/05_future_modules/index
   chapters/06_your_module_name/index  # <-- Add this line
```

### Step 5: Update API Reference Index

**File:** `docs/api/index.rst`

Add your module to the API reference:

```rst
.. toctree::
   :maxdepth: 2

   common/index
   dq_validator/index
   your_module/index  # <-- Add this line
```

### Step 6: Write User Guide Content

Create comprehensive guides in your module's chapter directory:

- **core_concepts.rst** - Explain key concepts and architecture
- **usage_guide.rst** - Step-by-step usage instructions
- **examples.rst** - Practical code examples

### Step 7: Test Documentation Build

```bash
# Build documentation locally
python docs/build_docs.py

# Or use Make
cd docs && make html

# View in browser
open docs/_build/html/index.html
```

### Step 8: Submit Pull Request

1. Commit your documentation changes
2. Push to your branch
3. Create pull request with description of documentation updates
4. Documentation will auto-deploy after merge

## Documentation Standards

### Docstring Style

Use **Google-style docstrings**:

```python
def function(arg1: str, arg2: int = 0) -> bool:
    """
    Brief description.
    
    Longer description with more details about what the function does.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2. Defaults to 0.
    
    Returns:
        True if successful, False otherwise.
    
    Raises:
        ValueError: If arg1 is empty
        TypeError: If arg2 is not an integer
    
    Example:
        >>> result = function("test", 5)
        >>> print(result)
        True
    """
    pass
```

### RST File Structure

```rst
.. _unique_reference_label:

Page Title
==========

Introduction paragraph.

Section Heading
---------------

Content for this section.

Subsection Heading
~~~~~~~~~~~~~~~~~~

Content for subsection.

Code Example
------------

.. code-block:: python

    # Python code example
    from module import Class
    
    obj = Class()
    result = obj.method()

.. note::
   Important note for users.

.. warning::
   Warning about potential issues.
```

## Continuous Integration

### Automatic Deployment

Documentation is **automatically built and deployed** when:

1. Code is pushed to `main` branch
2. Pull request is merged
3. GitHub Actions workflow runs
4. Documentation is deployed to GitHub Pages

**Workflow:** `.github/workflows/docs.yml`

### Build Checks

The CI pipeline will:
- ✅ Check for Sphinx build errors
- ✅ Validate RST syntax
- ✅ Generate API documentation from docstrings
- ✅ Deploy to GitHub Pages

## Best Practices

### 1. Write Docstrings First
- Write docstrings as you code
- API docs are auto-generated from docstrings
- Saves time and ensures accuracy

### 2. Provide Examples
- Include code examples in docstrings
- Create separate example files in `examples/`
- Reference examples in user guides

### 3. Keep Documentation Updated
- Update docs when changing APIs
- Document breaking changes
- Update version numbers

### 4. Use Cross-References
```rst
See :ref:`authentication` for details.
See :class:`dq_validator.Validator` for API reference.
See :meth:`Validator.validate` for method details.
```

### 5. Test Locally Before Committing
```bash
# Always test build locally
python docs/build_docs.py

# Check for warnings
# Fix any broken links or references
```

## Module Documentation Checklist

When adding a new module, ensure you have:

- [ ] Written comprehensive docstrings in Python code
- [ ] Created module chapter directory (`docs/chapters/XX_module/`)
- [ ] Created module index file with overview
- [ ] Written core concepts guide
- [ ] Written usage guide with examples
- [ ] Created API reference files (`docs/api/module/`)
- [ ] Added module to main `docs/index.rst`
- [ ] Added module to `docs/api/index.rst`
- [ ] Provided code examples in `examples/`
- [ ] Tested documentation build locally
- [ ] Submitted pull request with documentation

## Getting Help

- **Sphinx Documentation:** https://www.sphinx-doc.org/
- **RST Primer:** https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
- **Google Style Docstrings:** https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
- **Contact:** Reach out to the documentation team for assistance

## Example: Adding a New Module

See `docs/chapters/05_future_modules/index.rst` for a complete template and guidelines for adding new modules to the SDK.