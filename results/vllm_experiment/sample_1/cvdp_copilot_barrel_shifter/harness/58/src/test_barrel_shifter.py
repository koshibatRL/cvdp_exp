import cocotb
from cocotb.triggers import Timer
import random

def verify(data_in, shift_bits, mode, left_right, mask, data_width):
    """Helper function to calculate expected output and error."""
    error = 0
    if mode in [0b000, 0b001, 0b010, 0b011] and shift_bits >= data_width:
        error = 1
        expected = 0
    elif mode == 0b000:  # Logical Shift
        if left_right == 1:
            expected = (data_in << shift_bits) & ((1 << data_width) - 1)
        else:
            expected = (data_in >> shift_bits)
    elif mode == 0b001:  # Arithmetic Shift
        if left_right == 1:
            expected = (data_in << shift_bits) & ((1 << data_width) - 1)
        else:
            sign_bit = data_in >> (data_width - 1)
            expected = (data_in >> shift_bits) | (
                ((1 << shift_bits) - 1) << (data_width - shift_bits) if sign_bit else 0
            )
    elif mode == 0b010:  # Rotate
        if left_right == 1:
            expected = (
                (data_in << shift_bits) | (data_in >> (data_width - shift_bits))
            ) & ((1 << data_width) - 1)
        else:
            expected = (
                (data_in >> shift_bits) | (data_in << (data_width - shift_bits))
            ) & ((1 << data_width) - 1)
    elif mode == 0b011:  # Custom Masked Shift
        if left_right == 1:
            expected = ((data_in << shift_bits) & mask) & ((1 << data_width) - 1)
        else:
            expected = ((data_in >> shift_bits) & mask) & ((1 << data_width) - 1)
    elif mode == 0b100:  # Arithmetic Addition/Subtraction
        if left_right == 1:
            expected = (data_in + shift_bits) & ((1 << data_width) - 1)
        else:
            expected = (data_in - shift_bits) & ((1 << data_width) - 1)
    elif mode == 0b101:  # Priority Encoder
        expected = max((i for i in range(data_width) if (data_in & (1 << i))), default=0)
    elif mode == 0b110:  # Modulo Arithmetic
        if left_right == 1:
            expected = (data_in + shift_bits) % data_width
        else:
            expected = (data_in - shift_bits) % data_width
    else:  # Invalid mode
        error = 1
        expected = 0

    return expected, error

def calculate_parity(data_out):
    """Helper function to calculate parity."""
    return bin(data_out).count("1") % 2  # 0 for even parity, 1 for odd parity

@cocotb.test()
async def test_predefined_barrel_shifter(dut):
    """Test the barrel shifter module with predefined test cases."""
    data_width = int(dut.data_width.value)

    # Predefined test cases for all modes
    predefined_tests = [
        {"data_in": 0b101010 & ((1 << data_width) - 1), "shift_bits": 2, "mode": 0b000, "left_right": 1, "mask": 0, "description": "Logical Shift Left"},
        {"data_in": 0b111100 & ((1 << data_width) - 1), "shift_bits": 2, "mode": 0b000, "left_right": 0, "mask": 0, "description": "Logical Shift Right"},
        {"data_in": 0b101011 & ((1 << data_width) - 1), "shift_bits": 2, "mode": 0b001, "left_right": 0, "mask": 0, "description": "Arithmetic Shift Right"},
        {"data_in": 0b101011 & ((1 << data_width) - 1), "shift_bits": 2, "mode": 0b010, "left_right": 1, "mask": 0, "description": "Rotate Left"},
        {"data_in": 0b101011 & ((1 << data_width) - 1), "shift_bits": 2, "mode": 0b011, "left_right": 0, "mask": 0b111100 & ((1 << data_width) - 1), "description": "Custom Masked Right Shift"},
        {"data_in": 0b101011 & ((1 << data_width) - 1), "shift_bits": 2, "mode": 0b100, "left_right": 1, "mask": 0, "description": "Arithmetic Addition"},
        {"data_in": 0b101011 & ((1 << data_width) - 1), "shift_bits": 2, "mode": 0b101, "left_right": 0, "mask": 0, "description": "Priority Encoder"},
        {"data_in": 0b101011 & ((1 << data_width) - 1), "shift_bits": 2, "mode": 0b110, "left_right": 1, "mask": 0, "description": "Modulo Addition"},
        {"data_in": 0b101011 & ((1 << data_width) - 1), "shift_bits": 2, "mode": 0b111, "left_right": 1, "mask": 0, "description": "Invalid Mode"},
    ]

    for i, test in enumerate(predefined_tests, 1):
        # Apply inputs
        dut.data_in.value = test["data_in"]
        dut.shift_bits.value = test["shift_bits"]
        dut.mode.value = test["mode"]
        dut.left_right.value = test["left_right"]
        dut.mask.value = test["mask"]
        dut.enable.value = 1  # Enable the module
        dut.enable_parity.value = 1  # Enable parity

        # Wait for combinational logic to settle
        await Timer(5, units="ns")

        # Compute expected output, parity, and error
        expected_output, expected_error = verify(
            test["data_in"], test["shift_bits"], test["mode"], test["left_right"], test["mask"], data_width
        )
        expected_parity = calculate_parity(expected_output)

        # Extract DUT outputs
        actual_output = int(dut.data_out.value)
        actual_parity = int(dut.parity_out.value)
        actual_error = int(dut.error.value)

        # Logging
        cocotb.log.info(
            f"Predefined Test #{i}: {test['description']}\n"
            f"  Inputs:\n"
            f"    data_in       = {bin(test['data_in'])}\n"
            f"    shift_bits    = {test['shift_bits']}\n"
            f"    mode          = {bin(test['mode'])}\n"
            f"    left_right    = {'Left' if test['left_right'] else 'Right'}\n"
            f"  Expected Output: {bin(expected_output)} (Parity: {expected_parity}, Error: {expected_error})\n"
            f"  Actual Output  : {bin(actual_output)} (Parity: {actual_parity}, Error: {actual_error})"
        )

        # Assertions
        assert actual_output == expected_output, f"Test #{i} FAILED: Output mismatch"
        assert actual_parity == expected_parity, f"Test #{i} FAILED: Parity mismatch"
        assert actual_error == expected_error, f"Test #{i} FAILED: Error signal mismatch"

    cocotb.log.info("All predefined tests passed.")
