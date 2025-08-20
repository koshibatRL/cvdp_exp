import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
import random

# Parameters
A_DW = 32
B_DW = 32
OUT_DW = 32
random.seed(42)  # Ensures reproducibility of random values

async def initialize_dut(dut):
    """Initialize the DUT and set all inputs to their default values."""
    dut.reset_in.setimmediatevalue(1)
    dut.vector_a_valid_in.value = 0
    dut.dot_length_in.value = 0
    dut.vector_b_valid_in.value = 0
    dut.start_in.value = 0
    dut.vector_a_in.value = 0
    dut.vector_b_in.value = 0
    dut.a_complex_in.value = 0
    dut.b_complex_in.value = 0

    # Start the clock
    clock = Clock(dut.clk_in, 20, units="ns")
    cocotb.start_soon(clock.start())

    # Reset procedure
    await RisingEdge(dut.clk_in)
    dut.reset_in.value = 1
    await RisingEdge(dut.clk_in)
    await RisingEdge(dut.clk_in)
    dut.reset_in.value = 0
    await RisingEdge(dut.clk_in)
    dut._log.info("DUT Initialized: Reset completed and inputs set to default.")

async def send_vector(dut, vec_a, vec_b, length, a_complex=0, b_complex=0, interrupt_valid=False):
    """Send vector inputs to the DUT."""
    dut.dot_length_in.value = length
    dut.a_complex_in.value = a_complex
    dut.b_complex_in.value = b_complex
    await RisingEdge(dut.clk_in)
    dut.start_in.value = 1

    dut._log.info(f"Sending Vectors: Length = {length}, a_complex = {a_complex}, b_complex = {b_complex}")
    for i in range(length):
        await RisingEdge(dut.clk_in)
        dut.start_in.value = 0
        dut.vector_a_in.value = vec_a[i]
        dut.vector_b_in.value = vec_b[i]
        dut.vector_a_valid_in.value = 1
        dut.vector_b_valid_in.value = 1
# Print the input vectors and valid signals in hex format
        if interrupt_valid and i == length // 2:
            # Simulate an interruption
            dut.vector_a_valid_in.value = 0
            dut.vector_b_valid_in.value = 0
            await RisingEdge(dut.clk_in)
        dut._log.info(f"Cycle {i + 1}: vector_a_in = {hex(vec_a[i])}, "
                      f"vector_b_in = {hex(vec_b[i])}, "
                      f"vector_a_valid_in = {hex(int(dut.vector_a_valid_in.value))}, "
                      f"vector_b_valid_in = {hex(int(dut.vector_b_valid_in.value))}")

    await RisingEdge(dut.clk_in)
    dut.vector_a_valid_in.value = 0
    dut.vector_b_valid_in.value = 0

async def check_result(dut, expected_result, expected_error=False):
    """Check the DUT result and validate correctness."""
    await RisingEdge(dut.clk_in)
    await RisingEdge(dut.clk_in)
    await RisingEdge(dut.clk_in)

    valid = int(dut.dot_product_valid_out.value)
    error = int(dut.dot_product_error_out.value)
    result = int(dut.dot_product_out.value)

    dut._log.info(f"DUT Output: result = {result}, valid = {valid}, error = {error}")

    if error:
        if not expected_error:
            dut._log.error("Unexpected error detected! Dot product error asserted when it shouldn't be.")
            assert False
        else:
            dut._log.info("Dot product error correctly asserted as expected.")
    elif valid:
        if expected_error:
            dut._log.error("Expected dot product error, but valid_out is HIGH.")
            assert False
        elif result != expected_result:
            dut._log.error(f"Result mismatch! Expected: {expected_result}, Got: {result}")
            assert False
        else:
            dut._log.info(f"Result matches expected value: {expected_result}")
    else:
        dut._log.error("Unexpected state: Neither valid_out nor error_out is asserted.")
        assert False

# Original Tests (Updated to include a_complex and b_complex)

