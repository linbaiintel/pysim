"""RISC-V test pattern utilities"""
import re


def extract_test_patterns(test_source_file):
    """
    Extract test patterns from riscv-test source files
    Returns list of test cases with expected results
    
    Skips tests inside #if __riscv_xlen == 64 blocks to only extract RV32-compatible tests.
    
    Args:
        test_source_file: Path to .S assembly test file
        
    Returns:
        List of dictionaries with test_num, instruction, expected, src1, src2
    """
    tests = []
    
    with open(test_source_file, 'r') as f:
        lines = f.readlines()
    
    # Track whether we're in a RV64-only block
    in_rv64_block = False
    rv64_block_depth = 0
    
    # Process line by line to track #if blocks
    for i, line in enumerate(lines):
        # Check for #if __riscv_xlen == 64
        if re.search(r'#\s*if\s+__riscv_xlen\s*==\s*64', line):
            in_rv64_block = True
            rv64_block_depth += 1
        # Check for nested #if (inside RV64 block)
        elif in_rv64_block and re.search(r'#\s*if', line):
            rv64_block_depth += 1
        # Check for #endif
        elif re.search(r'#\s*endif', line):
            if in_rv64_block:
                rv64_block_depth -= 1
                if rv64_block_depth == 0:
                    in_rv64_block = False
        
        # Skip extraction if we're in RV64-only block
        if in_rv64_block:
            continue
        
        # Find TEST_RR_OP patterns: TEST_RR_OP(test_num, instruction, expected, src1, src2)
        # Example: TEST_RR_OP( 2, add, 0x00000000, 0x00000000, 0x00000000 );
        # Example: TEST_RR_OP( 2, slt, 0, 0x0000000000000000, 0x0000000000000000 );
        rr_pattern = r'TEST_RR_OP\s*\(\s*(\d+)\s*,\s*(\w+)\s*,\s*(0x[0-9a-fA-F]+|\d+)\s*,\s*(0x[0-9a-fA-F]+|\d+)\s*,\s*(0x[0-9a-fA-F]+|\d+)\s*\)'
        
        # Find TEST_IMM_OP patterns: TEST_IMM_OP(test_num, instruction, expected, src1, immediate)
        # Example: TEST_IMM_OP( 2, addi, 0x00000000, 0x00000000, 0x000 );
        imm_pattern = r'TEST_IMM_OP\s*\(\s*(\d+)\s*,\s*(\w+)\s*,\s*(0x[0-9a-fA-F]+|\d+)\s*,\s*(0x[0-9a-fA-F]+|\d+)\s*,\s*(0x[0-9a-fA-F]+|\d+)\s*\)'
        
        # Find TEST_SRLI patterns: TEST_SRLI(test_num, value, shift_amount)
        # Example: TEST_SRLI( 2,  0xffffffff80000000, 0  );
        # This macro computes: expected = (value & 0xFFFFFFFF) >> shift_amount for RV32
        srli_pattern = r'TEST_SRLI\s*\(\s*(\d+)\s*,\s*(0x[0-9a-fA-F]+|\d+)\s*,\s*(0x[0-9a-fA-F]+|\d+)\s*\)'
        
        # Try TEST_RR_OP first
        match = re.search(rr_pattern, line)
        if match:
            test_num = int(match.group(1))
            instruction = match.group(2).upper()
            # Parse expected value (hex or decimal)
            expected_str = match.group(3)
            expected = int(expected_str, 16) if expected_str.startswith('0x') else int(expected_str)
            # Parse src1 (hex or decimal)
            src1_str = match.group(4)
            src1 = int(src1_str, 16) if src1_str.startswith('0x') else int(src1_str)
            # Parse src2 (hex or decimal)
            src2_str = match.group(5)
            src2 = int(src2_str, 16) if src2_str.startswith('0x') else int(src2_str)
            
            tests.append({
                'test_num': test_num,
                'instruction': instruction,
                'expected': expected,
                'src1': src1,
                'src2': src2,
                'type': 'RR'  # Register-Register operation
            })
            continue
        
        # Try TEST_IMM_OP
        match = re.search(imm_pattern, line)
        if match:
            test_num = int(match.group(1))
            instruction = match.group(2).upper()
            # Parse expected value (hex or decimal)
            expected_str = match.group(3)
            expected = int(expected_str, 16) if expected_str.startswith('0x') else int(expected_str)
            # Parse src1 (hex or decimal)
            src1_str = match.group(4)
            src1 = int(src1_str, 16) if src1_str.startswith('0x') else int(src1_str)
            # Parse immediate (hex or decimal)
            imm_str = match.group(5)
            immediate = int(imm_str, 16) if imm_str.startswith('0x') else int(imm_str)
            
            tests.append({
                'test_num': test_num,
                'instruction': instruction,
                'expected': expected,
                'src1': src1,
                'src2': immediate,  # Store immediate in src2 for uniform handling
                'type': 'IMM'  # Immediate operation
            })
            continue
        
        # Try TEST_SRLI (special macro for SRLI instruction)
        match = re.search(srli_pattern, line)
        if match:
            test_num = int(match.group(1))
            # Parse value (hex or decimal)
            value_str = match.group(2)
            value = int(value_str, 16) if value_str.startswith('0x') else int(value_str)
            # Parse shift amount (hex or decimal)
            shift_str = match.group(3)
            shift_amount = int(shift_str, 16) if shift_str.startswith('0x') else int(shift_str)
            
            # Compute expected result for RV32: (value & 0xFFFFFFFF) >> shift_amount
            # This matches the TEST_SRLI macro definition for RV32
            expected = ((value & 0xFFFFFFFF) >> shift_amount) & 0xFFFFFFFF
            
            tests.append({
                'test_num': test_num,
                'instruction': 'SRLI',
                'expected': expected,
                'src1': value,
                'src2': shift_amount,  # Store shift amount in src2
                'type': 'IMM'  # SRLI is an immediate operation
            })
    
    return tests


