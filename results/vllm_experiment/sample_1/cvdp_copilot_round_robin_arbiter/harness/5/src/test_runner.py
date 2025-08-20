import os
from pathlib import Path
from cocotb_tools.runner import get_runner
import re
import logging

# Get environment variables for verilog sources, top-level language, simulation, etc.
verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = os.getenv("WAVE")

# Define the parameter you want to pass for the round robin arbiter
# Default to 4 if the env var is not set
N_DEVICES = os.getenv("N_DEVICES", "4")
TIMEOUT   = os.getenv("TIMEOUT", "16")  # Example: Timeout after 100 cycles


def test_runner():
    runner = get_runner(sim)
    
    # We pass the "N" parameter dynamically here.
    # The 'parameters' dict keys should match your Verilog parameter name exactly.
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        always=True,
        clean=True,
        waves=True,       # or wave=(wave=="1") if you only enable waves if wave=1
        verbose=True,
        timescale=("1ns", "1ns"),
        log_file="build.log",
        parameters={
            "N": N_DEVICES,  # Ties to 'parameter N = ...' in round_robin_arbiter
            "TIMEOUT": TIMEOUT
        }
    )

    runner.test(
        hdl_toplevel=toplevel,
        test_module=module,
        waves=True
    )

if __name__ == "__main__":
    test_runner()
