import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ReadOnly, Timer

import harness_library as hrs_lb
import random

@cocotb.test()
async def test_Bit_Difference_Counter(dut):

    # Parameters
    BIT_WIDTH = int(dut.BIT_WIDTH.value)
    COUNT_WIDTH = int(dut.COUNT_WIDTH.value)

    # Log the configuration
    dut._log.info(f"Testing Bit_Difference_Counter with BIT_WIDTH={BIT_WIDTH}")

    # Case 1: Minimum Difference (input_A and input_B are identical)
    input_A = random.randint(0, (1 << BIT_WIDTH) - 1)
    input_B = input_A  # Identical inputs for minimum difference

    # Apply inputs
    dut.input_A.value = input_A
    dut.input_B.value = input_B

    # Wait for the outputs to stabilize
    await Timer(10, units="ns")

    # Expected count is 0 since both inputs are identical
    expected_count = 0
    observed_count = int(dut.bit_difference_count.value)
    assert observed_count == expected_count, (
        f"Minimum difference test failed for input_A={input_A:0{BIT_WIDTH}b}, input_B={input_B:0{BIT_WIDTH}b}. "
        f"Expected: {expected_count}, Got: {observed_count}."
    )
    dut._log.info(f"Minimum difference test passed for input_A={input_A:0{BIT_WIDTH}b}, input_B={input_B:0{BIT_WIDTH}b}. "
                  f"Expected: {expected_count}, Got: {observed_count}.")

    # Case 2: Maximum Difference (input_A and input_B are bitwise inverses)
    input_A = (1 << BIT_WIDTH) - 1  # All bits set to 1
    input_B = 0  # All bits set to 0

    # Apply inputs
    dut.input_A.value = input_A
    dut.input_B.value = input_B

    # Wait for the outputs to stabilize
    await Timer(10, units="ns")

    # Expected count is the bit width since all bits differ
    expected_count = BIT_WIDTH
    observed_count = int(dut.bit_difference_count.value)
    assert observed_count == expected_count, (
        f"Maximum difference test failed for input_A={input_A:0{BIT_WIDTH}b}, input_B={input_B:0{BIT_WIDTH}b}. "
        f"Expected: {expected_count}, Got: {observed_count}."
    )
    dut._log.info(f"Maximum difference test passed for input_A={input_A:0{BIT_WIDTH}b}, input_B={input_B:0{BIT_WIDTH}b}. "
                  f"Expected: {expected_count}, Got: {observed_count}.")


    # Test multiple random cases
    for _ in range(20):  # Run 20 test cases
        # Generate random input vectors of width BIT_WIDTH
        input_A = random.randint(0, (1 << BIT_WIDTH) - 1)  
        input_B = random.randint(0, (1 << BIT_WIDTH) - 1)  

        # Apply inputs
        dut.input_A.value = input_A
        dut.input_B.value = input_B

        # Wait for the outputs to stabilize
        await Timer(10, units="ns")

        # Calculate expected Hamming distance
        xor_result = input_A ^ input_B
        expected_count = bin(xor_result).count('1')  

        # Format binary values with leading zeros to match BIT_WIDTH
        input_A_binary = f"{input_A:0{BIT_WIDTH}b}"
        input_B_binary = f"{input_B:0{BIT_WIDTH}b}"
        expected_count_binary = f"{expected_count:0{COUNT_WIDTH}b}"
        observed_count = int(dut.bit_difference_count.value)
        observed_count_binary = f"{observed_count:0{COUNT_WIDTH}b}"

        # Check the DUT output against the expected value
        assert observed_count == expected_count, (
            f"Test failed for input_A={input_A_binary}, input_B={input_B_binary}. "
            f"Expected: {expected_count_binary}, Got: {observed_count_binary}."
        )

        # Log the results
        dut._log.info(f"Test passed for input_A={input_A_binary}, input_B={input_B_binary}. "
                      f"Expected: {expected_count_binary}, Got: {observed_count_binary}.")

