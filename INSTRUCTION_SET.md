# RISC-V Instruction Set - Implementation Status

This document describes the RISC-V instructions supported by this simulator.

## Currently Implemented Instructions

### R-Type (Register-Register) Operations
| Instruction | Format | Description | Example |
|------------|--------|-------------|---------|
| ADD | `ADD rd, rs1, rs2` | Add | `ADD R1, R2, R3` → R1 = R2 + R3 |
| SUB | `SUB rd, rs1, rs2` | Subtract | `SUB R1, R2, R3` → R1 = R2 - R3 |
| AND | `AND rd, rs1, rs2` | Bitwise AND | `AND R1, R2, R3` → R1 = R2 & R3 |
| OR | `OR rd, rs1, rs2` | Bitwise OR | `OR R1, R2, R3` → R1 = R2 \| R3 |
| XOR | `XOR rd, rs1, rs2` | Bitwise XOR | `XOR R1, R2, R3` → R1 = R2 ^ R3 |
| SLT | `SLT rd, rs1, rs2` | Set if Less Than (signed) | `SLT R1, R2, R3` → R1 = (R2 < R3) ? 1 : 0 |
| SLTU | `SLTU rd, rs1, rs2` | Set if Less Than (unsigned) | `SLTU R1, R2, R3` → R1 = (R2 < R3) ? 1 : 0 |
| SLL | `SLL rd, rs1, rs2` | Shift Left Logical | `SLL R1, R2, R3` → R1 = R2 << R3 |
| SRL | `SRL rd, rs1, rs2` | Shift Right Logical | `SRL R1, R2, R3` → R1 = R2 >> R3 |
| SRA | `SRA rd, rs1, rs2` | Shift Right Arithmetic | `SRA R1, R2, R3` → R1 = R2 >> R3 (sign-extend) |

### I-Type (Immediate) Operations
| Instruction | Format | Description | Example |
|------------|--------|-------------|---------|
| ADDI | `ADDI rd, rs1, imm` | Add Immediate | `ADDI R1, R2, 100` → R1 = R2 + 100 |
| ANDI | `ANDI rd, rs1, imm` | AND Immediate | `ANDI R1, R2, 0xFF` → R1 = R2 & 0xFF |
| ORI | `ORI rd, rs1, imm` | OR Immediate | `ORI R1, R2, 0xF0` → R1 = R2 \| 0xF0 |
| XORI | `XORI rd, rs1, imm` | XOR Immediate | `XORI R1, R2, 0xFF` → R1 = R2 ^ 0xFF |
| SLTI | `SLTI rd, rs1, imm` | Set if Less Than Immediate (signed) | `SLTI R1, R2, 10` → R1 = (R2 < 10) ? 1 : 0 |
| SLTIU | `SLTIU rd, rs1, imm` | Set if Less Than Immediate (unsigned) | `SLTIU R1, R2, 10` → R1 = (R2 < 10) ? 1 : 0 |
| SLLI | `SLLI rd, rs1, shamt` | Shift Left Logical Immediate | `SLLI R1, R2, 4` → R1 = R2 << 4 |
| SRLI | `SRLI rd, rs1, shamt` | Shift Right Logical Immediate | `SRLI R1, R2, 4` → R1 = R2 >> 4 |
| SRAI | `SRAI rd, rs1, shamt` | Shift Right Arithmetic Immediate | `SRAI R1, R2, 2` → R1 = R2 >> 2 (sign-extend) |

### Load/Store Operations
| Instruction | Format | Description | Example |
|------------|--------|-------------|---------|
| LOAD/LW | `LOAD rd, offset(rs1)` | Load word from memory | `LOAD R1, 100(R2)` → R1 = mem[R2+100] |
| STORE/SW | `STORE rs2, offset(rs1)` | Store word to memory | `STORE R1, 100(R2)` → mem[R2+100] = R1 |

### Upper Immediate Operations
| Instruction | Format | Description | Example |
|------------|--------|-------------|---------|
| LUI | `LUI rd, imm` | Load Upper Immediate | `LUI R1, 0x12345` → R1 = 0x12345000 |
| AUIPC | `AUIPC rd, imm` | Add Upper Immediate to PC | `AUIPC R1, 0x1000` → R1 = PC + 0x1000000 (⚠️ PC tracking not implemented) |

### Branch Operations
**Note:** Branch instructions perform comparison only. PC update and actual branching are not implemented.

