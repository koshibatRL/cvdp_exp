import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
import random
import os

def reference_multiplier(a, b):
    return a * b

async def initialize_dut(dut):
    dut.A.value = 0
    dut.B.value = 0
    dut.valid_in.value = 0
    dut._log.info("DUT inputs initialized to zero.") 

async def apply_async_reset(dut):
    dut.rst_n.value = 0
    await FallingEdge(dut.clk)
    await Timer(3, units="ns")  # Small delay
    assert dut.Product.value == 0, "Error: Product output is not zero after reset"
    assert dut.valid_out.value == 0, "Error: valid_out is not zero after reset"
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

async def multiplier(dut, A, B):
    # Apply inputs
    dut.A.value = A
    dut.B.value = B
    dut.valid_in.value = 1
    await RisingEdge(dut.clk)  # Wait for one clock cycle
    dut.valid_in.value = 0     # Deassert valid_in after one clock cycle

    return A, B  # Return inputs for reference multiplier checking

def check_product(dut, a, b):
    expected_product = reference_multiplier(a, b)
    actual_product = dut.Product.value.to_unsigned()
    assert actual_product == expected_product, f"Error: Expected {expected_product}, Got {actual_product}"
    dut._log.info(f"Check passed: A={a}, B={b}, Product={actual_product}")

async def measure_latency(dut):
    latency = 0
    while dut.valid_out.value == 0:
        await RisingEdge(dut.clk)
        latency += 1
    return latency
