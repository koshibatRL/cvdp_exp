import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles, Timer
import test_runner
import json
import os


async def init_dut(dut):
    dut.rst_in.value     = 1
    dut.seq_in.value    = 1

    await RisingEdge(dut.clk_in)

@cocotb.test()
async def test_reset(dut):
    cocotb.start_soon(Clock(dut.clk_in, 10, units='ns').start())
    await init_dut(dut)

    # Retrieve test_sequence and expected_output from environment variables
    test_sequence = [0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0]  # Sequence at the start
    expected_output = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]  # Detected at position 9

    # ----------------------------------------
    # - Check No Operation
    # ----------------------------------------

    await RisingEdge(dut.clk_in)
    await RisingEdge(dut.clk_in)  # Wait until 2 clocks to de-assert reset
    await RisingEdge(dut.clk_in)  

    # Apply the test sequence with seq_in updated for only one clock cycle
    for i in range(len(test_sequence)):
        await RisingEdge(dut.clk_in)
        dut.seq_in.value = test_sequence[i]
        dut._log.info(f"Input: {dut.seq_in.value}, Decoded Output: {dut.seq_detected.value}, test_sequence: {test_sequence[i]}")
        await FallingEdge(dut.clk_in)
        assert dut.seq_detected.value == 0, f"Error at step {i}"

@cocotb.test()
async def test_detection_at_start(dut):
    cocotb.start_soon(Clock(dut.clk_in, 10, units='ns').start())
    await init_dut(dut)

    # Retrieve test_sequence and expected_output from environment variables
    test_sequence = [0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0]  # Sequence at the start
    expected_output = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]  # Detected at position 9

    # ----------------------------------------
    # - Check No Operation
    # ----------------------------------------

    await RisingEdge(dut.clk_in)
    await RisingEdge(dut.clk_in)  # Wait until 2 clocks to de-assert reset
    dut.rst_in.value = 0
    await RisingEdge(dut.clk_in)  

    # Apply the test sequence with seq_in updated for only one clock cycle
    for i in range(len(test_sequence)):
        await RisingEdge(dut.clk_in)
        dut.seq_in.value = test_sequence[i]
        dut._log.info(f"Input: {dut.seq_in.value}, Decoded Output: {dut.seq_detected.value}, test_sequence: {test_sequence[i]}")
        await FallingEdge(dut.clk_in)
        assert dut.seq_detected.value == expected_output[i], f"Error at step {i}"


@cocotb.test()
async def test_detection_at_end(dut):
    cocotb.start_soon(Clock(dut.clk_in, 10, units='ns').start())
    await init_dut(dut)

    # Retrieve test_sequence and expected_output from environment variables
    test_sequence = [1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0]  # Sequence at the end
    expected_output = [0] * 10 + [0, 0, 0, 1]  # Detected at the last position

    # ----------------------------------------
    # - Check No Operation
    # ----------------------------------------

    await RisingEdge(dut.clk_in)
    await RisingEdge(dut.clk_in)  # Wait until 2 clocks to de-assert reset
    dut.rst_in.value = 0
    await RisingEdge(dut.clk_in)  

    # Apply the test sequence with seq_in updated for only one clock cycle
    for i in range(len(test_sequence)):
        await RisingEdge(dut.clk_in)
        dut.seq_in.value = test_sequence[i]
        dut._log.info(f"Input: {dut.seq_in.value}, Decoded Output: {dut.seq_detected.value}, test_sequence: {test_sequence[i]}")
        await FallingEdge(dut.clk_in)
        assert dut.seq_detected.value == expected_output[i], f"Error at step {i}"

@cocotb.test()
async def test_multiple_occurrences(dut):
    cocotb.start_soon(Clock(dut.clk_in, 10, units='ns').start())
    await init_dut(dut)

    # Retrieve test_sequence and expected_output from environment variables
    test_sequence = [0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0]
    expected_output = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1]  # Two detections
    # ----------------------------------------
    # - Check No Operation
    # ----------------------------------------

    await RisingEdge(dut.clk_in)
    await RisingEdge(dut.clk_in)  # Wait until 2 clocks to de-assert reset
    dut.rst_in.value = 0
    await RisingEdge(dut.clk_in)  

    # Apply the test sequence with seq_in updated for only one clock cycle
    for i in range(len(test_sequence)):
        await RisingEdge(dut.clk_in)
        dut.seq_in.value = test_sequence[i]
        dut._log.info(f"Input: {dut.seq_in.value}, Decoded Output: {dut.seq_detected.value}, test_sequence: {test_sequence[i]}")
        await FallingEdge(dut.clk_in)
        assert dut.seq_detected.value == expected_output[i], f"Error at step {i}"

@cocotb.test()
async def test_noise_before_after(dut):
    cocotb.start_soon(Clock(dut.clk_in, 10, units='ns').start())
    await init_dut(dut)

    # Retrieve test_sequence and expected_output from environment variables
    test_sequence = [1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1]  # Noise before and after
    expected_output = [0] * 13 + [0, 1, 0]  # Detection happens at index 14 (1-clock delay)
    # ----------------------------------------
    # - Check No Operation
    # ----------------------------------------

    await RisingEdge(dut.clk_in)
    await RisingEdge(dut.clk_in)  # Wait until 2 clocks to de-assert reset
    dut.rst_in.value = 0
    await RisingEdge(dut.clk_in)  

    # Apply the test sequence with seq_in updated for only one clock cycle
    for i in range(len(test_sequence)):
        await RisingEdge(dut.clk_in)
        dut.seq_in.value = test_sequence[i]
        dut._log.info(f"Input: {dut.seq_in.value}, Decoded Output: {dut.seq_detected.value}, test_sequence: {test_sequence[i]}")
        await FallingEdge(dut.clk_in)
        assert dut.seq_detected.value == expected_output[i], f"Error at step {i}"

@cocotb.test()
async def test_rtl_bug_seq(dut):
    cocotb.start_soon(Clock(dut.clk_in, 10, units='ns').start())
    await init_dut(dut)

    # Retrieve test_sequence and expected_output from environment variables
    test_sequence = [1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0]  # Overlapping case
    expected_output = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0]  # Two detections
    # ----------------------------------------
    # - Check No Operation
    # ----------------------------------------

    await RisingEdge(dut.clk_in)
    await RisingEdge(dut.clk_in)  # Wait until 2 clocks to de-assert reset
    dut.rst_in.value = 0
    await RisingEdge(dut.clk_in)  

    # Apply the test sequence with seq_in updated for only one clock cycle
    for i in range(len(test_sequence)):
        await RisingEdge(dut.clk_in)
        dut.seq_in.value = test_sequence[i]
        dut._log.info(f"Input: {dut.seq_in.value}, Decoded Output: {dut.seq_detected.value}, test_sequence: {test_sequence[i]}")
        await FallingEdge(dut.clk_in)
        assert dut.seq_detected.value == expected_output[i], f"Error at step {i}"

