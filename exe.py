"""EXE (Execution Unit) for RISC-V pipeline simulator"""


class EXE:
    """Execution Unit for executing all RISC-V operations"""
    @staticmethod
    def execute(operation, operand1, operand2):
        """Execute ALU operation
        
        Args:
            operation: Operation to perform (ADD, SUB, AND, OR, XOR, SLT, SLTU, SLL, SRL, SRA, etc.)
            operand1: First operand (typically register value or immediate)
            operand2: Second operand (register value or immediate)
            
        Returns:
            Result of the operation (32-bit value)
        """
        op = operation.upper()
        
        # Ensure 32-bit operations (mask to 32 bits)
        MASK_32 = 0xFFFFFFFF
        operand1 = operand1 & MASK_32
        operand2 = operand2 & MASK_32
        
        # Basic arithmetic
        if op == 'ADD' or op == 'ADDI':
            result = (operand1 + operand2) & MASK_32
        elif op == 'SUB':
            result = (operand1 - operand2) & MASK_32
            
        # Logical operations
        elif op == 'AND' or op == 'ANDI':
            result = operand1 & operand2
        elif op == 'OR' or op == 'ORI':
            result = operand1 | operand2
        elif op == 'XOR' or op == 'XORI':
            result = operand1 ^ operand2
            
        # Comparison (signed)
        elif op == 'SLT' or op == 'SLTI':  # Set Less Than
            # Convert to signed for comparison
            op1_signed = EXE._to_signed(operand1)
            op2_signed = EXE._to_signed(operand2)
            result = 1 if op1_signed < op2_signed else 0
            
        # Comparison (unsigned)
        elif op == 'SLTU' or op == 'SLTIU':  # Set Less Than Unsigned
            result = 1 if operand1 < operand2 else 0
            
        # Shift operations
        elif op == 'SLL' or op == 'SLLI':  # Shift Left Logical
            shift_amount = operand2 & 0x1F  # Only lower 5 bits
            result = (operand1 << shift_amount) & MASK_32
            
        elif op == 'SRL' or op == 'SRLI':  # Shift Right Logical
            shift_amount = operand2 & 0x1F
            result = operand1 >> shift_amount
            
        elif op == 'SRA' or op == 'SRAI':  # Shift Right Arithmetic
            shift_amount = operand2 & 0x1F
            # Arithmetic shift preserves sign bit
            if operand1 & 0x80000000:  # If sign bit is set
                # Fill with 1s from the left
                result = operand1 >> shift_amount
                # Create mask of 1s for the high bits
                mask = ((1 << shift_amount) - 1) << (32 - shift_amount)
                result = result | mask
                result = result & MASK_32
            else:
                result = operand1 >> shift_amount
                
        else:
            result = 0
            
        return result
    
    @staticmethod
    def _to_signed(value):
        """Convert 32-bit unsigned value to signed integer"""
        if value & 0x80000000:  # If sign bit is set
            return value - 0x100000000
        return value
    
    @staticmethod
    def calculate_memory_address(base_value, offset):
        """Calculate memory address for LOAD/STORE operations
        
        Args:
            base_value: Base register value
            offset: Offset to add to base
            
        Returns:
            Memory address (base + offset)
        """
        return base_value + offset
    
    @staticmethod
    def execute_lui(immediate):
        """Execute LUI (Load Upper Immediate) instruction
        
        Args:
            immediate: 20-bit immediate value
            
        Returns:
            Result with immediate in upper 20 bits
        """
        return (immediate & 0xFFFFF) << 12
    
    @staticmethod
    def execute_auipc(immediate, pc=0):
        """Execute AUIPC (Add Upper Immediate to PC) instruction
        
        Args:
            immediate: 20-bit immediate value
            pc: Program counter value (default 0 if not tracked)
            
        Returns:
            PC + (immediate << 12), masked to 32 bits
        """
        return (pc + ((immediate & 0xFFFFF) << 12)) & 0xFFFFFFFF
    
    @staticmethod
    def execute_jal(offset, pc=0):
        """Execute JAL (Jump And Link) instruction
        
        Args:
            offset: Signed offset to add to PC
            pc: Current program counter value
            
        Returns:
            Tuple of (return_address, jump_target)
            - return_address: PC + 4 (address of next instruction)
            - jump_target: PC + offset (where to jump to)
        """
        return_address = (pc + 4) & 0xFFFFFFFF
        jump_target = (pc + offset) & 0xFFFFFFFF
        return return_address, jump_target
    
    @staticmethod
    def execute_jalr(base_value, offset, pc=0):
        """Execute JALR (Jump And Link Register) instruction
        
        Args:
            base_value: Value from source register
            offset: Signed offset to add to base
            pc: Current program counter value
            
        Returns:
            Tuple of (return_address, jump_target)
            - return_address: PC + 4 (address of next instruction)
            - jump_target: (base_value + offset) & ~1 (LSB cleared per RISC-V spec)
        """
        return_address = (pc + 4) & 0xFFFFFFFF
        jump_target = (base_value + offset) & 0xFFFFFFFE  # Clear LSB
        return return_address, jump_target
    
    @staticmethod
    def execute_ecall(registers):
        """Execute ECALL (Environment Call) instruction
        
        Simulates basic system calls based on RISC-V calling convention:
        - a7 (R17): syscall number
        - a0 (R10): first argument / return value
        - a1 (R11): second argument
        - a2 (R12): third argument
        
        Args:
            registers: RegisterFile object to read syscall arguments
            
        Returns:
            Dictionary with action and result:
            - {'action': 'exit', 'code': exit_code}
            - {'action': 'print', 'value': value}
            - {'action': 'nop'}  # For unimplemented syscalls
        """
        # Get syscall number from a7 (R17)
        syscall_num = registers.read('R17') if registers else 0
        
        if syscall_num == 93:  # exit
            exit_code = registers.read('R10') if registers else 0
            return {'action': 'exit', 'code': exit_code}
        elif syscall_num == 1:  # print integer (custom)
            value = registers.read('R10') if registers else 0
            return {'action': 'print', 'value': value}
        elif syscall_num == 64:  # write (simplified)
            fd = registers.read('R10') if registers else 1
            buf_addr = registers.read('R11') if registers else 0
            count = registers.read('R12') if registers else 0
            return {'action': 'write', 'fd': fd, 'addr': buf_addr, 'count': count}
        else:
            # Unknown syscall - treat as NOP
            return {'action': 'nop', 'syscall': syscall_num}
    
    @staticmethod
    def execute_ebreak():
        """Execute EBREAK (Environment Breakpoint) instruction
        
        Signals a breakpoint for debugger. In our simulator, we halt execution.
        
        Returns:
            Dictionary with action: {'action': 'break'}
        """
        return {'action': 'break'}
    
    @staticmethod
    def execute_mret(csr_bank):
        """Execute MRET (Machine Return) instruction
        
        Returns from machine-mode trap handler by:
        1. Restoring PC from mepc (0x341)
        2. Restoring interrupt enable: mstatus.MPIE -> mstatus.MIE
        3. Setting mstatus.MPIE to 1
        4. Restoring privilege mode from mstatus.MPP
        5. Setting mstatus.MPP to User mode (0)
        
        mstatus bit layout (relevant bits):
        - Bit 3: MIE (Machine Interrupt Enable)
        - Bit 7: MPIE (Machine Previous Interrupt Enable)
        - Bits 11-12: MPP (Machine Previous Privilege mode: 0=User, 3=Machine)
        
        Args:
            csr_bank: CSRBank instance to access mepc and mstatus
            
        Returns:
            Dictionary with new PC: {'type': 'mret', 'new_pc': <mepc_value>}
        """
        if csr_bank is None:
            # Should not happen in normal operation
            return {'type': 'mret', 'new_pc': 0}
        
        # Read return address from mepc
        new_pc = csr_bank.read(0x341)  # mepc
        
        # Read current mstatus
        mstatus = csr_bank.read(0x300)
        
        # Extract MPIE (bit 7)
        mpie = (mstatus >> 7) & 0x1
        
        # Modify mstatus:
        # 1. MIE (bit 3) = MPIE (bit 7)
        # 2. MPIE (bit 7) = 1
        # 3. MPP (bits 11-12) = 0 (User mode)
        
        # Clear MIE, MPIE, and MPP fields
        mstatus &= ~((1 << 3) | (1 << 7) | (0x3 << 11))
        
        # Set MIE = MPIE
        mstatus |= (mpie << 3)
        
        # Set MPIE = 1
        mstatus |= (1 << 7)
        
        # MPP already cleared to 0 (User mode)
        
        # Write back modified mstatus
        csr_bank.write(0x300, mstatus)
        
        return {'type': 'mret', 'new_pc': new_pc}
    
    @staticmethod
    def execute_csr_read_write(csr_bank, csr_addr, value):
        """Execute CSRRW - Atomic Read/Write CSR
        
        Args:
            csr_bank: CSRBank instance
            csr_addr: CSR address
            value: Value to write
            
        Returns:
            Old value of CSR
        """
        return csr_bank.write(csr_addr, value)
    
    @staticmethod
    def execute_csr_read_set(csr_bank, csr_addr, mask):
        """Execute CSRRS - Atomic Read and Set Bits in CSR
        
        Args:
            csr_bank: CSRBank instance
            csr_addr: CSR address
            mask: Bits to set (if mask is 0, just read)
            
        Returns:
            Old value of CSR
        """
        if mask == 0:
            # Just read, don't modify
            return csr_bank.read(csr_addr)
        return csr_bank.set_bits(csr_addr, mask)
    
    @staticmethod
    def execute_csr_read_clear(csr_bank, csr_addr, mask):
        """Execute CSRRC - Atomic Read and Clear Bits in CSR
        
        Args:
            csr_bank: CSRBank instance
            csr_addr: CSR address
            mask: Bits to clear (if mask is 0, just read)
            
        Returns:
            Old value of CSR
        """
        if mask == 0:
            # Just read, don't modify
            return csr_bank.read(csr_addr)
        return csr_bank.clear_bits(csr_addr, mask)
    
    @staticmethod
    def evaluate_branch(operation, val1, val2):
        """Evaluate branch condition
        
        Args:
            operation: Branch operation (BEQ, BNE, BLT, BGE, BLTU, BGEU)
            val1: First operand value
            val2: Second operand value
            
        Returns:
            True if branch should be taken, False otherwise
        """
        op = operation.upper()
        
        if op == 'BEQ':
            return val1 == val2
        elif op == 'BNE':
            return val1 != val2
        elif op == 'BLT':
            return EXE._to_signed(val1) < EXE._to_signed(val2)
        elif op == 'BGE':
            return EXE._to_signed(val1) >= EXE._to_signed(val2)
        elif op == 'BLTU':
            return val1 < val2
        elif op == 'BGEU':
            return val1 >= val2
        else:
            return False
    
    @staticmethod
    def execute_instruction(instruction, pc=0):
        """Execute any instruction and return result
        
        Args:
            instruction: Instruction object with operation, src_values, immediate, etc.
            pc: Current program counter value (needed for AUIPC)
            
        Returns:
            Tuple of (result, mem_address) where mem_address is None for non-memory ops
        """
        if instruction.is_bubble:
            return None, None
        
        op = instruction.operation
        result = None
        mem_address = None
        
        # Memory operations
        if op in ['LOAD', 'LW', 'LH', 'LB', 'LBU', 'LHU']:
            # LOAD: src_regs[0] is base address
            base_value = instruction.src_values[0] if instruction.src_values else 0
            mem_address = EXE.calculate_memory_address(base_value, instruction.offset)
            
        elif op in ['STORE', 'SW', 'SH', 'SB']:
            # STORE: src_regs[0] is value to store, src_regs[1] is base address
            base_value = instruction.src_values[1] if len(instruction.src_values) > 1 else 0
            mem_address = EXE.calculate_memory_address(base_value, instruction.offset)
            
        # Upper immediate instructions
        elif op == 'LUI':
            result = EXE.execute_lui(instruction.immediate)
            
        elif op == 'AUIPC':
            result = EXE.execute_auipc(instruction.immediate, pc)
        
        # System instructions
        elif op == 'ECALL':
            # ECALL needs access to registers - return special marker
            result = {'type': 'ecall'}
        
        elif op == 'EBREAK':
            # EBREAK signals breakpoint
            result = {'type': 'ebreak'}
        
        elif op == 'MRET':
            # MRET needs access to CSR bank - return special marker
            result = {'type': 'mret'}
        
        # Memory ordering instructions
        elif op in ['FENCE', 'FENCE.I']:
            # For single-core simulator without separate I-cache, these are NOPs
            result = None
        
        # CSR instructions
        elif op in ['CSRRW', 'CSRRS', 'CSRRC', 'CSRRWI', 'CSRRSI', 'CSRRCI']:
            # CSR operations return special marker that needs CSR bank access
            result = {'type': 'csr', 'operation': op, 'csr_addr': instruction.csr_addr}
            
        # Branch instructions
        elif op in ['BEQ', 'BNE', 'BLT', 'BGE', 'BLTU', 'BGEU']:
            val1 = instruction.src_values[0] if len(instruction.src_values) > 0 else 0
            val2 = instruction.src_values[1] if len(instruction.src_values) > 1 else 0
            branch_taken = EXE.evaluate_branch(op, val1, val2)
            result = 1 if branch_taken else 0
            
        # Jump instructions
        elif op == 'JAL':
            return_addr, jump_target = EXE.execute_jal(instruction.offset, pc)
            result = return_addr  # Return address stored in rd
            instruction.jump_target = jump_target
            
        elif op == 'JALR':
            base_value = instruction.src_values[0] if instruction.src_values else 0
            return_addr, jump_target = EXE.execute_jalr(base_value, instruction.offset, pc)
            result = return_addr  # Return address stored in rd
            instruction.jump_target = jump_target
            
        # ALU operations (including immediate)
        elif op:
            operand1 = instruction.src_values[0] if len(instruction.src_values) > 0 else 0
            
            if instruction.has_immediate:
                operand2 = instruction.immediate
            else:
                operand2 = instruction.src_values[1] if len(instruction.src_values) > 1 else 0
            
            result = EXE.execute(op, operand1, operand2)
        
        return result, mem_address
