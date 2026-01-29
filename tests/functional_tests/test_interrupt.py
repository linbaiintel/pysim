"""
Test Interrupt Enable/Pending Logic.

Tests the InterruptController class for interrupt masking, priority,
edge/level triggering, and deliverability.
"""
import unittest
from interrupt import InterruptController, InterruptSource
from csr import CSRBank


class TestInterruptController(unittest.TestCase):
    """Test suite for interrupt enable/pending logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.csr = CSRBank()
        self.ic = InterruptController(self.csr)
    
    # Basic pending/enable tests
    def test_set_pending_software(self):
        """Test setting software interrupt pending"""
        self.ic.set_pending(InterruptController.INT_SOFTWARE)
        
        self.assertTrue(self.ic.is_pending(InterruptController.INT_SOFTWARE))
        
        # Check mip bit
        mip = self.csr.read(0x344)
        self.assertTrue(mip & (1 << 3))
    
    def test_set_pending_timer(self):
        """Test setting timer interrupt pending"""
        self.ic.set_pending(InterruptController.INT_TIMER)
        
        self.assertTrue(self.ic.is_pending(InterruptController.INT_TIMER))
        
        mip = self.csr.read(0x344)
        self.assertTrue(mip & (1 << 7))
    
    def test_set_pending_external(self):
        """Test setting external interrupt pending"""
        self.ic.set_pending(InterruptController.INT_EXTERNAL)
        
        self.assertTrue(self.ic.is_pending(InterruptController.INT_EXTERNAL))
        
        mip = self.csr.read(0x344)
        self.assertTrue(mip & (1 << 11))
    
    def test_clear_pending(self):
        """Test clearing interrupt pending bit"""
        self.ic.set_pending(InterruptController.INT_TIMER)
        self.assertTrue(self.ic.is_pending(InterruptController.INT_TIMER))
        
        self.ic.clear_pending(InterruptController.INT_TIMER)
        self.assertFalse(self.ic.is_pending(InterruptController.INT_TIMER))
    
    def test_enable_interrupt(self):
        """Test enabling specific interrupt"""
        self.ic.enable_interrupt(InterruptController.INT_SOFTWARE)
        
        self.assertTrue(self.ic.is_enabled(InterruptController.INT_SOFTWARE))
        
        # Check mie bit
        mie = self.csr.read(0x304)
        self.assertTrue(mie & (1 << 3))
    
    def test_disable_interrupt(self):
        """Test disabling specific interrupt"""
        self.ic.enable_interrupt(InterruptController.INT_TIMER)
        self.ic.disable_interrupt(InterruptController.INT_TIMER)
        
        self.assertFalse(self.ic.is_enabled(InterruptController.INT_TIMER))
    
    def test_global_enable(self):
        """Test global interrupt enable"""
        self.ic.enable_global_interrupts()
        
        self.assertTrue(self.ic.is_globally_enabled())
        
        mstatus = self.csr.read(0x300)
        self.assertTrue(mstatus & (1 << 3))
    
    def test_global_disable(self):
        """Test global interrupt disable"""
        self.ic.enable_global_interrupts()
        self.ic.disable_global_interrupts()
        
        self.assertFalse(self.ic.is_globally_enabled())
    
    # Pending/enabled list tests
    def test_get_pending_interrupts(self):
        """Test getting list of pending interrupts"""
        self.ic.set_pending(InterruptController.INT_SOFTWARE)
        self.ic.set_pending(InterruptController.INT_EXTERNAL)
        
        pending = self.ic.get_pending_interrupts()
        
        self.assertIn(3, pending)
        self.assertIn(11, pending)
        self.assertNotIn(7, pending)
    
    def test_get_enabled_interrupts(self):
        """Test getting list of enabled interrupts"""
        self.ic.enable_interrupt(InterruptController.INT_TIMER)
        self.ic.enable_interrupt(InterruptController.INT_EXTERNAL)
        
        enabled = self.ic.get_enabled_interrupts()
        
        self.assertIn(7, enabled)
        self.assertIn(11, enabled)
        self.assertNotIn(3, enabled)
    
    def test_get_deliverable_interrupts_none_when_globally_disabled(self):
        """Test no interrupts deliverable when globally disabled"""
        self.ic.set_pending(InterruptController.INT_TIMER)
        self.ic.enable_interrupt(InterruptController.INT_TIMER)
        # Global interrupts disabled by default
        
        deliverable = self.ic.get_deliverable_interrupts()
        
        self.assertEqual(len(deliverable), 0)
    
    def test_get_deliverable_interrupts_when_enabled(self):
        """Test deliverable interrupts when all conditions met"""
        # Enable globally
        self.ic.enable_global_interrupts()
        
        # Enable specific interrupts
        self.ic.enable_interrupt(InterruptController.INT_TIMER)
        self.ic.enable_interrupt(InterruptController.INT_SOFTWARE)
        
        # Set pending
        self.ic.set_pending(InterruptController.INT_TIMER)
        self.ic.set_pending(InterruptController.INT_EXTERNAL)  # Not enabled
        
        deliverable = self.ic.get_deliverable_interrupts()
        
        # Only timer should be deliverable (pending AND enabled)
        self.assertIn(7, deliverable)
        self.assertNotIn(11, deliverable)  # Not enabled
        self.assertNotIn(3, deliverable)   # Not pending
    
    def test_get_deliverable_interrupts_masks_correctly(self):
        """Test deliverable interrupts mask pending with enabled"""
        self.ic.enable_global_interrupts()
        
        # Set all pending
        self.ic.set_pending(InterruptController.INT_SOFTWARE)
        self.ic.set_pending(InterruptController.INT_TIMER)
        self.ic.set_pending(InterruptController.INT_EXTERNAL)
        
        # Enable only timer
        self.ic.enable_interrupt(InterruptController.INT_TIMER)
        
        deliverable = self.ic.get_deliverable_interrupts()
        
        self.assertEqual(deliverable, [7])
    
    # Priority tests
    def test_get_highest_priority_external(self):
        """Test external interrupt has highest priority"""
        self.ic.enable_global_interrupts()
        self.ic.enable_interrupt(InterruptController.INT_SOFTWARE)
        self.ic.enable_interrupt(InterruptController.INT_TIMER)
        self.ic.enable_interrupt(InterruptController.INT_EXTERNAL)
        
        self.ic.set_pending(InterruptController.INT_SOFTWARE)
        self.ic.set_pending(InterruptController.INT_TIMER)
        self.ic.set_pending(InterruptController.INT_EXTERNAL)
        
        highest = self.ic.get_highest_priority_interrupt()
        
        self.assertEqual(highest, 11)  # External
    
    def test_get_highest_priority_software_over_timer(self):
        """Test software interrupt priority over timer"""
        self.ic.enable_global_interrupts()
        self.ic.enable_interrupt(InterruptController.INT_SOFTWARE)
        self.ic.enable_interrupt(InterruptController.INT_TIMER)
        
        self.ic.set_pending(InterruptController.INT_SOFTWARE)
        self.ic.set_pending(InterruptController.INT_TIMER)
        
        highest = self.ic.get_highest_priority_interrupt()
        
        self.assertEqual(highest, 3)  # Software
    
    def test_get_highest_priority_none_when_none_deliverable(self):
        """Test highest priority returns None when no interrupts deliverable"""
        highest = self.ic.get_highest_priority_interrupt()
        
        self.assertIsNone(highest)
    
    # Masking tests
    def test_mask_interrupts(self):
        """Test setting interrupt mask"""
        # Enable timer and external, disable software
        mask = (1 << 7) | (1 << 11)
        self.ic.mask_interrupts(mask)
        
        self.assertTrue(self.ic.is_enabled(InterruptController.INT_TIMER))
        self.assertTrue(self.ic.is_enabled(InterruptController.INT_EXTERNAL))
        self.assertFalse(self.ic.is_enabled(InterruptController.INT_SOFTWARE))
    
    def test_get_interrupt_mask(self):
        """Test getting current interrupt mask"""
        self.ic.enable_interrupt(InterruptController.INT_SOFTWARE)
        self.ic.enable_interrupt(InterruptController.INT_TIMER)
        
        mask = self.ic.get_interrupt_mask()
        
        expected = (1 << 3) | (1 << 7)
        self.assertEqual(mask, expected)
    
    def test_get_pending_mask(self):
        """Test getting pending interrupt mask"""
        self.ic.set_pending(InterruptController.INT_TIMER)
        self.ic.set_pending(InterruptController.INT_EXTERNAL)
        
        mask = self.ic.get_pending_mask()
        
        expected = (1 << 7) | (1 << 11)
        self.assertEqual(mask, expected)
    
    # Edge/level triggering tests
    def test_edge_triggered_configuration(self):
        """Test configuring interrupt as edge-triggered"""
        self.ic.set_edge_triggered(InterruptController.INT_TIMER)
        
        self.assertTrue(self.ic.is_edge_triggered(InterruptController.INT_TIMER))
        self.assertFalse(self.ic.is_level_triggered(InterruptController.INT_TIMER))
    
    def test_level_triggered_configuration(self):
        """Test configuring interrupt as level-triggered (default)"""
        # Default is level-triggered
        self.assertTrue(self.ic.is_level_triggered(InterruptController.INT_SOFTWARE))
        
        # Change to edge, then back to level
        self.ic.set_edge_triggered(InterruptController.INT_SOFTWARE)
        self.ic.set_level_triggered(InterruptController.INT_SOFTWARE)
        
        self.assertTrue(self.ic.is_level_triggered(InterruptController.INT_SOFTWARE))
    
    def test_edge_triggered_latched(self):
        """Test edge-triggered interrupt latches pending bit"""
        self.ic.set_edge_triggered(InterruptController.INT_TIMER)
        
        self.ic.set_pending(InterruptController.INT_TIMER, edge=True)
        
        self.assertTrue(self.ic.is_pending(InterruptController.INT_TIMER))
        self.assertIn(InterruptController.INT_TIMER, self.ic.latched_edges)
    
    def test_acknowledge_clears_edge_triggered(self):
        """Test acknowledging edge-triggered interrupt clears pending"""
        self.ic.set_edge_triggered(InterruptController.INT_EXTERNAL)
        self.ic.set_pending(InterruptController.INT_EXTERNAL, edge=True)
        
        self.ic.acknowledge_interrupt(InterruptController.INT_EXTERNAL)
        
        self.assertFalse(self.ic.is_pending(InterruptController.INT_EXTERNAL))
        self.assertNotIn(InterruptController.INT_EXTERNAL, self.ic.latched_edges)
    
    def test_acknowledge_level_triggered_no_auto_clear(self):
        """Test acknowledging level-triggered interrupt doesn't auto-clear"""
        # Level-triggered by default
        self.ic.set_pending(InterruptController.INT_SOFTWARE)
        
        self.ic.acknowledge_interrupt(InterruptController.INT_SOFTWARE)
        
        # Should still be pending (software must clear source)
        self.assertTrue(self.ic.is_pending(InterruptController.INT_SOFTWARE))
    
    # Interrupt code conversion
    def test_get_interrupt_code_software(self):
        """Test converting software interrupt bit to code"""
        code = self.ic.get_interrupt_code(InterruptController.INT_SOFTWARE)
        
        self.assertEqual(code, InterruptController.INTERRUPT_SOFTWARE)
        self.assertEqual(code, 0x80000003)
    
    def test_get_interrupt_code_timer(self):
        """Test converting timer interrupt bit to code"""
        code = self.ic.get_interrupt_code(InterruptController.INT_TIMER)
        
        self.assertEqual(code, InterruptController.INTERRUPT_TIMER)
        self.assertEqual(code, 0x80000007)
    
    def test_get_interrupt_code_external(self):
        """Test converting external interrupt bit to code"""
        code = self.ic.get_interrupt_code(InterruptController.INT_EXTERNAL)
        
        self.assertEqual(code, InterruptController.INTERRUPT_EXTERNAL)
        self.assertEqual(code, 0x8000000B)
    
    # Reset test
    def test_reset(self):
        """Test resetting interrupt controller state"""
        # Setup some state
        self.ic.enable_global_interrupts()
        self.ic.enable_interrupt(InterruptController.INT_SOFTWARE)
        self.ic.enable_interrupt(InterruptController.INT_TIMER)
        self.ic.set_pending(InterruptController.INT_SOFTWARE)
        self.ic.set_pending(InterruptController.INT_TIMER)
        
        # Reset
        self.ic.reset()
        
        # Verify all cleared
        self.assertFalse(self.ic.is_globally_enabled())
        self.assertFalse(self.ic.is_enabled(InterruptController.INT_SOFTWARE))
        self.assertFalse(self.ic.is_enabled(InterruptController.INT_TIMER))
        self.assertFalse(self.ic.is_pending(InterruptController.INT_SOFTWARE))
        self.assertFalse(self.ic.is_pending(InterruptController.INT_TIMER))
        self.assertEqual(len(self.ic.latched_edges), 0)
    
    # Status string test
    def test_get_status_string(self):
        """Test getting human-readable status"""
        self.ic.enable_global_interrupts()
        self.ic.enable_interrupt(InterruptController.INT_TIMER)
        self.ic.set_pending(InterruptController.INT_TIMER)
        
        status = self.ic.get_status_string()
        
        self.assertIn("Global Enable: True", status)
        self.assertIn("T=True", status)  # Timer pending
        self.assertIn("Deliverable", status)


