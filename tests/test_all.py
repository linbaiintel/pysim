#!/usr/bin/env python3
"""
Comprehensive test suite for RISC-V pipeline simulator.
Imports and runs all functional tests.
"""

import unittest
import sys
import os

# Add parent directory to path to import pipeline module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import functional tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'functional_tests')))
from test_pipeline import (TestPipelineCorrectness, TestInstructionParsing, 
                           TestHazardDetection, TestNoFalseHazards)
from test_edge_cases import TestEdgeCases
from test_instruction_types import TestInstructionTypes, TestPerformance
from test_immediate import TestImmediateInstructions
from test_shift import TestShiftInstructions
from test_comparison import TestComparisonInstructions
from test_upper_immediate import TestUpperImmediateInstructions
from test_branch import TestBranchInstructions
from test_complex_programs import TestComplexPrograms
from test_load_store import TestLoadStoreInstructions
from test_jump import TestJumpInstructions
from test_flush import TestPipelineFlush


if __name__ == '__main__':
    unittest.main()
