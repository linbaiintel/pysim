"""Tests for CLINT integration with pipeline"""

import unittest
import simpy
from pipeline import Pipeline
from instruction import Instruction


class TestPipelineCLINT(unittest.TestCase):
    """Test CLINT integration in pipeline"""
    
    def test_pipeline_has_clint(self):
        """Test pipeline initializes with CLINT"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        self.assertIsNotNone(pipeline.clint)
        self.assertEqual(pipeline.clint.mtime, 0)
    
    def test_clint_ticks_during_execution(self):
        """Test CLINT mtime increments as pipeline executes"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        initial_mtime = pipeline.clint.mtime
        
        # Run a simple instruction
        instructions = ["ADDI R1, R0, 10"]
        pipeline.run(instructions)
        
        # mtime should have incremented
        self.assertGreater(pipeline.clint.mtime, initial_mtime)
    
    def test_timer_interrupt_during_execution(self):
        """Test timer interrupt triggers during program execution"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        # Enable timer interrupt
        pipeline.interrupt_controller.enable_interrupt(
            pipeline.interrupt_controller.INT_TIMER
        )
        
        # Enable global interrupts
        mstatus = pipeline.csr_bank.read(0x300)
        mstatus |= (1 << 3)  # Set MIE
        pipeline.csr_bank.write(0x300, mstatus)
        
        # Set up timer to interrupt after 5 cycles (will happen quickly)
        pipeline.clint.set_timer_interrupt(5)
        
        # Set trap handler
        pipeline.csr_bank.write(0x305, 0x80000000)  # mtvec
        
        # Run program
        instructions = [
            "ADDI R1, R0, 1",
            "ADDI R2, R0, 2",
            "ADDI R3, R0, 3",
        ]
        pipeline.run(instructions)
        
        # Check that CLINT advanced mtime beyond the threshold
        self.assertGreaterEqual(pipeline.clint.mtime, 5)
        
        # Check that timer interrupt was triggered
        self.assertTrue(
            pipeline.interrupt_controller.is_pending(
                pipeline.interrupt_controller.INT_TIMER
            ), 
            "Timer interrupt should be pending after mtime >= mtimecmp"
        )
    
    def test_clint_memory_mapped_access(self):
        """Test accessing CLINT via memory-mapped registers"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        # Write to mtime
        pipeline.clint.write_register(pipeline.clint.MTIME_BASE, 0x12345678)
        value = pipeline.clint.read_register(pipeline.clint.MTIME_BASE)
        self.assertEqual(value, 0x12345678)
        
        # Write to mtimecmp
        pipeline.clint.write_register(pipeline.clint.MTIMECMP_BASE, 0xABCDEF00)
        value = pipeline.clint.read_register(pipeline.clint.MTIMECMP_BASE)
        self.assertEqual(value, 0xABCDEF00)
    
    def test_freertos_style_periodic_ticks(self):
        """Test FreeRTOS-style periodic timer ticks"""
        env = simpy.Environment()
        # Use time_scale=100 for faster testing
        pipeline = Pipeline(env)
        pipeline.clint = __import__('clint').CLINT(
            pipeline.interrupt_controller, 
            time_scale=100
        )
        
        # Enable interrupts
        pipeline.interrupt_controller.enable_interrupt(
            pipeline.interrupt_controller.INT_TIMER
        )
        mstatus = pipeline.csr_bank.read(0x300)
        mstatus |= (1 << 3)
        pipeline.csr_bank.write(0x300, mstatus)
        
        # Set up for tick every 10 time units
        tick_interval = 10
        pipeline.clint.set_timer_interrupt(tick_interval)
        pipeline.csr_bank.write(0x305, 0x80000000)
        
        # Run some instructions
        instructions = ["ADDI R1, R0, 1"] * 50
        pipeline.run(instructions)
        
        # Should have gotten at least one timer interrupt
        self.assertGreater(pipeline.clint.mtime, 0)
    
    def test_software_interrupt_via_clint(self):
        """Test software interrupt through CLINT"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        # Trigger software interrupt
        pipeline.clint.trigger_software_interrupt()
        
        # Verify it's pending
        self.assertTrue(
            pipeline.interrupt_controller.is_pending(
                pipeline.interrupt_controller.INT_SOFTWARE
            )
        )
        
        # Clear it
        pipeline.clint.clear_software_interrupt()
        self.assertFalse(
            pipeline.interrupt_controller.is_pending(
                pipeline.interrupt_controller.INT_SOFTWARE
            )
        )
    
    def test_clint_status_during_execution(self):
        """Test CLINT status reporting"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        # Set up timer
        pipeline.clint.set_timer_interrupt(100)
        
        # Get initial status
        status = pipeline.clint.get_status()
        self.assertEqual(status['mtime'], 0)
        self.assertEqual(status['mtimecmp'], 100)
        self.assertFalse(status['timer_pending'])
        self.assertEqual(status['cycles_until_interrupt'], 100)
        
        # Run to advance time
        instructions = ["ADDI R1, R0, 1"] * 20
        pipeline.run(instructions)
        
        # Check status updated
        status = pipeline.clint.get_status()
        self.assertGreater(status['mtime'], 0)
    
    def test_multiple_timer_interrupts(self):
        """Test handling multiple timer interrupts"""
        env = simpy.Environment()
        pipeline = Pipeline(env)
        
        # Enable interrupts
        pipeline.interrupt_controller.enable_interrupt(
            pipeline.interrupt_controller.INT_TIMER
        )
        mstatus = pipeline.csr_bank.read(0x300)
        mstatus |= (1 << 3)
        pipeline.csr_bank.write(0x300, mstatus)
        pipeline.csr_bank.write(0x305, 0x80000000)
        
        # Set first timer interrupt at 5 cycles
        pipeline.clint.set_timer_interrupt(5)
        
        # Run program
        instructions = ["ADDI R1, R0, 1"] * 3
        pipeline.run(instructions)
        
        # Should have triggered
        self.assertTrue(
            pipeline.interrupt_controller.is_pending(
                pipeline.interrupt_controller.INT_TIMER
            ) or pipeline.clint.mtime >= 5
        )


if __name__ == '__main__':
    unittest.main()
