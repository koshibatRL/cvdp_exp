import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
import random

@cocotb.test()
async def test_parallel_run_length(dut):

    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Reset the DUT
    dut.reset_n.value = 0
    dut.data_in.value = 0
    await Timer(20, units='ns')
    dut.reset_n.value = 1

    # Test parameters
    data_width = int(dut.DATA_WIDTH.value)
    num_streams = int(dut.NUM_STREAMS.value)

    # Drive all ones
    await drive_all_ones(dut, num_streams, data_width)

    # Drive all zeros
    await drive_all_zeros(dut, num_streams, data_width)
    
    await RisingEdge(dut.clk)
    dut.reset_n.value = 0
    dut.data_in.value = 0
    dut._log.info(f"APPLY on the fly reset")
    if dut.reset_n.value == 0:
        assert dut.run_value.value == 0, f"[ERROR] run_value is not zero after reset: {dut.run_value.value}"
        assert dut.valid.value == 0, f"[ERROR] valid is not zero after reset: {dut.valid.value}"
        assert dut.data_out.value == 0, f"[ERROR] data_out is not zero after reset: {dut.data_out.value}"
    dut._log.info(f"After on the fly reset :: data_out = {dut.data_out.value}, valid = {dut.valid.value}, run_value = {dut.run_value.value}")
    
    await RisingEdge(dut.clk)
    # Drive random inputs
    await drive_and_validate(dut, num_streams, data_width, 6)
    await random_stream_enable(dut, num_streams, data_width, 6)

async def drive_all_ones(dut, num_streams, data_width):

    for i in range(data_width + 1):
        dut.stream_enable.value = (1 << num_streams) - 1 
        dut.data_in.value = (1 << num_streams) - 1  # Set all streams to 1
        await RisingEdge(dut.clk)

    # Wait for stable output
    await FallingEdge(dut.clk)

    # Extract and validate run_value for all streams
    run_value_int = int(dut.run_value.value)
    bits_per_stream = (data_width - 1).bit_length() + 1  # $clog2(DATA_WIDTH) + 1

    # Compute expected_run_value
    expected_run_value = 0
    for stream in range(num_streams):
        expected_run_value |= (data_width << (stream * bits_per_stream))

    assert run_value_int == expected_run_value, \
        f"[ERROR] run_value is not matched after continuous ones: {bin(run_value_int)}, expected: {bin(expected_run_value)}"

    # Extract and validate valid for all streams
    valid_int = int(dut.valid.value)
    expected_valid = (1 << num_streams) - 1  # All valid bits should be set
    assert valid_int == expected_valid, \
        f"[ERROR] valid is not matched after continuous ones: {bin(valid_int)}, expected: {bin(expected_valid)}"

    # Extract and validate data_out for all streams
    data_out_int = int(dut.data_out.value)
    expected_data_out = (1 << num_streams) - 1  # All data_out bits should be set
    assert data_out_int == expected_data_out, \
        f"[ERROR] data_out is not matched after continuous ones: {bin(data_out_int)}, expected: {bin(expected_data_out)}"

async def drive_all_zeros(dut, num_streams, data_width):

    for i in range(data_width + 1):
        dut.stream_enable.value = (1 << num_streams) - 1 
        dut.data_in.value = 0  # Set all streams to 0
        await RisingEdge(dut.clk)

    # Wait for stable output
    await FallingEdge(dut.clk)

    # Extract and validate run_value for all streams
    run_value_int = int(dut.run_value.value)
    bits_per_stream = (data_width - 1).bit_length() + 1  # $clog2(DATA_WIDTH) + 1

    # Compute expected_run_value
    expected_run_value = 0  # Run length is 0 for all streams
    for stream in range(num_streams):
        expected_run_value |= (data_width << (stream * bits_per_stream))
    assert run_value_int == expected_run_value, \
        f"[ERROR] run_value is not matched after continuous zeros: {bin(run_value_int)}, expected: {bin(expected_run_value)}"

    # Extract and validate valid for all streams
    valid_int = int(dut.valid.value)
    expected_valid = (1 << num_streams) - 1  # All valid bits should be set
    assert valid_int == expected_valid, \
        f"[ERROR] valid is not matched after continuous zeros: {bin(valid_int)}, expected: {bin(expected_valid)}"

    # Extract and validate data_out for all streams
    data_out_int = int(dut.data_out.value)
    expected_data_out = 0  # All data_out bits should be 0
    assert data_out_int == expected_data_out, \
        f"[ERROR] data_out is not matched after continuous zeros: {bin(data_out_int)}, expected: {bin(expected_data_out)}"

