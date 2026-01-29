"""
Test MRET (Machine Return) instruction.

Tests MRET parsing and execution, including CSR state restoration.
"""
import unittest
from instruction import Instruction
from exe import EXE
from csr import CSRBank


class TestMRETInstruction(unittest.TestCase):
    """Test suite for MRET instruction"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.csr_bank = CSRBank()
    
    # Parsing tests
    def test_mret_parsing(self):
        """Test MRET instruction parsing"""
        instr = Instruction("MRET")
        self.assertEqual(instr.operation, "MRET")
        self.assertIsNone(instr.dest_reg)
        self.assertEqual(instr.src_regs, [])
    
    def test_mret_case_insensitive(self):
        """Test MRET parsing is case insensitive"""
        instr_lower = Instruction("mret")
        instr_upper = Instruction("MRET")
        instr_mixed = Instruction("MrEt")
        
        self.assertEqual(instr_lower.operation, "MRET")
        self.assertEqual(instr_upper.operation, "MRET")
        self.assertEqual(instr_mixed.operation, "MRET")
    
    # Basic execution tests
    def test_mret_execution_returns_type(self):
        """Test MRET execution returns correct type"""
        result = EXE.execute_mret(self.csr_bank)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'mret')
        self.assertIn('new_pc', result)
    
    def test_mret_returns_mepc_value(self):
        """Test MRET returns PC value from mepc CSR"""
        # Set mepc to some address
        self.csr_bank.write(0x341, 0x1000)
        
        result = EXE.execute_mret(self.csr_bank)
        self.assertEqual(result['new_pc'], 0x1000)
    
    def test_mret_with_different_mepc_values(self):
        """Test MRET with various mepc values"""
        test_values = [0x0, 0x1234, 0xABCD, 0x80000000, 0xFFFFFFFC]
        
        for expected_pc in test_values:
            with self.subTest(expected_pc=expected_pc):
                self.csr_bank.write(0x341, expected_pc)
                result = EXE.execute_mret(self.csr_bank)
                self.assertEqual(result['new_pc'], expected_pc)
    
    # mstatus manipulation tests
    def test_mret_restores_mie_from_mpie(self):
        """Test MRET restores MIE bit from MPIE bit"""
        # Set mstatus with MPIE=1, MIE=0
        # Bit 7 (MPIE) = 1, Bit 3 (MIE) = 0
        mstatus = 0x80  # MPIE=1
        self.csr_bank.write(0x300, mstatus)
        
        EXE.execute_mret(self.csr_bank)
        
        new_mstatus = self.csr_bank.read(0x300)
        mie = (new_mstatus >> 3) & 0x1
        
        self.assertEqual(mie, 1, "MIE should be 1 after MRET when MPIE was 1")
    
    def test_mret_mpie_becomes_zero_when_mpie_is_zero(self):
        """Test MRET sets MIE=0 when MPIE was 0"""
        # Set mstatus with MPIE=0, MIE=1
        # Bit 7 (MPIE) = 0, Bit 3 (MIE) = 1
        mstatus = 0x08  # MIE=1, MPIE=0
        self.csr_bank.write(0x300, mstatus)
        
        EXE.execute_mret(self.csr_bank)
        
        new_mstatus = self.csr_bank.read(0x300)
        mie = (new_mstatus >> 3) & 0x1
        
        self.assertEqual(mie, 0, "MIE should be 0 after MRET when MPIE was 0")
    
    def test_mret_sets_mpie_to_one(self):
        """Test MRET sets MPIE bit to 1"""
        # Start with MPIE=0
        mstatus = 0x00
        self.csr_bank.write(0x300, mstatus)
        
        EXE.execute_mret(self.csr_bank)
        
        new_mstatus = self.csr_bank.read(0x300)
        mpie = (new_mstatus >> 7) & 0x1
        
        self.assertEqual(mpie, 1, "MPIE should be 1 after MRET")
    
    def test_mret_clears_mpp_to_user_mode(self):
        """Test MRET clears MPP bits to 0 (User mode)"""
        # Set mstatus with MPP=3 (Machine mode)
        # Bits 11-12 (MPP) = 0b11 = 3
        mstatus = 0x1800  # MPP=3
        self.csr_bank.write(0x300, mstatus)
        
        EXE.execute_mret(self.csr_bank)
        
        new_mstatus = self.csr_bank.read(0x300)
        mpp = (new_mstatus >> 11) & 0x3
        
        self.assertEqual(mpp, 0, "MPP should be 0 (User mode) after MRET")
    
    def test_mret_preserves_other_mstatus_bits(self):
        """Test MRET preserves other mstatus bits"""
        # Set some other bits in mstatus (not MIE, MPIE, or MPP)
        # Bit 0-2, 4-6, 8-10, 13-31
        mstatus = 0xFFFF_FFFF  # All bits set
        self.csr_bank.write(0x300, mstatus)
        
        EXE.execute_mret(self.csr_bank)
        
        new_mstatus = self.csr_bank.read(0x300)
        
        # Check that bits outside MIE (3), MPIE (7), MPP (11-12) are preserved
        # We expect: MIE=1 (from MPIE), MPIE=1 (set), MPP=0 (cleared)
        # So bits that should be 1: all except MPP (11-12) which become 0
        
        # Mask out MIE, MPIE, MPP
        mask_out = ~((1 << 3) | (1 << 7) | (0x3 << 11))
        preserved_bits = new_mstatus & mask_out
        expected_preserved = 0xFFFF_FFFF & mask_out
        
        self.assertEqual(preserved_bits, expected_preserved, 
                        "Other mstatus bits should be preserved")
    
    def test_mret_complete_scenario(self):
        """Test complete MRET scenario: trap entry and return"""
        # Simulate trap entry state:
        # 1. mepc contains return address
        # 2. mstatus.MPIE contains old MIE value
        # 3. mstatus.MPP contains old privilege mode
        # 4. mstatus.MIE is cleared (interrupts disabled in trap)
        
        return_address = 0x2000
        self.csr_bank.write(0x341, return_address)  # mepc
        
        # Set mstatus: MPIE=1 (interrupts were enabled before trap)
        #              MIE=0 (interrupts disabled during trap)
        #              MPP=3 (was in Machine mode)
        mstatus = (1 << 7) | (0x3 << 11)  # MPIE=1, MPP=3, MIE=0
        self.csr_bank.write(0x300, mstatus)
        
        # Execute MRET
        result = EXE.execute_mret(self.csr_bank)
        
        # Check PC is restored
        self.assertEqual(result['new_pc'], return_address)
        
        # Check mstatus is updated correctly
        new_mstatus = self.csr_bank.read(0x300)
        mie = (new_mstatus >> 3) & 0x1
        mpie = (new_mstatus >> 7) & 0x1
        mpp = (new_mstatus >> 11) & 0x3
        
        self.assertEqual(mie, 1, "MIE should be restored to 1")
        self.assertEqual(mpie, 1, "MPIE should be set to 1")
        self.assertEqual(mpp, 0, "MPP should be cleared to 0")
    
    # Edge cases
    def test_mret_with_none_csr_bank(self):
        """Test MRET with None CSR bank (error case)"""
        result = EXE.execute_mret(None)
        self.assertEqual(result['type'], 'mret')
        self.assertEqual(result['new_pc'], 0)
    
    def test_mret_execute_instruction_integration(self):
        """Test MRET through execute_instruction interface"""
        instr = Instruction("MRET")
        result, mem_address = EXE.execute_instruction(instr)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'mret')
        self.assertIsNone(mem_address)


if __name__ == '__main__':
    unittest.main()
