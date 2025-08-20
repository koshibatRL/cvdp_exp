import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import random

# Function to calculate GCD in software for comparison
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def gcd_three(a, b, c):
    return gcd(gcd(a, b), c)
    
# Function to calculate LCM of three numbers
def lcm_three(a, b, c):
    return a*b*c // gcd_three(a*b, b*c, c*a)

# Coroutine to reset the DUT
async def reset_dut(dut):
    dut.rst.value = 1
    dut.go.value  = 0
    dut.A.value   = 0
    dut.B.value   = 0
    dut.C.value   = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.OUT.value == 0, f"Reset Test failed OUT Expected 0, got {int(dut.OUT.value)}"
    assert dut.done.value == 0, f"Reset Test failed done Expected 0, got {int(dut.done.value)}"
    dut.rst.value = 0
    await RisingEdge(dut.clk)
    assert dut.OUT.value == 0, f"Reset Test failed OUT Expected 0, got {int(dut.OUT.value)}"
    assert dut.done.value == 0, f"Reset Test failed done Expected 0, got {int(dut.done.value)}"

# Main LCM test coroutine
@cocotb.test()
async def lcm_test(dut):
    """ Test LCM calculation for different combinations of A, B, and C """
    
    # Start the clock with 10ns period
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    width     = int(dut.WIDTH.value)
    max_value = (1 << width) - 1
    # Reset the DUT
    await reset_dut(dut)
    
    # Define test cases for non-zero, positive numbers
    test_cases = [
        (1, 1, 1),  
        (4, 2, 2),  
        (6, 3, 3),  
        (15, 5, 10),
        (8, 4, 2),  
        (9, 6, 3),  
        (12, 8, 4), 
        (14, 7, 7), 
        (max_value, max_value, max_value), 
        (max_value-1, max_value-2, max_value), 
        (1, max_value, 1)  # (worst case for WIDTH)
    ]
    
    # Test all pre-defined test cases
    for A, B, C in test_cases:
        # Apply inputs
        dut.A.value  = A
        dut.B.value  = B
        dut.C.value  = C
        dut.go.value = 1
        latency      = 0
        
        # Wait for the `done` signal
        await RisingEdge(dut.clk)
        # Release go signal
        dut.go.value = 0
        await RisingEdge(dut.clk)
        latency += 1
        while (dut.done.value == 0):
            await RisingEdge(dut.clk)
            latency += 1
        
        # Compare the result with expected LCM
        expected_lcm = lcm_three(A, B, C)
        assert dut.OUT.value == expected_lcm, f"Test failed with A={A}, B={B}, C={C}. Expected {expected_lcm}, got {int(dut.OUT.value)}"
        
        if ((A==1) and (B==2**width-1) and (C==1) ):
            assert latency == (2**(width+1))+1+2+2,f"The design latency to calculate the LCM is incorrect. A={A}, B={B}, C={C}. Expected Latency: {(2**(width+1))+1+2+2}, Actual Latency: {latency}"
        elif((A==B==C)):
            assert latency == 2+2+1+2,f"The design latency to calculate the LCM is incorrect. A={A}, B={B}, C={C}. Expected Latency: {2+2+1+2}, Actual Latency: {latency}"

        await RisingEdge(dut.clk)
        assert dut.done.value == 0, f"Done should be high for only 1 clk cycle, expected 0, got {int(dut.done.value)}"
        latency = 0
    # Reset the DUT
    await reset_dut(dut)
        
# Additional stress test with random values for A, B, and C
@cocotb.test()
async def lcm_stress_test(dut):
    """ Stress test LCM calculation with random non-zero, positive values """
    
    # Start the clock with 10ns period
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    latency = 0
    
    # Reset the DUT
    await reset_dut(dut)
    
    width = int(dut.WIDTH.value)
    
    # Run random test cases
    for _ in range(100):
        A = random.randint(1, (1 << width) - 1)  # A is positive number
        B = random.randint(1, (1 << width) - 1)  # B is positive number
        C = random.randint(1, (1 << width) - 1)  # C is positive number
        latency = 0

        # Apply inputs
        dut.A.value  = A
        dut.B.value  = B
        dut.C.value  = C
        dut.go.value = 1
        
        # Wait for the `done` signal
        await RisingEdge(dut.clk)
        # Release go signal
        dut.go.value = 0
        while (dut.done.value == 0):
            await RisingEdge(dut.clk)
            latency += 1
        
        # Compare the result with expected LCM
        expected_lcm = lcm_three(A, B, C)
        assert dut.OUT.value == expected_lcm, f"Test failed with A={A}, B={B}, C={C}. Expected {expected_lcm}, got {int(dut.OUT.value)}"
        if ((A==1) and (B==2**width-1) and (C==1) ):
            assert latency == (2**(width+1))+1+2+2,f"The design latency to calculate the LCM is incorrect. A={A}, B={B}, C={C}. Expected Latency: {(2**(width+1))+1+2+2}, Actual Latency: {latency}"
        elif((A==B==C)):
            assert latency == 2+2+1+2,f"The design latency to calculate the LCM is incorrect. A={A}, B={B}, C={C}. Expected Latency: {2+2+1+2}, Actual Latency: {latency}"

        await RisingEdge(dut.clk)
        assert dut.done.value == 0, f"Done should be high for only 1 clk cycle, expected 0, got {int(dut.done.value)}"
        latency = 0
    
    # Reset the DUT
    await reset_dut(dut)
