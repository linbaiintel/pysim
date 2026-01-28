"""Tests for system instructions (ECALL, EBREAK)"""
import unittest
from instruction import Instruction
from exe import EXE
from register_file import RegisterFile


class TestSystemInstructions(unittest.TestCase):
    """Test ECALL and EBREAK system instructions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.registers = RegisterFile()
    
    # ==================== ECALL Tests ====================
    
    def test_ecall_parsing(self):
        """Test ECALL instruction parsing"""
        inst = Instruction("ECALL")
        self.assertEqual(inst.operation, "ECALL")
        self.assertIsNone(inst.dest_reg)
        self.assertEqual(inst.src_regs, [])
    
    def test_ecall_exit_syscall(self):
        """Test ECALL with exit syscall (93)"""
        self.registers.write('R17', 93)  # syscall number = exit
        self.registers.write('R10', 42)  # exit code = 42
        
        result = EXE.execute_ecall(self.registers)
        
        self.assertEqual(result['action'], 'exit')
        self.assertEqual(result['code'], 42)
    
    def test_ecall_print_syscall(self):
        """Test ECALL with print integer syscall (1)"""
        self.registers.write('R17', 1)   # syscall number = print
        self.registers.write('R10', 123) # value to print
        
        result = EXE.execute_ecall(self.registers)
        
        self.assertEqual(result['action'], 'print')
        self.assertEqual(result['value'], 123)
    
    def test_ecall_write_syscall(self):
        """Test ECALL with write syscall (64)"""
        self.registers.write('R17', 64)   # syscall number = write
        self.registers.write('R10', 1)    # fd = stdout
        self.registers.write('R11', 1000) # buffer address
        self.registers.write('R12', 20)   # count
        
        result = EXE.execute_ecall(self.registers)
        
        self.assertEqual(result['action'], 'write')
        self.assertEqual(result['fd'], 1)
        self.assertEqual(result['addr'], 1000)
        self.assertEqual(result['count'], 20)
    
    def test_ecall_unknown_syscall(self):
        """Test ECALL with unknown syscall number"""
        self.registers.write('R17', 999)  # unknown syscall
        
        result = EXE.execute_ecall(self.registers)
        
        self.assertEqual(result['action'], 'nop')
        self.assertEqual(result['syscall'], 999)
    
    def test_ecall_no_registers(self):
        """Test ECALL with no register file (defaults to 0)"""
        result = EXE.execute_ecall(None)
        
        self.assertEqual(result['action'], 'nop')
        self.assertEqual(result['syscall'], 0)
    
    def test_ecall_exit_with_zero(self):
        """Test ECALL exit with exit code 0 (success)"""
        self.registers.write('R17', 93)  # exit syscall
        self.registers.write('R10', 0)   # exit code = 0
        
        result = EXE.execute_ecall(self.registers)
        
        self.assertEqual(result['action'], 'exit')
        self.assertEqual(result['code'], 0)
    
    def test_ecall_exit_with_negative(self):
        """Test ECALL exit with negative exit code"""
        self.registers.write('R17', 93)
        self.registers.write('R10', -1)
        
        result = EXE.execute_ecall(self.registers)
        
        self.assertEqual(result['action'], 'exit')
        # Note: Negative values will be interpreted as unsigned 32-bit
    
    # ==================== EBREAK Tests ====================
    
    def test_ebreak_parsing(self):
        """Test EBREAK instruction parsing"""
        inst = Instruction("EBREAK")
        self.assertEqual(inst.operation, "EBREAK")
        self.assertIsNone(inst.dest_reg)
        self.assertEqual(inst.src_regs, [])
    
    def test_ebreak_execution(self):
        """Test EBREAK execution"""
        result = EXE.execute_ebreak()
        
        self.assertEqual(result['action'], 'break')
    
    def test_ebreak_return_type(self):
        """Test EBREAK returns dictionary"""
        result = EXE.execute_ebreak()
        
        self.assertIsInstance(result, dict)
        self.assertIn('action', result)
    
    # ==================== Integration Tests ====================
    
    def test_ecall_in_execute_instruction(self):
        """Test ECALL through execute_instruction"""
        inst = Instruction("ECALL")
        inst.src_values = []
        
        result, mem_addr = EXE.execute_instruction(inst)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'ecall')
        self.assertIsNone(mem_addr)
    
    def test_ebreak_in_execute_instruction(self):
        """Test EBREAK through execute_instruction"""
        inst = Instruction("EBREAK")
        inst.src_values = []
        
        result, mem_addr = EXE.execute_instruction(inst)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'ebreak')
        self.assertIsNone(mem_addr)
    
    def test_system_instructions_case_insensitive(self):
        """Test system instructions are case-insensitive"""
        inst1 = Instruction("ecall")
        inst2 = Instruction("ECALL")
        inst3 = Instruction("ebreak")
        inst4 = Instruction("EBREAK")
        
        self.assertEqual(inst1.operation, "ECALL")
        self.assertEqual(inst2.operation, "ECALL")
        self.assertEqual(inst3.operation, "EBREAK")
        self.assertEqual(inst4.operation, "EBREAK")
    
    # ==================== Edge Cases ====================
    
    def test_ecall_with_large_values(self):
        """Test ECALL with large register values"""
        self.registers.write('R17', 1)
        self.registers.write('R10', 0xFFFFFFFF)  # Max 32-bit value
        
        result = EXE.execute_ecall(self.registers)
        
        self.assertEqual(result['action'], 'print')
        self.assertEqual(result['value'], 0xFFFFFFFF)
    
    def test_multiple_ecalls_same_registers(self):
        """Test multiple ECALL executions with same register file"""
        # First call - exit
        self.registers.write('R17', 93)
        self.registers.write('R10', 1)
        result1 = EXE.execute_ecall(self.registers)
        
        # Second call - print (change syscall number)
        self.registers.write('R17', 1)
        self.registers.write('R10', 100)
        result2 = EXE.execute_ecall(self.registers)
        
        self.assertEqual(result1['action'], 'exit')
        self.assertEqual(result1['code'], 1)
        self.assertEqual(result2['action'], 'print')
        self.assertEqual(result2['value'], 100)


if __name__ == '__main__':
    unittest.main()
