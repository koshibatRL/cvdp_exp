import cocotb
from cocotb.triggers import Timer
import random

def truncate(value, width):
    return value & ((1 << width) - 1)


def verify(data_in, shift_bits, mode, left_right, mask, data_width, condition=None, bit_op_type=None):
    """Helper function to calculate expected output and error."""
    error = 0  # Default to no error
    if mode == 0b000:  # Logical Shift
        if shift_bits >= data_width:
            expected = 0
            error = 0b10  # Out-of-Range Shift
        else:
            if left_right == 1:
                expected = (data_in << shift_bits) & ((1 << data_width) - 1)
            else:
                expected = (data_in >> shift_bits)
    elif mode == 0b001:  # Arithmetic Shift
        if shift_bits >= data_width:
            expected = 0
            error = 0b10  # Out-of-Range Shift
        else:
            if left_right == 1:
                expected = (data_in << shift_bits) & ((1 << data_width) - 1)
            else:
                sign_bit = data_in >> (data_width - 1)
                expected = (data_in >> shift_bits) | (
                    ((1 << shift_bits) - 1) << (data_width - shift_bits) if sign_bit else 0
                )
    elif mode == 0b010:  # Rotate
        if shift_bits >= data_width:
            expected = 0
            error = 0b10  # Out-of-Range Shift
        else:
            if left_right == 1:
                expected = (
                    (data_in << shift_bits) | (data_in >> (data_width - shift_bits))
                ) & ((1 << data_width) - 1)
            else:
                expected = (
                    (data_in >> shift_bits) | (data_in << (data_width - shift_bits))
                ) & ((1 << data_width) - 1)
    elif mode == 0b011:  # Custom Masked Shift
        if shift_bits >= data_width:
            expected = 0
            error = 0b10  # Out-of-Range Shift
        else:
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
        if data_in == 0:
            expected = 0
            error = 0b01  # No bits set
        else:
            expected = max((i for i in range(data_width) if (data_in & (1 << i))), default=0)
    elif mode == 0b110:  # Modulo Arithmetic
        if left_right == 1:
            expected = (data_in + shift_bits) % data_width
        else:
            expected = (data_in - shift_bits) % data_width
    elif mode == 0b111:  # Conditional Bit Manipulation
        if bit_op_type == 0b00:  # Toggle
            expected = data_in ^ condition
        elif bit_op_type == 0b01:  # Set
            expected = data_in | condition
        elif bit_op_type == 0b10:  # Clear
            expected = data_in & ~condition
        else:  # Invalid bit_op_type
            expected = 0
            error = 0b01  # Invalid operation type
    else:  # Invalid mode
        expected = 0
        error = 0b01  # Invalid mode
    return expected & ((1 << data_width) - 1), error


def calculate_parity(data_out):
    """Helper function to calculate parity."""
    return bin(data_out).count("1") % 2  # 0 for even parity, 1 for odd parity

def truncate(value, width):
    """Truncate a value to the given bit width."""
    return value & ((1 << width) - 1)

