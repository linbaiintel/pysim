"""
Test pipeline with interrupt checking.

Tests that the pipeline can check for and deliver interrupts during execution.
"""
import unittest
import simpy
from pipeline import Pipeline
from interrupt import InterruptController


class TestPipelineInterrupts(unittest.TestCase):
    """Test suite for pipeline interrupt checking"""
    
    def test_pipeline_has_interrupt_controller(self):
        """Test pipeline initializes with interrupt controller"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        self.assertIsNotNone(pipeline.interrupt_controller)
        self.assertIsNotNone(pipeline.trap_controller)
        self.assertIsNotNone(pipeline.csr_bank)
    
    def test_pipeline_checks_interrupts_no_pending(self):
        """Test pipeline runs normally when no interrupts pending"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        # Simple program
        instructions = [
            "ADDI R1, R0, 10",
            "ADDI R2, R0, 20",
            "ADD R3, R1, R2"
        ]
        
        completed = pipeline.run(instructions)
        
        # All instructions should complete
        self.assertEqual(len(completed), 3)
    
    def test_pipeline_with_interrupt_pending_and_disabled(self):
        """Test interrupt not delivered when globally disabled"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        # Set interrupt pending but don't enable
        pipeline.interrupt_controller.set_pending(InterruptController.INT_TIMER)
        # Global interrupts disabled by default
        
        instructions = [
            "ADDI R1, R0, 10",
            "ADDI R2, R0, 20"
        ]
        
        completed = pipeline.run(instructions)
        
        # Instructions complete normally
        self.assertEqual(len(completed), 2)
    
    def test_pipeline_with_csr_operations(self):
        """Test pipeline handles CSR operations"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        # Initialize a register
        pipeline.register_file.write('R1', 0x100)
        
        instructions = [
            "CSRRW R2, 0x300, R1",  # Write 0x100 to mstatus, read old value
        ]
        
        completed = pipeline.run(instructions)
        
        # Should complete
        self.assertEqual(len(completed), 1)
        
        # Check CSR was written
        mstatus = pipeline.csr_bank.read(0x300)
        self.assertEqual(mstatus, 0x100)
    
    def test_pipeline_mret_instruction(self):
        """Test MRET instruction in pipeline"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        # Setup: set mepc to return address
        pipeline.csr_bank.write(0x341, 0x2000)  # mepc
        
        # Set mstatus with MPIE=1
        mstatus = (1 << 7)  # MPIE=1
        pipeline.csr_bank.write(0x300, mstatus)
        
        instructions = [
            "MRET"
        ]
        
        completed = pipeline.run(instructions)
        
        # Should complete
        self.assertEqual(len(completed), 1)
        
        # Check mstatus updated (MIE should be restored)
        new_mstatus = pipeline.csr_bank.read(0x300)
        mie = (new_mstatus >> 3) & 0x1
        self.assertEqual(mie, 1)  # MIE restored from MPIE
    
    def test_pipeline_ecall_triggers_trap(self):
        """Test ECALL triggers trap in pipeline"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        # Set trap handler address
        pipeline.csr_bank.write(0x305, 0x80000000)  # mtvec
        
        instructions = [
            "ECALL"
        ]
        
        completed = pipeline.run(instructions)
        
        # Should complete (ECALL itself completes)
        self.assertEqual(len(completed), 1)
        
        # Check trap was recorded in CSRs
        mcause = pipeline.csr_bank.read(0x342)
        self.assertEqual(mcause, 11)  # ECALL from Machine mode
    
    def test_pipeline_interrupt_controller_accessible(self):
        """Test interrupt controller methods accessible from pipeline"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        ic = pipeline.interrupt_controller
        
        # Should be able to set pending
        ic.set_pending(ic.INT_TIMER)
        self.assertTrue(ic.is_pending(ic.INT_TIMER))
        
        # Should be able to enable
        ic.enable_interrupt(ic.INT_TIMER)
        self.assertTrue(ic.is_enabled(ic.INT_TIMER))
        
        # Should be able to enable globally
        ic.enable_global_interrupts()
        self.assertTrue(ic.is_globally_enabled())
    
    def test_pipeline_with_enabled_interrupt(self):
        """Test pipeline with interrupt enabled and pending"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        # Enable timer interrupt
        ic = pipeline.interrupt_controller
        ic.enable_global_interrupts()
        ic.enable_interrupt(ic.INT_TIMER)
        ic.set_pending(ic.INT_TIMER)
        
        # Set trap handler
        pipeline.csr_bank.write(0x305, 0x80000000)
        
        instructions = [
            "ADDI R1, R0, 10",
            "ADDI R2, R0, 20"
        ]
        
        # Run pipeline - interrupt should be checked before each fetch
        completed = pipeline.run(instructions)
        
        # Note: Interrupt will be delivered before first instruction
        # Pipeline will flush and redirect to handler
        # Original instructions will get bubbles inserted
        
        # Check that interrupt was handled
        mepc = pipeline.csr_bank.read(0x341)  # Should have saved PC
        mcause = pipeline.csr_bank.read(0x342)  # Should have interrupt cause
        
        # mcause should have MSB set for interrupt
        self.assertTrue(mcause & 0x80000000)


if __name__ == '__main__':
    unittest.main()
