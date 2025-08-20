import cocotb
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock
from cocotb.regression import TestFactory
import random
import os

@cocotb.test()
async def test_continuous_adder(dut):
    """
    Test the cont_adder_complex module in both continuous and fixed-window modes.
    """
    # Retrieve parameters from environment variables
    parameters = {
        "DATA_WIDTH": int(os.getenv("PARAM_DATA_WIDTH", "32")),
        "THRESHOLD_VALUE_1": int(os.getenv("PARAM_THRESHOLD_VALUE_1", "50")),
        "THRESHOLD_VALUE_2": int(os.getenv("PARAM_THRESHOLD_VALUE_2", "100")),
        "THRESHOLD_VALUE_3": int(os.getenv("PARAM_THRESHOLD_VALUE_3", "150")),
        "SIGNED_INPUTS": int(os.getenv("PARAM_SIGNED_INPUTS", "1")),
        "WEIGHT": int(os.getenv("PARAM_WEIGHT", "1")),
        "ACCUM_MODE": int(os.getenv("PARAM_ACCUM_MODE", "0")),
    }

    dut._log.info(f"Testing with parameters: {parameters}")

    # Set up the clock (10 ns period)
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Reset and initialize control signals
    dut.reset.value      = 1
    dut.enable.value     = 0
    dut.accum_clear.value= 0
    dut.data_valid.value = 0
    dut.data_in.value    = 0
    dut.window_size.value= 4  # Relevant in fixed-window mode
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.reset.value      = 0
    dut.enable.value     = 1  # Enable accumulation

    mode_str = "Continuous" if parameters["ACCUM_MODE"] == 0 else "Fixed-Window"
    dut._log.info(f"Testing {mode_str} Mode...")

    # Data sequence to send
    data_sequence = [10, 20, 30, 40, 50, 60, 70, 80]

    for i, data in enumerate(data_sequence):
        # Apply data
        dut.data_in.value = data
        dut.data_valid.value = 1
        dut._log.info(f"Sending data: {data} at time {cocotb.simulator.get_sim_time()} ns")
        await RisingEdge(dut.clk)
        dut.data_valid.value = 0

        # Wait one clock cycle
        await RisingEdge(dut.clk)

        # Log outputs (including new ports: threshold_3 and busy)
        if parameters["ACCUM_MODE"] == 0:
            dut._log.info(f"Cycle {i} (Continuous):")
            dut._log.info(f"  data_in       = {dut.data_in.value.signed_integer}")
            dut._log.info(f"  threshold_1   = {dut.threshold_1.value}")
            dut._log.info(f"  threshold_2   = {dut.threshold_2.value}")
            dut._log.info(f"  threshold_3   = {dut.threshold_3.value}")
            dut._log.info(f"  sum_ready     = {dut.sum_ready.value}")
            dut._log.info(f"  sum_out       = {dut.sum_out.value.signed_integer}")
            dut._log.info(f"  avg_out       = {dut.avg_out.value.signed_integer}")
            dut._log.info(f"  busy          = {dut.busy.value}")
            if dut.sum_ready.value == 1:
                dut._log.info(f"  Sum Ready! sum_out={dut.sum_out.value.signed_integer} at time {cocotb.simulator.get_sim_time()} ns")
            dut._log.info("")
        else:
            dut._log.info(f"Cycle {i} (Fixed-Window):")
            dut._log.info(f"  data_in       = {dut.data_in.value.signed_integer}")
            dut._log.info(f"  threshold_1   = {dut.threshold_1.value}")
            dut._log.info(f"  threshold_2   = {dut.threshold_2.value}")
            dut._log.info(f"  threshold_3   = {dut.threshold_3.value}")
            dut._log.info(f"  sum_ready     = {dut.sum_ready.value}")
            dut._log.info(f"  sum_out       = {dut.sum_out.value.signed_integer}")
            dut._log.info(f"  avg_out       = {dut.avg_out.value.signed_integer}")
            dut._log.info(f"  busy          = {dut.busy.value}")
            if dut.sum_ready.value == 1:
                dut._log.info(f"  Sum Ready! sum_out={dut.sum_out.value.signed_integer}, avg_out={dut.avg_out.value.signed_integer} at time {cocotb.simulator.get_sim_time()} ns")
            dut._log.info("")

        await RisingEdge(dut.clk)

    dut._log.info("Test completed.")


