import cocotb
# import uvm_pkg::*
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles, Timer
# from cocotb.results import TestFailure
import random
import time
import harness_library as hrs_lb
import math
       
@cocotb.test()
async def test_virtual2physical_tlb(dut):
    # Parameters
    ADDR_WIDTH = 8
    PAGE_WIDTH = 8
    TLB_SIZE = 4
    PAGE_TABLE_SIZE = 16

    # Initialize clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Initialize signals
    dut.reset.value = 1
    dut.virtual_address.value = 0
    await Timer(20, units="ns")
    dut.reset.value = 0
    await Timer(60, units="ns")
    # Initialize page table memory
    page_table_memory = [i for i in range(PAGE_TABLE_SIZE)]

    # Test 1: Random Test for Virtual Address Translation
    for _ in range(10):
        await FallingEdge(dut.clk)
        dut.virtual_address.value = random.randint(0,7)  # Random virtual address
        await RisingEdge(dut.clk)
        await Timer(1, units="ns")
        if dut.physical_address.value.to_unsigned() != page_table_memory[dut.virtual_address.value.to_unsigned()]:
            print(f"TEST 1 FAILED! Virtual Address: {dut.virtual_address.value.to_unsigned()}, "
                          f"Expected: {page_table_memory[dut.virtual_address.value.to_unsigned()]}, "
                          f"Got: {dut.physical_address.value.to_unsigned()}")
        else:
            print(f"TEST 1 PASSED! Virtual Address: {dut.virtual_address.value.to_unsigned()}, "
                         f"Physical Address: {dut.physical_address.value.to_unsigned()}")
            
        assert dut.physical_address.value.to_unsigned() == page_table_memory[dut.virtual_address.value.to_unsigned()], f"TEST 1 PASSED! Virtual Address: {dut.virtual_address.value.to_unsigned()},Physical Address: {dut.physical_address.value.to_unsigned()}"
        

    # Miss Test (0 to 15)
    j = 7
    for _ in range(8):
        await FallingEdge(dut.clk)
        j = j + 1
        dut.virtual_address.value = j  # Virtual address outside valid range
        await RisingEdge(dut.clk)
        if dut.miss.value.to_unsigned() != 1:
            print(f"MISS TEST FAILED! Virtual Address: {dut.virtual_address.value.to_unsigned()}, "
                          f"Miss: {dut.miss.value.to_unsigned()} (Expected: 1)")
        else:
            print(f"MISS TEST PASSED! Virtual Address: {dut.virtual_address.value.to_unsigned()} "
                         f"resulted in a Miss")

    # Hit Cache Test (Initialize TLB and check hits)
    tlb_values = [i for i in range(TLB_SIZE)]
    for i in range(TLB_SIZE):
        await FallingEdge(dut.clk)
        dut.virtual_address.value = i
        await RisingEdge(dut.clk)
    
    # Test if hits occur for the initialized TLB values
    for i in range(TLB_SIZE):
        await FallingEdge(dut.clk)
        dut.virtual_address.value = tlb_values[i]
        await RisingEdge(dut.clk)
        assert dut.hit.value.to_unsigned() == 1, f"HIT TEST FAILED! Virtual Address: {dut.virtual_address.value.to_unsigned()},{dut.hit.value.to_unsigned()} (Expected: 1)"
        if dut.hit.value.to_unsigned() != 1:
            print(f"HIT TEST FAILED! Virtual Address: {dut.virtual_address.value.to_unsigned()}, "
                          f"Hit: {dut.hit.value.to_unsigned()} (Expected: 1)")
        else:
            print(f"HIT TEST PASSED! Virtual Address: {dut.virtual_address.value} "
                         f"resulted in a Hit")

    # Finish simulation
    await Timer(100, units="ns")
    print("Simulation completed.")
