import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
import random

@cocotb.test()
async def test_kogge_stone_adder(dut):
    """Test Kogge-Stone Adder: Should pass for bug-free RTL and fail for bugged RTL."""

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset DUT
    dut.reset.value = 1
    await Timer(20, units="ns")
    dut.reset.value = 0
    await RisingEdge(dut.clk)

    failures = 0

    # Run 100 randomized tests
    for i in range(100):
        A = random.randint(0, 0xFFFF)
        B = random.randint(0, 0xFFFF)
        expected_sum = (A + B) & 0x1FFFF  # 17-bit sum

        # Apply inputs
        dut.A.value = A
        dut.B.value = B
        dut.start.value = 1
        await RisingEdge(dut.clk)
        dut.start.value = 0

        # Wait for `done`
        while dut.done.value == 0:
            await RisingEdge(dut.clk)

        observed_sum = dut.Sum.value.to_unsigned()

        # Log test iteration details
        cocotb.log.info(f"Test {i+1}: A={A}, B={B}, Expected={expected_sum}, Got={observed_sum}")

        if observed_sum != expected_sum:
            failures += 1
            cocotb.log.error(f"BUG DETECTED! A={A}, B={B}, Expected={expected_sum}, Got={observed_sum}")

    # Special Cases: Directly target the faulty logic (Carry Skipping & MSB Sum Corruption)
    special_cases = [
        (0b00001111_00001111, 0b00001111_00001111),  # Carry at 3,7 should propagate correctly
        (0b00000000_11111111, 0b11111111_00000000),  # Tests full bit carry chain
        (0b01010101_01010101, 0b10101010_10101010),  # Alternating bits to check propagation
        (0b10000000_00000000, 0b10000000_00000000),  # Ensures no sum corruption at MSB
        (0b00000000_00000000, 0b11111111_11111111),  # Testing max 16-bit addition
        (0b11111111_11111111, 0b00000000_00000001),  # Edge case for ripple carry
    ]

    for i, (A, B) in enumerate(special_cases, start=1):
        expected_sum = (A + B) & 0x1FFFF  # 17-bit sum

        dut.A.value = A
        dut.B.value = B
        dut.start.value = 1
        await RisingEdge(dut.clk)
        dut.start.value = 0

        while dut.done.value == 0:
            await RisingEdge(dut.clk)

        observed_sum = dut.Sum.value.to_unsigned()

        # Log special case details
        cocotb.log.info(f"Special Case {i}: A={A}, B={B}, Expected={expected_sum}, Got={observed_sum}")

        if observed_sum != expected_sum:
            failures += 1
            cocotb.log.error(f"BUG DETECTED in SPECIAL CASE! A={A}, B={B}, Expected={expected_sum}, Got={observed_sum}")

    # Fail the test if any failures were detected
    assert failures == 0, f"Test failed! {failures} incorrect results detected!"

    cocotb.log.info("All test cases passed successfully for bug-free RTL!")
