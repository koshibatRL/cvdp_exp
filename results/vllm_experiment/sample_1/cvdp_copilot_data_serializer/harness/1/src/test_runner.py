# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

import os
import pytest
from cocotb.runner import get_runner

# Environment Variables
verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG", "verilog")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL", "data_serializer")
module          = os.getenv("MODULE", "test_data_serializer")

# Parameter values
DATA_W_values    = [8]        # e.g. we only test 8-bit width in this demo
BIT_ORDER_values = [0, 1]     # LSB-first or MSB-first
PARITY_values    = [0, 1, 2]  # none, even, odd

@pytest.mark.parametrize("DATA_W",    DATA_W_values)
@pytest.mark.parametrize("BIT_ORDER", BIT_ORDER_values)
@pytest.mark.parametrize("PARITY",    PARITY_values)
def test_data_serializer(DATA_W, BIT_ORDER, PARITY):
    """
    Parameterized test that compiles and simulates data_serializer
    for each combination of (DATA_W, BIT_ORDER, PARITY).
    Uses Cocotb's built-in runner with the 'parameters' dict argument.
    """

    print(f"Running simulation with DATA_W={DATA_W}, BIT_ORDER={BIT_ORDER}, PARITY={PARITY}")

    # Create a runner for your chosen simulator
    runner = get_runner(sim)

    # Build (compile) the design, passing Verilog parameters in 'parameters={}'
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        parameters={
            "DATA_W":   DATA_W,
            "BIT_ORDER":BIT_ORDER,
            "PARITY":   PARITY
        },
        always=True,
        clean=True,
        waves=True,
        verbose=True,
        timescale=("1ns", "1ps"),
        log_file=f"sim_dw{DATA_W}_bo{BIT_ORDER}_pa{PARITY}.log"
    )

    # Run Cocotb test(s) in the Python module 'module'
    runner.test(
        hdl_toplevel=toplevel,
        test_module=module,
        waves=True
    )
