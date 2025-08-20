import os
import random
import pytest
from cocotb_tools.runner import get_runner

# Gather environment variables for simulation settings
verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = bool(os.getenv("WAVE"))

# Define a runner function that takes the WIDTH parameter
def runner(WIDTH):
    # Get the simulator runner for the specified simulator (e.g., icarus)
    runner = get_runner(sim)
    
    # Build the simulation environment with the randomized WIDTH parameter
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        parameters={'WIDTH': WIDTH},
        always=True,               # Build even if files have not changed
        clean=True,                # Clean previous builds
        waves=True,
        verbose=False,
        timescale=("1ns", "1ns"),  # Set timescale
        log_file="sim.log"         # Log the output of the simulation
    )
    
    # Run the test module
    runner.test(hdl_toplevel=toplevel, test_module=module, waves=wave)

# Generate random WIDTH values for test cases
test_param = [random.randint(1, 32) for _ in range(4)]

# Parametrize the test with random WIDTH values
@pytest.mark.parametrize("WIDTH", test_param)
def test_array_multiplier_run(WIDTH):
    # Log the randomized WIDTH
    print(f"Running with WIDTH = {WIDTH}")
    
    # Call the runner function with the randomized WIDTH
    runner(WIDTH)
