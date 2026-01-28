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
        self.immediate = None  # For immediate values in I-type instructions
        self.has_immediate = False
        
        # For storing computed values during execution
        self.src_values = []
        self.result = None
        self.mem_address = None
        self.jump_target = None  # For JAL/JALR jump target address
        self.is_jump = False  # Flag for jump instructions
        
        if not self.is_bubble:
            self.parse()
    
    def parse(self):
        """Parse instruction to extract destination and source registers"""
        # Handle different instruction formats:
        # R-type: OP dest, src1, src2 (e.g., ADD R1, R2, R3)
        # I-type: OP dest, src1, imm (e.g., ADDI R1, R2, 100)
        # Load: LOAD dest, offset(base) (e.g., LOAD R1, 100(R2))
        # Store: STORE src, offset(base) (e.g., STORE R1, 100(R2))
        # Upper Immediate: LUI/AUIPC dest, imm (e.g., LUI R1, 0x12345)
        # Branch: BEQ src1, src2, offset (e.g., BEQ R1, R2, 100)
        
        text_upper = self.text.upper()
        
        # Memory operations (Load/Store)
        if "LOAD" in text_upper or "LW" in text_upper or "LB" in text_upper or "LH" in text_upper or "LBU" in text_upper or "LHU" in text_upper:
            match = re.search(r'(\w+)\s+(\w+),\s*(-?\d+)\((\w+)\)', self.text, re.IGNORECASE)
            if match:
                self.operation = match.group(1).upper()
                self.dest_reg = match.group(2)
                self.offset = int(match.group(3))
                self.src_regs = [match.group(4)]  # base register
                
        elif "STORE" in text_upper or "SW" in text_upper or "SB" in text_upper or "SH" in text_upper:
            match = re.search(r'(\w+)\s+(\w+),\s*(-?\d+)\((\w+)\)', self.text, re.IGNORECASE)
            if match:
                self.operation = match.group(1).upper()
                self.dest_reg = None  # STORE doesn't write to register
                self.offset = int(match.group(3))
                self.src_regs = [match.group(2), match.group(4)]  # value and base register
                
        # Upper Immediate instructions (LUI, AUIPC)
        elif text_upper.startswith('LUI') or text_upper.startswith('AUIPC'):
            match = re.search(r'(\w+)\s+(\w+),\s*(-?(?:0x)?[0-9a-fA-F]+)', self.text, re.IGNORECASE)
            if match:
                self.operation = match.group(1).upper()
                self.dest_reg = match.group(2)
                self.immediate = self._parse_immediate(match.group(3))
                self.has_immediate = True
                self.src_regs = []
                
        # System instructions (ECALL, EBREAK)
        elif text_upper in ['ECALL', 'EBREAK']:
            self.operation = text_upper
            self.dest_reg = None  # System instructions don't write to register
            self.src_regs = []
        
        # Memory ordering instructions (FENCE, FENCE.I)
        elif text_upper in ['FENCE', 'FENCE.I']:
            self.operation = text_upper
            self.dest_reg = None  # FENCE instructions don't write to register
            self.src_regs = []
            
        # Branch instructions
        elif text_upper.startswith('B'):
            match = re.search(r'(\w+)\s+(\w+),\s*(\w+),\s*(-?\d+)', self.text, re.IGNORECASE)
            if match:
                self.operation = match.group(1).upper()
                self.dest_reg = None  # Branches don't write to register
                self.src_regs = [match.group(2), match.group(3)]
                self.offset = int(match.group(4))
                
        # Jump instructions
        elif text_upper.startswith('JAL'):
            self.is_jump = True
            if 'JALR' in text_upper:
                # JALR: dest, src, offset
                match = re.search(r'JALR\s+(\w+),\s*(\w+),\s*(-?\d+)', self.text, re.IGNORECASE)
                if match:
                    self.operation = 'JALR'
                    self.dest_reg = match.group(1)
                    self.src_regs = [match.group(2)]
                    self.offset = int(match.group(3))
            else:
                # JAL: dest, offset
                match = re.search(r'JAL\s+(\w+),\s*(-?\d+)', self.text, re.IGNORECASE)
                if match:
                    self.operation = 'JAL'
                    self.dest_reg = match.group(1)
                    self.offset = int(match.group(2))
                    self.src_regs = []
                    
        # I-type instructions (immediate operations) - CHECK BEFORE R-type!
        elif re.search(r'I\b', text_upper):  # Instructions ending with 'I' (ADDI, ANDI, etc.)
            # Match pattern: OPCODE dest, src, immediate
            match = re.search(r'(\w+)\s+(\w+),\s*(\w+),\s*(-?(?:0x)?[0-9a-fA-F]+)', self.text, re.IGNORECASE)
            if match:
                self.operation = match.group(1).upper()
                self.dest_reg = match.group(2)
                # Check if third operand is a register or already parsed
                third_operand = match.group(3)
                # If it starts with R and is followed by digit, it's a register
                if third_operand.upper().startswith('R') and len(third_operand) > 1:
                    self.src_regs = [third_operand]
                else:
                    # It's an immediate disguised as register name
                    self.src_regs = []
                self.immediate = self._parse_immediate(match.group(4))
                self.has_immediate = True
                
        # R-type instructions (register-register operations)
        else:
            match = re.search(r'(\w+)\s+(\w+),\s*(\w+),\s*(\w+)', self.text, re.IGNORECASE)
            if match:
                self.operation = match.group(1).upper()
                self.dest_reg = match.group(2)
                # Check if operands look like registers (start with R or are x0-x31)
                src1 = match.group(3)
                src2 = match.group(4)
                # If both operands start with R or x, they're registers
                if (src1.upper().startswith('R') or src1.startswith('x')) and \
                   (src2.upper().startswith('R') or src2.startswith('x')):
                    self.src_regs = [src1, src2]
                # If second operand is a number, it's actually an immediate (I-type)
                elif src2.isdigit() or (src2.startswith('-') and src2[1:].isdigit()) or src2.startswith('0x'):
                    self.operation = match.group(1).upper()
                    self.dest_reg = match.group(2)
                    self.src_regs = [src1]
                    self.immediate = self._parse_immediate(src2)
                    self.has_immediate = True
                else:
                    self.src_regs = [src1, src2]
    
    def _parse_immediate(self, imm_str):
        """Parse immediate value (supports decimal and hex)"""
        imm_str = imm_str.strip()
        if imm_str.startswith('0x') or imm_str.startswith('0X'):
            return int(imm_str, 16)
        else:
            return int(imm_str)
    
    def __str__(self):
        return self.text
    
    def __repr__(self):
        return f"Instruction({self.text})"
