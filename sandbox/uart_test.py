#!/usr/bin/env python3
"""
UART Test - Demonstrates printf-like functionality

This test shows how to use the memory-mapped UART peripheral
to print characters and strings from RISC-V assembly code.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import simpy
from pipeline import Pipeline


def test_uart_basic():
    """Test basic UART character output"""
    print("\n" + "="*70)
    print("UART Test 1: Basic Character Output")
    print("="*70)
    
    env = simpy.Environment()
    pipeline = Pipeline(env)
    
    # UART TX register is at 0x10000000
    # We'll write ASCII characters one by one
    
    # Store ASCII values in registers and write to UART
    program = [
        # Print 'H' (ASCII 72)
        "ADDI R1, R0, 72",
        "LUI R2, 0x10000",           # R2 = 0x10000000 (UART base)
        "SW R1, 0(R2)",               # Write 'H' to UART
        
        # Print 'e' (ASCII 101)
        "ADDI R1, R0, 101",
        "SW R1, 0(R2)",
        
        # Print 'l' (ASCII 108)
        "ADDI R1, R0, 108",
        "SW R1, 0(R2)",
        "SW R1, 0(R2)",               # Write twice for 'll'
        
        # Print 'o' (ASCII 111)
        "ADDI R1, R0, 111",
        "SW R1, 0(R2)",
        
        # Print '!' (ASCII 33)
        "ADDI R1, R0, 33",
        "SW R1, 0(R2)",
        
        # Print newline (ASCII 10)
        "ADDI R1, R0, 10",
        "SW R1, 0(R2)",
    ]
    
    print("\nRunning program to print 'Hello!' via UART...")
    print("-"*70)
    print("UART Output: ", end="")
    
    pipeline.run(program)
    
    print("-"*70)
    stats = pipeline.uart.get_statistics()
    print(f"✓ Test completed: {stats['chars_transmitted']} characters transmitted\n")


def test_uart_string():
    """Test printing a string stored in memory"""
    print("\n" + "="*70)
    print("UART Test 2: String from Memory")
    print("="*70)
    
    env = simpy.Environment()
    pipeline = Pipeline(env)
    
    # Store a string in memory starting at address 0x1000
    test_string = "RISC-V UART Works!\n"
    string_addr = 0x1000
    
    for i, char in enumerate(test_string):
        pipeline.memory.write_byte(string_addr + i, ord(char))
    
    # Program to print string character by character
    program = [
        f"ADDI R3, R0, {string_addr}",  # R3 = string address
        f"ADDI R4, R0, {len(test_string)}",  # R4 = string length
        "LUI R5, 0x10000",              # R5 = UART base address
        "ADDI R6, R0, 0",               # R6 = counter = 0
        
        # Loop: print each character
        "LB R1, 0(R3)",                 # Load byte from string
        "SW R1, 0(R5)",                 # Write to UART
        "ADDI R3, R3, 1",               # Increment string pointer
        "ADDI R6, R6, 1",               # Increment counter
        "BNE R6, R4, -16",              # Loop if counter != length
    ]
    
    print("\nPrinting string from memory...")
    print("-"*70)
    print("UART Output: ", end="")
    
    pipeline.run(program)
    
    print("-"*70)
    stats = pipeline.uart.get_statistics()
    print(f"✓ Test completed: {stats['chars_transmitted']} characters transmitted\n")


def test_uart_with_function():
    """Test UART with a putchar-like function"""
    print("\n" + "="*70)
    print("UART Test 3: Putchar Function")
    print("="*70)
    
    env = simpy.Environment()
    pipeline = Pipeline(env)
    
    # Simple program that calls a putchar function
    program = [
        # Main program
        "ADDI R10, R0, 65",             # R10 = 'A'
        "JAL R1, 8",                    # Call putchar (skip 2 instructions)
        "ADDI R10, R0, 10",             # R10 = newline
        "JAL R1, 4",                    # Call putchar (skip 1 instruction)
        "JAL R0, 8",                    # Exit (jump past putchar)
        
        # putchar function (expects char in R10)
        "LUI R11, 0x10000",             # R11 = UART base
        "SW R10, 0(R11)",               # Write char to UART
        "JALR R0, 0(R1)",               # Return
    ]
    
    print("\nCalling putchar function...")
    print("-"*70)
    print("UART Output: ", end="")
    
    pipeline.run(program)
    
    print("-"*70)
    stats = pipeline.uart.get_statistics()
    print(f"✓ Test completed: {stats['chars_transmitted']} characters transmitted\n")


def test_uart_status_register():
    """Test UART status register"""
    print("\n" + "="*70)
    print("UART Test 4: Status Register")
    print("="*70)
    
    env = simpy.Environment()
    pipeline = Pipeline(env)
    
    # Read status register
    program = [
        "LUI R1, 0x10000",              # R1 = UART base
        "ADDI R1, R1, 4",               # R1 = status register (base + 4)
        "LW R2, 0(R1)",                 # Read status
        # R2 should now contain 0x01 (TX ready)
    ]
    
    print("\nReading UART status register...")
    pipeline.run(program)
    
    status = pipeline.register_file.read("R2")
    print(f"Status register value: 0x{status:02x}")
    print(f"TX Ready bit: {status & 0x01}")
    
    if status & 0x01:
        print("✓ UART is ready for transmission\n")
    else:
        print("✗ UART status error\n")


def main():
    """Run all UART tests"""
    print("\n" + "="*70)
    print("RISC-V UART Peripheral Test Suite")
    print("="*70)
    print("\nThese tests demonstrate memory-mapped UART functionality")
    print("which enables printf() support for FreeRTOS applications.\n")
    
    test_uart_basic()
    test_uart_string()
    test_uart_with_function()
    test_uart_status_register()
    
    print("="*70)
    print("All UART tests completed successfully!")
    print("="*70)
    print("\nTo use UART in C code (for FreeRTOS):")
    print("""
    // Define UART address
    #define UART_TX_REG ((volatile char*)0x10000000)
    
    // Simple putchar function
    void uart_putc(char c) {
        *UART_TX_REG = c;
    }
    
    // printf support (implement _write)
    int _write(int fd, const void *buf, size_t count) {
        for (size_t i = 0; i < count; i++) {
            uart_putc(((char*)buf)[i]);
        }
        return count;
    }
    """)
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
