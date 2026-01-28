# Using RISC-V Official Tests with Your Simulator

## Overview

You now have **two approaches** to integrate official RISC-V tests into your simulator:

### **Approach 1: Pattern Extraction (Recommended & Working)**
Extracts test patterns from source files and converts them to your simulator's text format.

**✓ Advantages:**
- Works immediately with your existing simulator
- No need to modify simulator architecture
- Easy to understand and debug
- Already tested and working!

**Files:**
- `utils/riscv_test_utils.py` - Extracts test patterns from `.S` source files
- `tests/functional_tests/riscv_test_adapter.py` - Executes tests on simulator
- `tests/functional_tests/run_riscv_tests.py` - Main test runner
- `scripts/run_functional_tests.sh` - Convenient bash wrapper

### **Approach 2: Binary Decoding (Future Enhancement)**
Decodes actual binary instructions from ELF files.

**Files:**
- `utils/elf_loader.py` - Loads ELF binaries and decodes RISC-V machine code

**⚠ Requires:** Extending your simulator to handle binary instructions and memory-mapped I/O.

---

## Quick Start - Running Tests

### Test a Single Instruction

```bash
cd /home/linbai/pysim
./scripts/run_functional_tests.sh add
```

### Run All Tests

```bash
./scripts/run_functional_tests.sh
```

### Current Test Results

```
✓ PASS add       :  15 passed,   0 failed
✓ PASS addi      :  15 passed,   0 failed
✓ PASS sub       :  14 passed,   0 failed
✓ PASS and       :   4 passed,   0 failed
✓ PASS andi      :   4 passed,   0 failed
✓ PASS sll       :  19 passed,   0 failed
✓ PASS slli      :  15 passed,   0 failed
✓ PASS srli      :  15 passed,   0 failed
... (19 instructions tested)

------------------------------------------------------------
TOTAL: 217/217 tests passed (100.0%)
```

---

## How It Works

### 1. Test Pattern Extraction

The official RISC-V tests use multiple macro types:

**TEST_RR_OP** (Register-Register operations):
```assembly
TEST_RR_OP( 2, add, 0x00000002, 0x00000001, 0x00000001 );
```

**TEST_IMM_OP** (Immediate operations):
```assembly
TEST_IMM_OP( 2, addi, 0x00000002, 0x00000001, 0x001 );
```

**TEST_SRLI** (SRLI specific macro):
```assembly
TEST_SRLI( 2, 0xffffffff80000000, 0 );
```

Our adapter extracts these into:
```python
{
    'test_num': 2,
    'instruction': 'ADD',
    'expected': 0x2,
    'src1': 0x1,
    'src2': 0x1,
    'type': 'RR'  # or 'IMM' for immediate
}
```

### 2. Format Conversion

Converts to your simulator's format:

**For Register-Register:**
```python
{
    'setup': {'R1': 0x1, 'R2': 0x1},
    'instruction': 'ADD R3, R1, R2',
    'expected_result': {'R3': 0x2}
}
```

**For Immediate:**
```python
{
    'setup': {'R1': 0x1},
    'instruction': 'ADDI R3, R1, 1',
    'expected_result': {'R3': 0x2}
}
```

### 3. Execution & Validation

```python
processor = RISCVProcessor()
processor.initialize_registers(test['setup'])
processor.execute([test['instruction']], verbose=False)
result = processor.get_register('R3')
assert result == expected  # Validates correctness
```

---

## Supported Instructions

Currently supported (217 tests from official RISC-V test suite):

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

**Macro Support:**
- TEST_RR_OP - Register-register operations
- TEST_IMM_OP - Immediate operations
- TEST_SRLI - SRLI-specific macro with computed expected values

---

## Adding More Tests

### For New Instructions

1. Check if test source exists:
   ```bash
   ls 3rd_party/riscv-tests/isa/rv64ui/
   ```

2. Add to test list in `tests/functional_tests/run_riscv_tests.py`:
   ```python
   test_files = [
       'add', 'sub', 'mul',  # Add new test here
   ]
   ```

