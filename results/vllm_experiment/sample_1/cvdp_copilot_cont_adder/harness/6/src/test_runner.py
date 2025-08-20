import os
from pathlib import Path
from cocotb.runner import get_runner
import re
import logging
import pytest

verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = os.getenv("WAVE")

def test_runner(DATA_WIDTH: int=32, THRESHOLD_VALUE: int=100, SIGNED_INPUTS: int=1 ):
    parameter = {"DATA_WIDTH":DATA_WIDTH, "THRESHOLD_VALUE":THRESHOLD_VALUE, "SIGNED_INPUTS":SIGNED_INPUTS }
    
    # Debug information
    print(f"[DEBUG] Running simulation with DATA_WIDTH={DATA_WIDTH}, THRESHOLD_VALUE={THRESHOLD_VALUE}, SIGNED_INPUTS={SIGNED_INPUTS}")
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
        timescale=("1ns", "1ns"),
        log_file="build.log")

    runner.test(hdl_toplevel=toplevel, test_module=module, waves=True)   

# Parametrize test for different WIDTH and WINDOW_SIZE
@pytest.mark.parametrize("DATA_WIDTH", [16,32,64])
@pytest.mark.parametrize("THRESHOLD_VALUE", [10,100,1000,555])
@pytest.mark.parametrize("SIGNED_INPUTS", [1,0])
#@pytest.mark.parametrize("test", range(1))
def test_continous_adder(DATA_WIDTH, THRESHOLD_VALUE, SIGNED_INPUTS):
    # Run the simulation with specified parameters
    test_runner(DATA_WIDTH=DATA_WIDTH, THRESHOLD_VALUE=THRESHOLD_VALUE, SIGNED_INPUTS=SIGNED_INPUTS)