@cocotb.test()
async def test_case_reset_assert(dut):
    """Test Case: Reset behavior during computation."""
    await initialize_dut(dut)

    vec_a = [1, 1, 1, 1]
    vec_b = [1, 2, 3, 4]

    await send_vector(dut, vec_a, vec_b, 4, a_complex=0, b_complex=0)

    # Assert reset during computation
    dut.reset_in.value = 1
    await RisingEdge(dut.clk_in)
    await RisingEdge(dut.clk_in)
    await RisingEdge(dut.clk_in)

    dut._log.info(f"Inputs after reset: vector_a_in = {dut.vector_a_in.value}, vector_b_in = {dut.vector_b_in.value}")
    dut._log.info(f"Outputs after reset: dot_product_out = {dut.dot_product_out.value}, dot_product_valid_out = {dut.dot_product_valid_out.value}")

    assert dut.dot_product_out.value == 0, f"dot_product_out expected to be 0, got {int(dut.dot_product_out.value)}"
    assert dut.dot_product_valid_out.value == 0, "dot_product_valid_out expected to be 0, but it is HIGH"

    dut._log.info("Reset behavior verified: Outputs reset to 0 as expected.")

@cocotb.test()
async def test_case_length_4(dut):
    """Test Case : Length 4."""
    await initialize_dut(dut)

    vec_a = [1, 1, 1, 1]
    vec_b = [1, 2, 3, 4]
    expected_result = sum(a * b for a, b in zip(vec_a, vec_b))

    await send_vector(dut, vec_a, vec_b, 4, a_complex=0, b_complex=0, interrupt_valid=False)
    await check_result(dut, expected_result, expected_error=False)

@cocotb.test()
async def test_case_length_8(dut):
    """Test Case : Length 8."""
    await initialize_dut(dut)

    vec_a = [2] * 8
    vec_b = [i + 1 for i in range(8)]
    expected_result = sum(a * b for a, b in zip(vec_a, vec_b))

    await send_vector(dut, vec_a, vec_b, 8, a_complex=0, b_complex=0, interrupt_valid=False)
    await check_result(dut, expected_result, expected_error=False)

@cocotb.test()
async def test_case_random_length_6(dut):
    """Test Case : Random Length 6."""
    await initialize_dut(dut)

    vec_a = [random.randint(0, 255) for _ in range(6)]
    vec_b = [random.randint(0, 65535) for _ in range(6)]
    expected_result = sum(a * b for a, b in zip(vec_a, vec_b))

    await send_vector(dut, vec_a, vec_b, 6, a_complex=0, b_complex=0, interrupt_valid=False)
    await check_result(dut, expected_result, expected_error=False)

@cocotb.test()
async def test_case_random_length_127(dut):
    """Test Case : Random Length 127."""
    await initialize_dut(dut)

    vec_a = [random.randint(0, 255) for _ in range(127)]
    vec_b = [random.randint(0, 65535) for _ in range(127)]
    expected_result = sum(a * b for a, b in zip(vec_a, vec_b))

    await send_vector(dut, vec_a, vec_b, 127, a_complex=0, b_complex=0, interrupt_valid=False)
    await check_result(dut, expected_result, expected_error=False)

@cocotb.test()
async def test_case_random_length_99(dut):
    """Test Case : Random Length 99."""
    await initialize_dut(dut)

    vec_a = [random.randint(0, 255) for _ in range(99)]
    vec_b = [random.randint(0, 65535) for _ in range(99)]
    expected_result = sum(a * b for a, b in zip(vec_a, vec_b))

    await send_vector(dut, vec_a, vec_b, 99, a_complex=0, b_complex=0, interrupt_valid=False)
    await check_result(dut, expected_result, expected_error=False)

