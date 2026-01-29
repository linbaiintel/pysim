"""Memory module for RISC-V pipeline simulator"""


class Memory:
    """Byte-addressable data memory for LOAD/STORE operations
    
    Supports:
    - Configurable memory size (default 1MB)
    - Byte, halfword (2 bytes), and word (4 bytes) access
    - Little-endian byte ordering
    - Sign extension for signed loads (LB, LH)
    """
    def __init__(self, size=1*1024*1024, base_address=0, uart=None, clint=None):
        """Initialize memory
        
        Args:
            size: Memory size in bytes (default 1MB)
            base_address: Base address offset (default 0)
            uart: Optional UART peripheral for memory-mapped I/O
            clint: Optional CLINT peripheral for memory-mapped timer
        """
        self.size = size
        self.base_address = base_address
        self.data = bytearray(size)
        self.uart = uart
        self.clint = clint
    
    def _check_address(self, address, access_size=1):
        """Validate memory address and alignment
        
        Args:
            address: Memory address to check
            access_size: Size of access in bytes (1, 2, or 4)
            
        Raises:
            ValueError: If address is out of bounds or misaligned
        """
        offset = address - self.base_address
        if offset < 0 or offset + access_size > self.size:
            raise ValueError(f"Memory access out of bounds: 0x{address:08x} "
                           f"(valid range: 0x{self.base_address:08x}-0x{self.base_address + self.size - 1:08x})")
        
        # Check alignment for halfword and word access
        if access_size == 2 and offset % 2 != 0:
            raise ValueError(f"Misaligned halfword access at 0x{address:08x}")
        elif access_size == 4 and offset % 4 != 0:
            raise ValueError(f"Misaligned word access at 0x{address:08x}")
    
    # Byte access (8-bit)
    def read_byte(self, address, signed=False):
        """Read byte from memory
        
        Args:
            address: Memory address
            signed: If True, sign-extend to 32 bits
            
        Returns:
            Byte value (sign-extended to 32 bits if signed=True)
        """
        self._check_address(address, 1)
        offset = address - self.base_address
        value = self.data[offset]
        
        if signed and (value & 0x80):  # Sign bit set
            return value | 0xFFFFFF00  # Sign extend to 32 bits
        return value
    
    def write_byte(self, address, value):
        """Write byte to memory
        
        Args:
            address: Memory address
            value: Byte value to write (only lower 8 bits used)
        """
        self._check_address(address, 1)
        offset = address - self.base_address
        self.data[offset] = value & 0xFF
    
    # Halfword access (16-bit, little-endian)
    def read_halfword(self, address, signed=False):
        """Read halfword (2 bytes) from memory
        
        Args:
            address: Memory address (must be 2-byte aligned)
            signed: If True, sign-extend to 32 bits
            
        Returns:
            Halfword value (sign-extended to 32 bits if signed=True)
        """
        self._check_address(address, 2)
        offset = address - self.base_address
        
        # Little-endian: LSB first
        value = self.data[offset] | (self.data[offset + 1] << 8)
        
        if signed and (value & 0x8000):  # Sign bit set
            return value | 0xFFFF0000  # Sign extend to 32 bits
        return value
    
    def write_halfword(self, address, value):
        """Write halfword (2 bytes) to memory
        
        Args:
            address: Memory address (must be 2-byte aligned)
            value: Halfword value to write (only lower 16 bits used)
        """
        self._check_address(address, 2)
        offset = address - self.base_address
        
        # Little-endian: LSB first
        self.data[offset] = value & 0xFF
        self.data[offset + 1] = (value >> 8) & 0xFF
    
    # Word access (32-bit, little-endian)
    def read_word(self, address):
        """Read word (4 bytes) from memory
        
        Args:
            address: Memory address (must be 4-byte aligned)
            
        Returns:
            Word value (32 bits)
        """
        # Check for UART memory-mapped I/O
        if self.uart and self.uart.is_uart_address(address):
            value = self.uart.read_register(address)
            return value if value is not None else 0
        
        # Check for CLINT memory-mapped I/O
        if self.clint and self.clint.MSIP_BASE <= address < self.clint.MTIME_BASE + 8:
            value = self.clint.read_register(address)
            return value if value is not None else 0
        
        self._check_address(address, 4)
        offset = address - self.base_address
        
        # Little-endian: LSB first
        value = (self.data[offset] |
                (self.data[offset + 1] << 8) |
                (self.data[offset + 2] << 16) |
                (self.data[offset + 3] << 24))
        return value & 0xFFFFFFFF
    
    def write_word(self, address, value):
        """Write word (4 bytes) to memory
        
        Args:
            address: Memory address (must be 4-byte aligned)
            value: Word value to write (only lower 32 bits used)
        """
        # Check for UART memory-mapped I/O
        if self.uart and self.uart.is_uart_address(address):
            self.uart.write_register(address, value)
            return
        
        # Check for CLINT memory-mapped I/O
        if self.clint and self.clint.MSIP_BASE <= address < self.clint.MTIME_BASE + 8:
            self.clint.write_register(address, value)
            return
        
        self._check_address(address, 4)
        offset = address - self.base_address
        
        # Little-endian: LSB first
        self.data[offset] = value & 0xFF
        self.data[offset + 1] = (value >> 8) & 0xFF
        self.data[offset + 2] = (value >> 16) & 0xFF
        self.data[offset + 3] = (value >> 24) & 0xFF
    
    # Legacy methods for backward compatibility
    def read(self, address):
        """Legacy method: Read word from memory (backward compatible)"""
        try:
            return self.read_word(address)
        except ValueError:
            return 0
    
    def write(self, address, value):
        """Legacy method: Write word to memory (backward compatible)"""
        try:
            self.write_word(address, value)
        except ValueError:
            pass
    
    def load_program(self, program_data, start_address=0):
        """Load program data into memory
        
        Args:
            program_data: List of bytes or bytearray
            start_address: Starting address to load program
        """
        offset = start_address - self.base_address
        if offset < 0 or offset + len(program_data) > self.size:
            raise ValueError(f"Program too large or invalid start address")
        
        self.data[offset:offset + len(program_data)] = program_data
    
    def dump(self, start_address, length, bytes_per_line=16):
        """Dump memory contents in hexadecimal format
        
        Args:
            start_address: Starting address to dump
            length: Number of bytes to dump
            bytes_per_line: Number of bytes per line (default 16)
        """
        print(f"\n=== Memory Dump (0x{start_address:08x} - 0x{start_address + length - 1:08x}) ===")
        
        for i in range(0, length, bytes_per_line):
            addr = start_address + i
            offset = addr - self.base_address
            
            if offset < 0 or offset >= self.size:
                continue
            
            # Print address
            print(f"0x{addr:08x}:", end=" ")
            
            # Print hex bytes
            for j in range(bytes_per_line):
                if offset + j < self.size:
                    print(f"{self.data[offset + j]:02x}", end=" ")
                else:
                    print("  ", end=" ")
            
            print(" |", end=" ")
            
            # Print ASCII representation
            for j in range(bytes_per_line):
                if offset + j < self.size:
                    byte = self.data[offset + j]
                    if 32 <= byte < 127:
                        print(chr(byte), end="")
                    else:
                        print(".", end="")
            
            print()
        print("=" * 70)
    
    def clear(self):
        """Clear all memory (set to zero)"""
        self.data = bytearray(self.size)
    
    def get_stats(self):
        """Get memory statistics"""
        non_zero = sum(1 for b in self.data if b != 0)
        return {
            'size': self.size,
            'base_address': self.base_address,
            'bytes_used': non_zero,
            'bytes_free': self.size - non_zero,
            'utilization': (non_zero / self.size) * 100
        }
    
    def __str__(self):
        stats = self.get_stats()
        return (f"Memory(size={stats['size']} bytes, "
                f"base=0x{stats['base_address']:08x}, "
                f"used={stats['bytes_used']} bytes, "
                f"{stats['utilization']:.2f}% utilized)")

