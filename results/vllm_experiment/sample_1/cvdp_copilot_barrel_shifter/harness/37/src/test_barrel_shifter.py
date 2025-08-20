import cocotb
from cocotb.triggers import Timer
import random

# The testbench will use the parameters as they are passed during simulation from the test_runner.py
# So no need to define DATA_WIDTH or SHIFT_BITS_WIDTH here

@cocotb.test()
async def test_shift_left(dut):
    """ Test left shift """
    # Log the dynamic parameters being used
    data_width = len(dut.data_in)
    shift_bits_width = len(dut.shift_bits)
    
    dut._log.info(f"Testing left shift with DATA_WIDTH={data_width}, SHIFT_BITS_WIDTH={shift_bits_width}")
    
    dut.rotate_left_right.value = 0  # Perform shift, not rotation
    dut.left_right.value = 1  # Left shift
    dut.data_in.value = random.randint(0, 2**data_width - 1)
    dut.shift_bits.value = random.randint(0, 2**shift_bits_width - 1)

    await Timer(10, units="ns")

    # Perform the left shift and mask with the proper data width
    shift_result = (int(dut.data_in.value) << int(dut.shift_bits.value)) & ((1 << data_width) - 1)
    
    # Print the expected and actual values
    dut._log.info(f"Shift left -> data_in: {hex(int(dut.data_in.value))}, shift_bits: {int(dut.shift_bits.value)}")
    dut._log.info(f"Expected output: {hex(shift_result)}, Actual output: {hex(int(dut.data_out.value))}")

    assert dut.data_out.value == shift_result, f"Left shift failed: expected {hex(shift_result)}, got {hex(int(dut.data_out.value))}"


@cocotb.test()
async def test_shift_right(dut):
    """ Test right shift """
    data_width = len(dut.data_in)
    shift_bits_width = len(dut.shift_bits)
    
    dut._log.info(f"Testing right shift with DATA_WIDTH={data_width}, SHIFT_BITS_WIDTH={shift_bits_width}")
    
    dut.rotate_left_right.value = 0  # Perform shift, not rotation
    dut.left_right.value = 0  # Right shift
    dut.data_in.value = random.randint(0, 2**data_width - 1)
    dut.shift_bits.value = random.randint(0, 2**shift_bits_width - 1)

    await Timer(10, units="ns")

    # Perform the right shift and mask with the proper data width
    shift_result = (int(dut.data_in.value) >> int(dut.shift_bits.value)) & ((1 << data_width) - 1)

    # Print the expected and actual values
    dut._log.info(f"Shift right -> data_in: {hex(int(dut.data_in.value))}, shift_bits: {int(dut.shift_bits.value)}")
    dut._log.info(f"Expected output: {hex(shift_result)}, Actual output: {hex(int(dut.data_out.value))}")

    assert dut.data_out.value == shift_result, f"Right shift failed: expected {hex(shift_result)}, got {hex(int(dut.data_out.value))}"


@cocotb.test()
async def test_rotate_left(dut):
    """ Test left rotate """
    data_width = len(dut.data_in)
    shift_bits_width = len(dut.shift_bits)
    
    dut._log.info(f"Testing left rotate with DATA_WIDTH={data_width}, SHIFT_BITS_WIDTH={shift_bits_width}")
    
    dut.rotate_left_right.value = 1  # Perform rotation, not shift
    dut.left_right.value = 1  # Left rotate
    dut.data_in.value = random.randint(0, 2**data_width - 1)
    dut.shift_bits.value = random.randint(0, 2**shift_bits_width - 1)

    await Timer(10, units="ns")

    # Perform the left rotate and mask with the proper data width
    rotate_result = ((int(dut.data_in.value) << int(dut.shift_bits.value)) | 
                     (int(dut.data_in.value) >> (data_width - int(dut.shift_bits.value)))) & ((1 << data_width) - 1)
    
    # Print the expected and actual values
    dut._log.info(f"Rotate left -> data_in: {hex(int(dut.data_in.value))}, shift_bits: {int(dut.shift_bits.value)}")
    dut._log.info(f"Expected output: {hex(rotate_result)}, Actual output: {hex(int(dut.data_out.value))}")

    assert dut.data_out.value == rotate_result, f"Left rotate failed: expected {hex(rotate_result)}, got {hex(int(dut.data_out.value))}"


@cocotb.test()
async def test_rotate_right(dut):
    """ Test right rotate """
    data_width = len(dut.data_in)
    shift_bits_width = len(dut.shift_bits)
    
    dut._log.info(f"Testing right rotate with DATA_WIDTH={data_width}, SHIFT_BITS_WIDTH={shift_bits_width}")
    
    dut.rotate_left_right.value = 1  # Perform rotation, not shift
    dut.left_right.value = 0  # Right rotate
    dut.data_in.value = random.randint(0, 2**data_width - 1)
    dut.shift_bits.value = random.randint(0, 2**shift_bits_width - 1)

    await Timer(10, units="ns")

    # Perform the right rotate and mask with the proper data width
    rotate_result = ((int(dut.data_in.value) >> int(dut.shift_bits.value)) | 
                     (int(dut.data_in.value) << (data_width - int(dut.shift_bits.value)))) & ((1 << data_width) - 1)

    # Print the expected and actual values
    dut._log.info(f"Rotate right -> data_in: {hex(int(dut.data_in.value))}, shift_bits: {int(dut.shift_bits.value)}")
    dut._log.info(f"Expected output: {hex(rotate_result)}, Actual output: {hex(int(dut.data_out.value))}")

    assert dut.data_out.value == rotate_result, f"Right rotate failed: expected {hex(rotate_result)}, got {hex(int(dut.data_out.value))}"


@cocotb.test()
async def test_no_shift_rotate(dut):
    """ Test case where no shift or rotate is performed (shift/rotate by 0) """
    data_width = len(dut.data_in)
    shift_bits_width = len(dut.shift_bits)
    
    dut._log.info(f"Testing no shift/rotate with DATA_WIDTH={data_width}, SHIFT_BITS_WIDTH={shift_bits_width}")
    
    dut.rotate_left_right.value = random.randint(0, 1)  # Randomly choose rotate or shift
    dut.left_right.value = random.randint(0, 1)  # Randomly choose left or right
    dut.data_in.value = random.randint(0, 2**data_width - 1)
    dut.shift_bits.value = 0  # No shift or rotate

    await Timer(10, units="ns")

    # Print the actual values
    dut._log.info(f"No shift/rotate -> data_in: {hex(int(dut.data_in.value))}")
    dut._log.info(f"Expected output: {hex(int(dut.data_in.value))}, Actual output: {hex(int(dut.data_out.value))}")

    # Expect the data_out to be the same as data_in
    assert dut.data_out.value == dut.data_in.value, f"No shift/rotate failed: expected {hex(int(dut.data_in.value))}, got {hex(int(dut.data_out.value))}"
