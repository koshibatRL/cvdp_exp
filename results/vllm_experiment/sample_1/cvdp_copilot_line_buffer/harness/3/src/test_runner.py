import cocotb
import os
import pytest
import random
import math
from cocotb_tools.runner import get_runner

# Environment configuration
verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = bool(os.getenv("WAVE"))
#NBW_DATA=NBW_DATA, NS_ROW=NS_ROW, NS_COLUMN=NS_COLUMN, NS_R_OUT=NS_R_OUT, NS_C_OUT=NS_C_OUT, CONSTANT=CONSTANT
def runner(NBW_DATA: int = 8, NS_ROW: int = 10,  NS_COLUMN: int = 8,  NS_R_OUT: int = 4,  NS_C_OUT: int = 3,  CONSTANT: int = 255, NBW_ROW: int = 4, NBW_COL: int = 3, NBW_MODE: int = 3):
    # Simulation parameters
    parameter = {
        "NBW_DATA" : NBW_DATA,
        "NS_ROW"   : NS_ROW,
        "NS_COLUMN": NS_COLUMN,
        "NS_R_OUT" : NS_R_OUT,
        "NS_C_OUT" : NS_C_OUT,
        "CONSTANT" : CONSTANT,
        "NBW_ROW"  : NBW_ROW,
        "NBW_COL"  : NBW_COL,
        "NBW_MODE" : NBW_MODE
    }

    # Debug information
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


# Generate "default" and a random size
random_nbw_data  = [8]   + [random.randint(9,16)  for _ in range(1)]
random_ns_row    = [10]  + [random.randint(9,16)  for _ in range(1)]
random_ns_column = [8]   + [random.randint(9,16)  for _ in range(1)]
random_ns_r_out  = [4]   + [random.randint(1,7)   for _ in range(1)]
random_ns_c_out  = [3]   + [random.randint(1,7)   for _ in range(1)]
random_constant  = [255] + [random.randint(0,254) for _ in range(1)]

# Parametrize test for different random parameters
@pytest.mark.parametrize("NBW_DATA", random_nbw_data)
@pytest.mark.parametrize("NS_ROW"  , random_ns_row)
@pytest.mark.parametrize("NS_COLUMN", random_ns_column)
@pytest.mark.parametrize("NS_R_OUT", random_ns_r_out)
@pytest.mark.parametrize("NS_C_OUT", random_ns_c_out)
@pytest.mark.parametrize("CONSTANT", random_constant)

def test_data(NBW_DATA, NS_ROW, NS_COLUMN, NS_R_OUT, NS_C_OUT, CONSTANT):
    # Run the simulation with specified parameters
    NBW_ROW = math.ceil(math.log2(NS_ROW))
    NBW_COL = math.ceil(math.log2(NS_COLUMN))
    runner(NBW_DATA=NBW_DATA, NS_ROW=NS_ROW, NS_COLUMN=NS_COLUMN, NS_R_OUT=NS_R_OUT, NS_C_OUT=NS_C_OUT, CONSTANT=CONSTANT, NBW_ROW=NBW_ROW, NBW_COL=NBW_COL, NBW_MODE=3)