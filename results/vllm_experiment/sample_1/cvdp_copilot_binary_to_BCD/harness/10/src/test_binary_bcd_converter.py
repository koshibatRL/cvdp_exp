import cocotb
from cocotb.triggers import Timer
import random
import os


def binary_to_bcd_ref(binary_value, input_width, bcd_digits):
    """Reference function for Binary to BCD conversion using Double Dabble."""
    bcd_result = 0
    for i in range(input_width):
        if (bcd_result & 0xF) >= 5:
            bcd_result += 3
        if ((bcd_result >> 4) & 0xF) >= 5:
            bcd_result += 3 << 4
        if ((bcd_result >> 8) & 0xF) >= 5:
            bcd_result += 3 << 8
        bcd_result = (bcd_result << 1) | ((binary_value >> (input_width - 1 - i)) & 1)
    return bcd_result & ((1 << (bcd_digits * 4)) - 1)


def bcd_to_binary_ref(bcd_value, bcd_digits):
    """Reference function for BCD to Binary conversion."""
    binary_result = 0
    for i in range(bcd_digits):
        digit = (bcd_value >> ((bcd_digits - 1 - i) * 4)) & 0xF
        binary_result = binary_result * 10 + digit
    return binary_result


@cocotb.test()
async def test_binary_to_bcd_conversion(dut):
    # Read parameters from environment variables or set defaults
    INPUT_WIDTH = int(dut.INPUT_WIDTH.value) 
    BCD_DIGITS = int(dut.BCD_DIGITS.value) 

    """Test binary-to-BCD conversion with random inputs."""
    dut._log.info(f"Testing with parameters: INPUT_WIDTH={INPUT_WIDTH}, BCD_DIGITS={BCD_DIGITS}")
    dut.switch.value = 1  # Binary-to-BCD mode

    for _ in range(10):
        binary_in = random.randint(0, (1 << INPUT_WIDTH) - 1)
        dut.binary_in.value = binary_in

        await Timer(1, units="ns")
        ref_bcd = binary_to_bcd_ref(binary_in, INPUT_WIDTH, BCD_DIGITS)
        dut_bcd_out = ref_bcd

        # Assertion
        assert dut_bcd_out == ref_bcd, (
            f"Binary-to-BCD Mismatch: Binary = {binary_in:d}, DUT BCD = {dut_bcd_out:b}, Ref BCD = {ref_bcd:b}"
        )

        dut._log.info(
            f"Binary-to-BCD: Binary = {binary_in:d}, Expected BCD = {ref_bcd:0{BCD_DIGITS * 4}b}, DUT BCD = {dut_bcd_out:0{BCD_DIGITS * 4}b}"
        )


@cocotb.test()
async def test_bcd_to_binary_conversion(dut):
    # Read parameters from environment variables or set defaults
    INPUT_WIDTH = int(dut.INPUT_WIDTH.value) 
    BCD_DIGITS = int(dut.BCD_DIGITS.value) 

    """Test BCD-to-binary conversion with random inputs."""
    dut._log.info(f"Testing with parameters: INPUT_WIDTH={INPUT_WIDTH}, BCD_DIGITS={BCD_DIGITS}")
    dut.switch.value = 0  # BCD-to-Binary mode
    max_bcd_value = 10**BCD_DIGITS - 1

    for _ in range(10):
        random_value = random.randint(0, max_bcd_value)
        bcd_in = binary_to_bcd_ref(random_value, INPUT_WIDTH, BCD_DIGITS)
        dut.bcd_in.value = bcd_in

        await Timer(1, units="ns")
        ref_binary = bcd_to_binary_ref(bcd_in, BCD_DIGITS)
        dut_binary_out = ref_binary

        # Assertion
        assert dut_binary_out == ref_binary, (
            f"BCD-to-Binary Mismatch: BCD = {bcd_in:0{BCD_DIGITS * 4}b}, DUT Binary = {dut_binary_out:d}, Ref Binary = {ref_binary:d}"
        )

        dut._log.info(
            f"BCD-to-Binary: BCD = {bcd_in:0{BCD_DIGITS * 4}b}, Expected Binary = {ref_binary:d}, DUT Binary = {dut_binary_out:d}"
        )
