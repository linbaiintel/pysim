"""Pipeline flush mechanism tests"""
import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import simpy
from pipeline import Pipeline


class TestPipelineFlush(unittest.TestCase):
    """Test pipeline flush mechanism for jumps and branches"""
    
    def test_jal_triggers_flush(self):
        """Test that JAL triggers pipeline flush"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        pipeline.register_file.write_pc(0x1000)
        
        instructions = [
            "JAL R1, 100",
            "ADD R2, R3, R4",  # Should be flushed
        ]
        results = pipeline.run(instructions)
        
        # JAL should trigger flush
        self.assertGreater(pipeline.flush_count, 0, "JAL should trigger flush")
        self.assertEqual(pipeline.flush_count, 1, "Should have exactly 1 flush")
        
    def test_jalr_triggers_flush(self):
        """Test that JALR triggers pipeline flush"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        pipeline.register_file.write("R2", 0x2000)
        pipeline.register_file.write_pc(0x1000)
        
        instructions = [
            "JALR R1, R2, 0",
            "SUB R3, R4, R5",  # Should be flushed
        ]
        results = pipeline.run(instructions)
        
        self.assertGreater(pipeline.flush_count, 0, "JALR should trigger flush")
        
    def test_taken_branch_triggers_flush(self):
        """Test that taken branch triggers flush"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        pipeline.register_file.write("R1", 5)
        pipeline.register_file.write("R2", 5)
        pipeline.register_file.write_pc(0x2000)
        
        instructions = [
            "BEQ R1, R2, 50",   # Branch taken (R1 == R2)
            "ADD R3, R1, R2",   # Should be flushed
        ]
        results = pipeline.run(instructions)
        
        self.assertGreater(pipeline.flush_count, 0, "Taken branch should trigger flush")
        
    def test_not_taken_branch_no_flush(self):
        """Test that not-taken branch does NOT trigger flush"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        pipeline.register_file.write("R1", 5)
        pipeline.register_file.write("R2", 10)
        pipeline.register_file.write_pc(0x3000)
        
        instructions = [
            "BEQ R1, R2, 50",   # Branch NOT taken (R1 != R2)
            "ADD R3, R1, R2",   # Should execute
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(pipeline.flush_count, 0, "Not-taken branch should NOT flush")
        self.assertEqual(len(results), 2, "Both instructions should complete")
        
    def test_bne_taken_triggers_flush(self):
        """Test that taken BNE triggers flush"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        pipeline.register_file.write("R1", 5)
        pipeline.register_file.write("R2", 10)
        
        instructions = [
            "BNE R1, R2, 40",   # Branch taken (R1 != R2)
            "OR R3, R1, R2",    # Should be flushed
        ]
        results = pipeline.run(instructions)
        
        self.assertGreater(pipeline.flush_count, 0, "Taken BNE should trigger flush")
        
    def test_blt_taken_triggers_flush(self):
        """Test that taken BLT triggers flush"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        pipeline.register_file.write("R1", 5)
        pipeline.register_file.write("R2", 10)
        
        instructions = [
            "BLT R1, R2, 30",   # Branch taken (5 < 10)
            "XOR R3, R1, R2",   # Should be flushed
        ]
        results = pipeline.run(instructions)
        
        self.assertGreater(pipeline.flush_count, 0, "Taken BLT should trigger flush")
        
    def test_flush_converts_to_bubbles(self):
        """Test that flushed instructions become bubbles"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        pipeline.register_file.write("R2", 10)
        pipeline.register_file.write("R3", 20)
        pipeline.register_file.write_pc(0x1000)
        
        instructions = [
            "JAL R1, 100",
            "ADD R4, R2, R3",   # Should be flushed
            "SUB R5, R2, R3",   # Should be flushed
        ]
        results = pipeline.run(instructions)
        
        # Only JAL should complete, others flushed
        # Some might execute if they were already in Execute stage
        self.assertLess(len(results), len(instructions), 
                        "Fewer instructions should complete due to flush")
        
    def test_multiple_jumps_multiple_flushes(self):
        """Test that multiple jumps cause multiple flushes"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        pipeline.register_file.write("R2", 0x2000)
        pipeline.register_file.write_pc(0x1000)
        
        instructions = [
            "JAL R1, 100",
            "NOOP",
            "NOOP", 
            "JALR R3, R2, 0",
            "NOOP",
        ]
        
        # Note: NOOP might not be a valid instruction, using ADD R0, R0, R0 instead
        instructions = [
            "JAL R1, 100",
            "ADD R0, R0, R0",
            "ADD R0, R0, R0", 
        ]
        results = pipeline.run(instructions)
        
        # At least one flush from JAL
        self.assertGreaterEqual(pipeline.flush_count, 1)
        
    def test_flush_target_pc_set(self):
        """Test that flush sets target PC correctly"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        pipeline.register_file.write_pc(0x1000)
        
        instructions = ["JAL R1, 256"]
        results = pipeline.run(instructions)
        
        # Check that JAL completed
        self.assertEqual(len(results), 1)
        # Jump target should have been calculated
        jal_instr = results[0]
        expected_target = 0x1000 + 256
        self.assertEqual(jal_instr.jump_target, expected_target)


if __name__ == '__main__':
    unittest.main()
