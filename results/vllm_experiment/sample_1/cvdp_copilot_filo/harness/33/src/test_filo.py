import cocotb
from cocotb.triggers import RisingEdge, Timer
import random

# Clock generation task
async def clock_gen(dut):
    while True:
        dut.clk.value = 0
        await Timer(5, units='ns')
        dut.clk.value = 1
        await Timer(5, units='ns')

# Task to apply reset
async def apply_reset(dut):
    dut.reset.value = 1
    await Timer(20, units='ns')
    dut.reset.value = 0
    await RisingEdge(dut.clk)

# Task to push random data and store the value for later verification
async def push_data(dut, pushed_values, DATA_WIDTH):
    if dut.reset.value == 1:
        dut._log.info("Cannot push during reset.")
        return  # Skip push operation if reset is high

    value = random.randint(0, (1 << DATA_WIDTH) - 1)
    if dut.full.value == 1:
        dut._log.info("Cannot push, FILO is full.")
        assert False, "Trying to push when FILO is full."
    else:
        dut.push.value = 1
        dut.data_in.value = value
        await RisingEdge(dut.clk)
        dut._log.info(f"Pushed random value: {hex(value)}")
        pushed_values.append(value)
        dut.push.value = 0
        await Timer(20, units='ns')

# Task to pop data and verify it against the expected value
async def pop_data(dut, expected_value, DATA_WIDTH):
    if dut.reset.value == 1:
        dut._log.info("Cannot pop during reset.")
        return

    if dut.empty.value == 1:
        dut._log.info("Cannot pop, FILO is empty.")
        assert False, "Trying to pop when FILO is empty."
    else:
        dut.pop.value = 1
        await RisingEdge(dut.clk)
        dut.pop.value = 0
        await Timer(20, units='ns')
        popped_value = int(dut.data_out.value) & ((1 << DATA_WIDTH) - 1)
        dut._log.info(f"Popped value: {hex(popped_value)}")
        assert popped_value == expected_value, f"Expected {hex(expected_value)}, but got {hex(popped_value)}"

@cocotb.test()
async def test_filo_dynamic(dut):
    """ Test FILO_RTL behavior with parameters dynamically retrieved from DUT """

    # Retrieve parameters from the DUT
    DATA_WIDTH = int(dut.DATA_WIDTH.value)
    FILO_DEPTH = int(dut.FILO_DEPTH.value)

    # Start the clock generation
    cocotb.start_soon(clock_gen(dut))

    # Initialize signals
    dut.push.value = 0
    dut.pop.value = 0
    dut.data_in.value = 0
    dut.reset.value = 0

    # Apply initial reset
    dut._log.info("Starting Initial Reset...")
    await apply_reset(dut)
    await RisingEdge(dut.clk)
    dut._log.info(f"After initial reset: full = {dut.full.value}, empty = {dut.empty.value}")
    
    # Initial assertions after reset
    assert dut.empty.value == 1, "FILO should be empty after reset"
    assert dut.full.value == 0, "FILO should not be full after reset"

    # List to store the random values pushed into FILO
    pushed_values = []

    # Push Test: Push random data into the FILO buffer
    dut._log.info(f"Starting Push Test with random data width {DATA_WIDTH} and FILO depth {FILO_DEPTH}...")
    for _ in range(FILO_DEPTH):
        await push_data(dut, pushed_values, DATA_WIDTH)

    await RisingEdge(dut.clk)
    dut._log.info(f"After pushing: full = {dut.full.value}, empty = {dut.empty.value}")
    assert dut.full.value == 1, "FILO should be full after pushing FILO_DEPTH elements"
    assert dut.empty.value == 0, "FILO should not be empty after pushing"

    # Pop Test: Pop data from the FILO buffer in reverse order
    dut._log.info("Starting Pop Test...")
    while pushed_values:
        expected_value = pushed_values.pop()
        await pop_data(dut, expected_value, DATA_WIDTH)

    dut._log.info(f"After popping: full = {dut.full.value}, empty = {dut.empty.value}")
    assert dut.empty.value == 1, "FILO should be empty after all values are popped"
    assert dut.full.value == 0, "FILO should not be full after all values are popped"

    # Feedthrough Test: Push and pop in the same cycle when empty
    dut._log.info("Starting Feedthrough Test...")
    await apply_reset(dut)
    await Timer(10, units='ns')

    if dut.empty.value == 1:
        feedthrough_value = random.randint(0, (1 << DATA_WIDTH) - 1)
        dut.push.value = 1
        dut.pop.value = 1
        dut.data_in.value = feedthrough_value
        dut._log.info(f"Feedthrough pushed value: {hex(feedthrough_value)}")
        await RisingEdge(dut.clk)
        await Timer(10, units='ns')
        popped_value = int(dut.data_out.value) & ((1 << DATA_WIDTH) - 1)
        dut._log.info(f"Feedthrough popped value: {hex(popped_value)}")
        assert popped_value == feedthrough_value, f"Feedthrough test failed, expected {hex(feedthrough_value)}"
        dut.push.value = 0
        dut.pop.value = 0
    else:
        assert False, "Error: FILO is not empty before feedthrough test."

    # Final check
    await RisingEdge(dut.clk)
    dut._log.info(f"Final status: full = {dut.full.value}, empty = {dut.empty.value}")

    # Extend simulation time to ensure all outputs are captured
    await Timer(100, units='ns')
