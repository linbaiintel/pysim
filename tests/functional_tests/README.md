# Functional Tests

This directory contains functional tests that validate the simulator against official RISC-V test patterns.

## Files

### `riscv_test_adapter.py`
Contains test execution logic for running extracted patterns on the simulator.

**Key Functions:**
- `run_extracted_tests(sim_tests, processor_class)` - Executes tests and validates results

**Note:** Pattern extraction and conversion utilities have been moved to `utils/riscv_test_utils.py` for reusability.

### `run_riscv_tests.py`
Main test runner that orchestrates functional testing.

**Usage:**
```bash
# Test a specific instruction
python tests/functional_tests/run_riscv_tests.py add

# Run all available tests
python tests/functional_tests/run_riscv_tests.py

# Or use the convenient bash script:
./scripts/run_functional_tests.sh add
./scripts/run_functional_tests.sh  # Run all tests
```

**Functions:**
- `run_test_file(test_name)` - Run tests for a single instruction
- `run_all_basic_tests()` - Run complete test suite

## Currently Supported Instructions

The functional tests currently validate **217 test cases (100% passing)**:

**Arithmetic:**
- ADD (15 tests), ADDI (15 tests), SUB (14 tests)

**Logical:**
- AND (4 tests), ANDI (4 tests)
- OR (4 tests), ORI (4 tests)
- XOR (4 tests), XORI (4 tests)

**Shifts:**
- SLL (19 tests), SLLI (15 tests)
- SRL (5 tests), SRLI (15 tests)
- SRA (20 tests), SRAI (15 tests)

**Comparison:**
- SLT (15 tests), SLTI (15 tests)
- SLTU (15 tests), SLTIU (15 tests)

## Supported Test Macros

The test extractor supports three macro types:

1. **TEST_RR_OP** - Register-register operations (R-type)
   ```assembly
   TEST_RR_OP( 2, add, 0x00000002, 0x00000001, 0x00000001 );
   ```

2. **TEST_IMM_OP** - Immediate operations (I-type)
   ```assembly
   TEST_IMM_OP( 2, addi, 0x00000002, 0x00000001, 0x001 );
   ```

3. **TEST_SRLI** - SRLI-specific with computed expected values
   ```assembly
   TEST_SRLI( 2, 0xffffffff80000000, 0 );
   ```

## Adding New Tests

1. Ensure test source exists:
   ```bash
   ls 3rd_party/riscv-tests/isa/rv64ui/
   ```

2. Add instruction to the test list in `run_riscv_tests.py`:
   ```python
   test_files = [
       'add', 'sub', 'new_instruction',
   ]
   ```

3. If the test uses a different macro format (e.g., `TEST_LD_OP`, `TEST_ST_OP`, `TEST_BR_OP`), extend the pattern matching in `utils/riscv_test_utils.py` function `extract_test_patterns()`:
   ```python
   # Example: Add new pattern for branch operations
   br_pattern = r'TEST_BR_OP\s*\(\s*(\d+)\s*,\s*(\w+)\s*,...\)'
   ```

## Special Features

- **RV64 Filtering**: Automatically skips tests inside `#if __riscv_xlen == 64` blocks
- **Value Format**: Handles both hexadecimal (0x...) and decimal value formats
- **Sign Extension**: Properly sign-extends 12-bit immediates for I-type instructions
- **32-bit Masking**: Ensures all results are masked to 32-bit for RV32 compatibility

## Test Results Format

Tests report pass/fail for each instruction:
```
============================================================
Running ADD tests
============================================================
Found 15 tests to run

============================================================
Results: 15 passed, 0 failed out of 15 tests
============================================================
```

Failures show details:
```
✗ Test #5 FAILED: ADD R3, R1, R2
  Expected R3=0x00000002, got 0x00000003
```

## See Also

- [RISCV_TESTS_GUIDE.md](../../RISCV_TESTS_GUIDE.md) - Complete guide
- [Official RISC-V Tests](../../3rd_party/riscv-tests/) - Test source files
