"""
Test FENCE and FENCE.I memory ordering instructions.

These instructions are NOPs in a single-core simulator without separate I-cache,
but we test that they parse correctly and don't cause errors.
"""
import unittest
from instruction import Instruction
from exe import EXE


class TestFenceInstructions(unittest.TestCase):
    """Test suite for FENCE and FENCE.I instructions"""
    
    def test_fence_parsing(self):
        """Test that FENCE instruction parses correctly"""
        instr = Instruction("FENCE")
        self.assertEqual(instr.operation, "FENCE")
        self.assertIsNone(instr.dest_reg)
        self.assertEqual(instr.src_regs, [])
        self.assertFalse(instr.is_bubble)
    
    def test_fence_i_parsing(self):
        """Test that FENCE.I instruction parses correctly"""
        instr = Instruction("FENCE.I")
        self.assertEqual(instr.operation, "FENCE.I")
        self.assertIsNone(instr.dest_reg)
        self.assertEqual(instr.src_regs, [])
        self.assertFalse(instr.is_bubble)
    
    def test_fence_lowercase(self):
        """Test FENCE instruction with lowercase"""
        instr = Instruction("fence")
        self.assertEqual(instr.operation, "FENCE")
    
    def test_fence_i_lowercase(self):
        """Test FENCE.I instruction with lowercase"""
        instr = Instruction("fence.i")
        self.assertEqual(instr.operation, "FENCE.I")
    
    def test_fence_execution(self):
        """Test that FENCE executes as NOP (returns None)"""
        instr = Instruction("FENCE")
        result, mem_address = EXE.execute_instruction(instr)
        self.assertIsNone(result)
        self.assertIsNone(mem_address)
    
    def test_fence_i_execution(self):
        """Test that FENCE.I executes as NOP (returns None)"""
        instr = Instruction("FENCE.I")
        result, mem_address = EXE.execute_instruction(instr)
        self.assertIsNone(result)
        self.assertIsNone(mem_address)
    
    def test_fence_no_destination(self):
        """Test that FENCE doesn't write to any register"""
        instr = Instruction("FENCE")
        self.assertIsNone(instr.dest_reg)
    
    def test_fence_i_no_destination(self):
        """Test that FENCE.I doesn't write to any register"""
        instr = Instruction("FENCE.I")
        self.assertIsNone(instr.dest_reg)
    
    def test_fence_no_source_regs(self):
        """Test that FENCE doesn't read any registers"""
        instr = Instruction("FENCE")
        self.assertEqual(len(instr.src_regs), 0)
    
    def test_fence_i_no_source_regs(self):
        """Test that FENCE.I doesn't read any registers"""
        instr = Instruction("FENCE.I")
        self.assertEqual(len(instr.src_regs), 0)
    
    def test_fence_multiple_execution(self):
        """Test that multiple FENCE instructions can execute without errors"""
        for _ in range(10):
            instr = Instruction("FENCE")
            result, mem_address = EXE.execute_instruction(instr)
            self.assertIsNone(result)
            self.assertIsNone(mem_address)
    
    def test_fence_i_multiple_execution(self):
        """Test that multiple FENCE.I instructions can execute without errors"""
        for _ in range(10):
            instr = Instruction("FENCE.I")
            result, mem_address = EXE.execute_instruction(instr)
            self.assertIsNone(result)
            self.assertIsNone(mem_address)
    
    def test_fence_mixed_case(self):
        """Test FENCE with mixed case"""
        instr = Instruction("FeNcE")
        self.assertEqual(instr.operation, "FENCE")
    
    def test_fence_i_mixed_case(self):
        """Test FENCE.I with mixed case"""
        instr = Instruction("FenCe.I")
        self.assertEqual(instr.operation, "FENCE.I")


if __name__ == '__main__':
    unittest.main()
