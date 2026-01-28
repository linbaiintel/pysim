"""CSR (Control and Status Register) Bank for RISC-V simulator"""


class CSRBank:
    """Control and Status Register Bank
    
    Implements basic CSR functionality for educational purposes.
    Supports standard RISC-V CSR addresses.
    """
    
    # Standard CSR addresses (subset for educational purposes)
    CSR_ADDRESSES = {
        # Machine Information Registers
        0xF11: 'mvendorid',   # Vendor ID
        0xF12: 'marchid',     # Architecture ID
        0xF13: 'mimpid',      # Implementation ID
        0xF14: 'mhartid',     # Hardware thread ID
        
        # Machine Trap Setup
        0x300: 'mstatus',     # Machine status
        0x301: 'misa',        # ISA and extensions
        0x304: 'mie',         # Machine interrupt enable
        0x305: 'mtvec',       # Machine trap-handler base address
        
        # Machine Trap Handling
        0x340: 'mscratch',    # Machine scratch register
        0x341: 'mepc',        # Machine exception program counter
        0x342: 'mcause',      # Machine trap cause
        0x343: 'mtval',       # Machine bad address or instruction
        0x344: 'mip',         # Machine interrupt pending
        
        # Machine Counter/Timers
        0xB00: 'mcycle',      # Machine cycle counter
        0xB02: 'minstret',    # Machine instructions-retired counter
        0xC00: 'cycle',       # Cycle counter (user-mode)
        0xC01: 'time',        # Timer (user-mode)
        0xC02: 'instret',     # Instructions-retired counter (user-mode)
    }
    
    def __init__(self):
        """Initialize CSR bank with default values"""
        self.csrs = {}
        
        # Initialize with default values
        self.csrs[0xF11] = 0x0         # mvendorid (not implemented)
        self.csrs[0xF12] = 0x0         # marchid (not implemented)
        self.csrs[0xF13] = 0x0         # mimpid (not implemented)
        self.csrs[0xF14] = 0x0         # mhartid (hart 0)
        
        self.csrs[0x300] = 0x00000000  # mstatus
        self.csrs[0x301] = 0x40000100  # misa (RV32I)
        self.csrs[0x304] = 0x0         # mie
        self.csrs[0x305] = 0x0         # mtvec
        
        self.csrs[0x340] = 0x0         # mscratch
        self.csrs[0x341] = 0x0         # mepc
        self.csrs[0x342] = 0x0         # mcause
        self.csrs[0x343] = 0x0         # mtval
        self.csrs[0x344] = 0x0         # mip
        
        self.csrs[0xB00] = 0x0         # mcycle
        self.csrs[0xB02] = 0x0         # minstret
        self.csrs[0xC00] = 0x0         # cycle
        self.csrs[0xC01] = 0x0         # time
        self.csrs[0xC02] = 0x0         # instret
    
    def read(self, csr_addr):
        """Read from CSR
        
        Args:
            csr_addr: CSR address (12-bit immediate)
            
        Returns:
            32-bit value from CSR, or 0 if CSR doesn't exist
        """
        csr_addr = csr_addr & 0xFFF  # Mask to 12 bits
        return self.csrs.get(csr_addr, 0) & 0xFFFFFFFF
    
    def write(self, csr_addr, value):
        """Write to CSR
        
        Args:
            csr_addr: CSR address (12-bit immediate)
            value: 32-bit value to write
            
        Returns:
            Old value of the CSR
        """
        csr_addr = csr_addr & 0xFFF  # Mask to 12 bits
        value = value & 0xFFFFFFFF   # Mask to 32 bits
        
        old_value = self.csrs.get(csr_addr, 0)
        
        # Check for read-only CSRs (0xF00-0xFFF range)
        if 0xF00 <= csr_addr <= 0xFFF:
            # Read-only, don't write
            return old_value
        
        self.csrs[csr_addr] = value
        return old_value
    
    def set_bits(self, csr_addr, mask):
        """Set bits in CSR (CSRRS operation)
        
        Args:
            csr_addr: CSR address
            mask: Bits to set
            
        Returns:
            Old value of the CSR
        """
        csr_addr = csr_addr & 0xFFF
        old_value = self.read(csr_addr)
        new_value = old_value | mask
        self.write(csr_addr, new_value)
        return old_value
    
    def clear_bits(self, csr_addr, mask):
        """Clear bits in CSR (CSRRC operation)
        
        Args:
            csr_addr: CSR address
            mask: Bits to clear
            
        Returns:
            Old value of the CSR
        """
        csr_addr = csr_addr & 0xFFF
        old_value = self.read(csr_addr)
        new_value = old_value & ~mask
        self.write(csr_addr, new_value)
        return old_value
    
    def increment_cycle(self):
        """Increment cycle counters (called each cycle)"""
        self.csrs[0xB00] = (self.csrs.get(0xB00, 0) + 1) & 0xFFFFFFFF  # mcycle
        self.csrs[0xC00] = (self.csrs.get(0xC00, 0) + 1) & 0xFFFFFFFF  # cycle
    
    def increment_instret(self):
        """Increment instruction-retired counters (called when instruction retires)"""
        self.csrs[0xB02] = (self.csrs.get(0xB02, 0) + 1) & 0xFFFFFFFF  # minstret
        self.csrs[0xC02] = (self.csrs.get(0xC02, 0) + 1) & 0xFFFFFFFF  # instret
    
    def get_csr_name(self, csr_addr):
        """Get human-readable CSR name
        
        Args:
            csr_addr: CSR address
            
        Returns:
            String name of CSR, or 'unknown' if not recognized
        """
        csr_addr = csr_addr & 0xFFF
        return self.CSR_ADDRESSES.get(csr_addr, f'csr_0x{csr_addr:03x}')
