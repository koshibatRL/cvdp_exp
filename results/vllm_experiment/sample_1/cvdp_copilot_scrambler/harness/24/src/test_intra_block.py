import cocotb
from cocotb.clock import Clock, Timer
from cocotb.triggers import RisingEdge
import random
import harness_library as hrs_lb

@cocotb.test()
async def test_inter_block(dut):   
    debug = 0

    # Initialize the DataProcessor model
    model = hrs_lb.IntraBlock()

    # Retrieve parameters from the DUT
    DATA_WIDTH = dut.DATA_WIDTH.value.to_unsigned()

    # Range for input values
    data_min = 0
    data_max = int(2**DATA_WIDTH - 1)
    # Generate random input data
    iter_number = 8
    in_data_vec = [data_min, data_max] + [random.randint(data_min, data_max) for i in range(iter_number)]

    await hrs_lb.dut_init(dut)

    for in_data in in_data_vec:
        dut.in_data.value = in_data
        model_out_data = model.rearrange_data(in_data)
        await Timer(10, units="ns")

        dut_out_data = dut.out_data.value.to_unsigned()

        if debug:
            cocotb.log.info(f"Input Data: {hex(in_data)}, DUT Output Data: {hex(dut_out_data)}, Model Output Data: {hex(model_out_data)}")

        #assert dut_out_data == model_out_data