#!/usr/bin/env python3
"""
Visualization and analysis utilities for pipeline testing.
Can be imported by test files or run standalone.
"""

import sys
import os
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import simpy
from pipeline import Pipeline
import re


def draw_pipeline_diagram(instructions):
    """
    Draw a pipeline execution diagram showing stage occupancy over time.
    
    Args:
        instructions: List of instruction strings
        
    Example output:
              | t0 | t1 | t2  | t3  | t4  | t5  | t6 |
        Inst1 | IF | ID | EXE | MEM | WB  |     |    |
        Inst2 |    | IF | ID  | EXE | MEM | WB  |    |
    """
    # Capture pipeline output
    import sys
    from io import StringIO
    
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    env = simpy.Environment()
    pipeline = Pipeline(env)
    results = pipeline.run(instructions)
    
    output = sys.stdout.getvalue()
    sys.stdout = old_stdout
    
    # Parse the output to track stage occupancy
    stage_map = {
        'Fetch': 'IF',
        'Decode': 'ID',
        'Execute': 'EXE',
        'Memory': 'MEM',
        'WriteBack': 'WB'
    }
    
    # Build timeline: timeline[cycle][instruction_text] = stage
    timeline = {}
    
    for line in output.split('\n'):
        if 'processing:' in line:
            # Parse: [Cycle X] Stage processing: instruction
            match = re.match(r'\[Cycle (\d+)\] (\w+) stage processing: (.+)', line)
            if match:
                cycle = int(match.group(1))
                stage = match.group(2)
                inst_text = match.group(3)
                
                if inst_text != 'BUBBLE':
                    if cycle not in timeline:
                        timeline[cycle] = {}
                    timeline[cycle][inst_text] = stage_map.get(stage, stage)
    
    # Build the diagram
    max_cycle = max(timeline.keys()) if timeline else 0
    
    # Print header
    print("\nPipeline Execution Diagram:")
    print("=" * (11 + (max_cycle + 1) * 6))
    
    header = "          "
    for t in range(max_cycle + 1):
        header += f"| t{t:<2} "
    print(header + "|")
    print("-" * (11 + (max_cycle + 1) * 6))
    
    # Print each instruction's timeline
    for idx, inst in enumerate(instructions, 1):
        row = f"Inst {idx:<4} "
        for cycle in range(max_cycle + 1):
            if cycle in timeline and inst in timeline[cycle]:
                stage = timeline[cycle][inst]
                row += f"| {stage:<3} "
            else:
                row += "|     "
        print(row + "|")
    
    print("=" * (11 + (max_cycle + 1) * 6))
    print(f"\nLegend: IF=Fetch, ID=Decode, EXE=Execute, MEM=Memory, WB=WriteBack")
    print(f"Total cycles: {max_cycle + 1}, Stalls: {pipeline.stall_count}")
    
    return timeline


def visualize_pipeline_execution(instructions, show_details=True):
    """
    Create a visual summary of pipeline execution.
    
    Args:
        instructions: List of instruction strings
        show_details: Whether to print detailed output
        
    Returns:
        Dictionary with execution metrics
    """
    env = simpy.Environment()
    pipeline = Pipeline(env)
    results = pipeline.run(instructions)
    
    metrics = {
        'total_cycles': env.now,
        'instructions_completed': len(results),
        'stalls_inserted': pipeline.stall_count,
        'cpi': env.now / len(results) if results else 0,
        'ipc': len(results) / env.now if env.now > 0 else 0,
    }
    
    if show_details:
        print("\n" + "="*80)
        print("PIPELINE EXECUTION SUMMARY")
        print("="*80)
        print(f"Instructions: {instructions}")
        print("-"*80)
        print(f"  Total cycles: {metrics['total_cycles']}")
        print(f"  Instructions completed: {metrics['instructions_completed']}")
        print(f"  Stalls inserted: {metrics['stalls_inserted']}")
        print(f"  CPI (Cycles Per Instruction): {metrics['cpi']:.2f}")
        print(f"  IPC (Instructions Per Cycle): {metrics['ipc']:.2f}")
        print("="*80)
    
    return metrics


