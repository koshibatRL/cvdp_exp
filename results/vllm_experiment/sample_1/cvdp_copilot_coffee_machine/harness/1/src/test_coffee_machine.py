import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import harness_library as hrs_lb
import random

def compare_values(dut, model, debug=0):
    dut_bean_sel = dut.o_bean_sel.value.to_unsigned()
    dut_grind_beans = dut.o_grind_beans.value.to_unsigned()
    dut_use_powder = dut.o_use_powder.value.to_unsigned()
    dut_heat_water = dut.o_heat_water.value.to_unsigned()
    dut_pour_coffee = dut.o_pour_coffee.value.to_unsigned()
    dut_error = dut.o_error.value.to_unsigned()

    model_output = model.get_status()
    model_bean_sel    = int(model_output["o_bean_sel"])
    model_grind_beans = int(model_output["o_grind_beans"])
    model_use_powder  = int(model_output["o_use_powder"])
    model_heat_water  = int(model_output["o_heat_water"])
    model_pour_coffee = int(model_output["o_pour_coffee"])
    model_error       = int(model_output["o_error"])

    if debug == 1:
        print("\nINPUTS")
        print(f"DUT i_grind_delay   = {dut.i_grind_delay.value.to_unsigned()} MODEL i_grind_delay   = {model.i_grind_delay}")
        print(f"DUT i_heat_delay    = {dut.i_heat_delay.value.to_unsigned()} MODEL i_heat_delay    = {model.i_heat_delay}")
        print(f"DUT i_pour_delay    = {dut.i_pour_delay.value.to_unsigned()} MODEL i_pour_delay    = {model.i_pour_delay}")
        print(f"DUT i_bean_sel      = {dut.i_bean_sel.value.to_unsigned()} MODEL i_bean_sel      = {model.i_bean_sel}")
        print(f"DUT i_operation_sel = {dut.i_operation_sel.value.to_unsigned()} MODEL i_operation_sel = {model.operation}")
        print("\nOUTPUTS")
        print(f"DUT o_bean_sel    = {dut_bean_sel} MODEL o_bean_sel    = {model_bean_sel}")
        print(f"DUT o_grind_beans = {dut_grind_beans} MODEL o_grind_beans = {model_grind_beans}")
        print(f"DUT o_use_powder  = {dut_use_powder} MODEL o_use_powder  = {model_use_powder}")
        print(f"DUT o_heat_water  = {dut_heat_water} MODEL o_heat_water  = {model_heat_water}")
        print(f"DUT o_pour_coffee = {dut_pour_coffee} MODEL o_pour_coffee = {model_pour_coffee}")
        print(f"DUT o_error = {dut_error} MODEL o_error = {model_error}")
        print(f"DUT state = {dut.state_ff.value} MODEL state = {model.state}")

    assert dut_bean_sel    == model_bean_sel,    f"[ERROR] DUT o_bean_sel does not match model o_bean_sel: {dut_bean_sel} != {model_bean_sel}"
    assert dut_grind_beans == model_grind_beans, f"[ERROR] DUT o_grind_beans does not match model o_grind_beans: {dut_grind_beans} != {model_grind_beans}"
    assert dut_use_powder  == model_use_powder,  f"[ERROR] DUT o_use_powder does not match model o_use_powder: {dut_use_powder} != {model_use_powder}"
    assert dut_heat_water  == model_heat_water,  f"[ERROR] DUT o_heat_water does not match model o_heat_water: {dut_heat_water} != {model_heat_water}"
    assert dut_pour_coffee == model_pour_coffee, f"[ERROR] DUT o_pour_coffee does not match model o_pour_coffee: {dut_pour_coffee} != {model_pour_coffee}"
    assert dut_error       == model_error,       f"[ERROR] DUT o_error does not match model o_error: {dut_error} != {model_error}"



