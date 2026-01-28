"""Comparison instruction tests"""
import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import simpy
from pipeline import Pipeline


class TestComparisonInstructions(unittest.TestCase):
    """Test comparison/set instructions"""
    
    def test_slt(self):
        """Test SLT (Set Less Than)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["SLT R1, R2, R3"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "SLT should complete")
        
    def test_sltu(self):
        """Test SLTU (Set Less Than Unsigned)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["SLTU R1, R2, R3"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "SLTU should complete")
        
    def test_slti(self):
        """Test SLTI (Set Less Than Immediate)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["SLTI R1, R2, 100"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "SLTI should complete")
        
    def test_sltiu(self):
        """Test SLTIU (Set Less Than Immediate Unsigned)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["SLTIU R1, R2, 100"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "SLTIU should complete")
        
    def test_comparison_chain(self):
        """Test chain of comparison instructions"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADDI R1, R0, 10",
            "ADDI R2, R0, 20",
            "SLT R3, R1, R2",
            "SLTU R4, R2, R1",
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 4, "All comparison instructions should complete")


if __name__ == '__main__':
    unittest.main()
