#!/usr/bin/env python3
"""
Unit tests for pipeline edge cases and special scenarios.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import simpy
from pipeline import Pipeline


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and corner conditions"""
    
    def test_single_instruction(self):
        """Test pipeline with single instruction"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        results = pipeline.run(["ADD R1, R2, R3"])
        
        self.assertEqual(len(results), 1, "Single instruction should complete")
        self.assertEqual(pipeline.stall_count, 0, "No stalls for single instruction")
        
    def test_two_instructions(self):
        """Test pipeline with two instructions"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        results = pipeline.run(["ADD R1, R2, R3", "SUB R4, R5, R6"])
        
        self.assertEqual(len(results), 2, "Both instructions should complete")
        
    def test_three_way_dependency_chain(self):
        """Test three-way dependency chain"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "ADD R4, R1, R5",
            "ADD R6, R4, R7"
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 3, "All instructions should complete")
        self.assertGreaterEqual(pipeline.stall_count, 6, 
                               "Dependency chain should cause multiple stalls")
                               
    def test_store_instruction(self):
        """Test STORE instruction (no writeback register)"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "STORE R1, 100(R4)"
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 2, "Both instructions should complete")
        
    def test_load_store_sequence(self):
        """Test LOAD followed by STORE"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "LOAD R1, 100(R2)",
            "STORE R1, 200(R3)"
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 2, "Both instructions should complete")
        self.assertGreater(pipeline.stall_count, 0, 
                          "STORE depends on LOAD result")
                          
    def test_all_same_destination(self):
        """Test multiple instructions writing to same register"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "SUB R1, R4, R5",
            "OR R1, R6, R7",
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 3, "All instructions should complete")
        # In-order pipeline shouldn't stall for WAW


class TestInstructionTypes(unittest.TestCase):
    """Test different instruction types"""
    
    def test_arithmetic_instructions(self):
        """Test various arithmetic instructions"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "SUB R4, R5, R6",
            "OR R7, R8, R9",
            "AND R10, R11, R12",
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 4, "All arithmetic instructions should complete")
        
    def test_memory_instructions(self):
        """Test LOAD and STORE instructions"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "LOAD R1, 0(R2)",
            "LOAD R3, 100(R4)",
            "STORE R1, 200(R5)",
            "STORE R3, 300(R6)",
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 4, "All memory instructions should complete")
        
    def test_mixed_instruction_types(self):
        """Test mix of arithmetic and memory instructions"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "LOAD R4, 100(R5)",
            "SUB R6, R1, R4",
            "STORE R6, 200(R7)",
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 4, "Mixed instruction types should complete")


class TestPerformance(unittest.TestCase):
    """Test performance metrics"""
    
    def test_cpi_for_independent_instructions(self):
        """Test CPI for independent instructions"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "SUB R4, R5, R6",
            "OR R7, R8, R9",
            "AND R10, R11, R12",
        ]
        results = pipeline.run(instructions)
        
        cpi = env.now / len(results)
        # For a 5-stage pipeline with 4 instructions:
        # First instruction takes 5 cycles, then 1 per instruction = 5 + 3 = 8 cycles
        # CPI = 8/4 = 2.0 in ideal case, but could be higher
        self.assertLess(cpi, 6.0, "CPI should be reasonable for independent instructions")
        
    def test_stall_count_tracking(self):
        """Test that stall count is properly tracked"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "ADD R4, R1, R5",
        ]
        results = pipeline.run(instructions)
        
        self.assertIsInstance(pipeline.stall_count, int, "Stall count should be integer")
        self.assertGreaterEqual(pipeline.stall_count, 0, "Stall count should be non-negative")


if __name__ == '__main__':
    unittest.main()
