"""Branch instruction tests"""
import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import simpy
from pipeline import Pipeline


class TestBranchInstructions(unittest.TestCase):
    """Test branch instructions"""
    
    def test_beq(self):
        """Test BEQ (Branch if Equal)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["BEQ R1, R2, 8"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "BEQ should complete")
        
    def test_bne(self):
        """Test BNE (Branch if Not Equal)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["BNE R1, R2, 12"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "BNE should complete")
        
    def test_blt(self):
        """Test BLT (Branch if Less Than)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["BLT R1, R2, 16"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "BLT should complete")
        
    def test_bge(self):
        """Test BGE (Branch if Greater or Equal)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["BGE R1, R2, 20"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "BGE should complete")
        
    def test_bltu(self):
        """Test BLTU (Branch if Less Than Unsigned)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["BLTU R1, R2, 24"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "BLTU should complete")
        
    def test_bgeu(self):
        """Test BGEU (Branch if Greater or Equal Unsigned)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["BGEU R1, R2, 28"]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 1, "BGEU should complete")
        
    def test_branch_with_setup(self):
        """Test branch with setup instructions"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADDI R1, R0, 10",
            "ADDI R2, R0, 20",
            "BEQ R1, R2, 8",
            "ADD R3, R1, R2",
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 4, "All instructions should complete")


if __name__ == '__main__':
    unittest.main()
