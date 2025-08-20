import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import random
import harness_library as hrs_lb
import time

@cocotb.test()
async def test_moving_average(dut):

    # Start clock
    cocotb.start_soon(Clock(dut.clk, 2, units='ns').start())
    cocotb.log.info("[INFO] Clock started.")
    width = 12
    window = 8

    cocotb.log.info(f"WIDTH = {width}, WINDOW_SIZE = {window}")

    # Initialize DUT
    await hrs_lb.dut_init(dut) 
    # Apply reset and enable
    await hrs_lb.reset_dut(dut)
    await hrs_lb.enable_dut(dut)

    # Wait for a couple of cycles to stabilize
    for _ in range(2):
        await RisingEdge(dut.clk)

    # Ensure all outputs are zero
    assert dut.data_out.value == 0, f"[ERROR] data_out is not zero after reset: {dut.data_out.value}"

    current_sum = 0
    data_queue = []
    previous_expected_avg = None  # Variable to hold the previous cycle's expected average
    cycle_num = data_in = random.randint(500, 1000)
    cycle_off_enable = random.randint(1,int(cycle_num/2))
    cycle_on_enable  = random.randint(cycle_off_enable+1,int(cycle_num*3/4))

    # Just for DEBUG, set to 1
    debug = 0

    if debug:
        cocotb.log.info(cycle_off_enable)
        cocotb.log.info(cycle_on_enable)
    # Apply random stimulus and check output
    for cycle in range(cycle_num):  # Run the test for 20 cycles
        if cycle == cycle_off_enable:
            # Disable the DUT after {cycle_off_enable} cycles
            cocotb.log.info(f'[INFO] Disabling DUT after {cycle_off_enable} cycles')
            dut.enable.value = 0

        if cycle == cycle_on_enable:
            # Re-enable the DUT after {cycle_on_enable-cycle_off_enable} cycles
            cocotb.log.info(f'[INFO] Re-enabling DUT after {cycle_on_enable} cycles')
            dut.enable.value = 1

        # Generate random data input
        data_in = random.randint(0, 2**width-1)
        dut.data_in.value = data_in
        await RisingEdge(dut.clk)

        if dut.enable.value == 1:
            # Calculate the expected average using the helper function
            expected_avg, current_sum = await hrs_lb.calculate_moving_average(data_queue, current_sum, data_in, window)

        # Read the DUT output
        actual_avg = dut.data_out.value.to_unsigned()

        # Compare the current DUT output with the previous cycle's expected average
        if previous_expected_avg is not None:
            assert actual_avg == previous_expected_avg, \
                f"[ERROR] Mismatch at cycle {cycle}: Expected {previous_expected_avg}, got {actual_avg}"

            if debug:
                cocotb.log.info(f"[DEBUG] Cycle {cycle}/{cycle_num}: DUT average = {actual_avg}")
                cocotb.log.info(f"[DEBUG] Cycle {cycle}/{cycle_num}: Testbench average = {previous_expected_avg}")
            
        # Update the previous expected average only if enable is high
        if dut.enable.value == 1:
            previous_expected_avg = expected_avg

    # Disable the module and finish the test
    dut.enable.value = 0
    await RisingEdge(dut.clk)
    cocotb.log.info("[INFO] Test completed successfully.")