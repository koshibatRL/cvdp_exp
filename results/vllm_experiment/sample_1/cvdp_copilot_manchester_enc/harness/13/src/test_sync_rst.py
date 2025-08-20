import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random

# Initialize DUT
async def init_dut(dut):
    dut.rst_in.value = 1
    dut.enc_valid_in.value = 0
    dut.enc_data_in.value = 0
    await Timer(10, units='ns')

# Test case 1: With out Applying Synchronous reset
@cocotb.test()
async def test_no_reset(dut):
    
    N = 3  # Set the value of N (can be dynamically passed)
    cocotb.start_soon(Clock(dut.clk_in, 2, units='ns').start())
    
    print("N =", N)

    # Introduce a random delay before starting the test
    for i in range(random.randint(50, 100)):
        await RisingEdge(dut.clk_in)

    # Start loopback task
    async def loopback():
        while True:
            await RisingEdge(dut.clk_in)
            dut.dec_valid_in.value = dut.enc_valid_out.value
            dut.dec_data_in.value = dut.enc_data_out.value
    
    cocotb.start_soon(loopback())

    # Main testing loop for Manchester encoding/decoding
    for i in range(1 << N):
        await RisingEdge(dut.clk_in)
        dut.enc_valid_in.value = 1
        dut.enc_data_in.value = i
        await RisingEdge(dut.clk_in)
        dut.enc_valid_in.value = 0
        
        await RisingEdge(dut.dec_valid_out)
        await Timer(1, units='ns')

        # Fetch decoded data
        decoded_data = dut.dec_data_out.value
        # Check if the decoded data matches
        if decoded_data == i:
            dut._log.info(f"Decoded data match: expected {i}, got {int(decoded_data)}")
        else:
            assert decoded_data == i, f"Decoded data mismatch: expected {i}, got {int(decoded_data)}"

# Test Case 2: Reset Test for synchronous reset
@cocotb.test()
async def test_top_manchester(dut):
    await init_dut(dut)
    N = 2  # Set the value of N (can be dynamically passed)
    cocotb.start_soon(Clock(dut.clk_in, 2, units='ns').start())
    await RisingEdge(dut.clk_in)
    await RisingEdge(dut.clk_in)
    dut.rst_in.value = 0

    print("N =", N)

    # Start loopback task
    async def loopback():
        while True:
            await RisingEdge(dut.clk_in)
            dut.dec_valid_in.value = dut.enc_valid_out.value
            dut.dec_data_in.value = dut.enc_data_out.value
    
    cocotb.start_soon(loopback())

    # Main testing loop for Manchester encoding/decoding
    for i in range(1 << N):
        await RisingEdge(dut.clk_in)
        dut.enc_valid_in.value = 1
        dut.enc_data_in.value = i
        await RisingEdge(dut.clk_in)
        dut.enc_valid_in.value = 0
        
        await RisingEdge(dut.dec_valid_out)
        await Timer(1, units='ns')

        # Fetch decoded data
        decoded_data = dut.dec_data_out.value
        # Check if the decoded data matches
        if decoded_data == i:
            dut._log.info(f"Decoded data match: expected {i}, got {int(decoded_data)}")
        else:
            assert decoded_data == i, f"Decoded data mismatch: expected {i}, got {int(decoded_data)}"

# Test Case 3: Reset In middle of Test
@cocotb.test()
async def test_sync_reset(dut):
    await init_dut(dut)
    N = 3  # Set the value of N (can be dynamically passed)
    cocotb.start_soon(Clock(dut.clk_in, 2, units='ns').start())
    await RisingEdge(dut.clk_in)
    await RisingEdge(dut.clk_in)
    dut.rst_in.value = 0

    print("N =", N)

    # Start loopback task
    async def loopback():
        while True:
            await RisingEdge(dut.clk_in)
            dut.dec_valid_in.value = dut.enc_valid_out.value
            dut.dec_data_in.value = dut.enc_data_out.value
    
    cocotb.start_soon(loopback())

    # Introduce a random delay before Applying another reset
    for i in range(random.randint(50, 100)):
        await RisingEdge(dut.clk_in)

    await RisingEdge(dut.clk_in)
    dut.rst_in.value = 1
    await RisingEdge(dut.clk_in)
    await RisingEdge(dut.clk_in)

    for i in range(1 << N):
        await RisingEdge(dut.clk_in)
        dut.enc_valid_in.value = 1
        dut.enc_data_in.value = i
        await RisingEdge(dut.clk_in)
        dut.enc_valid_in.value = 0
        
        await RisingEdge(dut.clk_in)
        # Fetch decoded data
        decoded_data = dut.dec_data_out.value
        # Check if the decoded data matches
        if decoded_data == 0:
            dut._log.info(f"Decoded data match: expected {0}, got {int(decoded_data)}")
        else:
            assert decoded_data == 0, f"Decoded data mismatch: expected {0}, got {int(decoded_data)}"

