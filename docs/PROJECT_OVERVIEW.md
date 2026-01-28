# RISC-V 5-Stage Pipeline Simulator - Project Overview

## Quick Facts

**Project Type:** Cycle-accurate RISC-V pipeline simulator  
**Language:** Python 3.12+  
**Framework:** SimPy 4.1.1 (discrete-event simulation)  
**RV32I Coverage:** 29/40 instructions (72.5%)  
**Test Suite:** 109 tests, all passing  
**Status:** ✅ Complete for user-mode computational programs

---

## What This Simulator Does

### Core Functionality
1. **5-Stage Pipeline**: Fetch → Decode → Execute → Memory → WriteBack
2. **Hazard Detection**: Automatically detects RAW (Read-After-Write) dependencies
3. **Stall Insertion**: Inserts pipeline bubbles when hazards are detected
4. **Pipeline Flush**: Handles control flow changes (branches, jumps)
5. **Cycle-Accurate**: Tracks exact cycle counts, stalls, and flushes

### What You Can Run
✅ Pure computational programs (algorithms, math)  
✅ Programs with loops and conditionals  
✅ Function calls (JAL/JALR)  
✅ Array and pointer manipulation  
✅ Hand-written RISC-V assembly  
✅ Educational/learning examples  

### What You Cannot Run
❌ Programs with system calls (printf, exit)  
❌ Programs with exceptions/interrupts  
❌ Multi-threaded programs  
❌ Programs requiring CSR access  

**Reason:** Missing 11 system/privileged level instructions (ECALL, EBREAK, FENCE, FENCE.I, CSR operations)

---

## Architecture Overview

### Pipeline Stages

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  Fetch  │ → │ Decode  │ → │ Execute │ → │ Memory  │ → │WriteBack│
└─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
     │             │              │             │             │
     └─────────────┴──────────────┴─────────────┴─────────────┘
                        Stage Buffers
