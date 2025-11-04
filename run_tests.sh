#!/bin/bash
# Script to run all tests and code quality checks

echo "🧪 Running tests..."
pytest

echo ""
echo "📊 Generating coverage report..."
pytest --cov=. --cov-report=term-missing

echo ""
echo "🎨 Checking code formatting..."
black --check .

echo ""
echo "🔍 Running linter..."
flake8 .

echo ""
echo "✅ All checks complete!"

