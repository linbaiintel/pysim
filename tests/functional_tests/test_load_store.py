"""Functional tests for LOAD and STORE instructions"""
import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import simpy
from pipeline import Pipeline


class TestLoadStoreInstructions(unittest.TestCase):
    """Test suite for LOAD and STORE instructions"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.env = simpy.Environment()
        self.pipeline = Pipeline(self.env)
    
    def run_instructions(self, instructions, initial_regs=None):
        """Helper to run instructions with optional register initialization"""
        if initial_regs:
            for reg, value in initial_regs.items():
                self.pipeline.register_file.write(reg, value)
        self.pipeline.run(instructions)
        return self.pipeline
    
    # ========================================================================
    # WORD (32-bit) LOAD/STORE TESTS
    # ========================================================================
    
    def test_sw_lw_basic(self):
        """Test basic SW (Store Word) and LW (Load Word)"""
        instructions = [
            "SW R1, 0(R2)",
            "LW R3, 0(R2)",
        ]
        self.run_instructions(instructions, {'R1': 0x12345678, 'R2': 100})
        
        stored = self.pipeline.register_file.read('R1')
        loaded = self.pipeline.register_file.read('R3')
        self.assertEqual(stored, loaded, 
                        f"SW/LW failed: stored {stored:#010x}, loaded {loaded:#010x}")
    
    def test_lw_sw_maximum_value(self):
        """Test LW/SW with maximum 32-bit value"""
        instructions = [
            "SW R4, 0(R5)",
            "LW R6, 0(R5)",
        ]
        self.run_instructions(instructions, {'R4': 0xFFFFFFFF, 'R5': 200})
        
        result = self.pipeline.register_file.read('R6')
        expected = 0xFFFFFFFF
        self.assertEqual(result, expected,
                        f"LW max value failed: got {result:#010x}, expected {expected:#010x}")
    
    def test_lw_sw_with_offset(self):
        """Test LW/SW with non-zero offset"""
        instructions = [
            "SW R7, 20(R8)",
            "LW R9, 20(R8)",
        ]
        self.run_instructions(instructions, {'R7': 0xABCDEF01, 'R8': 300})
        
        result = self.pipeline.register_file.read('R9')
        expected = 0xABCDEF01
        self.assertEqual(result, expected,
                        f"LW with offset failed: got {result:#010x}, expected {expected:#010x}")
    
    def test_multiple_sw_lw(self):
        """Test multiple SW/LW operations to different addresses"""
        instructions = [
            "SW R1, 0(R10)",
            "SW R2, 4(R10)",
            "SW R3, 8(R10)",
            "LW R4, 0(R10)",
            "LW R5, 4(R10)",
            "LW R6, 8(R10)",
        ]
        initial_regs = {
            'R1': 0x11111111,
            'R2': 0x22222222,
            'R3': 0x33333333,
            'R10': 400
        }
        self.run_instructions(instructions, initial_regs)
        
        self.assertEqual(self.pipeline.register_file.read('R4'), 0x11111111)
        self.assertEqual(self.pipeline.register_file.read('R5'), 0x22222222)
        self.assertEqual(self.pipeline.register_file.read('R6'), 0x33333333)
    
    # ========================================================================
    # HALFWORD (16-bit) LOAD/STORE TESTS
    # ========================================================================
    
    def test_sh_lh_signed(self):
        """Test SH (Store Halfword) and LH (Load Halfword) with sign extension"""
        instructions = [
            "SH R11, 0(R12)",
            "LH R13, 0(R12)",
        ]
        # 0xFFFF should sign-extend to 0xFFFFFFFF
        self.run_instructions(instructions, {'R11': 0x0000FFFF, 'R12': 500})
        
        result = self.pipeline.register_file.read('R13')
        expected = 0xFFFFFFFF  # Sign-extended
        self.assertEqual(result, expected,
                        f"LH sign extension failed: got {result:#010x}, expected {expected:#010x}")
    
    def test_sh_lh_positive(self):
        """Test SH/LH with positive value (no sign extension)"""
        instructions = [
            "SH R14, 0(R15)",
            "LH R16, 0(R15)",
        ]
        # 0x7FFF should sign-extend to 0x00007FFF (positive)
        self.run_instructions(instructions, {'R14': 0x00007FFF, 'R15': 600})
        
        result = self.pipeline.register_file.read('R16')
        expected = 0x00007FFF  # Positive, no sign extension
        self.assertEqual(result, expected,
                        f"LH positive value failed: got {result:#010x}, expected {expected:#010x}")
    
    def test_sh_lhu_unsigned(self):
        """Test SH and LHU (Load Halfword Unsigned) - no sign extension"""
        instructions = [
            "SH R17, 0(R18)",
            "LHU R19, 0(R18)",
        ]
        # 0xFFFF should zero-extend to 0x0000FFFF
        self.run_instructions(instructions, {'R17': 0x0000FFFF, 'R18': 700})
        
        result = self.pipeline.register_file.read('R19')
        expected = 0x0000FFFF  # Zero-extended
        self.assertEqual(result, expected,
                        f"LHU failed: got {result:#010x}, expected {expected:#010x}")
    
    def test_sh_lhu_with_offset(self):
        """Test SH/LHU with offset"""
        instructions = [
            "SH R20, 10(R21)",
            "LHU R22, 10(R21)",
        ]
        self.run_instructions(instructions, {'R20': 0x0000ABCD, 'R21': 800})
        
        result = self.pipeline.register_file.read('R22')
        expected = 0x0000ABCD
        self.assertEqual(result, expected,
                        f"LHU with offset failed: got {result:#010x}, expected {expected:#010x}")
    
    # ========================================================================
    # BYTE (8-bit) LOAD/STORE TESTS
    # ========================================================================
    
    def test_sb_lb_signed(self):
        """Test SB (Store Byte) and LB (Load Byte) with sign extension"""
        instructions = [
            "SB R23, 0(R24)",
            "LB R25, 0(R24)",
        ]
        # 0xFF should sign-extend to 0xFFFFFFFF
        self.run_instructions(instructions, {'R23': 0x000000FF, 'R24': 900})
        
        result = self.pipeline.register_file.read('R25')
        expected = 0xFFFFFFFF  # Sign-extended
        self.assertEqual(result, expected,
                        f"LB sign extension failed: got {result:#010x}, expected {expected:#010x}")
    
    def test_sb_lb_positive(self):
        """Test SB/LB with positive value"""
        instructions = [
            "SB R26, 0(R27)",
            "LB R28, 0(R27)",
        ]
        # 0x7F should sign-extend to 0x0000007F (positive)
        self.run_instructions(instructions, {'R26': 0x0000007F, 'R27': 1000})
        
        result = self.pipeline.register_file.read('R28')
        expected = 0x0000007F  # Positive, no sign extension
        self.assertEqual(result, expected,
                        f"LB positive value failed: got {result:#010x}, expected {expected:#010x}")
    
    def test_sb_lbu_unsigned(self):
        """Test SB and LBU (Load Byte Unsigned) - no sign extension"""
        instructions = [
            "SB R29, 0(R30)",
            "LBU R31, 0(R30)",
        ]
        # 0xFF should zero-extend to 0x000000FF
        self.run_instructions(instructions, {'R29': 0x000000FF, 'R30': 1100})
        
        result = self.pipeline.register_file.read('R31')
        expected = 0x000000FF  # Zero-extended
        self.assertEqual(result, expected,
                        f"LBU failed: got {result:#010x}, expected {expected:#010x}")
    
    def test_sb_lbu_with_offset(self):
        """Test SB/LBU with offset"""
        instructions = [
            "SB R1, 15(R2)",
            "LBU R3, 15(R2)",
        ]
        self.run_instructions(instructions, {'R1': 0x000000AB, 'R2': 1200})
        
        result = self.pipeline.register_file.read('R3')
        expected = 0x000000AB
        self.assertEqual(result, expected,
                        f"LBU with offset failed: got {result:#010x}, expected {expected:#010x}")
    
    # ========================================================================
    # MIXED SIZE OPERATIONS
    # ========================================================================
    
    def test_mixed_store_sizes(self):
        """Test storing different sizes to adjacent memory locations"""
        instructions = [
            "SW R4, 0(R10)",    # Store word at 0
            "SH R5, 4(R10)",    # Store halfword at 4
            "SB R6, 6(R10)",    # Store byte at 6
            "LW R7, 0(R10)",    # Load word from 0
            "LHU R8, 4(R10)",   # Load halfword from 4
            "LBU R9, 6(R10)",   # Load byte from 6
        ]
        initial_regs = {
            'R4': 0xDEADBEEF,
            'R5': 0x0000CAFE,
            'R6': 0x000000BA,
            'R10': 1300
        }
        self.run_instructions(instructions, initial_regs)
        
        self.assertEqual(self.pipeline.register_file.read('R7'), 0xDEADBEEF)
        self.assertEqual(self.pipeline.register_file.read('R8'), 0x0000CAFE)
        self.assertEqual(self.pipeline.register_file.read('R9'), 0x000000BA)
    
    def test_overwrite_memory(self):
        """Test overwriting memory with different sizes"""
        instructions = [
            "SW R11, 0(R12)",   # Store word
            "SB R13, 0(R12)",   # Overwrite first byte
            "LW R14, 0(R12)",   # Load word (should have modified first byte)
        ]
        initial_regs = {
            'R11': 0x12345678,
            'R12': 1400,
            'R13': 0x000000FF
        }
        self.run_instructions(instructions, initial_regs)
        
        result = self.pipeline.register_file.read('R14')
        # First byte changed from 0x78 to 0xFF (little-endian)
        expected = 0x123456FF
        self.assertEqual(result, expected,
                        f"Memory overwrite failed: got {result:#010x}, expected {expected:#010x}")
    
    # ========================================================================
    # EDGE CASES
    # ========================================================================
    
    def test_load_store_zero(self):
        """Test loading and storing zero value"""
        instructions = [
            "SW R15, 0(R16)",
            "LW R17, 0(R16)",
        ]
        self.run_instructions(instructions, {'R15': 0x00000000, 'R16': 1500})
        
        result = self.pipeline.register_file.read('R17')
        expected = 0x00000000
        self.assertEqual(result, expected,
                        f"Load/store zero failed: got {result:#010x}, expected {expected:#010x}")
    
    def test_store_load_sequence(self):
        """Test sequential store and load operations"""
        instructions = [
            "SW R18, 0(R20)",
            "SW R19, 4(R20)",
            "LW R21, 0(R20)",
            "LW R22, 4(R20)",
        ]
        initial_regs = {
            'R18': 0x11111111,
            'R19': 0x22222222,
            'R20': 1600
        }
        self.run_instructions(instructions, initial_regs)
        
        self.assertEqual(self.pipeline.register_file.read('R21'), 0x11111111)
        self.assertEqual(self.pipeline.register_file.read('R22'), 0x22222222)


def run_tests():
    """Run all tests in this module"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestLoadStoreInstructions)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 70)
    print("LOAD/STORE Functional Tests")
    print("=" * 70)
    success = run_tests()
    sys.exit(0 if success else 1)
