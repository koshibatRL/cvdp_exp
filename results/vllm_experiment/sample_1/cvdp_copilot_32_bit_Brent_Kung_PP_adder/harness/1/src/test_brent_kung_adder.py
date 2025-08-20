import cocotb
from cocotb.regression import TestFactory
from cocotb.triggers import Timer
from random import randint

# Cocotb testbench for Brent-Kung Adder
@cocotb.test()
async def test_brent_kung_adder(dut):
    """Test the 32-bit Brent-Kung Adder for different input cases."""

    # Define the test vectors based on the SystemVerilog run_test_case task
    test_vectors = [
        (0x00000000, 0x00000000, 0, 0x00000000, 0, "Test Case 1: Zero inputs"),
        (0x7FFFFFFF, 0x7FFFFFFF, 0, 0xFFFFFFFE, 0, "Test Case 2: Large positive numbers with no carry"),
        (0x80000000, 0x80000000, 0, 0x00000000, 1, "Test Case 3: Adding two large negative numbers, carry-out expected"),
        (0x0000FFFF, 0xFFFF0000, 0, 0xFFFFFFFF, 0, "Test Case 4: Numbers with different magnitudes"),
        (0xFFFFFFFF, 0xFFFFFFFF, 1, 0xFFFFFFFF, 1, "Test Case 5: Large numbers with carry-in"),
        (0x55555555, 0xAAAAAAAA, 0, 0xFFFFFFFF, 0, "Test Case 6: Alternating 1's and 0's, no carry-in"),
        (0xA1B2C3D4, 0x4D3C2B1A, 1, 0xEEEEEEEF, 0, "Test Case 7: Random values with carry-in"),
        (0xF0F0F0F0, 0x0F0F0F0F, 0, 0xFFFFFFFF, 0, "Test Case 8: Large hexadecimal numbers"),
        (0x12345678, 0x87654321, 1, 0x9999999A, 0, "Test Case 9: Random edge case with carry-in"),
        (0xDEADBEEF, 0xC0FFEE00, 0, 0x9FADACEF, 1, "Test Case 10: Random edge case, carry-out expected"),
        (0x11111111, 0x22222222, 1, 0x33333334, 0, "Test Case 11: Simple increasing values with carry-in"),
        (0x00000001, 0x00000001, 1, 0x00000003, 0, "Test Case 12: Smallest non-zero inputs with carry-in"),
    ]

    # Iterate through the test vectors and apply them to the DUT
    for a, b, carry_in, expected_sum, expected_carry_out, case_name in test_vectors:
        # Apply inputs
        dut.a.value = a
        dut.b.value = b
        dut.carry_in.value = carry_in

        # Wait for the DUT to process the inputs
        await Timer(10, units="ns")

        # Capture the outputs
        actual_sum = dut.sum.value
        actual_carry_out = dut.carry_out.value

        # Convert `LogicArray` to integer for correct formatting
        actual_sum_int = int(actual_sum)
        actual_carry_out_int = int(actual_carry_out)

        # Log the test case details
        dut._log.info(f"Running test case: {case_name}")
        dut._log.info(f"a: {a:08X}, b: {b:08X}, carry_in: {carry_in}")
        dut._log.info(f"Expected Sum: {expected_sum:08X}, Actual Sum: {actual_sum_int:08X}")
        dut._log.info(f"Expected Carry Out: {expected_carry_out}, Actual Carry Out: {actual_carry_out_int}")

        # Assertions to check if outputs match expectations
        assert actual_sum_int == expected_sum, f"{case_name} - Sum Mismatch: Expected {expected_sum:08X}, Got {actual_sum_int:08X}"
        assert actual_carry_out_int == expected_carry_out, f"{case_name} - Carry Out Mismatch: Expected {expected_carry_out}, Got {actual_carry_out_int}"

        # Wait for a short time before the next test case
        await Timer(10, units="ns")

    # Additional random test cases
    num_random_tests = 10  # Number of random tests to generate
    for i in range(num_random_tests):
        # Generate random values for a, b, and carry_in
        a = randint(0, 0xFFFFFFFF)
        b = randint(0, 0xFFFFFFFF)
        carry_in = randint(0, 1)

        # Apply inputs
        dut.a.value = a
        dut.b.value = b
        dut.carry_in.value = carry_in

        # Wait for the DUT to process the inputs
        await Timer(10, units="ns")

        # Capture the outputs
        actual_sum = dut.sum.value
        actual_carry_out = dut.carry_out.value

        # Convert `LogicArray` to integer for correct formatting
        actual_sum_int = int(actual_sum)
        actual_carry_out_int = int(actual_carry_out)

        # Log the random test case details
        dut._log.info(f"Random Test Case {i + 1}")
        dut._log.info(f"a: {a:08X}, b: {b:08X}, carry_in: {carry_in}")
        dut._log.info(f"Actual Sum: {actual_sum_int:08X}, Actual Carry Out: {actual_carry_out_int}")

        # Wait for a short time before the next random test case
        await Timer(10, units="ns")

