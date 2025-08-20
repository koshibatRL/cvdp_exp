import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random
import harness_library as hrs_lb

@cocotb.test()
async def test_binary_multiplier_random(dut):

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # Start clock

    # Apply reset and verify zeroed outputs
    await hrs_lb.apply_async_reset(dut)

    # Number of random test cases to generate
    num_random_tests = 5
    WIDTH = int(dut.WIDTH.value)
    MAX_VAL = (1 << WIDTH) - 1

    for _ in range(num_random_tests):
        # Generate random values within WIDTH range
        A = random.randint(0, MAX_VAL)
        B = random.randint(0, MAX_VAL)

        # Call multiplier with random inputs and check product
        await hrs_lb.multiplier(dut, A, B)

        # Measure latency and check expected latency
        observed_latency = await hrs_lb.measure_latency(dut)
        expected_latency = WIDTH + 2
        assert observed_latency == expected_latency, f"Latency mismatch: Expected {expected_latency}, Got {observed_latency}"

        # Verify the product against the expected value
        hrs_lb.check_product(dut, A, B)

    dut._log.info(f"Completed random test cases for WIDTH = {WIDTH}")


@cocotb.test()
async def test_binary_multiplier_max_value(dut):

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # Start clock

    # Apply reset and verify zeroed outputs
    await hrs_lb.apply_async_reset(dut)

    # Read WIDTH from the DUT
    WIDTH = int(dut.WIDTH.value)
    MAX_VAL = (1 << WIDTH) - 1
    A = MAX_VAL
    B = MAX_VAL

    # Call the multiplier and check the product
    await hrs_lb.multiplier(dut, A, B)

    # Measure and check latency
    observed_latency = await hrs_lb.measure_latency(dut)
    expected_latency = WIDTH + 2
    assert observed_latency == expected_latency, f"Latency mismatch: Expected {expected_latency}, Got {observed_latency}"

    # Verify the product against the expected maximum value
    hrs_lb.check_product(dut, A, B)

    dut._log.info(f"Max value test completed for WIDTH = {WIDTH}")


@cocotb.test()
async def test_binary_multiplier_alternating_bits(dut):

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # Start clock

    # Apply reset and verify zeroed outputs
    await hrs_lb.apply_async_reset(dut)

    WIDTH = int(dut.WIDTH.value)

    # Generate alternating bit patterns, accounting for both even and odd WIDTH
    A_pattern = ("01" * ((WIDTH + 1) // 2))[:WIDTH]  # Ensure length matches WIDTH
    B_pattern = ("10" * ((WIDTH + 1) // 2))[:WIDTH]  # Ensure length matches WIDTH

    # Convert patterns to integers
    A = int(A_pattern, 2)
    B = int(B_pattern, 2)

    # Call multiplier with alternating bit patterns
    await hrs_lb.multiplier(dut, A, B)

    # Measure and check latency
    observed_latency = await hrs_lb.measure_latency(dut)
    expected_latency = WIDTH + 2
    assert observed_latency == expected_latency, f"Latency mismatch: Expected {expected_latency}, Got {observed_latency}"

    # Verify the product for the alternating bit pattern
    hrs_lb.check_product(dut, A, B)

    dut._log.info("Alternating bits test completed.")


@cocotb.test()
async def test_binary_multiplier_zero(dut):

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # Start clock

    # Apply reset and verify zeroed outputs
    await hrs_lb.apply_async_reset(dut)

    WIDTH = int(dut.WIDTH.value)
    expected_latency = WIDTH + 2  # Expected latency for zero multiplication

    # Test case 1: A = 0, B = random non-zero
    A = 0
    B = random.randint(1, (1 << WIDTH) - 1)
    await hrs_lb.multiplier(dut, A, B)

    # Measure latency and check if it matches expected
    observed_latency = await hrs_lb.measure_latency(dut)
    assert observed_latency == expected_latency, f"Latency mismatch: Expected {expected_latency}, Got {observed_latency}"
    hrs_lb.check_product(dut, A, B)

    # Test case 2: A = random non-zero, B = 0
    A = random.randint(1, (1 << WIDTH) - 1)
    B = 0
    await hrs_lb.multiplier(dut, A, B)

    # Measure latency and check if it matches expected
    observed_latency = await hrs_lb.measure_latency(dut)
    assert observed_latency == expected_latency, f"Latency mismatch: Expected {expected_latency}, Got {observed_latency}"
    hrs_lb.check_product(dut, A, B)

    # Test case 3: A = 0, B = 0
    A, B = 0, 0
    await hrs_lb.multiplier(dut, A, B)

    # Measure latency and check if it matches expected
    observed_latency = await hrs_lb.measure_latency(dut)
    assert observed_latency == expected_latency, f"Latency mismatch: Expected {expected_latency}, Got {observed_latency}"
    hrs_lb.check_product(dut, A, B)

    dut._log.info("Zero multiplication test cases completed.")
