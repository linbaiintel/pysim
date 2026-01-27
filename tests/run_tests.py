#!/usr/bin/env python3
"""
Main test runner for the pipeline simulator test suite.
Run all tests or specific test modules.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def run_all_tests(verbosity=2):
    """Run all test suites"""
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_specific_tests(test_module, verbosity=2):
    """Run tests from a specific module"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_module)
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def print_usage():
    """Print usage information"""
    print("Pipeline Simulator Test Suite")
    print("=" * 70)
    print("\nUsage:")
    print("  python run_tests.py                 # Run all tests")
    print("  python run_tests.py correctness     # Run correctness tests")
    print("  python run_tests.py hazards         # Run hazard tests")
    print("  python run_tests.py edge_cases      # Run edge case tests")
    print("\nOr use unittest directly:")
    print("  python -m unittest discover tests   # Run all tests")
    print("  python -m unittest tests.test_correctness  # Specific module")
    print()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            print_usage()
            sys.exit(0)
        
        # Run specific test module
        test_map = {
            'correctness': 'tests.test_correctness',
            'hazards': 'tests.test_hazards',
            'edge_cases': 'tests.test_edge_cases',
        }
        
        test_name = sys.argv[1]
        if test_name in test_map:
            print(f"\nRunning {test_name} tests...\n")
            success = run_specific_tests(test_map[test_name])
        else:
            print(f"Unknown test module: {test_name}")
            print_usage()
            sys.exit(1)
    else:
        # Run all tests
        print("\nRunning all tests...\n")
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
