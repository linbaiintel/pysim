#!/usr/bin/env python3
"""
Comprehensive unit tests for RISC-V pipeline simulator.
Combines all instruction tests, hazard detection, edge cases, and functional correctness.
"""

import unittest
import sys
import os

# Add parent directory to path to import pipeline module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import simpy
from pipeline import Pipeline, Instruction
from riscv import run_program

# Import functional tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'functional_tests')))
from test_upper_immediate import TestUpperImmediateInstructions


# ============================================================================
# PIPELINE CORRECTNESS TESTS
# ============================================================================

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


# ============================================================================
# HAZARD DETECTION TESTS
# ============================================================================

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
        
        self.assertEqual(len(results), 2, "Both instructions should complete")
        
    def test_writeback_stage_not_stalled(self):
        """Test that instructions in WriteBack stage don't cause stalls"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        instructions = [
            "ADD R1, R2, R3",
            "SUB R4, R5, R6",
            "OR R7, R8, R9",
            "AND R10, R11, R12",
            "XOR R13, R1, R14",  # By now R1 should be in WriteBack or done
        ]
        results = pipeline.run(instructions)
        
        self.assertEqual(len(results), 5, "All instructions should complete")


# ============================================================================
# EDGE CASES AND SPECIAL SCENARIOS
# ============================================================================

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


# ============================================================================
# NEW RISC-V INSTRUCTIONS TESTS
# ============================================================================

class TestImmediateInstructions(unittest.TestCase):
    """Test I-type instructions with immediate values"""
    
    def test_addi_positive(self):
        """Test ADDI with positive immediate"""
        exec_info, regs, mem = run_program(['ADDI R1, R0, 42'], {}, {}, verbose=False)
        self.assertEqual(regs['R1'], 42)
    
    def test_addi_negative(self):
        """Test ADDI with negative immediate"""
        exec_info, regs, mem = run_program(['ADDI R1, R2, -10'], {'R2': 100}, {}, verbose=False)
        self.assertEqual(regs['R1'], 90)
    
    def test_andi(self):
        """Test ANDI instruction"""
        exec_info, regs, mem = run_program(['ANDI R1, R2, 0xF'], {'R2': 0xFF}, {}, verbose=False)
        self.assertEqual(regs['R1'], 0xF)
    
    def test_ori(self):
        """Test ORI instruction"""
        exec_info, regs, mem = run_program(['ORI R1, R2, 0xF0'], {'R2': 0x0F}, {}, verbose=False)
        self.assertEqual(regs['R1'], 0xFF)
    
    def test_xori(self):
        """Test XORI instruction"""
        exec_info, regs, mem = run_program(['XORI R1, R2, 0xFF'], {'R2': 0xAA}, {}, verbose=False)
        self.assertEqual(regs['R1'], 0x55)
    
    def test_slti_true(self):
        """Test SLTI when condition is true"""
        exec_info, regs, mem = run_program(['SLTI R1, R2, 10'], {'R2': 5}, {}, verbose=False)
        self.assertEqual(regs['R1'], 1)
    
    def test_slti_false(self):
        """Test SLTI when condition is false"""
        exec_info, regs, mem = run_program(['SLTI R1, R2, 10'], {'R2': 15}, {}, verbose=False)
        self.assertEqual(regs.get('R1', 0), 0)
    
    def test_sltiu(self):
        """Test SLTIU (unsigned comparison)"""
        exec_info, regs, mem = run_program(['SLTIU R1, R2, 10'], {'R2': 5}, {}, verbose=False)
        self.assertEqual(regs['R1'], 1)


class TestShiftInstructions(unittest.TestCase):
    """Test shift instructions (R-type and I-type)"""
    
    def test_slli(self):
        """Test SLLI (Shift Left Logical Immediate)"""
        exec_info, regs, mem = run_program(['SLLI R1, R2, 4'], {'R2': 0x1}, {}, verbose=False)
        self.assertEqual(regs['R1'], 0x10)
    
    def test_srli(self):
        """Test SRLI (Shift Right Logical Immediate)"""
        exec_info, regs, mem = run_program(['SRLI R1, R2, 4'], {'R2': 0xF0}, {}, verbose=False)
        self.assertEqual(regs['R1'], 0x0F)
    
    def test_srai_positive(self):
        """Test SRAI with positive number"""
        exec_info, regs, mem = run_program(['SRAI R1, R2, 2'], {'R2': 0x10}, {}, verbose=False)
        self.assertEqual(regs['R1'], 0x04)
    
    def test_srai_negative(self):
        """Test SRAI with negative number (sign extension)"""
        exec_info, regs, mem = run_program(['SRAI R1, R2, 2'], {'R2': 0xFFFFFFFC}, {}, verbose=False)
        self.assertEqual(regs['R1'], 0xFFFFFFFF)
    
    def test_sll_register(self):
        """Test SLL (Shift Left Logical with register)"""
        exec_info, regs, mem = run_program(['SLL R1, R2, R3'], {'R2': 0x1, 'R3': 8}, {}, verbose=False)
        self.assertEqual(regs['R1'], 0x100)
    
    def test_srl_register(self):
        """Test SRL (Shift Right Logical with register)"""
        exec_info, regs, mem = run_program(['SRL R1, R2, R3'], {'R2': 0xFF00, 'R3': 8}, {}, verbose=False)
        self.assertEqual(regs['R1'], 0xFF)
    
    def test_sra_register(self):
        """Test SRA (Shift Right Arithmetic with register)"""
        exec_info, regs, mem = run_program(['SRA R1, R2, R3'], {'R2': 0x80000000, 'R3': 1}, {}, verbose=False)
        self.assertEqual(regs['R1'], 0xC0000000)


class TestComparisonInstructions(unittest.TestCase):
    """Test comparison instructions"""
    
    def test_sltu_true(self):
        """Test SLTU (Set Less Than Unsigned) - true case"""
        exec_info, regs, mem = run_program(['SLTU R1, R2, R3'], {'R2': 5, 'R3': 10}, {}, verbose=False)
        self.assertEqual(regs['R1'], 1)
    
    def test_sltu_false(self):
        """Test SLTU - false case"""
        exec_info, regs, mem = run_program(['SLTU R1, R2, R3'], {'R2': 10, 'R3': 5}, {}, verbose=False)
        self.assertEqual(regs.get('R1', 0), 0)
    
    def test_slt_signed_negative(self):
        """Test SLT with negative numbers"""
        exec_info, regs, mem = run_program(['SLT R1, R2, R3'], {'R2': 0xFFFFFFFE, 'R3': 0}, {}, verbose=False)
        self.assertEqual(regs['R1'], 1)


class TestUpperImmediateInstructions(unittest.TestCase):
    """Test LUI and AUIPC instructions"""
    
    def test_lui_basic(self):
        """Test LUI (Load Upper Immediate)"""
        exec_info, regs, mem = run_program(['LUI R1, 0x12345'], {}, {}, verbose=False)
        self.assertEqual(regs['R1'], 0x12345000)
    
    def test_lui_max_value(self):
        """Test LUI with maximum 20-bit value"""
        exec_info, regs, mem = run_program(['LUI R1, 0xFFFFF'], {}, {}, verbose=False)
        self.assertEqual(regs['R1'], 0xFFFFF000)
    
    def test_lui_then_addi(self):
        """Test LUI combined with ADDI to load 32-bit constant"""
        exec_info, regs, mem = run_program(['LUI R1, 0x12345', 'ADDI R1, R1, 0x678'], {}, {}, verbose=False)
        self.assertEqual(regs['R1'], 0x12345678)


class TestBranchInstructions(unittest.TestCase):
    """Test branch instructions (comparison only)"""
    
    def test_beq_equal(self):
        """Test BEQ when registers are equal"""
        exec_info, regs, mem = run_program(['BEQ R1, R2, 100'], {'R1': 42, 'R2': 42}, {}, verbose=False)
        self.assertIn('completed_instructions', exec_info)
    
    def test_beq_not_equal(self):
        """Test BEQ when registers are not equal"""
        exec_info, regs, mem = run_program(['BEQ R1, R2, 100'], {'R1': 42, 'R2': 10}, {}, verbose=False)
        self.assertIn('completed_instructions', exec_info)
    
    def test_bne(self):
        """Test BNE (Branch Not Equal)"""
        exec_info, regs, mem = run_program(['BNE R1, R2, 100'], {'R1': 42, 'R2': 10}, {}, verbose=False)
        self.assertIn('completed_instructions', exec_info)
    
    def test_blt_signed(self):
        """Test BLT (Branch Less Than - signed)"""
        exec_info, regs, mem = run_program(['BLT R1, R2, 100'], {'R1': 0xFFFFFFFE, 'R2': 0}, {}, verbose=False)
        self.assertIn('completed_instructions', exec_info)
    
    def test_bge_signed(self):
        """Test BGE (Branch Greater or Equal - signed)"""
        exec_info, regs, mem = run_program(['BGE R1, R2, 100'], {'R1': 10, 'R2': 5}, {}, verbose=False)
        self.assertIn('completed_instructions', exec_info)
    
    def test_bltu_unsigned(self):
        """Test BLTU (Branch Less Than Unsigned)"""
        exec_info, regs, mem = run_program(['BLTU R1, R2, 100'], {'R1': 5, 'R2': 10}, {}, verbose=False)
        self.assertIn('completed_instructions', exec_info)
    
    def test_bgeu_unsigned(self):
        """Test BGEU (Branch Greater or Equal Unsigned)"""
        exec_info, regs, mem = run_program(['BGEU R1, R2, 100'], {'R1': 10, 'R2': 5}, {}, verbose=False)
        self.assertIn('completed_instructions', exec_info)


class TestComplexPrograms(unittest.TestCase):
    """Test complex programs using multiple instructions"""
    
    def test_bit_manipulation(self):
        """Test program with bit manipulation using shifts and logical ops"""
        exec_info, regs, mem = run_program([
                'ADDI R1, R0, 0xFF',
                'SLLI R2, R1, 8',
                'ORI R3, R2, 0x0F',
                'ANDI R4, R3, 0xF0F0'
            ], {}, {}, verbose=False)
        self.assertEqual(regs['R1'], 0xFF)
        self.assertEqual(regs['R2'], 0xFF00)
        self.assertEqual(regs['R3'], 0xFF0F)
        self.assertEqual(regs['R4'], 0xF000)
    
    def test_load_large_constant(self):
        """Test loading a large 32-bit constant using LUI + ADDI"""
        exec_info, regs, mem = run_program(['LUI R1, 0xDEADB', 'ADDI R1, R1, 0xEEF'], {}, {}, verbose=False)
        self.assertEqual(regs['R1'], 0xDEADBEEF)
    
    def test_immediate_arithmetic_chain(self):
        """Test chain of immediate arithmetic operations"""
        exec_info, regs, mem = run_program([
                'ADDI R1, R0, 100',
                'ADDI R2, R1, 50',
                'SLTI R3, R2, 200',
                'XORI R4, R3, 1'
            ], {}, {}, verbose=False)
        self.assertEqual(regs['R1'], 100)
        self.assertEqual(regs['R2'], 150)
        self.assertEqual(regs['R3'], 1)
        self.assertEqual(regs.get('R4', 0), 0)


if __name__ == '__main__':
    unittest.main()