```

**Stage Responsibilities:**
- **Fetch**: Read instruction from memory
- **Decode**: Parse instruction, check for hazards
- **Execute**: Perform ALU operations, compute addresses, evaluate branches
- **Memory**: Load/store data, pass through ALU results
- **WriteBack**: Write results to register file

### Hazard Detection

**RAW (Read-After-Write) Hazards:**
```
ADD R1, R2, R3    # Produces R1
SUB R4, R1, R5    # Consumes R1 → HAZARD!
```

**Detection Logic:**
1. In Decode stage, check if source registers (rs1, rs2) are being produced by instructions in Execute or Memory stages
2. If hazard detected, insert bubbles (stalls) until producer reaches WriteBack
3. Stall duration: 3 cycles for EXE stage, 2 cycles for MEM stage

### Pipeline Flush

**When:** Control flow changes (jumps, taken branches)  
**Why:** Instructions after jump/branch were fetched from wrong PC  
**How:** Convert all Fetch and Decode stage instructions to bubbles

**Example:**
```
JAL R1, func      # Jump to func, flush IF and ID stages
<wrong inst>      # This becomes bubble
<wrong inst>      # This becomes bubble
func: ADD R2, ...  # First correct instruction
```

---

## Instruction Set Coverage

### Fully Implemented (29 instructions)

| Category | Count | Instructions |
|----------|-------|--------------|
| **R-type ALU** | 10 | ADD, SUB, AND, OR, XOR, SLT, SLTU, SLL, SRL, SRA |
| **I-type ALU** | 9 | ADDI, ANDI, ORI, XORI, SLTI, SLTIU, SLLI, SRLI, SRAI |
| **Load** | 5 | LW, LH, LB, LHU, LBU |
| **Store** | 3 | SW, SH, SB |
| **Upper Immediate** | 2 | LUI, AUIPC |
| **Branch** | 6 | BEQ, BNE, BLT, BGE, BLTU, BGEU |
| **Jump** | 2 | JAL, JALR |

### Not Implemented (11 instructions)

| Category | Count | Instructions | Reason |
|----------|-------|--------------|--------|
| **System** | 2 | ECALL, EBREAK | Requires OS/debugger |
| **Memory Ordering** | 2 | FENCE, FENCE.I | Not needed for single-core |
| **CSR** | 7 | CSRRW, CSRRS, CSRRC, CSRRWI, CSRRSI, CSRRCI | Privileged operations |

See [RV32I_COVERAGE.md](RV32I_COVERAGE.md) for detailed analysis.

---

## Components

### Core Modules

#### 1. `pipeline.py` - Pipeline Controller
**Responsibilities:**
- Orchestrates all 5 pipeline stages
- Manages stage buffers
- Implements hazard detection logic
- Handles pipeline flush
- Tracks performance metrics (cycles, stalls, flushes)

**Key Classes:**
- `Pipeline`: Main pipeline controller with SimPy processes for each stage
- `FetchStage`, `DecodeStage`, `ExecuteStage`, `MemoryStage`, `WriteBackStage`

#### 2. `instruction.py` - Instruction Representation
**Responsibilities:**
- Parse instruction strings into structured format
- Extract opcode, registers, immediates
- Identify instruction type (R/I/S/B/U/J)
- Track jump/branch properties

**Key Classes:**
- `Instruction`: Represents a RISC-V instruction with all fields

#### 3. `exe.py` - Execution Unit
**Responsibilities:**
- Execute all ALU operations
- Perform comparisons for branches
- Calculate jump targets
- Handle signed/unsigned arithmetic
- Implement shift operations

**Key Functions:**
- `execute_add()`, `execute_sub()`, `execute_and()`, etc.
- `execute_branch()` - Branch condition evaluation
- `execute_jal()`, `execute_jalr()` - Jump execution

#### 4. `register_file.py` - Register File
**Responsibilities:**
- Store 32 general-purpose registers
- Enforce R0 = 0 (writes to R0 are ignored)
- Track PC (Program Counter)

**Key Features:**
- 32-bit registers (R0-R31)
- Thread-safe read/write
- PC tracking for jumps/branches

#### 5. `memory.py` - Data Memory
**Responsibilities:**
- Byte-addressable memory (4KB default)
- Load/store word, halfword, byte
- Sign extension (LH, LB) and zero extension (LHU, LBU)

**Key Features:**
- 32-bit word access (4-byte aligned)
- 16-bit halfword access (2-byte aligned)
- 8-bit byte access

#### 6. `riscv.py` - High-Level Processor Interface
**Responsibilities:**
- Convenient API for running programs
- Initialize registers and memory
- Execute programs and return results

**Key Classes:**
- `RISCVProcessor`: High-level processor wrapper

### Utilities

#### 7. `utils/elf_loader.py` - ELF Binary Loader
**Responsibilities:**
- Load RISC-V ELF binaries
- Decode machine code to instruction objects
- Extract program sections (text, data)

**Key Functions:**
- `load_elf()` - Load ELF binary
- `decode_instruction()` - Decode 32-bit instruction

#### 8. `utils/riscv_test_utils.py` - Test Utilities
**Responsibilities:**
- Extract test patterns from official RISC-V tests
- Validate test results
- Generate test reports

---

## Test Suite Structure

### Functional Tests (109 tests)

**Location:** `tests/functional_tests/`

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_instruction_types.py` | 20 | R-type and basic I-type operations |
| `test_immediate.py` | 15 | Immediate operations edge cases |
| `test_comparison.py` | 10 | SLT/SLTU signed/unsigned comparisons |
| `test_shift.py` | 12 | All shift operations (SLL/SRL/SRA/SLLI/SRLI/SRAI) |
| `test_load_store.py` | 18 | Load/store variants with sign/zero extension |
| `test_upper_immediate.py` | 6 | LUI and AUIPC operations |
| `test_branch.py` | 12 | All branch types with flush |
| `test_jump.py` | 12 | JAL/JALR with return address and flush |
| `test_flush.py` | 9 | Pipeline flush mechanism |
| `test_pipeline.py` | 8 | Pipeline behavior and hazards |
| `test_edge_cases.py` | 5 | Corner cases and edge conditions |
| `test_complex_programs.py` | 2 | Multi-instruction programs |

**Run all tests:**
```bash
python -m unittest discover tests/functional_tests -v
# Output: Ran 109 tests in 0.049s - OK
```

---

## Performance Metrics

### Tracked Metrics

1. **Total Cycles**: Total simulation time
2. **Instructions Completed**: Number of instructions that reached WriteBack
3. **Stall Count**: Number of pipeline stalls due to hazards
4. **Flush Count**: Number of pipeline flushes due to control flow
5. **CPI (Cycles Per Instruction)**: Average cycles per instruction
6. **IPC (Instructions Per Cycle)**: Throughput metric

### Expected Performance

**Without hazards or control flow:**
- CPI ≈ 1.8-2.0 (includes pipeline fill time)
- IPC ≈ 0.5-0.55

**With RAW hazards:**
- CPI increases by 2-3 cycles per hazard
- Each hazard in EXE: +3 cycles
- Each hazard in MEM: +2 cycles

**With branches/jumps:**
- Each flush: +2 cycles (discard IF and ID stage instructions)
- Flush count tracked separately

---

## Development Workflow

### Adding New Instructions

1. **Update `instruction.py`:** Add instruction parsing
2. **Update `exe.py`:** Add execution logic
3. **Update `elf_loader.py`:** Add decoding for machine code
4. **Add tests:** Create comprehensive test cases
5. **Update docs:** Document new instruction

### Running Tests

```bash
# All tests
python -m unittest discover tests/functional_tests -v

# Specific category
python -m unittest tests.functional_tests.test_jump -v

# Single test
python -m unittest tests.functional_tests.test_jump.TestJump.test_jal_basic -v

# With scripts
./scripts/run_all_tests.sh
```

### Debugging Pipeline

