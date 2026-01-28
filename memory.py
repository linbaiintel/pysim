"""Memory module for RISC-V pipeline simulator"""


class Memory:
    """Data memory for LOAD/STORE operations"""
    def __init__(self):
        self.data = {}
    
    def read(self, address):
        """Read value from memory address"""
        return self.data.get(address, 0)
    
    def write(self, address, value):
        """Write value to memory address"""
        self.data[address] = value
    
    def __str__(self):
        return str(self.data)
