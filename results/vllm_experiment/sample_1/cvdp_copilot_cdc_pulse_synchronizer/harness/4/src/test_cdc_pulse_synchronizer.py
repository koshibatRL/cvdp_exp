import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random

# Initialize DUT
async def init_dut(dut):
    dut.rst_in.value = 1
    dut.src_pulse.value = 0
    await RisingEdge(dut.src_clock)
    await RisingEdge(dut.src_clock)
    await RisingEdge(dut.src_clock)
    await RisingEdge(dut.src_clock)

# Test Case Run: src_pulse toggles and observe des_pulse
async def run_test(dut):
    await RisingEdge(dut.src_clock)
    dut.rst_in.value = 0

    # Toggle src_pulse once
    for _ in range(1):
        await RisingEdge(dut.src_clock)
        dut.src_pulse.value = 1
        await RisingEdge(dut.src_clock)
        dut.src_pulse.value = 0

    # Monitor des_pulse
    des_pulse_received = False
    des_clock_cycles = 0
    while not des_pulse_received and des_clock_cycles < 5:
        await RisingEdge(dut.des_clock)
        des_clock_cycles += 1
        dut._log.info(f"des_pulse = {dut.des_pulse.value}")
        if dut.des_pulse.value == 1:
            des_pulse_received = True

    assert des_pulse_received, "des_pulse was not received within 4 des_clock cycles"

# Test Case 1: src_clock and des_clock same speed, same phase
@cocotb.test()
async def test_src_100MHz_des_100MHz_same_phase(dut):
    cocotb.start_soon(Clock(dut.src_clock, 10, units='ns').start())  # src_clock, 100MHz
    cocotb.start_soon(Clock(dut.des_clock, 10, units='ns').start())  # des_clock, 100MHz same phase
    await init_dut(dut)
    await run_test(dut)

# Test Case 2: src_clock fast, des_clock slow
@cocotb.test()
async def test_src_100MHz_des_50MHz(dut):
    cocotb.start_soon(Clock(dut.src_clock, 10, units='ns').start())  # Fast src_clock, 100 MHz
    cocotb.start_soon(Clock(dut.des_clock, 20, units='ns').start())  # Slow des_clock, 50 MHz
    await init_dut(dut)
    await run_test(dut)

# Test Case 3: src_clock slow, des_clock fast
@cocotb.test()
async def test_src_50MHz_des_100MHz(dut):
    cocotb.start_soon(Clock(dut.src_clock, 20, units='ns').start())  # Slow src_clock, 50MHz
    cocotb.start_soon(Clock(dut.des_clock, 10, units='ns').start())   # Fast des_clock, 100MHz
    await init_dut(dut)
    await run_test(dut)

# Test Case 4: src_clock and des_clock same speed, different phase
@cocotb.test()
async def test_src_100MHz_des_100MHz_and_different_phase(dut):
    cocotb.start_soon(Clock(dut.src_clock, 10, units='ns').start())  # src_clock, 100MHz
    await Timer(5, units='ns')  # Add manual phase shift
    cocotb.start_soon(Clock(dut.des_clock, 10, units='ns').start())  # des_clock, 100MHz with phase shift
    await init_dut(dut)
    await run_test(dut)

# Test Case 5: src_clock slow, des_clock fast
@cocotb.test()
async def test_RTL_Bug_src_100MHz_des_250MHz(dut):
    cocotb.start_soon(Clock(dut.src_clock, 10, units='ns').start())  # Slow src_clock, 100MHz
    cocotb.start_soon(Clock(dut.des_clock, 4, units='ns').start())   # Fast des_clock, 250MHz
    await init_dut(dut)
    await run_test(dut)

