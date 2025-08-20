import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge
import harness_library as hrs_lb  
import random


@cocotb.test()
async def test_bcd_to_excess_3(dut):
    """ Test BCD to Excess-3 conversion with parity and error checks """

    # Start the clock with a period of 10ns
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Initialize the DUT signals to default states
    await hrs_lb.dut_init(dut)

    # Apply Reset
    # Reset is active high; this block ensures DUT starts in a known state
    dut.rst.value = 1
    dut.enable.value = 0  
    dut.bcd.value = 0  
    await FallingEdge(dut.clk)  
    dut.rst.value = 0  # Release reset

    # Enable the DUT
    dut.enable.value = 1  # Enable the DUT for normal operation
    await FallingEdge(dut.clk)  # Wait for one clock edge to synchronize

    # Helper function to calculate expected parity for a 4-bit BCD input
    def calculate_parity(bcd):
        # XOR reduction: parity is calculated as XOR of all bits of the BCD input
        return (bcd & 1) ^ ((bcd >> 1) & 1) ^ ((bcd >> 2) & 1) ^ ((bcd >> 3) & 1)

    # Helper function to check the DUT's outputs against expected values
    def check_output(bcd, expected_excess3, expected_error, expected_parity):
        # Verify Excess-3 output
        assert dut.excess3.value == expected_excess3, (
            f"BCD={bcd}: Expected Excess-3={expected_excess3}, Got={int(dut.excess3.value)}"
        )
        # Verify Error output
        assert dut.error.value == expected_error, (
            f"BCD={bcd}: Expected Error={expected_error}, Got={int(dut.error.value)}"
        )
        # Verify Parity output
        assert dut.parity.value == expected_parity, (
            f"BCD={bcd}: Expected Parity={expected_parity}, Got={int(dut.parity.value)}"
        )

    # Test all valid BCD inputs (0-9)
    # Map valid BCD inputs to their expected Excess-3 outputs
    valid_bcd_to_excess3 = {
        0: 3, 1: 4, 2: 5, 3: 6, 4: 7,
        5: 8, 6: 9, 7: 10, 8: 11, 9: 12,
    }

    for bcd, expected_excess3 in valid_bcd_to_excess3.items():
        # Apply valid BCD input
        dut.bcd.value = bcd
        await FallingEdge(dut.clk)  # Wait for one clock edge to capture output
        # Calculate expected parity for the input
        expected_parity = calculate_parity(bcd)
        # Check the DUT outputs
        check_output(bcd, expected_excess3, expected_error=0, expected_parity=expected_parity)
        print(f"Valid Test Passed: BCD={bcd}, Excess-3={expected_excess3}, Parity={expected_parity}")

    # Test invalid BCD inputs (e.g., values greater than 9)
    # Map invalid BCD inputs to their expected behavior
    invalid_bcd_values = [10, 15]
    for bcd in invalid_bcd_values:
        # Apply invalid BCD input
        dut.bcd.value = bcd
        await FallingEdge(dut.clk)  # Wait for one clock edge to capture output
        # Calculate expected parity for the invalid input
        expected_parity = calculate_parity(bcd)
        # Check the DUT outputs: Expect error=1, Excess-3=0
        check_output(bcd, expected_excess3=0, expected_error=1, expected_parity=expected_parity)
        print(f"Invalid Test Passed: BCD={bcd}, Excess-3=0, Error Raised, Parity={expected_parity}")

    # Test reset functionality
    # Apply reset signal
    dut.rst.value = 1
    await FallingEdge(dut.clk)  # Wait for the reset to propagate
    # Check that all outputs are cleared to their default state
    assert dut.excess3.value == 0, "Reset failed to clear Excess-3 output"
    assert dut.error.value == 0, "Reset failed to clear Error flag"
    assert dut.parity.value == 0, "Reset failed to clear Parity output"
    dut.rst.value = 0  # Release reset
    await FallingEdge(dut.clk)  # Wait for reset to deassert
    print("Reset Test Passed")

    # Re-test a valid BCD input after reset to ensure normal operation resumes
    dut.bcd.value = 1  # Apply valid BCD input
    await FallingEdge(dut.clk)
    expected_parity = calculate_parity(1)  # Calculate expected parity for input 1
    check_output(1, expected_excess3=4, expected_error=0, expected_parity=expected_parity)
    print("Post-Reset Test Passed")

    # Finish simulation
    cocotb.log.info("All tests completed successfully.")






'''import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer
import harness_library as hrs_lb
import random

@cocotb.test()
async def bcd_to_excess_3(dut):
    """ Test BCD to Excess-3 conversion including error flag assertions. """

    # Start the clock with a period of 10ns
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Initialize the DUT signals
    await hrs_lb.dut_init(dut)

    # Task: Apply reset (Active High)
    dut.rst.value = 1
    await FallingEdge(dut.clk)  # Wait for the next clock edge
    dut.rst.value = 0
    #await RisingEdge(dut.clk)  # Wait for the next clock edge

    
    # Enable the module
    dut.enable.value = 1
    await FallingEdge(dut.clk)  # Wait for a clock edge

    # Test all valid BCD inputs
    for bcd in range(10):  # Valid BCD values are 0 to 9
        dut.bcd.value = bcd
        await FallingEdge(dut.clk)  # Wait for the next clock edge
        print(f"Performing bcd to excess_3 operation: bcd = {dut.bcd.value}, excess3 = {dut.excess3.value}")

    # Test invalid BCD inputs
    invalid_bcd_values = [10, 15]  # Invalid BCD values
    for bcd in invalid_bcd_values:
        dut.bcd.value = bcd
        await FallingEdge(dut.clk)  # Wait for the next clock edge
        print(f"Performing bcd to excess_3 invalid operation: bcd = {dut.bcd.value}, excess3 = {dut.excess3.value}")
        

    # Assert reset while enabled
    dut.rst.value = 1
    await RisingEdge(dut.clk)  # Wait for the next clock edge
    dut.rst.value = 0
    await RisingEdge(dut.clk)  # Wait for the next clock edge
    

    # Re-test a valid BCD input after reset
    dut.bcd.value = 1
    await FallingEdge(dut.clk)
    

    # Finish simulation
    cocotb.log.info("Test completed successfully.")'''
