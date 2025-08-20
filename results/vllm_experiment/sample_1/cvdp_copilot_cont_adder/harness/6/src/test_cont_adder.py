import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

# Helper function to reset the DUT
async def reset_dut(dut):
    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.clk)

# Helper function to apply input data
async def apply_input(dut, data, data_valid):
    dut.data_in.value = data
    dut.data_valid.value = data_valid
    print(data)
    await RisingEdge(dut.clk)

@cocotb.test()
async def test_continuous_adder_1(dut):
    # Get the parameters from the DUT
    DATA_WIDTH = int(dut.DATA_WIDTH.value)
    THRESHOLD_VALUE = int(dut.THRESHOLD_VALUE.value)
    SIGNED_INPUTS = int(dut.SIGNED_INPUTS.value)

    # Create a clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Initialize the design
    dut.reset.value = 1
    dut.data_in.value = 0
    dut.data_valid.value = 0
    dut.sum_out.value = 0
    dut.sum_ready.value = 0
    await Timer(20, units="ns")
    await reset_dut(dut)

    total_sum = 0

    # Define test values based on SIGNED_INPUTS parameter
    if SIGNED_INPUTS == 1:
        # Test with both positive and negative values
        test_values = [THRESHOLD_VALUE // 2, -THRESHOLD_VALUE // 4, THRESHOLD_VALUE // 3]
    else:
        # Test with positive values only
        test_values = [THRESHOLD_VALUE // 2, THRESHOLD_VALUE // 4]

    await RisingEdge(dut.clk)
    
    for value in test_values:
        total_sum += value
        await apply_input(dut, value, 1)
        sum_ready = int(dut.sum_ready.value)
        if SIGNED_INPUTS == 1:
            if total_sum >= THRESHOLD_VALUE or total_sum <= -THRESHOLD_VALUE:
                assert sum_ready == 1, f"sum_ready should be asserted when sum reaches threshold, total_sum={total_sum}"
                sum_out = int(dut.sum_out.value.signed_integer)
                print("Sum = ", sum_out)
                assert sum_out == total_sum, f"sum_out is {sum_out}, but expected {total_sum}"
                sum_accum = int(dut.sum_accum.value.signed_integer)
                assert sum_accum == 0, f"Accumulator should be reset, but it is {sum_accum}"
                total_sum = 0
            else:
                assert sum_ready == 0, f"sum_ready should not be asserted yet, total_sum={total_sum}"
        else:
            if total_sum >= THRESHOLD_VALUE:
                assert sum_ready == 1, f"sum_ready should be asserted when sum reaches threshold, total_sum={total_sum}"
                sum_out = int(dut.sum_out.value)
                print("Sum = ",sum_out)
                assert sum_out == total_sum, f"sum_out is {sum_out}, but expected {total_sum}"
                sum_accum = int(dut.sum_accum.value)
                assert sum_accum == 0, f"Accumulator should be reset, but it is {sum_accum}"
                total_sum = 0
            else:
                assert sum_ready == 0, f"sum_ready should not be asserted yet, total_sum={total_sum}"

    # Apply an input that will cause the sum to reach the threshold
    if SIGNED_INPUTS == 1:
        if total_sum >= 0:
            final_input = THRESHOLD_VALUE - total_sum
        else:
            final_input = -THRESHOLD_VALUE - total_sum
    else:
        final_input = THRESHOLD_VALUE - total_sum
    total_sum += final_input
    await apply_input(dut, final_input, 1)
    await RisingEdge(dut.clk)
    sum_ready = int(dut.sum_ready.value)
    if SIGNED_INPUTS == 1:
        assert sum_ready == 1, f"sum_ready should be asserted when sum reaches threshold, total_sum={total_sum}"
        sum_out = int(dut.sum_out.value.signed_integer)
        print("Sum = ",sum_out)
        assert sum_out == total_sum, f"sum_out is {sum_out}, but expected {total_sum}"
        sum_accum = int(dut.sum_accum.value.signed_integer)
        assert sum_accum == 0, f"Accumulator should be reset, but it is {sum_accum}"
    else:
        assert sum_ready == 1, f"sum_ready should be asserted when sum reaches threshold, total_sum={total_sum}"
        sum_out = int(dut.sum_out.value)
        print("Sum = ",sum_out)
        assert sum_out == total_sum, f"sum_out is {sum_out}, but expected {total_sum}"
        sum_accum = int(dut.sum_accum.value)
        assert sum_accum == 0, f"Accumulator should be reset, but it is {sum_accum}"

    # Check that sum_ready is deasserted after one clock cycle
    await RisingEdge(dut.clk)
    assert dut.sum_ready.value == 0, "sum_ready should be deasserted after one clock cycle"


@cocotb.test()
async def test_continuous_adder_2(dut):
    # Get the parameters from the DUT
    DATA_WIDTH = int(dut.DATA_WIDTH.value)
    THRESHOLD_VALUE = int(dut.THRESHOLD_VALUE.value)
    SIGNED_INPUTS = int(dut.SIGNED_INPUTS.value)

    # Create a clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Initialize the design
    dut.reset.value = 1
    dut.data_in.value = 0
    dut.data_valid.value = 0
    dut.sum_out.value = 0
    dut.sum_ready.value = 0
    await Timer(20, units="ns")
    await reset_dut(dut)

    total_sum = 0

    # Define test values based on SIGNED_INPUTS parameter
    if SIGNED_INPUTS == 1:
        # Test with both positive and negative values
        test_values = [THRESHOLD_VALUE // 2, -THRESHOLD_VALUE // 4, 0]
    else:
        # Test with positive values only
        test_values = [THRESHOLD_VALUE // 2, 0, 0]

    await RisingEdge(dut.clk)
    
    for value in test_values:
        total_sum += value
        await apply_input(dut, value, 1)
        sum_ready = int(dut.sum_ready.value)
        if SIGNED_INPUTS == 1:
            if total_sum >= THRESHOLD_VALUE or total_sum <= -THRESHOLD_VALUE:
                assert sum_ready == 1, f"sum_ready should be asserted when sum reaches threshold, total_sum={total_sum}"
                sum_out = int(dut.sum_out.value.signed_integer)
                print("Sum = ",sum_out)
                assert sum_out == total_sum, f"sum_out is {sum_out}, but expected {total_sum}"
                sum_accum = int(dut.sum_accum.value.signed_integer)
                assert sum_accum == 0, f"Accumulator should be reset, but it is {sum_accum}"
                total_sum = 0
            else:
                assert sum_ready == 0, f"sum_ready should not be asserted yet, total_sum={total_sum}"
        else:
            if total_sum >= THRESHOLD_VALUE:
                assert sum_ready == 1, f"sum_ready should be asserted when sum reaches threshold, total_sum={total_sum}"
                sum_out = int(dut.sum_out.value)
                print("Sum = ",sum_out)
                assert sum_out == total_sum, f"sum_out is {sum_out}, but expected {total_sum}"
                sum_accum = int(dut.sum_accum.value)
                assert sum_accum == 0, f"Accumulator should be reset, but it is {sum_accum}"
                total_sum = 0
            else:
                assert sum_ready == 0, f"sum_ready should not be asserted yet, total_sum={total_sum}"

    # Apply an input that will cause the sum to reach the threshold
    if SIGNED_INPUTS == 1:
        if total_sum >= 0:
            final_input = THRESHOLD_VALUE - total_sum
        else:
            final_input = -THRESHOLD_VALUE - total_sum
    else:
        final_input = THRESHOLD_VALUE - total_sum
    total_sum += final_input
    await apply_input(dut, final_input, 1)
    await RisingEdge(dut.clk)
    sum_ready = int(dut.sum_ready.value)
    if SIGNED_INPUTS == 1:
        assert sum_ready == 1, f"sum_ready should be asserted when sum reaches threshold, total_sum={total_sum}"
        sum_out = int(dut.sum_out.value.signed_integer)
        print("Sum = ",sum_out)
        assert sum_out == total_sum, f"sum_out is {sum_out}, but expected {total_sum}"
        sum_accum = int(dut.sum_accum.value.signed_integer)
        assert sum_accum == 0, f"Accumulator should be reset, but it is {sum_accum}"
    else:
        assert sum_ready == 1, f"sum_ready should be asserted when sum reaches threshold, total_sum={total_sum}"
        sum_out = int(dut.sum_out.value)
        print("Sum = ",sum_out)
        assert sum_out == total_sum, f"sum_out is {sum_out}, but expected {total_sum}"
        sum_accum = int(dut.sum_accum.value)
        assert sum_accum == 0, f"Accumulator should be reset, but it is {sum_accum}"

    # Check that sum_ready is deasserted after one clock cycle
    await RisingEdge(dut.clk)
    assert dut.sum_ready.value == 0, "sum_ready should be deasserted after one clock cycle"
    

@cocotb.test()
async def test_continuous_adder_3(dut):
    # Get the parameters from the DUT
    DATA_WIDTH = int(dut.DATA_WIDTH.value)
    THRESHOLD_VALUE = int(dut.THRESHOLD_VALUE.value)
    SIGNED_INPUTS = int(dut.SIGNED_INPUTS.value)

    # Create a clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Initialize the design
    dut.reset.value = 1
    dut.data_in.value = 0
    dut.data_valid.value = 0
    dut.sum_out.value = 0
    dut.sum_ready.value = 0
    await Timer(20, units="ns")
    await reset_dut(dut)

    total_sum = 0

    # Define test values based on SIGNED_INPUTS parameter
    if SIGNED_INPUTS == 1:
        # Test with both positive and negative values
        test_values = [0, -THRESHOLD_VALUE // 4, 0]
    else:
        # Test with positive values only
        test_values = [0, 1, 0]

    await RisingEdge(dut.clk)
    
    for value in test_values:
        total_sum += value
        await apply_input(dut, value, 1)
        sum_ready = int(dut.sum_ready.value)
        if SIGNED_INPUTS == 1:
            if total_sum >= THRESHOLD_VALUE or total_sum <= -THRESHOLD_VALUE:
                assert sum_ready == 1, f"sum_ready should be asserted when sum reaches threshold, total_sum={total_sum}"
                sum_out = int(dut.sum_out.value.signed_integer)
                print("Sum = ",sum_out)
                assert sum_out == total_sum, f"sum_out is {sum_out}, but expected {total_sum}"
                sum_accum = int(dut.sum_accum.value.signed_integer)
                assert sum_accum == 0, f"Accumulator should be reset, but it is {sum_accum}"
                total_sum = 0
            else:
                assert sum_ready == 0, f"sum_ready should not be asserted yet, total_sum={total_sum}"
        else:
            if total_sum >= THRESHOLD_VALUE:
                assert sum_ready == 1, f"sum_ready should be asserted when sum reaches threshold, total_sum={total_sum}"
                sum_out = int(dut.sum_out.value)
                print("Sum = ",sum_out)
                assert sum_out == total_sum, f"sum_out is {sum_out}, but expected {total_sum}"
                sum_accum = int(dut.sum_accum.value)
                assert sum_accum == 0, f"Accumulator should be reset, but it is {sum_accum}"
                total_sum = 0
            else:
                assert sum_ready == 0, f"sum_ready should not be asserted yet, total_sum={total_sum}"

    # Apply an input that will cause the sum to reach the threshold
    if SIGNED_INPUTS == 1:
        if total_sum >= 0:
            final_input = THRESHOLD_VALUE - total_sum
        else:
            final_input = -THRESHOLD_VALUE - total_sum
    else:
        final_input = THRESHOLD_VALUE - total_sum
    total_sum += final_input
    await apply_input(dut, final_input, 1)
    await RisingEdge(dut.clk)
    sum_ready = int(dut.sum_ready.value)
    if SIGNED_INPUTS == 1:
        assert sum_ready == 1, f"sum_ready should be asserted when sum reaches threshold, total_sum={total_sum}"
        sum_out = int(dut.sum_out.value.signed_integer)
        print("Sum = ",sum_out)
        assert sum_out == total_sum, f"sum_out is {sum_out}, but expected {total_sum}"
        sum_accum = int(dut.sum_accum.value.signed_integer)
        assert sum_accum == 0, f"Accumulator should be reset, but it is {sum_accum}"
    else:
        assert sum_ready == 1, f"sum_ready should be asserted when sum reaches threshold, total_sum={total_sum}"
        sum_out = int(dut.sum_out.value)
        print("Sum = ",sum_out)
        assert sum_out == total_sum, f"sum_out is {sum_out}, but expected {total_sum}"
        sum_accum = int(dut.sum_accum.value)
        assert sum_accum == 0, f"Accumulator should be reset, but it is {sum_accum}"

    # Check that sum_ready is deasserted after one clock cycle
    await RisingEdge(dut.clk)
    assert dut.sum_ready.value == 0, "sum_ready should be deasserted after one clock cycle"