import os
import random
from cocotb_tools.runner import get_runner
import pytest

# Gather environment variables for simulation settings
verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = bool(os.getenv("WAVE"))

# Define a runner function that takes the WIDTH parameter
def runner(H, W, N):
    # Get the simulator runner for the specified simulator (e.g., icarus)
    runner = get_runner(sim)
    
    # Build the simulation environment with the randomized WIDTH parameter
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        parameters={'H': H, 'W' : W, 'N' : N },
        always=True,               # Build even if files have not changed
        clean=True,                # Clean previous builds
        waves=True,
        verbose=False,
        timescale=("1ns", "1ns"),  # Set timescale
        log_file="sim.log"         # Log the output of the simulation
    )
    
    # Run the test module
    runner.test(hdl_toplevel=toplevel, test_module=module, waves=wave)

# Parametrize test for different WIDTH and SIGNED_EN
@pytest.mark.parametrize("H", [8])
@pytest.mark.parametrize("W", [5])
@pytest.mark.parametrize("N", [1,4,8])
def test_alphablending(H, W, N):
    # Log the randomized WIDTH
    print(f'Running with: H = {H}, W = {W},  N = {N}')

    # Call the runner function with the randomized WIDTH
    runner(H,W, N)