class TestInterruptSource(unittest.TestCase):
    """Test suite for InterruptSource"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.csr = CSRBank()
        self.ic = InterruptController(self.csr)
        self.source = InterruptSource("Timer", InterruptController.INT_TIMER)
    
    def test_connect_source(self):
        """Test connecting interrupt source to controller"""
        self.source.connect(self.ic)
        
        self.assertEqual(self.source.controller, self.ic)
    
    def test_assert_interrupt_level_triggered(self):
        """Test asserting level-triggered interrupt"""
        self.source.connect(self.ic)
        
        self.source.assert_interrupt()
        
        self.assertTrue(self.source.is_active())
        self.assertTrue(self.ic.is_pending(InterruptController.INT_TIMER))
    
    def test_deassert_interrupt_level_triggered(self):
        """Test deasserting level-triggered interrupt"""
        self.source.connect(self.ic)
        
        self.source.assert_interrupt()
        self.source.deassert_interrupt()
        
        self.assertFalse(self.source.is_active())
        self.assertFalse(self.ic.is_pending(InterruptController.INT_TIMER))
    
    def test_assert_interrupt_edge_triggered(self):
        """Test asserting edge-triggered interrupt"""
        self.ic.set_edge_triggered(InterruptController.INT_TIMER)
        self.source.connect(self.ic)
        
        self.source.assert_interrupt()
        
        self.assertTrue(self.ic.is_pending(InterruptController.INT_TIMER))
        self.assertIn(InterruptController.INT_TIMER, self.ic.latched_edges)
    
    def test_pulse_interrupt(self):
        """Test interrupt pulse"""
        self.source.connect(self.ic)
        
        self.source.pulse()
        
        # For level-triggered, pulse clears it
        self.assertFalse(self.source.is_active())
        self.assertFalse(self.ic.is_pending(InterruptController.INT_TIMER))
    
    def test_pulse_interrupt_edge_triggered(self):
        """Test interrupt pulse with edge trigger"""
        self.ic.set_edge_triggered(InterruptController.INT_TIMER)
        self.source.connect(self.ic)
        
        self.source.pulse()
        
        # Edge-triggered latches on rising edge
        self.assertTrue(self.ic.is_pending(InterruptController.INT_TIMER))


if __name__ == '__main__':
    unittest.main()
