###############################################################################
# Cocotb test: Single Parameter per Simulation Run
###############################################################################
# In this script, you do NOT loop over multiple parameter combos. Instead,
# you pick (BIT_ORDER, PARITY) at compile time. This matches how Verilog
# parameters work (resolved at compile/elaboration time).
###############################################################################

import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, with_timeout
from cocotb.result import TestFailure
import asyncio  # Import asyncio to access TimeoutError

@cocotb.test()
async def test_data_serializer_single_param(dut):
    """
    Single-parameter test of data_serializer with added TIMEOUT checks.
    The actual (BIT_ORDER, PARITY) must match how the DUT was compiled.
    For example:
      iverilog -o sim.vvp -s data_serializer \
               -P data_serializer.BIT_ORDER=0 \
               -P data_serializer.PARITY=1 \
               data_serializer.sv

    Then run Cocotb on 'sim.vvp':
      make SIM=icarus TOPLEVEL=data_serializer MODULE=test_data_serializer

    This test will:
      1) Create a clock
      2) Perform a reset
      3) Run three sub-tests:
         - Basic transmission
         - Gating pause/resume
         - Multiple words
      4) If any sub-test times out, we raise TestFailure.
    """

    ###########################################################################
    # 1) Set up clock + default signals
    ###########################################################################
    cocotb.start_soon(Clock(dut.clk, 5, "ns").start())

    # By default, let's assume s_ready_i=1 (always ready)
    # and tx_en_i=1 (enabled).
    dut.s_ready_i.value = 1
    dut.tx_en_i.value   = 1
    dut.reset.value     = 0

    ###########################################################################
    # 2) Identify the compiled param values
    #    (Optionally read environment variables or just keep "doc" info)
    ###########################################################################
    # If you'd like, you can parse environment variables to document them:
    # But the DUT *itself* is compiled with certain param values.
    # We'll read them for clarity/logging only.
    bit_order = int(dut.BIT_ORDER.value)  # optional
    parity    = int(dut.PARITY.value)    # optional

    dut._log.info(f"Running with BIT_ORDER={bit_order}, PARITY={parity} (compile-time).")

    ###########################################################################
    # 3) Reset the DUT
    ###########################################################################
    try:
        await with_timeout(reset_dut(dut), 2000, "ns")
    except asyncio.TimeoutError:
        raise TestFailure("Timeout: reset_dut did not complete in time!")

    ###########################################################################
    # 4) Run the three sub-tests with separate timeouts
    ###########################################################################
    # Define timeout durations (in nanoseconds)
    BASIC_TRANSMISSION_TIMEOUT = 5000  # Adjust as needed
    GATING_PAUSE_RESUME_TIMEOUT = 5000  # Adjust as needed
    MULTIPLE_WORDS_TIMEOUT = 5000  # Adjust as needed

    # 4.1) Basic Transmission
    try:
        await with_timeout(test_basic_transmission(dut, bit_order, parity), BASIC_TRANSMISSION_TIMEOUT, "ns")
    except asyncio.TimeoutError:
        raise TestFailure("Timeout: test_basic_transmission took too long!")

    # 4.2) Gating Pause/Resume
    try:
        await with_timeout(test_gating_pause_resume(dut, bit_order, parity), GATING_PAUSE_RESUME_TIMEOUT, "ns")
    except asyncio.TimeoutError:
        raise TestFailure("Timeout: test_gating_pause_resume took too long!")

    # 4.3) Multiple Words
    try:
        await with_timeout(test_multiple_words(dut, bit_order, parity), MULTIPLE_WORDS_TIMEOUT, "ns")
    except asyncio.TimeoutError:
        raise TestFailure("Timeout: test_multiple_words took too long!")

    dut._log.info(f"All sub-tests PASSED for (BIT_ORDER={bit_order}, PARITY={parity}).")


###############################################################################
# DUT Reset
###############################################################################
async def reset_dut(dut, cycles=4):
    """Drive reset=1 for 'cycles' clock edges, then deassert it."""
    dut.reset.value = 1
    for _ in range(cycles):
        await RisingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.clk)


###############################################################################
# Test 1: Basic Transmission
###############################################################################
async def test_basic_transmission(dut, bit_order, parity):
    """
    Sends vectors [0xAA, 0x55, 0xF0, 0x0F] => captures & checks correctness.
    """
    dut._log.info("[TEST] Basic Transmission")
    test_vectors = [0xAA, 0x55, 0xF0, 0x0F]

    for vec in test_vectors:
        await send_parallel_data(dut, vec)
        await capture_word_and_compare(dut, vec, bit_order, parity)
        await Timer(10, units="ns")

    dut._log.info("[TEST] Basic Transmission => PASSED")


