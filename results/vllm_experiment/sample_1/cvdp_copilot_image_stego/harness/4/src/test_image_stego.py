import cocotb
from cocotb.triggers import Timer
import os
import random

def compute_expected_output(img_in, data_in, bpp, row, col):
    """
    Replicates the logic in the Verilog code for each pixel:
        - bpp = 00: LSB replaced by data_in[i]
        - bpp = 01: 2 LSB replaced by data_in[2*i+1 : 2*i]
        - bpp = 10: 3 LSB replaced by data_in[3*i+2 : 3*i]
        - bpp = 11: 4 LSB replaced by data_in[4*i+3 : 4*i]
    """
    total_pixels = row * col
    out_val = 0

    for i in range(total_pixels):
        pixel = (img_in >> (i*8)) & 0xFF  # extract 8 bits for pixel i
        if bpp == 0b00:
            bit = (data_in >> i) & 0x1
            pixel = (pixel & 0xFE) | bit
        elif bpp == 0b01:
            bits = (data_in >> (2*i)) & 0x3
            pixel = (pixel & 0xFC) | bits
        elif bpp == 0b10:
            bits = (data_in >> (3*i)) & 0x7
            pixel = (pixel & 0xF8) | bits
        elif bpp == 0b11:
            bits = (data_in >> (4*i)) & 0xF
            pixel = (pixel & 0xF0) | bits

        # place updated pixel back in correct position
        out_val |= (pixel & 0xFF) << (i*8)

    return out_val


@cocotb.test()
async def test_basic(dut):
    """
    Basic test: small deterministic input to verify correct replacement.
    """

    # -- Grab row/col from environment variables
    row = int(os.getenv("ROW", "2"))
    col = int(os.getenv("COL", "2"))
    total_pixels = row * col

    dut._log.info("=== [BASIC TEST] Starting ===")

    # Let's pick bpp=00 for a simple test
    dut.bpp.value = 0b00

    # Example: 4 pixels => (row=2, col=2). 8 bits each => 32 bits
    # We'll do a simple pattern for img_in
    img_val = 0b11110000000011111010101001010101  # 0xF00FAA55
    dut.img_in.value = img_val

    # data_in => 4 bits per pixel => total of 16 bits
    # For bpp=00, we only use 1 bit per pixel, effectively the lower bits
    data_val = 0b0000000000000101  # 0x0005
    dut.data_in.value = data_val

    await Timer(2, units="ns")

    bpp = 0b00
    expected_val = compute_expected_output(img_val, data_val, bpp, row, col)
    actual_val = dut.img_out.value.to_unsigned()  # recommended alternative to .integer

    # Print in binary with correct zero padding
    dut._log.info(f"Inputs : img_in=0b{img_val:0{total_pixels*8}b}, "
                  f"data_in=0b{data_val:0{total_pixels*4}b}, bpp={bpp:02b}")
    dut._log.info(f"Output : actual=0b{actual_val:0{total_pixels*8}b}, "
                  f"expected=0b{expected_val:0{total_pixels*8}b}")

    assert actual_val == expected_val, \
        f"[BASIC TEST] Mismatch: got=0b{actual_val:0{total_pixels*8}b}, expected=0b{expected_val:0{total_pixels*8}b}"

    dut._log.info("=== [BASIC TEST] PASSED ===")


@cocotb.test()
async def test_edgecase_all_zeros(dut):
    """
    Edge case test: All zeros in img_in and data_in.
    """
    row = int(os.getenv("ROW", "2"))
    col = int(os.getenv("COL", "2"))
    total_pixels = row * col

    dut._log.info("=== [EDGE CASE TEST - ALL ZEROS] Starting ===")

    # Test with bpp=00
    dut.bpp.value = 0b00

    img_val = 0x00000000  # All zeros
    data_val = 0x0000  # All zeros

    dut.img_in.value = img_val
    dut.data_in.value = data_val

    await Timer(2, units="ns")

    bpp = 0b00
    expected_val = compute_expected_output(img_val, data_val, bpp, row, col)
    actual_val = dut.img_out.value.to_unsigned()

    dut._log.info(f"Inputs : img_in=0b{img_val:0{total_pixels*8}b}, "
                  f"data_in=0b{data_val:0{total_pixels*4}b}, bpp={bpp:02b}")
    dut._log.info(f"Output : actual=0b{actual_val:0{total_pixels*8}b}, "
                  f"expected=0b{expected_val:0{total_pixels*8}b}")

    assert actual_val == expected_val, \
        f"[EDGE CASE - ALL ZEROS] Mismatch: got=0b{actual_val:0{total_pixels*8}b}, expected=0b{expected_val:0{total_pixels*8}b}"

    dut._log.info("=== [EDGE CASE TEST - ALL ZEROS] PASSED ===")


