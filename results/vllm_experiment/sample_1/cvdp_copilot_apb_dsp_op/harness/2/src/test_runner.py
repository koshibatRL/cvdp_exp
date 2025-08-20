# test_runner.py

import os
from cocotb.runner import get_runner
import pytest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fetch environment variables
verilog_sources = os.getenv("VERILOG_SOURCES", "").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG", "verilog")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")

def runner(addr_width, data_width):
    """
    Runs the cocotb simulation with the specified ADDR_WIDTH and DATA_WIDTH parameters.

    Args:
        addr_width (int): The ADDR_WIDTH value to test.
        data_width (int): The DATA_WIDTH value to test.
    """
    logger.info(f"Starting simulation with ADDR_WIDTH = {addr_width}")
    logger.info(f"Starting simulation with DATA_WIDTH = {data_width}")

    # Initialize the simulator runner
    runner = get_runner(sim)

    # Build the simulation with the specified ADDR_WIDTH and DATA_WIDTH parameters
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        parameters={"ADDR_WIDTH": addr_width, "DATA_WIDTH": data_width},  # Pass ADDR_WIDTH parameter
        # Simulator Arguments
        always=True,
        clean=True,
        waves=False,        # Disable waveform generation for faster runs
        verbose=False,      # Set to True for detailed simulator logs
        timescale=("1ns", "1ps"),
        log_file=f"sim_{toplevel}.log"
    )

    # Run the simulation
    runner.test(
        hdl_toplevel=toplevel,
        test_module=module,
        waves=False
    )

    logger.info(f"Completed simulation with ADDR_WIDTH and DATA_WIDTH = {addr_width, data_width}")

@pytest.mark.parametrize("addr_width, data_width", [(8, 32)])  # Add desired ADDR_WIDTH and DATA_WIDTH values here
def test_cvdp_copilot_apb_dsp_op(addr_width, data_width):
    """
    Pytest function to run cocotb simulations with different ADDR_WIDTH and DATA_WIDTH parameters.

    Args:
        addr_width (int): The ADDR_WIDTH value to test.
        data_width (int): The DATA_WIDTH value to test.
    """
    try:
        runner(addr_width, data_width)
    except Exception as e:
        logger.error(f"Simulation failed for ADDR_WIDTH and DATA_WIDTH = {addr_width, data_width}: {e}")
        # Using assert False to report failure without halting other tests
        assert False, f"Simulation failed for ADDR_WIDTH and DATA_WIDTH = {addr_width, data_width}: {e}"