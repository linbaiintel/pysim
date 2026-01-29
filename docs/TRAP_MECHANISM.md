# RISC-V Trap and Interrupt Mechanism

This document describes the trap and interrupt handling mechanism implemented in the RISC-V simulator.

## Overview

The trap mechanism implements the RISC-V privileged architecture specification for handling exceptions (synchronous) and interrupts (asynchronous). This is essential for:
- Operating system support (FreeRTOS, bare-metal OS)
- Exception handling (illegal instructions, breakpoints)
- Interrupt servicing (timer, external devices)
- System calls (ECALL)

## Architecture

### TrapController Class

The `TrapController` class in [trap.py](../trap.py) manages all trap and interrupt functionality:

```python
from trap import TrapController
from csr import CSRBank

csr_bank = CSRBank()
trap_controller = TrapController(csr_bank)
```

### Exception Types

**Synchronous Exceptions** (occur during instruction execution):
| Code | Name | Description | Trigger |
|------|------|-------------|---------|
| 0 | Instruction misaligned | PC not 4-byte aligned | Jump to odd address |
| 1 | Instruction access fault | Cannot fetch instruction | Bad instruction address |
| 2 | Illegal instruction | Invalid opcode/encoding | Unknown instruction |
| 3 | Breakpoint | Debug breakpoint | EBREAK instruction |
| 4 | Load address misaligned | Load address not aligned | Unaligned LW/LH |
| 5 | Load access fault | Cannot read memory | Bad load address |
| 6 | Store address misaligned | Store address not aligned | Unaligned SW/SH |
| 7 | Store access fault | Cannot write memory | Bad store address |
| 8 | Environment call (U-mode) | System call from User | ECALL in User mode |
| 11 | Environment call (M-mode) | System call from Machine | ECALL in Machine mode |

### Interrupt Types

**Asynchronous Interrupts** (occur between instructions):
| Code | Name | Description |
|------|------|-------------|
| 3 (0x80000003) | Software interrupt | Inter-processor interrupt |
| 7 (0x80000007) | Timer interrupt | Timer expired |
| 11 (0x8000000B) | External interrupt | External device |

**Note**: Interrupt codes have MSB set (bit 31) to distinguish from exceptions.

## Trap Entry Mechanism

When an exception or interrupt occurs, the following sequence happens automatically:

### 1. Save Current State
```
mepc (0x341) ← PC        # Save program counter
                         # - For exceptions: address of faulting instruction
                         # - For interrupts: address of next instruction
```

### 2. Update mstatus CSR
```
mstatus.MPIE ← mstatus.MIE    # Save interrupt enable
mstatus.MIE ← 0                # Disable interrupts
mstatus.MPP ← current_mode     # Save privilege mode (3=Machine)
```

### 3. Record Trap Cause
```
mcause (0x342) ← cause_code    # Exception code or interrupt code (with MSB)
mtval (0x343) ← trap_value     # Faulting address or instruction bits
```

### 4. Jump to Handler
```
PC ← mtvec.BASE                # Jump to trap handler
                               # - Direct mode: always BASE
                               # - Vectored mode: BASE + 4*cause (interrupts only)
```

## Trap Exit Mechanism (MRET)

The MRET instruction returns from a trap handler:

### MRET Behavior
```
PC ← mepc                      # Restore saved PC
mstatus.MIE ← mstatus.MPIE     # Restore interrupt enable
mstatus.MPIE ← 1               # Set MPIE to 1
mstatus.MPP ← 0                # Return to User mode
```

### Usage
```assembly
# Trap handler
trap_handler:
    # Save context (registers)
    # Handle trap
    # Restore context
    MRET                        # Return from trap
```

## CSR Registers

### mtvec (0x305) - Trap Vector Base Address

**Format**: `[BASE[31:2] | MODE[1:0]]`

**Modes**:
- `00` (0): Direct mode - all traps jump to BASE
- `01` (1): Vectored mode - exceptions to BASE, interrupts to BASE + 4*cause
- `10`, `11`: Reserved

**Example**:
```python
# Set trap handler to 0x80000000 in direct mode
csr.write(0x305, 0x80000000 | 0x0)

# Set trap handler to 0x80000000 in vectored mode
csr.write(0x305, 0x80000000 | 0x1)
# - Exceptions go to 0x80000000
# - Timer interrupt (7) goes to 0x8000001C (0x80000000 + 7*4)
```

### mstatus (0x300) - Machine Status Register

**Relevant bits**:
- `MIE[3]`: Machine Interrupt Enable (global interrupt enable)
- `MPIE[7]`: Machine Previous Interrupt Enable (saved MIE)
- `MPP[12:11]`: Machine Previous Privilege mode (00=User, 11=Machine)

