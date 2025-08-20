import os
from cocotb_tools.runner import get_runner
import pytest

verilog_sources = os.getenv("VERILOG_SOURCES").split()
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = bool(os.getenv("WAVE"))


def runner(CLK_DIV: int = 8):

    parameter = {
        "CLK_DIV": CLK_DIV
    }
  
    print(f"[DEBUG] Parameters: {parameter}") 
    runner = get_runner(sim)
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        parameters=parameter,
        always=True,
        clean=True,
        waves=wave,
        verbose=True,
        timescale=("1ns", "1ns"),
        log_file="sim.log"
    )
    runner.test(hdl_toplevel=toplevel, test_module=module, waves=wave)


@pytest.mark.parametrize("test", range(1))
@pytest.mark.parametrize("CLK_DIV", [4,8,16,10,6])
def test_serial_line_converter(test, CLK_DIV):
    runner(CLK_DIV=CLK_DIV)
