#!/usr/bin/env python3
"""
Demo of JAL and JALR jump instructions
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from riscv import RISCVProcessor


def demo_jal():
    """Demonstrate JAL (Jump And Link) instruction"""
    print("=" * 70)
    print("JAL (Jump And Link) Demonstration")
    print("=" * 70)
    print("\nJAL stores the return address (PC+4) in destination register")
    print("and jumps to PC + offset\n")
    
    processor = RISCVProcessor()
    processor.register_file.write_pc(0x1000)  # Set initial PC
    
    program = [
        "JAL R1, 100",     # Jump to PC + 100, store return address in R1
    ]
    
    print("Program:")
    for i, instr in enumerate(program):
        print(f"  {i}: {instr}")
    
    print("\nInitial PC: 0x1000")
    print("\nExecution:")
    processor.execute(program)
    
    print("\nResults:")
    print(f"  R1 (return address) = {processor.get_register('R1'):#010x} (PC + 4 = 0x1000 + 4)")
    print(f"  Jump target would be = 0x1064 (PC + 100 = 0x1000 + 0x64)")


def demo_jalr():
    """Demonstrate JALR (Jump And Link Register) instruction"""
    print("\n" + "=" * 70)
    print("JALR (Jump And Link Register) Demonstration")
    print("=" * 70)
    print("\nJALR stores the return address (PC+4) in destination register")
    print("and jumps to (rs1 + offset) & ~1 (clears LSB)\n")
    
    processor = RISCVProcessor()
    processor.register_file.write("R2", 0x2000)  # Base address
    processor.register_file.write_pc(0x1000)     # Set initial PC
    
    program = [
        "JALR R1, R2, 50",  # Jump to R2 + 50, store return address in R1
    ]
    
    print("Program:")
    for i, instr in enumerate(program):
        print(f"  {i}: {instr}")
    
    print("\nInitial state:")
    print(f"  PC = 0x1000")
    print(f"  R2 = 0x2000")
    print("\nExecution:")
    processor.execute(program)
    
    print("\nResults:")
    print(f"  R1 (return address) = {processor.get_register('R1'):#010x} (PC + 4 = 0x1000 + 4)")
    print(f"  Jump target would be = 0x2032 (R2 + 50 = 0x2000 + 0x32)")


def demo_function_call():
    """Demonstrate function call pattern with JAL and JALR"""
    print("\n" + "=" * 70)
    print("Function Call Pattern (JAL + JALR)")
    print("=" * 70)
    print("\nSimulates: call function, execute function, return")
    print("(Note: pipeline flush not implemented, so instructions run sequentially)\n")
    
    processor = RISCVProcessor()
    processor.register_file.write("R10", 5)      # Argument
    processor.register_file.write("R11", 10)     # Argument
    processor.register_file.write_pc(0x1000)     # Initial PC
    
    program = [
        "JAL R1, 20",           # Call function at PC+20, save return in R1
        "ADD R12, R10, R11",    # Code after function call
        # Simulated function body:
        "ADDI R10, R10, 1",     # Increment R10
        "JALR R0, R1, 0",       # Return to caller (jump to address in R1)
    ]
    
    print("Program (simulating function call):")
    for i, instr in enumerate(program):
        print(f"  {i}: {instr}")
    
    print("\nInitial state:")
    print(f"  PC = 0x1000")
    print(f"  R10 = 5")
    print(f"  R11 = 10")
    
    print("\nExecution:")
    processor.execute(program)
    
    print("\nResults:")
    print(f"  R1 (return address) = {processor.get_register('R1'):#010x}")
    print(f"  R10 (modified) = {processor.get_register('R10')}")
    print(f"  R12 (sum) = {processor.get_register('R12')}")
    
    print("\nNote: In a real implementation with PC tracking and pipeline flush,")
    print("the function would execute at PC+20 and return would jump back.")


def demo_jalr_computed_address():
    """Demonstrate JALR with computed target address"""
    print("\n" + "=" * 70)
    print("JALR with Computed Address")
    print("=" * 70)
    print("\nJALR can jump to an address computed at runtime\n")
    
    processor = RISCVProcessor()
    processor.register_file.write("R2", 0x1000)  # Base
    processor.register_file.write_pc(0x2000)     # Initial PC
    
    program = [
        "ADDI R3, R2, 256",   # Compute target: R3 = R2 + 256
        "JALR R1, R3, 0",     # Jump to address in R3
    ]
    
    print("Program:")
    for i, instr in enumerate(program):
        print(f"  {i}: {instr}")
    
    print("\nInitial state:")
    print(f"  PC = 0x2000")
    print(f"  R2 = 0x1000")
    
    print("\nExecution:")
    processor.execute(program)
    
    print("\nResults:")
    print(f"  R3 (computed address) = {processor.get_register('R3'):#010x}")
    print(f"  R1 (return address) = {processor.get_register('R1'):#010x}")
    print(f"  Jump target would be = {processor.get_register('R3'):#010x}")


def main():
    print("\n" + "=" * 70)
    print("RISC-V Jump Instructions (JAL/JALR) Demo")
    print("=" * 70)
    print()
    
    demo_jal()
    demo_jalr()
    demo_function_call()
    demo_jalr_computed_address()
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print("""
JAL (Jump And Link):
  - Syntax: JAL rd, offset
  - Stores PC+4 in rd (return address)
  - Jumps to PC + offset
  - Used for function calls with fixed offsets

JALR (Jump And Link Register):
  - Syntax: JALR rd, rs1, offset
  - Stores PC+4 in rd (return address)
  - Jumps to (rs1 + offset) & ~1 (LSB cleared)
  - Used for returns, computed jumps, indirect calls
  
Current Implementation:
  ✓ JAL and JALR execution
  ✓ Return address calculation (PC+4)
  ✓ Jump target calculation
  ✓ LSB clearing for JALR (RISC-V spec compliance)
  ⚠ Pipeline flush not implemented (instructions run sequentially)
  ⚠ PC doesn't update to jump target (would need fetch stage changes)
""")
    print("=" * 70)


if __name__ == "__main__":
    main()
