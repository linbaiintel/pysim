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
        if op in ['LOAD', 'STORE', 'LW', 'LH', 'LB', 'LBU', 'LHU', 'SW', 'SH', 'SB']:
            base_value = instruction.src_values[0] if instruction.src_values else 0
            mem_address = EXE.calculate_memory_address(base_value, instruction.offset)
            
        # Upper immediate instructions
        elif op == 'LUI':
            result = EXE.execute_lui(instruction.immediate)
            
        elif op == 'AUIPC':
            result = EXE.execute_auipc(instruction.immediate, pc)
            
        # Branch instructions
        elif op in ['BEQ', 'BNE', 'BLT', 'BGE', 'BLTU', 'BGEU']:
            val1 = instruction.src_values[0] if len(instruction.src_values) > 0 else 0
            val2 = instruction.src_values[1] if len(instruction.src_values) > 1 else 0
            branch_taken = EXE.evaluate_branch(op, val1, val2)
            result = 1 if branch_taken else 0
            
        # Jump instructions
        elif op in ['JAL', 'JALR']:
            result = 0  # Would store return address (needs PC tracking)
            
        # ALU operations (including immediate)
        elif op:
            operand1 = instruction.src_values[0] if len(instruction.src_values) > 0 else 0
            
            if instruction.has_immediate:
                operand2 = instruction.immediate
            else:
                operand2 = instruction.src_values[1] if len(instruction.src_values) > 1 else 0
            
            result = EXE.execute(op, operand1, operand2)
        
        return result, mem_address