@cocotb.test()
async def test_case_random_vectors_and_length(dut):
    """Test Case : Random Length."""
    await initialize_dut(dut)

    length = random.randint(1, 127)
    vec_a = [random.randint(0, 255) for _ in range(length)]
    vec_b = [random.randint(0, 65535) for _ in range(length)]
    expected_result = sum(a * b for a, b in zip(vec_a, vec_b))

    dut._log.info(f"Random Length: {length}")

    await send_vector(dut, vec_a, vec_b, length, a_complex=0, b_complex=0, interrupt_valid=False)
    await check_result(dut, expected_result, expected_error=False)

# New Tests (Appended)
@cocotb.test()
async def dot_product_complex_vecb_test(dut):
    """Test Case: Complex Mode for Vector B"""
    await initialize_dut(dut)

    LEN = 4
    vec_a = [1] * LEN
    vec_b = [-x for x in range(LEN)]

    # Correctly pack vec_b: MSB = Imaginary, LSB = Real
    vec_b_twos_complex = [(b & 0xFFFF) | ((b & 0xFFFF) << 16) for b in vec_b]

    # Calculate expected result
    acc_re, acc_im = 0, 0
    for a, b in zip(vec_a, vec_b_twos_complex):
        b_re = b & 0xFFFF
        b_im = (b >> 16) & 0xFFFF

        b_re = b_re if b_re < 0x8000 else b_re - 0x10000
        b_im = b_im if b_im < 0x8000 else b_im - 0x10000

        acc_re += a * b_re
        acc_im += a * b_im

    acc_re &= 0xFFFF
    acc_im &= 0xFFFF
    expected_result = (acc_im << 16) | acc_re

    await send_vector(dut, vec_a, vec_b_twos_complex, LEN, a_complex=0, b_complex=1, interrupt_valid=False)
    await check_result(dut, expected_result, expected_error=False)

@cocotb.test()
async def dot_product_complex_veca_test(dut):
    """Test Case: Complex Mode for Vector A"""
    await initialize_dut(dut)

    LEN = 4
    vec_a = [-x for x in range(LEN)]
    vec_b = [1] * LEN

    # Correctly pack vec_a: MSB = Imaginary, LSB = Real
    vec_a_twos_complex = [(a & 0xFFFF) | ((a & 0xFFFF) << 16) for a in vec_a]

    acc_re, acc_im = 0, 0
    for a, b in zip(vec_a_twos_complex, vec_b):
        a_re = a & 0xFFFF
        a_im = (a >> 16) & 0xFFFF

        a_re = a_re if a_re < 0x8000 else a_re - 0x10000
        a_im = a_im if a_im < 0x8000 else a_im - 0x10000

        acc_re += a_re * b
        acc_im += a_im * b

    acc_re &= 0xFFFF
    acc_im &= 0xFFFF
    expected_result = (acc_im << 16) | acc_re

    await send_vector(dut, vec_a_twos_complex, vec_b, LEN, a_complex=1, b_complex=0, interrupt_valid=False)
    await check_result(dut, expected_result, expected_error=False)

@cocotb.test()
async def dot_product_both_vec_complex_test(dut):
    """Test Case: Both Vectors in Complex Mode"""
    await initialize_dut(dut)

    LEN = 8
    vec_a = [-x for x in range(LEN)]
    vec_b = [-x for x in range(LEN)]

    # Correctly pack vec_a and vec_b into unsigned 32-bit format
    vec_a_twos_complex = [(a & 0xFFFF) | ((a & 0xFFFF) << 16) for a in vec_a]
    vec_b_twos_complex = [(b & 0xFFFF) | ((b & 0xFFFF) << 16) for b in vec_b]

    # Calculate expected result
    acc_re = 0
    acc_im = 0
    for a, b in zip(vec_a_twos_complex, vec_b_twos_complex):
        # Extract real and imaginary parts
        a_re = a & 0xFFFF
        a_im = (a >> 16) & 0xFFFF
        b_re = b & 0xFFFF
        b_im = (b >> 16) & 0xFFFF

        # Convert to signed 16-bit
        a_re = a_re if a_re < 0x8000 else a_re - 0x10000
        a_im = a_im if a_im < 0x8000 else a_im - 0x10000
        b_re = b_re if b_re < 0x8000 else b_re - 0x10000
        b_im = b_im if b_im < 0x8000 else b_im - 0x10000

        # Accumulate real and imaginary parts
        acc_re += a_re * b_re - a_im * b_im
        acc_im += a_re * b_im + a_im * b_re

    # Convert to 16-bit two's complement
    acc_re &= 0xFFFF
    acc_im &= 0xFFFF

    # Combine into 32-bit result
    expected_result = (acc_im << 16) | acc_re

    # Send vectors to the DUT and check the result
    await send_vector(dut, vec_a_twos_complex, vec_b_twos_complex, LEN, a_complex=1, b_complex=1, interrupt_valid=False)
    await check_result(dut, expected_result, expected_error=False)


