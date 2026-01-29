# CLINT (Core Local Interruptor) Implementation

## Overview

CLINT (Core Local Interruptor) is a RISC-V standard peripheral that provides timer and software interrupts for machine mode. This implementation is designed to support FreeRTOS and other RTOS schedulers that require periodic timer interrupts.

## Features

- **Timer Interrupt** (mtime/mtimecmp)
  - 64-bit timer counter (mtime)
  - 64-bit compare register (mtimecmp)
  - Triggers interrupt when mtime >= mtimecmp
  - Configurable time scaling for realistic timing

- **Software Interrupt** (msip)
  - Inter-processor interrupt support
  - Memory-mapped control register

- **Memory-Mapped Registers**
  - Standard RISC-V CLINT address map
  - 32-bit and 64-bit register access

## Memory Map

Standard RISC-V CLINT addresses:

| Address | Register | Size | Description |
|---------|----------|------|-------------|
| 0x02000000 | msip | 4 bytes | Machine Software Interrupt Pending |
| 0x02004000 | mtimecmp (low) | 4 bytes | Timer compare lower 32 bits |
| 0x02004004 | mtimecmp (high) | 4 bytes | Timer compare upper 32 bits |
| 0x0200bff8 | mtime (low) | 4 bytes | Timer counter lower 32 bits |
| 0x0200bffc | mtime (high) | 4 bytes | Timer counter upper 32 bits |

## Usage

### Basic Timer Setup

```python
from clint import CLINT
from interrupt import InterruptController
from csr import CSRBank

# Create components
csr_bank = CSRBank()
int_ctrl = InterruptController(csr_bank)
clint = CLINT(int_ctrl, time_scale=1)

# Set timer to interrupt after 1000 time units
clint.set_timer_interrupt(1000)

# Tick the timer
for _ in range(1000):
    clint.tick(1)

# Check if interrupt is pending
if int_ctrl.is_pending(int_ctrl.INT_TIMER):
    print("Timer interrupt triggered!")
```

### FreeRTOS Tick Configuration

For FreeRTOS with 1ms ticks at 1MHz CPU frequency:

```python
# Use time_scale=1000 (1000 CPU cycles = 1ms at 1MHz)
clint = CLINT(int_ctrl, time_scale=1000)

# Set up for periodic 1ms ticks
TICK_RATE_MS = 1
clint.set_timer_interrupt(TICK_RATE_MS)

# In timer interrupt handler:
def timer_interrupt_handler():
    # Clear interrupt by setting new mtimecmp
    current_time = clint.read_mtime_64()
    clint.write_mtimecmp_64(current_time + TICK_RATE_MS)
    
    # FreeRTOS tick handling
    # xPortSysTickHandler()
```

### Software Interrupts

```python
# Trigger software interrupt
clint.trigger_software_interrupt()

# In interrupt handler, clear it:
clint.clear_software_interrupt()
```

### Memory-Mapped Access

```python
# Write to mtime (lower 32 bits)
clint.write_register(CLINT.MTIME_BASE, 0x12345678)

# Read from mtime (upper 32 bits)
value = clint.read_register(CLINT.MTIME_BASE + 4)

# 64-bit access
clint.write_mtime_64(0x0000000012345678)
full_time = clint.read_mtime_64()
```

## Pipeline Integration

CLINT is integrated into the pipeline simulator:

```python
from pipeline import Pipeline
import simpy

env = simpy.Environment()
pipeline = Pipeline(env)

# Access CLINT through pipeline
pipeline.clint.set_timer_interrupt(100)

# CLINT ticks automatically during pipeline execution
instructions = ["ADDI R1, R0, 1"] * 50
pipeline.run(instructions)

print(f"Final mtime: {pipeline.clint.mtime}")
```

The CLINT ticks once per pipeline stage completion, incrementing `mtime` based on the configured `time_scale`.

## Time Scaling

The `time_scale` parameter controls how many cycles equal one time unit:

- `time_scale=1`: mtime increments every cycle (default)
- `time_scale=1000`: mtime increments every 1000 cycles (good for ms timing)
- `time_scale=1000000`: mtime increments every 1M cycles (good for second timing)

Example for 100MHz CPU with 10ms ticks:
```python
# 100MHz = 100,000,000 Hz
# 10ms = 0.01s = 1,000,000 cycles at 100MHz
# So time_scale = 1,000,000 / 10 = 100,000

clint = CLINT(int_ctrl, time_scale=100000)
clint.set_timer_interrupt(10)  # 10 time units = 10 * 10ms = 100ms
```

## API Reference