###############################################################################
# Test 2: Gating Pause/Resume
###############################################################################
async def test_gating_pause_resume(dut, bit_order, parity):
    """
    Send a single word, pause after 4 bits, resume, verify final bits.
    """
    dut._log.info("[TEST] Gating Pause/Resume")
    test_data = 0xA5

    # Start concurrency: send & capture
    send_coro = cocotb.start_soon(_send_and_capture(dut, test_data, bit_order, parity))

    # Wait until 4 bits have been seen
    bits_seen = 0
    timeout_cycles = 1000
    cycles = 0
    while bits_seen < 4:
        await RisingEdge(dut.clk)
        cycles += 1
        if cycles > timeout_cycles:
            raise TestFailure("Timeout waiting for 4 bits before pausing.")
        if dut.s_valid_o.value and dut.s_ready_i.value and dut.tx_en_i.value:
            bits_seen += 1

    # Pause
    dut.tx_en_i.value = 0
    dut._log.info("Paused after 4 bits...")
    await Timer(30, units="ns")

    # Resume
    dut.tx_en_i.value = 1
    dut._log.info("Resumed transmission.")

    # Wait for concurrency to finish
    await send_coro

    dut._log.info("[TEST] Gating Pause/Resume => PASSED")


async def _send_and_capture(dut, data, bit_order, parity):
    """Helper: send data then capture SHIFT_W bits."""
    await send_parallel_data(dut, data)
    await capture_word_and_compare(dut, data, bit_order, parity)


###############################################################################
# Test 3: Multiple Words
###############################################################################
async def test_multiple_words(dut, bit_order, parity):
    """
    Send [0x12, 0x34, 0xAB], capturing each, verifying correctness.
    """
    dut._log.info("[TEST] Multiple Words")
    words = [0x12, 0x34, 0xAB]

    for w in words:
        await send_parallel_data(dut, w)
        await capture_word_and_compare(dut, w, bit_order, parity)
        dut._log.info(f"[OK] Word 0x{w:02X} transmitted & verified.")
        await Timer(10, units="ns")

    dut._log.info("[TEST] Multiple Words => PASSED")


###############################################################################
# Helper Routines
###############################################################################
async def send_parallel_data(dut, data):
    """Wait for p_ready_o, then drive p_data_i with p_valid_i=1 for one clock."""
    await wait_for_ready(dut)
    dut.p_data_i.value  = data
    dut.p_valid_i.value = 1
    await RisingEdge(dut.clk)
    dut.p_valid_i.value = 0


async def wait_for_ready(dut, timeout=1000):
    """Busy-wait until p_ready_o==1, with a max of 'timeout' cycles."""
    count = 0
    while True:
        await RisingEdge(dut.clk)
        if dut.p_ready_o.value.integer == 1:
            return
        count += 1
        if count > timeout:
            raise TestFailure("Timeout waiting for p_ready_o == 1")


async def capture_word_and_compare(dut, expected_data, bit_order, parity):
    """
    1) Capture (DATA_W + EXTRA_BIT) bits from s_data_o in ascending time.
       i.e., captured_shift[0] = first bit out, captured_shift[1] = second bit out, etc.
    2) Build the 'expected_shift' in time order as well (MSB-first => reversed).
    3) Compare them. If mismatch => raise TestFailure.
    """

    data_w = 8
    extra_bit = 1 if (parity != 0) else 0
    shift_w = data_w + extra_bit

    captured_shift = 0
    bit_count = 0

    # --------------
    # Part 1) Capture shift_w bits
    # --------------
    while bit_count < shift_w:
        await RisingEdge(dut.clk)
        if dut.s_valid_o.value and dut.s_ready_i.value and dut.tx_en_i.value:
            bit_val = (dut.s_data_o.value.integer & 1)
            # Place new bit in the "time-order" index
            captured_shift |= (bit_val << bit_count)
            bit_count += 1

    # --------------
    # Part 2) Compute parity bit (if any)
    # --------------
    if parity == 0:
        parity_bit = 0
    else:
        # Basic: even => XOR, odd => invert XOR
        xor_val = 0
        for b in range(data_w):
            xor_val ^= ((expected_data >> b) & 1)
        if parity == 1:  # even
            parity_bit = xor_val
        else:            # odd
            parity_bit = xor_val ^ 1

    # --------------
    # Part 3) Build expected_shift in time-order, matching your Verilog TB:
    #     - LSB-first => earliest bit out is data[0], next is data[1], ...
    #     - MSB-first => earliest bit out is data[data_w-1], next => data[data_w-2], ...
    # --------------
    expected_shift = 0
    for i in range(shift_w):
        if bit_order == 0:
            # LSB-first => if i<data_w => data[i], else parity
            if i < data_w:
                bit_i = (expected_data >> i) & 1
            else:
                bit_i = parity_bit
        else:
            # MSB-first => if i<data_w => data[data_w-1 - i], else parity
            if i < data_w:
                bit_i = (expected_data >> (data_w - 1 - i)) & 1
            else:
                bit_i = parity_bit

        expected_shift |= (bit_i << i)

    # --------------
    # Part 4) Compare
    # --------------
    if captured_shift != expected_shift:
        dut._log.error("[ERROR] Mismatch in captured word!")
        dut._log.error(f"  Captured = 0x{captured_shift:X}")
        dut._log.error(f"  Expected = 0x{expected_shift:X}")
        raise TestFailure("Captured serial bits do not match expected pattern.")
