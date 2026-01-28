"""ELF loader and RISC-V instruction decoder for running binary tests"""
import struct
from elftools.elf.elffile import ELFFile


class RISCVDecoder:
    """Decode 32-bit RISC-V instructions into our simulator format"""
    
    # RISC-V register names (ABI names)
    REG_ABI_NAMES = [
        'zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2',  # x0-x7
        's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5',    # x8-x15
        'a6', 'a7', 's2', 's3', 's4', 's5', 's6', 's7',    # x16-x23
        's8', 's9', 's10', 's11', 't3', 't4', 't5', 't6'   # x24-x31
    ]
    
    @staticmethod
    def get_reg_name(reg_num):
        """Convert register number to name (map to our R0-R31 format)"""
        if 0 <= reg_num < 32:
            return f"R{reg_num}"
        return f"R{reg_num}"
    
    @staticmethod
    def decode_r_type(instr):
        """Decode R-type instruction"""
        opcode = instr & 0x7F
        rd = (instr >> 7) & 0x1F
        funct3 = (instr >> 12) & 0x7
        rs1 = (instr >> 15) & 0x1F
        rs2 = (instr >> 20) & 0x1F
        funct7 = (instr >> 25) & 0x7F
        
        # Map to instruction
        if opcode == 0x33:  # OP
            if funct3 == 0x0:
                if funct7 == 0x00:
                    return f"ADD {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {RISCVDecoder.get_reg_name(rs2)}"
                elif funct7 == 0x20:
                    return f"SUB {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {RISCVDecoder.get_reg_name(rs2)}"
            elif funct3 == 0x7:  # AND
                return f"AND {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {RISCVDecoder.get_reg_name(rs2)}"
            elif funct3 == 0x6:  # OR
                return f"OR {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {RISCVDecoder.get_reg_name(rs2)}"
            elif funct3 == 0x4:  # XOR
                return f"XOR {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {RISCVDecoder.get_reg_name(rs2)}"
            elif funct3 == 0x1:  # SLL
                return f"SLL {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {RISCVDecoder.get_reg_name(rs2)}"
            elif funct3 == 0x5:
                if funct7 == 0x00:  # SRL
                    return f"SRL {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {RISCVDecoder.get_reg_name(rs2)}"
                elif funct7 == 0x20:  # SRA
                    return f"SRA {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {RISCVDecoder.get_reg_name(rs2)}"
            elif funct3 == 0x2:  # SLT
                return f"SLT {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {RISCVDecoder.get_reg_name(rs2)}"
            elif funct3 == 0x3:  # SLTU
                return f"SLTU {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {RISCVDecoder.get_reg_name(rs2)}"
        
        return None
    
    @staticmethod
    def decode_i_type(instr):
        """Decode I-type instruction"""
        opcode = instr & 0x7F
        rd = (instr >> 7) & 0x1F
        funct3 = (instr >> 12) & 0x7
        rs1 = (instr >> 15) & 0x1F
        imm = (instr >> 20) & 0xFFF
        
        # Sign extend immediate
        if imm & 0x800:
            imm = imm | 0xFFFFF000
        imm = struct.unpack('i', struct.pack('I', imm))[0]
        
        if opcode == 0x13:  # OP-IMM
            if funct3 == 0x0:  # ADDI
                return f"ADDI {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {imm}"
            elif funct3 == 0x7:  # ANDI
                return f"ANDI {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {imm}"
            elif funct3 == 0x6:  # ORI
                return f"ORI {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {imm}"
            elif funct3 == 0x4:  # XORI
                return f"XORI {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {imm}"
            elif funct3 == 0x1:  # SLLI
                shamt = imm & 0x1F
                return f"SLLI {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {shamt}"
            elif funct3 == 0x5:
                shamt = imm & 0x1F
                if (imm >> 10) & 0x1:  # SRAI
                    return f"SRAI {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {shamt}"
                else:  # SRLI
                    return f"SRLI {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {shamt}"
            elif funct3 == 0x2:  # SLTI
                return f"SLTI {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {imm}"
            elif funct3 == 0x3:  # SLTIU
                return f"SLTIU {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {imm}"
        elif opcode == 0x03:  # LOAD
            if funct3 == 0x2:  # LW
                return f"LOAD {RISCVDecoder.get_reg_name(rd)}, {imm}({RISCVDecoder.get_reg_name(rs1)})"
        elif opcode == 0x67:  # JALR
            return f"JALR {RISCVDecoder.get_reg_name(rd)}, {RISCVDecoder.get_reg_name(rs1)}, {imm}"
        
        return None
    
    @staticmethod
    def decode_s_type(instr):
        """Decode S-type instruction (stores)"""
        opcode = instr & 0x7F
        funct3 = (instr >> 12) & 0x7
        rs1 = (instr >> 15) & 0x1F
        rs2 = (instr >> 20) & 0x1F
        imm_low = (instr >> 7) & 0x1F
        imm_high = (instr >> 25) & 0x7F
        imm = (imm_high << 5) | imm_low
        
        # Sign extend
        if imm & 0x800:
            imm = imm | 0xFFFFF000
        imm = struct.unpack('i', struct.pack('I', imm))[0]
        
        if opcode == 0x23:  # STORE
            if funct3 == 0x2:  # SW
                return f"STORE {RISCVDecoder.get_reg_name(rs2)}, {imm}({RISCVDecoder.get_reg_name(rs1)})"
        
        return None
    
    @staticmethod
    def decode_b_type(instr):
        """Decode B-type instruction (branches)"""
        opcode = instr & 0x7F
        funct3 = (instr >> 12) & 0x7
        rs1 = (instr >> 15) & 0x1F
        rs2 = (instr >> 20) & 0x1F
        
        imm11 = (instr >> 7) & 0x1
        imm1_4 = (instr >> 8) & 0xF
        imm5_10 = (instr >> 25) & 0x3F
        imm12 = (instr >> 31) & 0x1
        
        imm = (imm12 << 12) | (imm11 << 11) | (imm5_10 << 5) | (imm1_4 << 1)
        
        # Sign extend
        if imm & 0x1000:
            imm = imm | 0xFFFFE000
        imm = struct.unpack('i', struct.pack('I', imm))[0]
        
        if opcode == 0x63:  # BRANCH
            branch_ops = {
                0x0: 'BEQ', 0x1: 'BNE', 0x4: 'BLT',
                0x5: 'BGE', 0x6: 'BLTU', 0x7: 'BGEU'
            }
            if funct3 in branch_ops:
                op = branch_ops[funct3]
                return f"{op} {RISCVDecoder.get_reg_name(rs1)}, {RISCVDecoder.get_reg_name(rs2)}, {imm}"
        
        return None
    
    @staticmethod
    def decode_u_type(instr):
        """Decode U-type instruction (LUI, AUIPC)"""
        opcode = instr & 0x7F
        rd = (instr >> 7) & 0x1F
        imm = instr & 0xFFFFF000
        
        if opcode == 0x37:  # LUI
            return f"LUI {RISCVDecoder.get_reg_name(rd)}, {imm >> 12}"
        elif opcode == 0x17:  # AUIPC
            return f"AUIPC {RISCVDecoder.get_reg_name(rd)}, {imm >> 12}"
        
        return None
    
    @staticmethod
    def decode_j_type(instr):
        """Decode J-type instruction (JAL)"""
        opcode = instr & 0x7F
        rd = (instr >> 7) & 0x1F
        
        imm19_12 = (instr >> 12) & 0xFF
        imm11 = (instr >> 20) & 0x1
        imm1_10 = (instr >> 21) & 0x3FF
        imm20 = (instr >> 31) & 0x1
        
        imm = (imm20 << 20) | (imm19_12 << 12) | (imm11 << 11) | (imm1_10 << 1)
        
        # Sign extend
        if imm & 0x100000:
            imm = imm | 0xFFE00000
        imm = struct.unpack('i', struct.pack('I', imm))[0]
        
        if opcode == 0x6F:  # JAL
            return f"JAL {RISCVDecoder.get_reg_name(rd)}, {imm}"
        
        return None
    
    @staticmethod
    def decode(instr_word):
        """Decode a 32-bit instruction word"""
        if instr_word == 0:
            return "NOP"
        
        opcode = instr_word & 0x7F
        
        # Try each instruction type
        if opcode in [0x33]:  # R-type
            result = RISCVDecoder.decode_r_type(instr_word)
        elif opcode in [0x13, 0x03, 0x67]:  # I-type
            result = RISCVDecoder.decode_i_type(instr_word)
        elif opcode in [0x23]:  # S-type
            result = RISCVDecoder.decode_s_type(instr_word)
        elif opcode in [0x63]:  # B-type
            result = RISCVDecoder.decode_b_type(instr_word)
        elif opcode in [0x37, 0x17]:  # U-type
            result = RISCVDecoder.decode_u_type(instr_word)
        elif opcode in [0x6F]:  # J-type
            result = RISCVDecoder.decode_j_type(instr_word)
        else:
            result = None
        
        if result:
            return result
        return f"UNKNOWN(0x{instr_word:08x})"


