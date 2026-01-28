"""Adapter to run RISC-V tests on simulator"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.riscv_test_utils import extract_test_patterns, convert_to_simulator_format


def run_extracted_tests(sim_tests, processor_class):
    """
    Run extracted tests on our simulator
    
    Args:
        sim_tests: List of test cases from convert_to_simulator_format
        processor_class: The RISCVProcessor class to instantiate
    """
    passed = 0
    failed = 0
    
    for test in sim_tests:
        processor = processor_class()
        
        # Setup initial state
        processor.initialize_registers(test['setup'])
        
        # Execute instruction
        processor.execute([test['instruction']], verbose=False)
        
        # Check result
        success = True
        for reg, expected_val in test['expected_result'].items():
            actual_val = processor.get_register(reg)
            if actual_val != expected_val:
                print(f"✗ Test #{test['test_num']} FAILED: {test['instruction']}")
                print(f"  Expected {reg}={expected_val:#010x}, got {actual_val:#010x}")
                failed += 1
                success = False
                break
        
        if success:
            passed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed} tests")
    print(f"{'='*60}")
    
    return passed, failed


if __name__ == "__main__":
    # Example: Extract tests from the ADD instruction test
    test_source = "3rd_party/riscv-tests/isa/rv64ui/add.S"
    
    if os.path.exists(test_source):
        print(f"Extracting test patterns from {test_source}...")
        tests = extract_test_patterns(test_source)
        print(f"Found {len(tests)} test patterns\n")
        
        # Show first few tests
        for test in tests[:5]:
            print(f"Test #{test['test_num']}: {test['instruction']} "
                  f"{test['src1']:#x} + {test['src2']:#x} = {test['expected']:#x}")
        
        print("\nConverting to simulator format...")
        sim_tests = convert_to_simulator_format(tests)
        
        # Show first converted test
        if sim_tests:
            print(f"\nExample converted test:")
            print(f"  Setup: {sim_tests[0]['setup']}")
            print(f"  Instruction: {sim_tests[0]['instruction']}")
            print(f"  Expected: {sim_tests[0]['expected_result']}")
        
        # Optionally run tests (uncomment when ready)
        # from riscv import RISCVProcessor
        # run_extracted_tests(sim_tests, RISCVProcessor)
    else:
        print(f"Test source file not found: {test_source}")
        print("Make sure riscv-tests is cloned in 3rd_party/")
