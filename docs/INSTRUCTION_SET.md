# RISC-V Instruction Set - Implementation Status

This document describes the RISC-V instructions supported by this simulator. **Status: 29/40 RV32I instructions implemented (72.5%)**

For complete RV32I coverage analysis, see [RV32I_COVERAGE.md](RV32I_COVERAGE.md).

## Currently Implemented Instructions (29/40)

### R-Type (Register-Register) Operations ✅ 10/10
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

### I-Type (Immediate) ALU Operations ✅ 9/9
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

### Load Operations ✅ 5/5
| Instruction | Format | Description | Example |
|------------|--------|-------------|---------|
| LW | `LW rd, offset(rs1)` | Load Word (32-bit) | `LW R1, 100(R2)` → R1 = mem[R2+100] |
| LH | `LH rd, offset(rs1)` | Load Halfword (16-bit, sign-extended) | `LH R1, 100(R2)` → R1 = sign_extend(mem[R2+100]) |
| LB | `LB rd, offset(rs1)` | Load Byte (8-bit, sign-extended) | `LB R1, 100(R2)` → R1 = sign_extend(mem[R2+100]) |
| LHU | `LHU rd, offset(rs1)` | Load Halfword Unsigned | `LHU R1, 100(R2)` → R1 = zero_extend(mem[R2+100]) |
| LBU | `LBU rd, offset(rs1)` | Load Byte Unsigned | `LBU R1, 100(R2)` → R1 = zero_extend(mem[R2+100]) |

### Store Operations ✅ 3/3
| Instruction | Format | Description | Example |
|------------|--------|-------------|---------|
| SW | `SW rs2, offset(rs1)` | Store Word (32-bit) | `SW R1, 100(R2)` → mem[R2+100] = R1 |
| SH | `SH rs2, offset(rs1)` | Store Halfword (16-bit) | `SH R1, 100(R2)` → mem[R2+100] = R1[15:0] |
| SB | `SB rs2, offset(rs1)` | Store Byte (8-bit) | `SB R1, 100(R2)` → mem[R2+100] = R1[7:0] |

### Upper Immediate Operations ✅ 2/2
| Instruction | Format | Description | Example |
|------------|--------|-------------|---------|
| LUI | `LUI rd, imm` | Load Upper Immediate | `LUI R1, 0x12345` → R1 = 0x12345000 |
| AUIPC | `AUIPC rd, imm` | Add Upper Immediate to PC | `AUIPC R1, 0x1000` → R1 = PC + (0x1000 << 12) |

### Branch Operations ✅ 6/6
| Instruction | Format | Description | Example |
|------------|--------|-------------|---------|
| BEQ | `BEQ rs1, rs2, offset` | Branch if Equal | `BEQ R1, R2, 100` → if (R1 == R2) PC += offset |
| BNE | `BNE rs1, rs2, offset` | Branch if Not Equal | `BNE R1, R2, 100` → if (R1 != R2) PC += offset |
| BLT | `BLT rs1, rs2, offset` | Branch if Less Than (signed) | `BLT R1, R2, 100` → if (R1 < R2) PC += offset |
| BGE | `BGE rs1, rs2, offset` | Branch if Greater or Equal (signed) | `BGE R1, R2, 100` → if (R1 >= R2) PC += offset |
| BLTU | `BLTU rs1, rs2, offset` | Branch if Less Than (unsigned) | `BLTU R1, R2, 100` → if (R1 < R2) PC += offset |
| BGEU | `BGEU rs1, rs2, offset` | Branch if Greater or Equal (unsigned) | `BGEU R1, R2, 100` → if (R1 >= R2) PC += offset |

**Pipeline behavior:** Taken branches trigger pipeline flush. Not-taken branches continue normally.

### Jump Operations ✅ 2/2
| Instruction | Format | Description | Example |
|------------|--------|-------------|---------|
| JAL | `JAL rd, offset` | Jump and Link | `JAL R1, 100` → R1 = PC+4, PC += offset |
| JALR | `JALR rd, rs1, offset` | Jump and Link Register | `JALR R1, R2, 8` → R1 = PC+4, PC = (R2+8)&~1 |

**Pipeline behavior:** All jumps trigger pipeline flush to discard incorrectly fetched instructions.

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

## Not Yet Implemented (11/40 RV32I)

### System Instructions ❌ 0/2
| Instruction | Why Missing | Impact |
|------------|-------------|--------|
| ECALL | Requires OS environment simulation | Cannot run programs with system calls (printf, exit) |
| EBREAK | Requires debugger support | Cannot use breakpoints |

### Memory Ordering ❌ 0/2
| Instruction | Why Missing | Impact |
|------------|-------------|--------|
| FENCE | Multi-core synchronization | Single-core simulator doesn't need it (can be NOP) |
| FENCE.I | Instruction cache synchronization | No separate I-cache (can be NOP) |

### Control and Status Registers (CSR) ❌ 0/7
| Instruction | Why Missing | Impact |
|------------|-------------|--------|
| CSRRW, CSRRS, CSRRC | CSR bank not implemented | Cannot access performance counters |
| CSRRWI, CSRRSI, CSRRCI | CSR bank not implemented | Cannot use immediate CSR operations |

**Note:** The simulator is **complete for user-mode computational programs**. Missing instructions are system/privileged level operations.

## Test Coverage

**109 tests** covering:
- ✅ All R-type register operations (10 instructions)
- ✅ All I-type immediate operations (9 instructions)
- ✅ All shift operations (6 variants)
- ✅ Signed and unsigned comparisons
- ✅ All load variants (LW, LH, LB, LHU, LBU) with sign/zero extension
- ✅ All store variants (SW, SH, SB)
- ✅ Upper immediate instructions (LUI, AUIPC)
- ✅ All branch types (BEQ, BNE, BLT, BGE, BLTU, BGEU) with pipeline flush
- ✅ Jump instructions (JAL, JALR) with return address and flush
- ✅ RAW hazard detection and stalling
- ✅ Pipeline flush mechanism
- ✅ Complex multi-instruction programs

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
../README.md) - Main documentation and getting started
- [RV32I_COVERAGE.md](RV32I_COVERAGE.md) - Comprehensive RV32I implementation analysis
- [JAL_JALR_IMPLEMENTATION.md](JAL_JALR_IMPLEMENTATION.md) - Jump instruction details
- [PIPELINE_FLUSH.md](PIPELINE_FLUSH.md) - Pipeline flush mechanism
- [tests/functional_tests/](../tests/functional_tests/) - Comprehensive test suite (109 tests)
```assembly
ADDI R1, R0, 100      # R1 = 100
SLTI R2, R1, 200      # R2 = 1 (100 < 200)
BEQ R2, R0, skip      # Skip if R2 == 0 (not taken)
```

## See Also
- [README.md](README.md) - Main documentation
- [tests/test_new_instructions.py](tests/test_new_instructions.py) - Test suite for all instructions
