#!/usr/bin/env python
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
"""
Documentation build script for IBM watsonx.data intelligence SDK

This script builds the Sphinx documentation and performs validation checks.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a shell command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    
    print(result.stdout)
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    required_packages = [
        'sphinx',
        'sphinx_book_theme',
        'sphinx_autodoc_typehints',
        'sphinx_copybutton',
        'sphinx_favicon'
        # 'sphinxcontrib.autodoc_pydantic' - Optional
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_').replace('.', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print("Install with: pip install -r docs/requirements.txt")
        return False
    
    print("All dependencies installed [OK]")
    return True


def clean_build():
    """Clean previous build artifacts."""
    print("\nCleaning previous build...")
    build_dir = Path(__file__).parent / "_build"
    
    if build_dir.exists():
        import shutil
        shutil.rmtree(build_dir)
        print("Build directory cleaned [OK]")
    else:
        print("No previous build to clean")
    
    return True


def build_html():
    """Build HTML documentation."""
    print("\nBuilding HTML documentation...")
    
    docs_dir = Path(__file__).parent
    cmd = [
        'sphinx-build',
        '-b', 'html',
        '.',
        '_build/html'
    ]
    
    return run_command(cmd, cwd=docs_dir)


def check_build():
    """Check if build was successful."""
    print("\nChecking build output...")
    
    index_file = Path(__file__).parent / "_build" / "html" / "index.html"
    
    if index_file.exists():
        print(f"Documentation built successfully [OK]")
        print(f"Output: {index_file.parent}")
        return True
    else:
        print("Build failed: index.html not found")
        return False


def main():
    """Main build process."""
    print("=" * 60)
    print("IBM watsonx.data intelligence SDK - Documentation Build")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Clean previous build
    if not clean_build():
        sys.exit(1)
    
    # Build HTML documentation
    if not build_html():
        print("\n[FAILED] Build failed!")
        sys.exit(1)
    
    # Check build output
    if not check_build():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Documentation build completed successfully!")
    print("=" * 60)
    print(f"\nOpen: {Path(__file__).parent / '_build' / 'html' / 'index.html'}")


if __name__ == "__main__":
    main()

# Made with Bob
