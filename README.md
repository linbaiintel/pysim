# RISC-V 5-Stage Pipeline Simulator

A cycle-accurate simulation of a RISC-V 5-stage pipeline using SimPy, with comprehensive hazard detection, pipeline flush mechanism, and **100% complete RV32I implementation (40/40 instructions)**.

## Overview
This simulator implements a classic 5-stage in-order pipeline:
- **IF** (Fetch): Fetch instruction from memory
- **ID** (Decode): Decode instruction and read registers
- **EXE** (Execute): Perform ALU operations, compute addresses, evaluate branches
- **MEM** (Memory): Access data memory for loads/stores
- **WB** (WriteBack): Write result to register file

**Key Features:**
- **RAW Hazard Detection**: Detects read-after-write dependencies and inserts stalls
- **Pipeline Flush**: Handles control flow changes (branches, jumps) by flushing incorrect instructions
- **RV32I Support**: 40/40 instructions - **100% COMPLETE RV32I implementation** \u2705
- **Cycle-Accurate**: Tracks exact cycle counts, stalls, and flushes for performance analysis

## Setup

### Create and Activate Virtual Environment
```bash
python3 -m venv pysim-venv
source pysim-venv/bin/activate  # On Windows: pysim-venv\Scripts\activate
pip install -r requirements.txt
```

**Dependencies:**
- `simpy==4.1.1` - Discrete event simulation framework
- `pyelftools==0.32` - ELF binary parsing (for RISC-V test validation)

## Running the Simulator

### Basic Usage
```bash
# Run processor examples (main entry point)
python riscv.py

# Or run pipeline directly (low-level)
python pipeline.py
```

### Using the Processor API
```python
from riscv import RISCVProcessor, run_program

# Create and configure processor
processor = RISCVProcessor()
processor.initialize_registers({'R2': 10, 'R3': 20})
processor.initialize_memory({100: 42})

# Execute program
program = ["ADD R1, R2, R3", "STORE R1, 100(R0)"]
exec_info = processor.execute(program)

# Or use convenience function
exec_info, regs, mem = run_program(
    instructions=program,
    initial_registers={'R2': 10, 'R3': 20},
    initial_memory={100: 42}
)
```

### Visualize Pipeline Execution
```bash
# See pipeline diagrams with stage occupancy
python tests/visualization.py

# Or create custom visualization
python sandbox/vis_pipeline.py
```

### Run Test Suite
```bash
# Run all functional tests (205 tests)
python -m unittest discover tests/functional_tests -v

# Run specific test modules
python -m unittest tests.functional_tests.test_branch -v
python -m unittest tests.functional_tests.test_jump -v
python -m unittest tests.functional_tests.test_flush -v
python -m unittest tests.functional_tests.test_load_store -v
python -m unittest tests.functional_tests.test_system -v
python -m unittest tests.functional_tests.test_fence -v
python -m unittest tests.functional_tests.test_csr -v

# Or use convenience scripts
./scripts/run_all_tests.sh
./scripts/run_functional_tests.sh
```

## Test Categories
**166 Total Tests**  
**Coverage by category:**

#### Arithmetic & Logic (test_instruction_types.py, test_comparison.py, test_immediate.py, test_shift.py)
- R-type operations (ADD, SUB, AND, OR, XOR, SLT, SLTU, SLL, SRL, SRA)
- I-type immediate operations (ADDI, ANDI, ORI, XORI, SLTI, SLTIU, SLLI, SRLI, SRAI)
- Comparison operations and edge cases
- Shift operations (logical and arithmetic)

#### Memory Operations (test_load_store.py)
- Load variants: LW, LH, LB, LHU, LBU (with sign/zero extension)
- Store variants: SW, SH, SB
- Unaligned access, edge addresses, hazard detection

#### Control Flow (test_branch.py, test_jump.py, test_flush.py)
- Branch instructions: BEQ, BNE, BLT, BGE, BLTU, BGEU
- Jump instructions: JAL, JALR (with return address calculation)
- Pipeline flush on taken branches and jumps
- No flush on not-taken branches

#### System Instructions (test_system.py)
- ECALL (environment call) with syscall emulation
- EBREAK (breakpoint) as halt signal

#### Memory Ordering (test_fence.py)
- FENCE (memory ordering) as NOP
- FENCE.I (instruction cache fence) as NOP

#### Control and Status Registers (test_csr.py)
- CSRRW, CSRRS, CSRRC (register variants)
- CSRRWI, CSRRSI, CSRRCI (immediate variants)
- CSR bank with standard RISC-V addresses
- Read-only CSR protection
- Atomic read-modify-write operations

