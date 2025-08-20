import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

async def initialize_dut(dut):
    """Initialize the DUT by starting the clock and applying reset."""
    # Start a 10 ns period clock.
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Apply reset.
    dut.reset.value = 1
    dut.data_valid.value = 0
    dut.data_in.value = 0
    dut.window_size.value = 0
    for _ in range(2):
        await RisingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.clk)
    dut._log.info("Initialization complete: reset de-asserted.")


@cocotb.test()
async def test_window_based_accumulation(dut):
    """
    Test window-based accumulation (ACCUM_MODE == 1).

    This test sets a window size and applies a sequence of valid inputs.
    It then verifies that the sum, average, and sum_ready signals are as expected.
    """
    accum_mode = int(os.getenv("PARAM_ACCUM_MODE", "0"))
    if accum_mode != 1:
        dut._log.info("Skipping window-based accumulation test because ACCUM_MODE != 1")
        return

    await initialize_dut(dut)

    # Set window size for the test.
    window_size = 3
    dut.window_size.value = window_size
    dut._log.info(f"Window-based test: window_size set to {window_size}")

    # Retrieve the WEIGHT parameter from the environment.
    weight = int(os.getenv("PARAM_WEIGHT", "1"))
    # Define a sequence of input values.
    inputs = [5, 10, -3]
    expected_sum = sum([x * weight for x in inputs])
    expected_avg = int(expected_sum / window_size)

    # Feed inputs with data_valid asserted.
    for cycle, value in enumerate(inputs):
        dut.data_in.value = value
        dut.data_valid.value = 1
        await RisingEdge(dut.clk)
        dut._log.info(f"Cycle {cycle}: data_in = {value}, weighted = {value * weight}")

    # Allow one extra cycle for outputs to latch.
    await RisingEdge(dut.clk)
    if int(dut.sum_ready.value) == 1:
        dut._log.info("Window-based test: sum_ready asserted as expected.")
    else:
        dut._log.error("Window-based test: sum_ready NOT asserted.")

    if int(dut.sum_out.value) == expected_sum:
        dut._log.info(f"Window-based test: sum_out is correct: {dut.sum_out.value} (expected {expected_sum}).")
    else:
        dut._log.error(f"Window-based test: sum_out is {dut.sum_out.value}, expected {expected_sum}.")

    if int(dut.avg_out.value) == expected_avg:
        dut._log.info(f"Window-based test: avg_out is correct: {dut.avg_out.value} (expected {expected_avg}).")
    else:
        dut._log.error(f"Window-based test: avg_out is {dut.avg_out.value}, expected {expected_avg}.")

    # Extra cycles before finishing.
    for _ in range(2):
        await RisingEdge(dut.clk)
    dut._log.info("Window-based accumulation test completed.")


