import os
from pathlib import Path
from cocotb_tools.runner import get_runner
import re
import logging

# Get environment variables for verilog sources, top-level language, and simulation options
verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = os.getenv("WAVE")

# Define the parameters you want to pass (can also get them from environment or command line)
DATA_WIDTH = os.getenv("DATA_WIDTH", 32)  # Default to 16 if not provided
SHIFT_BITS_WIDTH = os.getenv("SHIFT_BITS_WIDTH", 5)  # Default to 4 if not provided

def test_runner():
    runner = get_runner(sim)
    
    # Modify the runner to include parameter passing logic for Icarus or your chosen simulator
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        always=True,
        clean=True,
        waves=True,
        verbose=True,
        timescale=("1ns", "1ns"),
        log_file="build.log",
        # Pass parameters dynamically here using +define+ syntax
        parameters={
            "data_width": DATA_WIDTH,
            "shift_bits_width": SHIFT_BITS_WIDTH
        }
    )

    runner.test(hdl_toplevel=toplevel, test_module=module, waves=True)


if __name__ == "__main__":
    test_runner()
