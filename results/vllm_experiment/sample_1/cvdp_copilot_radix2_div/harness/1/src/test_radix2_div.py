import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.coroutine
async def reset_dut(dut, duration_ns):
    """Reset the DUT."""
    dut.rst_n.value = 0
    await Timer(duration_ns, units='ns')
    await RisingEdge(dut.clk)  # Align reset release with clock
    dut.rst_n.value = 1
    await Timer(10, units='ns')  # Small delay to ensure stability


@cocotb.coroutine
async def perform_test(dut, dividend, divisor, failed_tests):
    """Perform a single test case."""
    # Apply inputs
    dut.dividend.value = dividend
    dut.divisor.value = divisor
    dut.start.value = 1
    await RisingEdge(dut.clk)  # Align inputs with the clock edge
    dut.start.value = 0

    # Wait for the `done` signal to go high (max latency = 10 cycles)
    for _ in range(10):
        if dut.done.value:
            break
        await RisingEdge(dut.clk)
    else:
        raise cocotb.result.TestFailure("Timeout waiting for `done` signal.")

    # Allow one additional clock cycle for signal stabilization
    await RisingEdge(dut.clk)

    # Compute expected results
    if divisor != 0:
        expected_quotient = dividend // divisor
        expected_remainder = dividend % divisor
    else:
        expected_quotient = 0xFF  # Error case for divide by zero
        expected_remainder = 0xFF

    # Log results
    cocotb.log.info(f"Test Case: Dividend={dividend}, Divisor={divisor}")
    cocotb.log.info(f"Expected: Quotient={expected_quotient}, Remainder={expected_remainder}")
    cocotb.log.info(f"Received: Quotient={int(dut.quotient.value)}, Remainder={int(dut.remainder.value)}")

    # Check results and collect failures
    if int(dut.quotient.value) != expected_quotient or int(dut.remainder.value) != expected_remainder:
        cocotb.log.error(f"Test FAILED: Dividend={dividend}, Divisor={divisor}")
        failed_tests.append((dividend, divisor, expected_quotient, expected_remainder,
                             int(dut.quotient.value), int(dut.remainder.value)))
    else:
        cocotb.log.info("Test PASSED!")


@cocotb.test()
async def tb_verified_radix2_div(dut):
    """Testbench for verified_radix2_div."""
    # Set up clock with a 10ns period (100MHz frequency)
    clock = Clock(dut.clk, 10, units='ns')
    cocotb.start_soon(clock.start())  # Start the clock

    # Reset the DUT
    await reset_dut(dut, 20)

    # List to store failed test cases
    failed_tests = []

    # Predefined test cases
    test_cases = [
        (100, 10),
        (255, 15),
        (0, 1),
        (1, 0),  # Divide by zero
        (50, 25),
        (200, 20),
        (128, 64),
        (255, 1),
        (1, 255),
        (128, 128),
        (15, 4),
        (255, 255),
        (250, 5),
        (77, 7),
        (123, 11),
        (90, 9),
    ]

    for dividend, divisor in test_cases:
        await perform_test(dut, dividend, divisor, failed_tests)

    # Summary of test results
    if failed_tests:
        cocotb.log.error("\nSUMMARY OF FAILED TEST CASES:")
        for failure in failed_tests:
            dividend, divisor, expected_quotient, expected_remainder, actual_quotient, actual_remainder = failure
            cocotb.log.error(
                f"FAILED: Dividend={dividend}, Divisor={divisor}, "
                f"Expected: Quotient={expected_quotient}, Remainder={expected_remainder}, "
                f"Received: Quotient={actual_quotient}, Remainder={actual_remainder}"
            )
        raise cocotb.result.TestFailure(f"{len(failed_tests)} test(s) failed.")
    else:
        cocotb.log.info("All test cases passed!")