@cocotb.test()
async def test_threshold_based_accumulation(dut):
    """
    Test threshold-based accumulation (ACCUM_MODE == 0).

    This test applies a sequence of valid inputs that should trigger threshold events.
    It verifies that threshold_1, threshold_2, sum_ready, and sum_out are correctly set.
    """
    accum_mode = int(os.getenv("PARAM_ACCUM_MODE", "0"))
    if accum_mode != 0:
        dut._log.info("Skipping threshold-based accumulation test because ACCUM_MODE != 0")
        return

    await initialize_dut(dut)

    # For threshold-based mode, window_size is not used.
    dut.window_size.value = 0

    weight = int(os.getenv("PARAM_WEIGHT", "1"))
    # Get threshold values (passed as parameters).
    THRESHOLD_VALUE_1 = int(os.getenv("PARAM_THRESHOLD_VALUE_1", "50"))
    THRESHOLD_VALUE_2 = int(os.getenv("PARAM_THRESHOLD_VALUE_2", "100"))
    # Define a sequence of inputs.
    inputs = [10, 15, -5, 3]
    accumulated = 0

    for cycle, value in enumerate(inputs):
        dut.data_in.value = value
        dut.data_valid.value = 1
        await RisingEdge(dut.clk)
        weighted = value * weight
        accumulated += weighted
        threshold1_expected = (accumulated >= THRESHOLD_VALUE_1 or accumulated <= -THRESHOLD_VALUE_1)
        threshold2_expected = (accumulated >= THRESHOLD_VALUE_2 or accumulated <= -THRESHOLD_VALUE_2)
        dut._log.info(f"Cycle {cycle}: data_in = {value}, weighted = {weighted}, accumulated = {accumulated}")
        dut._log.info(f"Cycle {cycle}: expected threshold_1 = {threshold1_expected}, threshold_2 = {threshold2_expected}")

        if int(dut.threshold_1.value) != int(threshold1_expected):
            dut._log.error(f"Cycle {cycle}: threshold_1 mismatch: got {dut.threshold_1.value}, expected {threshold1_expected}")
        else:
            dut._log.info(f"Cycle {cycle}: threshold_1 is correct.")

        if int(dut.threshold_2.value) != int(threshold2_expected):
            dut._log.error(f"Cycle {cycle}: threshold_2 mismatch: got {dut.threshold_2.value}, expected {threshold2_expected}")
        else:
            dut._log.info(f"Cycle {cycle}: threshold_2 is correct.")

        if threshold1_expected or threshold2_expected:
            if int(dut.sum_ready.value) != 1:
                dut._log.error(f"Cycle {cycle}: sum_ready expected 1, got {dut.sum_ready.value}")
            else:
                dut._log.info(f"Cycle {cycle}: sum_ready asserted as expected.")
            if int(dut.sum_out.value) != accumulated:
                dut._log.error(f"Cycle {cycle}: sum_out mismatch: got {dut.sum_out.value}, expected {accumulated}")
            else:
                dut._log.info(f"Cycle {cycle}: sum_out is correct.")
        else:
            if int(dut.sum_ready.value) != 0:
                dut._log.error(f"Cycle {cycle}: sum_ready expected 0, got {dut.sum_ready.value}")

    dut.data_valid.value = 0
    await RisingEdge(dut.clk)
    dut._log.info("Threshold-based accumulation test completed.")


@cocotb.test()
async def test_reset_behavior(dut):
    """
    Test reset behavior.

    This test applies a few inputs, then asserts reset mid-operation.
    It checks that all relevant signals (sum_out, avg_out, sum_ready) return to 0.
    """
    await initialize_dut(dut)

    weight = int(os.getenv("PARAM_WEIGHT", "1"))
    inputs = [10, 20]
    for value in inputs:
        dut.data_in.value = value
        dut.data_valid.value = 1
        await RisingEdge(dut.clk)
        dut._log.info(f"Before reset: data_in = {value}, weighted = {value * weight}")

    # Assert reset in the middle of operation.
    dut._log.info("Asserting reset mid-operation.")
    dut.reset.value = 1
    dut.data_valid.value = 0
    await RisingEdge(dut.clk)

    # Check that outputs have been cleared.
    if int(dut.sum_out.value) == 0 and int(dut.avg_out.value) == 0 and int(dut.sum_ready.value) == 0:
        dut._log.info("Reset behavior: Outputs are reset as expected.")
    else:
        dut._log.error(
            f"Reset behavior: Outputs not reset (sum_out={dut.sum_out.value}, "
            f"avg_out={dut.avg_out.value}, sum_ready={dut.sum_ready.value})."
        )

    dut.reset.value = 0
    await RisingEdge(dut.clk)
    dut._log.info("Reset behavior test completed.")


@cocotb.test()
async def test_no_data_valid(dut):
    """
    Test that no accumulation occurs when data_valid is de-asserted.

    This test drives data_in with changes while data_valid remains low,
    verifying that the accumulated sum (sum_out) does not update.
    """
    await initialize_dut(dut)

    weight = int(os.getenv("PARAM_WEIGHT", "1"))
    initial_sum = int(dut.sum_out.value)

    for value in [15, -8, 5]:
        dut.data_in.value = value
        dut.data_valid.value = 0
        await RisingEdge(dut.clk)
        dut._log.info(f"data_valid low: data_in = {value} (weighted = {value * weight}); no update expected.")
        if int(dut.sum_out.value) != initial_sum:
            dut._log.error(f"Unexpected update: sum_out changed to {dut.sum_out.value} (expected {initial_sum}).")
        else:
            dut._log.info("No update in sum_out as expected.")

    dut._log.info("Test for no data_valid updates completed.")