#### Upper Immediate (test_upper_immediate.py)
- LUI (Load Upper Immediate)
- AUIPC (Add Upper Immediate to PC)

#### Pipeline Behavior (test_pipeline.py, test_edge_cases.py)
- RAW hazard detection and stalling
- Pipeline flush mechanism
- Bubble insertion
- Long dependency chains
- CPI/IPC calculations

**Run all tests:**
```bash
python -m unittest discover tests/functional_tests -v
# Output: Ran 205 tests in ~0.07s
```

## Pipeline Visualization

### View Execution Diagram
```bash
python tests/visualization.py
```

**Example output:**
```
Pipeline Execution Diagram:
====================================================
          | t0 | t1 | t2  | t3  | t4  | t5  | t6 |
----------------------------------------------------
Inst 1    | IF | ID | EXE | MEM | WB  |     |    |
Inst 2    |    | IF |     |     |     | ID  | EXE|
====================================================
```

Empty cells show stalls/bubbles inserted for hazards.

### Custom Visualization
Create your own visualization in `sandbox/`:
```python
from tests.visualization import draw_pipeline_diagram

draw_pipeline_diagram([
    "ADD R1, R2, R3",
    "SUB R4, R1, R5"
])
```

## Architecture Details

### Pipeline Stages
1. **Fetch**: Read instruction, store in fetch_to_decode buffer
2. **Decode**: Parse instruction, check for hazards
3. **Execute**: Perform computation
4. **Memory**: Access memory (LOAD/STORE)
5. **WriteBack**: Write result to register file

### Hazard Detection & Pipeline Control
- **RAW Detection**: Checks Execute and Memory stages for read-after-write hazards
- **Stall Insertion**: Inser31/40 RV32I)
- **R-type (10)**: ADD, SUB, AND, OR, XOR, SLT, SLTU, SLL, SRL, SRA
- **I-type ALU (9)**: ADDI, ANDI, ORI, XORI, SLTI, SLTIU, SLLI, SRLI, SRAI
- **Load (5)**: LW, LH, LB, LHU, LBU
- **Store (3)**: SW, SH, SB
- **Upper (2)**: LUI, AUIPC
- **Branch (6)**: BEQ, BNE, BLT, BGE, BLTU, BGEU
- **Jump (2)**: JAL, JALR
- **System (2)**: ECALL, EBREAKB, LHU, LBU
- **Store (3)**: SW, SH, SB
- **Upper (2)**: LUI, AUIPC
- **Branch (6)**: BEQ, BNE, BLT, BGE, BLTU, BGEU
- **Jump (2)**: JAL, JALR

See [docs/RV32I_COVERAGE.md](docs/RV32I_COVERAGE.md) for complete instruction coverage and missing system instructions.

## Testing Strategy

### Calculate Expected Cycles
```
Expected cycles = (# instructions) + 4 + (# stalls)
```
- 4 = pipeline depth minus 1 (initial fill time)

### Verify Stall Count
For each RAW hazard:
- **Hazard in Execute stage**: 3 cycle stall
- **Hazard in Memory stage**: 2 cycle stall

**Formula:**
```
Total stalls = Σ (distance_to_writeback for each hazard)
```

## Common Issues and Debugging

### Issue 1: Missing Hazard Detection
**Symptom:** Stall count = 0 when dependencies exist
**Test:** Run back-to-back dependent instructions
**Fix:** Verify `check_hazard()` examines Execute and Memory stages

### Issue 2: Over-Stalling
**Symptom:** Too many stalls for independent instructions
**Test:** Run independent instructions, expect 0 stalls
**Fix:** Ensure hazard detection doesn't check WriteBack stage

### Issue 3: Wrong Pipeline State Tracking
**Symptom:** Hazards detected at wrong cycles
**Test:** Add debug prints in `check_hazard()`
**Fix:** Update pipeline_state at correct time (when entering stage)

### Issue 4: Instruction Loss
**Symptom:** Fewer instructions complete than submitted
**Test:** Count completed instructions
**Fix:** Check all buffers are properly connected

### Issue 5: Out-of-Order Completion
**Symptom:** Instructions complete in wrong order
**Test:** Compare result order to input order
**Fix:** Ensure in-order writeback

## Performance Metrics

### Key Metrics
```
CPI = Total Cycles / Instructions Completed
IPC = Instructions Completed / Total Cycles
Stall Rate = Stalls / Instructions
```

### Expected Values (No Forwarding)
- **Independent instructions**: CPI ≈ 2.0-2.5, IPC ≈ 0.4-0.5
- **With dependencies**: CPI increases with stalls
- **Maximum IPC**: 1.0 (theoretical limit for in-order pipeline)

