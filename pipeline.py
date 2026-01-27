# write a 5 stage pipeline module for risc-v architecture with time-stepped simulation using SimPy
import simpy

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
        print(f"[Cycle {self.env.now}] {self.name} stage processing: {instruction}")
        yield self.env.timeout(self.latency)
        print(f"[Cycle {self.env.now}] {self.name} stage completed: {instruction}")
        return instruction


# Define the 5 stages of the pipeline
class FetchStage(PipelineStage):
    def __init__(self, env):
        super().__init__(env, "Fetch", latency=1)
    
    def process(self, instruction):
        """Simulate fetching instruction from memory"""
        yield from super().process(instruction)
        return f"Fetched[{instruction}]"


class DecodeStage(PipelineStage):
    def __init__(self, env):
        super().__init__(env, "Decode", latency=1)
    
    def process(self, instruction):
        """Simulate decoding instruction"""
        yield from super().process(instruction)
        return f"Decoded[{instruction}]"


class ExecuteStage(PipelineStage):
    def __init__(self, env):
        super().__init__(env, "Execute", latency=1)
    
    def process(self, instruction):
        """Simulate executing instruction"""
        yield from super().process(instruction)
        return f"Executed[{instruction}]"


class MemoryStage(PipelineStage):
    def __init__(self, env):
        super().__init__(env, "Memory", latency=1)
    
    def process(self, instruction):
        """Simulate memory access"""
        yield from super().process(instruction)
        return f"Memory[{instruction}]"


class WriteBackStage(PipelineStage):
    def __init__(self, env):
        super().__init__(env, "WriteBack", latency=1)
    
    def process(self, instruction):
        """Simulate writing back to register"""
        yield from super().process(instruction)
        return f"WriteBack[{instruction}]"


class Pipeline:
    def __init__(self, env):
        self.env = env
        self.fetch = FetchStage(env)
        self.decode = DecodeStage(env)
        self.execute = ExecuteStage(env)
        self.memory = MemoryStage(env)
        self.write_back = WriteBackStage(env)
        
        # Create buffers between stages
        self.fetch_to_decode = simpy.Store(env)
        self.decode_to_execute = simpy.Store(env)
        self.execute_to_memory = simpy.Store(env)
        self.memory_to_writeback = simpy.Store(env)
        
        self.completed_instructions = []

    def stage_runner(self, stage, input_buffer, output_buffer):
        """Run a stage continuously, processing instructions from input buffer"""
        while True:
            instruction = yield input_buffer.get()
            processed = yield self.env.process(stage.process(instruction))
            if output_buffer is not None:
                yield output_buffer.put(processed)
            else:
                # Last stage - store completed instruction
                self.completed_instructions.append(processed)

    def instruction_feeder(self, instructions):
        """Feed instructions into the pipeline at specified intervals"""
        for i, instruction in enumerate(instructions):
            print(f"\n[Cycle {self.env.now}] Injecting instruction: {instruction}")
            yield self.fetch_to_decode.put(instruction)
            yield self.env.timeout(1)  # Issue new instruction every cycle

    def run(self, instructions):
        """Run the pipeline with a list of instructions"""
        # Start all pipeline stages
        self.env.process(self.stage_runner(self.fetch, self.fetch_to_decode, self.decode_to_execute))
        self.env.process(self.stage_runner(self.decode, self.decode_to_execute, self.execute_to_memory))
        self.env.process(self.stage_runner(self.execute, self.execute_to_memory, self.memory_to_writeback))
        self.env.process(self.stage_runner(self.memory, self.memory_to_writeback, None))
        
        # Actually the writeback stage is handled in memory_to_writeback -> None
        # Let's fix this
        self.env.process(self.stage_runner(self.write_back, self.memory_to_writeback, None))
        
        # Feed instructions
        self.env.process(self.instruction_feeder(instructions))
        
        # Run simulation for enough time to complete all instructions
        # Each instruction takes 5 cycles, plus we need extra time for the last instruction
        total_cycles = len(instructions) + 5
        self.env.run(until=total_cycles)
        
        return self.completed_instructions


if __name__ == "__main__":
    print("=== RISC-V 5-Stage Pipeline Simulator ===\n")
    
    # Create SimPy environment
    env = simpy.Environment()
    
    # Create pipeline
    pipeline = Pipeline(env)
    
    # Test with multiple instructions
    instructions = [
        "ADD R1, R2, R3",
        "SUB R4, R5, R6",
        "LOAD R7, 100(R8)",
        "STORE R9, 200(R10)"
    ]
    
    results = pipeline.run(instructions)
    
    print("\n=== Pipeline Execution Complete ===")
    print(f"Total instructions completed: {len(results)}")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result}")