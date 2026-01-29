# Interrupt Enable and Pending Logic

This document describes the advanced interrupt enable/pending logic implemented in the RISC-V simulator.

## Overview

The `InterruptController` class in [interrupt.py](../interrupt.py) provides fine-grained control over interrupt handling including:
- Individual interrupt enable/disable
- Global interrupt enable/disable  
- Interrupt pending tracking (mip CSR)
- Priority-based interrupt resolution
- Edge and level-triggered interrupt support
- Interrupt masking and deliverability calculation
- Interrupt source simulation

This is separate from but integrated with the `TrapController` for complete interrupt handling.

## Architecture

### InterruptController Class

```python
from interrupt import InterruptController
from csr import CSRBank

csr_bank = CSRBank()
int_controller = InterruptController(csr_bank)
```

### Key Concepts

**Three Interrupt Types**:
- Software interrupt (bit 3, code 0x80000003)
- Timer interrupt (bit 7, code 0x80000007)
- External interrupt (bit 11, code 0x8000000B)

**Interrupt Delivery Conditions**:
An interrupt is deliverable if ALL of:
1. Globally enabled (mstatus.MIE = 1)
2. Individually enabled (mie bit set)
3. Pending (mip bit set)

**Priority Order**:
1. External (highest)
2. Software
3. Timer (lowest)

## Pipeline Integration

The InterruptController is integrated with the pipeline through the TrapController:

```python
# In pipeline.py
class Pipeline:
    def __init__(self):
        self.csr_bank = CSRBank()
        self.trap_controller = TrapController(self.csr_bank)
        self.interrupt_controller = self.trap_controller.interrupt_controller
```

### Interrupt Delivery Flow
1. **Before Fetch**: Pipeline calls `trap_controller.check_pending_interrupts()`
2. **Priority Resolution**: InterruptController returns highest priority interrupt
3. **Deliverability Check**: Verifies global enable (MIE) and individual enable (mie bit)
4. **Trap Entry**: TrapController delivers interrupt and updates CSRs
5. **Pipeline Flush**: Cancels in-flight instructions
6. **Handler Execution**: Pipeline fetches from handler address

### Usage in Pipeline
```python
# Enable and trigger interrupt
pipeline.interrupt_controller.enable_interrupt(pipeline.interrupt_controller.INT_TIMER)
pipeline.interrupt_controller.set_pending(pipeline.interrupt_controller.INT_TIMER)

# Enable global interrupts
mstatus = pipeline.csr_bank.read(0x300)
mstatus |= (1 << 3)  # Set MIE
pipeline.csr_bank.write(0x300, mstatus)

# Run - interrupt will be delivered before first instruction
pipeline.run(instructions)
```

See [PIPELINE_INTERRUPTS.md](../PIPELINE_INTERRUPTS.md) for complete integration details.

## Basic Operations

### Setting Interrupts Pending

```python
# Set timer interrupt pending
int_controller.set_pending(InterruptController.INT_TIMER)

# Check if pending
if int_controller.is_pending(InterruptController.INT_TIMER):
    print("Timer interrupt pending")
```

### Enabling Interrupts

```python
# Enable specific interrupt
int_controller.enable_interrupt(InterruptController.INT_TIMER)

# Enable globally (mstatus.MIE)
int_controller.enable_global_interrupts()

# Check if enabled
if int_controller.is_enabled(InterruptController.INT_TIMER):
    print("Timer interrupt enabled")
```

### Clearing Interrupts

```python
# Clear pending bit
int_controller.clear_pending(InterruptController.INT_TIMER)

# Disable specific interrupt
int_controller.disable_interrupt(InterruptController.INT_TIMER)

# Disable globally
int_controller.disable_global_interrupts()
```

## Advanced Features

### Interrupt Masking

Set multiple interrupt enables at once:

```python
# Enable timer and external, disable software
mask = (1 << 7) | (1 << 11)  # Bits 7 and 11
int_controller.mask_interrupts(mask)

# Get current mask
current_mask = int_controller.get_interrupt_mask()
print(f"Enabled interrupts: {current_mask:#x}")
```

### Deliverable Interrupts

Get list of interrupts ready for delivery:

