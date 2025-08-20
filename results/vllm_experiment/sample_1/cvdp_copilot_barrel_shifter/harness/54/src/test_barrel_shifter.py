import cocotb
from cocotb.triggers import Timer
import random


def verify(data_in, shift_bits, mode, left_right, mask, data_width):
    """Helper function to calculate expected output."""
    if mode == 0b000:  # Logical Shift
        if left_right == 1:
            expected = (data_in << shift_bits) & ((1 << data_width) - 1)
        else:
            expected = (data_in >> shift_bits)
    elif mode == 0b001:  # Arithmetic Shift
        if left_right == 1:
            expected = (data_in << shift_bits) & ((1 << data_width) - 1)
        else:
            # Sign-extend the MSB for arithmetic shift
            sign_bit = data_in >> (data_width - 1)
            expected = (data_in >> shift_bits) | (
                ((1 << shift_bits) - 1) << (data_width - shift_bits) if sign_bit else 0
            )
    elif mode == 0b010:  # Rotate
        if left_right == 1:  # Rotate left
            expected = (
                (data_in << shift_bits) | (data_in >> (data_width - shift_bits))
            ) & ((1 << data_width) - 1)
        else:  # Rotate right
            expected = (
                (data_in >> shift_bits) | (data_in << (data_width - shift_bits))
            ) & ((1 << data_width) - 1)
    elif mode == 0b011:  # Custom Masked Shift
        if left_right == 1:  # Masked left shift
            expected = ((data_in << shift_bits) & mask) & ((1 << data_width) - 1)
        else:  # Masked right shift
            expected = ((data_in >> shift_bits) & mask) & ((1 << data_width) - 1)
    elif mode == 0b100:  # XOR with Shifted Data and Mask
        if left_right == 1:  # XOR after left shift
            expected = ((data_in << shift_bits) & ((1 << data_width) - 1)) ^ mask
        else:  # XOR after right shift
            expected = ((data_in >> shift_bits) & ((1 << data_width) - 1)) ^ mask
    else:  # Invalid mode
        expected = 0
    return expected


@cocotb.test()
async def test_predefined_barrel_shifter(dut):
    """Test the barrel shifter module with predefined test cases, including new 3-bit modes."""
    data_width = int(dut.data_width.value)
    shift_bits_width = int(dut.shift_bits_width.value)

    predefined_tests = [
        {"data_in": 0b1010111100001100 & ((1 << data_width) - 1), "shift_bits": 4, "mode": 0b000, "left_right": 1, "mask": 0, "description": "Logical Shift Left"},
        {"data_in": 0b1111000011110000 & ((1 << data_width) - 1), "shift_bits": 4, "mode": 0b000, "left_right": 0, "mask": 0, "description": "Logical Shift Right"},
        {"data_in": 0b1010111100001100 & ((1 << data_width) - 1), "shift_bits": 4, "mode": 0b001, "left_right": 0, "mask": 0, "description": "Arithmetic Shift Right"},
        {"data_in": 0b1010111100001100 & ((1 << data_width) - 1), "shift_bits": 4, "mode": 0b010, "left_right": 1, "mask": 0, "description": "Rotate Left"},
        {"data_in": 0b1010111100001100 & ((1 << data_width) - 1), "shift_bits": 4, "mode": 0b011, "left_right": 0, "mask": 0b1111000011110000 & ((1 << data_width) - 1), "description": "Custom Masked Right Shift"},
        {"data_in": 0b1010111100001100 & ((1 << data_width) - 1), "shift_bits": 4, "mode": 0b100, "left_right": 1, "mask": 0b1111111100000000 & ((1 << data_width) - 1), "description": "XOR with Shifted Data and Mask (Left)"},
        {"data_in": 0b1010111100001100 & ((1 << data_width) - 1), "shift_bits": 4, "mode": 0b100, "left_right": 0, "mask": 0b1111000011110000 & ((1 << data_width) - 1), "description": "XOR with Shifted Data and Mask (Right)"},
        {"data_in": 0b1010111100001100 & ((1 << data_width) - 1), "shift_bits": 4, "mode": 0b111, "left_right": 0, "mask": 0, "description": "Invalid Mode"},
    ]

    for i, test in enumerate(predefined_tests, 1):
        dut.data_in.value = test["data_in"]
        dut.shift_bits.value = test["shift_bits"]
        dut.mode.value = test["mode"]
        dut.left_right.value = test["left_right"]
        dut.mask.value = test["mask"]

        await Timer(1, units="ns")

        expected_output = verify(
            test["data_in"], test["shift_bits"], test["mode"], test["left_right"], test["mask"], data_width
        )

        actual_output = int(dut.data_out.value)

        mode_str = {
            0b000: "Logical Shift",
            0b001: "Arithmetic Shift",
            0b010: "Rotate",
            0b011: "Custom Masked Shift",
            0b100: "XOR with Shifted Data and Mask",
        }.get(test["mode"], "Invalid Mode")

        cocotb.log.info(
            f"\nPredefined Test #{i}: {test['description']}\n"
            f"  Mode: {mode_str} ({bin(test['mode'])})\n"
            f"  Inputs:\n"
            f"    data_in       = {bin(test['data_in']):>{data_width+2}} ({test['data_in']})\n"
            f"    shift_bits    = {test['shift_bits']} ({bin(test['shift_bits'])})\n"
            f"    mask          = {bin(test['mask']):>{data_width+2}} ({test['mask']})\n"
            f"  Expected Output: {bin(expected_output):>{data_width+2}} ({expected_output})\n"
            f"  Actual Output  : {bin(actual_output):>{data_width+2}} ({actual_output})"
        )

        assert actual_output == expected_output, f"Predefined Test #{i} FAILED"



