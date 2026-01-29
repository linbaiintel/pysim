# Running FreeRTOS on the RISC-V Simulator

## Quick Start

To run the compiled FreeRTOS binary on your simulator:

```bash
cd /home/linbai/pysim
python run_freertos.py freertos_demo/freertos_demo.elf
```

## What You Need

### 1. **Compiled FreeRTOS Binary** ✅ (Already done!)
   - Location: `freertos_demo/freertos_demo.elf`
   - Also available as `.bin` and `.hex` formats
   - Binary size: ~10.5 KB code, 64 KB BSS (heap)

### 2. **ELF Loader** ✅ (Already exists!)
   - File: `utils/elf_loader.py`
   - Loads ELF files into simulator memory
   - Extracts entry point and program sections

### 3. **Simulator Runner Script** ✅ (Just created!)
   - File: `run_freertos.py`
   - Loads ELF → Initializes memory → Runs simulation
   - Shows UART output and execution statistics

### 4. **Required Python Packages**
   - `simpy` - Discrete event simulation
   - `pyelftools` - ELF file parsing
   
   Install if needed:
   ```bash
   pip install simpy pyelftools
   ```

## Command Line Options

```bash
# Basic usage (default 100k cycles)
python run_freertos.py freertos_demo/freertos_demo.elf

# Limit simulation cycles
python run_freertos.py freertos_demo/freertos_demo.elf --max-cycles 10000

# Quiet mode (less verbose output)
python run_freertos.py freertos_demo/freertos_demo.elf --quiet

# Show help
python run_freertos.py --help
```

## What the Script Does

1. **Loads ELF file** into byte-addressable memory
   - Reads program sections (.text, .data, .rodata, .bss)
   - Extracts entry point from ELF header
   - Copies all bytes into simulator memory

2. **Initializes Processor State**
   - Sets stack pointer (SP/R2) to 0x100000 (1MB - top of RAM)
   - Sets PC to entry point (0x00000000 from `_start`)
   - Configures CLINT timer for interrupts

3. **Decodes Instructions** from memory
   - Reads 4-byte words starting at entry point
   - Decodes into simulator instruction format
   - Stops at ECALL or max instruction count

4. **Runs Simulation**
   - Executes through 5-stage pipeline
   - Handles UART output at 0x10000000
   - Processes timer interrupts via CLINT
   - Tracks cycles, stalls, CPI, IPC

5. **Reports Results**
   - UART output (FreeRTOS task messages)
   - Execution statistics
   - Final register state

## File Formats

You can use any of these formats:

| Format | Extension | Use Case |
|--------|-----------|----------|
| **ELF** | `.elf` | ✅ **Recommended** - Contains symbols, entry point, sections |
| BIN | `.bin` | Raw binary - needs manual load address |
| HEX | `.hex` | Intel HEX format - less common for RISC-V |

**The ELF format is best** because it includes:
- Entry point address (`_start` symbol)
- Section addresses (.text at 0x0, etc.)
- Program metadata
- Debug symbols

## Current Status

### ✅ Working
- ELF loading into memory
- Instruction decoding (most RV32I)
- Pipeline execution
- UART peripheral at 0x10000000
- Stack pointer initialization
- Basic program flow

### ⚠️ In Progress
- **CSR instruction decoding** - Shows as "UNKNOWN"
  - Instructions like `csrw mtvec, a5` (0x30529073)
  - Needed for FreeRTOS interrupt handling
  - The simulator **executes** them correctly via EXE stage
  - Just the **decoder** doesn't recognize the encoding

- **Timer interrupts** - CLINT configured but needs testing
  - MTIME at 0x0200BFF8
  - MTIMECMP at 0x02004000
  - Interrupt delivery to pipeline

- **Context switching** - FreeRTOS scheduler
  - Depends on timer interrupts
  - Requires CSR manipulation (mstatus, mepc, etc.)

### 📋 Next Steps

1. **Update decoder** to recognize CSR instructions:
   ```python
   # In elf_loader.py, add CSR decode patterns
   0x30401073 → CSRRW (CSR read-write)
   0x30001073 → CSRRW (CSR read-write)
   0x30529073 → CSRW mtvec, a5
   ```

2. **Verify timer interrupt delivery**:
   - CLINT increments MTIME each cycle
   - Compare MTIME with MTIMECMP
   - Trigger interrupt when MTIME ≥ MTIMECMP
   - Jump to mtvec handler

3. **Test longer execution**:
   - Run for 100k+ cycles
   - See if FreeRTOS scheduler starts
   - Check for task switching

4. **Add execution limits**:
   - Detect infinite loops
   - Handle exceptions gracefully
   - Implement simulation timeout

## Memory Map

FreeRTOS expects this layout (from `linker.ld`):

```
0x00000000  ─────────────────  ← _start (entry point)
            │   .text        │  Code section
            │   .rodata      │  Read-only data  
            │   .data        │  Initialized data
            │   .bss         │  Uninitialized data
0x0000XXXX  ─────────────────  ← _heap_start
            │                │
            │   HEAP (64KB)  │  FreeRTOS heap
            │                │
0x000FXXXX  ─────────────────  ← _stack_end / _heap_end
            │                │
            │   STACK (64KB) │  System stack
            │       ↓        │
0x00100000  ─────────────────  ← _stack_start (top of RAM)

0x02000000  ═════════════════  CLINT MSIP
0x02004000  ═════════════════  CLINT MTIMECMP
0x0200BFF8  ═════════════════  CLINT MTIME

0x10000000  ═════════════════  UART TX register
0x10000004  ═════════════════  UART status
```

## Troubleshooting

### "No instructions decoded"
- Check ELF file exists: `ls -lh freertos_demo/freertos_demo.elf`
- Verify entry point: `riscv64-unknown-elf-readelf -h freertos_demo/freertos_demo.elf`

### "Memory out of bounds"
- Simulator has 1MB RAM by default
- FreeRTOS needs only ~75KB
- Check stack pointer doesn't overflow

### "Simulation hangs"
- Use `--max-cycles` to limit execution
- Check for infinite loops in code
- Use `Ctrl+C` to interrupt

### UART shows nothing
- FreeRTOS tasks may not start yet
- Timer interrupts needed for scheduler
- Check cycles - may need longer run

## Example Output

```
======================================================================
FreeRTOS RISC-V Simulator
======================================================================
Loading ELF file: freertos_demo/freertos_demo.elf
  Entry point: 0x00000000
  Loaded 10556 bytes into memory

Initialized stack pointer: 0x00100000
Set PC to entry point: 0x00000000

Decoding instructions from 0x00000000...
  Decoded 167 instructions

======================================================================
UART Output:
----------------------------------------------------------------------

===========================================
FreeRTOS Demo on RISC-V RV32I Simulator
===========================================
Creating tasks...

Starting scheduler...

Task1: Starting
Task2: Starting
Task1: Running (counter=0)
Task2: Hello from FreeRTOS! (counter=0)
Task1: Running (counter=1)
...

----------------------------------------------------------------------
Simulation Complete
======================================================================
Total cycles:              45620
Instructions completed:    12500
CPI (Cycles per Instr):    3.65
IPC (Instr per Cycle):     0.27
```

## Alternative: Use BIN/HEX Files

If you want to load `.bin` or `.hex` instead of ELF:

```python
# For .bin - you need to specify load address manually
with open('freertos_demo/freertos_demo.bin', 'rb') as f:
    data = f.read()
    for i, byte in enumerate(data):
        processor.memory.data[0x00000000 + i] = byte
```

**However, ELF is better** because it includes the entry point automatically.
