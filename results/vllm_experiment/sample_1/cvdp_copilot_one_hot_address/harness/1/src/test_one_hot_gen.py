import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import harness_library as hrs_lb
import random

def compare_values(dut, model, debug=0):
    dut_ready   = dut.o_ready.value
    dut_address = dut.o_address_one_hot.value.to_unsigned()

    model_ready   = model.o_ready
    model_address = model.o_address_one_hot

    if debug == 1:
        print("\nOUTPUTS")
        print(f"DUT o_ready   = {dut_ready} MODEL o_ready   = {model_ready}")
        print(f"DUT o_address = {dut_address} MODEL o_address = {model_address}")
        print(f"DUT state     = {dut.state_ff.value} MODEL state     = {model.state}")
    
    assert dut_ready   == model_ready,   f"[ERROR] DUT o_ready does not match model o_ready: {dut_ready} != {model_ready}"
    assert dut_address == model_address, f"[ERROR] DUT o_address does not match model o_address: {dut_address} != {model_address}"

@cocotb.test()
async def test_top_fir(dut):
    """Test the One Hot Gen module with edge cases and random data."""

    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())
    model = hrs_lb.OneHotGen(dut.NS_A.value.to_unsigned(), dut.NS_B.value.to_unsigned())

    resets = 5
    runs = 100

    await hrs_lb.dut_init(dut)

    for i in range(resets):
        # Reset DUT
        # Set all inputs to 0
        dut.i_config.value    = 0
        dut.i_start.value     = 0
        dut.rst_async_n.value = 0
        await RisingEdge(dut.clk)
        dut.rst_async_n.value = 1
        await RisingEdge(dut.clk)

        # Reset model
        model.reset()

        compare_values(dut, model)

        for j in range(runs):
            if dut.i_start.value == 1:
                model.config = dut.i_config.value.to_unsigned()
                model.update()
            else:
                config = random.randint(0,3)
                dut.i_start.value  = 1
                dut.i_config.value = config
                model.config = config

            await RisingEdge(dut.clk)
            dut.i_start.value  = random.randint(0,1)
            dut.i_config.value = random.randint(0,3)
            compare_values(dut, model)

            await RisingEdge(dut.clk)
            model.update()
            dut.i_start.value  = random.randint(0,1)
            dut.i_config.value = random.randint(0,3)
            compare_values(dut, model)

            while dut.o_ready.value == 0:
                dut.i_start.value  = random.randint(0,1)
                dut.i_config.value = random.randint(0,3)
                await RisingEdge(dut.clk)
                model.update()
                compare_values(dut, model)