@cocotb.test()
async def test_predefined_barrel_shifter(dut):
    """Test the barrel shifter module with predefined test cases."""
    data_width = int(dut.data_width.value)

    # Predefined test cases for all modes including Conditional Bit Manipulation
    predefined_tests = [
    # Logical Shift
    {"data_in": truncate(0x1234, data_width), "shift_bits": 4, "mode": 0b000, "left_right": 1, "mask": 0, "description": "Logical Shift Left"},
    {"data_in": truncate(0x1234, data_width), "shift_bits": 4, "mode": 0b000, "left_right": 0, "mask": 0, "description": "Logical Shift Right"},

    # Arithmetic Shift
    {"data_in": truncate(0xF234, data_width), "shift_bits": 3, "mode": 0b001, "left_right": 0, "mask": 0, "description": "Arithmetic Shift Right"},

    # Rotate
    {"data_in": truncate(0x1234, data_width), "shift_bits": 4, "mode": 0b010, "left_right": 1, "mask": 0, "description": "Rotate Left"},

    # Masked Shift
    {"data_in": truncate(0x1234, data_width), "shift_bits": 4, "mode": 0b011, "left_right": 1, "mask": truncate(0xFF00, data_width), "description": "Masked Left Shift"},

    # Arithmetic Addition/Subtraction
    {"data_in": truncate(0x1234, data_width), "shift_bits": 4, "mode": 0b100, "left_right": 1, "mask": 0, "description": "Arithmetic Addition"},

    # Priority Encoder
    {"data_in": truncate(0x0840, data_width), "shift_bits": 0, "mode": 0b101, "left_right": 0, "mask": 0, "description": "Priority Encoder"},

    # Modulo Arithmetic
    {"data_in": truncate(0x1234, data_width), "shift_bits": 5, "mode": 0b110, "left_right": 1, "mask": 0, "description": "Modulo Addition"},

    # Conditional Bit Manipulation
    {"data_in": truncate(0x1234, data_width), "shift_bits": 4, "mode": 0b111, "left_right": 1, "condition": truncate(0x0F0F, data_width), "bit_op_type": 0b00, "description": "Toggle Bits"},
    {"data_in": truncate(0x1234, data_width), "shift_bits": 4, "mode": 0b111, "left_right": 1, "condition": truncate(0x0F0F, data_width), "bit_op_type": 0b01, "description": "Set Bits"},
    {"data_in": truncate(0x1234, data_width), "shift_bits": 4, "mode": 0b111, "left_right": 1, "condition": truncate(0x0F0F, data_width), "bit_op_type": 0b10, "description": "Clear Bits"},
    {"data_in": truncate(0x1234, data_width), "shift_bits": 4, "mode": 0b111, "left_right": 1, "condition": truncate(0x0F0F, data_width), "bit_op_type": 0b11, "description": "Clear Bits"},    
    ]


    for i, test in enumerate(predefined_tests, 1):
        # Apply inputs
        dut.data_in.value = test["data_in"]
        dut.shift_bits.value = test["shift_bits"]
        dut.mode.value = test["mode"]
        dut.left_right.value = test["left_right"]
        dut.mask.value = test.get("mask", 0)
        dut.condition.value = test.get("condition", 0)
        dut.bit_op_type.value = test.get("bit_op_type", 0)
        dut.enable_parity.value = 1  # Enable parity

        # Wait for combinational logic to settle
        await Timer(5, units="ns")

        # Compute expected output, parity, and error
        expected_output, expected_error = verify(
            test["data_in"],
            test["shift_bits"],
            test["mode"],
            test["left_right"],
            test.get("mask", 0),
            data_width,
            test.get("condition", 0),
            test.get("bit_op_type", 0),
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
            f"    condition     = {bin(test.get('condition', 0))}\n"
            f"    bit_op_type   = {bin(test.get('bit_op_type', 0))}\n"
            f"  Expected Output: {bin(expected_output)} (Parity: {expected_parity}, Error: {bin(expected_error)})\n"
            f"  Actual Output  : {bin(actual_output)} (Parity: {actual_parity}, Error: {bin(actual_error)})"
        )

        # Assertions
        assert actual_output == expected_output, f"Test #{i} FAILED: Output mismatch"
        assert actual_parity == expected_parity, f"Test #{i} FAILED: Parity mismatch"
        assert actual_error == expected_error, f"Test #{i} FAILED: Error mismatch"

    cocotb.log.info("All predefined tests passed.")

