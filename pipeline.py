# write a 5 stage pipeline module for risc-v architecture with time-stepped simulation using SimPy
import simpy
from register_file import RegisterFile
from memory import Memory
from exe import EXE
from instruction import Instruction


class PipelineStage:
    def __init__(self, env, name, latency=1):
        self.env = env
        self.name = name
        self.latency = latency  # number of cycles this stage takes
        self.current_instruction = None
        self.pipe = simpy.Store(env)  # buffer to hold instruction between stages
        
    def process(self, instruction):
        """Process instruction for this stage's latency"""
        self.current_instruction = instruction
        if not instruction.is_bubble:
            print(f"[Cycle {self.env.now}] {self.name} stage processing: {instruction}")
        yield self.env.timeout(self.latency)
        if not instruction.is_bubble:
            print(f"[Cycle {self.env.now}] {self.name} stage completed: {instruction}")
        return instruction


# Define the 5 stages of the pipeline
class FetchStage(PipelineStage):
    def __init__(self, env):
        super().__init__(env, "Fetch", latency=1)
    
    def process(self, instruction):
        """Simulate fetching instruction from memory"""
        yield from super().process(instruction)
        return instruction


class DecodeStage(PipelineStage):
    def __init__(self, env, register_file):
        super().__init__(env, "Decode", latency=1)
        self.register_file = register_file
    
    def process(self, instruction):
        """Simulate decoding instruction and reading registers"""
        yield from super().process(instruction)
        
        # Read source register values
        if not instruction.is_bubble:
            instruction.src_values = [self.register_file.read(reg) for reg in instruction.src_regs]
            if instruction.src_values:
                print(f"  -> Read registers: {dict(zip(instruction.src_regs, instruction.src_values))}")
        
        return instruction


class ExecuteStage(PipelineStage):
    def __init__(self, env, exe, register_file):
        super().__init__(env, "Execute", latency=1)
        self.exe = exe
        self.register_file = register_file
    
    def process(self, instruction):
        """Simulate executing instruction"""
        yield from super().process(instruction)
        
        # Delegate execution to EXE
        if not instruction.is_bubble:
            op = instruction.operation
            
            # Execute instruction through EXE
            # Get current PC for AUIPC instruction
            current_pc = self.register_file.read_pc()
            result, mem_address = self.exe.execute_instruction(instruction, current_pc)
            
            # Store results in instruction
            if mem_address is not None:
                instruction.mem_address = mem_address
                print(f"  -> Calculated address: {instruction.mem_address}")
            
            if result is not None:
                instruction.result = result
                
                # Print appropriate message based on operation type
                if op == 'LUI':
                    print(f"  -> LUI result: {result:#010x}")
                elif op == 'AUIPC':
                    print(f"  -> AUIPC result: PC({current_pc:#010x}) + {instruction.immediate:#010x} = {result:#010x}")
                elif op in ['BEQ', 'BNE', 'BLT', 'BGE', 'BLTU', 'BGEU']:
                    branch_taken = (result == 1)
                    print(f"  -> Branch {op}: {'TAKEN' if branch_taken else 'NOT TAKEN'} (PC update not implemented)")
                elif op in ['JAL', 'JALR']:
                    print(f"  -> {op}: Jump instruction (PC update not implemented)")
                else:
                    print(f"  -> EXE result: {result}")
        
        return instruction


