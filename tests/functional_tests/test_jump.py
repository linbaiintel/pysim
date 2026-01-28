"""Jump instruction tests (JAL, JALR)"""
import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import simpy
from pipeline import Pipeline
from instruction import Instruction


class TestJumpInstructions(unittest.TestCase):
    """Test JAL and JALR jump instructions"""
    
    def test_jal_parsing(self):
        """Test JAL instruction parsing"""
        instr = Instruction("JAL R1, 100")
        self.assertEqual(instr.operation, "JAL")
        self.assertEqual(instr.dest_reg, "R1")
        self.assertEqual(instr.offset, 100)
        self.assertTrue(instr.is_jump)
        self.assertEqual(len(instr.src_regs), 0)
        
    def test_jalr_parsing(self):
        """Test JALR instruction parsing"""
        instr = Instruction("JALR R1, R2, 50")
        self.assertEqual(instr.operation, "JALR")
        self.assertEqual(instr.dest_reg, "R1")
        self.assertIn("R2", instr.src_regs)
        self.assertEqual(instr.offset, 50)
        self.assertTrue(instr.is_jump)
        
    def test_jal_execution(self):
        """Test JAL instruction execution"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        # Initialize PC to 0x1000
        pipeline.register_file.write_pc(0x1000)
        
        instructions = ["JAL R1, 100"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "JAL should complete")
        # Check that return address (PC+4 = 0x1004) was stored
        return_addr = pipeline.register_file.read("R1")
        self.assertEqual(return_addr, 0x1004, "Return address should be PC+4")
        
    def test_jalr_execution(self):
        """Test JALR instruction execution"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        # Set R2 to base address 0x2000
        pipeline.register_file.write("R2", 0x2000)
        # Initialize PC to 0x1000
        pipeline.register_file.write_pc(0x1000)
        
        instructions = ["JALR R1, R2, 50"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "JALR should complete")
        # Check that return address (PC+4 = 0x1004) was stored
        return_addr = pipeline.register_file.read("R1")
        self.assertEqual(return_addr, 0x1004, "Return address should be PC+4")
        
    def test_jal_negative_offset(self):
        """Test JAL with negative offset (backward jump)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        pipeline.register_file.write_pc(0x1000)
        
        instructions = ["JAL R3, -100"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1)
        return_addr = pipeline.register_file.read("R3")
        self.assertEqual(return_addr, 0x1004)
        
    def test_jalr_with_zero_offset(self):
        """Test JALR with zero offset"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        pipeline.register_file.write("R5", 0x3000)
        pipeline.register_file.write_pc(0x1000)
        
        instructions = ["JALR R4, R5, 0"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1)
        return_addr = pipeline.register_file.read("R4")
        self.assertEqual(return_addr, 0x1004)
        
    def test_jal_link_to_r0(self):
        """Test JAL storing to R0 (should remain 0 if implemented)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        pipeline.register_file.write_pc(0x2000)
        
        instructions = ["JAL R0, 200"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1)
        # R0 should remain 0 (RISC-V convention)
        self.assertEqual(pipeline.register_file.read("R0"), 0)
        
    def test_jal_then_other_instruction(self):
        """Test JAL followed by another instruction"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        pipeline.register_file.write("R2", 10)
        pipeline.register_file.write("R3", 20)
        pipeline.register_file.write_pc(0x1000)
        
        instructions = [
            "JAL R1, 100",
            "ADD R4, R2, R3",
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 2)
        # Both instructions should complete
        return_addr = pipeline.register_file.read("R1")
        self.assertEqual(return_addr, 0x1004)
        sum_result = pipeline.register_file.read("R4")
        self.assertEqual(sum_result, 30)
        
    def test_jalr_dependency(self):
        """Test JALR with dependency on previous instruction"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        pipeline.register_file.write("R2", 0x1000)
        pipeline.register_file.write_pc(0x1000)
        
        instructions = [
            "ADDI R3, R2, 256",  # R3 = R2 + 256
            "JALR R1, R3, 0",    # Jump to address in R3
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 2)
        # Check stalls occurred due to dependency
        self.assertGreater(pipeline.stall_count, 0)
        
    def test_function_call_pattern(self):
        """Test function call pattern with JAL and JALR"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        pipeline.register_file.write("R10", 5)
        pipeline.register_file.write("R11", 10)
        pipeline.register_file.write_pc(0x1000)
        
        instructions = [
            "JAL R1, 20",           # Call function at PC+20, flushes following
            "ADD R12, R10, R11",    # Code after call - may be flushed
            # Simulated function body
            "ADDI R10, R10, 1",     # Modify R10
            "JALR R0, R1, 0",       # Return (jump to address in R1), flushes following
        ]
        results = pipeline.run(instructions)
        
        # With pipeline flush, some instructions will be flushed
        # JAL completes, then flushes following instructions
        # At least JAL should complete
        self.assertGreaterEqual(len(results), 1, "At least JAL should complete")
        # R1 should have return address
        return_addr = pipeline.register_file.read("R1")
        self.assertEqual(return_addr, 0x1004)
        # Check that flush occurred
        self.assertGreater(pipeline.flush_count, 0, "Pipeline should have been flushed")
        
    def test_multiple_jal_instructions(self):
        """Test multiple JAL instructions in sequence"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        # Note: With pipeline flush, each JAL will flush following instructions
        pipeline.register_file.write_pc(0x1000)
        
        instructions = [
            "JAL R1, 100",
            "JAL R2, 200",  # Will be flushed by first JAL
            "JAL R3, 300",  # Will be flushed by first JAL
        ]
        results = pipeline.run(instructions)
        
        # Only first JAL should complete, others are flushed
        self.assertGreaterEqual(len(results), 1, "At least first JAL should complete")
        # First JAL should complete and store return address
        self.assertEqual(pipeline.register_file.read("R1"), 0x1004)
        # Check that flush occurred
        self.assertGreater(pipeline.flush_count, 0, "Pipeline should have been flushed")
        
    def test_jalr_clears_lsb(self):
        """Test that JALR clears the LSB of target address per RISC-V spec"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        # Set R2 to odd address
        pipeline.register_file.write("R2", 0x2001)
        pipeline.register_file.write_pc(0x1000)
        
        instructions = ["JALR R1, R2, 0"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1)
        # Jump target should have LSB cleared (checked in instruction.jump_target)
        instr = results[0]
        # Target should be 0x2000 (LSB cleared)
        self.assertEqual(instr.jump_target & 1, 0, "JALR should clear LSB of target")


if __name__ == '__main__':
    unittest.main()
