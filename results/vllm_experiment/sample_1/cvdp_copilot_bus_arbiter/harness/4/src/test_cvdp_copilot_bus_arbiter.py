import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

# Clock generation coroutine
@cocotb.coroutine
async def clock_gen(dut):
    """Generate clock signal."""
    while True:
        dut.clk.value = 0
        await Timer(5, units='ns')  # 100 MHz clock
        dut.clk.value = 1
        await Timer(5, units='ns')

# Helper function to apply reset
async def apply_reset(dut):
    """Apply a reset signal to the DUT."""
    dut.reset.value = 1
    await Timer(20, units="ns")
    dut.reset.value = 0
    await RisingEdge(dut.clk)

# Test Case 1: No requests, expect `grant1` and `grant2` to be 0
@cocotb.test()
async def test_no_requests(dut):
    """Test 1: No requests active - both grants should be 0"""
    cocotb.start_soon(clock_gen(dut))  # Start the clock
    await apply_reset(dut)
    dut.req1.value = 0
    dut.req2.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)    
    assert dut.grant1.value == 0, "grant1 should be 0 when no requests are active"
    assert dut.grant2.value == 0, "grant2 should be 0 when no requests are active"

# Test Case 2: Only req1 is asserted
@cocotb.test()
async def test_only_req1(dut):
    """Test 2: Only req1 asserted - grant1 should be 1, grant2 should be 0"""
    cocotb.start_soon(clock_gen(dut))  # Start the clock
    #await apply_reset(dut)
    dut.req1.value = 1
    dut.req2.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)    
    assert dut.grant1.value == 1, "grant1 should be 1 when only req1 is asserted"
    assert dut.grant2.value == 0, "grant2 should be 0 when only req1 is asserted"

# Test Case 3: Only req2 is asserted
@cocotb.test()
async def test_only_req2(dut):
    """Test 3: Only req2 asserted - grant2 should be 1, grant1 should be 0"""
    cocotb.start_soon(clock_gen(dut))  # Start the clock
    #await apply_reset(dut)
    dut.req1.value = 0
    dut.req2.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)    
    assert dut.grant1.value == 0, "grant1 should be 0 when only req2 is asserted"
    assert dut.grant2.value == 1, "grant2 should be 1 when only req2 is asserted"

# Test Case 4: Both req1 and req2 asserted, grant2 has priority
@cocotb.test()
async def test_both_requests(dut):
    """Test 4: Both req1 and req2 asserted - grant2 should have priority"""
    cocotb.start_soon(clock_gen(dut))  # Start the clock
    #await apply_reset(dut)
    dut.req1.value = 1
    dut.req2.value = 1
    dut.dynamic_priority.value = 0  # Priority to req2
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)    
    assert dut.grant1.value == 0, "grant1 should be 0 when both req1 and req2 are asserted"
    assert dut.grant2.value == 1, "grant2 should be 1 when both req1 and req2 are asserted"

# Test Case 5: Change priority to req1 while both requests are asserted
@cocotb.test()
async def test_dynamic_priority_change(dut):
    """Test 5: Change priority to req1 while both requests are asserted - grant1 should become 1"""
    cocotb.start_soon(clock_gen(dut))  # Start the clock
    #await apply_reset(dut)
    dut.req1.value = 1
    dut.req2.value = 1
    dut.dynamic_priority.value = 1  # Priority to req1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)    
    assert dut.grant1.value == 1, "grant1 should be 1 when priority is given to req1"
    assert dut.grant2.value == 0, "grant2 should be 0 when priority is given to req1"

# Test Case 6: Fast Priority Toggle
@cocotb.test()
async def test_fast_priority_toggle(dut):
    """Test 6: Fast Priority Toggle - ensure stable behavior"""
    cocotb.start_soon(clock_gen(dut))  # Start the clock
    #await apply_reset(dut)
    dut.req1.value = 1
    dut.req2.value = 1
    dut.dynamic_priority.value = 0  # Start with priority to req2
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)    
    assert dut.grant2.value == 1, "grant2 should be active with initial priority to req2"

    dut.dynamic_priority.value = 1  # Change priority to req1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)    
    assert dut.grant1.value == 1, "grant1 should be active after changing priority to req1"

    dut.dynamic_priority.value = 0  # Change priority back to req2
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)    
    assert dut.grant2.value == 1, "grant2 should be active after changing priority back to req2"

# Test Case 7: Overlapping Requests with Priority Change
@cocotb.test()
async def test_overlapping_requests(dut):
    """Test 7: Overlapping Requests - req1 active, then req2 with priority to req2"""
    cocotb.start_soon(clock_gen(dut))  # Start the clock
    #await apply_reset(dut)
    dut.req1.value = 1
    dut.dynamic_priority.value = 1  # Priority to req1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)    
    assert dut.grant1.value == 1, "grant1 should be active with initial priority to req1"

    dut.req2.value = 1  # Assert req2
    dut.dynamic_priority.value = 0  # Change priority to req2
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)    
    assert dut.grant2.value == 1, "grant2 should take over with priority switched to req2"

# Test Case 8: Late Request Assertion
@cocotb.test()
async def test_late_request_assertion(dut):
    """Test 8: Late Request Assertion - req2 asserts late with priority to req2"""
    cocotb.start_soon(clock_gen(dut))  # Start the clock
    #await apply_reset(dut)
    dut.req1.value = 1
    dut.dynamic_priority.value = 1  # Priority to req1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.grant1.value == 1, "grant1 should be active with priority to req1"

    dut.req2.value = 1  # Assert req2 late
    dut.dynamic_priority.value = 0  # Change priority to req2
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)    
    assert dut.grant2.value == 1, "grant2 should take over after req2 asserts and priority changes to req2"

# Test Case 9: Deassertion During Transition
@cocotb.test()
async def test_deassertion_during_transition(dut):
    """Test 9: Deassertion During Transition - req1 deasserts while transitioning to grant2"""
    cocotb.start_soon(clock_gen(dut))  # Start the clock
    #await apply_reset(dut)
    dut.req1.value = 1
    dut.req2.value = 1
    dut.dynamic_priority.value = 1  # Priority to req1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)    
    assert dut.grant1.value == 1, "grant1 should be active with priority to req1"

    dut.req1.value = 0  # Deassert req1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)    
    assert dut.grant2.value == 1, "grant2 should take over after req1 deasserts"
