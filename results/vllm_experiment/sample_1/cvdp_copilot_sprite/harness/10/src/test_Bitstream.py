import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, Timer
import harness_library as hrs_lb
import random

@cocotb.test()
async def test_bitstream(dut):
    
   debug = 0

   cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())
   
   model = hrs_lb.Bitstream()

   # Initialize DUT
   await hrs_lb.dut_init(dut)   
   # Reset the design
   await hrs_lb.reset_dut(dut.rst_n)
   model.reset()

   # Cycles to make design stable before insert stimulus
   await RisingEdge(dut.clk)

   for i in range(20):
      enb       = random.randint(0,1)
      rempty_in = random.randint(0,1)
      rinc_in   = random.randint(0,1)
      i_byte    = random.randint(0,255)
      dut.enb.value       = enb
      dut.rempty_in.value = rempty_in
      dut.rinc_in.value   = rinc_in
      dut.i_byte.value    = i_byte

      model.update_fsm(enb, rempty_in, rinc_in, i_byte)
      
      await RisingEdge(dut.clk)
      cocotb.log.info(f"[INPUT] enb: {enb}, rempty_inc: {rempty_in}, rinc_in: {rinc_in}, i_byte: {bin(i_byte)}")
      cocotb.log.info(f"[DUT]   state = {dut.curr_state.value.to_unsigned()}")
      cocotb.log.info(f"[MODEL] state = {model.curr_state}")

      model_o_bit      = model.o_bit
      model_rinc_out   = model.rinc_out
      model_rempty_out = model.rempty_out
      dut_o_bit      = dut.o_bit.value
      dut_rinc_out   = dut.rinc_out.value
      dut_rempty_out = dut.rempty_out.value

      cocotb.log.info(f"[OUT MODEL] o_bit: {model_o_bit}, rinc_out: {model_rinc_out}, rempty_out: {model_rempty_out}, rde: {model.rde}")
      cocotb.log.info(f"[OUT DUR]   o_bit: {dut_o_bit}, rinc_out: {dut_rinc_out}, rempty_out: {dut_rempty_out}, rde: {dut.rde.value}")

      assert dut_o_bit     == model_o_bit     ,f"Mismatch, expected:{model_o_bit     }, dut:{dut_o_bit     }"
      assert dut_rinc_out  == model_rinc_out  ,f"Mismatch, expected:{model_rinc_out  }, dut:{dut_rinc_out  }"
      assert dut_rempty_out== model_rempty_out,f"Mismatch, expected:{model_rempty_out}, dut:{dut_rempty_out}"