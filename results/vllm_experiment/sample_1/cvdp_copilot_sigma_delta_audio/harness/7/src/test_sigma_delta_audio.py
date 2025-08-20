import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge
import random

@cocotb.test()
async def test_sigma_delta_audio(dut):
    """Cocotb testbench replicating the paula_audio_sigmadelta_tb logic."""

    # Create a 10ns total period clock (toggling every 5ns)
    cocotb.start_soon(Clock(dut.clk_sig, 5, units="ns").start())

    # We'll track errors in a local Python variable
    errors = 0

    cocotb.log.info("----- Test Start -----")

    # Initialize inputs
    dut.clk_sig.value = 0
    dut.clk_en_sig.value = 0
    dut.load_data_sum.value = 0
    dut.read_data_sum.value = 0
    
    # Apply reset-like condition for 20ns
    await Timer(20, units="ns")
    dut.clk_en_sig.value = 1
    
    # Test Case 1: Zero Input Test
    cocotb.log.info("Running Test Case 1: Zero Input Test")
    dut.load_data_sum.value = 0
    dut.read_data_sum.value = 0
    await Timer(20, units="ns")
    if (dut.left_sig.value != 0) or (dut.right_sig.value != 0):
        cocotb.log.error("Test Case 1 Failed")
        errors += 1
    else:
        cocotb.log.info("Test Case 1 Passed")

    # Test Case 2: Maximum Negative Values
    cocotb.log.info("Running Test Case 2: Maximum Negative Values")
    dut.load_data_sum.value = 0x80  # 15'h80 (two's complement negative for 15 bits)
    dut.read_data_sum.value = 0x80
    await Timer(20, units="ns")
    if (dut.left_sig.value == 1) or (dut.right_sig.value == 1):
        cocotb.log.error("Test Case 2 Failed")
        errors += 1
    else:
        cocotb.log.info("Test Case 2 Passed")

    # Test Case 3: Small Positive Values
    cocotb.log.info("Running Test Case 3: Small Positive Values")
    dut.load_data_sum.value = 10
    dut.read_data_sum.value = 20
    await Timer(20, units="ns")
    if (dut.left_sig.value == 1) or (dut.right_sig.value == 1):
        cocotb.log.error("Test Case 3 Failed")
        errors += 1
    else:
        cocotb.log.info("Test Case 3 Passed")

    # Test Case 4: Small Negative Values
    cocotb.log.info("Running Test Case 4: Small Negative Values")
    # For a 15-bit negative, mask it properly (though Cocotb may handle small negatives directly).
    dut.load_data_sum.value = (-10) & 0x7FFF
    dut.read_data_sum.value = (-20) & 0x7FFF
    await Timer(20, units="ns")
    if (dut.left_sig.value == 1) or (dut.right_sig.value == 1):
        cocotb.log.error("Test Case 4 Failed")
        errors += 1
    else:
        cocotb.log.info("Test Case 4 Passed")

    # Test Case 5: Large Alternating Values
    cocotb.log.info("Running Test Case 5: Large Alternating Values")
    dut.load_data_sum.value = 0x40
    dut.read_data_sum.value = 0xC0
    await Timer(10, units="ns")
    if dut.left_sig.value == 1:
        cocotb.log.error("Test Case 5 Failed")
        errors += 1
    else:
        cocotb.log.info("Test Case 5 Passed")

    # Test Case 6: Rapid Change in Values
    cocotb.log.info("Running Test Case 6: Rapid Change in Values")
    dut.load_data_sum.value = 50
    dut.read_data_sum.value = 60
    await Timer(10, units="ns")
    dut.load_data_sum.value = 70
    dut.read_data_sum.value = 80
    await Timer(10, units="ns")
    if (dut.left_sig.value == 1) or (dut.right_sig.value == 1):
        cocotb.log.error("Test Case 6 Failed")
        errors += 1
    else:
        cocotb.log.info("Test Case 6 Passed")

    # Test Case 7: Incremental Increase
    cocotb.log.info("Running Test Case 7: Incremental Increase")
    dut.load_data_sum.value = 1
    dut.read_data_sum.value = 2
    for _ in range(5):
        await Timer(10, units="ns")
        # replicate "load_data_sum = load_data_sum + 15'd1"
        dut.load_data_sum.value = (int(dut.load_data_sum.value) + 1) & 0x7FFF
        # replicate "read_data_sum = read_data_sum + 15'd1"
        dut.read_data_sum.value = (int(dut.read_data_sum.value) + 1) & 0x7FFF
    # After the loop, check if left_sig==0 or right_sig==0
    if (dut.left_sig.value == 0) or (dut.right_sig.value == 0):
        cocotb.log.error("Test Case 7 Failed")
        errors += 1
    else:
        cocotb.log.info("Test Case 7 Passed")

    # Test Case 8: Decremental Decrease
    cocotb.log.info("Running Test Case 8: Decremental Decrease")
    dut.load_data_sum.value = 10
    dut.read_data_sum.value = 20
    for _ in range(5):
        await Timer(10, units="ns")
        dut.load_data_sum.value = (int(dut.load_data_sum.value) - 1) & 0x7FFF
        dut.read_data_sum.value = (int(dut.read_data_sum.value) - 1) & 0x7FFF
    if (dut.left_sig.value == 1) or (dut.right_sig.value == 1):
        cocotb.log.error("Test Case 8 Failed")
        errors += 1
    else:
        cocotb.log.info("Test Case 8 Passed")

    # Final Test Result
    if errors == 0:
        cocotb.log.info("All tests passed!")
    else:
        cocotb.log.error(f"Some tests failed. Errors: {errors}")

    cocotb.log.info("----- Test Completed -----")
