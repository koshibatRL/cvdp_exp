# tests/test_prim_max_find.py

import cocotb
from cocotb.triggers import RisingEdge, Timer
import random
import os

@cocotb.test()
async def test_prim_max_find(dut):
    """
    Generic Testbench for the prim_max_find module using cocotb.
    It dynamically adapts to different NumSrc and Width configurations
    based on environment variables.
    """

    # ----------------------------
    # Retrieve Parameters
    # ----------------------------
    # Fetch parameters from environment variables set via Makefile
    num_src = len(dut.valid_i)
    width = len(dut.max_value_o)
    src_width = (num_src - 1).bit_length()
    num_levels = (num_src - 1).bit_length()
    num_nodes = 2**(num_levels + 1) - 1

    dut._log.info(f"Running test with NumSrc={num_src}, Width={width}")

    # ----------------------------
    # Clock Generation
    # ----------------------------
    async def clock_gen():
        """
        Generates a clock signal by toggling clk_i every 5 ns.
        """
        while True:
            dut.clk_i.value = 0
            await Timer(5, units='ns')
            dut.clk_i.value = 1
            await Timer(5, units='ns')

    # Start the clock
    cocotb.start_soon(clock_gen())

    # ----------------------------
    # Reset Handling
    # ----------------------------
    async def reset_dut():
        """
        Asserts and de-asserts the reset signal.
        """
        dut.rst_ni.value = 0  # Assert reset (active low)
        await RisingEdge(dut.clk_i)
        await RisingEdge(dut.clk_i)
        dut.rst_ni.value = 1  # De-assert reset
        await RisingEdge(dut.clk_i)

    # Apply reset
    await reset_dut()

    # ----------------------------
    # Helper Function to Assign Values
    # ----------------------------
    def assign_test_values(value_list):
        """
        Assigns a list of values to the DUT's values_i signal.
        Only the first num_src values are assigned.
        """
        test_values = 0
        for j, val in enumerate(value_list):
            if j >= num_src:
                break  # Ignore values beyond num_src
            test_values |= (val << (j * width))
        return test_values

    # ----------------------------
    # Apply Test Task
    # ----------------------------
    async def apply_test(test_values, test_valids, expected_max_value, expected_max_index, expected_valid):
        """
        Applies a single test case to the DUT and checks the results.
        """
        # Assign test values and valids
        dut.values_i.value = test_values
        dut.valid_i.value = test_valids

        # Wait for one rising edge to apply inputs
        await RisingEdge(dut.clk_i)

        # Wait for pipeline latency (similar to Verilog's repeat($clog2(NumSrc)+1))
        for _ in range(num_levels + 1):
            await RisingEdge(dut.clk_i)

        # Capture DUT outputs
        dut_max_value = int(dut.max_value_o.value.integer)
        dut_max_idx = int(dut.max_idx_o.value.integer)
        dut_max_valid = int(dut.max_valid_o.value.integer)

        # Check results
        if expected_valid:
            # When expected_valid is True, verify all outputs
            if (dut_max_value != expected_max_value or
                dut_max_idx != expected_max_index or
                dut_max_valid != expected_valid):
                dut._log.error(f"Test failed:")
                dut._log.error(f"  Input values: {test_values:0{width*num_src}b}")
                dut._log.error(f"  Input valids: {test_valids:0{num_src}b}")
                dut._log.error(f"  Expected max value: {expected_max_value}, Got: {dut_max_value}")
                dut._log.error(f"  Expected max index: {expected_max_index}, Got: {dut_max_idx}")
                dut._log.error(f"  Expected valid: {expected_valid}, Got: {dut_max_valid}")
                assert False, "Test case failed."
            else:
                dut._log.info("Test passed.")
        else:
            # When expected_valid is False, only verify that max_valid_o is 0
            if dut_max_valid != expected_valid:
                dut._log.error(f"Test failed:")
                dut._log.error(f"  Input values: {test_values:0{width*num_src}b}")
                dut._log.error(f"  Input valids: {test_valids:0{num_src}b}")
                dut._log.error(f"  Expected valid: {expected_valid}, Got: {dut_max_valid}")
                assert False, "Test case failed."
            else:
                dut._log.info("Test passed.")

    # ----------------------------
    # Randomized Test Task
    # ----------------------------
    async def random_test(num_iterations):
        """
        Performs randomized testing by generating random inputs and verifying outputs.
        """
        for i in range(num_iterations):
            # Generate random values and valids
            rand_values = 0
            rand_valids = 0
            rand_array = []
            for j in range(num_src):
                val = random.randint(0, 2**width - 1)
                rand_array.append(val)
                rand_values |= (val << (j * width))
                if random.randint(0, 1):
                    rand_valids |= (1 << j)

            # Compute expected max and index
            expected_max = 0
            expected_idx = 0
            any_valid = False
            for j in range(num_src):
                if (rand_valids >> j) & 1:
                    if not any_valid or rand_array[j] > expected_max:
                        expected_max = rand_array[j]
                        expected_idx = j
                        any_valid = True

            if not any_valid:
                expected_max = 0
                expected_idx = 0

            # Apply the test
            try:
                await apply_test(rand_values, rand_valids, expected_max, expected_idx, any_valid)
                dut._log.info(f"Random Test {i+1}/{num_iterations} passed.")
            except AssertionError:
                dut._log.error(f"Random Test {i+1}/{num_iterations} failed.")
                raise

    # ----------------------------
    # Specific Test Cases
    # ----------------------------

    # Test Case 1: All invalid inputs
    test_values = 0  # All values zero
    test_valids = 0  # All valids zero
    await apply_test(
        test_values=test_values,
        test_valids=test_valids,
        expected_max_value=0,
        expected_max_index=0,
        expected_valid=0
    )

    # Test Case 2: Single valid input
    test_values = assign_test_values([10] + [0]*(num_src-1))  # Set first input to 10
    test_valids = (1 << 0)  # Only first input is valid
    await apply_test(
        test_values=test_values,
        test_valids=test_valids,
        expected_max_value=10,
        expected_max_index=0,
        expected_valid=1
    )

    # Test Case 3: Multiple valid inputs with distinct values
    # Example: [10, 20, 30, 40, 5, 25, 15, 35]
    values_tc3 = [10, 20, 30, 40, 5, 25, 15, 35]
    test_values = assign_test_values(values_tc3)
    test_valids = (1 << min(len(values_tc3), num_src)) - 1  # All assigned inputs are valid
    expected_max_value_tc3 = max(values_tc3[:num_src]) if num_src <= len(values_tc3) else max(values_tc3)
    # Find the first occurrence of the max value
    expected_max_index_tc3 = values_tc3[:num_src].index(expected_max_value_tc3)
    await apply_test(
        test_values=test_values,
        test_valids=test_valids,
        expected_max_value=expected_max_value_tc3,
        expected_max_index=expected_max_index_tc3,
        expected_valid=1
    )

    # Test Case 4: Multiple valid inputs with duplicate maximum values
    # Example: [10, 40, 30, 40, 5, 25, 15, 35]
    values_tc4 = [10, 40, 30, 40, 5, 25, 15, 35]
    test_values = assign_test_values(values_tc4)
    test_valids = (1 << min(len(values_tc4), num_src)) - 1  # All assigned inputs are valid
    # Find the first occurrence of the max value
    if len(values_tc4) >= num_src:
        assigned_values_tc4 = values_tc4[:num_src]
    else:
        assigned_values_tc4 = values_tc4
    expected_max_value_tc4 = max(assigned_values_tc4)
    expected_max_index_tc4 = assigned_values_tc4.index(expected_max_value_tc4)
    await apply_test(
        test_values=test_values,
        test_valids=test_valids,
        expected_max_value=expected_max_value_tc4,
        expected_max_index=expected_max_index_tc4,  # First occurrence
        expected_valid=1
    )

    # Test Case 5: Random valid patterns
    # Example: [50, 0, 10, 0, 100, 0, 5, 0]
    values_tc5 = [50, 0, 10, 0, 100, 0, 5, 0]
    test_values = assign_test_values(values_tc5)
    # Manually set valid bits: indices 0,2,4,6
    test_valids = 0
    for idx in [0, 2, 4, 6]:
        if idx < num_src:
            test_valids |= (1 << idx)
    # Compute expected max value and index
    assigned_values_tc5 = [50, 0, 10, 0, 100, 0, 5, 0][:num_src]
    max_valid_values_tc5 = [v for v, valid in zip(assigned_values_tc5, [bool(test_valids & (1 << j)) for j in range(num_src)]) if valid]
    if max_valid_values_tc5:
        expected_max_value_tc5 = max(max_valid_values_tc5)
        expected_max_index_tc5 = assigned_values_tc5.index(expected_max_value_tc5)
    else:
        expected_max_value_tc5 = 0
        expected_max_index_tc5 = 0

    await apply_test(
        test_values=test_values,
        test_valids=test_valids,
        expected_max_value=expected_max_value_tc5,
        expected_max_index=expected_max_index_tc5,
        expected_valid=1
    )

    # ----------------------------
    # Randomized Test Cases
    # ----------------------------
    dut._log.info("Starting randomized tests...")
    await random_test(num_iterations=10)
    dut._log.info("All randomized tests passed.")

    # ----------------------------
    # End of Test
    # ----------------------------
    dut._log.info("All tests completed successfully.")