class ELFTestLoader:
    """Load riscv-test ELF binaries and extract instructions"""
    
    TOHOST_ADDR = 0x80001000
    ENTRY_POINT = 0x80000000
    
    def __init__(self, elf_path):
        self.elf_path = elf_path
        self.memory = {}
        self.entry_point = None
        
    def load(self):
        """Load ELF file into memory"""
        with open(self.elf_path, 'rb') as f:
            elf = ELFFile(f)
            self.entry_point = elf.header['e_entry']
            
            # Load program segments
            for segment in elf.iter_segments():
                if segment['p_type'] == 'PT_LOAD':
                    addr = segment['p_vaddr']
                    data = segment.data()
                    for i, byte in enumerate(data):
                        self.memory[addr + i] = byte
        
        return self.memory, self.entry_point
    
    def read_word(self, addr):
        """Read 32-bit word from memory (little-endian)"""
        bytes_data = [self.memory.get(addr + i, 0) for i in range(4)]
        return struct.unpack('<I', bytes(bytes_data))[0]
    
    def extract_instructions(self, start_addr=None, max_instructions=1000):
        """
        Extract and decode instructions from loaded ELF
        
        Returns list of (address, instruction_string) tuples
        """
        if start_addr is None:
            start_addr = self.entry_point
        
        instructions = []
        addr = start_addr
        
        for _ in range(max_instructions):
            if addr not in self.memory:
                break
            
            instr_word = self.read_word(addr)
            decoded = RISCVDecoder.decode(instr_word)
            instructions.append((addr, decoded))
            
            addr += 4  # Next instruction
            
            # Stop at ECALL or infinite loop
            if (instr_word & 0x7F) == 0x73:  # SYSTEM instruction
                break
        
        return instructions


