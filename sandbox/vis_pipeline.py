import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.visualization import draw_pipeline_diagram

draw_pipeline_diagram([
    "ADD R1, R2, R3",      # R1 = R2 + R3
    "SUB R1, R4, R5",      # WAW: both write to R1
    "LOAD R6, 100(R1)",    # RAW: needs R1
    "STORE R6, 200(R7)"    # RAW: needs R6 from LOAD
])