import os
from cocotb_tools.runner import get_runner
import pytest

verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = bool(os.getenv("WAVE"))

def runner(DATA_WIDTH: int=4 ,NUM_STREAMS : int=4):
    parameter = {"DATA_WIDTH":DATA_WIDTH , "NUM_STREAMS" : NUM_STREAMS}
    runner = get_runner(sim)
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        # Arguments
        parameters=parameter,
        always=True,
        clean=True,
        waves=wave,
        verbose=True,
        timescale=("1ns", "1ns"),
        log_file="sim.log")
    runner.test(hdl_toplevel=toplevel, test_module=module, waves=wave)


@pytest.mark.parametrize("DATA_WIDTH", [8,16,10,7])
@pytest.mark.parametrize("NUM_STREAMS", [4,8,10,7])
def test_run_length(DATA_WIDTH,NUM_STREAMS):
        runner(DATA_WIDTH = DATA_WIDTH, NUM_STREAMS = NUM_STREAMS) 
