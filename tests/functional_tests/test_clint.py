"""Tests for CLINT (Core Local Interruptor) peripheral"""

import unittest
from clint import CLINT
from interrupt import InterruptController
from csr import CSRBank


class TestCLINT(unittest.TestCase):
    """Test CLINT timer and software interrupt functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.csr_bank = CSRBank()
        self.int_ctrl = InterruptController(self.csr_bank)
        self.clint = CLINT(self.int_ctrl)
    
    def test_clint_initialization(self):
        """Test CLINT initializes with correct defaults"""
        self.assertEqual(self.clint.mtime, 0)
        self.assertEqual(self.clint.mtimecmp, 0xFFFFFFFFFFFFFFFF)
        self.assertEqual(self.clint.msip, 0)
        self.assertTrue(self.clint.timer_enabled)
    
    def test_mtime_increments_on_tick(self):
        """Test mtime increments with tick()"""
        initial_mtime = self.clint.mtime
        self.clint.tick(1)
        self.assertEqual(self.clint.mtime, initial_mtime + 1)
        
        self.clint.tick(10)
        self.assertEqual(self.clint.mtime, initial_mtime + 11)
    
    def test_mtime_with_time_scale(self):
        """Test mtime respects time_scale"""
        clint = CLINT(self.int_ctrl, time_scale=1000)
        
        # Should not increment until 1000 cycles
        clint.tick(500)
        self.assertEqual(clint.mtime, 0)
        
        clint.tick(500)
        self.assertEqual(clint.mtime, 1)
        
        clint.tick(1000)
        self.assertEqual(clint.mtime, 2)
    
    def test_timer_interrupt_triggers(self):
        """Test timer interrupt triggers when mtime >= mtimecmp"""
        # Set mtimecmp to trigger at time 10
        self.clint.mtimecmp = 10
        
        # Advance to time 9 - no interrupt
        for _ in range(9):
            self.clint.tick()
        self.assertFalse(self.int_ctrl.is_pending(self.int_ctrl.INT_TIMER))
        
        # Advance to time 10 - interrupt triggers
        self.clint.tick()
        self.assertTrue(self.int_ctrl.is_pending(self.int_ctrl.INT_TIMER))
    
    def test_timer_interrupt_stays_pending(self):
        """Test timer interrupt stays pending after trigger"""
        self.clint.mtimecmp = 5
        
        # Trigger interrupt
        for _ in range(5):
            self.clint.tick()
        self.assertTrue(self.int_ctrl.is_pending(self.int_ctrl.INT_TIMER))
        
        # Continue ticking - interrupt stays pending
        self.clint.tick()
        self.clint.tick()
        self.assertTrue(self.int_ctrl.is_pending(self.int_ctrl.INT_TIMER))
    
    def test_write_mtimecmp_clears_interrupt(self):
        """Test writing mtimecmp clears pending timer interrupt"""
        self.clint.mtimecmp = 5
        for _ in range(5):
            self.clint.tick()
        self.assertTrue(self.int_ctrl.is_pending(self.int_ctrl.INT_TIMER))
        
        # Write mtimecmp - should clear interrupt
        self.clint.write_mtimecmp_64(100)
        self.assertFalse(self.int_ctrl.is_pending(self.int_ctrl.INT_TIMER))
    
    def test_read_write_mtime_register(self):
        """Test reading and writing mtime via memory-mapped registers"""
        # Write lower 32 bits
        self.clint.write_register(CLINT.MTIME_BASE, 0x12345678)
        self.assertEqual(self.clint.read_register(CLINT.MTIME_BASE), 0x12345678)
        
        # Write upper 32 bits
        self.clint.write_register(CLINT.MTIME_BASE + 4, 0xABCDEF00)
        self.assertEqual(self.clint.read_register(CLINT.MTIME_BASE + 4), 0xABCDEF00)
        
        # Verify full 64-bit value
        expected = (0xABCDEF00 << 32) | 0x12345678
        self.assertEqual(self.clint.read_mtime_64(), expected)
    
    def test_read_write_mtimecmp_register(self):
        """Test reading and writing mtimecmp via memory-mapped registers"""
        # Write lower 32 bits
        self.clint.write_register(CLINT.MTIMECMP_BASE, 0x11111111)
        self.assertEqual(self.clint.read_register(CLINT.MTIMECMP_BASE), 0x11111111)
        
        # Write upper 32 bits
        self.clint.write_register(CLINT.MTIMECMP_BASE + 4, 0x22222222)
        self.assertEqual(self.clint.read_register(CLINT.MTIMECMP_BASE + 4), 0x22222222)
        
        # Verify full 64-bit value
        expected = (0x22222222 << 32) | 0x11111111
        self.assertEqual(self.clint.read_mtimecmp_64(), expected)
    
    def test_msip_triggers_software_interrupt(self):
        """Test writing msip triggers software interrupt"""
        # Initially no interrupt
        self.assertFalse(self.int_ctrl.is_pending(self.int_ctrl.INT_SOFTWARE))
        
        # Write 1 to msip
        self.clint.write_register(CLINT.MSIP_BASE, 1)
        self.assertTrue(self.int_ctrl.is_pending(self.int_ctrl.INT_SOFTWARE))
        self.assertEqual(self.clint.msip, 1)
        
        # Write 0 to msip - clears interrupt
        self.clint.write_register(CLINT.MSIP_BASE, 0)
        self.assertFalse(self.int_ctrl.is_pending(self.int_ctrl.INT_SOFTWARE))
        self.assertEqual(self.clint.msip, 0)
    
    def test_trigger_software_interrupt_method(self):
        """Test trigger_software_interrupt() helper method"""
        self.clint.trigger_software_interrupt()
        self.assertEqual(self.clint.msip, 1)
        self.assertTrue(self.int_ctrl.is_pending(self.int_ctrl.INT_SOFTWARE))
    
    def test_clear_software_interrupt_method(self):
        """Test clear_software_interrupt() helper method"""
        self.clint.trigger_software_interrupt()
        self.clint.clear_software_interrupt()
        self.assertEqual(self.clint.msip, 0)
        self.assertFalse(self.int_ctrl.is_pending(self.int_ctrl.INT_SOFTWARE))
    
    def test_set_timer_interrupt_method(self):
        """Test set_timer_interrupt() helper method"""
        # Set interrupt 100 time units in the future
        self.clint.mtime = 50
        self.clint.set_timer_interrupt(100)
        self.assertEqual(self.clint.mtimecmp, 150)
        
        # Advance to trigger
        while self.clint.mtime < 150:
            self.clint.tick()
        self.assertTrue(self.int_ctrl.is_pending(self.int_ctrl.INT_TIMER))
    
    def test_clear_timer_interrupt_method(self):
        """Test clear_timer_interrupt() helper method"""
        self.clint.mtimecmp = 10
        for _ in range(10):
            self.clint.tick()
        self.assertTrue(self.int_ctrl.is_pending(self.int_ctrl.INT_TIMER))
        
        self.clint.clear_timer_interrupt()
        self.assertEqual(self.clint.mtimecmp, 0xFFFFFFFFFFFFFFFF)
        self.assertFalse(self.int_ctrl.is_pending(self.int_ctrl.INT_TIMER))
    
    def test_reset_clint(self):
        """Test reset() restores initial state"""
        # Modify state
        self.clint.mtime = 1000
        self.clint.mtimecmp = 500
        self.clint.msip = 1
        self.int_ctrl.set_pending(self.int_ctrl.INT_TIMER)
        
        # Reset
        self.clint.reset()
        
        # Verify reset state
        self.assertEqual(self.clint.mtime, 0)
        self.assertEqual(self.clint.mtimecmp, 0xFFFFFFFFFFFFFFFF)
        self.assertEqual(self.clint.msip, 0)
        self.assertFalse(self.int_ctrl.is_pending(self.int_ctrl.INT_TIMER))
        self.assertFalse(self.int_ctrl.is_pending(self.int_ctrl.INT_SOFTWARE))
    
    def test_get_status(self):
        """Test get_status() returns correct information"""
        self.clint.mtime = 100
        self.clint.mtimecmp = 150
        
        status = self.clint.get_status()
        self.assertEqual(status['mtime'], 100)
        self.assertEqual(status['mtimecmp'], 150)
        self.assertFalse(status['timer_pending'])
        self.assertEqual(status['cycles_until_interrupt'], 50)
    
    def test_freertos_tick_scenario(self):
        """Test typical FreeRTOS tick scenario"""
        # FreeRTOS typically uses 1ms ticks at 1MHz (1000 cycles per tick)
        clint = CLINT(self.int_ctrl, time_scale=1000)
        
        # Enable timer interrupt
        self.int_ctrl.enable_interrupt(self.int_ctrl.INT_TIMER)
        
        # Set up for 10ms (10 ticks)
        clint.set_timer_interrupt(10)
        
        # Simulate 10,000 cycles (10ms at 1MHz)
        for _ in range(10000):
            clint.tick(1)
        
        # Should have triggered interrupt
        self.assertTrue(self.int_ctrl.is_pending(self.int_ctrl.INT_TIMER))
        self.assertEqual(clint.mtime, 10)
    
    def test_periodic_timer_interrupts(self):
        """Test setting up periodic timer interrupts"""
        tick_interval = 100
        ticks_received = []
        
        for tick_num in range(5):
            # Set next interrupt
            self.clint.set_timer_interrupt(tick_interval)
            
            # Run until interrupt
            while not self.int_ctrl.is_pending(self.int_ctrl.INT_TIMER):
                self.clint.tick(1)
            
            ticks_received.append(self.clint.mtime)
            
            # Clear interrupt by setting new mtimecmp
            self.int_ctrl.clear_pending(self.int_ctrl.INT_TIMER)
        
        # Verify periodic ticks
        expected = [100, 200, 300, 400, 500]
        self.assertEqual(ticks_received, expected)
    
    def test_mtime_64bit_overflow(self):
        """Test mtime handles 64-bit overflow correctly"""
        # Set mtime near max
        self.clint.mtime = 0xFFFFFFFFFFFFFFFE
        
        # Tick should wrap around
        self.clint.tick(3)
        self.assertEqual(self.clint.mtime, 0x0000000000000001)
    
    def test_memory_mapped_register_bounds(self):
        """Test reading invalid addresses returns 0"""
        invalid_addr = 0x03000000
        self.assertEqual(self.clint.read_register(invalid_addr), 0)
    
    def test_concurrent_timer_and_software_interrupts(self):
        """Test both timer and software interrupts can be pending"""
        # Trigger both
        self.clint.mtimecmp = 10
        for _ in range(10):
            self.clint.tick()
        self.clint.trigger_software_interrupt()
        
        # Both should be pending
        self.assertTrue(self.int_ctrl.is_pending(self.int_ctrl.INT_TIMER))
        self.assertTrue(self.int_ctrl.is_pending(self.int_ctrl.INT_SOFTWARE))


if __name__ == '__main__':
    unittest.main()
