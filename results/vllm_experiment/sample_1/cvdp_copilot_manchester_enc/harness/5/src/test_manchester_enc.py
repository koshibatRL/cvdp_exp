import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import os
import json

# Initialize DUT
async def init_dut(dut):
    dut.rst_in.value = 1
    dut.enc_valid_in.value = 0
    dut.enc_data_in.value = 0
    await Timer(10, units='ns')

# Test: Manchester encoding and decoding
@cocotb.test()
async def test_top_manchester(dut):
    # Fetch test_sequence and expected_output from environment
    test_sequence = json.loads(os.getenv("TEST_SEQUENCE"))
    expected_output = json.loads(os.getenv("EXPECTED_OUTPUT"))

    N = int(dut.N.value)
    cocotb.start_soon(Clock(dut.clk_in, 2, units='ns').start())

    await init_dut(dut)
    dut.rst_in.value = 0

    # Apply test_sequence and validate encoded/decoded outputs
    for i, enc_data in enumerate(test_sequence):
        await RisingEdge(dut.clk_in)
        dut.enc_valid_in.value = 1
        dut.enc_data_in.value = enc_data
        await RisingEdge(dut.clk_in)
        dut.enc_valid_in.value = 0

        await RisingEdge(dut.enc_valid_out)
        await Timer(1, units='ns')
        
        decoded_data = dut.enc_data_out.value
        assert decoded_data == expected_output[i], f"Decoded data mismatch: expected {expected_output[i]}, got {decoded_data}"