def convert_to_simulator_format(tests, instruction_map=None):
    """
    Convert test patterns to simulator instruction format
    
    Args:
        tests: List of test dictionaries from extract_test_patterns
        instruction_map: Optional mapping of RISC-V mnemonics to simulator mnemonics
        
    Returns:
        List of test dictionaries ready for simulator execution
    """
    if instruction_map is None:
        instruction_map = {
            # R-type instructions
            'ADD': 'ADD',
            'SUB': 'SUB',
            'AND': 'AND',
            'OR': 'OR',
            'XOR': 'XOR',
            'SLL': 'SLL',
            'SRL': 'SRL',
            'SRA': 'SRA',
            'SLT': 'SLT',
            'SLTU': 'SLTU',
            # I-type instructions
            'ADDI': 'ADDI',
            'ANDI': 'ANDI',
            'ORI': 'ORI',
            'XORI': 'XORI',
            'SLLI': 'SLLI',
            'SRLI': 'SRLI',
            'SRAI': 'SRAI',
            'SLTI': 'SLTI',
            'SLTIU': 'SLTIU',
        }
    
    sim_tests = []
    
    for test in tests:
        instr = test['instruction']
        test_type = test.get('type', 'RR')
        
        if instr not in instruction_map:
            continue
        
        # For immediate operations, format as: INSTR R3, R1, immediate
        # For register operations, format as: INSTR R3, R1, R2
        if test_type == 'IMM':
            # Immediate value is stored in src2
            immediate = test['src2']
            # Sign-extend 12-bit immediate to 32-bit for proper handling
            if immediate & 0x800:  # Check sign bit (bit 11)
                immediate |= 0xFFFFF000  # Sign extend
            immediate &= 0xFFFFFFFF  # Ensure 32-bit
            
            sim_test = {
                'test_num': test['test_num'],
                'setup': {
                    'R1': test['src1'],  # Map to R1
                },
                'instruction': f"{instruction_map[instr]} R3, R1, {immediate}",
                'expected_result': {
                    'R3': test['expected'] & 0xFFFFFFFF  # 32-bit result
                }
            }
        else:
            # Register-register operation
            sim_test = {
                'test_num': test['test_num'],
                'setup': {
                    'R1': test['src1'],  # Map to R1
                    'R2': test['src2'],  # Map to R2
                },
                'instruction': f"{instruction_map[instr]} R3, R1, R2",
                'expected_result': {
                    'R3': test['expected'] & 0xFFFFFFFF  # 32-bit result
                }
            }
        
        sim_tests.append(sim_test)
    
    return sim_tests
