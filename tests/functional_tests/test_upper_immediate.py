"""Functional tests for LUI and AUIPC instructions"""
import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import simpy
from pipeline import Pipeline


class TestUpperImmediateInstructions(unittest.TestCase):
    """Test suite for LUI and AUIPC instructions"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.env = simpy.Environment()
        self.pipeline = Pipeline(self.env)
    
    def run_instructions(self, instructions, initial_pc=0x1000):
        """Helper to run instructions and return pipeline"""
        self.pipeline.register_file.write_pc(initial_pc)
        self.pipeline.run(instructions)
        return self.pipeline
    
    def test_lui_basic(self):
        """Test basic LUI instruction"""
        instructions = ["LUI R1, 0x12345"]
        self.run_instructions(instructions)
        
        result = self.pipeline.register_file.read('R1')
        expected = 0x12345000
        self.assertEqual(result, expected, 
                        f"LUI R1, 0x12345 failed: got {result:#010x}, expected {expected:#010x}")
    
    def test_lui_maximum_value(self):
        """Test LUI with maximum 20-bit immediate"""
        instructions = ["LUI R2, 0xFFFFF"]
        self.run_instructions(instructions)
        
        result = self.pipeline.register_file.read('R2')
        expected = 0xFFFFF000
        self.assertEqual(result, expected,
                        f"LUI with max value failed: got {result:#010x}, expected {expected:#010x}")
    
    def test_lui_zero(self):
        """Test LUI with zero immediate"""
        instructions = ["LUI R3, 0x0"]
        self.run_instructions(instructions)
        
        result = self.pipeline.register_file.read('R3')
        expected = 0x00000000
        self.assertEqual(result, expected,
                        f"LUI with zero failed: got {result:#010x}, expected {expected:#010x}")
    
    def test_lui_multiple(self):
        """Test multiple LUI instructions"""
        instructions = [
            "LUI R1, 0x12345",
            "LUI R2, 0xABCDE",
            "LUI R3, 0xFFFFF",
        ]
        self.run_instructions(instructions)
        
        test_cases = [
            ('R1', 0x12345000),
            ('R2', 0xABCDE000),
            ('R3', 0xFFFFF000),
        ]
        
        for reg, expected in test_cases:
            result = self.pipeline.register_file.read(reg)
            self.assertEqual(result, expected,
                           f"{reg} incorrect: got {result:#010x}, expected {expected:#010x}")
    
    def test_auipc_basic(self):
        """Test basic AUIPC instruction"""
        instructions = ["AUIPC R4, 0x100"]
        initial_pc = 0x1000
        self.run_instructions(instructions, initial_pc=initial_pc)
        
        result = self.pipeline.register_file.read('R4')
        expected = initial_pc + (0x100 << 12)
        self.assertEqual(result, expected,
                        f"AUIPC R4, 0x100 failed: got {result:#010x}, expected {expected:#010x}")
    
    def test_auipc_zero_offset(self):
        """Test AUIPC with zero offset (should return PC)"""
        instructions = ["AUIPC R5, 0x0"]
        initial_pc = 0x2000
        self.run_instructions(instructions, initial_pc=initial_pc)
        
        result = self.pipeline.register_file.read('R5')
        expected = initial_pc
        self.assertEqual(result, expected,
                        f"AUIPC with zero offset failed: got {result:#010x}, expected {expected:#010x}")
    
    def test_auipc_different_pcs(self):
        """Test AUIPC with different PC values"""
        test_cases = [
            (0x1000, 0x10, 0x1000 + 0x10000),
            (0x2000, 0x10, 0x2000 + 0x10000),
            (0x8000, 0x1, 0x8000 + 0x1000),
            (0x10000, 0x100, 0x10000 + 0x100000),
        ]
        
        for pc, imm, expected in test_cases:
            with self.subTest(pc=pc, imm=imm):
                # Create new environment for each test
                env = simpy.Environment()
                pipeline = Pipeline(env)
                pipeline.register_file.write_pc(pc)
                
                instructions = [f"AUIPC R6, {imm:#x}"]
                pipeline.run(instructions)
                
                result = pipeline.register_file.read('R6')
                self.assertEqual(result, expected,
                               f"AUIPC at PC={pc:#x} with imm={imm:#x} failed: "
                               f"got {result:#010x}, expected {expected:#010x}")
    
    def test_auipc_negative_offset(self):
        """Test AUIPC with large immediate (maximum 20-bit value)"""
        instructions = ["AUIPC R7, 0xFFFFF"]
        initial_pc = 0x8000
        self.run_instructions(instructions, initial_pc=initial_pc)
        
        result = self.pipeline.register_file.read('R7')
        # 0xFFFFF << 12 = 0xFFFFF000 (treated as unsigned in our implementation)
        expected = (initial_pc + (0xFFFFF << 12)) & 0xFFFFFFFF
        self.assertEqual(result, expected,
                        f"AUIPC with max offset failed: got {result:#010x}, expected {expected:#010x}")
    
    def test_lui_addi_combination(self):
        """Test LUI + ADDI pattern for loading 32-bit constants"""
        # Load 0x12345678 using LUI + ADDI
        instructions = [
            "LUI R8, 0x12345",
            "ADDI R8, R8, 0x678",
        ]
        self.run_instructions(instructions)
        
        result = self.pipeline.register_file.read('R8')
        expected = 0x12345678
        self.assertEqual(result, expected,
                        f"LUI+ADDI combination failed: got {result:#010x}, expected {expected:#010x}")
    
    def test_auipc_addi_combination(self):
        """Test AUIPC + ADDI pattern for PC-relative addressing"""
        instructions = [
            "AUIPC R9, 0x1",
            "ADDI R9, R9, 0x234",
        ]
        initial_pc = 0x1000
        self.run_instructions(instructions, initial_pc=initial_pc)
        
        result = self.pipeline.register_file.read('R9')
        expected = initial_pc + 0x1000 + 0x234
        self.assertEqual(result, expected,
                        f"AUIPC+ADDI combination failed: got {result:#010x}, expected {expected:#010x}")
    
    def test_lui_different_registers(self):
        """Test LUI writing to different registers"""
        instructions = [
            "LUI R10, 0x11111",
            "LUI R11, 0x22222",
            "LUI R12, 0x33333",
            "LUI R13, 0x44444",
        ]
        self.run_instructions(instructions)
        
        test_cases = [
            ('R10', 0x11111000),
            ('R11', 0x22222000),
            ('R12', 0x33333000),
            ('R13', 0x44444000),
        ]
        
        for reg, expected in test_cases:
            result = self.pipeline.register_file.read(reg)
            self.assertEqual(result, expected,
                           f"{reg} incorrect: got {result:#010x}, expected {expected:#010x}")
    
    def test_lui_overwrites_register(self):
        """Test that LUI properly overwrites existing register values"""
        # Set initial value
        self.pipeline.register_file.write('R14', 0xFFFFFFFF)
        
        instructions = ["LUI R14, 0x12345"]
        self.run_instructions(instructions)
        
        result = self.pipeline.register_file.read('R14')
        expected = 0x12345000
        self.assertEqual(result, expected,
                        f"LUI should overwrite register: got {result:#010x}, expected {expected:#010x}")
    
    def test_auipc_multiple_sequential(self):
        """Test multiple AUIPC instructions in sequence"""
        instructions = [
            "AUIPC R15, 0x1",
            "AUIPC R16, 0x2",
            "AUIPC R17, 0x3",
        ]
        initial_pc = 0x4000
        self.run_instructions(instructions, initial_pc=initial_pc)
        
        # All AUIPC instructions use the same PC value (not incremented in this simulator)
        test_cases = [
            ('R15', initial_pc + 0x1000),
            ('R16', initial_pc + 0x2000),
            ('R17', initial_pc + 0x3000),
        ]
        
        for reg, expected in test_cases:
            result = self.pipeline.register_file.read(reg)
            self.assertEqual(result, expected,
                           f"{reg} incorrect: got {result:#010x}, expected {expected:#010x}")


def run_tests():
    """Run all tests in this module"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestUpperImmediateInstructions)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 70)
    print("LUI and AUIPC Functional Tests")
    print("=" * 70)
    success = run_tests()
    sys.exit(0 if success else 1)
