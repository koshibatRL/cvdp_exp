import os
from pathlib import Path
from cocotb.runner import get_runner
import re
import logging
import pytest
import random

verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = os.getenv("WAVE")

param_width = os.getenv("N", "8")

def test_runner():
    runner = get_runner(sim)
    parameters = {
        "N": param_width,
    }
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        # Arguments
        always=True,
        clean=True,
        waves=True,
        verbose=True,
        parameters=parameters,
        timescale=("1ns", "1ns"),
        log_file="build.log")

    runner.test(hdl_toplevel=toplevel, test_module=module, waves=True)   


if __name__ == "__main__":
    test_runner()