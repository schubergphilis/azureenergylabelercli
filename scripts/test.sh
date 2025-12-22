#!/usr/bin/env bash
# File: test.sh
# Modern replacement for ci/scripts/test.py

set -euo pipefail

echo "🧪 Running tests..."

# Create test output directory
mkdir -p test-output

# Run tests with coverage
echo "🏃‍♂️ Running pytest with coverage..."
python -m pytest tests/ \
    --cov=azureenergylabelercli \
    --cov-report=html:test-output/coverage \
    --cov-report=term-missing \
    --cov-report=xml \
    --junit-xml=test-output/junit.xml \
    --html=test-output/pytest-report.html \
    --self-contained-html

echo "✅ Tests completed successfully!"
echo "📊 Coverage report: test-output/coverage/index.html"
echo "📋 Test report: test-output/pytest-report.html"
