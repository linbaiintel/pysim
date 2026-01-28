# RISC-V 5-Stage Pipeline Simulator

A time-stepped simulation of a RISC-V 5-stage pipeline using SimPy, with hazard detection and stall insertion.

## Overview
This simulator implements a classic 5-stage in-order pipeline:
- **IF** (Fetch): Fetch instruction from memory
- **ID** (Decode): Decode instruction and read registers
- **EXE** (Execute): Perform ALU operations
- **MEM** (Memory): Access data memory
- **WB** (WriteBack): Write result to register

The simulator detects **RAW (Read After Write)** hazards and inserts stalls/bubbles to maintain correctness.

## Setup

### Create and Activate Virtual Environment
```bash
python3 -m venv pysim-venv
source pysim-venv/bin/activate  # On Windows: pysim-venv\Scripts\activate
pip install simpy
```

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
# Run all tests
python -m unittest discover tests -v

# Run specific test module
python -m unittest tests.test_correctness
python -m unittest tests.test_hazards
python -m unittest tests.test_edge_cases

# Or use the test runner
python tests/run_tests.py
```

## Test Categories

### 1. Functional Correctness Tests
**What to verify:**
- All instructions complete execution
- Instructions complete in program order (in-order pipeline)
- No instructions are lost or duplicated
- Register dependencies are respected

**Run tests:**
```bash
python -m unittest tests.test_correctness -v
```

**Key tests:**
- ✅ Back-to-back dependencies
- ✅ Independent instructions
- ✅ LOAD-use hazards
- ✅ Mixed dependencies
- ✅ Instruction parsing (R-type, LOAD, STORE)

### 2. Hazard Detection Tests
**What to verify:**
- RAW (Read After Write) hazards are detected
- Stalls are inserted when needed
- No false hazards (over-stalling)
- WAW and WAR are correctly ignored in in-order pipeline

**Run tests:**
```bash
python -m unittest tests.test_hazards -v
```

**Expected behavior:**
- RAW with Execute stage: 3 cycle stall
- RAW with Memory stage: 2 cycle stall  
- No stall for WriteBack stage (data available)
- No stall for independent instructions

### 3. Edge Case and Performance Tests
**What to verify:**
- Single instruction execution
- Long dependency chains
- STORE instructions (no destination register)
- All instruction types (R-type, LOAD, STORE)
- CPI (Cycles Per Instruction) metrics
- IPC (Instructions Per Cycle) metrics

**Run tests:**
```bash
python -m unittest tests.test_edge_cases -v
```

**Expected metrics:**
- Independent instructions: CPI ≈ 2.0-2.5 (with pipeline fill)
- With dependencies: CPI increases with stalls
- Maximum IPC ≈ 1.0 (one instruction per cycle at steady state)

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

### Hazard Detection
- Checks Execute and Memory stages for RAW hazards
- Inserts bubbles into Execute stage when hazard detected
- Stalls until producer instruction reaches WriteBack

### Supported Instructions
- **R-type**: `ADD R1, R2, R3`, `SUB R4, R5, R6`, `OR R7, R8, R9`, `AND R10, R11, R12`, `XOR R13, R14, R15`
- **LOAD**: `LOAD R1, 100(R2)`
- **STORE**: `STORE R3, 200(R4)`

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
├── riscv.py                # Main processor interface (start here!)
├── pipeline.py             # Pipeline implementation
├── instruction.py          # Instruction parsing
├── register_file.py        # Register file component
├── memory.py               # Data memory component
├── alu.py                  # Arithmetic Logic Unit
├── requirements.txt        # Python dependencies
├── README.md               # This file (main documentation)
├── .gitignore              # Git ignore rules
├── sandbox/                # Experimental scripts
│   └── vis_pipeline.py     # Custom visualization examples
└── tests/                  # Test suite
    ├── __init__.py
    ├── test_correctness.py # Functional tests
    ├── test_hazards.py     # Hazard detection tests
    ├── test_edge_cases.py  # Edge cases and performance
    ├── visualization.py    # Visualization utilities
    ├── run_tests.py        # Test runner
    └── README.md           # Test documentation
```

## Testing Checklist

- [ ] All instructions complete successfully
- [ ] RAW hazards are detected and stalled
- [ ] Independent instructions don't stall
- [ ] Instruction order is preserved
- [ ] All 5 stages are executed for each instruction
- [ ] Bubbles are inserted during stalls
- [ ] Pipeline state is tracked correctly
- [ ] LOAD instructions work correctly
- [ ] STORE instructions work correctly
- [ ] Single instruction works
- [ ] Long dependency chains work
- [ ] CPI/IPC metrics are reasonable

## Future Enhancements

### Data Forwarding
- EX → EX forwarding: 0 cycle stall
- MEM → EX forwarding: 0 cycle stall
- WB → EX forwarding: 0 cycle stall
- LOAD-use still requires 1 cycle stall

### Branch Prediction
- Branch misprediction penalty
- Flush pipeline on misprediction
- Branch target buffer

### Out-of-Order Execution
- WAW hazards become real
- WAR hazards become real
- Register renaming needed
- Reorder buffer

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
