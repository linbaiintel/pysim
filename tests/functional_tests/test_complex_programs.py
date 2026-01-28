"""Complex program tests"""
import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import simpy
from pipeline import Pipeline


class TestComplexPrograms(unittest.TestCase):
    """Test complex instruction sequences"""
    
    def test_fibonacci_like_sequence(self):
        """Test Fibonacci-like computation"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADDI R1, R0, 1",      # R1 = 1
            "ADDI R2, R0, 1",      # R2 = 1
            "ADD R3, R1, R2",      # R3 = R1 + R2
            "ADD R4, R2, R3",      # R4 = R2 + R3
            "ADD R5, R3, R4",      # R5 = R3 + R4
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 5, "All Fibonacci instructions should complete")
        
    def test_array_sum_pattern(self):
        """Test array summation pattern"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADDI R10, R0, 0",      # sum = 0
            "LOAD R1, 0(R20)",      # load array[0]
            "ADD R10, R10, R1",     # sum += array[0]
            "LOAD R2, 4(R20)",      # load array[1]
            "ADD R10, R10, R2",     # sum += array[1]
            "LOAD R3, 8(R20)",      # load array[2]
            "ADD R10, R10, R3",     # sum += array[2]
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 7, "All array sum instructions should complete")
        
    def test_nested_arithmetic(self):
        """Test nested arithmetic operations"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADDI R1, R0, 5",
            "ADDI R2, R0, 3",
            "ADD R3, R1, R2",      # R3 = R1 + R2
            "SUB R4, R3, R1",      # R4 = R3 - R1
            "AND R5, R3, R4",      # R5 = R3 & R4
            "OR R6, R3, R5",       # R6 = R3 | R5
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 6, "All nested arithmetic should complete")
        
    def test_memory_copy_pattern(self):
        """Test memory copy pattern"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "LOAD R1, 0(R10)",
            "STORE R1, 0(R11)",
            "LOAD R2, 4(R10)",
            "STORE R2, 4(R11)",
            "LOAD R3, 8(R10)",
            "STORE R3, 8(R11)",
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 6, "All memory copy instructions should complete")
        
    def test_conditional_computation(self):
        """Test conditional-like computation pattern"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADDI R1, R0, 10",
            "ADDI R2, R0, 20",
            "SLT R3, R1, R2",      # R3 = (R1 < R2)
            "BEQ R3, R0, 8",       # if R3 == 0, skip next
            "ADD R4, R1, R2",      # R4 = R1 + R2
            "SUB R5, R2, R1",      # R5 = R2 - R1
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 6, "All conditional instructions should complete")


if __name__ == '__main__':
    unittest.main()
