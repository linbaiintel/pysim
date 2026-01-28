#!/bin/bash
# Run unit tests
#
# Usage:
#   ./scripts/run_unit_tests.sh              # Run all unit tests
#   ./scripts/run_unit_tests.sh -v          # Run with verbose output
#   ./scripts/run_unit_tests.sh -k pattern  # Run tests matching pattern

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Activate virtual environment
if [ -f "pysim-venv/bin/activate" ]; then
    source pysim-venv/bin/activate
else
    echo "Error: Virtual environment not found at pysim-venv/"
    exit 1
fi

# Check if test file exists
if [ ! -f "tests/test_all.py" ]; then
    echo "Error: Unit tests not found at tests/test_all.py"
    exit 1
fi

echo "=========================================="
echo "Running Unit Tests"
echo "=========================================="
echo ""

# Check if pytest is available
if command -v pytest &> /dev/null; then
    # Use pytest if available
    pytest tests/test_all.py "$@"
else
    # Fall back to direct Python execution
    python tests/test_all.py
fi

echo ""
echo "=========================================="
echo "Unit tests complete!"
echo "=========================================="
