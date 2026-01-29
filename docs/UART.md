# UART Peripheral Implementation

## Overview

A simple memory-mapped UART peripheral has been added to the RISC-V simulator to enable character output, which is essential for `printf()` support in FreeRTOS and bare-metal applications.

## Memory Map

| Address | Register | Access | Description |
|---------|----------|--------|-------------|
| 0x10000000 | TX_DATA | Write | UART transmit data register (write byte to print) |
| 0x10000004 | STATUS | Read | UART status register (bit 0 = TX ready, always 1) |

## Features

- **Character Output**: Write a byte to 0x10000000 to transmit it to the terminal
- **Always Ready**: Status register always indicates ready (simplified for simulation)
- **Automatic Flushing**: Characters appear immediately on stdout
- **Integrated with Memory**: Works seamlessly with load/store instructions

## Usage in Assembly

### Simple Character Output
```assembly
# Print 'H' (ASCII 72)
ADDI R1, R0, 72        # R1 = 'H'
LUI R2, 0x10000        # R2 = 0x10000000 (UART base)
SW R1, 0(R2)           # Write to UART TX register
```

### String Output Loop
```assembly
# Assume string address in R3, length in R4
LUI R5, 0x10000        # R5 = UART base
ADDI R6, R0, 0         # R6 = counter = 0

loop:
LB R1, 0(R3)           # Load character
SW R1, 0(R5)           # Print character
ADDI R3, R3, 1         # Increment pointer
ADDI R6, R6, 1         # Increment counter
BNE R6, R4, loop       # Loop if not done
```

## Usage in C (for FreeRTOS)

### Define UART Address
```c
#define UART_TX_REG  ((volatile char*)0x10000000)
#define UART_STATUS  ((volatile uint32_t*)0x10000004)
```

### Simple Putchar Function
```c
void uart_putc(char c) {
    *UART_TX_REG = c;
}

void uart_puts(const char *str) {
    while (*str) {
        uart_putc(*str++);
    }
}
```

### Printf Support (Newlib)
To enable `printf()` with newlib, implement the `_write()` syscall:

```c
#include <sys/types.h>

int _write(int fd, const void *buf, size_t count) {
    volatile char *uart = (char*)0x10000000;
    
    if (fd == 1 || fd == 2) {  // stdout or stderr
        for (size_t i = 0; i < count; i++) {
            uart[0] = ((char*)buf)[i];
        }
        return count;
    }
    
    return -1;
}
```

Then in your FreeRTOS tasks:
```c
void vTaskExample(void *pvParameters) {
    printf("Hello from FreeRTOS task!\n");
    printf("Counter: %d\n", 42);
    
    for(;;) {
        vTaskDelay(pdMS_TO_TICKS(1000));
        printf("Task running...\n");
    }
}
```

## Integration with Simulator

The UART is automatically integrated into the pipeline:

```python
# In pipeline.py
from uart import UART

class Pipeline:
    def __init__(self, env):
        self.uart = UART()
        self.memory = Memory(uart=self.uart, clint=self.clint)
```

The Memory class automatically routes reads/writes to UART addresses to the UART peripheral.

## Testing

Run the UART test suite:
```bash
python examples/uart_test.py
```

Tests include:
1. Basic character output
2. String output from memory
3. Function calls (putchar-style)
4. Status register reads

## Example Output

```
======================================================================
UART Test 1: Basic Character Output
======================================================================
Running program to print 'Hello!' via UART...
----------------------------------------------------------------------
UART Output: Hello!
----------------------------------------------------------------------
✓ Test completed: 7 characters transmitted
```

## Implementation Details

### UART Class ([uart.py](../uart.py))
- Simple memory-mapped peripheral
- Writes to TX register print to stdout
- Status register always returns 0x01 (ready)
- Tracks character transmission count

### Memory Integration ([memory.py](../memory.py))
- Checks UART address range before normal memory access
- Routes UART writes/reads to UART peripheral
- Supports byte and word access to UART registers

## FreeRTOS Integration

With this UART implementation, FreeRTOS applications can:
- Print debug messages from tasks
- Log scheduler events
- Display task status
- Output diagnostic information
- Use standard printf() formatting

This makes debugging and monitoring FreeRTOS behavior much easier!

## Future Enhancements

Potential additions:
- RX (receive) support for input
- Interrupt generation on receive
- FIFO buffers for TX/RX
- Baud rate emulation
- Multiple UART instances

## Related Files

- [uart.py](../uart.py) - UART peripheral implementation
- [memory.py](../memory.py) - Memory with UART integration
- [pipeline.py](../pipeline.py) - Pipeline with UART
- [examples/uart_test.py](../examples/uart_test.py) - UART test suite
