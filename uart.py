"""Simple UART Peripheral for RISC-V Simulator

Provides a memory-mapped UART for character output, enabling printf() support
in FreeRTOS and bare-metal applications.

Memory Map:
- 0x10000000: UART TX data register (write a byte to transmit)
- 0x10000004: UART status register (read-only, bit 0 = TX ready)

Usage in C:
    volatile char *uart_tx = (char*)0x10000000;
    *uart_tx = 'H';  // Prints 'H' to terminal
    
    // For printf support, implement _write():
    int _write(int fd, const void *buf, size_t count) {
        volatile char *uart = (char*)0x10000000;
        for (size_t i = 0; i < count; i++) {
            *uart = ((char*)buf)[i];
        }
        return count;
    }
"""

import sys


class UART:
    """Simple UART peripheral for character output
    
    Provides memory-mapped UART functionality for printing to terminal.
    Characters written to TX register appear immediately on stdout.
    """
    
    # Memory-mapped register addresses
    TX_DATA_REG = 0x10000000    # Write byte here to transmit
    STATUS_REG = 0x10000004     # Read-only status (always ready)
    
    # Status register bits
    STATUS_TX_READY = 0x01      # Transmitter ready (always set)
    
    def __init__(self, output_stream=None):
        """Initialize UART peripheral
        
        Args:
            output_stream: File-like object for output (default: sys.stdout)
        """
        self.output_stream = output_stream or sys.stdout
        self.tx_buffer = []
        self.char_count = 0
        
    def write_register(self, address, value):
        """Write to UART register
        
        Args:
            address: Register address
            value: Value to write (only lower 8 bits used for TX)
        
        Returns:
            True if write was handled, False otherwise
        """
        if address == self.TX_DATA_REG:
            # Transmit byte
            char = chr(value & 0xFF)
            self.output_stream.write(char)
            self.output_stream.flush()
            self.char_count += 1
            return True
        elif address == self.STATUS_REG:
            # Status register is read-only, ignore writes
            return True
        
        return False
    
    def read_register(self, address):
        """Read from UART register
        
        Args:
            address: Register address
            
        Returns:
            Register value, or None if address not handled
        """
        if address == self.STATUS_REG:
            # Always ready to transmit
            return self.STATUS_TX_READY
        elif address == self.TX_DATA_REG:
            # Reading TX register returns 0
            return 0
        
        return None
    
    def is_uart_address(self, address):
        """Check if address belongs to UART
        
        Args:
            address: Memory address to check
            
        Returns:
            True if address is a UART register
        """
        return address in [self.TX_DATA_REG, self.STATUS_REG]
    
    def get_statistics(self):
        """Get UART statistics
        
        Returns:
            Dictionary with UART stats
        """
        return {
            'chars_transmitted': self.char_count,
        }
    
    def reset(self):
        """Reset UART to initial state"""
        self.tx_buffer.clear()
        self.char_count = 0


# Helper function for test/demo purposes
def create_uart_test():
    """Create a simple UART test"""
    uart = UART()
    
    # Test character output
    test_string = "Hello from RISC-V UART!\n"
    print("Testing UART peripheral:")
    print("-" * 40)
    
    for char in test_string:
        uart.write_register(UART.TX_DATA_REG, ord(char))
    
    print("-" * 40)
    stats = uart.get_statistics()
    print(f"Transmitted {stats['chars_transmitted']} characters")


if __name__ == "__main__":
    create_uart_test()
