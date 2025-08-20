import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles, Timer

# ----------------------------------------
# - Tests
# ----------------------------------------

async def init_dut(dut):

    dut.rst_in.value     = 1
    dut.mode_in.value    = 0
    dut.enable_in.value  = 0
    dut.ref_modulo.value = 0

    await RisingEdge(dut.clk_in)


@cocotb.test()
async def test_basic(dut):

    cocotb.start_soon(Clock(dut.clk_in, 10, units='ns').start())
    await init_dut(dut)

    # ----------------------------------------
    # - Check No Operation
    # ----------------------------------------

    await FallingEdge(dut.clk_in)

    dut.mode_in.value   = 5 # Testing Ring Counter
    dut.enable_in.value = 0 # Testing Ring Counter
    
    await RisingEdge(dut.clk_in)
    dut.rst_in.value    = 0

    await FallingEdge(dut.clk_in)
    dut.enable_in.value = 1

    for _ in range(5):
        await FallingEdge(dut.clk_in)

    assert dut.o_count.value == 2 ** 4