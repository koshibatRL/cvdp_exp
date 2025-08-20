import cocotb
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def test_register_file_bist(dut):
    """Test BIST functionality of the cvdp_copilot_register_file_2R1W module"""

    # Constants
    DATA_WIDTH = 32
    DEPTH = 5

    # Initialize input signals
    dut.resetn.value = 0
    dut.test_mode.value = 0
    dut.din.value = 0
    dut.wad1.value = 0
    dut.wen1.value = 0
    dut.rad1.value = 0
    dut.rad2.value = 0
    dut.ren1.value = 0
    dut.ren2.value = 0

    pass_count = 0
    fail_count = 0

    # Clock Generation (assuming a 100 MHz clock)
    async def clock_gen():
        while True:
            dut.clk.value = 0
            await Timer(5, units="ns")
            dut.clk.value = 1
            await Timer(5, units="ns")

    # Start clock
    cocotb.start_soon(clock_gen())

    # Apply reset
    dut.resetn.value = 0
    await RisingEdge(dut.clk)
    dut.resetn.value = 1
    await RisingEdge(dut.clk)

    # Define a helper function for waiting on bist_done
    async def wait_for_bist_done():
        while not int(dut.bist_done.value):
            await RisingEdge(dut.clk)

    # Test 1: BIST Normal Operation
    dut._log.info("Test 1: BIST Normal Operation")
    dut.test_mode.value = 1
    await RisingEdge(dut.clk)

    # Wait for BIST completion
    await wait_for_bist_done()

    # Check BIST result
    if dut.bist_fail.value != 0:
        dut._log.error("Test 1 Failed: BIST reported failure")
        fail_count += 1
    else:
        dut._log.info("Test 1 Passed: BIST completed successfully")
        pass_count += 1

    # Reset test mode
    dut.test_mode.value = 0
    await RisingEdge(dut.clk)

    # Test 3: Normal Operation After BIST
    dut._log.info("Test 3: Normal Operation After BIST")
    dut.din.value = 0xA5A5A5A5
    dut.wad1.value = 5
    dut.wen1.value = 1
    await RisingEdge(dut.clk)
    dut.wen1.value = 0

    # Read from the register file
    dut.ren1.value = 1
    dut.rad1.value = 5
    await RisingEdge(dut.clk)

    # Check output
    if dut.dout1.value != 0xA5A5A5A5:
        dut._log.error(f"Test 3 Failed: Expected dout1 = 0xA5A5A5A5, got {dut.dout1.value:#x}")
        fail_count += 1
    else:
        dut._log.info("Test 3 Passed: Normal operation successful")
        pass_count += 1

    # Test 4: BIST Re-entry
    dut._log.info("Test 4: BIST Re-entry")
    dut.test_mode.value = 1
    await RisingEdge(dut.clk)

    # Wait for BIST completion
    await wait_for_bist_done()

    # Check BIST result
    if dut.bist_fail.value != 0:
        dut._log.error("Test 4 Failed: BIST reported failure upon re-entry")
        fail_count += 1
    else:
        dut._log.info("Test 4 Passed: BIST re-entry successful")
        pass_count += 1

    # Reset test mode
    dut.test_mode.value = 0
    await RisingEdge(dut.clk)

    # Test 5: BIST During Normal Operation
    dut._log.info("Test 5: BIST Activation During Normal Operation")
    dut.din.value = 0xDEADBEEF
    dut.wad1.value = 15
    dut.wen1.value = 1
    await RisingEdge(dut.clk)
    dut.wen1.value = 0

    # Activate BIST during normal operation
    dut.test_mode.value = 1
    await RisingEdge(dut.clk)

    # Wait for BIST completion
    await wait_for_bist_done()

    # Check BIST result
    if dut.bist_fail.value != 0:
        dut._log.error("Test 5 Failed: BIST reported failure during normal operation")
        fail_count += 1
    else:
        dut._log.info("Test 5 Passed: BIST during normal operation successful")
        pass_count += 1

    # Display test results
    dut._log.info("-------------------------------------------------")
    dut._log.info("Test Results:")
    dut._log.info("Total Tests Passed: {}".format(pass_count))
    dut._log.info("Total Tests Failed: {}".format(fail_count))
    dut._log.info("-------------------------------------------------")

    # Assert based on test outcomes
    assert fail_count == 0, "Some tests failed. Check log for details."
    dut._log.info("All tests passed successfully!")
