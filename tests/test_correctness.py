#!/usr/bin/env python3
"""
Unit tests for RISC-V pipeline simulator correctness.
Tests functional correctness and instruction completion.
"""

import unittest
import sys
import os

# Add parent directory to path to import pipeline module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import simpy
from pipeline import Pipeline, Instruction


class TestPipelineCorrectness(unittest.TestCase):
    """Test that pipeline produces correct results"""
    
    def test_back_to_back_dependencies(self):
        """Test back-to-back RAW dependencies"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "ADD R4, R1, R5",  # depends on R1
            "ADD R6, R4, R7",  # depends on R4
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 3, "All instructions should complete")
        self.assertEqual(pipeline.stall_count, 6, "Should have 6 stalls (3 per dependency)")
        
    def test_independent_instructions(self):
        """Test independent instructions with no hazards"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "ADD R4, R5, R6",
            "ADD R7, R8, R9",
            "ADD R10, R11, R12",
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 4, "All instructions should complete")
        self.assertEqual(pipeline.stall_count, 0, "No stalls for independent instructions")
        
    def test_load_use_hazard(self):
        """Test LOAD-use hazard"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "LOAD R1, 100(R2)",
            "ADD R3, R1, R4",  # Load-use: needs R1 from LOAD
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 2, "Both instructions should complete")
        self.assertEqual(pipeline.stall_count, 3, "Should have 3 stalls for LOAD-use")
        
    def test_mixed_dependencies(self):
        """Test mixed dependencies"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "SUB R4, R5, R6",  # Independent
            "OR R7, R1, R4",   # Depends on both R1 and R4
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 3, "All instructions should complete")
        self.assertEqual(pipeline.stall_count, 3, "Should have 3 stalls for R1 dependency")
        
    def test_instruction_order_preserved(self):
        """Test that instructions complete in program order"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "SUB R4, R1, R5",
            "OR R6, R1, R7",
        ]
        results = pipeline.run(instructions)
        
        # Verify order is preserved
        for i, (result, original) in enumerate(zip(results, instructions)):
            self.assertEqual(str(result), original, 
                           f"Instruction {i} order not preserved")


class TestInstructionParsing(unittest.TestCase):
    """Test instruction parsing"""
    
    def test_r_type_parsing(self):
        """Test R-type instruction parsing"""
        instr = Instruction("ADD R1, R2, R3")
        self.assertEqual(instr.dest_reg, "R1")
        self.assertIn("R2", instr.src_regs)
        self.assertIn("R3", instr.src_regs)
        self.assertFalse(instr.is_bubble)
        
    def test_load_parsing(self):
        """Test LOAD instruction parsing"""
        instr = Instruction("LOAD R6, 100(R1)")
        self.assertEqual(instr.dest_reg, "R6")
        self.assertIn("R1", instr.src_regs)
        
    def test_store_parsing(self):
        """Test STORE instruction parsing"""
        instr = Instruction("STORE R6, 200(R7)")
        self.assertIsNone(instr.dest_reg)
        self.assertIn("R6", instr.src_regs)
        self.assertIn("R7", instr.src_regs)
        
    def test_bubble_instruction(self):
        """Test bubble/NOP instruction"""
        instr = Instruction("BUBBLE")
        self.assertTrue(instr.is_bubble)
        self.assertIsNone(instr.dest_reg)
        self.assertEqual(len(instr.src_regs), 0)


if __name__ == '__main__':
    unittest.main()