# Test Case 6: Random clock frequencies and reset src_pulse
@cocotb.test()
async def test_random_clocks_and_reset(dut):
    for iteration in range(10):
        src_period = random.randint(3, 20)  # Random period between 5 and 20 ns
        des_period = random.randint(3, 20)  # Random period between 5 and 20 ns

        src_frequency = 1000 / src_period  # Convert period to frequency in MHz
        des_frequency = 1000 / des_period  # Convert period to frequency in MHz

        dut._log.info(f"Iteration {iteration + 1}: Selected src_clock frequency: {src_frequency:.2f} MHz")
        dut._log.info(f"Iteration {iteration + 1}: Selected des_clock frequency: {des_frequency:.2f} MHz")

        cocotb.start_soon(Clock(dut.src_clock, src_period, units='ns').start())
        cocotb.start_soon(Clock(dut.des_clock, des_period, units='ns').start())
        await init_dut(dut)
        await run_test(dut)
        await RisingEdge(dut.des_clock)
        await RisingEdge(dut.des_clock)
        await RisingEdge(dut.des_clock)
        await RisingEdge(dut.des_clock)


# Test Case 7: Reset Test
@cocotb.test()
async def test_reset(dut):
    src_period = 10  # Fixed period for src_clock
    des_period = 10  # Fixed period for des_clock

    cocotb.start_soon(Clock(dut.src_clock, src_period, units='ns').start())
    cocotb.start_soon(Clock(dut.des_clock, des_period, units='ns').start())

    # Initialize DUT with reset
    await init_dut(dut)

    # De-assert reset and toggle src_pulse
    dut.rst_in.value = 0
    await RisingEdge(dut.src_clock)
    dut.src_pulse.value = 1
    await RisingEdge(dut.src_clock)
    dut.src_pulse.value = 0

    # Assert & De-assert reset
    await RisingEdge(dut.src_clock)
    await RisingEdge(dut.src_clock)
    dut.rst_in.value = 1
    await RisingEdge(dut.src_clock)
    dut.rst_in.value = 0
    await RisingEdge(dut.src_clock)


    # Ensure des_pulse is not asserted after reset
    des_pulse_received = False
    des_clock_cycles = 0
    while not des_pulse_received and des_clock_cycles < 5:
        await RisingEdge(dut.des_clock)
        des_clock_cycles += 1
        dut._log.info(f"des_pulse = {dut.des_pulse.value}")
        if dut.des_pulse.value == 0:
            des_pulse_received = True

    assert des_pulse_received, "des_pulse should not be assrted after reset"

# Test Case 8: close frequencies
@cocotb.test()
async def test_src_90MHz_des_100MHz(dut):
    cocotb.start_soon(Clock(dut.src_clock, 11, units='ns').start())  # Slow src_clock, 90MHz
    cocotb.start_soon(Clock(dut.des_clock, 10, units='ns').start())   # Fast des_clock, 100MHz
    await init_dut(dut)
    await run_test(dut)

# Test Case 9: Prime frequencies
@cocotb.test()
async def test_src_111p1MHz_des_83p33MHz(dut):
    cocotb.start_soon(Clock(dut.src_clock, 9, units='ns').start())  # Slow src_clock, 111.1MHz
    cocotb.start_soon(Clock(dut.des_clock, 12, units='ns').start())   # Fast des_clock, 83.33MHz
    await init_dut(dut)
    await run_test(dut)

# Test Case 10: distance frequencies
@cocotb.test()
async def test_src_1MHz_des_100MHz(dut):
    cocotb.start_soon(Clock(dut.src_clock, 1000, units='ns').start())  # Slow src_clock, 1MHz
    cocotb.start_soon(Clock(dut.des_clock, 10, units='ns').start())   # Fast des_clock, 100MHz
    await init_dut(dut)
    await run_test(dut)

# Test Case 11: Inverse frequencies
@cocotb.test()
async def test_src_100MHz_des_1MHz(dut):
    cocotb.start_soon(Clock(dut.src_clock, 10, units='ns').start())  # Slow src_clock, 100MHz
    cocotb.start_soon(Clock(dut.des_clock, 1000, units='ns').start())   # Fast des_clock, 1MHz
    await init_dut(dut)
    await run_test(dut)
