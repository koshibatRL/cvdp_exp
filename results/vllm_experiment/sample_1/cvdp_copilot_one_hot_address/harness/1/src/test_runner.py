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

def runner(NS_A: int = 8, NS_B: int = 4):
    # Simulation parameters
    parameter = {
        "NS_A": NS_A,
        "NS_B": NS_B
    }

    # Debug information
    print(f"\n[DEBUG] Running simulation with NS_A={NS_A}")
    print(f"[DEBUG] Running simulation with NS_B={NS_B}")
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

# Generate minimum, default and more random sizes
random_ns_a = [2] + [8] + [random.randint(3,32) for _ in range(2)]
random_ns_b = [2] + [4] + [random.randint(3,32) for _ in range(2)]

# Parametrize test for different random data sizes
@pytest.mark.parametrize("NS_A", random_ns_a)
@pytest.mark.parametrize("NS_B", random_ns_b)

def test_data(NS_A, NS_B):
    # Run the simulation with specified parameters
    runner(NS_A=NS_A, NS_B=NS_B)