@cocotb.test()
async def test_coffee_machine(dut):
    """Test the Coffee Machine module with edge cases and random data."""

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    model = hrs_lb.CoffeeMachine()

    # Retrieve parameters from the DUT
    NBW_DLY   = dut.NBW_DLY.value.to_unsigned()
    NBW_BEANS = dut.NBW_BEANS.value.to_unsigned()
    NS_BEANS  = dut.NS_BEANS.value.to_unsigned()
    
    model.num_beans = NS_BEANS

    # Range for input values
    delay_min = 1
    delay_max = int(2**NBW_DLY - 1)

    beans_min = 1
    beans_max = int(2**NBW_BEANS - 1)

    resets = 20
    runs = 10

    await hrs_lb.dut_init(dut)

    for k in range(resets):
        # Reset the DUT
        
        # Set all inputs to zero
        dut.i_grind_delay.value   = 0
        dut.i_heat_delay.value    = 0
        dut.i_pour_delay.value    = 0
        dut.i_bean_sel.value      = 0
        dut.i_operation_sel.value = 0
        dut.i_start.value         = 0
        dut.i_sensor.value        = 0
        dut.rst_async_n.value     = 0
        await RisingEdge(dut.clk)

        model.reset()
        model.i_sensor = 0
        model.update_error()
        
        dut.rst_async_n.value = 1
        await RisingEdge(dut.clk)
        # Compare reset values
        compare_values(dut, model)

        await RisingEdge(dut.clk)
        
        ## Test errors

        # Generic error
        dut.i_sensor.value = 8
        model.i_sensor = 8
        model.update_error()

        await RisingEdge(dut.clk)
        compare_values(dut, model)

        # No water error
        dut.i_sensor.value = 1
        operation = random.randint(0,5)
        dut.i_operation_sel.value = operation
        model.i_sensor = 1
        model.operation = operation
        model.update_error()

        await RisingEdge(dut.clk)
        compare_values(dut, model)

        # No beans error
        dut.i_sensor.value = 2
        operation = random.randint(2,3)
        dut.i_operation_sel.value = operation
        model.i_sensor = 2
        model.operation = operation
        model.update_error()

        await RisingEdge(dut.clk)
        compare_values(dut, model)

        # No powder error (op = 1)
        dut.i_sensor.value = 4
        dut.i_operation_sel.value = 1
        model.i_sensor = 4
        model.operation = 1
        model.update_error()

        await RisingEdge(dut.clk)
        compare_values(dut, model)

        # No powder error (op = 4)
        dut.i_sensor.value = 4
        dut.i_operation_sel.value = 4
        model.i_sensor = 4
        model.operation = 4
        model.update_error()

        await RisingEdge(dut.clk)
        compare_values(dut, model)

        # Wrong operation error
        dut.i_sensor.value = 0
        operation = random.randint(6,7)
        dut.i_operation_sel.value = operation
        model.i_sensor = 0
        model.operation = operation
        model.update_error()

        await RisingEdge(dut.clk)
        compare_values(dut, model)

        for i in range(runs):
            # Generate random delay
            grind_delay = random.randint(delay_min, delay_max)
            heat_delay  = random.randint(delay_min, delay_max)
            pour_delay  = random.randint(delay_min, delay_max)
            bean_sel    = random.randint(beans_min, beans_max)
            operation   = random.randint(0,5)

            dut.i_sensor.value        = 0
            dut.i_grind_delay.value   = grind_delay
            dut.i_heat_delay.value    = heat_delay
            dut.i_pour_delay.value    = pour_delay
            dut.i_bean_sel.value      = bean_sel
            dut.i_operation_sel.value = operation
            dut.i_start.value         = 1

            model.i_sensor  = 0
            model.operation = operation
            model.update_error()

            await RisingEdge(dut.clk)
            dut.i_start.value         = 0
            compare_values(dut, model)
            await RisingEdge(dut.clk)
            compare_values(dut, model)
            while dut.o_pour_coffee.value == 0:
                await RisingEdge(dut.clk)
                model.update_state(operation=operation, i_sensor=0, i_grind_delay=grind_delay, i_heat_delay=heat_delay, i_pour_delay=pour_delay, i_bean_sel=bean_sel)
                compare_values(dut, model)
            
            while dut.o_pour_coffee.value == 1:
                await RisingEdge(dut.clk)
                model.update_state(operation=operation, i_sensor=0, i_grind_delay=grind_delay, i_heat_delay=heat_delay, i_pour_delay=pour_delay, i_bean_sel=bean_sel)
                compare_values(dut, model)

        # Create a test to validate that i_sensor[3] stops the opeartion
        # Generate random delay
        grind_delay = random.randint(delay_min, delay_max)
        heat_delay  = random.randint(delay_min, delay_max)
        pour_delay  = random.randint(delay_min, delay_max)
        bean_sel    = random.randint(beans_min, beans_max)
        operation   = random.randint(0,5)

        dut.i_sensor.value        = 0
        dut.i_grind_delay.value   = grind_delay
        dut.i_heat_delay.value    = heat_delay
        dut.i_pour_delay.value    = pour_delay
        dut.i_bean_sel.value      = bean_sel
        dut.i_operation_sel.value = operation
        dut.i_start.value         = 1

        model.i_sensor  = 0
        model.operation = operation
        model.update_error()

        await RisingEdge(dut.clk)
        dut.i_start.value = 0
        compare_values(dut, model)

        await RisingEdge(dut.clk)
        compare_values(dut, model)
        # Set sensor value to 8 -> Generic error
        dut.i_sensor.value = 8
        model.update_state(operation=operation, i_sensor=8, i_grind_delay=grind_delay, i_heat_delay=heat_delay, i_pour_delay=pour_delay, i_bean_sel=bean_sel)

        await RisingEdge(dut.clk)
        # o_error should be 1 here
        compare_values(dut, model)

        await RisingEdge(dut.clk)
        # DUT must be back in IDLE
        model.idle()
        compare_values(dut, model)
        