@cocotb.test()
async def run_random_test(dut):
    """
    Test the cont_adder_complex module with random inputs.
    """
    parameters = {
        "ACCUM_MODE": int(os.getenv("PARAM_ACCUM_MODE", "0")),
        "THRESHOLD_VALUE_1": int(os.getenv("PARAM_THRESHOLD_VALUE_1", "50")),
        "THRESHOLD_VALUE_2": int(os.getenv("PARAM_THRESHOLD_VALUE_2", "100")),
        "THRESHOLD_VALUE_3": int(os.getenv("PARAM_THRESHOLD_VALUE_3", "150")),
        "WEIGHT": int(os.getenv("PARAM_WEIGHT", "1"))
    }
    ACCUM_MODE = parameters["ACCUM_MODE"]

    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Reset and initialize control signals
    dut.reset.value       = 1
    dut.enable.value      = 0
    dut.accum_clear.value = 0
    dut.data_valid.value  = 0
    dut.data_in.value     = 0
    window_size = random.randint(1, 8)
    dut.window_size.value = window_size
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.reset.value       = 0
    dut.enable.value      = 1

    if ACCUM_MODE == 1:
        dut._log.info(f"Window size set to: {window_size}")

    num_transactions = 8
    mode_str = "Continuous" if ACCUM_MODE == 0 else "Fixed-Window"
    dut._log.info(f"Testing Random Inputs in {mode_str} Mode...")

    for i in range(num_transactions):
        data = random.randint(0, 40)
        dut.data_in.value = data
        dut.data_valid.value = 1
        dut._log.info(f"Sending data: {data} at time {cocotb.simulator.get_sim_time()} ns")
        await RisingEdge(dut.clk)
        dut.data_valid.value = 0

        await RisingEdge(dut.clk)

        if ACCUM_MODE == 0:
            dut._log.info(f"Cycle {i} (Continuous):")
            dut._log.info(f"  data_in       = {dut.data_in.value.signed_integer}")
            dut._log.info(f"  threshold_1   = {dut.threshold_1.value}")
            dut._log.info(f"  threshold_2   = {dut.threshold_2.value}")
            dut._log.info(f"  threshold_3   = {dut.threshold_3.value}")
            dut._log.info(f"  sum_ready     = {dut.sum_ready.value}")
            dut._log.info(f"  sum_out       = {dut.sum_out.value.signed_integer}")
            dut._log.info(f"  busy          = {dut.busy.value}")
            if dut.sum_ready.value == 1:
                dut._log.info(f"  Sum Ready! sum_out={dut.sum_out.value.signed_integer} at time {cocotb.simulator.get_sim_time()} ns")
            dut._log.info("")
        else:
            dut._log.info(f"Cycle {i} (Fixed-Window):")
            dut._log.info(f"  data_in       = {dut.data_in.value.signed_integer}")
            dut._log.info(f"  threshold_1   = {dut.threshold_1.value}")
            dut._log.info(f"  threshold_2   = {dut.threshold_2.value}")
            dut._log.info(f"  threshold_3   = {dut.threshold_3.value}")
            dut._log.info(f"  sum_ready     = {dut.sum_ready.value}")
            dut._log.info(f"  sum_out       = {dut.sum_out.value.signed_integer}")
            dut._log.info(f"  avg_out       = {dut.avg_out.value.signed_integer}")
            dut._log.info(f"  busy          = {dut.busy.value}")
            if dut.sum_ready.value == 1:
                dut._log.info(f"  Sum Ready! sum_out={dut.sum_out.value.signed_integer}, avg_out={dut.avg_out.value.signed_integer} at time {cocotb.simulator.get_sim_time()} ns")
            dut._log.info("")

        await RisingEdge(dut.clk)

    dut._log.info("Random Input Test completed.")