**Example**:
```python
# Enable interrupts globally
mstatus = csr.read(0x300)
csr.write(0x300, mstatus | (1 << 3))  # Set MIE

# Check previous interrupt state
mpie = (mstatus >> 7) & 0x1
```

### mie (0x304) - Machine Interrupt Enable

**Bits**:
- `MSIE[3]`: Machine Software Interrupt Enable
- `MTIE[7]`: Machine Timer Interrupt Enable
- `MEIE[11]`: Machine External Interrupt Enable

**Example**:
```python
# Enable timer interrupts
mie = csr.read(0x304)
csr.write(0x304, mie | (1 << 7))
```

### mip (0x344) - Machine Interrupt Pending

**Bits**:
- `MSIP[3]`: Machine Software Interrupt Pending
- `MTIP[7]`: Machine Timer Interrupt Pending
- `MEIP[11]`: Machine External Interrupt Pending

**Note**: Written by hardware/trap controller, read by software.

### mepc (0x341) - Machine Exception Program Counter

Holds the PC to return to after trap handling.

### mcause (0x342) - Machine Cause

**Format**: `[Interrupt[31] | Exception Code[30:0]]`
- Bit 31 = 0: Synchronous exception, bits[30:0] = exception code
- Bit 31 = 1: Asynchronous interrupt, bits[30:0] = interrupt code

### mtval (0x343) - Machine Trap Value

Additional information about the trap:
- Address that caused fault (for address exceptions)
- Instruction bits (for illegal instruction)
- 0 (for other traps)

## Usage Examples

### Example 1: Handle ECALL Exception

```python
from trap import TrapController
from csr import CSRBank

csr = CSRBank()
trap = TrapController(csr)

# Setup trap handler
csr.write(0x305, 0x80000000)  # mtvec = 0x80000000

# Execute ECALL instruction at PC=0x1000
result = trap.ecall(pc=0x1000)

print(f"Exception type: {result['type']}")         # 'exception'
print(f"Handler PC: {result['handler_pc']:#x}")    # 0x80000000
print(f"Saved PC: {result['epc']:#x}")             # 0x1000
print(f"Cause: {result['cause']}")                  # 11 (ECALL from M-mode)

# CSR state after exception:
assert csr.read(0x341) == 0x1000           # mepc = saved PC
assert csr.read(0x342) == 11               # mcause = ECALL_FROM_M
assert (csr.read(0x300) >> 3) & 0x1 == 0   # MIE = 0 (disabled)
```

### Example 2: Deliver Timer Interrupt

```python
csr = CSRBank()
trap = TrapController(csr)

# Setup
csr.write(0x305, 0x80000000)  # mtvec

# Enable interrupts globally
mstatus = csr.read(0x300)
csr.write(0x300, mstatus | (1 << 3))  # MIE = 1

# Enable timer interrupt specifically
mie = csr.read(0x304)
csr.write(0x304, mie | (1 << 7))  # MTIE = 1

# Timer fires (set by hardware/CLINT)
trap.set_interrupt_pending('timer')

# Check for interrupts at next instruction fetch
next_pc = 0x2000
result = trap.check_pending_interrupts(next_pc)

if result:
    print(f"Interrupt delivered!")
    print(f"Handler: {result['handler_pc']:#x}")
    print(f"Next PC saved: {result['epc']:#x}")    # 0x2000
    print(f"Cause: {result['cause']:#x}")          # 0x80000007 (Timer)
```

### Example 3: Vectored Interrupts

```python
csr = CSRBank()
trap = TrapController(csr)

# Setup vectored mode
handler_base = 0x80000000
csr.write(0x305, handler_base | 0x1)  # Vectored mode

# Enable interrupts
mstatus = csr.read(0x300)
csr.write(0x300, mstatus | (1 << 3))
mie = csr.read(0x304)
csr.write(0x304, mie | (1 << 7) | (1 << 3))  # Timer + Software

# Set software interrupt pending
trap.set_interrupt_pending('software')
result = trap.check_pending_interrupts(0x1000)

# Software interrupt (cause 3) vectors to BASE + 3*4
assert result['handler_pc'] == 0x80000000 + 3*4  # 0x8000000C
```

### Example 4: Interrupt Priority

When multiple interrupts are pending, they are delivered in priority order:
1. External (highest priority)
2. Software
3. Timer (lowest priority)

```python
csr = CSRBank()
trap = TrapController(csr)

# Enable all interrupts
mstatus = csr.read(0x300)
csr.write(0x300, mstatus | (1 << 3))
mie = csr.read(0x304)
csr.write(0x304, mie | (1 << 3) | (1 << 7) | (1 << 11))

# Set all interrupts pending
trap.set_interrupt_pending('software')
trap.set_interrupt_pending('timer')
trap.set_interrupt_pending('external')

# External has highest priority
result = trap.check_pending_interrupts(0x1000)
assert result['cause'] == TrapController.INTERRUPT_EXTERNAL  # 0x8000000B
```

