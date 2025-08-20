import os
import pytest
import math
from cocotb_tools.runner import get_runner

# Gather environment variables for simulation settings
verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = bool(os.getenv("WAVE"))

# Define a runner function that takes the N parameter
def runner(N):
    # Calculate M as log2(N)
    M = math.ceil(math.log2(N))  # Ensure M is an integer

    # Get the simulator runner for the specified simulator
    runner = get_runner(sim)

    # Build the simulation environment with dynamic N and M parameters
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        parameters={"N": N, "M": M},  # Pass parameters dynamically
        always=True,               # Build even if files have not changed
        clean=True,                # Clean previous builds
        waves=True,
        verbose=True,
        timescale=("1ns", "1ns"),  # Set timescale
        log_file="sim.log"         # Log the output of the simulation
    )

    # Run the test module
    runner.test(hdl_toplevel=toplevel, test_module=module, waves=True)

# Define test parameters for N
test_param = [4, 8, 16, 32, 64, 128]  # Example values for N

# Parametrize the test with the defined N values
@pytest.mark.parametrize("N", test_param)
def test_apb(N):
    # Call the runner function with the specified N
    runner(N)
