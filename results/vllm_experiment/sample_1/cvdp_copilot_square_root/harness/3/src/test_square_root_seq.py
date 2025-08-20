import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random
import math

RANDOM_TESTCASE = 8;

async def expected_sqrt(value):
    #Calculate the integer square root.
    return int(math.isqrt(value))

@cocotb.test()
async def test_square_root_seq(dut):
    width = int(dut.WIDTH.value)
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Define golden latencies for each width and test case
    golden_latencies = {
        2:  {'MAX': 2, 'MIN': 1},
        4:  {'MAX': 4, 'MIN': 1},
        8:  {'MAX': 16, 'MIN': 1},
        16: {'MAX': 256, 'MIN': 1},
        32: {'MAX': 65536, 'MIN': 1}
    }

    dut.rst.value = 1  # Assert reset
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0  # Deassert reset

    test_cases = [
        {"num": (2**width) - 1, "description": "MAX number"},
        {"num": 0, "description": "MIN number"}
    ]

    for test_case in test_cases:
        await RisingEdge(dut.clk)
        num = test_case["num"]
        dut.num.value = num
        expected_root = await expected_sqrt(num)
        dut.start.value = 1
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        dut.start.value = 0

        # Initialize latency counter
        latency = 0
        # Wait for the operation to complete
        while dut.done.value == 0:
            await RisingEdge(dut.clk)
            latency += 1

        final_root = int(dut.final_root.value)
        assert final_root == expected_root, f"Test {test_case['description']} FAILED: Input = {num}, Calculated = {final_root}, Expected = {expected_root}"
        
        # Get the expected golden latency for the current test
        test_key = 'MAX' if num == (2**width) - 1 else 'MIN'
        expected_latency = golden_latencies[width][test_key]

        # Assert and log if latency mismatch
        if latency != expected_latency:
            dut._log.error(f"Test {test_case['description']} FAILED: Latency mismatch, expected {expected_latency+1}, got {latency+1}")
            assert False, f"Latency mismatch for test {test_case['description']} - expected {expected_latency+1}, got {latency+1}"
        else:
            dut._log.info(f"Test {test_case['description']} PASSED: Input = {num}, Calculated = {final_root}, Expected = {expected_root}, Latency = {latency+1} cycles")
            

@cocotb.test()
async def test_square_root_seq(dut):
    width = int(dut.WIDTH.value)
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Assert and deassert reset
    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0
    await RisingEdge(dut.clk)  # Wait for a clock edge post reset deassertion

    test_count = 0
    # Define test cases including edge cases
    test_values = [random.randint(0, (1 << width) - 1) for _ in range(RANDOM_TESTCASE-1)] + [(1 << width) - 1, 0]
    #print(bin(test_values))
    
    for num in test_values:
        dut.num.value = num
        expected_root = await expected_sqrt(num)

        # Initialize the test action
        dut.start.value = 1
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        dut.start.value = 0
        
        # Initialize latency counter
        latency = 0
        # Wait for the operation to complete
        while dut.done.value == 0:
            await RisingEdge(dut.clk)
            latency += 1
                
        # Read the result and verify
        final_root = int(dut.final_root.value)
        if final_root == expected_root:
            dut._log.info(f"Test {test_count} PASSED: Input = {num}, Calculated = {final_root}, Expected = {expected_root}")
        else:
            dut._log.error(f"Test {test_count} FAILED: Input = {num}, Calculated = {final_root}, Expected = {expected_root}")
            assert final_root == expected_root, f"Assertion failed for test {test_count}"
        
        test_count += 1 
         