| Instruction | Format | Description | Example |
|------------|--------|-------------|---------|
| BEQ | `BEQ rs1, rs2, offset` | Branch if Equal | `BEQ R1, R2, 100` → if (R1 == R2) branch |
| BNE | `BNE rs1, rs2, offset` | Branch if Not Equal | `BNE R1, R2, 100` → if (R1 != R2) branch |
| BLT | `BLT rs1, rs2, offset` | Branch if Less Than (signed) | `BLT R1, R2, 100` → if (R1 < R2) branch |
| BGE | `BGE rs1, rs2, offset` | Branch if Greater or Equal (signed) | `BGE R1, R2, 100` → if (R1 >= R2) branch |
| BLTU | `BLTU rs1, rs2, offset` | Branch if Less Than (unsigned) | `BLTU R1, R2, 100` → if (R1 < R2) branch |
| BGEU | `BGEU rs1, rs2, offset` | Branch if Greater or Equal (unsigned) | `BGEU R1, R2, 100` → if (R1 >= R2) branch |

### Jump Operations
**Note:** Jump instructions recognized but PC tracking not implemented.

| Instruction | Format | Description | Status |
|------------|--------|-------------|---------|
| JAL | `JAL rd, offset` | Jump and Link | ⚠️ Parsed but not functional (needs PC) |
| JALR | `JALR rd, rs1, offset` | Jump and Link Register | ⚠️ Parsed but not functional (needs PC) |

## Instruction Format Details

### Immediate Value Formats
- **Decimal:** `100`, `-50`
- **Hexadecimal:** `0x1A`, `0xFF`
- Immediates are sign-extended to 32 bits

### Register Naming
- Standard format: `R0` through `R31`
- `R0` is hardwired to zero (writes are ignored)

### Memory Addressing
- Format: `offset(base_register)`
- Example: `LOAD R1, 100(R2)` loads from address `R2 + 100`
- Negative offsets supported: `LOAD R1, -10(R2)`

## ALU Implementation Details

### 32-bit Operations
All operations are performed on 32-bit values with proper masking.

### Shift Operations
- Shift amounts use only the lower 5 bits (0-31)
- **SLL/SLLI:** Logical left shift, fills with zeros
- **SRL/SRLI:** Logical right shift, fills with zeros
- **SRA/SRAI:** Arithmetic right shift, sign-extends

### Signed vs Unsigned
- **Signed:** `SLT`, `SLTI`, `BLT`, `BGE` - uses two's complement comparison
- **Unsigned:** `SLTU`, `SLTIU`, `BLTU`, `BGEU` - uses unsigned comparison

## Test Coverage

59 tests covering:
- ✅ R-type register operations
- ✅ I-type immediate operations  
- ✅ Shift operations (all 6 variants)
- ✅ Signed and unsigned comparisons
- ✅ Upper immediate instructions (LUI)
- ✅ Branch comparisons (6 types)
- ✅ Load/Store operations
- ✅ RAW hazard detection
- ✅ Pipeline stall behavior
- ✅ Complex multi-instruction programs

## Not Yet Implemented (RV32I Extensions)

### Memory Access Variants
- `LB`, `LH`, `LBU`, `LHU` - Load byte/halfword (signed/unsigned)
- `SB`, `SH` - Store byte/halfword

### Control Flow
- Full PC (Program Counter) tracking
- Actual branch/jump execution
- Return address handling

### System Instructions
- `ECALL` - Environment call
- `EBREAK` - Breakpoint

## Usage Examples

### Loading a 32-bit Constant
```assembly
LUI R1, 0xDEADB      # Load upper 20 bits
ADDI R1, R1, 0xEEF   # Add lower 12 bits
# Result: R1 = 0xDEADBEEF
```

### Bit Manipulation
```assembly
ADDI R1, R0, 0xFF     # R1 = 255
SLLI R2, R1, 8        # R2 = 255 << 8 = 0xFF00
ORI R3, R2, 0x0F      # R3 = 0xFF00 | 0x0F = 0xFF0F
ANDI R4, R3, 0xF0F0   # R4 = 0xFF0F & 0xF0F0 = 0xF000
```

### Conditional Logic
```assembly
ADDI R1, R0, 100      # R1 = 100
SLTI R2, R1, 200      # R2 = 1 (100 < 200)
BEQ R2, R0, skip      # Skip if R2 == 0 (not taken)
```

## See Also
- [README.md](README.md) - Main documentation
- [tests/test_new_instructions.py](tests/test_new_instructions.py) - Test suite for all instructions
