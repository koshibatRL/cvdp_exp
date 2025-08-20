import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, Event
import random
import os
import json


# Initialize DUT
async def init_dut(dut):
    dut.rst_in.value = 1
    dut.src_pulse.value = 0
    await RisingEdge(dut.src_clock)
    await RisingEdge(dut.src_clock)
    await RisingEdge(dut.src_clock)
    await RisingEdge(dut.src_clock)

# Test Case Run: Toggle src_pulse for all channels and observe des_pulse
async def run_test(dut):
    await RisingEdge(dut.src_clock)
    NUM_CHANNELS = int(dut.NUM_CHANNELS.value)
    dut.rst_in.value = 0

    src_falling_event = Event()
    des_falling_event = Event()

    async def wait_for_src_falling():
        await FallingEdge(dut.rst_src_sync)
        src_falling_event.set()

    async def wait_for_des_falling():
        await FallingEdge(dut.rst_des_sync)
        des_falling_event.set()

    # Start monitoring for reset synchronization completion
    cocotb.start_soon(wait_for_src_falling())
    cocotb.start_soon(wait_for_des_falling())

    # Wait for both source and destination resets to synchronize
    await src_falling_event.wait()
    await des_falling_event.wait()

    # Toggle src_pulse for all channels
    for channel in range(NUM_CHANNELS):
        await RisingEdge(dut.src_clock)
        dut.src_pulse.value = 1 << channel  # Activate one channel at a time
        await RisingEdge(dut.src_clock)
        dut.src_pulse.value = 0

    # Monitor des_pulse for each channel
    #for channel in range(NUM_CHANNELS):
        des_pulse_received = False
        des_clock_cycles = 0
        while not des_pulse_received and des_clock_cycles < 5:
            await RisingEdge(dut.des_clock)
            des_clock_cycles += 1
            des_pulse_value = dut.des_pulse.value.to_unsigned() 
            dut._log.info(f"des_pulse[{channel}] = {(des_pulse_value >> channel) & 1}")
            if ((des_pulse_value >> channel) & 1) == 1:
                des_pulse_received = True

        assert des_pulse_received, f"des_pulse[{channel}] was not received within 5 des_clock cycles"


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
async def test_src_100MHz_des_100MHz_different_phase(dut):
    cocotb.start_soon(Clock(dut.src_clock, 10, units='ns').start())  # src_clock, 100MHz
    await Timer(5, units='ns')  # Add manual phase shift
    cocotb.start_soon(Clock(dut.des_clock, 10, units='ns').start())  # des_clock, 100MHz with phase shift
    await init_dut(dut)
    await run_test(dut)

# Test Case 5: src_clock fast, des_clock much faster
@cocotb.test()
async def test_src_100MHz_des_250MHz(dut):
    cocotb.start_soon(Clock(dut.src_clock, 10, units='ns').start())  # src_clock, 100MHz
    cocotb.start_soon(Clock(dut.des_clock, 4, units='ns').start())   # des_clock, 250MHz
    await init_dut(dut)
    await run_test(dut)

# Test Case 6: Random clock frequencies
@cocotb.test()
async def test_random_clocks(dut):
    for _ in range(5):  # Run 5 iterations
        src_period = random.randint(5, 20)
        des_period = random.randint(5, 20)
        cocotb.start_soon(Clock(dut.src_clock, src_period, units='ns').start())
        cocotb.start_soon(Clock(dut.des_clock, des_period, units='ns').start())
        await init_dut(dut)
        await run_test(dut)

# Test Case 7: Reset test
@cocotb.test()
async def test_reset_behavior(dut):
    cocotb.start_soon(Clock(dut.src_clock, 10, units='ns').start())
    cocotb.start_soon(Clock(dut.des_clock, 10, units='ns').start())
    NUM_CHANNELS = int(dut.NUM_CHANNELS.value)
    await init_dut(dut)

    # Deassert reset, toggle src_pulse
    dut.rst_in.value = 0
    for _ in range(NUM_CHANNELS):
        await RisingEdge(dut.src_clock)
        dut.src_pulse.value = 1
        await RisingEdge(dut.src_clock)
        dut.src_pulse.value = 0

    # Assert reset mid-operation
    dut.rst_in.value = 1
    await Timer(10, units='ns')
    dut.rst_in.value = 0
    await RisingEdge(dut.src_clock)

    # Verify no des_pulse after reset
    for _ in range(5):
        await RisingEdge(dut.des_clock)
        assert dut.des_pulse.value.to_unsigned() == 0, "des_pulse should not be asserted after reset"

# Test Case 8: Close frequencies
@cocotb.test()
async def test_close_frequencies(dut):
    cocotb.start_soon(Clock(dut.src_clock, 11, units='ns').start())  # src_clock, ~90.9MHz
    cocotb.start_soon(Clock(dut.des_clock, 10, units='ns').start())  # des_clock, 100MHz
    await init_dut(dut)
    await run_test(dut)