def compare_instruction_sequences(sequences):
    """
    Compare multiple instruction sequences.
    
    Args:
        sequences: List of (name, instructions) tuples
        
    Returns:
        List of metric dictionaries
    """
    print("\n" + "="*80)
    print("PIPELINE COMPARISON")
    print("="*80)
    print("\n{:30s} {:>8s} {:>8s} {:>8s} {:>6s}".format(
        "Sequence", "Instrs", "Cycles", "Stalls", "CPI"
    ))
    print("-" * 80)
    
    results = []
    for name, instructions in sequences:
        env = simpy.Environment()
        pipeline = Pipeline(env)
        pipeline.run(instructions)
        
        metrics = {
            'name': name,
            'instructions': len(instructions),
            'cycles': env.now,
            'stalls': pipeline.stall_count,
            'cpi': env.now / len(instructions) if instructions else 0
        }
        results.append(metrics)
        
        print("{:30s} {:>8d} {:>8d} {:>8d} {:>6.2f}".format(
            name, metrics['instructions'], metrics['cycles'], 
            metrics['stalls'], metrics['cpi']
        ))
    
    print("-" * 80)
    return results


def verify_instruction_order(instructions):
    """
    Verify that instructions complete in program order.
    
    Args:
        instructions: List of instruction strings
        
    Returns:
        True if order is correct, False otherwise
    """
    env = simpy.Environment()
    pipeline = Pipeline(env)
    results = pipeline.run(instructions)
    
    # Verify order
    match = all(str(r) == i for r, i in zip(results, instructions))
    
    return match


def calculate_expected_performance(instructions):
    """
    Calculate theoretical best-case performance.
    
    Args:
        instructions: List of instruction strings
        
    Returns:
        Dictionary with expected metrics
    """
    # Ideal pipeline: 4 cycles to fill + 1 cycle per instruction after first
    ideal_cycles = 4 + len(instructions)
    ideal_cpi = ideal_cycles / len(instructions) if instructions else 0
    
    return {
        'ideal_cycles': ideal_cycles,
        'ideal_cpi': ideal_cpi,
        'ideal_ipc': 1.0,  # Maximum throughput
    }


if __name__ == "__main__":
    # Example 1: Pipeline diagram for independent instructions
    print("\n" + "="*80)
    print("Example 1: Independent instructions (no hazards)")
    print("="*80)
    draw_pipeline_diagram([
        "ADD R1, R2, R3",
        "SUB R4, R5, R6",
        "OR R7, R8, R9"
    ])
    
    # Example 2: Pipeline diagram with RAW hazard
    print("\n" + "="*80)
    print("Example 2: Back-to-back dependency (RAW hazard)")
    print("="*80)
    draw_pipeline_diagram([
        "ADD R1, R2, R3",
        "SUB R4, R1, R5"
    ])
    
    # Example 3: LOAD-use hazard
    print("\n" + "="*80)
    print("Example 3: LOAD-use hazard")
    print("="*80)
    draw_pipeline_diagram([
        "LOAD R1, 100(R2)",
        "ADD R3, R1, R4"
    ])
    
    # Example 4: Multiple dependencies
    print("\n" + "="*80)
    print("Example 4: Chain of dependencies")
    print("="*80)
    draw_pipeline_diagram([
        "ADD R1, R2, R3",
        "ADD R4, R1, R5",
        "ADD R6, R4, R7"
    ])
    
    # Performance comparison
    print("\n" + "="*80)
    print("Performance Comparison")
    print("="*80)
    sequences = [
        ("No dependencies", [
            "ADD R1, R2, R3",
            "SUB R4, R5, R6",
            "OR R7, R8, R9",
        ]),
        ("Linear dependencies", [
            "ADD R1, R2, R3",
            "ADD R4, R1, R5",
            "ADD R6, R4, R7",
        ]),
        ("Partial dependencies", [
            "ADD R1, R2, R3",
            "SUB R4, R5, R6",
            "OR R7, R1, R4",
        ]),
    ]
    
    compare_instruction_sequences(sequences)
