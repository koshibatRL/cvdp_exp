import os
import json
from cocotb_tools.runner import get_runner
import pytest

# Fetch environment variables for Verilog source setup
verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = os.getenv("WAVE")

# Runner to execute tests
def test_runner(NUM_CHANNELS: int=4):
    
    parameters = {"NUM_CHANNELS": NUM_CHANNELS}

    runner = get_runner(sim)

    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        parameters=parameters,
        always=True,
        clean=True,
        waves=True,
        verbose=True,
        timescale=("1ns", "1ns"),
        log_file="sim.log"
    )
    runner.test(hdl_toplevel=toplevel, test_module=module,waves=True)

@pytest.mark.parametrize ("NUM_CHANNELS", [(8)])
def test_with_NUM_CHANNELS_4(NUM_CHANNELS):
    test_runner(NUM_CHANNELS=NUM_CHANNELS)

