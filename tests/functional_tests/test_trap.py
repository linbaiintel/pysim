"""
Test Trap and Interrupt Mechanism.

Tests trap entry, interrupt delivery, CSR state management, and ECALL/EBREAK integration.
"""
import unittest
from trap import TrapController
from csr import CSRBank


class TestTrapController(unittest.TestCase):
    """Test suite for trap and interrupt mechanism"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.csr_bank = CSRBank()
        self.trap = TrapController(self.csr_bank)
    
    # Exception handling tests
    def test_exception_saves_pc_to_mepc(self):
        """Test exception saves faulting PC to mepc"""
        pc = 0x1000
        self.trap.trigger_exception(TrapController.EXCEPTION_ECALL_FROM_M, pc)
        
        mepc = self.csr_bank.read(0x341)
        self.assertEqual(mepc, pc)
    
    def test_exception_sets_mcause(self):
        """Test exception sets mcause with exception code"""
        pc = 0x2000
        result = self.trap.trigger_exception(TrapController.EXCEPTION_BREAKPOINT, pc)
        
        mcause = self.csr_bank.read(0x342)
        self.assertEqual(mcause, TrapController.EXCEPTION_BREAKPOINT)
        self.assertEqual(result['cause'], TrapController.EXCEPTION_BREAKPOINT)
    
    def test_exception_sets_mtval(self):
        """Test exception sets mtval with trap value"""
        pc = 0x3000
        trap_value = 0xDEADBEEF
        self.trap.trigger_exception(TrapController.EXCEPTION_ILLEGAL_INSTRUCTION, 
                                    pc, trap_value)
        
        mtval = self.csr_bank.read(0x343)
        self.assertEqual(mtval, trap_value)
    
    def test_exception_disables_interrupts(self):
        """Test exception disables interrupts (clears mstatus.MIE)"""
        # Enable interrupts first
        mstatus = self.csr_bank.read(0x300)
        mstatus |= (1 << 3)  # Set MIE
        self.csr_bank.write(0x300, mstatus)
        
        # Trigger exception
        self.trap.trigger_exception(TrapController.EXCEPTION_ECALL_FROM_M, 0x1000)
        
        # Check MIE is cleared
        new_mstatus = self.csr_bank.read(0x300)
        mie = (new_mstatus >> 3) & 0x1
        self.assertEqual(mie, 0, "MIE should be 0 after exception")
    
    def test_exception_saves_mie_to_mpie(self):
        """Test exception saves current MIE to MPIE"""
        # Set MIE=1
        mstatus = self.csr_bank.read(0x300)
        mstatus |= (1 << 3)  # Set MIE
        self.csr_bank.write(0x300, mstatus)
        
        # Trigger exception
        self.trap.trigger_exception(TrapController.EXCEPTION_ECALL_FROM_M, 0x1000)
        
        # Check MPIE=1 (saved from MIE)
        new_mstatus = self.csr_bank.read(0x300)
        mpie = (new_mstatus >> 7) & 0x1
        self.assertEqual(mpie, 1, "MPIE should be 1 (saved from MIE)")
    
    def test_exception_sets_mpp_to_machine_mode(self):
        """Test exception sets MPP to Machine mode (3)"""
        self.trap.trigger_exception(TrapController.EXCEPTION_ECALL_FROM_M, 0x1000)
        
        mstatus = self.csr_bank.read(0x300)
        mpp = (mstatus >> 11) & 0x3
        self.assertEqual(mpp, 3, "MPP should be 3 (Machine mode)")
    
    def test_exception_returns_handler_address(self):
        """Test exception returns trap handler address from mtvec"""
        # Set mtvec base address
        handler_base = 0x80000000
        self.csr_bank.write(0x305, handler_base)
        
        result = self.trap.trigger_exception(TrapController.EXCEPTION_ECALL_FROM_M, 0x1000)
        
        self.assertEqual(result['handler_pc'], handler_base)
        self.assertEqual(result['type'], 'exception')
    
    def test_exception_with_vectored_mtvec_uses_base(self):
        """Test exceptions use base address even in vectored mode"""
        # Set mtvec to vectored mode (mode=1)
        handler_base = 0x80000000
        self.csr_bank.write(0x305, handler_base | 0x1)
        
        result = self.trap.trigger_exception(TrapController.EXCEPTION_BREAKPOINT, 0x1000)
        
        # Exceptions always use base (no vectoring)
        self.assertEqual(result['handler_pc'], handler_base)
    
    # ECALL/EBREAK integration
    def test_ecall_triggers_exception(self):
        """Test ECALL triggers environment call exception"""
        pc = 0x1000
        result = self.trap.ecall(pc)
        
        self.assertEqual(result['type'], 'exception')
        self.assertEqual(result['cause'], TrapController.EXCEPTION_ECALL_FROM_M)
        
        mcause = self.csr_bank.read(0x342)
        self.assertEqual(mcause, TrapController.EXCEPTION_ECALL_FROM_M)
    
    def test_ebreak_triggers_exception(self):
        """Test EBREAK triggers breakpoint exception"""
        pc = 0x2000
        result = self.trap.ebreak(pc)
        
        self.assertEqual(result['type'], 'exception')
        self.assertEqual(result['cause'], TrapController.EXCEPTION_BREAKPOINT)
        
        mcause = self.csr_bank.read(0x342)
        self.assertEqual(mcause, TrapController.EXCEPTION_BREAKPOINT)
    
    def test_illegal_instruction_exception(self):
        """Test illegal instruction exception with instruction bits"""
        pc = 0x3000
        bad_instruction = 0xFFFFFFFF
        
        result = self.trap.illegal_instruction(pc, bad_instruction)
        
        self.assertEqual(result['type'], 'exception')
        self.assertEqual(result['cause'], TrapController.EXCEPTION_ILLEGAL_INSTRUCTION)
        
        mtval = self.csr_bank.read(0x343)
        self.assertEqual(mtval, bad_instruction)
    
    # Interrupt handling tests
    def test_set_interrupt_pending_software(self):
        """Test setting software interrupt pending"""
        self.trap.set_interrupt_pending('software')
        
        self.assertIn(TrapController.INTERRUPT_SOFTWARE, self.trap.pending_interrupts)
        
        # Check mip bit is set
        mip = self.csr_bank.read(0x344)
        self.assertTrue(mip & (1 << 3))
    
    def test_set_interrupt_pending_timer(self):
        """Test setting timer interrupt pending"""
        self.trap.set_interrupt_pending('timer')
        
        self.assertIn(TrapController.INTERRUPT_TIMER, self.trap.pending_interrupts)
        
        mip = self.csr_bank.read(0x344)
        self.assertTrue(mip & (1 << 7))
    
    def test_set_interrupt_pending_external(self):
        """Test setting external interrupt pending"""
        self.trap.set_interrupt_pending('external')
        
        self.assertIn(TrapController.INTERRUPT_EXTERNAL, self.trap.pending_interrupts)
        
        mip = self.csr_bank.read(0x344)
        self.assertTrue(mip & (1 << 11))
    
    def test_clear_interrupt_pending(self):
        """Test clearing pending interrupt"""
        self.trap.set_interrupt_pending('timer')
        self.trap.clear_interrupt_pending('timer')
        
        self.assertNotIn(TrapController.INTERRUPT_TIMER, self.trap.pending_interrupts)
        
        mip = self.csr_bank.read(0x344)
        self.assertFalse(mip & (1 << 7))
    
    def test_check_pending_interrupts_when_disabled(self):
        """Test pending interrupts not delivered when globally disabled"""
        self.trap.set_interrupt_pending('timer')
        
        # Ensure MIE=0 (interrupts disabled)
        mstatus = self.csr_bank.read(0x300)
        mstatus &= ~(1 << 3)
        self.csr_bank.write(0x300, mstatus)
        
        result = self.trap.check_pending_interrupts(0x1000)
        self.assertIsNone(result, "Interrupts should not be delivered when MIE=0")
    
    def test_check_pending_interrupts_when_enabled(self):
        """Test pending interrupts delivered when enabled"""
        # Enable interrupts globally (MIE=1)
        mstatus = self.csr_bank.read(0x300)
        mstatus |= (1 << 3)
        self.csr_bank.write(0x300, mstatus)
        
        # Enable timer interrupt (mie bit 7)
        mie = self.csr_bank.read(0x304)
        mie |= (1 << 7)
        self.csr_bank.write(0x304, mie)
        
        # Set timer interrupt pending
        self.trap.set_interrupt_pending('timer')
        
        # Check interrupts
        result = self.trap.check_pending_interrupts(0x2000)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'interrupt')
        self.assertEqual(result['cause'], TrapController.INTERRUPT_TIMER)
    
    def test_interrupt_saves_next_pc_to_mepc(self):
        """Test interrupt saves next PC (not current) to mepc"""
        # Enable interrupts
        mstatus = self.csr_bank.read(0x300)
        mstatus |= (1 << 3)
        self.csr_bank.write(0x300, mstatus)
        
        mie = self.csr_bank.read(0x304)
        mie |= (1 << 7)
        self.csr_bank.write(0x304, mie)
        
        self.trap.set_interrupt_pending('timer')
        
        next_pc = 0x3000
        self.trap.check_pending_interrupts(next_pc)
        
        mepc = self.csr_bank.read(0x341)
        self.assertEqual(mepc, next_pc)
    
    def test_interrupt_sets_mcause_with_msb(self):
        """Test interrupt sets mcause with MSB=1"""
        mstatus = self.csr_bank.read(0x300)
        mstatus |= (1 << 3)
        self.csr_bank.write(0x300, mstatus)
        
        mie = self.csr_bank.read(0x304)
        mie |= (1 << 3)  # Software interrupt
        self.csr_bank.write(0x304, mie)
        
        self.trap.set_interrupt_pending('software')
        self.trap.check_pending_interrupts(0x1000)
        
        mcause = self.csr_bank.read(0x342)
        self.assertEqual(mcause, TrapController.INTERRUPT_SOFTWARE)
        self.assertTrue(mcause & 0x80000000, "MSB should be 1 for interrupts")
    
    def test_interrupt_direct_mode(self):
        """Test interrupt uses base address in direct mode"""
        handler_base = 0x80000000
        self.csr_bank.write(0x305, handler_base | 0x0)  # Direct mode
        
        mstatus = self.csr_bank.read(0x300)
        mstatus |= (1 << 3)
        self.csr_bank.write(0x300, mstatus)
        
        mie = self.csr_bank.read(0x304)
        mie |= (1 << 7)
        self.csr_bank.write(0x304, mie)
        
        self.trap.set_interrupt_pending('timer')
        result = self.trap.check_pending_interrupts(0x1000)
        
        self.assertEqual(result['handler_pc'], handler_base)
    
    def test_interrupt_vectored_mode(self):
        """Test interrupt uses vectored address in vectored mode"""
        handler_base = 0x80000000
        self.csr_bank.write(0x305, handler_base | 0x1)  # Vectored mode
        
        mstatus = self.csr_bank.read(0x300)
        mstatus |= (1 << 3)
        self.csr_bank.write(0x300, mstatus)
        
        mie = self.csr_bank.read(0x304)
        mie |= (1 << 7)  # Timer interrupt (cause 7)
        self.csr_bank.write(0x304, mie)
        
        self.trap.set_interrupt_pending('timer')
        result = self.trap.check_pending_interrupts(0x1000)
        
        # Timer interrupt (7) should vector to base + 7*4
        expected_handler = handler_base + (7 * 4)
        self.assertEqual(result['handler_pc'], expected_handler)
    
    def test_interrupt_priority_external_highest(self):
        """Test external interrupt has highest priority"""
        # Enable all interrupts
        mstatus = self.csr_bank.read(0x300)
        mstatus |= (1 << 3)
        self.csr_bank.write(0x300, mstatus)
        
        mie = self.csr_bank.read(0x304)
        mie |= (1 << 3) | (1 << 7) | (1 << 11)  # All enabled
        self.csr_bank.write(0x304, mie)
        
        # Set all interrupts pending
        self.trap.set_interrupt_pending('software')
        self.trap.set_interrupt_pending('timer')
        self.trap.set_interrupt_pending('external')
        
        # Check - should deliver external first
        result = self.trap.check_pending_interrupts(0x1000)
        
        self.assertEqual(result['cause'], TrapController.INTERRUPT_EXTERNAL)
    
    def test_interrupt_removed_from_pending_when_delivered(self):
        """Test interrupt removed from pending set when delivered"""
        mstatus = self.csr_bank.read(0x300)
        mstatus |= (1 << 3)
        self.csr_bank.write(0x300, mstatus)
        
        mie = self.csr_bank.read(0x304)
        mie |= (1 << 7)
        self.csr_bank.write(0x304, mie)
        
        self.trap.set_interrupt_pending('timer')
        self.trap.check_pending_interrupts(0x1000)
        
        # Should be removed from pending
        self.assertNotIn(TrapController.INTERRUPT_TIMER, self.trap.pending_interrupts)
    
    def test_interrupt_not_delivered_if_specific_not_enabled(self):
        """Test interrupt not delivered if specific bit not set in mie"""
        # Global enable
        mstatus = self.csr_bank.read(0x300)
        mstatus |= (1 << 3)
        self.csr_bank.write(0x300, mstatus)
        
        # But don't enable timer interrupt in mie (bit 7)
        mie = self.csr_bank.read(0x304)
        mie &= ~(1 << 7)
        self.csr_bank.write(0x304, mie)
        
        self.trap.set_interrupt_pending('timer')
        result = self.trap.check_pending_interrupts(0x1000)
        
        self.assertIsNone(result, "Timer interrupt should not be delivered if not enabled in mie")
    
    # Complete trap sequence tests
    def test_complete_trap_sequence_exception(self):
        """Test complete trap sequence: exception entry"""
        # Setup: enable interrupts, set trap vector
        mstatus = self.csr_bank.read(0x300)
        mstatus |= (1 << 3)  # MIE=1
        self.csr_bank.write(0x300, mstatus)
        
        handler_addr = 0x80000000
        self.csr_bank.write(0x305, handler_addr)
        
        # Trigger ECALL
        pc = 0x1000
        result = self.trap.ecall(pc)
        
        # Verify all CSRs updated correctly
        self.assertEqual(self.csr_bank.read(0x341), pc)  # mepc
        self.assertEqual(result['handler_pc'], handler_addr)
        
        new_mstatus = self.csr_bank.read(0x300)
        self.assertEqual((new_mstatus >> 3) & 0x1, 0)  # MIE=0
        self.assertEqual((new_mstatus >> 7) & 0x1, 1)  # MPIE=1 (saved from MIE)
        self.assertEqual((new_mstatus >> 11) & 0x3, 3)  # MPP=3 (Machine)
    
    def test_none_csr_bank_returns_none(self):
        """Test trap controller with None CSR bank"""
        trap = TrapController(None)
        result = trap.trigger_exception(TrapController.EXCEPTION_ECALL_FROM_M, 0x1000)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