# Test Case 9: Prime frequencies
@cocotb.test()
async def test_prime_frequencies(dut):
    cocotb.start_soon(Clock(dut.src_clock, 9, units='ns').start())  # src_clock, ~111.1MHz
    cocotb.start_soon(Clock(dut.des_clock, 12, units='ns').start())  # des_clock, ~83.33MHz
    await init_dut(dut)
    await run_test(dut)

# Test Case 10: Very slow src_clock, very fast des_clock
@cocotb.test()
async def test_src_1MHz_des_100MHz(dut):
    cocotb.start_soon(Clock(dut.src_clock, 1000, units='ns').start())  # src_clock, 1MHz
    cocotb.start_soon(Clock(dut.des_clock, 10, units='ns').start())   # des_clock, 100MHz
    await init_dut(dut)
    await run_test(dut)

# Test Case 11: Very fast src_clock, very slow des_clock
@cocotb.test()
async def test_src_100MHz_des_1MHz(dut):
    cocotb.start_soon(Clock(dut.src_clock, 10, units='ns').start())  # src_clock, 100MHz
    cocotb.start_soon(Clock(dut.des_clock, 1000, units='ns').start())  # des_clock, 1MHz
    await init_dut(dut)
    await run_test(dut)

# Test Case 12: N=configurable, Sequence
@cocotb.test()
async def test_src_NUM_CHANNLES_config_input_shift(dut):
    cocotb.start_soon(Clock(dut.src_clock, 10, units='ns').start())  # src_clock, 100MHz
    cocotb.start_soon(Clock(dut.des_clock, 1000, units='ns').start())  # des_clock, 1MHz
    NUM_CHANNELS = int(dut.NUM_CHANNELS.value)
    await init_dut(dut)

    await RisingEdge(dut.src_clock)
    dut.rst_in.value = 0

    src_falling_event = Event()
    des_falling_event = Event()

    async def wait_for_src_falling():
        await FallingEdge(dut.rst_src_sync)
        src_falling_event.set()

    async def wait_for_des_falling():
        await FallingEdge(dut.rst_des_sync)
        des_falling_event.set()

    # Start monitoring for reset synchronization completion
    cocotb.start_soon(wait_for_src_falling())
    cocotb.start_soon(wait_for_des_falling())

    # Wait for both source and destination resets to synchronize
    await src_falling_event.wait()
    await des_falling_event.wait()

    # Toggle src_pulse for all channels
    for channel in range(NUM_CHANNELS):
        await RisingEdge(dut.src_clock)
        dut.src_pulse.value = 1 << channel  # Activate one channel at a time
        await RisingEdge(dut.src_clock)
        dut.src_pulse.value = 0

    # Monitor des_pulse for each channel
        des_pulse_received = False
        des_clock_cycles = 0
        while not des_pulse_received and des_clock_cycles < 5:
            await RisingEdge(dut.des_clock)
            des_clock_cycles += 1
            des_pulse_value = dut.des_pulse.value.to_unsigned()  
            dut._log.info(f"des_pulse[{channel}] = {(des_pulse_value >> channel) & 1}")
            if ((des_pulse_value >> channel) & 1) == 1:
                des_pulse_received = True

        assert des_pulse_received, f"des_pulse[{channel}] was not received within 5 des_clock cycles"

# Test Case 13: N=4, Sequence
@cocotb.test()
async def test_src_NUM_CHANNLES_4_sequence(dut):
    cocotb.start_soon(Clock(dut.src_clock, 10, units='ns').start())  # src_clock, 100MHz
    cocotb.start_soon(Clock(dut.des_clock, 20, units='ns').start())  # des_clock, 50MHz
    await init_dut(dut)

    await RisingEdge(dut.src_clock)
    dut.rst_in.value = 0

    src_falling_event = Event()
    des_falling_event = Event()

    async def wait_for_src_falling():
        await FallingEdge(dut.rst_src_sync)
        src_falling_event.set()

    async def wait_for_des_falling():
        await FallingEdge(dut.rst_des_sync)
        des_falling_event.set()

    # Start monitoring for reset synchronization completion
    cocotb.start_soon(wait_for_src_falling())
    cocotb.start_soon(wait_for_des_falling())

    # Wait for both source and destination resets to synchronize
    await src_falling_event.wait()
    await des_falling_event.wait()

    # Define the sequence to send and the expected result
    sequence = [0b0001, 0b0010, 0b0000, 0b1100, 0b0000, 0b0000, 0b0000, 0b0000, 0b0000, 0b0000]
    expected = [0b0000, 0b0000, 0b0000, 0b0000, 0b0001, 0b0001, 0b0010, 0b0010, 0b1100, 0b1100]

    # Send the sequence on src_pulse and validate against expected
    for i, value in enumerate(sequence):
        dut.src_pulse.value = value  # Apply the src_pulse value

        # Compare observed with expected for the current cycle
        await RisingEdge(dut.src_clock)  # Wait for one des_clock cycle
        observed = dut.des_pulse.value.to_unsigned()  # Capture des_pulse
        assert observed == expected[i], f"Test failed at cycle {i}: Observed = {observed:04b}, Expected = {expected[i]:04b}"

