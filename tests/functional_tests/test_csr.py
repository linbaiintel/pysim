"""
Test CSR (Control and Status Register) instructions.

Tests CSRRW, CSRRS, CSRRC, CSRRWI, CSRRSI, CSRRCI operations.
"""
import unittest
from instruction import Instruction
from exe import EXE
from csr import CSRBank


class TestCSRInstructions(unittest.TestCase):
    """Test suite for CSR instructions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.csr_bank = CSRBank()
    
    # CSRRW tests
    def test_csrrw_parsing(self):
        """Test CSRRW instruction parsing"""
        instr = Instruction("CSRRW R1, 0x300, R2")
        self.assertEqual(instr.operation, "CSRRW")
        self.assertEqual(instr.dest_reg, "R1")
        self.assertEqual(instr.csr_addr, 0x300)
        self.assertEqual(instr.src_regs, ["R2"])
        self.assertFalse(instr.has_immediate)
    
    def test_csrrw_execution(self):
        """Test CSRRW read/write operation"""
        self.csr_bank.write(0x300, 0x12345678)
        old_value = EXE.execute_csr_read_write(self.csr_bank, 0x300, 0xABCDEF00)
        self.assertEqual(old_value, 0x12345678)
        self.assertEqual(self.csr_bank.read(0x300), 0xABCDEF00)
    
    def test_csrrw_zero_write(self):
        """Test CSRRW with zero value"""
        self.csr_bank.write(0x340, 0xFFFFFFFF)
        old_value = EXE.execute_csr_read_write(self.csr_bank, 0x340, 0)
        self.assertEqual(old_value, 0xFFFFFFFF)
        self.assertEqual(self.csr_bank.read(0x340), 0)
    
    # CSRRS tests
    def test_csrrs_parsing(self):
        """Test CSRRS instruction parsing"""
        instr = Instruction("CSRRS R3, 0x304, R4")
        self.assertEqual(instr.operation, "CSRRS")
        self.assertEqual(instr.dest_reg, "R3")
        self.assertEqual(instr.csr_addr, 0x304)
        self.assertEqual(instr.src_regs, ["R4"])
    
    def test_csrrs_set_bits(self):
        """Test CSRRS set bits operation"""
        self.csr_bank.write(0x304, 0x0000FF00)
        old_value = EXE.execute_csr_read_set(self.csr_bank, 0x304, 0x00FF00FF)
        self.assertEqual(old_value, 0x0000FF00)
        self.assertEqual(self.csr_bank.read(0x304), 0x00FFFFFF)
    
    def test_csrrs_read_only(self):
        """Test CSRRS with zero mask (read-only)"""
        self.csr_bank.write(0x305, 0xDEADBEEF)
        old_value = EXE.execute_csr_read_set(self.csr_bank, 0x305, 0)
        self.assertEqual(old_value, 0xDEADBEEF)
        self.assertEqual(self.csr_bank.read(0x305), 0xDEADBEEF)  # Unchanged
    
    # CSRRC tests
    def test_csrrc_parsing(self):
        """Test CSRRC instruction parsing"""
        instr = Instruction("CSRRC R5, 0x340, R6")
        self.assertEqual(instr.operation, "CSRRC")
        self.assertEqual(instr.dest_reg, "R5")
        self.assertEqual(instr.csr_addr, 0x340)
        self.assertEqual(instr.src_regs, ["R6"])
    
    def test_csrrc_clear_bits(self):
        """Test CSRRC clear bits operation"""
        self.csr_bank.write(0x340, 0xFFFFFFFF)
        old_value = EXE.execute_csr_read_clear(self.csr_bank, 0x340, 0x0F0F0F0F)
        self.assertEqual(old_value, 0xFFFFFFFF)
        self.assertEqual(self.csr_bank.read(0x340), 0xF0F0F0F0)
    
    def test_csrrc_read_only(self):
        """Test CSRRC with zero mask (read-only)"""
        self.csr_bank.write(0x341, 0xCAFEBABE)
        old_value = EXE.execute_csr_read_clear(self.csr_bank, 0x341, 0)
        self.assertEqual(old_value, 0xCAFEBABE)
        self.assertEqual(self.csr_bank.read(0x341), 0xCAFEBABE)  # Unchanged
    
    # CSRRWI tests (immediate variants)
    def test_csrrwi_parsing(self):
        """Test CSRRWI instruction parsing"""
        instr = Instruction("CSRRWI R7, 0x300, 15")
        self.assertEqual(instr.operation, "CSRRWI")
        self.assertEqual(instr.dest_reg, "R7")
        self.assertEqual(instr.csr_addr, 0x300)
        self.assertEqual(instr.immediate, 15)
        self.assertTrue(instr.has_immediate)
        self.assertEqual(instr.src_regs, [])
    
    def test_csrrwi_execution(self):
        """Test CSRRWI with immediate value"""
        self.csr_bank.write(0x300, 0x00000000)
        old_value = EXE.execute_csr_read_write(self.csr_bank, 0x300, 0x1F)
        self.assertEqual(old_value, 0)
        self.assertEqual(self.csr_bank.read(0x300), 0x1F)
    
    def test_csrrwi_max_immediate(self):
        """Test CSRRWI with max 5-bit immediate (31)"""
        instr = Instruction("CSRRWI R1, 0x340, 31")
        self.assertEqual(instr.immediate, 31)
    
    # CSRRSI tests
    def test_csrrsi_parsing(self):
        """Test CSRRSI instruction parsing"""
        instr = Instruction("CSRRSI R8, 0x304, 10")
        self.assertEqual(instr.operation, "CSRRSI")
        self.assertEqual(instr.dest_reg, "R8")
        self.assertEqual(instr.csr_addr, 0x304)
        self.assertEqual(instr.immediate, 10)
        self.assertTrue(instr.has_immediate)
    
    def test_csrrsi_execution(self):
        """Test CSRRSI set bits with immediate"""
        self.csr_bank.write(0x304, 0x00000010)
        old_value = EXE.execute_csr_read_set(self.csr_bank, 0x304, 0x05)
        self.assertEqual(old_value, 0x10)
        self.assertEqual(self.csr_bank.read(0x304), 0x15)
    
    # CSRRCI tests
    def test_csrrci_parsing(self):
        """Test CSRRCI instruction parsing"""
        instr = Instruction("CSRRCI R9, 0x340, 7")
        self.assertEqual(instr.operation, "CSRRCI")
        self.assertEqual(instr.dest_reg, "R9")
        self.assertEqual(instr.csr_addr, 0x340)
        self.assertEqual(instr.immediate, 7)
        self.assertTrue(instr.has_immediate)
    
    def test_csrrci_execution(self):
        """Test CSRRCI clear bits with immediate"""
        self.csr_bank.write(0x340, 0x0000001F)
        old_value = EXE.execute_csr_read_clear(self.csr_bank, 0x340, 0x0F)
        self.assertEqual(old_value, 0x1F)
        self.assertEqual(self.csr_bank.read(0x340), 0x10)
    
    # Hexadecimal CSR address tests
    def test_csr_hex_address(self):
        """Test CSR with hexadecimal address"""
        instr = Instruction("CSRRW R1, 0xB00, R2")
        self.assertEqual(instr.csr_addr, 0xB00)
    
    def test_csr_decimal_address(self):
        """Test CSR with decimal address"""
        instr = Instruction("CSRRW R1, 768, R2")  # 768 = 0x300
        self.assertEqual(instr.csr_addr, 768)
    
    # Edge cases
    def test_csr_read_only_registers(self):
        """Test that read-only CSRs cannot be written"""
        # mvendorid (0xF11) is read-only
        self.csr_bank.write(0xF11, 0x12345678)
        self.assertEqual(self.csr_bank.read(0xF11), 0x0)  # Should remain 0
    
    def test_csr_cycle_counter(self):
        """Test cycle counter increments"""
        initial = self.csr_bank.read(0xC00)
        self.csr_bank.increment_cycle()
        self.assertEqual(self.csr_bank.read(0xC00), initial + 1)
    
    def test_csr_instret_counter(self):
        """Test instruction-retired counter increments"""
        initial = self.csr_bank.read(0xC02)
        self.csr_bank.increment_instret()
        self.assertEqual(self.csr_bank.read(0xC02), initial + 1)
    
    def test_csr_unknown_address(self):
        """Test reading from unknown CSR address returns 0"""
        value = self.csr_bank.read(0xFFF)
        self.assertEqual(value, 0)
    
    def test_csr_32bit_masking(self):
        """Test that CSR values are masked to 32 bits"""
        self.csr_bank.write(0x340, 0x123456789ABCDEF0)
        self.assertEqual(self.csr_bank.read(0x340), 0x9ABCDEF0)
    
    def test_csr_instruction_integration(self):
        """Test CSR instruction returns proper marker"""
        instr = Instruction("CSRRW R1, 0x300, R2")
        instr.src_values = [0x12345678]
        result, mem_address = EXE.execute_instruction(instr)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'csr')
        self.assertEqual(result['operation'], 'CSRRW')
        self.assertEqual(result['csr_addr'], 0x300)
    
    def test_csr_lowercase(self):
        """Test CSR instructions with lowercase"""
        instr = Instruction("csrrw R1, 0x300, R2")
        self.assertEqual(instr.operation, "CSRRW")
    
    def test_csr_mixed_case(self):
        """Test CSR instructions with mixed case"""
        instr = Instruction("CsRrS R1, 0x304, R2")
        self.assertEqual(instr.operation, "CSRRS")
    
    def test_csr_get_name(self):
        """Test getting human-readable CSR names"""
        self.assertEqual(self.csr_bank.get_csr_name(0x300), 'mstatus')
        self.assertEqual(self.csr_bank.get_csr_name(0xC00), 'cycle')
        self.assertEqual(self.csr_bank.get_csr_name(0xFFF), 'csr_0xfff')


if __name__ == '__main__':
    unittest.main()
