"""Run official RISC-V tests on our simulator using extracted patterns"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.riscv_test_utils import extract_test_patterns, convert_to_simulator_format
from tests.functional_tests.riscv_test_adapter import run_extracted_tests
from riscv import RISCVProcessor

def sign_extend_32bit(value):
    """Sign extend to 32-bit value"""
    value = value & 0xFFFFFFFF
    if value & 0x80000000:
        return value | 0xFFFFFFFF00000000
    return value

def run_test_file(test_name):
    """Run a specific test file"""
    test_source = f"3rd_party/riscv-tests/isa/rv64ui/{test_name}.S"
    
    if not os.path.exists(test_source):
        print(f"Test source not found: {test_source}")
        return None, None
    
    print(f"\n{'='*60}")
    print(f"Running {test_name.upper()} tests")
    print('='*60)
    
    # Extract and convert tests
    tests = extract_test_patterns(test_source)
    sim_tests = convert_to_simulator_format(tests)
    
    if not sim_tests:
        print(f"No compatible tests found in {test_name}")
        return 0, 0
    
    print(f"Found {len(sim_tests)} tests to run\n")
    
    # Run tests
    passed, failed = run_extracted_tests(sim_tests, RISCVProcessor)
    
    return passed, failed

def run_all_basic_tests():
    """Run all basic RV32I instruction tests"""
    test_files = [
        'add', 'addi', 'sub',
        'and', 'andi', 'or', 'ori', 'xor', 'xori',
        'sll', 'slli', 'srl', 'srli', 'sra', 'srai',
        'slt', 'slti', 'sltu', 'sltiu',
    ]
    
    total_passed = 0
    total_failed = 0
    results = {}
    
    print("\n" + "="*60)
    print("RUNNING OFFICIAL RISC-V TEST SUITE")
    print("="*60)
    
    for test in test_files:
        passed, failed = run_test_file(test)
        if passed is not None:
            results[test] = {'passed': passed, 'failed': failed}
            total_passed += passed
            total_failed += failed
    
    # Summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    for test, result in results.items():
        status = "✓ PASS" if result['failed'] == 0 else "✗ FAIL"
        print(f"{status} {test:10s}: {result['passed']:3d} passed, {result['failed']:3d} failed")
    
    print("\n" + "-"*60)
    total = total_passed + total_failed
    pass_rate = (total_passed / total * 100) if total > 0 else 0
    print(f"TOTAL: {total_passed}/{total} tests passed ({pass_rate:.1f}%)")
    print("="*60)
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        run_test_file(test_name)
    else:
        # Run all tests
        run_all_basic_tests()
