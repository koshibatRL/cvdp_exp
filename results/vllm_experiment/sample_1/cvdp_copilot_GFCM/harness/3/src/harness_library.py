import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly
import random

async def phase_shifted_clock(signal, period, phase_shift, units="ns"):
    """Generates a clock with a phase shift."""
    signal.value = 0 
    # Timer doesn't accept zero offset
    if phase_shift > 0:
        await Timer(phase_shift, units=units)
    while True:
        await Timer(period // 2, units=units)
        signal.value = ~ signal.value

async def check_glitch_free_transition(dut):
    dut._log.info(f"SEL EDGE")
    await ReadOnly()
    if dut.sel.value == 0:
        dut._log.info(f"SEL 1->0")
        #Glitch condition
        await RisingEdge(dut.clk2)
        dut._log.info(f"CLK2 1st POSEEDGE")
        await RisingEdge(dut.clk2)
        dut._log.info(f"CLK2 2nd POSEEDGE")
        await ReadOnly()
        # Assert clkout is no longer follwing clk2 by the 2nd edge of clk2 (2 stage ff sync) after sel deassertion
        assert dut.clkout.value == 0, f"Glitch detected, clkout is {dut.clkout.value}"
        # Wait for two clock cycles of clk1 so that clk1 is enabled
        await RisingEdge(dut.clk1)
        dut._log.info(f"CLK1 1st POSEEDGE")
        await RisingEdge(dut.clk1)
        dut._log.info(f"CLK1 2nd POSEEDGE")

    elif dut.sel.value == 1:
        dut._log.info(f"SEL 0->1")
        await RisingEdge(dut.clk1)
        dut._log.info(f"CLK1 1st POSEEDGE")
        await RisingEdge(dut.clk1)
        dut._log.info(f"CLK1 2nd POSEEDGE")
        await ReadOnly()
        # Assert clkout is no longer follwing clk1 by the 2nd edge of clk2 ((2 stage ff sync) after sel assertion
        assert dut.clkout.value == 0, f"Glitch detected, clkout is {dut.clkout.value}"
        # Wait for two clock cycles of clk2 so that clk2 is enabled
        await RisingEdge(dut.clk2)
        dut._log.info(f"CLK2 1st POSEEDGE")
        await RisingEdge(dut.clk2)
        dut._log.info(f"CLK2 2nd POSEEDGE")
    await ReadOnly()

def random_clock_select(dut):
    # List of clock signals
    clocks = [dut.clk1, dut.clk2]
    # Randomly choose between clk1 and clk2
    selected_clk = random.choice(clocks)
    return selected_clk