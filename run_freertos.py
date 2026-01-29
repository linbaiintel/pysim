#!/usr/bin/env python3
"""
Run FreeRTOS binary on RISC-V simulator

This script:
1. Loads the FreeRTOS ELF file into memory
2. Initializes the simulator with proper entry point
3. Runs the simulation with timer interrupts for FreeRTOS
"""

import sys
import os
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent / 'utils'))

from elf_loader import ELFTestLoader, RISCVDecoder
from riscv import RISCVProcessor
import simpy


def load_elf_to_memory(elf_path, processor):
    """
    Load ELF file into processor memory
    
    Args:
        elf_path: Path to ELF file
        processor: RISCVProcessor instance
        
    Returns:
        entry_point: Entry point address from ELF
    """
    print(f"Loading ELF file: {elf_path}")
    loader = ELFTestLoader(elf_path)
    
    # Load ELF into memory dictionary
    memory_dict, entry_point = loader.load()
    
    print(f"  Entry point: 0x{entry_point:08x}")
    print(f"  Loaded {len(memory_dict)} bytes into memory")
    
    # Copy memory into simulator's byte-addressed memory
    for addr, value in memory_dict.items():
        processor.memory.data[addr] = value
    
    return entry_point, loader


def decode_instructions_from_memory(processor, start_pc, max_instructions=50000):
    """
    Decode instructions from memory starting at PC
    
    Args:
        processor: RISCVProcessor with loaded memory
        start_pc: Starting PC address
        max_instructions: Maximum number of instructions to decode
        
    Returns:
        List of decoded instruction strings
    """
    instructions = []
    pc = start_pc
    
    print(f"\nDecoding instructions from 0x{start_pc:08x}...")
    
    for i in range(max_instructions):
        try:
            # Read 4-byte instruction (little-endian)
            word = processor.memory.read_word(pc)
            
            # Decode instruction
            instr_str = RISCVDecoder.decode(word)
            
            if instr_str is None:
                print(f"  WARNING: Failed to decode instruction at 0x{pc:08x}: 0x{word:08x}")
                break
            
            instructions.append(instr_str)
            pc += 4
            
            # Stop at ECALL or infinite loop (common end patterns)
            if word == 0x00000073:  # ECALL
                print(f"  Found ECALL at instruction {i+1}, stopping decode")
                break
            
            # Detect infinite loop: JAL x0, -4 (jump to self)
            if word == 0xffdff06f:
                print(f"  Found infinite loop at instruction {i+1}, stopping decode")
                break
                
        except Exception as e:
            print(f"  ERROR at PC 0x{pc:08x}: {e}")
            break
    
    print(f"  Decoded {len(instructions)} instructions")
    return instructions


def print_first_instructions(instructions, count=20):
    """Print first N instructions"""
    print(f"\nFirst {min(count, len(instructions))} instructions:")
    for i, instr in enumerate(instructions[:count]):
        print(f"  [{i:4d}] {instr}")
    if len(instructions) > count:
        print(f"  ... ({len(instructions) - count} more instructions)")