### Example 5: Complete Trap Sequence

```python
# 1. Setup
csr = CSRBank()
trap = TrapController(csr)
csr.write(0x305, 0x80000000)  # Trap handler address

# 2. Enable interrupts
mstatus = csr.read(0x300)
csr.write(0x300, mstatus | (1 << 3))  # MIE = 1

# 3. User code running at 0x1000
current_pc = 0x1000

# 4. ECALL executed - enter trap
result = trap.ecall(current_pc)
# Now at trap handler: 0x80000000
# Interrupts disabled (MIE = 0)
# mepc = 0x1000

# 5. Trap handler executes
# ... handle system call ...

# 6. MRET executed - exit trap
from exe import EXE
mret_result = EXE.execute_mret(csr)
# PC restored from mepc: 0x1000
# Interrupts restored (MIE = previous value)
# Back to user code

assert mret_result['new_pc'] == 0x1000
assert (csr.read(0x300) >> 3) & 0x1 == 1  # MIE restored
```

## Integration with Pipeline

To integrate trap handling with the pipeline simulator:

### 1. Add TrapController to Pipeline
```python
class Pipeline:
    def __init__(self):
        self.csr_bank = CSRBank()
        self.trap_controller = TrapController(self.csr_bank)
        # ... other pipeline components
```

### 2. Check for Interrupts at Fetch
```python
def fetch_stage(self):
    # Check for pending interrupts before fetching
    trap_info = self.trap_controller.check_pending_interrupts(self.pc)
    
    if trap_info:
        # Interrupt delivered - redirect to handler
        self.pc = trap_info['handler_pc']
        self.flush_pipeline()
        return
    
    # Normal instruction fetch
    instruction = self.memory.fetch(self.pc)
    # ...
```

### 3. Handle Exceptions in Execute
```python
def execute_stage(self, instruction):
    if instruction.operation == 'ECALL':
        trap_info = self.trap_controller.ecall(self.pc)
        self.pc = trap_info['handler_pc']
        self.flush_pipeline()
    elif instruction.operation == 'EBREAK':
        trap_info = self.trap_controller.ebreak(self.pc)
        self.pc = trap_info['handler_pc']
        self.flush_pipeline()
    # ... handle other instructions
```

### 4. Handle MRET
```python
def execute_stage(self, instruction):
    if instruction.operation == 'MRET':
        result = EXE.execute_mret(self.csr_bank)
        self.pc = result['new_pc']
        # No pipeline flush needed for MRET
```

## Testing

The trap mechanism includes 26 comprehensive tests in [test_trap.py](../tests/functional_tests/test_trap.py):

**Exception Tests** (13 tests):
- PC saved to mepc
- mcause/mtval set correctly
- Interrupt disable (MIE cleared)
- State save (MIE→MPIE, MPP set)
- Handler address calculation
- ECALL/EBREAK integration
- Illegal instruction handling

**Interrupt Tests** (13 tests):
- Pending interrupt tracking (mip)
- Global interrupt enable (mstatus.MIE)
- Per-interrupt enable (mie)
- Interrupt priority (External > Software > Timer)
- Direct vs vectored mode
- Next PC saved to mepc
- Interrupt delivery and removal from pending

Run tests:
```bash
python -m unittest tests.functional_tests.test_trap -v
```

## Limitations and Future Work

**Current Implementation**:
- ✅ Complete trap entry mechanism
- ✅ Complete trap exit (MRET)
- ✅ Exception handling (ECALL, EBREAK, illegal instruction)
- ✅ Interrupt support (software, timer, external)
- ✅ CSR state management
- ✅ Priority-based delivery
- ✅ Direct and vectored modes

**Future Enhancements**:
- CLINT (Core-Local Interruptor) peripheral for timer interrupts
- Actual privilege mode enforcement (currently assumes Machine mode)
- Supervisor mode support
- User mode trap delegation (medeleg/mideleg)
- WFI (Wait For Interrupt) instruction
- Performance counters for trap statistics

## References

- [RISC-V Privileged Architecture Specification](https://riscv.org/technical/specifications/)
- [trap.py](../trap.py) - TrapController implementation
- [test_trap.py](../tests/functional_tests/test_trap.py) - Comprehensive test suite
- [csr.py](../csr.py) - CSR bank implementation
- [exe.py](../exe.py) - MRET execution

## See Also

- [INSTRUCTION_SET.md](INSTRUCTION_SET.md) - All supported instructions
- [RV32I_COVERAGE.md](RV32I_COVERAGE.md) - Implementation status
- [README.md](../README.md) - Main documentation