3. If instruction uses different format (B-type, S-type, U-type, J-type), extend `extract_test_patterns()` in `utils/riscv_test_utils.py` with new pattern matching

### For Load/Store Tests

These require special handling. Look for `TEST_LD_OP` or `TEST_ST_OP` patterns and add extraction logic.

---

## Understanding Test Binaries (Advanced)

The compiled test binaries (`rv32ui-p-*`) follow this convention:

**Test Pass/Fail Protocol:**
- Tests write to memory address `0x80001000` (tohost)
- Value `1` = PASS
- Value > `1` = FAIL (contains test number)

**Entry Point:** 
- All tests start at `0x80000000`

**To Use Binaries (Future):**
1. Add ELF loader to simulator
2. Implement memory-mapped I/O for tohost
3. Add binary instruction decoder
4. Monitor tohost address for results

---

## Example: Manual Test Inspection

Want to see what a test does?

```bash
# View test source
cat 3rd_party/riscv-tests/isa/rv64ui/add.S

# Extract and view patterns
cd /home/linbai/pysim
source pysim-venv/bin/activate
python tests/functional_tests/riscv_test_adapter.py

# View compiled binary (if interested)
riscv64-unknown-elf-objdump -d 3rd_party/riscv-tests/isa/rv32ui-p-add | less
```

---

## Troubleshooting

### Test Not Found
```
Test source not found: 3rd_party/riscv-tests/isa/rv64ui/xxx.S
```
**Solution:** Check available tests:
```bash
ls 3rd_party/riscv-tests/isa/rv64ui/*.S
```

### No Compatible Tests Found
```
No compatible tests found in xxx
```
**Solution:** Test uses unsupported macro type (e.g., TEST_CASE, TEST_BR_OP, TEST_LD_OP, TEST_ST_OP). Extend `extract_test_patterns()` in `utils/riscv_test_utils.py` with new regex pattern.

Note: Current support includes TEST_RR_OP, TEST_IMM_OP, and TEST_SRLI.

### Import Errors
```
ModuleNotFoundError: No module named 'elftools'
```
**Solution:** Install dependencies:
```bash
source pysim-venv/bin/activate
pip install -r requirements.txt
```

All required packages (simpy, pyelftools) are specified in `requirements.txt`.

---

## Next Steps

1. **Run full test suite**: `python tests/functional_tests/run_riscv_tests.py`
2. **Add branch tests**: Extend for BEQ, BNE, BLT, BGE, etc.
3. **Add load/store tests**: Extract TEST_LD_OP and TEST_ST_OP patterns
4. **Integrate with CI**: Add to automated testing pipeline

---

## Files Reference

| File | Purpose | Usage |
|------|---------|-------|
| `utils/riscv_test_utils.py` | Extract & convert test patterns | Library module |
| `tests/functional_tests/riscv_test_adapter.py` | Execute tests on simulator | Library module |
| `tests/functional_tests/run_riscv_tests.py` | Main test runner | Direct Python execution |
| `scripts/run_functional_tests.sh` | Bash wrapper for tests | `./scripts/run_functional_tests.sh [test_name]` |
| `utils/elf_loader.py` | Load/decode binary tests | `python utils/elf_loader.py path/to/binary` |
| `3rd_party/riscv-tests/isa/` | Official test binaries & sources | Test data |

---

## Summary

**You can now validate your simulator against official RISC-V tests!** 

The current approach (pattern extraction) works perfectly with your existing simulator architecture and has **217 tests passing (100%)** covering all basic integer arithmetic, logical, shift, and comparison instructions. The system supports:

- **TEST_RR_OP**: Register-register operations (R-type)
- **TEST_IMM_OP**: Immediate operations (I-type)
- **TEST_SRLI**: Special SRLI macro with computed expectations
- **RV64 filtering**: Automatically skips RV64-specific tests for RV32 simulator
- **Flexible parsing**: Handles both hexadecimal (0x...) and decimal values

Extend it further by adding support for branch (B-type), load/store (S-type), and jump (J-type) instructions.
