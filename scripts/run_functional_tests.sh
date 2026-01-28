#!/bin/bash
# Run RISC-V functional tests
#
# Usage:
#   ./scripts/run_functional_tests.sh           # Run all tests
#   ./scripts/run_functional_tests.sh add       # Run ADD tests only
#   ./scripts/run_functional_tests.sh add sub   # Run multiple specific tests

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
    echo "Please run: python3 -m venv pysim-venv && source pysim-venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if test files exist
if [ ! -f "tests/functional_tests/run_riscv_tests.py" ]; then
    echo "Error: Functional tests not found at tests/functional_tests/run_riscv_tests.py"
    exit 1
fi

# Run tests
echo "=========================================="
echo "Running RISC-V Functional Tests"
echo "=========================================="
echo ""

if [ $# -eq 0 ]; then
    # No arguments - run all tests
    python tests/functional_tests/run_riscv_tests.py
else
    # Run specific tests
    for test in "$@"; do
        echo ""
        python tests/functional_tests/run_riscv_tests.py "$test"
    done
fi

echo ""
echo "=========================================="
echo "Functional tests complete!"
echo "=========================================="
