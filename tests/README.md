# Pipeline Simulator Test Suite

This directory contains all unit tests for the RISC-V 5-stage pipeline simulator.

## Test Structure

```
tests/
├── __init__.py              # Package initialization
├── run_tests.py             # Main test runner
├── test_all.py              # Consolidated comprehensive test suite
├── visualization.py         # Visualization and analysis utilities
└── README.md                # This file
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
# Run the complete test suite
python -m unittest tests.test_all

# Run specific test classes
python -m unittest tests.test_all.TestPipelineCorrectness
python -m unittest tests.test_all.TestHazardDetection
python -m unittest tests.test_all.TestImmediateInstructions
python -m unittest tests.test_all.TestShiftInstructions
python -m unittest tests.test_all.TestBranchInstructions
```

### Run Specific Test Cases
```bash
# Run a specific test class
python -m unittest tests.test_all.TestPipelineCorrectness

# Run a specific test method
python -m unittest tests.test_all.TestPipelineCorrectness.test_back_to_back_dependencies
python -m unittest tests.test_all.TestImmediateInstructions.test_addi_positive
python -m unittest tests.test_all.TestBranchInstructions.test_beq_equal
```

### Verbose Output
```bash
# More detailed output
python -m unittest discover tests -v

# Less detailed output
python -m unittest discover tests -q
```

## Test Modules

### test_all.py
Comprehensive test suite covering all aspects of the RISC-V pipeline simulator (59 tests total).

**Test Classes:**

#### Pipeline Functionality (10 tests)
- `TestPipelineCorrectness` - Basic pipeline operation and instruction ordering
- `TestInstructionParsing` - Instruction format parsing and validation

#### Hazard Detection (9 tests)
- `TestHazardDetection` - RAW hazard detection across pipeline stages
- `TestNoFalseHazards` - Verification of no spurious hazards

#### Edge Cases & Performance (11 tests)
- `TestEdgeCases` - Boundary conditions and special scenarios
- `TestInstructionTypes` - Different instruction type handling
- `TestPerformance` - CPI and stall tracking metrics

#### RISC-V Instructions (29 tests)
- `TestImmediateInstructions` - I-type arithmetic (ADDI, ANDI, ORI, XORI, SLTI, SLTIU)
- `TestShiftInstructions` - Shift operations (SLLI, SRLI, SRAI, SLL, SRL, SRA)
- `TestComparisonInstructions` - Comparison operations (SLT, SLTU)
- `TestUpperImmediateInstructions` - Upper immediate (LUI, AUIPC)
- `TestBranchInstructions` - Branch conditions (BEQ, BNE, BLT, BGE, BLTU, BGEU)
- `TestComplexPrograms` - Multi-instruction programs

**Key Test Scenarios:**
- Back-to-back dependencies and hazard handling
- Load-use hazards
- Independent instruction execution
- All RV32I immediate, shift, branch, and upper immediate instructions
- Bit manipulation and complex instruction sequences
- Pipeline stall counting and performance metrics

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

All 59 tests should pass with the following characteristics:

### Pipeline Correctness (10 tests)
- ✅ All instructions complete in program order
- ✅ Correct stall counts for various dependency scenarios
- ✅ Proper instruction parsing for all formats (R-type, I-type, Load/Store)

### Hazard Detection (9 tests)
- ✅ RAW hazards detected in Execute and Memory stages
- ✅ No false hazards for independent instructions
- ✅ Appropriate stall insertion for dependencies
- ✅ LOAD-use hazards handled correctly

### Edge Cases & Performance (11 tests)
- ✅ Single instruction execution works
- ✅ All instruction types supported (arithmetic, memory, logical)
- ✅ Dependency chains handled correctly
- ✅ Performance metrics tracked (CPI, stall count)

### RISC-V Instructions (29 tests)
- ✅ All I-type immediate instructions functional (ADDI, ANDI, ORI, XORI, SLTI, SLTIU)
- ✅ All shift instructions working (SLLI, SRLI, SRAI, SLL, SRL, SRA)
- ✅ Comparison instructions correct (SLT, SLTU with signed/unsigned)
- ✅ Upper immediate instructions (LUI, AUIPC)
- ✅ Branch condition evaluation (BEQ, BNE, BLT, BGE, BLTU, BGEU)
- ✅ Complex multi-instruction programs execute correctly

## Continuous Integration

To integrate with CI/CD:

```bash
# Run tests and exit with appropriate code
python tests/run_tests.py
echo $?  # 0 for success, 1 for failure
```

## Adding New Tests

To add new test cases:

1. Edit `tests/test_all.py`
2. Add a new test class or method within an existing class
3. Inherit from `unittest.TestCase`
4. Add test methods starting with `test_`
5. Use `self.assert*()` methods for assertions

Example:
```python
class TestMyNewFeature(unittest.TestCase):
    """Test new feature functionality"""
    
    def test_my_scenario(self):
        """Test specific scenario"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        results = pipeline.run(["ADD R1, R2, R3"])
        
        self.assertEqual(len(results), 1)
        self.assertEqual(pipeline.stall_count, 0)
```

**Best Practices:**
- Group related tests into classes
- Use descriptive test method names
- Add docstrings explaining what each test validates
- Test both success and failure cases
- Verify expected stall counts for hazard scenarios

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
