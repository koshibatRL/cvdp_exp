import os
from cocotb_tools.runner import get_runner
import pytest

verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = bool(os.getenv("WAVE"))

def runner(WIDTH):
    runner = get_runner(sim)
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        parameters= {'WIDTH': WIDTH},
        always=True,
        clean=True,
        waves=wave,
        verbose=False,
        timescale=("1ns", "1ns"),
        log_file="sim.log")
    runner.test(hdl_toplevel=toplevel, test_module=module, waves=wave)


def get_powers_of_two_pairs(iterations):
    value = 4
    pairs = []
    for _ in range(iterations):
        pairs.append(value)
        value *= 2
    return pairs

# Test the function
pairs = get_powers_of_two_pairs(5)
#print(pairs)

# random test
@pytest.mark.parametrize("WIDTH",pairs)
def test(WIDTH):
    print(f'Running with: WIDTH = {WIDTH}')
    runner(WIDTH)
