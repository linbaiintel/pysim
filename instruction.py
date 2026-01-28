"""Instruction class for RISC-V pipeline simulator"""
import re


class Instruction:
    """Represents a parsed instruction with register dependencies"""
    def __init__(self, text):
        self.text = text
        self.is_bubble = (text == "BUBBLE")
        self.dest_reg = None
        self.src_regs = []
        self.operation = None
        self.offset = 0
        
        # For storing computed values during execution
        self.src_values = []
        self.result = None
        self.mem_address = None
        
        if not self.is_bubble:
            self.parse()
    
    def parse(self):
        """Parse instruction to extract destination and source registers"""
        # Handle different instruction formats
        # Format: OP dest, src1, src2 (e.g., ADD R1, R2, R3)
        # Format: LOAD/STORE dest, offset(base) (e.g., LOAD R1, 100(R2))
        
        if "LOAD" in self.text:
            match = re.search(r'LOAD\s+(\w+),\s*(\d+)\((\w+)\)', self.text)
            if match:
                self.operation = 'LOAD'
                self.dest_reg = match.group(1)  # destination register
                self.offset = int(match.group(2))
                self.src_regs = [match.group(3)]  # base register
        elif "STORE" in self.text:
            match = re.search(r'STORE\s+(\w+),\s*(\d+)\((\w+)\)', self.text)
            if match:
                self.operation = 'STORE'
                self.dest_reg = None  # STORE doesn't write to register
                self.offset = int(match.group(2))
                self.src_regs = [match.group(1), match.group(3)]  # value and base register
        else:
            # Standard R-type: OP dest, src1, src2
            match = re.search(r'(\w+)\s+(\w+),\s*(\w+),\s*(\w+)', self.text)
            if match:
                self.operation = match.group(1)
                self.dest_reg = match.group(2)
                self.src_regs = [match.group(3), match.group(4)]
    
    def __str__(self):
        return self.text
    
    def __repr__(self):
        return f"Instruction({self.text})"
