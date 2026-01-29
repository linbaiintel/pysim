# Pipeline Interrupt Integration

This document describes the integration of interrupt checking and trap handling into the RISC-V pipeline simulator.

## Overview

The pipeline now checks for pending interrupts before each instruction fetch and can deliver interrupts during program execution. This enables proper support for asynchronous events like timer interrupts, which is essential for operating systems and real-time applications.

## Architecture

### Components Added to Pipeline

1. **CSRBank**: Control and Status Register bank for storing machine-mode state
2. **TrapController**: Handles trap entry/exit and interrupt delivery
3. **InterruptController**: Manages interrupt enable/pending logic with priority resolution

### Pipeline Modifications

#### 1. Instruction Feeder
Before each instruction fetch, the pipeline calls:
```python
interrupt_info = self.trap_controller.check_pending_interrupts(next_pc)
```

If an interrupt is deliverable:
- Pipeline flushes (inserts bubbles into fetch/decode/execute stages)
- PC redirects to trap handler (read from `mtvec`)
- Trap state saved to CSRs (`mepc`, `mcause`, `mstatus`)

#### 2. Execute Stage
Modified to handle special trap-related operations:
- **ECALL**: Triggers environment call exception
- **EBREAK**: Triggers breakpoint exception
- **MRET**: Returns from trap handler (calls `execute_mret` to get new PC)
- **CSR operations**: Marked for execution in WriteBack stage

#### 3. WriteBack Stage
Executes CSR operations and writes results to both CSRs and registers:
```python
if result_type == 'csr':
    csr_op = result['operation']
    csr_addr = result['csr']
    value = result['value']
    old_value = EXE.execute_csr_operation(csr_op, csr_addr, value, self.csr_bank)
```

## Interrupt Delivery Flow

1. **Interrupt Assertion**: External source calls `interrupt_controller.set_pending(interrupt_bit)`
2. **Enable Check**: Before fetch, pipeline checks if interrupt is both pending and enabled
3. **Priority Resolution**: InterruptController selects highest priority interrupt (External > Software > Timer)
4. **Trap Entry**: TrapController delivers interrupt:
   - Save PC to `mepc`
   - Write cause to `mcause` (MSB set for interrupts)
   - Clear MIE bit in `mstatus`
   - Jump to handler address from `mtvec`
5. **Pipeline Flush**: Insert bubbles to cancel in-flight instructions
6. **Handler Execution**: Pipeline fetches from handler address
7. **Return**: MRET restores PC from `mepc` and re-enables interrupts

## Usage Example

```python
from pipeline import Pipeline

# Create pipeline
pipeline = Pipeline()

# Enable timer interrupt
ic = pipeline.trap_controller.interrupt_controller
ic.enable_interrupt(ic.INT_TIMER)
ic.set_pending(ic.INT_TIMER)

# Set trap handler address
pipeline.csr_bank.write(0x305, 0x80000000)  # mtvec

# Enable global interrupts
mstatus = pipeline.csr_bank.read(0x300)
mstatus |= (1 << 3)  # Set MIE
pipeline.csr_bank.write(0x300, mstatus)

# Run program - interrupt will be delivered before first instruction
instructions = ["ADDI R1, R0, 10", "ADDI R2, R0, 20"]
pipeline.run(instructions)

# Check trap state
mepc = pipeline.csr_bank.read(0x341)   # Saved PC
mcause = pipeline.csr_bank.read(0x342)  # Cause (0x80000007 for timer)
```

## Testing

The pipeline interrupt integration includes 8 comprehensive tests in `test_pipeline_interrupts.py`:

1. **test_pipeline_has_interrupt_controller**: Verifies initialization
2. **test_pipeline_checks_interrupts_no_pending**: Normal execution without interrupts
3. **test_pipeline_with_interrupt_pending_and_disabled**: Interrupts not delivered when disabled
4. **test_pipeline_with_csr_operations**: CSR read/write in pipeline
5. **test_pipeline_mret_instruction**: MRET returns from trap
6. **test_pipeline_ecall_triggers_trap**: ECALL triggers trap
7. **test_pipeline_interrupt_controller_accessible**: Controller methods accessible
8. **test_pipeline_with_enabled_interrupt**: Full interrupt delivery and trap entry

All 248 tests pass (240 original + 8 new pipeline tests).

## Key Features

### Interrupt Checking
- Performed before each instruction fetch
- Respects global enable (MIE in mstatus)
- Respects individual enables (mie register)
- Uses priority-based resolution

### Trap Handling
- Supports synchronous exceptions (ECALL, EBREAK)
- Supports asynchronous interrupts (timer, software, external)
- Saves architectural state to CSRs
- Properly flushes pipeline on trap entry

### CSR Operations
- CSRRW, CSRRS, CSRRC implemented
- Execute in WriteBack stage with proper hazard handling
- Support for immediate variants (CSRRWI, etc.)

### MRET Instruction
- Restores PC from mepc
- Restores interrupt enable (MPIE → MIE)
- Clears MPIE
- Triggers pipeline flush to new PC

## Implementation Details

### Interrupt Controller Integration
The TrapController now queries the InterruptController for pending interrupts:
```python
interrupt_bit = self.interrupt_controller.get_highest_priority_interrupt()
```

This returns the bit position (3, 7, or 11) of the highest priority deliverable interrupt, or None if no interrupts can be delivered.

### Legacy Compatibility
The implementation maintains backward compatibility with the legacy `pending_interrupts` set for tests that use `set_interrupt_pending()` directly.

### Cycle-Accurate Behavior
- Interrupt check happens at cycle boundary before fetch
- Pipeline flush takes 3 cycles (fetch, decode, execute)
- Trap entry state saved before handler begins execution

## Files Modified

1. **pipeline.py**: Added interrupt/trap controller integration
2. **trap.py**: Updated `check_pending_interrupts()` to use InterruptController
3. **test_pipeline_interrupts.py**: New test suite for pipeline integration

## Future Enhancements

Potential improvements:
1. Vectored interrupt mode support (mtvec[0] = 1)
2. Nested interrupt handling
3. Interrupt latency measurements
4. Support for supervisor mode interrupts
5. Performance counters for interrupt statistics
