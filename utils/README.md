# Utils Directory

Utility modules for the RISC-V simulator.

## Modules

### `elf_loader.py`
**ELF Binary Loader and RISC-V Instruction Decoder**

Provides tools for loading and decoding RISC-V ELF binaries.

#### Classes

**`RISCVDecoder`**
- Decodes 32-bit RISC-V machine code instructions
- Supports R-type, I-type, S-type, B-type, U-type, and J-type instructions
- Outputs instructions in simulator text format

**`ELFTestLoader`**
- Loads RISC-V test ELF binaries into memory
- Extracts and decodes instruction sequences
- Useful for binary-level test validation

#### Usage Examples

```python
from utils.elf_loader import RISCVDecoder, ELFTestLoader

# Decode a single instruction
decoder = RISCVDecoder()
instruction = decoder.decode(0x003100B3)  # Returns: "ADD R1, R2, R3"

# Load and decode an ELF binary
loader = ELFTestLoader("3rd_party/riscv-tests/isa/rv32ui-p-add")
memory, entry_point = loader.load()
instructions = loader.extract_instructions()

for addr, instr in instructions[:10]:
    print(f"0x{addr:08x}: {instr}")
```

#### Command Line Usage

```bash
# Test decoder with example instructions
python utils/elf_loader.py

# Load and decode a specific test binary
python utils/elf_loader.py 3rd_party/riscv-tests/isa/rv32ui-p-add
```

### `riscv_test_utils.py`
**RISC-V Test Pattern Extraction Utilities**

Provides functions to extract and convert official RISC-V test patterns.

#### Functions

**`extract_test_patterns(test_source_file)`**
- Extracts test patterns from `.S` assembly test files
- Parses multiple macro types:
  - `TEST_RR_OP`: Register-register operations (R-type)
  - `TEST_IMM_OP`: Immediate operations (I-type)
  - `TEST_SRLI`: SRLI-specific macro with computed expected values
- Automatically filters RV64-specific tests (inside `#if __riscv_xlen == 64` blocks)
- Handles both hexadecimal (0x...) and decimal value formats
- Returns list of test dictionaries with test_num, instruction, expected, src1, src2, type

**`convert_to_simulator_format(tests, instruction_map=None)`**
- Converts extracted patterns to simulator instruction format
- Handles both R-type (register-register) and I-type (immediate) operations
- Maps register names and instruction mnemonics
- Sign-extends 12-bit immediates for I-type instructions
- Masks results to 32-bit for RV32 compatibility
- Returns test cases ready for execution

#### Usage Examples

```python
from utils.riscv_test_utils import extract_test_patterns, convert_to_simulator_format

# Extract patterns from test source
tests = extract_test_patterns("3rd_party/riscv-tests/isa/rv64ui/add.S")
print(f"Found {len(tests)} test patterns")

# Convert to simulator format
sim_tests = convert_to_simulator_format(tests)

# Each sim_test contains:
# - test_num: Test identifier
# - setup: Initial register values (R1, R2 for RR-type; R1 only for IMM-type)
# - instruction: Formatted instruction string (e.g., "ADD R3, R1, R2" or "ADDI R3, R1, 5")
# - expected_result: Expected register values after execution

# Example extracted test:
# {
#   'test_num': 2,
#   'instruction': 'ADDI',
#   'expected': 2,
#   'src1': 1,
#   'src2': 1,
#   'type': 'IMM'
# }
```

## Supported Instructions

### Test Pattern Extraction (`riscv_test_utils.py`)

Currently extracts tests for **217 test cases** from official RISC-V test suite:

- **Arithmetic**: ADD (15), ADDI (15), SUB (14)
- **Logical**: AND (4), ANDI (4), OR (4), ORI (4), XOR (4), XORI (4)
- **Shifts**: SLL (19), SLLI (15), SRL (5), SRLI (15), SRA (20), SRAI (15)
- **Comparison**: SLT (15), SLTI (15), SLTU (15), SLTIU (15)

### Binary Decoder (`elf_loader.py`)

The ELF decoder supports:

- **Arithmetic**: ADD, SUB, ADDI
- **Logical**: AND, OR, XOR, ANDI, ORI, XORI
- **Shifts**: SLL, SRL, SRA, SLLI, SRLI, SRAI
- **Comparison**: SLT, SLTU, SLTI, SLTIU
- **Branches**: BEQ, BNE, BLT, BGE, BLTU, BGEU
- **Jumps**: JAL, JALR
- **Upper Immediate**: LUI, AUIPC
- **Memory**: LOAD (LW), STORE (SW)

## Future Enhancements

- Support for RV64I (64-bit instructions)
- M extension (multiplication/division)
- A extension (atomic operations)
- F/D extensions (floating point)
- Compressed instructions (C extension)

## Dependencies

All dependencies are listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

**Required packages:**
- `pyelftools==0.32` - For parsing ELF files
- `simpy==4.1.1` - Discrete event simulation framework
