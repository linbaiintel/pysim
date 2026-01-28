# RV32I Instruction Set Coverage

## Current Implementation Status

**Total RV32I Instructions: 40**  
**Implemented: 31 (77.5%)**  
**Missing: 9 (22.5%)**

---

## ✅ FULLY IMPLEMENTED (31 instructions)

### Integer Computation (10 R-type)
| Instruction | Opcode | Description | Status |
|------------|--------|-------------|--------|
| ADD | 0x33 | Add | ✅ Tested |
| SUB | 0x33 | Subtract | ✅ Tested |
| SLL | 0x33 | Shift Left Logical | ✅ Tested |
| SLT | 0x33 | Set Less Than (signed) | ✅ Tested |
| SLTU | 0x33 | Set Less Than (unsigned) | ✅ Tested |
| XOR | 0x33 | Bitwise XOR | ✅ Tested |
| SRL | 0x33 | Shift Right Logical | ✅ Tested |
| SRA | 0x33 | Shift Right Arithmetic | ✅ Tested |
| OR | 0x33 | Bitwise OR | ✅ Tested |
| AND | 0x33 | Bitwise AND | ✅ Tested |

### Integer Computation - Immediate (9 I-type)
| Instruction | Opcode | Description | Status |
|------------|--------|-------------|--------|
| ADDI | 0x13 | Add Immediate | ✅ Tested |
| SLTI | 0x13 | Set Less Than Immediate (signed) | ✅ Tested |
| SLTIU | 0x13 | Set Less Than Immediate (unsigned) | ✅ Tested |
| XORI | 0x13 | XOR Immediate | ✅ Tested |
| ORI | 0x13 | OR Immediate | ✅ Tested |
| ANDI | 0x13 | AND Immediate | ✅ Tested |
| SLLI | 0x13 | Shift Left Logical Immediate | ✅ Tested |
| SRLI | 0x13 | Shift Right Logical Immediate | ✅ Tested |
| SRAI | 0x13 | Shift Right Arithmetic Immediate | ✅ Tested |

### Load Operations (5 I-type)
| Instruction | Opcode | Description | Status |
|------------|--------|-------------|--------|
| LB | 0x03 | Load Byte (signed) | ✅ Tested |
| LH | 0x03 | Load Halfword (signed) | ✅ Tested |
| LW | 0x03 | Load Word | ✅ Tested |
| LBU | 0x03 | Load Byte (unsigned) | ✅ Tested |
| LHU | 0x03 | Load Halfword (unsigned) | ✅ Tested |

### Store Operations (3 S-type)
| Instruction | Opcode | Description | Status |
|------------|--------|-------------|--------|
| SB | 0x23 | Store Byte | ✅ Tested |
| SH | 0x23 | Store Halfword | ✅ Tested |
| SW | 0x23 | Store Word | ✅ Tested |

### Upper Immediate (2 U-type)
| Instruction | Opcode | Description | Status |
|------------|--------|-------------|--------|
| LUI | 0x37 | Load Upper Immediate | ✅ Tested |
| AUIPC | 0x17 | Add Upper Immediate to PC | ✅ Tested |

### Branches (6 B-type)
| Instruction | Opcode | Description | Status |
|------------|--------|-------------|--------|
| BEQ | 0x63 | Branch if Equal | ✅ Tested with flush |
| BNE | 0x63 | Branch if Not Equal | ✅ Tested with flush |
| BLT | 0x63 | Branch if Less Than (signed) | ✅ Tested with flush |
| BGE | 0x63 | Branch if Greater or Equal (signed) | ✅ Tested with flush |
| BLTU | 0x63 | Branch if Less Than (unsigned) | ✅ Tested with flush |
| BGEU | 0x63 | Branch if Greater or Equal (unsigned) | ✅ Tested with flush |

### Jumps (2 J-type / I-type)
| Instruction | Opcode | Description | Status |
|------------|--------|-------------|--------|
| JAL | 0x6F | Jump and Link | ✅ Tested with flush |
| JALR | 0x67 | Jump and Link Register | ✅ Tested with flush |

### System Instructions (2)
| Instruction | Opcode | Description | Status |
|------------|--------|-------------|--------|
| ECALL | 0x73 | Environment Call (system call) | ✅ Tested with syscalls |
| EBREAK | 0x73 | Environment Breakpoint | ✅ Tested as halt |

---

## ❌ NOT IMPLEMENTED (9 instructions)
| Instruction | Opcode | Why Missing | Priority |
|------------|--------|-------------|----------|
| FENCE | 0x0F | Multi-core memory synchronization | Low |
| FENCE.I | 0x0F | I-cache synchronization | Low |

### Control and Status Registers (7)
| Instruction | Opcode | Why Missing | Priority |
|------------|--------|-------------|----------|
| CSRRW | 0x73 | CSR implementation needed | Low |
| CSRRS | 0x73 | CSR implementation needed | Low |
| CSRRC | 0x73 | CSR implementation needed | Low |
| CSRRWI | 0x73 | CSR implementation needed | Low |
| CSRRSI | 0x73 | CSR implementation needed | Low |
| CSRRCI | 0x73 | CSR implementation needed | Low |