@cocotb.test()
async def test_randomized_barrel_shifter(dut):
    """Test the barrel shifter module with randomized test cases for 3-bit modes."""
    data_width = int(dut.data_width.value)
    shift_bits_width = int(dut.shift_bits_width.value)

    for test_num in range(20):  # Run 20 randomized tests
        data_in = random.randint(0, (1 << data_width) - 1)
        shift_bits = random.randint(0, (1 << shift_bits_width) - 1)
        mode = random.randint(0, 7)  # 3-bit mode
        left_right = random.randint(0, 1)
        mask = random.randint(0, (1 << data_width) - 1)

        dut.data_in.value = data_in
        dut.shift_bits.value = shift_bits
        dut.mode.value = mode
        dut.left_right.value = left_right
        dut.mask.value = mask

        await Timer(1, units="ns")

        expected_output = verify(data_in, shift_bits, mode, left_right, mask, data_width)
        actual_output = int(dut.data_out.value)
        error_flag = int(dut.error.value)

        mode_str = {
            0b000: "Logical Shift",
            0b001: "Arithmetic Shift",
            0b010: "Rotate",
            0b011: "Custom Masked Shift",
            0b100: "XOR with Shifted Data and Mask",
        }.get(mode, "Invalid Mode")
        left_right_str = "Left" if left_right else "Right"

        log_message = f"\nRandom Test #{test_num}\n" \
                      f"  Mode: {mode_str} ({bin(mode)})\n" \
                      f"  Direction: {left_right_str}\n" \
                      f"  Inputs:\n" \
                      f"    data_in       = {bin(data_in):>{data_width+2}} ({data_in})\n" \
                      f"    shift_bits    = {shift_bits} ({bin(shift_bits)})\n"

        if mode in [0b011, 0b100]:  # Log mask for Custom Masked Shift and XOR
            log_message += f"    mask          = {bin(mask):>{data_width+2}} ({mask})\n"

        log_message += f"  Expected Output: {bin(expected_output):>{data_width+2}} ({expected_output})\n" \
                       f"  Actual Output  : {bin(actual_output):>{data_width+2}} ({actual_output})\n" \
                       f"  Error Flag     : {error_flag}"

        cocotb.log.info(log_message)

        assert actual_output == expected_output, f"Random Test #{test_num} FAILED"
        if mode not in [0b000, 0b001, 0b010, 0b011, 0b100]:
            assert error_flag == 1, f"Error flag not set for invalid mode {mode}"
        else:
            assert error_flag == 0, f"Error flag incorrectly set for valid mode {mode}"

    cocotb.log.info("All randomized test cases passed.")
