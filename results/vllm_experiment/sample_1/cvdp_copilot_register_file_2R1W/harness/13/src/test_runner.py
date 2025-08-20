# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

# test_runner.py

import os
from cocotb.runner import get_runner
import pytest
import pickle
import random

verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")


# Define a list of random test parameters
test_param = [32, 64, 96, 128]
@pytest.mark.parametrize("DATA_WIDTH", test_param)
def test_pytest(DATA_WIDTH):
    print(f'Running with: DATA_WIDTH = {DATA_WIDTH}')
    runner = get_runner(sim)
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        parameters= {'DATA_WIDTH': DATA_WIDTH},        
        # Arguments
        always=True,
        clean=True,
        waves=True,
        verbose=True,
        timescale=("1ns", "1ps"),
        log_file="sim.log")
    runner.test(hdl_toplevel=toplevel, test_module=module, waves=True)