**Enable verbose output:**
```python
# In pipeline.py, uncomment debug prints
self.verbose = True
```

**Visualize pipeline execution:**
```bash
python tests/visualization.py
```

---

## Known Limitations

### 1. No Data Forwarding
**Impact:** All hazards require full stalls (2-3 cycles)  
**Solution:** Implement forwarding paths (EX→EX, MEM→EX, WB→EX)  
**Benefit:** Reduce most hazards to 0 cycles, LOAD-use to 1 cycle

### 2. No Branch Prediction
**Impact:** All control flow changes incur flush penalty  
**Solution:** Implement static or dynamic branch prediction  
**Benefit:** Reduce flush penalty for correctly predicted branches

### 3. No Out-of-Order Execution
**Impact:** Pipeline stalls on every dependency  
**Solution:** Implement instruction window, reservation stations, register renaming  
**Benefit:** Hide latencies, increase ILP (Instruction-Level Parallelism)

### 4. No System Support
**Impact:** Cannot run standard C programs with printf/exit  
**Solution:** Implement basic syscall emulation (ECALL with syscall number in register)  
**Benefit:** Run real compiled programs

---

## Future Enhancements

### Priority 1: ECALL for System Calls
**Effort:** Medium (1-2 days)  
**Benefit:** High - enables running C programs  
**Implementation:**
```python
def execute_ecall(regs):
    syscall_num = regs['R17']  # RISC-V syscall convention
    if syscall_num == 93:  # exit
        return {'action': 'exit', 'code': regs['R10']}
    elif syscall_num == 64:  # write
        return {'action': 'write', 'fd': regs['R10'], 
                'buf': regs['R11'], 'len': regs['R12']}
```

### Priority 2: Data Forwarding
**Effort:** High (3-5 days)  
**Benefit:** High - dramatic performance improvement  
**Implementation:** Add forwarding logic in Execute stage

### Priority 3: Branch Prediction
**Effort:** Medium (2-3 days)  
**Benefit:** Medium - reduces control flow penalties  
**Implementation:** Simple 2-bit saturating counter per branch

### Priority 4: Stub System Instructions
**Effort:** Low (1 day)  
**Benefit:** Low - achieves 100% RV32I coverage  
**Implementation:** FENCE/FENCE.I as NOPs, EBREAK as halt

---

## Documentation Index

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Main documentation and getting started |
| [INSTRUCTION_SET.md](INSTRUCTION_SET.md) | Instruction reference with examples |
| [RV32I_COVERAGE.md](RV32I_COVERAGE.md) | Complete RV32I analysis (29/40) |
| [JAL_JALR_IMPLEMENTATION.md](JAL_JALR_IMPLEMENTATION.md) | Jump instruction details |
| [PIPELINE_FLUSH.md](PIPELINE_FLUSH.md) | Pipeline flush mechanism |
| [RISCV_TESTS_GUIDE.md](RISCV_TESTS_GUIDE.md) | Official RISC-V test suite integration |
| [tests/README.md](../tests/README.md) | Test suite documentation |

---

## Quick Start

### Installation
```bash
# Clone repository
git clone <repo-url>
cd pysim

# Create virtual environment
python3 -m venv pysim-venv
source pysim-venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run Example
```python
from riscv import RISCVProcessor

# Create processor
proc = RISCVProcessor()

# Initialize state
proc.initialize_registers({'R2': 10, 'R3': 20})

# Execute program
program = [
    "ADD R1, R2, R3",    # R1 = 10 + 20 = 30
    "SLLI R4, R1, 2",    # R4 = 30 << 2 = 120
    "SW R4, 100(R0)"     # mem[100] = 120
]

exec_info = proc.execute(program)
print(f"Completed in {exec_info['total_cycles']} cycles")
print(f"CPI: {exec_info['cpi']:.2f}")
```

### Run Tests
```bash
# All tests (109)
python -m unittest discover tests/functional_tests -v

# Specific category
python -m unittest tests.functional_tests.test_jump -v
```

---

## Contributing

### Code Style
- PEP 8 compliant
- Type hints where appropriate
- Comprehensive docstrings

### Testing Requirements
- All new instructions must have tests
- Minimum 90% code coverage
- Test edge cases and corner cases

### Documentation Requirements
- Update INSTRUCTION_SET.md for new instructions
- Add examples to README.md
- Update RV32I_COVERAGE.md

---

## License

See [LICENSE](../LICENSE) for details.

---

## References

- [RISC-V ISA Specification](https://riscv.org/technical/specifications/)
- [Computer Architecture: A Quantitative Approach](https://www.elsevier.com/books/computer-architecture/hennessy/978-0-12-811905-1) (Hennessy & Patterson)
- [SimPy Documentation](https://simpy.readthedocs.io/)
- [RISC-V Official Test Suite](https://github.com/riscv/riscv-tests)

---

**Last Updated:** January 28, 2026  
**Version:** 1.0  
**Status:** Production Ready (for computational programs)