@cocotb.test()
async def dot_product_complex_veca_random_vecb_test(dut):
    """Test Case: Complex Mode for Vector A with Random Length and Values for Vector B"""
    await initialize_dut(dut)

    # Randomize length and vectors
    LEN = random.randint(2, 128)  # Random length between 2 and 128
    vec_a = [-x for x in range(LEN)]  # Deterministic values for vector A
    vec_b = [random.randint(-128, 127) for _ in range(LEN)]  # Random values for vector B

    # Correctly pack vec_a: MSB = Imaginary, LSB = Real
    vec_a_twos_complex = [(a & 0xFFFF) | ((a & 0xFFFF) << 16) for a in vec_a]

    acc_re, acc_im = 0, 0
    for a, b in zip(vec_a_twos_complex, vec_b):
        a_re = a & 0xFFFF
        a_im = (a >> 16) & 0xFFFF

        # Convert to signed 16-bit
        a_re = a_re if a_re < 0x8000 else a_re - 0x10000
        a_im = a_im if a_im < 0x8000 else a_im - 0x10000

        # Accumulate real and imaginary parts
        acc_re += a_re * b
        acc_im += a_im * b

    # Truncate results to 16-bit and combine into 32-bit output
    acc_re &= 0xFFFF
    acc_im &= 0xFFFF
    expected_result = (acc_im << 16) | acc_re

    # Log the test details for debugging
    dut._log.info(f"Test Parameters: LEN = {LEN}")
    dut._log.info(f"Expected Result: 0x{expected_result:08X}")

    # Send vectors to the DUT and check the result
    await send_vector(dut, vec_a_twos_complex, vec_b, LEN, a_complex=1, b_complex=0, interrupt_valid=False)
    await check_result(dut, expected_result, expected_error=False)

@cocotb.test()
async def dot_product_error_insert_test(dut):
    """Test Case: Complex Mode for Vector B"""
    await initialize_dut(dut)

    LEN = 4
    vec_a = [1] * LEN
    vec_b = [-x for x in range(LEN)]

    # Correctly pack vec_b: MSB = Imaginary, LSB = Real
    vec_b_twos_complex = [(b & 0xFFFF) | ((b & 0xFFFF) << 16) for b in vec_b]

    # Calculate expected result
    acc_re, acc_im = 0, 0
    for a, b in zip(vec_a, vec_b_twos_complex):
        b_re = b & 0xFFFF
        b_im = (b >> 16) & 0xFFFF

        b_re = b_re if b_re < 0x8000 else b_re - 0x10000
        b_im = b_im if b_im < 0x8000 else b_im - 0x10000

        acc_re += a * b_re
        acc_im += a * b_im

    acc_re &= 0xFFFF
    acc_im &= 0xFFFF
    expected_result = (acc_im << 16) | acc_re

    await send_vector(dut, vec_a, vec_b_twos_complex, LEN, a_complex=0, b_complex=1, interrupt_valid=True)
    await check_result(dut, expected_result, expected_error=True)