### CLINT Class

#### Constructor
```python
CLINT(interrupt_controller, time_scale=1)
```
- `interrupt_controller`: InterruptController instance
- `time_scale`: Cycles per time unit (default: 1)

#### Methods

**Timer Control:**
- `tick(cycles=1)`: Advance timer by cycles
- `set_timer_interrupt(interval)`: Set interrupt after interval time units
- `clear_timer_interrupt()`: Disable timer interrupt

**Software Interrupts:**
- `trigger_software_interrupt()`: Set software interrupt pending
- `clear_software_interrupt()`: Clear software interrupt

**Register Access:**
- `read_register(address)`: Read 32-bit register
- `write_register(address, value)`: Write 32-bit register
- `read_mtime_64()`: Read full 64-bit mtime
- `write_mtime_64(value)`: Write full 64-bit mtime
- `read_mtimecmp_64()`: Read full 64-bit mtimecmp
- `write_mtimecmp_64(value)`: Write full 64-bit mtimecmp

**Utility:**
- `reset()`: Reset CLINT to initial state
- `get_status()`: Get current timer status

### Status Dictionary

`get_status()` returns:
```python
{
    'mtime': current_time,
    'mtimecmp': compare_value,
    'msip': software_interrupt_bit,
    'timer_pending': bool,
    'cycles_until_interrupt': int
}
```

## Implementation Notes

### Interrupt Clearing

Timer interrupts stay pending after mtime >= mtimecmp. To clear:
1. Write new value to mtimecmp (automatic clear)
2. Set mtimecmp > mtime

Software interrupts must be explicitly cleared:
- Write 0 to msip register
- Call `clear_software_interrupt()`

### 64-bit Registers

The 64-bit `mtime` and `mtimecmp` registers are accessed via two 32-bit memory-mapped registers:
- Lower 32 bits at base address
- Upper 32 bits at base address + 4

When writing mtimecmp, either write clears the timer interrupt.

### Precision

Timer precision depends on `time_scale`:
- Smaller time_scale = higher precision, faster mtime increment
- Larger time_scale = lower precision, slower mtime increment

Choose based on your timing requirements and simulation speed.

## Testing

The implementation includes comprehensive tests:

- **test_clint.py**: 20 tests for CLINT functionality
  - Initialization and defaults
  - Timer increment and scaling
  - Interrupt triggering and clearing
  - Memory-mapped register access
  - Software interrupts
  - Periodic tick scenarios
  - FreeRTOS-style usage

- **test_pipeline_clint.py**: 8 tests for pipeline integration
  - CLINT initialization in pipeline
  - mtime increment during execution
  - Memory-mapped access
  - Software interrupt integration
  - Status reporting

All 28 tests pass successfully.

## Examples

### Example 1: Simple Timer

```python
clint = CLINT(interrupt_controller)

# Set timer for 50 cycles
clint.set_timer_interrupt(50)

# Simulate 50 cycles
for i in range(50):
    clint.tick(1)
    if i == 49:
        assert interrupt_controller.is_pending(InterruptController.INT_TIMER)
```

### Example 2: Periodic Ticks

```python
TICK_INTERVAL = 100

for tick in range(10):
    clint.set_timer_interrupt(TICK_INTERVAL)
    
    # Run until interrupt
    while not interrupt_controller.is_pending(InterruptController.INT_TIMER):
        clint.tick(1)
    
    print(f"Tick {tick} at mtime={clint.mtime}")
    interrupt_controller.clear_pending(InterruptController.INT_TIMER)
```

### Example 3: FreeRTOS Integration

```python
# Setup for 1kHz tick rate (1ms ticks) at 1MHz
clint = CLINT(interrupt_controller, time_scale=1000)

def vPortSetupTimerInterrupt():
    """FreeRTOS port timer setup"""
    clint.set_timer_interrupt(1)  # 1 time unit = 1ms

def xPortSysTickHandler():
    """FreeRTOS tick handler"""
    # Increment tick count
    vTaskIncrementTick()
    
    # Set next interrupt
    current = clint.read_mtime_64()
    clint.write_mtimecmp_64(current + 1)
```

## Future Enhancements

Potential improvements:
1. Multiple hart (CPU core) support
2. Vectored interrupt mode integration
3. Performance counters
4. Watchdog timer support
5. Real-time clock (RTC) integration
6. Power management (timer disable/enable)
7. Prescaler for more flexible timing

## References

- RISC-V Privileged Architecture Specification
- SiFive E31/E51 Manual (CLINT implementation)
- FreeRTOS RISC-V Port Documentation
