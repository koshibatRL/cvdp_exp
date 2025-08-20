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

def runner(NBW_DLY: int = 5, NBW_BEANS: int = 2, NS_BEANS: int = 4):
    # Simulation parameters
    parameter = {
        "NBW_DLY": NBW_DLY,
        "NBW_BEANS": NBW_BEANS,
        "NS_BEANS": NS_BEANS
    }

    # Debug information
    print(f"\n[DEBUG] Running simulation with NBW_DLY={NBW_DLY}")
    print(f"[DEBUG] Running simulation with NBW_BEANS={NBW_BEANS}")
    print(f"[DEBUG] Running simulation with NS_BEANS={NS_BEANS}")
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
random_nbw_dly   = [2] + [5] + [random.randint(3, 8) for _ in range(2)]
random_nbw_beans = [1] + [2] + [random.randint(3, 8) for _ in range(2)]

# Parametrize test for different random data sizes
@pytest.mark.parametrize("NBW_DLY", random_nbw_dly)
@pytest.mark.parametrize("NBW_BEANS", random_nbw_beans)
def test_data(NBW_DLY, NBW_BEANS):
    random_ns_beans = 2**NBW_BEANS
    # Run the simulation with specified parameters
    runner(NBW_DLY=NBW_DLY, NBW_BEANS=NBW_BEANS, NS_BEANS=random_ns_beans)