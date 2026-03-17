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
# IBM watsonx.data intelligence SDK Documentation

This directory contains the Sphinx documentation for the IBM watsonx.data intelligence SDK.

## Documentation Structure

```
docs/
├── conf.py                      # Sphinx configuration
├── index.rst                    # Main landing page
├── requirements.txt             # Documentation dependencies
├── build_docs.py               # Build script
├── README.md                   # This file
│
├── _static/                    # Static assets
│   ├── css/
│   │   └── theme.css          # Custom IBM styling
│   └── images/
│       ├── favicon.ico        # Browser icon
│       └── ibm_data_intelligence_logo.svg  # Logo
│
├── chapters/                   # Documentation chapters
│   ├── 01_welcome/            # Welcome and installation
│   ├── 02_overview/           # Features and release notes
│   ├── 03_common_modules/     # Shared authentication
│   ├── 04_dq_validator/       # DQ Validator module
│   └── 05_future_modules/     # Future module guidelines
│
└── api/                        # API reference
    ├── common/                # Common modules API
    └── dq_validator/          # DQ Validator API
```

## Building Documentation Locally

### Prerequisites

1. Install Python 3.8 or higher
2. Install the SDK:
   ```bash
   pip install -e .
   ```
3. Install documentation dependencies:
   ```bash
   pip install -r docs/requirements.txt
   ```

### Build Methods

#### Method 1: Using the build script (Recommended)

```bash
python docs/build_docs.py
```

This script will:
- Check dependencies
- Clean previous builds
- Build HTML documentation
- Validate the output

#### Method 2: Using Sphinx directly

```bash
cd docs
sphinx-build -b html . _build/html
```

#### Method 3: Using Make (if available)

```bash
cd docs
make html
```

### Viewing the Documentation

After building, open `docs/_build/html/index.html` in your web browser.

## Documentation Deployment

### GitHub Pages

Documentation is automatically built and deployed to GitHub Pages when changes are pushed to the main branch.

The workflow is defined in `.github/workflows/docs.yml`.

### Manual Deployment

To manually deploy to GitHub Pages:

1. Build the documentation locally
2. Push the `_build/html` directory to the `gh-pages` branch
3. Enable GitHub Pages in repository settings

## Adding New Content

### Adding a New Chapter

1. Create a new directory: `docs/chapters/0X_chapter_name/`
2. Create `index.rst` in the new directory
3. Add content files (`.rst`)
4. Update `docs/index.rst` to include the new chapter in the toctree

### Adding API Documentation

1. Create RST file in `docs/api/module_name/`
2. Use autodoc directives to generate API docs from docstrings
3. Update `docs/api/index.rst` to include the new module

Example:

```rst
.. autoclass:: module.ClassName
   :members:
   :undoc-members:
   :show-inheritance:
```

### Adding a New Module (for Teams)

When adding a new SDK module:

1. Create module documentation:
   ```
   docs/chapters/0X_module_name/
   ├── index.rst
   ├── core_concepts.rst
   ├── usage.rst
   └── examples.rst
   ```

2. Create API reference:
   ```
   docs/api/module_name/
   ├── index.rst
   └── classes.rst
   ```

3. Update main index.rst to include your module
4. Follow the same structure as existing modules

## Customization

### Styling

Custom CSS is in `docs/_static/css/theme.css`. Modify this file to change:
- Colors (IBM blue theme)
- Fonts
- Layout
- Component styling

### Logo and Branding

Replace these files with your branding:
- `docs/_static/images/ibm_data_intelligence_logo.svg` - Main logo
- `docs/_static/images/favicon.ico` - Browser icon

### Configuration

Edit `docs/conf.py` to change:
- Project name and version
- Theme options
- Extensions
- Build behavior

## Writing Guidelines

### reStructuredText (RST) Basics

- **Headers**: Use `=`, `-`, `~`, `^` for different levels
- **Links**: `` :ref:`label` `` for internal links
- **Code blocks**: Use `.. code-block:: python`
- **Lists**: Use `*` or `1.` for lists
- **Emphasis**: `*italic*` and `**bold**`

### Best Practices

1. **Clear Structure**: Organize content logically
2. **Code Examples**: Include working code examples
3. **Cross-References**: Link related sections
4. **API Documentation**: Keep docstrings up-to-date
5. **Consistency**: Follow existing patterns

### Example RST File

```rst
.. _my_section:

My Section Title
================

Introduction paragraph.

Subsection
----------

Content with a code example:

.. code-block:: python

    from module import Class
    
    obj = Class()
    result = obj.method()

See :ref:`other_section` for more information.
```

## Troubleshooting

### Build Errors

**"Module not found"**
- Ensure the SDK is installed: `pip install -e .`
- Check that all dependencies are installed

**"WARNING: document isn't included in any toctree"**
- Add the document to a toctree directive in a parent file

**"WARNING: undefined label"**
- Check that the referenced label exists
- Ensure the label is defined with `.. _label_name:`

### Missing Dependencies

Install all required packages:
```bash
pip install -r docs/requirements.txt
```

### Clean Build

If you encounter persistent issues:
```bash
rm -rf docs/_build
python docs/build_docs.py
```

## Contributing

When contributing documentation:

1. Follow the existing structure and style
2. Test your changes locally before committing
3. Ensure all links work
4. Check for spelling and grammar
5. Update the table of contents if needed

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Sphinx Book Theme](https://sphinx-book-theme.readthedocs.io/)
- [IBM Design Language](https://www.ibm.com/design/language/)

## Support

For documentation issues or questions:
- Open an issue on GitHub
- Contact: data-intelligence-sdk@ibm.com