async def drive_and_validate(dut, num_streams, data_width, num_iterations):

    await FallingEdge(dut.clk)
    dut.reset_n.value = 1
    await FallingEdge(dut.clk)

    # Initialize expected run_length counters and previous data
    run_lengths = [0] * num_streams
    previous_data_in = 0
 
    for iteration in range(num_iterations):
        # Ensure every bit of data_in changes (using a while loop)
        while True:
            stream_enable = (1 << num_streams) - 1 
            data_in = ~previous_data_in & random.randint(0, (1 << num_streams) - 1)
            if data_in != previous_data_in:
                break

        # Apply new `data_in` value
        dut.data_in.value = data_in
        dut.stream_enable.value =  stream_enable
        await RisingEdge(dut.clk)

        # Expected calculations for outputs after applying the new data
        expected_valid = 0
        expected_data_out = 0

        for i in range(num_streams):
            current_bit = (data_in >> i) & 1
            previous_bit = (previous_data_in >> i) & 1

            # Update run_length logic
            if current_bit == previous_bit:
                if run_lengths[i] < data_width:
                    run_lengths[i] += 1
                else:
                    run_lengths[i] = 1  
            else:
                run_lengths[i] = 1  


            # Calculate expected `valid` and `data_out`
            if run_lengths[i] == data_width or current_bit != previous_bit:
                expected_valid |= (1 << i)
                expected_data_out |= (previous_bit << i)


        # Wait for falling edge to capture DUT outputs
        await FallingEdge(dut.clk)

        # Read DUT outputs
        dut_run_value = int(dut.run_value.value)
        dut_valid = int(dut.valid.value)
        dut_data_out = int(dut.data_out.value)

        # Log values
        dut._log.info(
            f"Iteration {iteration}: data_in={bin(data_in)}, prev_data_in={bin(previous_data_in)}, "
            f"stream_enable={bin(stream_enable)}, run_value={bin(dut_run_value)}, "
            f"valid={bin(dut_valid)}, expected_valid={bin(expected_valid)}, "
            f"data_out={bin(dut_data_out)}, expected_data_out={bin(expected_data_out)}"
        )

        # Assertions to validate outputs
        assert dut_valid == expected_valid, (
            f"Mismatch in valid: got {bin(dut_valid)}, expected {bin(expected_valid)}"
        )
        assert dut_data_out == expected_data_out, (
            f"Mismatch in data_out: got {bin(dut_data_out)}, expected {bin(expected_data_out)}"
        )

        # Update previous data for the next iteration
        previous_data_in = data_in

async def random_stream_enable(dut, num_streams, data_width, num_iterations):
    """
    Randomly toggle stream_enable and validate outputs based on RTL logic.
    """
    await RisingEdge(dut.clk)
    dut.reset_n.value = 0
    await FallingEdge(dut.clk)
    dut.reset_n.value = 1
    await FallingEdge(dut.clk)

    # Initialize previous data input and run-length counters
    previous_data_in = [0] * num_streams 
    run_lengths = [0] * num_streams

    for iteration in range(num_iterations):
        # Generate random inputs for stream_enable and data_in
        while True:
            random_stream_enable = random.randint(0, (1 << num_streams) - 1)
            random_data_in = random.randint(0, (1 << num_streams) - 1)
            if  random_data_in != previous_data_in:
                    break

        # Apply inputs to DUT
        dut.stream_enable.value = random_stream_enable
        dut.data_in.value = random_data_in
        await RisingEdge(dut.clk)

        # Initialize expected outputs
        expected_valid = 0
        expected_data_out = 0

        # Loop through each stream to calculate expected behavior
        for i in range(num_streams):
            if (random_stream_enable >> i) & 1:  # Stream is enabled
                current_bit = (random_data_in >> i) & 1
                prev_bit = previous_data_in[i]

                # Run-length update logic (matches RTL)
                if current_bit == prev_bit:
                    if run_lengths[i] < data_width:
                        run_lengths[i] += 1
                    else:
                        run_lengths[i] = 1  # Reset on reaching DATA_WIDTH
                else:
                    run_lengths[i] = 1  # Reset on input change

                # Valid and data_out update logic (matches RTL)
                if run_lengths[i] == data_width or current_bit != prev_bit:
                    expected_valid |= (1 << i)
                    expected_data_out |= (prev_bit << i)
                else:
                    expected_valid &= ~(1 << i)  # Explicit reset of valid[i]
                    expected_data_out &= ~(1 << i)

                # Update previous_data_in for the next iteration
                previous_data_in[i] = current_bit
            else:  # Stream is disabled
                run_lengths[i] = 0  # Reset run-length counter
                previous_data_in[i] = 0  # Reset prev_data_in
                expected_valid &= ~(1 << i)  # Reset valid[i]
                expected_data_out &= ~(1 << i)  # Reset data_out[i]

        await FallingEdge(dut.clk)

        # Read DUT outputs
        dut_valid = int(dut.valid.value)
        dut_data_out = int(dut.data_out.value)

        # Debugging information
        for i in range(num_streams):
            dut._log.info(f"Stream {i}: "
                          f"run_length={run_lengths[i]}, "
                          f"valid={(dut_valid >> i) & 1}, "
                          f"expected_valid={(expected_valid >> i) & 1}, "
                          f"data_out={(dut_data_out >> i) & 1}, "
                          f"expected_data_out={(expected_data_out >> i) & 1}")

        dut._log.info(f"Iteration {iteration}: stream_enable={bin(random_stream_enable)}, "
                      f"data_in={bin(random_data_in)}, previous_data_in={previous_data_in}, "
                      f"valid={bin(dut_valid)}, expected_valid={bin(expected_valid)}, "
                      f"data_out={bin(dut_data_out)}, expected_data_out={bin(expected_data_out)}")

        # Assertions for validation
        assert dut_valid == expected_valid, (
            f"[ERROR] valid mismatch: got {bin(dut_valid)}, expected {bin(expected_valid)}"
        )
        assert dut_data_out == expected_data_out, (
            f"[ERROR] data_out mismatch: got {bin(dut_data_out)}, expected {bin(expected_data_out)}"
        )

    await RisingEdge(dut.clk)