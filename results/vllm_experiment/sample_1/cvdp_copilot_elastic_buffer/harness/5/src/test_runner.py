# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

# test_runner.py

import os
from pathlib import Path
from cocotb_tools.runner import get_runner
import pytest

verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = os.getenv("WAVE")

def test_runner(WIDTH: int=16, NUM_PATTERNS: int=4):
    
    parameter = {"WIDTH":WIDTH, "NUM_PATTERNS":NUM_PATTERNS,}
    # Debug information
    print(f"[DEBUG] Running simulation with WIDTH={WIDTH}, NUM_PATTERNS={NUM_PATTERNS}")
    print(f"[DEBUG] Parameters: {parameter}")

    runner = get_runner(sim)
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,

        # Arguments
        always=True,
        clean=True,
        waves=True,
        verbose=True,
        parameters=parameter,
        timescale=("1ns", "1ps"),
        log_file="sim.log")

    runner.test(hdl_toplevel=toplevel, test_module=module, waves=True)

# Parametrize test for different WIDTH and NUM_PATTERNS
@pytest.mark.parametrize("WIDTH", [4, 16, 32, 64])
@pytest.mark.parametrize("NUM_PATTERNS", [4, 6, 8])

def test_elastic_buffer_pattern_matcher(WIDTH, NUM_PATTERNS):
    # Run the simulation with specified parameters
    test_runner(WIDTH=WIDTH, NUM_PATTERNS=NUM_PATTERNS)