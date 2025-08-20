import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
import harness_library as hrs_lb
import random

def compare_values(dut, model, debug=0):
    dut_window  = dut.o_image_window.value.to_unsigned()

    model_window = model.get_o_window_flat()

    if debug == 1:
        print("\nINPUTS")
        print(f"i_mode = {dut.i_mode.value.to_unsigned()}")
        print(f"i_valid = {dut.i_valid.value.to_unsigned()}")
        print(f"i_update_window = {dut.i_update_window.value.to_unsigned()}")
        print(f"i_row_image = {hex(dut.i_row_image.value.to_unsigned())}")
        print(f"i_image_row_start = {dut.i_image_row_start.value.to_unsigned()}")
        print(f"i_image_col_start = {dut.i_image_col_start.value.to_unsigned()}")
        print("\nOUTPUTS")
        print(f"DUT o_window  = {hex(dut_window)} MODEL o_window  = {hex(model_window)}")
        #print(f"Observed o_image_window = {hex(dut_window)}")
        #print(f"Expected o_image_window = {hex(model_window)}\n")
    
    assert dut_window == model_window,  f"[ERROR] DUT o_window does not match model o_window: {hex(dut_window)} != {hex(model_window)}"

@cocotb.test()
async def test_line_buffer(dut):
    """Test the Line Buffer module with edge cases and random data."""

    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Retrieve parameters from the DUT
    NBW_DATA  = dut.NBW_DATA.value.to_unsigned()
    NS_ROW    = dut.NS_ROW.value.to_unsigned()
    NS_COLUMN = dut.NS_COLUMN.value.to_unsigned()
    NS_R_OUT  = dut.NS_R_OUT.value.to_unsigned()
    NS_C_OUT  = dut.NS_C_OUT.value.to_unsigned()
    CONSTANT  = dut.CONSTANT.value.to_unsigned()

    random.seed(1)

    model = hrs_lb.LineBuffer(nbw_data=NBW_DATA, ns_row=NS_ROW, ns_col=NS_COLUMN, ns_r_out=NS_R_OUT, ns_c_out=NS_C_OUT, pad_constant=CONSTANT)

    resets = 4
    runs = 250

    data_min = int(0)
    data_max = int(2**NBW_DATA - 1)

    window_row_min = int(0)
    window_row_max = int(NS_ROW-1)

    window_col_min = int(0)
    window_col_max = int(NS_COLUMN-1)

    await hrs_lb.dut_init(dut)

    for i in range(resets):
        # Reset DUT
        # Set all inputs to 0
        dut.i_mode.value = 0
        dut.i_valid.value = 0
        dut.i_update_window.value = 0
        dut.i_row_image.value = 0
        dut.i_image_row_start.value = 0
        dut.i_image_col_start.value = 0
        dut.rst_async_n.value = 0
        await RisingEdge(dut.clk)
        dut.rst_async_n.value = 1
        await RisingEdge(dut.clk)

        # Reset model
        model.reset()

        await RisingEdge(dut.clk)

        compare_values(dut, model)

        for j in range(runs):
            valid = random.randint(0,1)
            update_window = random.randint(0,1)
            image_row = 0
            for k in range(NS_COLUMN):
                data = random.randint(data_min, data_max)
                image_row = (image_row << NBW_DATA) | data
            window_row = random.randint(window_row_min, window_row_max)
            window_col = random.randint(window_col_min, window_col_max)
            mode = random.randint(0,5)

            dut.i_mode.value = mode
            dut.i_valid.value = valid
            dut.i_update_window.value = update_window
            dut.i_row_image.value = image_row
            dut.i_image_row_start.value = window_row
            dut.i_image_col_start.value = window_col


            await RisingEdge(dut.clk)
            if update_window:
                model.update_inputs(window_row, window_col, mode)
            if valid:
                model.add_line(image_row)
            compare_values(dut, model)
