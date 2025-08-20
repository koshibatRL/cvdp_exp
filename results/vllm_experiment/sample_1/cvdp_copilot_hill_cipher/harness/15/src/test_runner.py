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
    )

    runner.test(hdl_toplevel=toplevel, test_module=module, waves=True)


if __name__ == "__main__":
    test_runner()
