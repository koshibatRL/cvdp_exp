import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def test_clamping_logic(dut):
    """
    Test to verify that the clamping logic works correctly in signal_correlator.
    The output should clamp to 15 if the sum exceeds the 4-bit range.
    """

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # 10 ns clock period

    # Reset the DUT
    dut.reset.value = 1
    dut.input_signal.value = 0
    dut.reference_signal.value = 0
    await RisingEdge(dut.clk)  # Wait for reset propagation
    dut.reset.value = 0
    await RisingEdge(dut.clk)  # Allow system to stabilize

    # Test case: Input that triggers clamping
    dut.input_signal.value = 0b11111111  # All bits `1`
    dut.reference_signal.value = 0b11111111  # All bits `1`

    await RisingEdge(dut.clk)  # Wait for one clock cycle
    await Timer(1, units="ns")  # Small delay for propagation

    # Extract output and check clamping
    output_value = dut.correlation_output.value.to_unsigned()
    assert output_value == 15, (
        f"Clamping test failed: Expected 15, got {output_value}"
    )

    cocotb.log.info("Clamping logic test passed: Output correctly clamps to 15.")
