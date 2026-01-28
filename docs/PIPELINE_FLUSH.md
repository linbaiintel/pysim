# Pipeline Flush Mechanism

## Overview
The pipeline flush mechanism handles control flow changes (jumps and branches) by canceling instructions that should not execute after a control flow transfer.

## When Flush Occurs

### Unconditional Jumps (Always Flush)
- **JAL** (Jump And Link) - Always flushes pipeline
- **JALR** (Jump And Link Register) - Always flushes pipeline

### Conditional Branches (Flush if Taken)
- **BEQ** - Flush if operands are equal
- **BNE** - Flush if operands are not equal
- **BLT** - Flush if first < second (signed)
- **BGE** - Flush if first >= second (signed)
- **BLTU** - Flush if first < second (unsigned)
- **BGEU** - Flush if first >= second (unsigned)

## How It Works

### 1. Detection Phase (Execute Stage)
```
Execute Stage completes instruction
  ↓
Is it JAL/JALR? → YES → Trigger flush with jump_target
  ↓ NO
Is it a branch? → YES → Branch taken? → YES → Trigger flush with branch_target
  ↓ NO                       ↓ NO
Continue normally          Continue normally
```

### 2. Flush Propagation
```
[Cycle N] Execute completes JAL/JALR or taken branch
         → flush_signal = True
         → flush_target_pc = calculated target
         → flush_count++

[Cycle N+1] Decode stage checks flush_signal
           → Converts current instruction to BUBBLE
           → Instruction does not execute

[Cycle N+2] Memory stage clears flush_signal
           → Normal operation resumes
```

### 3. Stage-Specific Behavior

| Stage | Behavior During Flush |
|-------|----------------------|
| **Fetch** | Not affected (instruction already fetched) |
| **Decode** | Converts instruction to bubble if flush_signal is true |
| **Execute** | Instruction continues (too late to cancel) |
| **Memory** | Instruction continues, clears flush_signal after completion |
| **WriteBack** | Instruction continues |

## Implementation Details

### Pipeline Class Additions
```python
class Pipeline:
    def __init__(self, env):
        # ... existing code ...
        self.flush_count = 0          # Track number of flushes
        self.flush_signal = False     # Flag to trigger flush
        self.flush_target_pc = None   # New PC after jump/branch
```

### Flush Trigger Method
```python
def trigger_flush(self, target_pc):
    """Trigger a pipeline flush and set new PC target"""
    self.flush_signal = True
    self.flush_target_pc = target_pc
    self.flush_count += 1
```

### Stage Runner Modifications
```python
def stage_runner(self, stage, input_buffer, output_buffer, stage_name=None):
    while True:
        instruction = yield input_buffer.get()
        
        # Check for flush in Decode stage
        if self.flush_signal and stage_name == 'decode':
            # Convert to bubble
            instruction = Instruction("BUBBLE")
        
        # ... process instruction ...
        
        # After Execute, check if flush should be triggered
        if stage_name == 'execute' and not instruction.is_bubble:
            if instruction.is_jump and instruction.jump_target:
                self.trigger_flush(instruction.jump_target)
            elif is_taken_branch(instruction):
                self.trigger_flush(instruction.jump_target)
        
        # Clear flush signal after Memory stage
        if stage_name == 'memory' and self.flush_signal:
            self.flush_signal = False
```

## Performance Impact

### Flush Cost
Each flush causes **1-2 bubble cycles** in the pipeline:
- 1 bubble from Decode stage conversion
- Additional bubbles if multiple instructions in flight

### Example: JAL Performance
```
Without Flush:
  JAL:  Fetch → Decode → Execute → Memory → WriteBack
  ADD:  -----   Fetch  → Decode  → Execute → Memory → WriteBack (WRONG!)
  
With Flush:
  JAL:  Fetch → Decode → Execute → Memory → WriteBack
  ADD:  -----   Fetch  → BUBBLE  → -------   -------  → ------- (CORRECT!)
```

