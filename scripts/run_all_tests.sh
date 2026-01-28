#!/bin/bash
# Run all tests (both unit and functional)
#
# Usage:
#   ./scripts/run_all_tests.sh

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=========================================="
echo "RUNNING ALL TESTS"
echo "=========================================="
echo ""

# Run unit tests
echo ">>> Running Unit Tests..."
echo ""
bash "$SCRIPT_DIR/run_unit_tests.sh"

echo ""
echo ""

# Run functional tests
echo ">>> Running Functional Tests..."
echo ""
bash "$SCRIPT_DIR/run_functional_tests.sh"

echo ""
echo "=========================================="
echo "ALL TESTS COMPLETE!"
echo "=========================================="