class MemoryStage(PipelineStage):
    def __init__(self, env, memory):
        super().__init__(env, "Memory", latency=1)
        self.memory = memory
    
    def process(self, instruction):
        """Simulate memory access"""
        yield from super().process(instruction)
        
        # Perform memory operation
        if not instruction.is_bubble and instruction.mem_address is not None:
            op = instruction.operation
            
            # LOAD operations
            if op == 'LW' or op == 'LOAD':
                # Load Word (32-bit)
                instruction.result = self.memory.read_word(instruction.mem_address)
                print(f"  -> LW: Loaded word {instruction.result:#010x} from address {instruction.mem_address:#x}")
                
            elif op == 'LH':
                # Load Halfword (16-bit, sign-extended)
                instruction.result = self.memory.read_halfword(instruction.mem_address, signed=True)
                print(f"  -> LH: Loaded halfword {instruction.result:#010x} from address {instruction.mem_address:#x}")
                
            elif op == 'LHU':
                # Load Halfword Unsigned (16-bit, zero-extended)
                instruction.result = self.memory.read_halfword(instruction.mem_address, signed=False)
                print(f"  -> LHU: Loaded halfword unsigned {instruction.result:#010x} from address {instruction.mem_address:#x}")
                
            elif op == 'LB':
                # Load Byte (8-bit, sign-extended)
                instruction.result = self.memory.read_byte(instruction.mem_address, signed=True)
                print(f"  -> LB: Loaded byte {instruction.result:#010x} from address {instruction.mem_address:#x}")
                
            elif op == 'LBU':
                # Load Byte Unsigned (8-bit, zero-extended)
                instruction.result = self.memory.read_byte(instruction.mem_address, signed=False)
                print(f"  -> LBU: Loaded byte unsigned {instruction.result:#010x} from address {instruction.mem_address:#x}")
            
            # STORE operations
            elif op == 'SW' or op == 'STORE':
                # Store Word (32-bit)
                store_value = instruction.src_values[0] if instruction.src_values else 0
                self.memory.write_word(instruction.mem_address, store_value)
                print(f"  -> SW: Stored word {store_value:#010x} to address {instruction.mem_address:#x}")
                
            elif op == 'SH':
                # Store Halfword (16-bit)
                store_value = instruction.src_values[0] if instruction.src_values else 0
                self.memory.write_halfword(instruction.mem_address, store_value & 0xFFFF)
                print(f"  -> SH: Stored halfword {store_value & 0xFFFF:#06x} to address {instruction.mem_address:#x}")
                
            elif op == 'SB':
                # Store Byte (8-bit)
                store_value = instruction.src_values[0] if instruction.src_values else 0
                self.memory.write_byte(instruction.mem_address, store_value & 0xFF)
                print(f"  -> SB: Stored byte {store_value & 0xFF:#04x} to address {instruction.mem_address:#x}")
        
        return instruction


class WriteBackStage(PipelineStage):
    def __init__(self, env, register_file):
        super().__init__(env, "WriteBack", latency=1)
        self.register_file = register_file
    
    def process(self, instruction):
        """Simulate writing back to register"""
        yield from super().process(instruction)
        
        # Write result to register file
        if not instruction.is_bubble and instruction.dest_reg and instruction.result is not None:
            self.register_file.write(instruction.dest_reg, instruction.result)
            print(f"  -> Wrote {instruction.result} to {instruction.dest_reg}")
        
        return instruction


