# FreeRTOS Demo for RISC-V RV32I Simulator

This directory contains a minimal FreeRTOS configuration for the RISC-V RV32I simulator.

## Configuration

- **ISA**: RV32I (no extensions)
- **Interrupt Controller**: CLINT (Core Local Interruptor)
- **Memory**: 1MB RAM starting at 0x00000000
- **UART**: 0x10000000 for printf support
- **Tick Rate**: 1000 Hz (1ms ticks)
- **CPU Clock**: 1 MHz (simulated)
- **Memory Allocator**: heap_4 (64KB heap)

## File Structure

```
freertos_demo/
├── FreeRTOSConfig.h      - FreeRTOS configuration
├── main.c                - Demo application (2 tasks)
├── startup.S             - Startup code
├── linker.ld             - Linker script
├── Makefile              - Build system
└── README.md             - This file
```

## Prerequisites

### RISC-V Toolchain

You need the RISC-V GNU toolchain:

```bash
# Ubuntu/Debian
sudo apt-get install gcc-riscv64-unknown-elf

# Or build from source
git clone https://github.com/riscv/riscv-gnu-toolchain
cd riscv-gnu-toolchain
./configure --prefix=/opt/riscv --with-arch=rv32i --with-abi=ilp32
make
export PATH=/opt/riscv/bin:$PATH
```

### FreeRTOS Kernel

Already included as submodule at `../3rd_party/FreeRTOS-Kernel/`

## Building

```bash
# Check toolchain
riscv32-unknown-elf-gcc --version

# Build the demo
cd freertos_demo
make

# Check binary size
make size
```

This will create:
- `freertos_demo.elf` - Executable with debug info
- `freertos_demo.bin` - Raw binary
- `freertos_demo.hex` - Intel hex format
- `freertos_demo.lst` - Disassembly listing

## Running on Simulator

### Option 1: Load ELF (Future)
```python
from riscv import RISCVProcessor
from utils.elf_loader import load_elf

processor = RISCVProcessor()
load_elf("freertos_demo/freertos_demo.elf", processor)
processor.execute_from(entry_point)
```

### Option 2: Current Simulator Tests

For now, use the Python-based FreeRTOS demos:
```bash
# Simple scheduler demo
python examples/freertos_simple_demo.py

# Full FreeRTOS-style demo
python examples/freertos_demo.py
```

## Demo Application

The demo creates two tasks:

**Task 1** (Priority 1):
- Prints message every 500ms
- Simulates LED blinking

**Task 2** (Priority 2):
- Prints message every 1000ms
- Higher priority than Task 1

Both tasks use `printf()` via UART at 0x10000000.

## Expected Output

```
===========================================
FreeRTOS Demo on RISC-V RV32I Simulator
===========================================
Tick Rate: 1000 Hz
CPU Clock: 1000000 Hz
Creating tasks...

Starting scheduler...

Task1: Starting
Task2: Starting
Task2: Hello from FreeRTOS! (counter=0)
Task1: Running (counter=0)
Task1: Running (counter=1)
Task2: Hello from FreeRTOS! (counter=1)
...
```

## Memory Usage

Typical memory layout:
```
Code (text):     ~20KB (FreeRTOS kernel + demo)
Data:            ~2KB
BSS:             ~2KB
Heap:            64KB (configurable)
Stack:           64KB (per task: 128 bytes minimum)
```

## Customization

### Change Tick Rate
Edit `FreeRTOSConfig.h`:
```c
#define configTICK_RATE_HZ    ( ( TickType_t ) 1000 )  // 1ms ticks
```

### Change Heap Size
```c
#define configTOTAL_HEAP_SIZE ( ( size_t ) ( 64 * 1024 ) )  // 64KB
```

### Add More Tasks
In `main.c`:
```c
xTaskCreate(vMyTask, "MyTask", configMINIMAL_STACK_SIZE, NULL, 1, NULL);
```

### Enable Features
In `FreeRTOSConfig.h`:
```c
#define configUSE_MUTEXES                       1
#define configUSE_COUNTING_SEMAPHORES           1
#define configUSE_QUEUE_SETS                    1
```

## Debugging

### Disassembly
```bash
riscv32-unknown-elf-objdump -d freertos_demo.elf > disasm.txt
```

### Memory Map
```bash
riscv32-unknown-elf-nm -n freertos_demo.elf > symbols.txt
```

### Size Analysis
```bash
riscv32-unknown-elf-size -A freertos_demo.elf
```

## Troubleshooting

### Build Errors

**Error**: `riscv32-unknown-elf-gcc: command not found`
- Install RISC-V toolchain (see Prerequisites)

**Error**: `No such file or directory: FreeRTOS.h`
- Ensure FreeRTOS-Kernel submodule is initialized:
  ```bash
  git submodule update --init --recursive
  ```

### Runtime Issues

**Stack Overflow**:
- Increase `configMINIMAL_STACK_SIZE` in FreeRTOSConfig.h
- Enable `configCHECK_FOR_STACK_OVERFLOW`

**Malloc Failed**:
- Increase `configTOTAL_HEAP_SIZE`
- Check memory usage with `size` tool

## References

- [FreeRTOS Documentation](https://www.freertos.org/Documentation/00-Overview)
- [RISC-V Spec](https://riscv.org/technical/specifications/)
- [FreeRTOS RISC-V Port](https://www.freertos.org/Using-FreeRTOS-on-RISC-V.html)
- [Simulator Documentation](../docs/)

## Next Steps

1. Build the demo: `make`
2. Examine the output: `make size`
3. Review disassembly: look at `.lst` file
4. Modify tasks in `main.c`
5. Add your own functionality
6. Integrate with simulator's ELF loader

## License

- FreeRTOS: MIT License
- Demo code: MIT License
- See individual files for details
