import os
from cocotb_tools.runner import get_runner
import pytest

verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = os.getenv("WAVE")

def test_runner(INPUT_WIDTH: int=12, BCD_DIGITS: int=5 ):
    parameter = {"INPUT_WIDTH":INPUT_WIDTH, "BCD_DIGITS":BCD_DIGITS}
    
    # Debug information
    print(f"[DEBUG] Running simulation with INPUT_WIDTH={INPUT_WIDTH}, BCD_DIGITS={BCD_DIGITS}")
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
@pytest.mark.parametrize("INPUT_WIDTH", [12])
@pytest.mark.parametrize("BCD_DIGITS", [5])

#@pytest.mark.parametrize("test", range(1))
def test_binary_bcd_converter(INPUT_WIDTH, BCD_DIGITS):
    # Run the simulation with specified parameters
    test_runner(INPUT_WIDTH=INPUT_WIDTH, BCD_DIGITS=BCD_DIGITS)
