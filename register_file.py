"""Register file for RISC-V pipeline simulator"""


class RegisterFile:
    """Register file with read/write operations"""
    def __init__(self):
        self.registers = {}
        # Initialize 32 registers with default values
        for i in range(32):
            self.registers[f'R{i}'] = 0
    
    def read(self, reg_name):
        """Read value from register"""
        return self.registers.get(reg_name, 0)
    
    def write(self, reg_name, value):
        """Write value to register"""
        if reg_name and reg_name != 'R0':  # R0 is always 0 in RISC-V
            self.registers[reg_name] = value
    
    def print_registers(self, show_all=False):
        """Print register values in a readable format"""
        print("\n=== Register File ===")
        if show_all:
            # Show all registers
            for i in range(32):
                reg_name = f'R{i}'
                value = self.registers[reg_name]
                print(f"{reg_name:4s}: {value:10d} (0x{value:08x})")
        else:
            # Only show non-zero registers
            non_zero = {k: v for k, v in self.registers.items() if v != 0}
            if non_zero:
                for reg_name, value in sorted(non_zero.items(), key=lambda x: int(x[0][1:])):
                    print(f"{reg_name:4s}: {value:10d} (0x{value:08x})")
            else:
                print("All registers are zero")
        print("=" * 40)
    
    def __str__(self):
        # Only show non-zero registers
        non_zero = {k: v for k, v in self.registers.items() if v != 0}
        return str(non_zero)