@cocotb.test()
async def test_edgecase_all_ones(dut):
    """
    Edge case test: All ones in img_in and data_in.
    """
    row = int(os.getenv("ROW", "2"))
    col = int(os.getenv("COL", "2"))
    total_pixels = row * col

    dut._log.info("=== [EDGE CASE TEST - ALL ONES] Starting ===")

    # Test with bpp=11
    dut.bpp.value = 0b11

    img_val = 0xFFFFFFFF  # All ones
    data_val = 0xFFFF  # All ones

    dut.img_in.value = img_val
    dut.data_in.value = data_val

    await Timer(2, units="ns")

    bpp = 0b11
    expected_val = compute_expected_output(img_val, data_val, bpp, row, col)
    actual_val = dut.img_out.value.to_unsigned()

    dut._log.info(f"Inputs : img_in=0b{img_val:0{total_pixels*8}b}, "
                  f"data_in=0b{data_val:0{total_pixels*4}b}, bpp={bpp:02b}")
    dut._log.info(f"Output : actual=0b{actual_val:0{total_pixels*8}b}, "
                  f"expected=0b{expected_val:0{total_pixels*8}b}")

    assert actual_val == expected_val, \
        f"[EDGE CASE - ALL ONES] Mismatch: got=0b{actual_val:0{total_pixels*8}b}, expected=0b{expected_val:0{total_pixels*8}b}"

    dut._log.info("=== [EDGE CASE TEST - ALL ONES] PASSED ===")


@cocotb.test()
async def test_edgecase_alternating_bits(dut):
    """
    Edge case test: Alternating bits in img_in and data_in.
    """
    row = int(os.getenv("ROW", "2"))
    col = int(os.getenv("COL", "2"))
    total_pixels = row * col

    dut._log.info("=== [EDGE CASE TEST - ALTERNATING BITS] Starting ===")

    # Test with bpp=10
    dut.bpp.value = 0b10

    # Create alternating bit patterns: 10101010 for img_in
    img_val = 0xAA55AA55  # 10101010010101011010101001010101
    data_val = 0xAAAA  # 1010101010101010

    dut.img_in.value = img_val
    dut.data_in.value = data_val

    await Timer(2, units="ns")

    bpp = 0b10
    expected_val = compute_expected_output(img_val, data_val, bpp, row, col)
    actual_val = dut.img_out.value.to_unsigned()

    dut._log.info(f"Inputs : img_in=0b{img_val:0{total_pixels*8}b}, "
                  f"data_in=0b{data_val:0{total_pixels*4}b}, bpp={bpp:02b}")
    dut._log.info(f"Output : actual=0b{actual_val:0{total_pixels*8}b}, "
                  f"expected=0b{expected_val:0{total_pixels*8}b}")

    assert actual_val == expected_val, \
        f"[EDGE CASE - ALTERNATING BITS] Mismatch: got=0b{actual_val:0{total_pixels*8}b}, expected=0b{expected_val:0{total_pixels*8}b}"

    dut._log.info("=== [EDGE CASE TEST - ALTERNATING BITS] PASSED ===")

@cocotb.test()
async def test_random(dut):
    """
    Random test: feed random images/data across all possible bpp values.
    """

    # -- Grab row/col from environment variables
    row = int(os.getenv("ROW", "2"))
    col = int(os.getenv("COL", "2"))
    total_pixels = row * col

    dut._log.info("=== [RANDOM TEST] Starting ===")

    for trial in range(5):
        bpp_rand = random.randint(0, 3)
        dut.bpp.value = bpp_rand

        # random bits for img_in => row*col * 8 bits
        img_val = random.getrandbits(total_pixels * 8)
        dut.img_in.value = img_val

        # random bits for data_in => row*col * 4 bits
        data_val = random.getrandbits(total_pixels * 4)
        dut.data_in.value = data_val

        await Timer(2, units="ns")

        expected_val = compute_expected_output(img_val, data_val, bpp_rand, row, col)
        actual_val = dut.img_out.value.to_unsigned()

        # Log in binary:
        dut._log.info(f"[Trial {trial}] bpp={bpp_rand:02b}, "
                      f"img_in=0b{img_val:0{total_pixels*8}b}, "
                      f"data_in=0b{data_val:0{total_pixels*4}b}")
        dut._log.info(f"[Trial {trial}] actual=0b{actual_val:0{total_pixels*8}b}, "
                      f"expected=0b{expected_val:0{total_pixels*8}b}")

        # Check
        assert actual_val == expected_val, \
            f"[RANDOM TEST Trial {trial}] Mismatch: got=0b{actual_val:0{total_pixels*8}b}, expected=0b{expected_val:0{total_pixels*8}b}"

    dut._log.info("=== [RANDOM TEST] PASSED ===")
