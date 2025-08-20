import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles, Timer
import random
import harness_library as hrs_lb


@cocotb.test()
async def test_montgomery_mult(dut): 
   N = int (dut.N.value)
   clock_period_ns = 10  # For example, 10ns clock period
   cocotb.start_soon(Clock(dut.clk, clock_period_ns, units='ns').start())
   await hrs_lb.dut_init(dut)
   
   dut.rst_n.value = 0
   await Timer(5, units="ns")

   dut.rst_n.value = 1 

   outputs_list = []
   await RisingEdge(dut.clk)
   for i in range(50):
      a = random.randint(0, N-1)
      b = random.randint(0, N-1)
      golden_result = hrs_lb.mod_mult(a,b, N)
      await FallingEdge(dut.clk)
      dut.a.value = a
      dut.b.value = b
      dut.valid_in.value = 1 
      await FallingEdge(dut.clk)
      dut.valid_in.value = 0 
        
      latency = 0 
      while (dut.valid_out.value != 1):
         await RisingEdge(dut.clk)
         latency = latency + 1
       
      dut_result = int (dut.result.value)
      assert latency == 4, f"Valid output should have latency of 2 clk cycles"
      assert dut_result == golden_result , f"Output doesn't match golden output: dut_output {hex(dut_result)}, Expected output {hex(golden_result)}"
   
   for i in range(200):
      a = random.randint(0, N-1)
      b = random.randint(0, N-1)
      golden_result = hrs_lb.mod_mult(a,b, N)
      outputs_list.append(golden_result)
      await FallingEdge(dut.clk)
      dut.a.value = a
      dut.b.value = b
      dut.valid_in.value = 1
      if i>3:
          expected_result =  outputs_list.pop(0)
          dut_result = int (dut.result.value) 
          assert dut_result == expected_result, " Failure!"

  