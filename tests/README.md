# Pipeline Simulator Test Suite

This directory contains all unit tests for the RISC-V 5-stage pipeline simulator.

## Test Structure

```
tests/
├── __init__.py              # Package initialization
├── run_tests.py             # Main test runner
├── test_correctness.py      # Functional correctness tests
├── test_hazards.py          # Hazard detection tests
├── test_edge_cases.py       # Edge cases and special scenarios
└── visualization.py         # Visualization and analysis utilities
```

## Running Tests

### Run All Tests
```bash
# Using the test runner
python tests/run_tests.py

# Using unittest directly
python -m unittest discover tests

# From the tests directory
cd tests && python run_tests.py
```

### Run Specific Test Modules
```bash
# Using the test runner
python tests/run_tests.py correctness
python tests/run_tests.py hazards
python tests/run_tests.py edge_cases

# Using unittest directly
python -m unittest tests.test_correctness
python -m unittest tests.test_hazards
python -m unittest tests.test_edge_cases
```

### Run Specific Test Cases
```bash
# Run a specific test class
python -m unittest tests.test_correctness.TestPipelineCorrectness

# Run a specific test method
python -m unittest tests.test_correctness.TestPipelineCorrectness.test_back_to_back_dependencies
```

### Verbose Output
```bash
# More detailed output
python -m unittest discover tests -v

# Less detailed output
python -m unittest discover tests -q
```

## Test Modules

### test_correctness.py
Tests functional correctness of the pipeline:
- All instructions complete
- Instructions complete in program order
- Correct stall counts for various scenarios
- Instruction parsing

**Key Test Cases:**
- `test_back_to_back_dependencies()` - Sequential RAW dependencies
- `test_independent_instructions()` - No hazards
- `test_load_use_hazard()` - LOAD followed by use
- `test_mixed_dependencies()` - Multiple dependency patterns
- `test_instruction_order_preserved()` - In-order completion

### test_hazards.py
Tests hazard detection mechanisms:
- RAW hazard detection in Execute and Memory stages
- No false hazards for independent instructions
- LOAD-use hazards
- Multiple source dependencies
- Long dependency chains

**Key Test Cases:**
- `test_raw_with_execute_stage()` - Detect hazard when producer in Execute
- `test_no_false_hazards()` - Independent instructions don't stall
- `test_load_use_hazard()` - Special case for LOAD instructions
- `test_chain_of_dependencies()` - Multiple dependent instructions

### test_edge_cases.py
Tests edge cases and special scenarios:
- Single instruction
- Multiple instructions writing same register
- STORE instructions (no destination register)
- LOAD/STORE sequences
- Different instruction types
- Performance metrics

**Key Test Cases:**
- `test_single_instruction()` - Minimal test case
- `test_three_way_dependency_chain()` - Long chains
- `test_store_instruction()` - Special instruction handling
- `test_cpi_for_independent_instructions()` - Performance verification

## Visualization Tools

### visualization.py
Provides utilities for analyzing pipeline execution:

```python
from tests.visualization import visualize_pipeline_execution

# Visualize a specific instruction sequence
metrics = visualize_pipeline_execution([
    "ADD R1, R2, R3",
    "SUB R4, R1, R5"
])

# Compare multiple sequences
from tests.visualization import compare_instruction_sequences
sequences = [
    ("Test 1", ["ADD R1, R2, R3", "SUB R4, R5, R6"]),
    ("Test 2", ["ADD R1, R2, R3", "SUB R4, R1, R5"]),
]
results = compare_instruction_sequences(sequences)
```

**Run standalone:**
```bash
python tests/visualization.py
```

## Expected Test Results

All tests should pass with the following characteristics:

### Correctness Tests
- ✅ All instructions complete
- ✅ Correct number of stalls
- ✅ In-order completion
- ✅ Proper instruction parsing

### Hazard Tests
- ✅ RAW hazards detected
- ✅ No false hazards
- ✅ Appropriate stall insertion
- ✅ LOAD-use hazards handled

### Edge Case Tests
- ✅ Single instruction works
- ✅ All instruction types supported
- ✅ Dependency chains handled
- ✅ Performance metrics reasonable

## Continuous Integration

To integrate with CI/CD:

```bash
# Run tests and exit with appropriate code
python tests/run_tests.py
echo $?  # 0 for success, 1 for failure
```

## Adding New Tests

To add new test cases:

1. Create or edit a test file in the `tests/` directory
2. Inherit from `unittest.TestCase`
3. Add test methods starting with `test_`
4. Use `self.assert*()` methods for assertions

Example:
```python
import unittest
from pipeline import Pipeline
import simpy

class TestMyFeature(unittest.TestCase):
    def test_my_scenario(self):
        env = simpy.Environment()
        pipeline = Pipeline(env)
        results = pipeline.run(["ADD R1, R2, R3"])
        
        self.assertEqual(len(results), 1)
```

## Troubleshooting

### Import Errors
Make sure you're running from the project root:
```bash
cd /home/linbai/pysim
python -m unittest discover tests
```

### Module Not Found
Ensure `__init__.py` exists in the tests directory:
```bash
touch tests/__init__.py
```

### Test Failures
Run with verbose output to see details:
```bash
python -m unittest discover tests -v
```

## Coverage Analysis

To check test coverage (requires `coverage` package):
```bash
pip install coverage
coverage run -m unittest discover tests
coverage report
coverage html  # Generate HTML report
```

## Performance Benchmarking

Use visualization tools to benchmark:
```bash
python tests/visualization.py > benchmark_results.txt
```
