# JAL and JALR Implementation Summary

## Overview
Added full support for RISC-V jump instructions JAL (Jump And Link) and JALR (Jump And Link Register).

## What Was Implemented

### 1. Instruction Class Updates ([instruction.py](../instruction.py))
- Added `is_jump` flag to identify jump instructions
- Added `jump_target` field to store calculated jump target address
- Jump instructions are marked with `is_jump = True` during parsing

### 2. EXE Class Enhancements ([exe.py](../exe.py))
Added two new execution methods:

**`execute_jal(offset, pc=0)`**
- Calculates return address: PC + 4
- Calculates jump target: PC + offset
- Returns: (return_address, jump_target)

**`execute_jalr(base_value, offset, pc=0)`**
- Calculates return address: PC + 4
- Calculates jump target: (base_value + offset) & ~1 (clears LSB per RISC-V spec)
- Returns: (return_address, jump_target)

**`execute_instruction()` updates**
- JAL: Uses offset from instruction
- JALR: Uses source register value + offset
- Both store jump_target in instruction for potential pipeline flush

### 3. Pipeline Updates ([pipeline.py](../pipeline.py))
- ExecuteStage now prints return address and jump target for JAL/JALR
- Displays hex values for better debugging
- Notes that pipeline flush is not yet implemented

## Test Coverage ([tests/functional_tests/test_jump.py](../tests/functional_tests/test_jump.py))

Created comprehensive test suite with **12 tests**:

1. **test_jal_parsing** - Verifies JAL instruction parsing
2. **test_jalr_parsing** - Verifies JALR instruction parsing
3. **test_jal_execution** - Tests JAL return address calculation
4. **test_jalr_execution** - Tests JALR return address calculation
5. **test_jal_negative_offset** - Tests backward jumps
6. **test_jalr_with_zero_offset** - Tests JALR with zero offset
7. **test_jal_link_to_r0** - Tests storing to R0 (should remain 0)
8. **test_jal_then_other_instruction** - Tests sequential execution after JAL
9. **test_jalr_dependency** - Tests RAW hazards with JALR
10. **test_function_call_pattern** - Simulates function call/return pattern
11. **test_multiple_jal_instructions** - Tests multiple JAL instructions
12. **test_jalr_clears_lsb** - Verifies LSB clearing per RISC-V spec

### Test Results
```
Ran 12 tests in 0.007s
OK
```

All tests in full suite: **100 tests passing** (88 original + 12 jump)

## RISC-V Specification Compliance

### JAL (Jump And Link)
✅ **Implemented:**
- Syntax: `JAL rd, offset`
- Stores PC+4 in rd (return address)
- Calculates jump target as PC + offset
- Supports positive and negative offsets
- 32-bit address arithmetic with proper masking

### JALR (Jump And Link Register)
✅ **Implemented:**
- Syntax: `JALR rd, rs1, offset`
- Stores PC+4 in rd (return address)
- Calculates jump target as (rs1 + offset) & ~1
- LSB is cleared per RISC-V specification
- Handles computed jumps and indirect calls

## Demo Program ([sandbox/demo_jump.py](../sandbox/demo_jump.py))

Created interactive demo showing:
1. JAL basic operation
2. JALR basic operation
3. Function call pattern (JAL + JALR)
4. JALR with computed addresses

Run with: `python3 sandbox/demo_jump.py`

## Limitations / Future Work

### ✅ Implemented (NEW):
1. **Pipeline Flush** - When a jump or taken branch occurs, instructions in early stages are flushed (converted to bubbles)
   - Flush triggered by JAL, JALR (unconditional jumps)
   - Flush triggered by taken branches (BEQ, BNE, BLT, BGE, BLTU, BGEU when condition is true)
   - Instructions in Decode stage are converted to bubbles during flush
   - Flush signal propagates through pipeline stages
   - flush_count tracked for performance analysis

### Not Yet Implemented:
1. **PC Update to Jump Target** - Fetch stage doesn't restart from jump target address
2. **Branch Prediction** - No speculation on jump/branch targets
3. **Return Address Stack** - No hardware optimization for function returns

### Current Behavior:
- Jump/branch instructions calculate target addresses correctly
- Instructions already in Execute or later stages complete (too late to flush)
- Instructions in Fetch/Decode are flushed when jump/branch taken
- Useful for understanding control flow and pipeline behavior
- Pipeline hazard detection works correctly with jump dependencies

## Integration

### Updated Files:
- `instruction.py` - Added is_jump and jump_target fields
- `exe.py` - Added execute_jal() and execute_jalr() methods
- `pipeline.py` - Updated ExecuteStage output formatting
- `tests/test_all.py` - Imported TestJumpInstructions
- `INSTRUCTION_SET.md` - Updated status to "Functional"

### New Files:
- `tests/functional_tests/test_jump.py` - Complete test suite
- `sandbox/demo_jump.py` - Interactive demonstration

## Example Usage

```python
from riscv import RISCVProcessor

processor = RISCVProcessor()
processor.register_file.write_pc(0x1000)
processor.register_file.write("R2", 0x2000)

program = [
    "JAL R1, 100",        # Jump forward, R1 = 0x1004
    "JALR R3, R2, 50",    # Jump to R2+50, R3 = 0x1004
]

results = processor.execute(program)

# R1 contains return address for JAL
print(f"R1 = {processor.get_register('R1'):#x}")  # 0x1004

# R3 contains return address for JALR
print(f"R3 = {processor.get_register('R3'):#x}")  # 0x1004
```

## Instruction Coverage Update

Total RV32I instructions parsed: **39**
Total instructions tested: **29** (74%)

Newly functional:
- JAL ✅
- JALR ✅

Remaining untested: 10 instructions (mostly system/fence instructions)