if __name__ == "__main__":
    import sys
    
    # Test the decoder with some example instructions
    print("=== RISC-V Instruction Decoder Test ===\n")
    
    test_instructions = [
        (0x003100B3, "ADD x1, x2, x3"),
        (0x403100B3, "SUB x1, x2, x3"),
        (0x00312093, "ADDI x1, x2, 3"),
        (0x00212103, "LW x2, 2(x2)"),
        (0x00212223, "SW x2, 2(x2)"),
    ]
    
    for instr_word, expected in test_instructions:
        decoded = RISCVDecoder.decode(instr_word)
        print(f"0x{instr_word:08x}: {decoded}")
    
    # Try loading an actual test if available
    test_file = "3rd_party/riscv-tests/isa/rv32ui-p-add"
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    
    import os
    if os.path.exists(test_file):
        print(f"\n=== Loading {test_file} ===\n")
        loader = ELFTestLoader(test_file)
        memory, entry = loader.load()
        print(f"Entry point: 0x{entry:08x}")
        print(f"Loaded {len(memory)} bytes\n")
        
        # Extract first 20 instructions
        instructions = loader.extract_instructions(max_instructions=20)
        print("First 20 instructions:")
        for addr, instr in instructions:
            print(f"  0x{addr:08x}: {instr}")
    else:
        print(f"\nTest file not found: {test_file}")
        print("Run: python elf_loader.py 3rd_party/riscv-tests/isa/rv32ui-p-add")
