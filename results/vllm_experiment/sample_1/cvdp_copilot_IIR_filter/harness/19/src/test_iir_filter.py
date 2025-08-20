import cocotb
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb.clock import Clock
import random

async def reset(dut):
    """ Asynchronous reset that lasts a few cycles """
    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0
    dut._log.info("Reset completed")

@cocotb.test()
async def test_async_reset(dut):
    """ Test that the outputs reset properly """
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    await reset(dut)

    assert dut.y.value == 0, f"Reset test failed: y = {dut.y.value}"
    dut._log.info("Async reset test passed")

@cocotb.test()
async def test_random_input(dut):
    """ Test the filter response to random input """
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    await reset(dut)

    for _ in range(100):
        in_val = random.randint(-32768, 32767)
        dut.x.value = in_val
        await RisingEdge(dut.clk)
        # You may want to compare outputs to expected values here
        dut._log.info(f"Input: {in_val}, Output: {dut.y.value}")

    dut._log.info("Random input test completed")

@cocotb.test()
async def test_boundary_conditions(dut):
    """ Test the filter response to boundary input values """
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    await reset(dut)

    max_val = 32767
    min_val = -32768

    # Test maximum value
    dut.x.value = max_val
    await RisingEdge(dut.clk)
    max_output = dut.y.value
    dut._log.info(f"Max input: {max_val}, Output: {max_output}")

    # Test minimum value
    dut.x.value = min_val
    await RisingEdge(dut.clk)
    min_output = dut.y.value
    dut._log.info(f"Min input: {min_val}, Output: {min_output}")

    assert max_output != min_output, "Boundary condition test failed: Outputs are not distinct"
    dut._log.info("Boundary condition test passed")