class Pipeline:
    def __init__(self, env, enable_forwarding=False):
        self.env = env
        self.enable_forwarding = enable_forwarding
        
        # Create hardware components
        self.register_file = RegisterFile()
        self.memory = Memory()
        self.exe = EXE()
        
        # Create pipeline stages with hardware components
        self.fetch = FetchStage(env)
        self.decode = DecodeStage(env, self.register_file)
        self.execute = ExecuteStage(env, self.exe, self.register_file)
        self.memory_stage = MemoryStage(env, self.memory)
        self.write_back = WriteBackStage(env, self.register_file)
        
        # Create buffers between stages
        self.fetch_to_decode = simpy.Store(env)
        self.decode_to_execute = simpy.Store(env)
        self.execute_to_memory = simpy.Store(env)
        self.memory_to_writeback = simpy.Store(env)
        self.writeback_output = simpy.Store(env)  # Optional: for tracking completed instructions
        
        self.completed_instructions = []
        self.stall_count = 0
        self.bubble_count = 0
        self.completion_time = 0  # Track when last instruction completes
        
        # Track instructions currently in pipeline stages (for hazard detection)
        self.pipeline_state = {
            'execute': None,
            'memory': None,
            'writeback': None
        }

    def check_hazard(self, instruction):
        """Check for RAW, WAR, WAW hazards"""
        if instruction.is_bubble:
            return False
        
        # RAW (Read After Write) - True dependency
        # Check if any source register is being written by instructions in EX or MEM stages
        # We DON'T check WriteBack stage because by then the value is available
        for src_reg in instruction.src_regs:
            # Check Execute stage
            if self.pipeline_state['execute'] and not self.pipeline_state['execute'].is_bubble:
                if self.pipeline_state['execute'].dest_reg == src_reg:
                    print(f"[Cycle {self.env.now}] RAW Hazard detected: {instruction.text} needs {src_reg} from {self.pipeline_state['execute'].text}")
                    return True
            
            # Check Memory stage
            if self.pipeline_state['memory'] and not self.pipeline_state['memory'].is_bubble:
                if self.pipeline_state['memory'].dest_reg == src_reg:
                    print(f"[Cycle {self.env.now}] RAW Hazard detected: {instruction.text} needs {src_reg} from {self.pipeline_state['memory'].text}")
                    return True
            
            # WriteBack stage: No stall needed - value is being written back and available
        
        # WAW (Write After Write) - Not a real hazard in in-order pipelines
        # In-order execution ensures later instructions write after earlier ones
        # Only relevant for out-of-order or superscalar processors
        
        # WAR (Write After Read) - Not a real hazard in in-order pipelines
        # In-order execution with register reads in Decode means earlier instructions
        # always read before later instructions write
        
        return False

    def stage_runner(self, stage, input_buffer, output_buffer, stage_name=None):
        """Run a stage continuously, processing instructions from input buffer"""
        while True:
            instruction = yield input_buffer.get()
            
            # Update pipeline state IMMEDIATELY when entering stage
            if stage_name and stage_name != 'decode':
                self.pipeline_state[stage_name] = instruction
            
            # Special handling for Decode stage - check for hazards
            if stage_name == 'decode':
                # Small delay to ensure other stages have updated their pipeline state
                # This handles SimPy concurrent execution within the same cycle
                yield self.env.timeout(0)
                
                # Check for hazards before decoding
                while self.check_hazard(instruction):
                    # Insert bubble and stall
                    print(f"[Cycle {self.env.now}] STALL: Inserting bubble into Execute stage")
                    bubble = Instruction("BUBBLE")
                    self.stall_count += 1
                    self.bubble_count += 1
                    
                    # Send bubble to next stage
                    yield output_buffer.put(bubble)
                    yield self.env.timeout(1)
                    
                    # Keep checking hazard on same instruction
            
            # Now process the instruction
            processed = yield self.env.process(stage.process(instruction))
            
            # Send to output buffer
            if output_buffer is not None:
                yield output_buffer.put(processed)
            else:
                # Last stage - store completed instruction
                if not instruction.is_bubble:
                    self.completed_instructions.append(processed)
                    self.completion_time = self.env.now  # Track actual completion time
            
            # Clear pipeline state after instruction exits this stage
            if stage_name and stage_name != 'decode':
                self.pipeline_state[stage_name] = None

    def instruction_feeder(self, instructions):
        """Feed instructions into the pipeline"""
        instruction_queue = [Instruction(instr) for instr in instructions]
        
        for instruction in instruction_queue:
            print(f"\n[Cycle {self.env.now}] Fetching instruction: {instruction}")
            yield self.fetch_to_decode.put(instruction)
            yield self.env.timeout(1)

    def run(self, instructions):
        """Run the pipeline with a list of instructions"""
        # Start all pipeline stages with stage names for tracking
        # Format: stage_runner(stage, input_buffer, output_buffer, stage_name)
        # Pipeline flow: Fetch -> Decode -> Execute -> Memory -> WriteBack
        self.env.process(self.stage_runner(self.fetch, self.fetch_to_decode, self.decode_to_execute))
        self.env.process(self.stage_runner(self.decode, self.decode_to_execute, self.execute_to_memory, 'decode'))
        self.env.process(self.stage_runner(self.execute, self.execute_to_memory, self.memory_to_writeback, 'execute'))
        self.env.process(self.stage_runner(self.memory_stage, self.memory_to_writeback, self.writeback_output, 'memory'))
        self.env.process(self.stage_runner(self.write_back, self.writeback_output, None, 'writeback'))
        
        # Feed instructions
        self.env.process(self.instruction_feeder(instructions))
        
        # Run simulation for enough time to complete all instructions
        # Account for stalls - give extra cycles
        # Use more cycles to ensure deeply dependent instructions complete
        total_cycles = len(instructions) * 10 + 20
        self.env.run(until=total_cycles)
        
        return self.completed_instructions