### Correctness Metrics
- **Completion rate**: 100% (all instructions complete)
- **Order preservation**: 100% (in-order completion)
- **False hazard rate**: 0% (no unnecessary stalls)

## Project Structure

```
pysim/
├── riscv.py                     # Main processor interface (start here!)
├── pipeline.py                  # 5-stage pipeline with hazard detection & flush
├── instruction.py               # Instruction parsing and representation
├── register_file.py             # 32-register file with R0=0 enforcement
├── memory.py                    # Byte-addressable memory (4KB default)
├── exe.py                       # Execution unit (ALU, branches, jumps)
├── requirements.txt             # Python dependencies (simpy, pyelftools)
├── README.md                    # This file (main documentation)
├── .gitignore                   # Git ignore rules
├── .gitmodules                  # Git submodule configuration
│
├── docs/                        # Documentation
│   ├── README.md                # Documentation index and navigation
│   ├── INSTRUCTION_SET.md       # Instruction reference with examples
│   ├── RV32I_COVERAGE.md        # Complete RV32I implementation status (29/40)
│   ├── PROJECT_OVERVIEW.md      # Architecture and design documentation
│   ├── FILE_INDEX.md            # Complete file listing and navigation
│   ├── JAL_JALR_IMPLEMENTATION.md  # Jump instruction implementation details
│   ├── PIPELINE_FLUSH.md        # Pipeline flush mechanism documentation
│   ├── RISCV_TESTS_GUIDE.md     # Guide for official RISC-V test suite
│   └── UPDATE_SUMMARY.md        # Recent documentation updates
│
├── 3rd_party/                   # Third-party dependencies
│   └── riscv-tests/             # Official RISC-V test suite (git submodule)
│
├── utils/                       # Utility modules
│   ├── __init__.py
│   ├── elf_loader.py            # ELF binary loader & RISC-V decoder
│   ├── riscv_test_utils.py      # Test pattern extraction utilities
│   └── README.md                # Utils documentation
│
├── scripts/                     # Convenience scripts
│   ├── run_all_tests.sh         # Run all tests
│   ├── run_functional_tests.sh  # Run functional tests only
│   ├── run_unit_tests.sh        # Run unit tests only
│   └── README.md                # Scripts documentation
│
├── sandbox/                     # Experimental/development scripts
│   ├── demo_flush.py            # Pipeline flush demonstrations
│   ├── demo_inst.py             # Instruction execution demos
│   ├── demo_jump.py             # Jump instruction demos
│   └── vis_pipeline.py          # Custom visualization examples
│
└── tests/                       # Test suite (109 tests)
    ├── __init__.py
    ├── test_all.py              # Legacy test runner
    ├── run_tests.py             # Modern test runner
    ├── visualization.py         # Pipeline execution visualization
    ├── README.md                # Test documentation
    ├── README_TESTS.md          # Detailed test guide
    └── functional_tests/        # Comprehensive functional tests (109 tests)
        ├── __init__.py
        ├── README.md                   # Functional tests documentation
        ├── test_instruction_types.py   # R-type and I-type tests
        ├── test_immediate.py           # Immediate operation tests
        ├── test_comparison.py          # SLT/SLTU tests
        ├── test_shift.py               # Shift operation tests
        ├── test_system.py              # System instructions (ECALL/EBREAK) - 16 tests
        ├── test_load_store.py          # Load/store variants (LW/LH/LB/LHU/LBU, SW/SH/SB)
        ├── test_upper_immediate.py     # LUI and AUIPC tests
        ├── test_branch.py              # Branch instruction tests (BEQ/BNE/BLT/BGE/BLTU/BGEU)
        ├── test_jump.py                # Jump tests (JAL/JALR) - 12 tests
        ├── test_flush.py               # Pipeline flush mechanism - 9 tests
        ├── test_pipeline.py            # Pipeline behavior tests
        ├── test_edge_cases.py          # Edge cases and corner cases
        ├── test_complex_programs.py    # Multi-instruction programs
        ├── riscv_test_adapter.py       # Adapter for official RISC-V tests
        └── run_riscv_tests.py          # Official test suite runner
```

