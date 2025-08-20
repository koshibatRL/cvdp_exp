import cocotb
from cocotb.triggers import Timer
import math
import random

@cocotb.test()
async def test_cascaded_encoder(dut):
    # Parameters
    N = int(dut.N.value)  # Total number of inputs
    M = int(dut.M.value)  # Output width (log2(N))

    dut._log.info(f"Testing cascaded encoder with N={N}, M={M}")

    # Test random inputs
    for _ in range(5):  # Run 5 test cases
        # Generate a random input vector
        input_vector = random.randint(0, (1 << N) - 1)
        dut.input_signal.value = input_vector  # Updated signal name

        await Timer(10, units="ns")  # Wait for propagation

        # Expected behavior
        expected_output, expected_upper_half, expected_lower_half = compute_cascaded_output(input_vector, N, M)


        # Assert correctness
        assert dut.out.value == expected_output, (
            f"Test failed for input {bin(input_vector)}: "
            f"Expected {expected_output}, Got {int(dut.out.value)}"
        )

        assert dut.out_upper_half.value == expected_upper_half, (
            f"Test failed for input {bin(input_vector)}: "
            f"Expected upper half {expected_upper_half}, Got {int(dut.out_upper_half.value)}"
        )

        assert dut.out_lower_half.value == expected_lower_half, (
            f"Test failed for input {bin(input_vector)}: "
            f"Expected lower half {expected_lower_half}, Got {int(dut.out_lower_half.value)}"
        )
        dut._log.info(
            f"PASSED: Input = {bin(input_vector)}, Output = {int(dut.out.value)}, "
            f"Upper Half = {int(dut.out_upper_half.value)}, Lower Half = {int(dut.out_lower_half.value)}"
        )


def compute_cascaded_output(inputs, N, M):
    """
    Compute the expected output of the cascaded encoder 
    """
    half_size = N // 2

    # Top half (left encoder)
    top_half = inputs >> half_size
    bottom_half = inputs & ((1 << half_size) - 1)

    enable_left = top_half != 0
    enable_right = bottom_half != 0

    upper_half_output = priority_index(top_half,M - 1)
    lower_half_output = priority_index(bottom_half, M - 1)

    if enable_left:
        # Priority to the top half
        cascaded_output=(1 << (M - 1)) | upper_half_output
    elif enable_right:
        # Priority to the bottom half
        cascaded_output=lower_half_output
    else:
        # No active input
        cascaded_output=0

    return cascaded_output, upper_half_output, lower_half_output

def priority_index(inputs, width):
    """
    Helper function to compute the index of the highest active bit.
    """
    for i in range(len(bin(inputs)) - 2, -1, -1):  # Skip '0b' prefix
        if inputs & (1 << i):
            return i & ((1 << width) - 1)
    return 0
