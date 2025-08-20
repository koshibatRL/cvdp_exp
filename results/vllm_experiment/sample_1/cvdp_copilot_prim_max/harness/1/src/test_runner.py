# runner.py

# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

import os
from cocotb.runner import get_runner
import pytest
from itertools import product

# ----------------------------
# Environment Variables
# ----------------------------

verilog_sources = os.getenv("VERILOG_SOURCES", "").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG", "verilog")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL", "prim_max_find")  # Update as needed
module          = os.getenv("MODULE", "test_prim_max_find")  # Update as needed

# ----------------------------
# Parameter Values
# ----------------------------

num_src_values = [4, 8, 16]        # Define the range for NumSrc
width_values = [8, 16, 24, 32]     # Define the range for Width

# Generate all combinations of NumSrc and Width
parameter_combinations = list(product(num_src_values, width_values))

# ----------------------------
# Pytest Parameterization
# ----------------------------

@pytest.mark.parametrize("NumSrc, Width", parameter_combinations)
def test_prim_max_find(NumSrc, Width):
    """
    Parameterized test_runner to verify the prim_max_find module for multiple NumSrc and Width values.
    """
    print(f"Running simulation with NumSrc = {NumSrc}, Width = {Width}")
    
    # Initialize the simulator runner
    runner = get_runner(sim)
    
    # Build and simulate with parameters
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        parameters={
            'NumSrc': NumSrc,
            'Width': Width
        },
        always=True,      # Rebuild every simulation run
        clean=True,       # Clean up previous simulation data
        waves=True,       # Generate waveform files
        verbose=True,     # Enable verbose logging
        timescale=("1ns", "1ps"),  # Set timescale
        log_file=f"sim_NumSrc_{NumSrc}_Width_{Width}.log"  # Unique log file per parameter set
    )

    # Run the simulation
    runner.test(
        hdl_toplevel=toplevel,
        test_module=module,
        waves=True
    )
