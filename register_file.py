"""Register file for RISC-V pipeline simulator"""


class RegisterFile:
    """Register file with read/write operations and special registers"""
    def __init__(self):
        self.registers = {}
        # Initialize 32 general-purpose registers with default values
        for i in range(32):
            self.registers[f'R{i}'] = 0
        
        # Special registers (not part of the 32 GPRs)
        self.pc = 0           # Program Counter
        self.next_pc = 4      # Next PC (for branches/jumps)
    
    def read(self, reg_name):
        """Read value from register"""
        return self.registers.get(reg_name, 0)
    
    def write(self, reg_name, value):
        """Write value to register (masked to 32-bit)"""
        if reg_name and reg_name != 'R0':  # R0 is always 0 in RISC-V
            self.registers[reg_name] = value & 0xFFFFFFFF
    
    def read_pc(self):
        """Read program counter"""
        return self.pc
    
    def write_pc(self, value):
        """Write program counter"""
        self.pc = value & 0xFFFFFFFF  # Keep 32-bit
    
    def increment_pc(self, amount=4):
        """Increment PC by specified amount (default 4 bytes)"""
        self.pc = (self.pc + amount) & 0xFFFFFFFF
    
    def update_pc(self):
        """Update PC to next_pc (for sequential execution after branch resolution)"""
        self.pc = self.next_pc
        self.next_pc = (self.pc + 4) & 0xFFFFFFFF
    
    def set_next_pc(self, value):
        """Set next PC value (for branches/jumps)"""
        self.next_pc = value & 0xFFFFFFFF
    
    def reset_pc(self, address=0):
        """Reset PC to specified address (default 0)"""
        self.pc = address & 0xFFFFFFFF
        self.next_pc = (address + 4) & 0xFFFFFFFF
    
    def print_registers(self, show_all=False, show_pc=True):
        """Print register values in a readable format"""
        print("\n=== Register File ===")
        
        # Show PC if requested
        if show_pc:
            print(f"PC  : {self.pc:10d} (0x{self.pc:08x})")
            print("-" * 40)
        
        if show_all:
            # Show all registers
            for i in range(32):
                reg_name = f'R{i}'
                value = self.registers[reg_name]
                # Add common RISC-V register aliases
                alias = self._get_register_alias(i)
                alias_str = f" ({alias})" if alias else ""
                print(f"{reg_name:4s}{alias_str:8s}: {value:10d} (0x{value:08x})")
        else:
            # Only show non-zero registers
            non_zero = {k: v for k, v in self.registers.items() if v != 0}
            if non_zero:
                for reg_name, value in sorted(non_zero.items(), key=lambda x: int(x[0][1:])):
                    reg_num = int(reg_name[1:])
                    alias = self._get_register_alias(reg_num)
                    alias_str = f" ({alias})" if alias else ""
                    print(f"{reg_name:4s}{alias_str:8s}: {value:10d} (0x{value:08x})")
            else:
                print("All registers are zero")
        print("=" * 40)
    
    def _get_register_alias(self, reg_num):
        """Get RISC-V ABI register alias"""
        aliases = {
            0: "zero",  # Hard-wired zero
            1: "ra",    # Return address
            2: "sp",    # Stack pointer
            3: "gp",    # Global pointer
            4: "tp",    # Thread pointer
            5: "t0",    # Temporary 0
            6: "t1",    # Temporary 1
            7: "t2",    # Temporary 2
            8: "s0/fp", # Saved register 0 / Frame pointer
            9: "s1",    # Saved register 1
            10: "a0",   # Function argument 0 / return value 0
            11: "a1",   # Function argument 1 / return value 1
            12: "a2",   # Function argument 2
            13: "a3",   # Function argument 3
            14: "a4",   # Function argument 4
            15: "a5",   # Function argument 5
            16: "a6",   # Function argument 6
            17: "a7",   # Function argument 7
            18: "s2",   # Saved register 2
            19: "s3",   # Saved register 3
            20: "s4",   # Saved register 4
            21: "s5",   # Saved register 5
            22: "s6",   # Saved register 6
            23: "s7",   # Saved register 7
            24: "s8",   # Saved register 8
            25: "s9",   # Saved register 9
            26: "s10",  # Saved register 10
            27: "s11",  # Saved register 11
            28: "t3",   # Temporary 3
            29: "t4",   # Temporary 4
            30: "t5",   # Temporary 5
            31: "t6",   # Temporary 6
        }
        return aliases.get(reg_num, "")
    
    def __str__(self):
        # Only show non-zero registers
        non_zero = {k: v for k, v in self.registers.items() if v != 0}
        return str(non_zero)
