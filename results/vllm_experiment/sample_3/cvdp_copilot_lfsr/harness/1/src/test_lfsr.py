import cocotb
import os
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles, Timer, Join
import random

# ----------------------------------------
# - Tests
# ----------------------------------------

async def assert_seed(dut, value : int = 0):

    # Assert seed value
    dut.reset.value = 0
    dut.lfsr_seed.value = value

    # Synchronize with Falling Edge again
    await FallingEdge(dut.clock)

    for _ in range(2):
        await RisingEdge(dut.clock)

    dut.reset.value = 1

    for i in range(256):
        await RisingEdge(dut.clock)
        if ((i == 0) or (i == 255)):
            print(dut.lfsr_out)
        if (i == 0):
            first_value = dut.lfsr_out;
        if (i == 0):
            q1 = int(dut.lfsr_out[6]) ^ int(dut.lfsr_out[0])
            q2 = int(dut.lfsr_out[5]) ^ int(dut.lfsr_out[0])
            q3 = int(dut.lfsr_out[1]) ^ int(dut.lfsr_out[0])
            lfsr_out =  (int(dut.lfsr_out[0]) << 7) | (int(dut.lfsr_out[7]) << 6) | (q1 << 5) | (q2 << 4) | (int(dut.lfsr_out[4]) << 3) | (int(dut.lfsr_out[3]) << 2) | (int(dut.lfsr_out[2]) << 1) | q3
            print("lfsr_out ",lfsr_out)
        if (i == 1):
            second_value = int(dut.lfsr_out.value);
            print("second_value ",second_value)
        if (i == 255):
            last_value = dut.lfsr_out;
    if (first_value == last_value):
        print("Max.length sequence");
    if (second_value == lfsr_out):
        print("PRBS next sequence has been checked")
    assert second_value == lfsr_out, f"The computed and DUT 8-bit LFSR sequences are not matching"
    assert first_value == last_value, f"8-bit LFSR doesn't support maximal length sequence"
  

@cocotb.test()
async def test_non_zero_1(dut):

    # Start clock thread
    cocotb.start_soon(Clock(dut.clock, 10, units='ns').start())

    # Assert seed and wait
    seed = int((1.0 - random.random()) * 2 ** 8);
    print("seed_1 ",seed)
    await assert_seed(dut, seed)

@cocotb.test()
async def test_non_zero_2(dut):

    # Start clock thread
    cocotb.start_soon(Clock(dut.clock, 10, units='ns').start())

  # Assert seed and wait
    seed = int((1.0 - random.random()) * 2 ** 8)
    print("seed_2 ",seed)
    await assert_seed(dut, seed)
    
@cocotb.test()
async def test_non_zero_3(dut):

    # Start clock thread
    cocotb.start_soon(Clock(dut.clock, 10, units='ns').start())

  # Assert seed and wait
    seed = int((1.0 - random.random()) * 2 ** 8)
    print("seed_3 ",seed)
    await assert_seed(dut, seed)