if __name__ == "__main__":
    print("=== RISC-V 5-Stage Pipeline Simulator with Hazard Detection ===\n")
    
    # Test 1: RAW Hazard Example
    print("Test 1: RAW (Read After Write) Hazard")
    print("-" * 60)
    env = simpy.Environment()
    pipeline = Pipeline(env)
    
    # Initialize registers for test
    pipeline.register_file.write('R2', 10)
    pipeline.register_file.write('R3', 20)
    pipeline.register_file.write('R5', 5)
    pipeline.register_file.write('R7', 7)
    pipeline.register_file.write('R9', 9)
    
    instructions = [
        "ADD R1, R2, R3",      # R1 = R2 + R3
        "SUB R4, R1, R5",      # RAW: needs R1 from previous instruction
        "OR R6, R1, R7",       # RAW: needs R1 from first instruction
        "AND R8, R6, R9"       # RAW: needs R6 from previous instruction
    ]
    
    results = pipeline.run(instructions)
    
    print("\n=== Execution Complete ===")
    print(f"Instructions completed: {len(results)}")
    print(f"Stalls/Bubbles inserted: {pipeline.stall_count}")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result}")
    
    # Test 2: WAW Hazard
    print("\n\n" + "="*60)
    print("Test 2: WAW (Write After Write) Hazard")
    print("-" * 60)
    env2 = simpy.Environment()
    pipeline2 = Pipeline(env2)
    
    # Initialize registers and memory for test
    pipeline2.register_file.write('R2', 10)
    pipeline2.register_file.write('R3', 20)
    pipeline2.register_file.write('R4', 15)
    pipeline2.register_file.write('R5', 5)
    pipeline2.register_file.write('R7', 100)
    pipeline2.memory.write(100, 42)
    pipeline2.memory.write(200, 99)
    
    instructions2 = [
        "ADD R1, R2, R3",      # R1 = R2 + R3
        "SUB R1, R4, R5",      # WAW: both write to R1
        "LOAD R6, 100(R1)",    # RAW: needs R1
        "STORE R6, 200(R7)"    # RAW: needs R6 from LOAD
    ]
    
    results2 = pipeline2.run(instructions2)
    
    print("\n=== Execution Complete ===")
    print(f"Instructions completed: {len(results2)}")
    print(f"Stalls/Bubbles inserted: {pipeline2.stall_count}")
    for i, result in enumerate(results2, 1):
        print(f"  {i}. {result}")
    
    # Test 3: No Hazards - Ideal Pipelining
    print("\n\n" + "="*60)
    print("Test 3: No Hazards - Full Pipeline Throughput")
    print("-" * 60)
    env3 = simpy.Environment()
    pipeline3 = Pipeline(env3)
    
    # Initialize registers for test
    pipeline3.register_file.write('R2', 10)
    pipeline3.register_file.write('R3', 20)
    pipeline3.register_file.write('R5', 5)
    pipeline3.register_file.write('R6', 3)
    pipeline3.register_file.write('R8', 15)
    pipeline3.register_file.write('R9', 7)
    pipeline3.register_file.write('R11', 8)
    pipeline3.register_file.write('R12', 4)
    
    instructions3 = [
        "ADD R1, R2, R3",      # No dependencies
        "SUB R4, R5, R6",      # No dependencies
        "OR R7, R8, R9",       # No dependencies
        "AND R10, R11, R12"    # No dependencies
    ]
    
    results3 = pipeline3.run(instructions3)
    
    print("\n=== Execution Complete ===")
    print(f"Instructions completed: {len(results3)}")
    print(f"Stalls/Bubbles inserted: {pipeline3.stall_count}")
    print("(No stalls expected - instructions are independent)")
    for i, result in enumerate(results3, 1):
        print(f"  {i}. {result}")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result}")


    # To visualize pipeline execution, use:
    # from tests.visualization import draw_pipeline_diagram
    # draw_pipeline_diagram(["ADD R1, R2, R3", "SUB R4, R1, R5"])