@cocotb.test()
async def test_negative_numbers(dut):
    """
    Test the cont_adder_complex module with a mix of negative and positive numbers.
    """
    parameters = {
        "DATA_WIDTH": int(os.getenv("PARAM_DATA_WIDTH", "32")),
        "THRESHOLD_VALUE_1": int(os.getenv("PARAM_THRESHOLD_VALUE_1", "50")),
        "THRESHOLD_VALUE_2": int(os.getenv("PARAM_THRESHOLD_VALUE_2", "100")),
        "THRESHOLD_VALUE_3": int(os.getenv("PARAM_THRESHOLD_VALUE_3", "150")),
        "SIGNED_INPUTS": int(os.getenv("PARAM_SIGNED_INPUTS", "1")),
        "WEIGHT": int(os.getenv("PARAM_WEIGHT", "1")),
        "ACCUM_MODE": int(os.getenv("PARAM_ACCUM_MODE", "0")),
    }
    ACCUM_MODE = parameters["ACCUM_MODE"]

    if parameters["SIGNED_INPUTS"] != 1:
        dut._log.warning("SIGNED_INPUTS is not enabled. This test requires SIGNED_INPUTS=1.")
        return

    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Reset and initialize control signals
    dut.reset.value       = 1
    dut.enable.value      = 0
    dut.accum_clear.value = 0
    dut.data_valid.value  = 0
    dut.data_in.value     = 0
    dut.window_size.value = 4
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.reset.value       = 0
    dut.enable.value      = 1

    data_sequence = [-30, 20, -10, 40, -50, 60, -70, 80]
    mode_str = "Continuous" if ACCUM_MODE == 0 else "Fixed-Window"
    dut._log.info(f"Testing Negative Numbers in {mode_str} Mode...")

    for i, data in enumerate(data_sequence):
        dut.data_in.value = data
        dut.data_valid.value = 1
        dut._log.info(f"Sending data: {data} at time {cocotb.simulator.get_sim_time()} ns")
        await RisingEdge(dut.clk)
        dut.data_valid.value = 0

        await RisingEdge(dut.clk)

        if ACCUM_MODE == 0:
            dut._log.info(f"Cycle {i} (Continuous):")
            dut._log.info(f"  data_in       = {dut.data_in.value.signed_integer}")
            dut._log.info(f"  threshold_1   = {dut.threshold_1.value}")
            dut._log.info(f"  threshold_2   = {dut.threshold_2.value}")
            dut._log.info(f"  threshold_3   = {dut.threshold_3.value}")
            dut._log.info(f"  sum_ready     = {dut.sum_ready.value}")
            dut._log.info(f"  sum_out       = {dut.sum_out.value.signed_integer}")
            dut._log.info(f"  busy          = {dut.busy.value}")
            if dut.sum_ready.value == 1:
                dut._log.info(f"  Sum Ready! sum_out={dut.sum_out.value.signed_integer} at time {cocotb.simulator.get_sim_time()} ns")
            dut._log.info("")
        else:
            dut._log.info(f"Cycle {i} (Fixed-Window):")
            dut._log.info(f"  data_in       = {dut.data_in.value.signed_integer}")
            dut._log.info(f"  threshold_1   = {dut.threshold_1.value}")
            dut._log.info(f"  threshold_2   = {dut.threshold_2.value}")
            dut._log.info(f"  threshold_3   = {dut.threshold_3.value}")
            dut._log.info(f"  sum_ready     = {dut.sum_ready.value}")
            dut._log.info(f"  sum_out       = {dut.sum_out.value.signed_integer}")
            dut._log.info(f"  avg_out       = {dut.avg_out.value.signed_integer}")
            dut._log.info(f"  busy          = {dut.busy.value}")
            if dut.sum_ready.value == 1:
                dut._log.info(f"  Sum Ready! sum_out={dut.sum_out.value.signed_integer}, avg_out={dut.avg_out.value.signed_integer} at time {cocotb.simulator.get_sim_time()} ns")
            dut._log.info("")

        await RisingEdge(dut.clk)

    dut._log.info("Negative Number Test completed.")
