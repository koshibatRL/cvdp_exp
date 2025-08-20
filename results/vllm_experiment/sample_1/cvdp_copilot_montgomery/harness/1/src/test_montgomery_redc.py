import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles, Timer
import random
import harness_library as hrs_lb


@cocotb.test()
async def test_montgomery_redc(dut): 
   N = int (dut.N.value)
   R = int (dut.R.value)
   R_INVERSE = int (dut.R_INVERSE.value)
   #TWO_NWIDTH = int (dut.TWO_NWIDTH.value)
   N_PRIME = (R * R_INVERSE - 1) // N
   await hrs_lb.dut_init(dut)


   for i in range(1000):
      T = random.randint(0, R*N-1)
      dut.T.value = T 
      exprected_result = hrs_lb.redc(T, N, R_INVERSE)
      await Timer(5, units="ns")
      dut_result = int (dut.result.value) 
      assert dut_result == exprected_result, " Failure!"
