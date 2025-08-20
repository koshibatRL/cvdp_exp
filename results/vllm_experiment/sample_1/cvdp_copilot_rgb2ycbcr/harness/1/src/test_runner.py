import os
from pathlib import Path
from cocotb_tools.runner import get_runner
import pytest

# Fetch environment variables
verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel = os.getenv("TOPLEVEL")
module = os.getenv("MODULE")
sim = os.getenv("SIM", "icarus")

def test_runner(IMG_WIDTH=4, IMG_HEIGHT=3):
    """Run Cocotb Test for AXI-Stream RGB to YCbCr Conversion"""

    # Parameterized test
    parameter_defines = {
        "IMG_WIDTH": IMG_WIDTH,
        "IMG_HEIGHT": IMG_HEIGHT,
    }
    print(f"Running simulation with IMG_WIDTH={IMG_WIDTH}, IMG_HEIGHT={IMG_HEIGHT}")


    runner = get_runner(sim)
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        always=True,
        clean=True,
        waves=True,
        verbose=True,
        timescale=("1ns", "1ps"),
        log_file="sim.log",
        defines={"SIMULATION": None}
    )
    plusargs = [f"+IMG_WIDTH={IMG_WIDTH}", f"+IMG_HEIGHT={IMG_HEIGHT}"]

    runner.test(hdl_toplevel=toplevel, test_module=module, waves=True, plusargs=plusargs)


@pytest.mark.parametrize("IMG_WIDTH,IMG_HEIGHT", [(2, 4), (5, 3), (6, 2)])
def test_axis_rgb2ycbcr(IMG_WIDTH, IMG_HEIGHT):
    """Parameterized test for AXIS RGB to YCbCr Converter"""

    print(f"Test Runner: IMG_WIDTH={IMG_WIDTH}, IMG_HEIGHT={IMG_HEIGHT}")
    test_runner(IMG_WIDTH=IMG_WIDTH, IMG_HEIGHT=IMG_HEIGHT)