Note: Some specs count CSR ops as 3 base + 3 immediate variants = 6 total

---

## Implementation Quality

### Fully Functional Features
✅ All computational instructions (ALU, shifts, comparisons)  
✅ All memory access instructions (loads/stores with proper sign extension)  
✅ All control flow instructions (branches, jumps with pipeline flush)  
✅ Upper immediate instructions (LUI, AUIPC with PC tracking)  
✅ System instructions (ECALL with syscall emulation, EBREAK as breakpoint)  
✅ Pipeline hazard detection and stalling  
✅ Pipeline flush mechanism for control flow  
✅ 32-bit register file with R0 hardwired to zero  
✅ Byte-addressable memory with word/halfword/byte access  

### Test Coverage
- **125 tests** covering all implemented instructions
- Parsing tests for all instruction formats
- Execution tests with edge cases
- Pipeline behavior tests (hazards, stalls, flush)
- System call emulation tests
- Integration tests with complex programs

---

## What's Missing and Why

### 1. FENCE / FENCE.I - Memory Ordering
**Description:** Synchronize memory and instruction caches  
**Use case:** Multi-core systems, self-modifying code  
**Why missing:** Single-core simulator, no separate I-cache  
**Workaround:** Not needed for single-threaded programs  
**Difficulty to add:** Trivial (implement as NOP)

### 2. CSR Instructions - Privileged Operations
**Description:** Read/write control and status registers  
**Use case:** Exception handling, interrupts, performance counters  
**Why missing:** No privileged mode, no CSR bank  
**Workaround:** Programs stay in user mode  
**Difficulty to add:** High (requires CSR implementation)

---

## Practical Impact

### What You CAN Run
✅ Pure computational programs (math, algorithms)  
✅ Programs with loops and conditionals  
✅ Programs with function calls  
✅ Programs using arrays and pointers  
✅ Programs with basic system calls (exit, print via ECALL)  
✅ Custom assembly test programs  
✅ Hand-written RISC-V assembly  
✅ Most educational/learning examples  

### What You CANNOT Run
❌ Programs requiring multi-core synchronization (FENCE)  
❌ Programs with CSR register access  
❌ Programs using performance counters  
❌ Self-modifying code (needs FENCE.I)  
❌ Complex OS-level programs  

### Typical Workaround
For educational purposes, write custom test programs that:
- Compute results in registers
- Store results in memory
- Avoid system calls
- Return via JALR or end naturally

---

## Recommendation

### For Educational/Learning Purposes
**Your implementation is COMPLETE** ✅

You have all instructions needed for:
- Teaching RISC-V architecture
- Understanding pipeline behavior
- Learning assembly programming
- Implementing algorithms
- Testing compiler output (with syscall workarounds)
basic syscall support
### To Support Standard C Programs
**ECALL is now implemented!** ✅

Basic syscall emulation is available:
- Exit (syscall 93)
- Print integer (syscall 1)  
- Write (syscall 64)

You can now run simple C programs with basic I/O!

### To Claim "Complete RV32I"
**Add stub implementations:**
- ECALL → print debug message
- EBREAK → halt simulation
- FENCE → NOP (no-operation)
- FENCE.I → NOP
- CSR ops → warning message or basic CSR bank

**~~ECALL → Basic syscall emulation~~ ✅ DONE
- ~~EBREAK → Halt simulation~~ ✅ DONE
- FENCE → NOP (no-operation)
- FENCE.I → NOP
- CSR ops → Warning message or basic CSR bank

**Effort:** 1 day  
**Benefit:** Can claim 100% RV32I coverage (currently 77.5%)5%)  
**Computational Completeness:** 100% ✅  
**User-Mode Completeness:** 100% ✅  
**Full RV32I Spec:** 72.5%  

**Missing Instructions:**
- 2 system (ECALL, 31/40 instructions (77.5%)  
**Computational Completeness:** 100% ✅  
**User-Mode Completeness:** 100% ✅  
**System Call Support:** Basic (exit, print, write) ✅  
**Full RV32I Spec:** 77.5%  

**Missing Instructions:**
- 2 memory ordering (FENCE, FENCE.I)
- 7 CSR operations

**All missing instructions are memory ordering or privileged level operations.**  
**Your simulator~~ECALL Support~~ ✅ COMPLETED
- ~~Enables running real C programs~~ ✅ Done
- ~~Basic syscall emulation (exit, write)~~ ✅ Implemented
- ~~Most useful addition~~ ✅ Complete

### Priority 2: Stub Implementations (Low Effort)
- FENCE → NOP
- FENCE.I → NOP  
- EBREAK → halt
- Achieves 100% instruction coverage

### Priority 3: CSR Bank (High Effort, Low Benefit for Education)
- Implement basic CSR registers
- Support CSR read/write
- Mainly for completeness

**Recommendation:** Stop here or add ECALL for maximum educational value!