**Key Directories:**
- **Core Simulator**: Root-level .py files (riscv.py, pipeline.py, instruction.py, csr.py, etc.)
- **docs/**: Comprehensive documentation including RV32I coverage analysis
- **utils/**: ELF loading and RISC-V instruction decoding utilities
- **tests/functional_tests/**: 166 comprehensive tests covering all implemented instructions
- **scripts/**: Shell scripts for convenient test execution
- **3rd_party/**: Official RISC-V test suite (git submodule)

## Testing Checklist

**Core Functionality** (205/205 tests passing)
- [x] RAW hazards are detected and stalled
- [x] Independent instructions don't stall
- [x] Instruction order is preserved (in-order pipeline)
- [x] All 5 stages are executed for each instruction
- [x] Bubbles are inserted during stalls
- [x] Pipeline state is tracked correctly

**Instruction Coverage** (40/40 = 100%)
- [x] R-type operations (ADD, SUB, AND, OR, XOR, SLT, SLTU, SLL, SRL, SRA)
- [x] I-type operations (ADDI, ANDI, ORI, XORI, SLTI, SLTIU, SLLI, SRLI, SRAI)
- [x] Load variants (LW, LH, LB, LHU, LBU) with sign/zero extension
- [x] Store variants (SW, SH, SB)
- [x] Upper immediate (LUI, AUIPC)
- [x] Branch instructions (BEQ, BNE, BLT, BGE, BLTU, BGEU)
- [x] Jump instructions (JAL, JALR) with return address calculation
- [x] System instructions (ECALL, EBREAK) with syscall emulation
- [x] Memory ordering (FENCE, FENCE.I) as NOPs
- [x] CSR instructions (CSRRW, CSRRS, CSRRC, CSRRWI, CSRRSI, CSRRCI)

**Pipeline Control**
- [x] Pipeline flush on jumps (JAL, JALR)
- [x] Pipeline flush on taken branches
- [x] No flush on not-taken branches
- [x] Flush converts Decode instructions to bubbles
- [x] Flush count tracked for performance metrics

**Edge Cases**
- [x] Single instruction execution
- [x] Long dependency chains
- [x] STORE instructions (no destination register)
- [x] Jump to register with LSB clearing (JALR)
- [x] Negative offsets and edge addresses
- [x] R0 hardwired to zero
- [x] System calls with various arguments
- [x] CSR read-only protection and atomic operations
- [x] CPI/IPC metrics calculated correctly

## Implementation Status

**\ud83c\udf89 100% RV32I COMPLETE (40/40 instructions)** \u2705

- All 40 RV32I base integer instructions implemented
- RAW hazard detection with stall insertion
- Full CSR bank with standard RISC-V addresses
- Cycle-accurate simulation with performance metrics
- Comprehensive test suite (205 tests)
- All load/store variants with proper sign/zero extension
- Jump instructions (JAL, JALR) with return address handling
- All branch instructions with condition evaluation
- System instructions (ECALL, EBREAK, MRET) with trap/exception support
- Memory ordering (FENCE, FENCE.I) implemented as NOPs
- Complete CSR support with atomic read-modify-write operations
- Full trap/interrupt mechanism with exception and interrupt handling

### \ud83c\udf89 RV32I Implementation: COMPLETE

**All 40 instructions of the RISC-V RV32I base integer instruction set are now fully implemented and tested!**

See [docs/RV32I_COVERAGE.md](docs/RV32I_COVERAGE.md) for complete implementation details.

### \ud83d\ude80 Future Enhancements

**Data Forwarding (Reduce Stalls)**
- EX \u2192 EX forwarding: 0 cycle stall instead of 3
- MEM \u2192 EX forwarding: 0 cycle stall instead of 2
- WB \u2192 EX forwarding: 0 cycle stall
- LOAD-use hazard: 1 cycle stall instead of 2-3

**Branch Prediction**
- Static prediction (always taken/not taken)
- Dynamic prediction (branch history table)
- Branch target buffer (BTB)
- Return address stack (RAS) for function calls

**Out-of-Order Execution**
- Instruction window and reservation stations
- Register renaming (WAW/WAR hazard elimination)
- Reorder buffer for in-order commit
- Speculative execution

**System Support**
- Basic syscall emulation (exit, write) for running C programs
- CSR register bank for performance counters
- Exception and interrupt handling

## Quick Reference

### Run Everything
```bash
# Install required python library
pip install -r requirements.txt

# Run processor examples (recommended)
python riscv.py

# Run all tests
python -m unittest discover tests -v

# Visualize pipeline execution
python tests/visualization.py

# Custom visualization
python sandbox/vis_pipeline.py
```

### Debugging Tips
1. Add print statements in `check_hazard()` to see what's being checked
2. Print `pipeline_state` at each cycle
3. Use smaller test cases (2-3 instructions)
4. Verify manually with paper and pencil for simple cases
5. Compare trace output with textbook pipeline diagrams
6. Use `draw_pipeline_diagram()` to visualize execution

## References
- Computer Architecture: A Quantitative Approach (Hennessy & Patterson)
- RISC-V ISA Specification
- SimPy Documentation: https://simpy.readthedocs.io/
