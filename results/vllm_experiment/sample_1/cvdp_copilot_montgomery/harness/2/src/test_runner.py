import os
from cocotb_tools.runner import get_runner
import pytest
import random
from math import gcd


verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = bool(os.getenv("WAVE"))

def runner(WIDTH, N, R, R_INVERSE):
    runner = get_runner(sim)
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        parameters= {'N':N, 'R':R, 'R_INVERSE': R_INVERSE},
        always=True,
        clean=True,
        waves=wave,
        verbose=False,
        timescale=("1ns", "1ns"),
        log_file="sim.log")
    runner.test(hdl_toplevel=toplevel, test_module=module, waves=True)

def is_prime(num):
    """Check if a number is prime."""
    if num <= 1:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

def modular_inverse(a, mod):
    """Find the modular inverse of a mod mod."""
    for x in range(1, mod):
        if (a * x) % mod == 1:
            return x
    return None

def ranomize_test_param():
    WIDTH = 32
    while True:
        N = random.randint(2, 1000)
        if not is_prime(N):
            continue

        R = 2**random.randint(2,10)
        if R <= N:
            continue

        # Compute R_INVERSE (modular inverse of R mod N)
        R_INVERSE = modular_inverse(R, N)
        if R_INVERSE is None:
            continue

        # Ensure all constraints are satisfied
        if gcd(R, N) == 1:  # R and N must be coprime (ensured since N is prime)
            break
    return(WIDTH, N, R, R_INVERSE)
def test_redc():
    for _ in range(5):
        WIDTH, N, R, R_INVERSE = ranomize_test_param()
        runner(WIDTH, N, R, R_INVERSE)