Cost: 1 extra cycle per jump/taken branch

## Test Coverage

### Basic Flush Tests ([test_flush.py](../tests/functional_tests/test_flush.py))
1. **test_jal_triggers_flush** - Verify JAL causes flush
2. **test_jalr_triggers_flush** - Verify JALR causes flush
3. **test_taken_branch_triggers_flush** - Verify taken branch causes flush
4. **test_not_taken_branch_no_flush** - Verify not-taken branch doesn't flush
5. **test_bne_taken_triggers_flush** - Verify BNE flush behavior
6. **test_blt_taken_triggers_flush** - Verify BLT flush behavior
7. **test_flush_converts_to_bubbles** - Verify instructions become bubbles
8. **test_multiple_jumps_multiple_flushes** - Multiple flush tracking
9. **test_flush_target_pc_set** - Verify target PC calculation

All 9 tests passing ✓

### Integration Tests
Jump and branch tests updated to account for flush behavior:
- test_function_call_pattern
- test_multiple_jal_instructions
- test_jal_then_other_instruction

Total: **109 tests passing** (100 original + 9 new flush tests)

## Demo Program

Run interactive demo:
```bash
python3 sandbox/demo_flush.py
```

Shows:
1. JAL triggering flush
2. Taken branch triggering flush  
3. Not-taken branch (no flush)
4. JALR triggering flush

## Limitations

### What's NOT Flushed
Instructions already in **Execute, Memory, or WriteBack** stages cannot be flushed because:
- Execute: Instruction has already computed results
- Memory: Memory access may have side effects
- WriteBack: Register write is about to occur

This matches real hardware - once an instruction reaches Execute, it's typically committed.

### PC Update Not Implemented
While flush prevents wrong instructions from executing, the Fetch stage doesn't actually restart from the jump target. This would require:
1. Fetch stage to receive flush_target_pc
2. Instruction feeder to jump to new location
3. Proper PC tracking per instruction

### Branch Prediction
Current implementation: **Always fetch sequential instructions**
- No branch prediction (always predict not-taken)
- Every taken branch/jump causes flush (1-2 cycle penalty)
- Real processors use branch predictors to reduce flush frequency

## Comparison to Real Processors

| Feature | This Implementation | Real RISC-V Core |
|---------|-------------------|------------------|
| Flush detection | Execute stage | Execute or later |
| Flush latency | 1-2 cycles | 1-3 cycles (varies) |
| Flush coverage | Decode only | All early stages |
| Branch prediction | None (always sequential) | Dynamic predictors |
| PC update | Not implemented | Immediate |
| Return address stack | None | Often included |

## Future Enhancements

1. **Full Pipeline Flush**: Flush Fetch stage as well
2. **PC Update**: Actually restart fetch from target
3. **Branch Prediction**: Predict branch direction to reduce flushes
4. **Branch Target Buffer**: Cache jump/branch targets
5. **Return Address Stack**: Optimize function returns
6. **Speculative Execution**: Execute both paths, discard wrong one

## Related Files

- **pipeline.py** - Core flush implementation
- **tests/functional_tests/test_flush.py** - Flush mechanism tests
- **sandbox/demo_flush.py** - Interactive demonstration
- **exe.py** - Jump target calculation
- **instruction.py** - Jump target storage

## Metrics

Track flush behavior in your programs:
```python
processor = RISCVProcessor()
info = processor.execute(program)

print(f"Flushes: {processor.pipeline.flush_count}")
print(f"Stalls: {processor.pipeline.stall_count}")
print(f"Total cycles: {info['total_cycles']}")
```

Analyze control flow overhead:
```python
flush_overhead = processor.pipeline.flush_count * 1.5  # avg 1.5 cycles per flush
control_flow_penalty = (flush_overhead / info['total_cycles']) * 100
print(f"Control flow penalty: {control_flow_penalty:.1f}%")
```
