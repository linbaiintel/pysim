"""ALU (Arithmetic Logic Unit) for RISC-V pipeline simulator"""


class ALU:
    """Arithmetic Logic Unit for executing operations"""
    @staticmethod
    def execute(operation, operand1, operand2):
        """Execute ALU operation"""
        op = operation.upper()
        if op == 'ADD':
            return operand1 + operand2
        elif op == 'SUB':
            return operand1 - operand2
        elif op == 'AND':
            return operand1 & operand2
        elif op == 'OR':
            return operand1 | operand2
        elif op == 'XOR':
            return operand1 ^ operand2
        elif op == 'SLT':  # Set Less Than
            return 1 if operand1 < operand2 else 0
        else:
            return 0
