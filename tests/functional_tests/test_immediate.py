"""Immediate instruction tests"""
import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import simpy
from pipeline import Pipeline


class TestImmediateInstructions(unittest.TestCase):
    """Test immediate (I-type) instructions"""
    
    def test_addi(self):
        """Test ADDI instruction"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["ADDI R1, R2, 100"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "ADDI should complete")
        
    def test_addi_negative(self):
        """Test ADDI with negative immediate"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["ADDI R1, R2, -50"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "ADDI with negative immediate should complete")
        
    def test_andi(self):
        """Test ANDI instruction"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["ANDI R1, R2, 255"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "ANDI should complete")
        
    def test_ori(self):
        """Test ORI instruction"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["ORI R1, R2, 15"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "ORI should complete")
        
    def test_xori(self):
        """Test XORI instruction"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["XORI R1, R2, 255"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "XORI should complete")
        
    def test_immediate_chain(self):
        """Test chain of immediate instructions"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADDI R1, R0, 10",
            "ADDI R1, R1, 20",
            "ANDI R1, R1, 255",
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 3, "All immediate instructions should complete")
        self.assertGreater(pipeline.stall_count, 0, 
                          "Dependencies should cause stalls")


if __name__ == '__main__':
    unittest.main()
