# Scripts Directory

Convenient shell scripts for running tests and managing the RISC-V simulator project.

## Available Scripts

### `run_functional_tests.sh`
Run RISC-V functional tests against official test patterns.

**Usage:**
```bash
# Run all functional tests
./scripts/run_functional_tests.sh

# Run specific test(s)
./scripts/run_functional_tests.sh add
./scripts/run_functional_tests.sh add sub and or

# From any directory
cd /home/linbai/pysim
./scripts/run_functional_tests.sh add
```

**Features:**
- Automatically activates virtual environment
- Validates that test files exist
- Supports multiple test arguments
- Clear output formatting

**Example Output:**
```
==========================================
Running RISC-V Functional Tests
==========================================

============================================================
Running ADD tests
============================================================
Found 15 tests to run

============================================================
Results: 15 passed, 0 failed out of 15 tests
============================================================

============================================================
FINAL SUMMARY
============================================================
✓ PASS add       :  15 passed,   0 failed
✓ PASS addi      :  15 passed,   0 failed
✓ PASS sub       :  14 passed,   0 failed
... (19 instructions)

------------------------------------------------------------
TOTAL: 217/217 tests passed (100.0%)
============================================================
```

**Test Coverage:**
- 217 official RISC-V test cases
- 19 instructions (arithmetic, logical, shift, comparison)
- Supports R-type and I-type operations
- 100% pass rate

---

### `run_unit_tests.sh`
Run comprehensive unit tests for the simulator.

**Usage:**
```bash
# Run all unit tests
./scripts/run_unit_tests.sh

# Run with verbose output (if pytest available)
./scripts/run_unit_tests.sh -v

# Run tests matching a pattern (if pytest available)
./scripts/run_unit_tests.sh -k "test_add"
```

**Features:**
- Uses pytest if available, falls back to direct Python execution
- Passes arguments through to pytest
- Tests 59 test cases across 13 classes
- Validates pipeline, hazards, edge cases, and instruction execution

---

### `run_all_tests.sh`
Run both unit and functional tests in sequence.

**Usage:**
```bash
# Run everything
./scripts/run_all_tests.sh
```

**Features:**
- Runs unit tests first
- Then runs functional tests
- Provides comprehensive test coverage
- Clear section separators

**Example Output:**
```
==========================================
RUNNING ALL TESTS
==========================================

>>> Running Unit Tests...

==========================================
Unit tests complete!
==========================================


>>> Running Functional Tests...

==========================================
Functional tests complete!
==========================================

==========================================
ALL TESTS COMPLETE!
==========================================
```

---

## Requirements

All scripts require:
- Virtual environment at `pysim-venv/`
- Required packages installed (see `requirements.txt`)

**Setup:**
```bash
cd /home/linbai/pysim
python3 -m venv pysim-venv
source pysim-venv/bin/activate
pip install -r requirements.txt
```

---

## Test Coverage

### Unit Tests (59 tests)
- Pipeline correctness (6 tests)
- Instruction parsing (8 tests)
- Hazard detection (7 tests)
- No false hazards (5 tests)
- Edge cases (6 tests)
- Instruction types (8 tests)
- Performance tests (2 tests)
- New instructions (17 tests across multiple categories)

### Functional Tests
Currently supports testing:
- **Arithmetic**: add, addi, sub
- **Logical**: and, andi, or, ori, xor, xori
- **Shifts**: sll, slli, srl, srli, sra, srai
- **Comparison**: slt, slti, sltu, sltiu

---

## Exit Codes

All scripts follow standard exit code conventions:
- `0` - All tests passed
- `1` - Test failure or setup error

---

## Troubleshooting

### Virtual Environment Not Found
```
Error: Virtual environment not found at pysim-venv/
```
**Solution:** Create and setup the virtual environment:
```bash
python3 -m venv pysim-venv
source pysim-venv/bin/activate
pip install -r requirements.txt
```

### Test Files Not Found
```
Error: Functional tests not found at tests/functional_tests/run_riscv_tests.py
```
**Solution:** Ensure you're running from the project root directory:
```bash
cd /home/linbai/pysim
./scripts/run_functional_tests.sh
```

### Permission Denied
```
bash: ./scripts/run_functional_tests.sh: Permission denied
```
**Solution:** Make scripts executable:
```bash
chmod +x scripts/*.sh
```

---

## CI/CD Integration

These scripts are designed to be CI-friendly:

```yaml
# Example GitHub Actions workflow
- name: Run all tests
  run: |
    source pysim-venv/bin/activate
    ./scripts/run_all_tests.sh
```

```yaml
# Run only functional tests
- name: Functional tests
  run: ./scripts/run_functional_tests.sh
```

---

## Development Workflow

**Quick test during development:**
```bash
# Test the instruction you're working on
./scripts/run_functional_tests.sh add

# Run unit tests to check for regressions
./scripts/run_unit_tests.sh
```

**Before committing:**
```bash
# Run full test suite
./scripts/run_all_tests.sh
```

**Testing specific functionality:**
```bash
# Arithmetic instructions
./scripts/run_functional_tests.sh add sub addi

# Logical operations
./scripts/run_functional_tests.sh and or xor

# Shifts
./scripts/run_functional_tests.sh sll srl sra
```
