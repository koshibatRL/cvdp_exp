import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def test_halfband_fir(dut):
    """Cocotb testbench for shalfband Module"""

    # Clock generation
    cocotb.start_soon(Clock(dut.i_clk, 10, units="ns").start())  # 10ns period

    # Reset DUT
    dut.i_reset.value = 1
    dut.i_tap_wr.value = 0
    dut.i_tap.value = 0
    dut.i_ce.value = 0
    dut.i_sample.value = 0
    await Timer(20, units="ns")
    dut.i_reset.value = 0
    await Timer(10, units="ns")
    
    cocotb.log.info("===== STARTING TESTBENCH =====")

    # TC1: Reset Behavior
    cocotb.log.info("TC1: Reset Behavior")
    assert dut.o_result.value == 0 and dut.o_ce.value == 0, f"TC1 FAILED! Expected o_result=0, o_ce=0, Got o_result={dut.o_result.value}, o_ce={dut.o_ce.value}"
    cocotb.log.info("TC1 PASSED\n")
    
    # TC2: No Operation
    cocotb.log.info("TC2: No Operation")
    await Timer(10, units="ns")
    assert dut.o_result.value == 0, f"TC2 FAILED! Expected o_result=0, Got {dut.o_result.value}"
    cocotb.log.info("TC2 PASSED\n")
    
    # TC3: Coefficient Write 1
    cocotb.log.info("TC3: Coefficient Write 1")
    dut.i_tap_wr.value = 1
    dut.i_tap.value = 0x00A
    await Timer(10, units="ns")
    dut.i_tap_wr.value = 0
    assert dut.i_tap.value == 0x00A, f"TC3 FAILED! Expected i_tap=00A, Got {dut.i_tap.value}"
    cocotb.log.info("TC3 PASSED\n")
    
    # TC4: Coefficient Write 2
    cocotb.log.info("TC4: Coefficient Write 2")
    dut.i_tap_wr.value = 1
    dut.i_tap.value = 0x00B
    await Timer(10, units="ns")
    dut.i_tap_wr.value = 0
    assert dut.i_tap.value == 0x00B, f"TC4 FAILED! Expected i_tap=00B, Got {dut.i_tap.value}"
    cocotb.log.info("TC4 PASSED\n")
    
    # TC5: Sample Input 1
    cocotb.log.info("TC5: Sample Input 1")
    dut.i_ce.value = 1
    dut.i_sample.value = 0x1234
    await Timer(10, units="ns")
    assert dut.i_sample.value == 0x1234, f"TC5 FAILED! Expected i_sample=1234, Got {dut.i_sample.value}"
    cocotb.log.info("TC5 PASSED\n")
    
    # TC6: Sample Input 2
    cocotb.log.info("TC6: Sample Input 2")
    dut.i_sample.value = 0x5678
    await Timer(10, units="ns")
    assert dut.i_sample.value == 0x5678, f"TC6 FAILED! Expected i_sample=5678, Got {dut.i_sample.value}"
    cocotb.log.info("TC6 PASSED\n")
    
    # TC7: Sample Input 3
    cocotb.log.info("TC7: Sample Input 3")
    dut.i_sample.value = 0x9ABC
    await Timer(10, units="ns")
    assert dut.i_sample.value == 0x9ABC, f"TC7 FAILED! Expected i_sample=9ABC, Got {dut.i_sample.value}"
    cocotb.log.info("TC7 PASSED\n")
    
    # TC8: Sample Input 4 with Tap Change
    cocotb.log.info("TC8: Sample Input 4 with Tap Change")
    dut.i_tap_wr.value = 1
    dut.i_tap.value = 0x00C
    dut.i_sample.value = 0xDEF0
    await Timer(10, units="ns")
    dut.i_tap_wr.value = 0
    assert dut.i_tap.value == 0x00C, f"TC8 FAILED! Expected i_tap=00C, Got {dut.i_tap.value}"
    cocotb.log.info("TC8 PASSED\n")
    
    # TC9: Sample Processing Continues
    cocotb.log.info("TC9: Sample Processing Continues")
    dut.i_sample.value = 0x1357
    await Timer(10, units="ns")
    assert dut.i_sample.value == 0x1357, f"TC9 FAILED! Expected i_sample=1357, Got {dut.i_sample.value}"
    cocotb.log.info("TC9 PASSED\n")
    
    # TC10: Sample Processing with Different Tap
    cocotb.log.info("TC10: Sample Processing with Different Tap")
    dut.i_tap_wr.value = 1
    dut.i_tap.value = 0x00D
    dut.i_sample.value = 0x2468
    await Timer(10, units="ns")
    dut.i_tap_wr.value = 0
    assert dut.i_tap.value == 0x00D, f"TC10 FAILED! Expected i_tap=00D, Got {dut.i_tap.value}"
    cocotb.log.info("TC10 PASSED\n")
    # TC11: Output result check
    cocotb.log.info("TC11: Output result check")
    await Timer(5, units="ns")
    assert dut.i_tap.value == 0x00D and dut.o_result.value == 0x002b36988, f"TC11 FAILED! Expected o_result=0x002b36988, Got {dut.o_result.value}"
    cocotb.log.info("TC11 PASSED\n")
    # TC12: Output result check
    cocotb.log.info("TC12: Output result check")
    await Timer(10, units="ns")
    assert dut.i_tap.value == 0x00D and dut.o_result.value == 0x7fcd64544, f"TC12 FAILED! Expected o_result=0x7fcd64544, Got {dut.o_result.value}"
    cocotb.log.info("TC12 PASSED\n")

    # TC13: Output result check
    cocotb.log.info("TC13: Output result check")
    await Timer(25, units="ns")
    assert dut.i_tap.value == 0x00D and dut.o_result.value == 0x0009aa4a9, f"TC13 FAILED! Expected o_result=0x0009aa4a9, Got {dut.o_result.value}"
    cocotb.log.info("TC13 PASSED\n")

    # TC14: Output result check
    cocotb.log.info("TC14: Output result check")
    await Timer(60, units="ns")
    assert dut.i_tap.value == 0x00D and dut.o_result.value == 0x001231b98, f"TC14 FAILED! Expected o_result=0x001231b98, Got {dut.o_result.value}"
    cocotb.log.info("TC14 PASSED\n")
    
    cocotb.log.info("===== ALL TESTS COMPLETED SUCCESSFULLY! =====")
