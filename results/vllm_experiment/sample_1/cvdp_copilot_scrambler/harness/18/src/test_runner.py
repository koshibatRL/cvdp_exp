import cocotb
import os
import pytest
import random
from cocotb_tools.runner import get_runner

# Environment configuration
verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = bool(os.getenv("WAVE"))

def runner(ROW_COL_WIDTH: int = 16, SUB_BLOCKS: int = 4):
    # Simulation parameters
    parameter = {
        "ROW_COL_WIDTH": ROW_COL_WIDTH,
        "SUB_BLOCKS": SUB_BLOCKS
    }

    # Debug information
    print(f"[DEBUG] Running simulation with ROW_COL_WIDTH={ROW_COL_WIDTH}, SUB_BLOCKS={SUB_BLOCKS}")
    print(f"[DEBUG] Parameters: {parameter}")

    # Configure and run the simulation
    sim_runner = get_runner(sim)
    sim_runner.build(
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

    # Run the test
    sim_runner.test(hdl_toplevel=toplevel, test_module=module, waves=True)

# Generate ROW_COL_WIDTH and SUB_BLOCKS values
row_col_width_values = [16]  # It should not change, the parameters are fixed (following the prompt)
sub_blocks_values = [4]      # It should not change, the parameters are fixed (following the prompt)

# Parametrize test for different ROW_COL_WIDTH and SUB_BLOCKS values
@pytest.mark.parametrize("ROW_COL_WIDTH", row_col_width_values)
@pytest.mark.parametrize("SUB_BLOCKS", sub_blocks_values)
@pytest.mark.parametrize("test", range(1))
def test_data(ROW_COL_WIDTH, SUB_BLOCKS, test):
    # Run the simulation with specified parameters
    runner(ROW_COL_WIDTH=ROW_COL_WIDTH, SUB_BLOCKS=SUB_BLOCKS)