```python
# Enable everything
int_controller.enable_global_interrupts()
int_controller.enable_interrupt(InterruptController.INT_TIMER)
int_controller.enable_interrupt(InterruptController.INT_SOFTWARE)

# Set some pending
int_controller.set_pending(InterruptController.INT_TIMER)
int_controller.set_pending(InterruptController.INT_EXTERNAL)  # Not enabled

# Get deliverable
deliverable = int_controller.get_deliverable_interrupts()
# Returns: [7] (timer only - pending AND enabled)
```

### Priority Resolution

Get highest priority interrupt:

```python
# Set all interrupts pending and enabled
int_controller.enable_global_interrupts()
int_controller.mask_interrupts((1 << 3) | (1 << 7) | (1 << 11))

int_controller.set_pending(InterruptController.INT_SOFTWARE)
int_controller.set_pending(InterruptController.INT_TIMER)
int_controller.set_pending(InterruptController.INT_EXTERNAL)

# Get highest priority
highest = int_controller.get_highest_priority_interrupt()
# Returns: 11 (external has highest priority)
```

### Edge vs Level Triggering

**Level-Triggered (Default)**:
- Interrupt remains pending while source is active
- Software must clear the interrupt source
- Pending bit clears when source drops

```python
# Default is level-triggered
int_controller.set_pending(InterruptController.INT_TIMER)

# Acknowledge doesn't auto-clear
int_controller.acknowledge_interrupt(InterruptController.INT_TIMER)
# Still pending until software clears source
```

**Edge-Triggered**:
- Interrupt latches on rising edge
- Automatically clears when acknowledged
- Source can drop immediately

```python
# Configure as edge-triggered
int_controller.set_edge_triggered(InterruptController.INT_TIMER)

# Set pending (edge latch)
int_controller.set_pending(InterruptController.INT_TIMER, edge=True)

# Acknowledge auto-clears
int_controller.acknowledge_interrupt(InterruptController.INT_TIMER)
# No longer pending
```

## Interrupt Sources

The `InterruptSource` class simulates external interrupt sources:

```python
from interrupt import InterruptSource

# Create timer source
timer = InterruptSource("System Timer", InterruptController.INT_TIMER)

# Connect to controller
timer.connect(int_controller)

# Assert interrupt (level-triggered)
timer.assert_interrupt()
# Controller now shows timer pending

# Deassert
timer.deassert_interrupt()
# Pending cleared

# Or generate pulse
timer.pulse()  # Assert then deassert
```

### Edge-Triggered Source

```python
# Configure as edge
int_controller.set_edge_triggered(InterruptController.INT_EXTERNAL)

external = InterruptSource("GPIO", InterruptController.INT_EXTERNAL)
external.connect(int_controller)

# Pulse generates edge
external.pulse()
# Latches pending bit even after pulse ends
```

## Usage Examples

### Example 1: Basic Interrupt Setup

```python
from interrupt import InterruptController
from csr import CSRBank

# Initialize
csr = CSRBank()
ic = InterruptController(csr)

# Setup: enable timer interrupt
ic.enable_global_interrupts()          # Global enable (mstatus.MIE)
ic.enable_interrupt(ic.INT_TIMER)      # Timer enable (mie bit 7)

# Timer fires
ic.set_pending(ic.INT_TIMER)

# Check if deliverable
if ic.is_pending(ic.INT_TIMER) and ic.is_enabled(ic.INT_TIMER):
    print("Timer interrupt ready for delivery")
    
# Or use convenience method
deliverable = ic.get_deliverable_interrupts()
if ic.INT_TIMER in deliverable:
    print("Timer is deliverable")
```

### Example 2: Priority Handling

```python
# Enable all interrupts
ic.enable_global_interrupts()
ic.mask_interrupts((1 << 3) | (1 << 7) | (1 << 11))

# Multiple interrupts fire
ic.set_pending(ic.INT_SOFTWARE)
ic.set_pending(ic.INT_TIMER)

# Get highest priority
highest = ic.get_highest_priority_interrupt()

if highest == ic.INT_SOFTWARE:
    print("Deliver software interrupt first")
    # Handle interrupt...
    ic.clear_pending(ic.INT_SOFTWARE)
    
    # Now check again
    highest = ic.get_highest_priority_interrupt()
    if highest == ic.INT_TIMER:
        print("Now deliver timer interrupt")
```

### Example 3: Interrupt Masking

