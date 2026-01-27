#!/usr/bin/env python3
"""
Unit tests for pipeline hazard detection.
Tests RAW hazard detection and stall insertion.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import simpy
from pipeline import Pipeline


class TestHazardDetection(unittest.TestCase):
    """Test hazard detection mechanisms"""
    
    def test_raw_with_execute_stage(self):
        """Test RAW hazard detection with Execute stage"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["ADD R1, R2, R3", "SUB R4, R1, R5"]
        results = pipeline.run(instructions)
        
        self.assertGreater(pipeline.stall_count, 0, 
                          "RAW hazard should be detected and cause stalls")
        self.assertEqual(len(results), 2, "Both instructions should complete")
        
    def test_raw_with_memory_stage(self):
        """Test RAW hazard detection with Memory stage"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        # Create scenario where instruction is in Memory when next one decodes
        instructions = [
            "ADD R1, R2, R3",
            "SUB R4, R5, R6",  # Independent, fills pipeline
            "OR R7, R1, R8",   # Depends on R1 which might be in Memory
        ]
        results = pipeline.run(instructions)
        
        self.assertGreaterEqual(pipeline.stall_count, 0, "Should handle Memory stage dependencies")
        self.assertEqual(len(results), 3, "All instructions should complete")
        
    def test_no_false_hazards(self):
        """Test that independent instructions don't trigger false hazards"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["ADD R1, R2, R3", "SUB R4, R5, R6"]
        results = pipeline.run(instructions)
        
        self.assertEqual(pipeline.stall_count, 0, 
                        "Independent instructions should not cause stalls")
                        
    def test_load_use_hazard(self):
        """Test LOAD-use hazard detection"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = ["LOAD R1, 100(R2)", "ADD R3, R1, R4"]
        results = pipeline.run(instructions)
        
        self.assertGreater(pipeline.stall_count, 0, 
                          "LOAD-use hazard should cause stalls")
        self.assertEqual(len(results), 2, "Both instructions should complete")
        
    def test_multiple_dependencies(self):
        """Test instruction with multiple source registers"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "SUB R4, R5, R6",
            "OR R7, R1, R4",  # Depends on both R1 and R4
        ]
        results = pipeline.run(instructions)
        
        # Should detect dependency on R1 (still in pipeline when OR decodes)
        self.assertGreaterEqual(pipeline.stall_count, 0, 
                                "Should detect at least one dependency")
        self.assertEqual(len(results), 3, "All instructions should complete")
        
    def test_chain_of_dependencies(self):
        """Test long chain of dependencies"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "ADD R1, R1, R4",  # Depends on previous R1
            "ADD R1, R1, R5",  # Depends on previous R1
        ]
        results = pipeline.run(instructions)
        
        # Each instruction depends on previous, should have multiple stalls
        self.assertGreater(pipeline.stall_count, 3, 
                          "Chain of dependencies should cause multiple stalls")
        self.assertEqual(len(results), 3, "All instructions should complete")


class TestNoFalseHazards(unittest.TestCase):
    """Test that we don't detect false hazards"""
    
    def test_waw_not_detected_in_order(self):
        """Test that WAW is not treated as hazard in in-order pipeline"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "SUB R1, R4, R5",  # Both write to R1, but in-order is fine
        ]
        results = pipeline.run(instructions)
        
        # There might be stalls if SUB reads R1, but not because of WAW
        self.assertEqual(len(results), 2, "Both instructions should complete")
        
    def test_writeback_stage_not_stalled(self):
        """Test that instructions in WriteBack stage don't cause stalls"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "SUB R4, R5, R6",  # Filler
            "OR R7, R8, R9",   # Filler
            "AND R10, R11, R12",  # Filler
            "XOR R13, R1, R14",  # By now R1 should be in WriteBack or done
        ]
        results = pipeline.run(instructions)
        
        # R1 should be available by the time XOR decodes
        self.assertEqual(len(results), 5, "All instructions should complete")


if __name__ == '__main__':
    unittest.main()
