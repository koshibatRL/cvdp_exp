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

def test_runner():

    runner = get_runner(sim)
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,

        # Arguments
        always=True,
        clean=True,
        waves=True,
        verbose=True,
        timescale=("1ns", "1ps"),
        log_file="sim.log")

    runner.test(hdl_toplevel=toplevel, test_module=module, waves=True)

def test_divider():
    test_runner()