@cocotb.test()
async def test_randomized_barrel_shifter(dut):
    """Test the barrel shifter module with randomized test cases."""
    data_width = int(dut.data_width.value)
    shift_bits_width = int(dut.shift_bits_width.value)

    for test_num in range(1, 21):  # Run 20 randomized tests
        # Randomize inputs
        data_in = random.randint(0, (1 << data_width) - 1)
        shift_bits = random.randint(0, (1 << shift_bits_width) - 1)
        mode = random.randint(0, 7)  # Include new mode (0b111)
        left_right = random.randint(0, 1)
        mask = random.randint(0, (1 << data_width) - 1)
        condition = random.randint(0, (1 << data_width) - 1)
        bit_op_type = random.randint(0, 3)  # Include all bit_op_type values

        # Apply inputs to DUT
        dut.data_in.value = data_in
        dut.shift_bits.value = shift_bits
        dut.mode.value = mode
        dut.left_right.value = left_right
        dut.mask.value = mask
        dut.condition.value = condition
        dut.bit_op_type.value = bit_op_type
        dut.enable_parity.value = 1  # Enable parity

        # Wait for combinational logic to settle
        await Timer(5, units="ns")

        # Compute expected output, parity, and error
        expected_output, expected_error = verify(
            data_in, shift_bits, mode, left_right, mask, data_width, condition, bit_op_type
        )
        expected_parity = calculate_parity(expected_output)

        # Extract DUT outputs
        actual_output = int(dut.data_out.value)
        actual_parity = int(dut.parity_out.value)
        actual_error = int(dut.error.value)

        # Logging
        cocotb.log.info(
            f"Random Test #{test_num}\n"
            f"  Inputs:\n"
            f"    data_in       = {bin(data_in)}\n"
            f"    shift_bits    = {shift_bits}\n"
            f"    mode          = {bin(mode)}\n"
            f"    left_right    = {'Left' if left_right else 'Right'}\n"
            f"    condition     = {bin(condition)}\n"
            f"    bit_op_type   = {bin(bit_op_type)}\n"
            f"  Expected Output: {bin(expected_output)} (Parity: {expected_parity}, Error: {bin(expected_error)})\n"
            f"  Actual Output  : {bin(actual_output)} (Parity: {actual_parity}, Error: {bin(actual_error)})"
        )

        # Assertions
        assert actual_output == expected_output, f"Random Test #{test_num} FAILED: Output mismatch"
        assert actual_parity == expected_parity, f"Random Test #{test_num} FAILED: Parity mismatch"
        assert actual_error == expected_error, f"Random Test #{test_num} FAILED: Error mismatch"

    cocotb.log.info("All randomized test cases passed.")


@cocotb.test()
async def test_out_of_range_shift(dut):
    """Test Out-of-Range Shift Error (error = 0b10)"""
    data_width = int(dut.data_width.value)
    dut.data_in.value = truncate(0x1234, data_width)
    dut.shift_bits.value = data_width  # deliberately out of range
    dut.mode.value = 0b000  # Logical shift
    dut.left_right.value = 1
    dut.mask.value = 0
    dut.condition.value = 0
    dut.bit_op_type.value = 0
    dut.enable_parity.value = 1

    await Timer(5, units="ns")
    assert int(dut.error.value) == 0b10, "Expected error = 0b10 for out-of-range shift"


@cocotb.test()
async def test_invalid_bit_op_type(dut):
    """Test Invalid bit_op_type in Conditional Bit Manipulation (error = 0b01)"""
    data_width = int(dut.data_width.value)
    dut.data_in.value = truncate(0x1234, data_width)
    dut.shift_bits.value = 0
    dut.mode.value = 0b111
    dut.left_right.value = 1
    dut.mask.value = 0
    dut.condition.value = truncate(0x0F0F, data_width)
    dut.bit_op_type.value = 0b11  # Invalid
    dut.enable_parity.value = 1

    await Timer(5, units="ns")
    assert int(dut.error.value) == 0b01, "Expected error = 0b01 for invalid bit_op_type"


@cocotb.test()
async def test_toggle_bits(dut):
    """Conditional Bit Manipulation - Toggle"""
    data_width = int(dut.data_width.value)
    data_in = truncate(0xAAAA, data_width)
    condition = truncate(0xFFFF, data_width)
    dut.data_in.value = data_in
    dut.shift_bits.value = 0
    dut.mode.value = 0b111
    dut.left_right.value = 1
    dut.condition.value = condition
    dut.bit_op_type.value = 0b00
    dut.enable_parity.value = 1

    await Timer(5, units="ns")
    expected = data_in ^ condition
    assert int(dut.data_out.value) == expected, "Toggle bit operation failed"


@cocotb.test()
async def test_clear_bits(dut):
    """Conditional Bit Manipulation - Clear"""
    data_width = int(dut.data_width.value)
    data_in = truncate(0xFFFF, data_width)
    condition = truncate(0xFF00, data_width)
    dut.data_in.value = data_in
    dut.shift_bits.value = 0
    dut.mode.value = 0b111
    dut.left_right.value = 1
    dut.condition.value = condition
    dut.bit_op_type.value = 0b10
    dut.enable_parity.value = 1

    await Timer(5, units="ns")
    expected = data_in & ~condition
    assert int(dut.data_out.value) == expected, "Clear bit operation failed"
