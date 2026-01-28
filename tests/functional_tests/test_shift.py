"""Shift instruction tests"""
import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import simpy
from pipeline import Pipeline


class TestShiftInstructions(unittest.TestCase):
    """Test shift instructions"""
    
    def test_slli(self):
        """Test SLLI (Shift Left Logical Immediate)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["SLLI R1, R2, 5"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "SLLI should complete")
        
    def test_srli(self):
        """Test SRLI (Shift Right Logical Immediate)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["SRLI R1, R2, 3"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "SRLI should complete")
        
    def test_srai(self):
        """Test SRAI (Shift Right Arithmetic Immediate)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["SRAI R1, R2, 4"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "SRAI should complete")
        
    def test_sll(self):
        """Test SLL (Shift Left Logical)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["SLL R1, R2, R3"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "SLL should complete")
        
    def test_srl(self):
        """Test SRL (Shift Right Logical)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["SRL R1, R2, R3"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "SRL should complete")
        
    def test_sra(self):
        """Test SRA (Shift Right Arithmetic)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["SRA R1, R2, R3"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "SRA should complete")
        
    def test_shift_dependencies(self):
        """Test shift instructions with dependencies"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADDI R1, R0, 8",
            "SLLI R2, R1, 2",
            "SRLI R3, R2, 1",
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 3, "All shift instructions should complete")
        self.assertGreater(pipeline.stall_count, 0, 
                          "Dependencies should cause stalls")


if __name__ == '__main__':
    unittest.main()
