#!/usr/bin/env bash
# File: build.sh
# Modern replacement for ci/scripts/build.py

set -euo pipefail

echo "🏗️  Building package..."

# Clean up previous builds
echo "🧹 Cleaning up previous builds..."
rm -rf build/ dist/ *.egg-info/

# Copy required files to package directory
echo "📁 Copying required files..."
cp .VERSION azureenergylabelercli/
cp LICENSE azureenergylabelercli/
cp AUTHORS.rst azureenergylabelercli/
cp CONTRIBUTING.rst azureenergylabelercli/
cp HISTORY.rst azureenergylabelercli/
cp README.rst azureenergylabelercli/

# Build the package
echo "📦 Building distribution packages..."
python -m build

# Check the built package
echo "🔍 Checking built package..."
python -m twine check dist/*

# Clean up copied files
echo "🧹 Cleaning up copied files..."
rm -f azureenergylabelercli/.VERSION
rm -f azureenergylabelercli/LICENSE
rm -f azureenergylabelercli/AUTHORS.rst
rm -f azureenergylabelercli/CONTRIBUTING.rst
rm -f azureenergylabelercli/HISTORY.rst
rm -f azureenergylabelercli/README.rst

echo "✅ Build completed successfully!"
