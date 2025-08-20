import os
from cocotb_tools.runner import get_runner
import pytest
import math

verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = bool(os.getenv("WAVE"))

def runner(DATA_WIDTH: int=0, SHIFT_DIRECTION: int = 0):
    WIDTH = int(DATA_WIDTH//2)
    code_width = math.ceil(math.log2(DATA_WIDTH+1))
    parameter = {"DATA_WIDTH":DATA_WIDTH, "SHIFT_DIRECTION": SHIFT_DIRECTION, "CODE_WIDTH": DATA_WIDTH + code_width}
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


@pytest.mark.parametrize("DATA_WIDTH", [4,8,16,32,64])
@pytest.mark.parametrize("SHIFT_DIRECTION", [0,1])
def test_nbit_sizling(DATA_WIDTH,SHIFT_DIRECTION):
        runner(DATA_WIDTH = DATA_WIDTH, SHIFT_DIRECTION = SHIFT_DIRECTION)