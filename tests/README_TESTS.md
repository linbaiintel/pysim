# Tests Directory

This directory contains test suites and test utilities for the RISC-V simulator.

## Structure

```
tests/
├── functional_tests/           # Official RISC-V test suite integration
│   ├── riscv_test_adapter.py  # Pattern extractor
│   └── run_riscv_tests.py     # Test runner
└── test_all.py                # Unit tests (59 tests, 13 classes)
```

## Files

### Functional Tests (`functional_tests/`)
Tests the simulator against official RISC-V test patterns.

- **`run_riscv_tests.py`** - Main test runner for official RISC-V test suite
  ```bash
  python tests/functional_tests/run_riscv_tests.py add      # Test ADD instruction
  python tests/functional_tests/run_riscv_tests.py          # Run all tests
  ```

- **`riscv_test_adapter.py`** - Extracts test patterns from official RISC-V test sources
  - Parses `.S` assembly files
  - Converts test macros to simulator format
  - Validates results

### Unit Tests
- **`test_all.py`** - Comprehensive unit tests for the simulator
  - 59 tests across 13 test classes
  - Covers pipeline, hazards, edge cases, and instruction execution

## Usage

### Run Official RISC-V Tests
```bash
cd /home/linbai/pysim
source pysim-venv/bin/activate

# Test specific instruction
python tests/functional_tests/run_riscv_tests.py add

# Run all available tests
python tests/functional_tests/run_riscv_tests.py
```

### Run Unit Tests
```bash
python -m pytest tests/test_all.py -v
# or
python tests/test_all.py
```

## Adding New Tests

To add tests for a new instruction:

1. Check if test source exists:
   ```bash
   ls 3rd_party/riscv-tests/isa/rv64ui/
   ```

2. Add to the test list in `functional_tests/run_riscv_tests.py`:
   ```python
   test_files = [
       'add', 'sub', 'your_new_instruction',
   ]
   ```

3. If the instruction uses a different test macro format, extend the pattern extraction in `functional_tests/riscv_test_adapter.py`

## See Also

- [`RISCV_TESTS_GUIDE.md`](../RISCV_TESTS_GUIDE.md) - Complete guide for using official RISC-V tests
- [`utils/`](../utils/) - Utility modules including ELF loader and binary decoder