```python
# Initially enable all
ic.enable_global_interrupts()
ic.mask_interrupts((1 << 3) | (1 << 7) | (1 << 11))

# Critical section: disable timer temporarily
old_mask = ic.get_interrupt_mask()
ic.disable_interrupt(ic.INT_TIMER)

# ... critical code ...

# Restore mask
ic.mask_interrupts(old_mask)
```

### Example 4: Complete Interrupt Flow

```python
from interrupt import InterruptController, InterruptSource
from csr import CSRBank

# Setup
csr = CSRBank()
ic = InterruptController(csr)

# Create timer source
timer = InterruptSource("Timer", ic.INT_TIMER)
timer.connect(ic)

# Enable interrupts
ic.enable_global_interrupts()
ic.enable_interrupt(ic.INT_TIMER)

# Timer fires
timer.assert_interrupt()

# Check for delivery
if ic.is_globally_enabled():
    highest = ic.get_highest_priority_interrupt()
    
    if highest == ic.INT_TIMER:
        print(f"Delivering timer interrupt")
        
        # Get interrupt code
        code = ic.get_interrupt_code(highest)
        print(f"Interrupt code: {code:#x}")  # 0x80000007
        
        # Acknowledge (for edge-triggered)
        ic.acknowledge_interrupt(highest)
        
        # For level-triggered, software clears source
        timer.deassert_interrupt()
```

### Example 5: Edge-Triggered Interrupts

```python
# Configure external as edge-triggered
ic.set_edge_triggered(ic.INT_EXTERNAL)

# Create GPIO source
gpio = InterruptSource("GPIO Button", ic.INT_EXTERNAL)
gpio.connect(ic)

# Button press (rising edge)
gpio.assert_interrupt()

# Button release
gpio.deassert_interrupt()

# Interrupt still pending (latched on edge)
assert ic.is_pending(ic.INT_EXTERNAL)

# Acknowledge clears it
ic.acknowledge_interrupt(ic.INT_EXTERNAL)
assert not ic.is_pending(ic.INT_EXTERNAL)
```

### Example 6: Status Monitoring

```python
# Setup some state
ic.enable_global_interrupts()
ic.enable_interrupt(ic.INT_TIMER)
ic.enable_interrupt(ic.INT_SOFTWARE)
ic.set_pending(ic.INT_TIMER)

# Get human-readable status
print(ic.get_status_string())

# Output:
# Global Enable: True
# Pending: SW=False T=True E=False
# Enabled: SW=True T=True E=False
# Deliverable: [7]
# Highest Priority: 7
```

### Example 7: Integration with TrapController

```python
from trap import TrapController
from interrupt import InterruptController
from csr import CSRBank

# Initialize both controllers
csr = CSRBank()
trap = TrapController(csr)
ic = trap.interrupt_controller  # TrapController creates InterruptController

# Enable timer interrupt
ic.enable_global_interrupts()
ic.enable_interrupt(ic.INT_TIMER)

# Set pending
ic.set_pending(ic.INT_TIMER)

# Check if deliverable
if ic.get_highest_priority_interrupt() is not None:
    # Use TrapController to deliver
    result = trap.check_pending_interrupts(next_pc=0x1000)
    
    if result:
        print(f"Interrupt delivered to: {result['handler_pc']:#x}")
```

## API Reference

### InterruptController Methods

**Pending Management**:
- `set_pending(interrupt_bit, edge=False)` - Set interrupt pending
- `clear_pending(interrupt_bit)` - Clear interrupt pending
- `is_pending(interrupt_bit)` - Check if pending
- `get_pending_interrupts()` - List all pending interrupts
- `get_pending_mask()` - Get pending bitmask

**Enable Management**:
- `enable_interrupt(interrupt_bit)` - Enable specific interrupt
- `disable_interrupt(interrupt_bit)` - Disable specific interrupt
- `is_enabled(interrupt_bit)` - Check if enabled
- `get_enabled_interrupts()` - List enabled interrupts
- `get_interrupt_mask()` - Get enable bitmask
- `mask_interrupts(mask)` - Set enable bitmask

**Global Enable**:
- `enable_global_interrupts()` - Set mstatus.MIE
- `disable_global_interrupts()` - Clear mstatus.MIE
- `is_globally_enabled()` - Check mstatus.MIE

