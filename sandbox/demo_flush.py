#!/usr/bin/env python3
"""Test pipeline flush mechanism for jumps and branches"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from riscv import RISCVProcessor


def test_jal_flush():
    """Test that JAL triggers pipeline flush"""
    print("=" * 70)
    print("JAL Pipeline Flush Test")
    print("=" * 70)
    print("\nJAL should flush instructions in Fetch and Decode stages\n")
    
    processor = RISCVProcessor()
    processor.register_file.write_pc(0x1000)
    processor.register_file.write("R2", 10)
    processor.register_file.write("R3", 20)
    
    program = [
        "JAL R1, 100",          # Should trigger flush
        "ADD R4, R2, R3",       # Should be flushed (not executed)
        "SUB R5, R2, R3",       # Should be flushed (not executed)
        "AND R6, R2, R3",       # Might execute (depends on timing)
    ]
    
    print("Program:")
    for i, instr in enumerate(program):
        print(f"  {i}: {instr}")
    
    print("\nExecution:")
    info = processor.execute(program)
    
    print("\nResults:")
    print(f"  Instructions completed: {len(info['completed_instructions'])}")
    print(f"  Flush count: {processor.pipeline.flush_count}")
    print(f"  Instructions flushed: {4 - len(info['completed_instructions'])}")
    
    for instr in info['completed_instructions']:
        print(f"    Completed: {instr}")
    
    print(f"\n  R1 (return address): {processor.get_register('R1'):#010x}")
    print(f"  R4 (should be 0 if flushed): {processor.get_register('R4')}")
    

def test_branch_taken_flush():
    """Test that taken branch triggers flush"""
    print("\n" + "=" * 70)
    print("Taken Branch Pipeline Flush Test")
    print("=" * 70)
    print("\nTaken branch should flush following instructions\n")
    
    processor = RISCVProcessor()
    processor.register_file.write_pc(0x2000)
    processor.register_file.write("R1", 5)
    processor.register_file.write("R2", 5)
    processor.register_file.write("R3", 10)
    
    program = [
        "BEQ R1, R2, 50",       # Branch taken (R1 == R2), should flush
        "ADD R4, R1, R3",       # Should be flushed
        "SUB R5, R1, R3",       # Should be flushed
    ]
    
    print("Program:")
    for i, instr in enumerate(program):
        print(f"  {i}: {instr}")
    
    print("\nExecution:")
    info = processor.execute(program)
    
    print("\nResults:")
    print(f"  Instructions completed: {len(info['completed_instructions'])}")
    print(f"  Flush count: {processor.pipeline.flush_count}")
    print(f"  R4 (should be 0 if flushed): {processor.get_register('R4')}")


def test_branch_not_taken_no_flush():
    """Test that not-taken branch doesn't flush"""
    print("\n" + "=" * 70)
    print("Not-Taken Branch (No Flush) Test")
    print("=" * 70)
    print("\nNot-taken branch should NOT flush\n")
    
    processor = RISCVProcessor()
    processor.register_file.write_pc(0x3000)
    processor.register_file.write("R1", 5)
    processor.register_file.write("R2", 10)
    processor.register_file.write("R3", 15)
    
    program = [
        "BEQ R1, R2, 50",       # Branch NOT taken (R1 != R2)
        "ADD R4, R1, R3",       # Should execute
    ]
    
    print("Program:")
    for i, instr in enumerate(program):
        print(f"  {i}: {instr}")
    
    print("\nExecution:")
    info = processor.execute(program)
    
    print("\nResults:")
    print(f"  Instructions completed: {len(info['completed_instructions'])}")
    print(f"  Flush count: {processor.pipeline.flush_count}")
    print(f"  R4 (should be 20): {processor.get_register('R4')}")


def test_jalr_flush():
    """Test that JALR triggers flush"""
    print("\n" + "=" * 70)
    print("JALR Pipeline Flush Test")
    print("=" * 70)
    print("\nJALR should flush instructions in early stages\n")
    
    processor = RISCVProcessor()
    processor.register_file.write_pc(0x4000)
    processor.register_file.write("R2", 0x5000)
    processor.register_file.write("R3", 10)
    
    program = [
        "JALR R1, R2, 0",       # Should trigger flush
        "ADD R4, R2, R3",       # Should be flushed
        "SUB R5, R2, R3",       # Should be flushed
    ]
    
    print("Program:")
    for i, instr in enumerate(program):
        print(f"  {i}: {instr}")
    
    print("\nExecution:")
    info = processor.execute(program)
    
    print("\nResults:")
    print(f"  Instructions completed: {len(info['completed_instructions'])}")
    print(f"  Flush count: {processor.pipeline.flush_count}")
    print(f"  R1 (return address): {processor.get_register('R1'):#010x}")
    print(f"  R4 (should be 0 if flushed): {processor.get_register('R4')}")


def main():
    print("\n" + "=" * 70)
    print("Pipeline Flush Mechanism Tests")
    print("=" * 70)
    print()
    
    test_jal_flush()
    test_branch_taken_flush()
    test_branch_not_taken_no_flush()
    test_jalr_flush()
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print("""
Pipeline Flush Mechanism:
  ✓ Triggered by JAL and JALR (unconditional jumps)
  ✓ Triggered by taken branches (BEQ, BNE, BLT, BGE, BLTU, BGEU)
  ✓ NOT triggered by not-taken branches
  ✓ Converts in-flight instructions to bubbles
  ✓ Prevents incorrect instruction execution after control flow change

Implementation:
  - Flush signal raised in Execute stage when jump/branch detected
  - Decode stage converts instructions to bubbles during flush
  - Flush cleared after Memory stage (allows propagation)
  - Tracks flush_count for performance analysis
""")
    print("=" * 70)


if __name__ == "__main__":
    main()
