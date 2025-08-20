import os
import json
from cocotb_tools.runner import get_runner
import pytest

verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = bool(os.getenv("WAVE"))

# Runner function to execute tests
def runner(N: int=8, test_sequence=None, expected_output=None):
    parameters = {"N": N}
    
    os.environ["TEST_SEQUENCE"] = json.dumps(test_sequence)
    os.environ["EXPECTED_OUTPUT"] = json.dumps(expected_output)

    runner = get_runner(sim)
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        parameters=parameters,
        always=True,
        clean=True,
        waves=True,
        verbose=True,
        timescale=("1ns", "1ns"),
        log_file="sim.log"
    )
    runner.test(hdl_toplevel=toplevel, test_module=module)


def manchester_encode(data, N):
    result = []
    for d in data:
        encoded = 0
        for i in range(N-1, -1, -1):  # Start from MSB
            if d & (1 << i):
                encoded = (encoded << 2) | 0b01
            else:
                encoded = (encoded << 2) | 0b10
        result.append(encoded)
    return result

# Test with Even N parameterized test_sequence and expected_output
@pytest.mark.parametrize("N, test_sequence, expected_output", [
    (6, [0x21], manchester_encode([0x21], 6)),
    (8, [0x2F], manchester_encode([0x2F], 8))
])
def test_manchester_even(N, test_sequence, expected_output):
    runner(N=N, test_sequence=test_sequence, expected_output=expected_output)

# Test with Odd N parameterized test_sequence and expected_output
@pytest.mark.parametrize("N, test_sequence, expected_output", [
    (31, [0x711111FF], manchester_encode([0x711111FF], 31)),
    (29, [0x111117FF], manchester_encode([0x111117FF], 29))
])
def test_manchester_odd(N, test_sequence, expected_output):
    runner(N=N, test_sequence=test_sequence, expected_output=expected_output)

