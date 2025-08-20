import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

def flatten_array(values, width):
    """Flatten a list of integer values (each 'width' bits wide) into a single integer.
       The 0th element becomes the least-significant WIDTH bits."""
    flattened = 0
    for i, val in enumerate(values):
        flattened |= (val & ((1 << width) - 1)) << (i * width)
    return flattened

async def reset_dut(dut, duration_ns=20):
    dut.rst.value = 1
    # Wait a few clock cycles (assume a 10 ns period)
    for _ in range((duration_ns // 10) + 1):
        await RisingEdge(dut.clk)
    dut.rst.value = 0
    await RisingEdge(dut.clk)

@cocotb.test()
async def run_all_tests(dut):
    """Top-level test for the elastic_buffer_pattern_matcher."""
    # Start a 10 ns clock on dut.clk.
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset the DUT.
    await reset_dut(dut, duration_ns=20)

    #---------------------------------------------------------------------------
    # Get derived parameter values from the DUT.
    # These should match the RTL defaults.
    #---------------------------------------------------------------------------
    WIDTH = int(dut.WIDTH.value)
    NUM_PATTERNS = int(dut.NUM_PATTERNS.value)
    full_mask = (1 << WIDTH) - 1

    # Helper: wait for the 3-stage pipeline to flush.
    async def wait_pipeline():
        for _ in range(4):
            await RisingEdge(dut.clk)
            dut.i_valid.value = 0

    # Use a test value that fits within WIDTH bits.
    test_val = 0xA & full_mask

    #---------------------------------------------------------------------------
    # Test 1: Exact Match
    #   - i_data equals each i_pattern.
    #   - Full mask (all ones).
    #   - Error tolerance = 0.
    # Expected: All bits of o_match should be 1.
    #---------------------------------------------------------------------------
    dut.i_data.value = test_val
    patterns = [test_val for _ in range(NUM_PATTERNS)]
    masks = [full_mask for _ in range(NUM_PATTERNS)]
    dut.i_pattern.value = flatten_array(patterns, WIDTH)
    dut.i_mask.value = flatten_array(masks, WIDTH)
    dut.i_valid.value = 1
    dut.i_error_tolerance.value = 0
    await wait_pipeline()
    for i in range(NUM_PATTERNS):
        assert int(dut.o_match.value[i]) == 1, (
            f"Test 1: Exact match failed for pattern {i}: expected 1, got {dut.o_match.value[i]}"
        )
    dut._log.info("Test 1: Exact match passed.")

    #---------------------------------------------------------------------------
    # Test 2: One Bit Error Within Tolerance
    #   - For pattern 0, flip one bit (LSB) in i_pattern.
    #   - All other patterns match exactly.
    #   - Error tolerance = 1.
    # Expected: Pattern 0 matches (error count 1) and others match.
    #---------------------------------------------------------------------------
    one_bit_error = test_val ^ 0x1  # flip LSB
    dut.i_data.value = test_val
    patterns = [one_bit_error] + [test_val for _ in range(NUM_PATTERNS - 1)]
    masks = [full_mask for _ in range(NUM_PATTERNS)]
    dut.i_pattern.value = flatten_array(patterns, WIDTH)
    dut.i_mask.value = flatten_array(masks, WIDTH)
    dut.i_valid.value = 1
    dut.i_error_tolerance.value = 1
    await wait_pipeline()
    assert int(dut.o_match.value[0]) == 1, "Test 2: One bit error within tolerance failed for pattern0."
    for i in range(1, NUM_PATTERNS):
        assert int(dut.o_match.value[i]) == 1, (
            f"Test 2: Exact match failed for pattern {i} in one-bit test."
        )
    dut._log.info("Test 2: One bit error within tolerance passed.")

    #---------------------------------------------------------------------------
    # Test 3: One Bit Error Outside Tolerance
    #   - Same as Test 2 but error tolerance = 0.
    # Expected: Pattern 0 should not match; others should match.
    #---------------------------------------------------------------------------
    dut.i_data.value = test_val
    patterns = [one_bit_error] + [test_val for _ in range(NUM_PATTERNS - 1)]
    masks = [full_mask for _ in range(NUM_PATTERNS)]
    dut.i_pattern.value = flatten_array(patterns, WIDTH)
    dut.i_mask.value = flatten_array(masks, WIDTH)
    dut.i_valid.value = 1
    dut.i_error_tolerance.value = 0
    await wait_pipeline()
    assert int(dut.o_match.value[0]) == 0, "Test 3: One bit error outside tolerance failed for pattern0."
    for i in range(1, NUM_PATTERNS):
        assert int(dut.o_match.value[i]) == 1, (
            f"Test 3: Exact match failed for pattern {i} in one-bit error outside tolerance test."
        )
    dut._log.info("Test 3: One bit error outside tolerance passed.")

    #---------------------------------------------------------------------------
    # Test 4: Mask (Don't-Care) Test
    #   - For pattern 0, ignore the lower 4 bits by zeroing them in the mask.
    #   - i_pattern differs from i_data only in the lower 4 bits.
    # Expected: The match should be asserted.
    #---------------------------------------------------------------------------
    # If WIDTH is less than 4, use full_mask (i.e. no don't-care bits).
    mask_ignore_lower4 = full_mask & ~(0xF) if WIDTH >= 4 else full_mask
    dut.i_data.value = test_val
    patterns = [test_val ^ 0xF] + [test_val for _ in range(NUM_PATTERNS - 1)]
    masks = [mask_ignore_lower4] + [full_mask for _ in range(NUM_PATTERNS - 1)]
    dut.i_pattern.value = flatten_array(patterns, WIDTH)
    dut.i_mask.value = flatten_array(masks, WIDTH)
    dut.i_valid.value = 1
    dut.i_error_tolerance.value = 0
    await wait_pipeline()
    assert int(dut.o_match.value[0]) == 1, "Test 4: Mask (don't-care) test failed for pattern0."
    dut._log.info("Test 4: Mask (don't-care) test passed.")

    #---------------------------------------------------------------------------
    # Test 5: Multiple Pattern Scenario with Mixed Results
    #   - Pattern 0: Exact match.
    #   - Pattern 1: One bit error (within tolerance).
    #   - Pattern 2: Two bit errors (exceeds tolerance).
    #   - Pattern 3: Mask all bits (mask = 0, so always match).
    #---------------------------------------------------------------------------
    dut.i_data.value = test_val
    patterns = [
        test_val,              # Pattern 0: exact match.
        test_val ^ 0x2,        # Pattern 1: one bit error.
        test_val ^ 0x3,        # Pattern 2: two bit errors.
        (0xDEAD & full_mask)   # Pattern 3: arbitrary value.
    ]
    masks = [
        full_mask,             # Pattern 0.
        full_mask,             # Pattern 1.
        full_mask,             # Pattern 2.
        0                      # Pattern 3: all don't care.
    ]
    dut.i_pattern.value = flatten_array(patterns, WIDTH)
    dut.i_mask.value = flatten_array(masks, WIDTH)
    dut.i_valid.value = 1
    dut.i_error_tolerance.value = 1
    await wait_pipeline()
    assert int(dut.o_match.value[0]) == 1, "Test 5: Pattern 0 failed (exact match)."
    assert int(dut.o_match.value[1]) == 1, "Test 5: Pattern 1 failed (one bit error within tolerance)."
    assert int(dut.o_match.value[2]) == 0, "Test 5: Pattern 2 failed (two bit errors, outside tolerance)."
    assert int(dut.o_match.value[3]) == 1, "Test 5: Pattern 3 failed (mask don't care)."
    dut._log.info("Test 5: Multiple pattern scenario passed.")

    #---------------------------------------------------------------------------
    # Test 6: Maximum Error Tolerance
    #   - Set i_error_tolerance to WIDTH.
    #   - For each pattern, use the complement of i_data (all bits differ).
    # Expected: With tolerance equal to WIDTH, all patterns match.
    #---------------------------------------------------------------------------
    dut.i_data.value = 0x0
    patterns = [((~0x0) & full_mask) for _ in range(NUM_PATTERNS)]
    masks = [full_mask for _ in range(NUM_PATTERNS)]
    dut.i_pattern.value = flatten_array(patterns, WIDTH)
    dut.i_mask.value = flatten_array(masks, WIDTH)
    dut.i_valid.value = 1
    dut.i_error_tolerance.value = WIDTH
    await wait_pipeline()
    for i in range(NUM_PATTERNS):
        assert int(dut.o_match.value[i]) == 1, f"Test 6: Maximum error tolerance failed for pattern {i}."
    dut._log.info("Test 6: Maximum error tolerance test passed.")

    #---------------------------------------------------------------------------
    # Test 7: Randomized Testing
    #   - For several iterations, generate random i_data, patterns, and masks.
    #   - Compute the expected error count per pattern and compare it to a random
    #     tolerance (between 0 and WIDTH//2).
    #---------------------------------------------------------------------------
    for iter in range(10):
        random_data = random.getrandbits(WIDTH)
        dut.i_data.value = random_data
        expected_matches = []
        tol = random.randint(0, WIDTH // 2)
        dut.i_error_tolerance.value = tol
        patterns = []
        masks = []
        for i in range(NUM_PATTERNS):
            pat = random.getrandbits(WIDTH)
            msk = random.getrandbits(WIDTH)
            patterns.append(pat)
            masks.append(msk)
            diff = (random_data ^ pat) & msk
            error_count = sum(1 for bit in range(WIDTH) if diff & (1 << bit))
            expected_matches.append(1 if error_count <= tol else 0)
        dut.i_pattern.value = flatten_array(patterns, WIDTH)
        dut.i_mask.value = flatten_array(masks, WIDTH)
        dut.i_valid.value = 1
        await wait_pipeline()
        for i in range(NUM_PATTERNS):
            assert int(dut.o_match.value[i]) == expected_matches[i], (
                f"Test 7: Random test iteration {iter}, pattern {i}: "
                f"expected {expected_matches[i]}, got {dut.o_match.value[i]}"
            )
    dut._log.info("Test 7: Randomized tests passed.")

    dut._log.info("All tests passed successfully!")
