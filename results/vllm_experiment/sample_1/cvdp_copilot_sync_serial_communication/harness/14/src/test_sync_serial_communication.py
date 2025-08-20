import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge,FallingEdge,Timer
import harness_library as hrs_lb
import random


sel_value = [1,2,3,4]


# Main test for sync_communication top module
@cocotb.test()
async def test_sync_communication(dut):
    #data_wd = int(dut.DATA_WIDTH.value)                                    # Get the data width from the DUT (Device Under Test)
    # Start the clock with a 10ns time period

    sel = random.choice(sel_value)

    if sel == 1:
        range_value = 8
        data_in = random.randint(0, 127)
    elif sel == 2:
        range_value = 16
        data_in = random.randint(0,4196)
    elif sel == 3:
        range_value = 32
        data_in = random.randint(0,18192)
    elif sel == 4:
        range_value = 64
        data_in = random.randint(0,154097)

    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Initialize the DUT signals with default 0
    await hrs_lb.dut_init(dut)

    # Reset the DUT rst_n signal
    await hrs_lb.reset_dut(dut.reset_n, duration_ns=25, active=False)

    # Ensure all control signals are low initially before starting the test
    dut.sel.value = 0
    dut.data_in.value = 0

    # Main test loop to validate both PISO and SIPO functionality
    for _ in range(sel):
        await drive_byte(dut,sel,range_value,data_in)
        await hrs_lb.reset_dut(dut.reset_n, duration_ns=25, active=False)

    await inject_parity_error(dut)


async def drive_byte(dut,sel,range_value,data_in):
    """Drive a byte of data to the DUT"""
    await RisingEdge(dut.clk)
    dut.data_in.value = data_in  # Assign a random byte (0-127)
    data_in_bits = f'{data_in:0{range_value}b}'
    dut._log.info(f" data_in = {int(dut.data_in.value)}, sel = {dut.sel.value}")
    for i in range(range_value):
        dut.sel.value  = sel
        #dut._log.info(f" data_in = {int(dut.data_in.value)}, sel = {dut.sel.value}")
        await RisingEdge(dut.clk)
    await RisingEdge(dut.done)
    await RisingEdge(dut.clk)
    dut._log.info(f" data_in = {int(dut.data_in.value)}, sel = {dut.sel.value}, data_out = {int(dut.data_out.value)}, done = {dut.done.value}")

    expected_data_out = dut.data_in.value
    dut._log.info(f" data_in = {int(dut.data_in.value)}, expected_data_out = {int(expected_data_out)}, data_out = {int(dut.data_out.value)}")

    assert int(dut.data_out.value) == expected_data_out, f"Test failed: Expected {expected_data_out}, got {int(dut.data_out.value)}"
    data_out = int(dut.data_out.value)
    data_out_bits = f'{data_out:0{range_value}b}'
    got_parity = {data_out_bits.count('1') % 2}
    expected_parity = {data_in_bits.count('1') % 2}
    dut._log.info(f"  expected_parity = {data_in_bits.count('1') % 2}, got_parity = {data_out_bits.count('1') % 2} parity_error = {dut.parity_error.value}")

    if expected_parity == got_parity:
        assert dut.parity_error.value == 0, f"Test failed: Got {dut.parity_error.value}"
    else:
        assert dut.parity_error.value == 1, f"Test failed: Got {dut.parity_error.value}"

async def inject_parity_error(dut):
    """Simulate injecting a parity error into the communication process."""
    # Initialize DUT signals
    data_in = random.randint(0, 127)  # Generate random byte data
    range_value = 8  # Assuming 8 bits for a byte
    sel = 1          # Corresponding to the byte-level selection
    corrupted_parity = 0

    dut.sel.value = 0
    dut.data_in.value = 0

    # Reset the DUT
    await hrs_lb.reset_dut(dut.reset_n, duration_ns=25, active=False)

    # Drive the byte of data
    dut.data_in.value = data_in
    data_in_bits = f"{data_in:08b}"

    for _ in range(range_value):
        dut.sel.value = sel
        await RisingEdge(dut.clk)

    # Wait for the TX block to signal it's done
    await RisingEdge(dut.done)
    
    # Force corrupt the parity bit (simulate bit flip)
    #corrupted_parity = not dut.uut_tx_block.parity.value  # Invert the correct parity value
    if dut.parity.value == 1:
        corrupted_parity = 0
    else:
        corrupted_parity = 1

    dut._log.info(f"Original parity: {int(dut.parity.value)}, Injecting corrupted parity: {int(corrupted_parity)}")
    dut.parity.value = corrupted_parity

    # Wait for RX block to process the corrupted data
    await RisingEdge(dut.done)

    # Validate the output
    dut._log.info(f"SEL: {int(dut.sel.value)}, Data In: {int(dut.data_in.value)}, "
                  f"Data Out: {int(dut.data_out.value)}, Done: {int(dut.done.value)}, "
                  f"Parity Error: {int(dut.parity_error.value)}")

    # Expecting a parity error
    assert dut.parity_error.value == 1, f"Parity error not detected! Parity Error: {int(dut.parity_error.value)}"
    dut._log.info("Parity error successfully injected and detected.")