**Delivery**:
- `get_deliverable_interrupts()` - List deliverable interrupts
- `get_highest_priority_interrupt()` - Get highest priority deliverable

**Edge/Level Triggering**:
- `set_edge_triggered(interrupt_bit)` - Configure as edge
- `set_level_triggered(interrupt_bit)` - Configure as level
- `is_edge_triggered(interrupt_bit)` - Check if edge
- `is_level_triggered(interrupt_bit)` - Check if level
- `acknowledge_interrupt(interrupt_bit)` - Acknowledge interrupt

**Utilities**:
- `get_interrupt_code(interrupt_bit)` - Convert bit to code
- `reset()` - Reset all state
- `get_status_string()` - Get status description

### InterruptSource Methods

- `connect(controller)` - Connect to InterruptController
- `assert_interrupt()` - Raise interrupt signal
- `deassert_interrupt()` - Lower interrupt signal
- `pulse()` - Generate interrupt pulse
- `is_active()` - Check if signal is active

## CSR Integration

The InterruptController directly manipulates CSR registers:

**mstatus (0x300)**:
- Bit 3 (MIE): Global interrupt enable
- Modified by `enable_global_interrupts()` / `disable_global_interrupts()`

**mie (0x304)**:
- Bit 3: Software interrupt enable
- Bit 7: Timer interrupt enable
- Bit 11: External interrupt enable
- Modified by `enable_interrupt()` / `disable_interrupt()` / `mask_interrupts()`

**mip (0x344)**:
- Bit 3: Software interrupt pending
- Bit 7: Timer interrupt pending
- Bit 11: External interrupt pending
- Modified by `set_pending()` / `clear_pending()`

## Testing

The interrupt controller includes 35 comprehensive tests in [test_interrupt.py](../tests/functional_tests/test_interrupt.py):

**Basic Tests** (8 tests):
- Set/clear pending bits
- Enable/disable interrupts
- Global enable/disable

**List Tests** (4 tests):
- Get pending interrupts
- Get enabled interrupts
- Get deliverable interrupts
- Mask filtering

**Priority Tests** (3 tests):
- External highest priority
- Software over timer
- No deliverable returns None

**Masking Tests** (3 tests):
- Set interrupt mask
- Get interrupt mask
- Get pending mask

**Edge/Level Tests** (5 tests):
- Configure triggering mode
- Edge latching
- Acknowledge behavior

**Source Tests** (6 tests):
- Connect source
- Assert/deassert
- Level vs edge behavior
- Pulse generation

**Utilities** (6 tests):
- Interrupt code conversion
- Reset
- Status string

Run tests:
```bash
python -m unittest tests.functional_tests.test_interrupt -v
```

## Performance Considerations

**Efficient Operations**:
- `is_pending()`, `is_enabled()` - Direct CSR read, O(1)
- `set_pending()`, `enable_interrupt()` - Single CSR write, O(1)
- `get_highest_priority_interrupt()` - Checks 3 bits with priority, O(1)

**Batch Operations**:
- Use `mask_interrupts()` instead of multiple `enable_interrupt()` calls
- Use `get_deliverable_interrupts()` instead of checking each individually

## Limitations and Future Work

**Current Implementation**:
- ✅ Three standard RISC-V interrupts (software, timer, external)
- ✅ Priority-based delivery
- ✅ Edge and level triggering
- ✅ Full CSR integration
- ✅ Interrupt source simulation

**Future Enhancements**:
- Additional interrupt sources (16 standard RISC-V interrupts)
- Nested interrupt support (automatically save/restore state)
- Interrupt delegation (medeleg/mideleg for supervisor mode)
- Per-hart interrupt controllers (multi-core)
- Performance counters for interrupt statistics

## References

- [interrupt.py](../interrupt.py) - InterruptController implementation
- [test_interrupt.py](../tests/functional_tests/test_interrupt.py) - Test suite
- [trap.py](../trap.py) - TrapController integration
- [TRAP_MECHANISM.md](TRAP_MECHANISM.md) - Trap/interrupt overview
- [RISC-V Privileged Spec](https://riscv.org/technical/specifications/) - Official specification

## See Also

- [INSTRUCTION_SET.md](INSTRUCTION_SET.md) - All supported instructions
- [RV32I_COVERAGE.md](RV32I_COVERAGE.md) - Implementation status
- [README.md](../README.md) - Main documentation