def dump_memory_to_file(processor, filename="memory_dump.txt", max_addr=0x20000):
    """
    Dump memory contents to a text file
    
    Args:
        processor: RISCVProcessor instance
        filename: Output file name
        max_addr: Maximum address to dump (default 128KB)
    """
    print(f"\nDumping memory to {filename}...")
    
    with open(filename, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("FreeRTOS Memory Dump After ELF Loading\n")
        f.write("=" * 80 + "\n\n")
        
        # Find non-zero memory regions
        regions = []
        in_region = False
        region_start = 0
        
        for addr in range(0, max_addr):
            byte_val = processor.memory.data[addr]
            if byte_val != 0:
                if not in_region:
                    region_start = addr
                    in_region = True
            else:
                if in_region:
                    regions.append((region_start, addr - 1))
                    in_region = False
        
        if in_region:
            regions.append((region_start, max_addr - 1))
        
        f.write(f"Total memory regions with data: {len(regions)}\n")
        f.write(f"Scanned address range: 0x00000000 - 0x{max_addr:08x}\n\n")
        
        for i, (start, end) in enumerate(regions):
            size = end - start + 1
            f.write(f"Region {i+1}: 0x{start:08x} - 0x{end:08x} ({size} bytes)\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("Detailed Memory Contents (Hex Dump)\n")
        f.write("=" * 80 + "\n\n")
        
        # Dump each region in hex format
        for i, (start, end) in enumerate(regions):
            f.write(f"\n{'─' * 80}\n")
            f.write(f"Region {i+1}: 0x{start:08x} - 0x{end:08x}\n")
            f.write(f"{'─' * 80}\n\n")
            
            # Align to 16-byte boundaries for cleaner output
            aligned_start = (start // 16) * 16
            aligned_end = ((end + 15) // 16) * 16
            
            for addr in range(aligned_start, aligned_end, 16):
                # Address
                f.write(f"0x{addr:08x}  ")
                
                # Hex bytes
                hex_bytes = []
                ascii_chars = []
                for j in range(16):
                    byte_addr = addr + j
                    if byte_addr < start or byte_addr > end or byte_addr >= max_addr:
                        hex_bytes.append("  ")
                        ascii_chars.append(" ")
                    else:
                        byte_val = processor.memory.data[byte_addr]
                        hex_bytes.append(f"{byte_val:02x}")
                        # ASCII representation
                        if 32 <= byte_val <= 126:
                            ascii_chars.append(chr(byte_val))
                        else:
                            ascii_chars.append(".")
                
                # Print hex in groups of 4
                f.write(" ".join(hex_bytes[0:4]) + "  ")
                f.write(" ".join(hex_bytes[4:8]) + "  ")
                f.write(" ".join(hex_bytes[8:12]) + "  ")
                f.write(" ".join(hex_bytes[12:16]) + "  ")
                
                # ASCII representation
                f.write("|" + "".join(ascii_chars) + "|\n")
        
        # Add instruction disassembly for .text section
        f.write("\n\n" + "=" * 80 + "\n")
        f.write("Instruction Disassembly (.text section)\n")
        f.write("=" * 80 + "\n\n")
        
        pc = 0
        for instr_num in range(min(100, len(regions[0]) // 4 if regions else 0)):
            addr = pc + instr_num * 4
            try:
                word = processor.memory.read_word(addr)
                decoded = RISCVDecoder.decode(word)
                f.write(f"0x{addr:08x}:  {word:08x}  {decoded}\n")
            except:
                break
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("End of Memory Dump\n")
        f.write("=" * 80 + "\n")
    
    print(f"  Memory dump saved to {filename}")
    print(f"  Found {len(regions)} non-zero memory regions")
    if regions:
        total_bytes = sum(end - start + 1 for start, end in regions)
        print(f"  Total data size: {total_bytes} bytes")


def run_freertos(elf_path, max_cycles=100000, verbose=True):
    """
    Run FreeRTOS ELF on simulator
    
    Args:
        elf_path: Path to FreeRTOS ELF file
        max_cycles: Maximum simulation cycles
        verbose: Print detailed execution trace
    """
    print("=" * 70)
    print("FreeRTOS RISC-V Simulator")
    print("=" * 70)
    
    # Create processor
    processor = RISCVProcessor(enable_forwarding=False)
    
    # Load ELF file
    entry_point, loader = load_elf_to_memory(elf_path, processor)
    
    # Initialize stack pointer (from linker script: top of RAM)
    # FreeRTOS uses _stack_start symbol, which should be at RAM_BASE + RAM_SIZE
    stack_pointer = 0x100000  # 1MB (end of RAM defined in linker.ld)
    processor.register_file.write('R2', stack_pointer)  # R2 = sp
    print(f"\nInitialized stack pointer: 0x{stack_pointer:08x}")
    
    # Set PC to entry point
    processor.register_file.write_pc(entry_point)
    print(f"Set PC to entry point: 0x{entry_point:08x}")
    
    # Decode instructions from memory
    instructions = decode_instructions_from_memory(processor, entry_point, max_instructions=50000)
    
    if not instructions:
        print("\nERROR: No instructions decoded!")
        return
    
    # Show first few instructions
    print_first_instructions(instructions, count=30)
    
    # Dump memory to file for inspection
    dump_memory_to_file(processor, filename="freertos_memory_dump.txt", max_addr=0x20000)
    
    # Configure CLINT for timer interrupts (important for FreeRTOS)
    print("\n" + "=" * 70)
    print("Configuring CLINT timer for FreeRTOS...")
    print("  MTIME base:    0x0200BFF8")
    print("  MTIMECMP base: 0x02004000")
    print("  MSIP base:     0x02000000")
    print("=" * 70)
    
    # Run simulation
    print(f"\nStarting simulation (max {max_cycles} cycles)...")
    print("=" * 70)
    print("UART Output:")
    print("-" * 70)
    
    try:
        # Execute with verbose output
        results = processor.execute(instructions, verbose=verbose)
        
        print("-" * 70)
        print("\n" + "=" * 70)
        print("Simulation Complete")
        print("=" * 70)
        print(f"Total cycles:              {results['total_cycles']}")
        print(f"Instructions completed:    {results['completed_instructions']}")
        print(f"Stalls:                    {results['stall_count']}")
        print(f"Bubbles:                   {results['bubble_count']}")
        print(f"CPI (Cycles per Instr):    {results['cpi']:.2f}")
        print(f"IPC (Instr per Cycle):     {results['ipc']:.2f}")
        
        # Show final register state
        print("\n" + "=" * 70)
        print("Final Register State (non-zero):")
        print("=" * 70)
        reg_state = processor.get_register_state()
        for reg, value in sorted(reg_state.items()):
            print(f"  {reg:4s} = 0x{value:08x} ({value:10d})")
        
    except KeyboardInterrupt:
        print("\n\n*** Simulation interrupted by user ***")
    except Exception as e:
        print(f"\n\n*** Simulation error: {e} ***")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run FreeRTOS on RISC-V simulator')
    parser.add_argument('elf_file', nargs='?', 
                       default='freertos_demo/freertos_demo.elf',
                       help='Path to FreeRTOS ELF file')
    parser.add_argument('--max-cycles', type=int, default=100000,
                       help='Maximum simulation cycles (default: 100000)')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress detailed execution trace')
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.elf_file):
        print(f"ERROR: ELF file not found: {args.elf_file}")
        print("\nAvailable files in freertos_demo/:")
        demo_dir = Path('freertos_demo')
        if demo_dir.exists():
            for f in sorted(demo_dir.glob('freertos_demo.*')):
                print(f"  {f}")
        sys.exit(1)
    
    run_freertos(args.elf_file, max_cycles=args.max_cycles, verbose=not args.quiet)
