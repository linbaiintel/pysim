"""Instruction type and performance tests"""
import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import simpy
from pipeline import Pipeline


class TestInstructionTypes(unittest.TestCase):
    """Test different instruction types"""
    
    def test_arithmetic_instructions(self):
        """Test various arithmetic instructions"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "SUB R4, R5, R6",
            "ADDI R7, R8, 100",
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 3, "All arithmetic instructions should complete")
        
    def test_logical_instructions(self):
        """Test various logical instructions"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "AND R1, R2, R3",
            "OR R4, R5, R6",
            "XOR R7, R8, R9",
            "ANDI R10, R11, 255",
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 4, "All logical instructions should complete")
        
    def test_memory_instructions(self):
        """Test memory instructions"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "LOAD R1, 100(R2)",
            "STORE R3, 200(R4)",
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 2, "Memory instructions should complete")
        
    def test_mixed_instruction_types(self):
        """Test mix of different instruction types"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",      # Arithmetic
            "AND R4, R5, R6",      # Logical
            "LOAD R7, 100(R8)",    # Memory
            "SLLI R9, R10, 5",     # Shift
            "BEQ R11, R12, 8",     # Branch
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 5, "Mixed instructions should complete")


class TestPerformance(unittest.TestCase):
    """Test pipeline performance characteristics"""
    
    def test_cpi_with_no_stalls(self):
        """Test CPI approaches 1.0 with independent instructions"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        # Many independent instructions with non-overlapping registers
        instructions = [
            "ADD R1, R10, R11",
            "ADD R2, R12, R13",
            "ADD R3, R14, R15",
        ]
        
        results = pipeline.run(instructions)
        
        cycles = pipeline.completion_time  # Use actual completion time, not simulation limit
        num_instructions = len(results)
        cpi = cycles / num_instructions if num_instructions > 0 else 0
        
        # CPI should be close to 1.0 (ideal) + initial fill time
        # For 3 instructions: ~7 cycles (4 for first + 1 each for rest)
        self.assertLess(cpi, 2.5, "CPI should be reasonable with no hazards")
        
    def test_cpi_with_dependencies(self):
        """Test CPI with many dependencies"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "ADD R1, R1, R4",
            "ADD R1, R1, R5",
            "ADD R1, R1, R6",
        ]
        
        results = pipeline.run(instructions)
        
        cycles = pipeline.completion_time  # Use actual completion time
        num_instructions = len(results)
        cpi = cycles / num_instructions if num_instructions > 0 else 0
        
        # CPI should be higher due to stalls
        self.assertGreater(cpi, 2.0, "CPI should be higher with many dependencies")
        
    def test_pipeline_throughput(self):
        """Test that pipeline completes many instructions"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        # Generate many independent instructions
        instructions = []
        for i in range(10):
            base_reg = (i * 3) % 10 + 1
            instructions.append(f"ADD R{base_reg}, R{base_reg+1}, R{base_reg+2}")
        
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), len(instructions), 
                        "All instructions should complete")


if __name__ == '__main__':
    unittest.main()
