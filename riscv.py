"""RISC-V Processor - Assembles all components into a complete processor"""
import simpy
from register_file import RegisterFile
from memory import Memory
from exe import EXE
from pipeline import Pipeline


class RISCVProcessor:
    """Complete RISC-V processor with pipeline, register file, memory, and ALU"""
    
    def __init__(self, enable_forwarding=False):
        """
        Initialize the RISC-V processor
        
        Args:
            enable_forwarding: Enable data forwarding (not yet implemented)
        """
        self.env = simpy.Environment()
        self.pipeline = Pipeline(self.env, enable_forwarding)
        
        # Direct access to hardware components
        self.register_file = self.pipeline.register_file
        self.memory = self.pipeline.memory
        self.exe = self.pipeline.exe
    
    def initialize_registers(self, register_values):
        """
        Initialize registers with specific values
        
        Args:
            register_values: Dictionary of {register_name: value}
        """
        for reg, value in register_values.items():
            self.register_file.write(reg, value)
    
    def initialize_memory(self, memory_data):
        """
        Initialize memory with specific data
        
        Args:
            memory_data: Dictionary of {address: value}
        """
        for addr, value in memory_data.items():
            self.memory.write(addr, value)
    
    def execute(self, instructions, verbose=True):
        """
        Execute a program (list of instructions)
        
        Args:
            instructions: List of instruction strings
            verbose: Print execution trace
            
        Returns:
            Dictionary with execution results
        """
        if not verbose:
            # Suppress output by temporarily redirecting
            import sys
            from io import StringIO
            old_stdout = sys.stdout
            sys.stdout = StringIO()
        
        try:
            results = self.pipeline.run(instructions)
            
            execution_info = {
                'completed_instructions': results,
                'total_cycles': self.env.now,
                'stall_count': self.pipeline.stall_count,
                'bubble_count': self.pipeline.bubble_count,
                'cpi': self.env.now / len(results) if results else 0,
                'ipc': len(results) / self.env.now if self.env.now > 0 else 0,
            }
            
            return execution_info
        finally:
            if not verbose:
                sys.stdout = old_stdout
    
    def get_register(self, reg_name):
        """Get value of a specific register"""
        return self.register_file.read(reg_name)
    
    def get_memory(self, address):
        """Get value at a specific memory address"""
        return self.memory.read(address)
    
    def get_register_state(self):
        """Get all non-zero registers"""
        return {k: v for k, v in self.register_file.registers.items() if v != 0}
    
    def get_memory_state(self):
        """Get all memory contents"""
        return dict(self.memory.data)
    
    def reset(self):
        """Reset the processor to initial state"""
        self.env = simpy.Environment()
        self.pipeline = Pipeline(self.env)
        self.register_file = self.pipeline.register_file
        self.memory = self.pipeline.memory
        self.alu = self.pipeline.alu


def run_program(instructions, initial_registers=None, initial_memory=None, verbose=True):
    """
    Convenience function to run a program on a fresh processor
    
    Args:
        instructions: List of instruction strings
        initial_registers: Optional dict of {register: value} for initialization
        initial_memory: Optional dict of {address: value} for initialization
        verbose: Print execution trace
        
    Returns:
        Tuple of (execution_info, final_register_state, final_memory_state)
    """
    processor = RISCVProcessor()
    
    # Initialize if provided
    if initial_registers:
        processor.initialize_registers(initial_registers)
    if initial_memory:
        processor.initialize_memory(initial_memory)
    
    # Execute program
    exec_info = processor.execute(instructions, verbose)
    
    # Get final state
    final_regs = processor.get_register_state()
    final_mem = processor.get_memory_state()
    
    return exec_info, final_regs, final_mem


if __name__ == "__main__":
    print("=== RISC-V Processor Example ===\n")
    
    # Example 1: Simple arithmetic program
    print("Example 1: Arithmetic Operations")
    print("-" * 60)
    
    program1 = [
        "ADD R1, R2, R3",    # R1 = 10 + 20 = 30
        "SUB R4, R1, R5",    # R4 = 30 - 5 = 25 (RAW on R1)
        "AND R6, R4, R8",    # R6 = 25 & 15 = 9 (RAW on R4)
    ]
    
    # Initialize registers for the program
    initial_regs = {
        'R2': 10,
        'R3': 20,
        'R5': 5,
        'R8': 15
    }
    
    exec_info, regs, mem = run_program(program1, initial_registers=initial_regs, verbose=True)
    
    print("\n=== Execution Summary ===")
    print(f"Total Cycles: {exec_info['total_cycles']}")
    print(f"Instructions: {len(exec_info['completed_instructions'])}")
    print(f"Stalls: {exec_info['stall_count']}")
    print(f"CPI: {exec_info['cpi']:.2f}")
    print(f"IPC: {exec_info['ipc']:.2f}")
    print(f"Final Registers: {regs}")
    
    # Example 2: Memory operations
    print("\n\n" + "=" * 60)
    print("Example 2: Memory Operations")
    print("-" * 60)
    
    processor = RISCVProcessor()
    processor.initialize_registers({'R3': 20})
    processor.initialize_memory({100: 42, 200: 99})
    
    program2 = [
        "LOAD R1, 100(R0)",   # Load value from memory[100] into R1
        "ADD R2, R1, R3",     # R2 = R1 + 20 (RAW on R1)
        "STORE R2, 200(R0)",  # Store R2 to memory[200]
    ]
    
    exec_info = processor.execute(program2, verbose=True)
    
    print("\n=== Execution Summary ===")
    print(f"Total Cycles: {exec_info['total_cycles']}")
    print(f"Stalls: {exec_info['stall_count']}")
    print(f"Final R1: {processor.get_register('R1')}")
    print(f"Final R2: {processor.get_register('R2')}")
    print(f"Memory[200]: {processor.get_memory(200)}")
    
    # Example 3: Independent instructions (no stalls)
    print("\n\n" + "=" * 60)
    print("Example 3: Parallel Execution (No Dependencies)")
    print("-" * 60)
    
    program3 = [
        "ADD R1, R2, R3",
        "SUB R4, R5, R6",
        "OR R7, R8, R9",
        "AND R10, R11, R12",
    ]
    
    # Initialize registers for independent operations
    initial_regs3 = {
        'R2': 10, 'R3': 20,
        'R5': 5, 'R6': 3,
        'R8': 15, 'R9': 7,
        'R11': 8, 'R12': 4
    }
    
    exec_info, regs, mem = run_program(program3, initial_registers=initial_regs3, verbose=True)
    
    print("\n=== Execution Summary ===")
    print(f"Total Cycles: {exec_info['total_cycles']}")
    print(f"Stalls: {exec_info['stall_count']} (should be 0)")
    print(f"CPI: {exec_info['cpi']:.2f}")
