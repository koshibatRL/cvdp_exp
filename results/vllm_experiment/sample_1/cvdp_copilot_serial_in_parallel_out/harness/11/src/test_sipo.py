import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge,FallingEdge, Timer
import harness_library as hrs_lb
import random
import math


@cocotb.test()
async def test_sipo(dut):
    # Randomly select data width and shift direction for this test iteration
    DATA_WIDTH = int(dut.DATA_WIDTH.value)
    SHIFT_DIRECTION = int(dut.SHIFT_DIRECTION.value)
    CODE_WIDTH = int(dut.CODE_WIDTH.value)
    

    # Start the clock with a 10ns time period
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Initialize the DUT signals with default 0
    await hrs_lb.dut_init(dut)

    # Reset the DUT rst_n signal
    await hrs_lb.reset_dut(dut.reset_n, duration_ns=25, active=False)

    dut.shift_en.value = 0                          # Disable shift initially
    dut.done.value = 0                              # Initialize the done signal to 0
    sin_list = []   
    sin_list_1 = []                  
    cocotb.log.info(f" SHIFT_DIRECTION = {SHIFT_DIRECTION}, data_wd = {DATA_WIDTH}")
    # Shift data_wd bits into the shift register
    print(f"---------------------------------------------------------------------------------------------------------------------------------------------------------")
    print(f"-----------------------------------------------NORMAL OPERATION ----------------------------------------------------------------------------------------")
    print(f"---------------------------------------------------------------------------------------------------------------------------------------------------------")
    for i in range(DATA_WIDTH):
        sin = random.randint(0, 1)                  # Generate a random bit to shift in (0 or 1)
        dut.shift_en.value = 1                      # Enable the shift and set the serial input bit
        dut.serial_in.value = sin          
        sin_list.append(sin)                        # Store the shifted bit for comparison later

        parallel_out = dut.uut_sipo.parallel_out.value       # Capture parallel output

        # Define the formatter to control the width of different log fields
    # For example: timestamp (15 characters), logger name (15 characters), log level (8 characters), message (50 characters)
        #cocotb.logging.Formatter('%(parallel_out)-15s')

        cocotb.log.info(f" Shifted sin = {sin}, parallel_out = {(parallel_out)} ")


        if i == DATA_WIDTH - 1:
            dut.done.value = 1                      # Indicate completion after last shift
            cocotb.log.info(f" done :{dut.done.value}")
        else:
            dut.done.value = 0                      # Done signal is low until the last shift
            cocotb.log.info(f" done :{dut.done.value}")

        await FallingEdge(dut.clk)                   # Wait for clock rising edge 
    #await RisingEdge(dut.clk)
    #cocotb.log.info(f" Shifted_sin = invalid, parallel_out = {(parallel_out)} ")
    

    if i == DATA_WIDTH - 1:
        dut.done.value = 1
        cocotb.log.info(f" done :{dut.done.value}")
    else:
        dut.done.value = 0
        cocotb.log.info(f" done :{dut.done.value}")
    # Wait for the final clock cycle to allow for the last shift
    await RisingEdge(dut.clk)

    # Capture the final parallel output
    parallel_out = dut.uut_sipo.parallel_out.value

    # expected behavior based on shift direction
    if SHIFT_DIRECTION == 1:
        # Shift left, capture parallel_out directly
        expected_output = int("".join(map(str, sin_list)), 2)
        cocotb.log.info(f"Shift left mode, Expected output: {expected_output}, Parallel output: {int(parallel_out)}")
    else:
        # Shift right, reverse the bit order of parallel_out
        original_parallel_out = format(int(parallel_out), f'0{DATA_WIDTH}b')  # Convert to binary string
        reversed_parallel_out = int(original_parallel_out[::1], 2)  # Reverse the bit order
        expected_output = int("".join(map(str, sin_list[::-1])), 2)
        cocotb.log.info(f" Shift right mode, Expected output: {expected_output}, Reversed parallel output: {reversed_parallel_out}")
    
    # Compare the parallel output with the expected output
    if SHIFT_DIRECTION == 1:
        assert int(parallel_out) == expected_output, f"Test failed: Expected {expected_output}, got {int(parallel_out)}"
    else:
        assert reversed_parallel_out == expected_output, f"Test failed: Expected {expected_output}, got {reversed_parallel_out}"


    # Final check for done signal - it should be high after the last shift
    assert dut.done.value == 1, "Test failed: 'done' signal was not high after the last bit shift."

    ecc_encoded = int(dut.encoded.value)
    dut.received.value = ecc_encoded
    await RisingEdge(dut.clk)
    cocotb.log.info(f" parallel_out = {int(parallel_out)}, ecc_encoded = {ecc_encoded}, received_ecc ={int(dut.received.value)}, data_out = {int(dut.data_out.value)} ")
    print(f"---------------------------------------------------------------------------------------------------------------------------------------------------------")
    print(f"--------------------------------------------------------INJECT SINGLE BIT ERROR -------------------------------------------------------------------------")
    print(f"---------------------------------------------------------------------------------------------------------------------------------------------------------")
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())
    # Initialize the DUT signals with default 0
    await hrs_lb.dut_init(dut)
    # Reset the DUT rst_n signal
    await hrs_lb.reset_dut(dut.reset_n, duration_ns=25, active=False)
    cocotb.log.info(f" SHIFT_DIRECTION = {SHIFT_DIRECTION}, data_wd = {DATA_WIDTH}")
    for i in range(DATA_WIDTH):
        sin = random.randint(0, 1)                  # Generate a random bit to shift in (0 or 1)
        dut.shift_en.value = 1                      # Enable the shift and set the serial input bit
        dut.serial_in.value = sin          
        sin_list_1.append(sin)                        # Store the shifted bit for comparison later

        parallel_out = dut.uut_sipo.parallel_out.value       # Capture parallel output

        # Define the formatter to control the width of different log fields
    # For example: timestamp (15 characters), logger name (15 characters), log level (8 characters), message (50 characters)
        #cocotb.logging.Formatter('%(parallel_out)-15s')

        cocotb.log.info(f" Shifted sin = {sin}, parallel_out = {(parallel_out)} ")


        if i == DATA_WIDTH - 1:
            dut.done.value = 1                      # Indicate completion after last shift
            cocotb.log.info(f" done :{dut.done.value}")
        else:
            dut.done.value = 0                      # Done signal is low until the last shift
            cocotb.log.info(f" done :{dut.done.value}")

        await FallingEdge(dut.clk)                   # Wait for clock rising edge 
        parallel_out = dut.uut_sipo.parallel_out.value

    if i == DATA_WIDTH - 1:
        dut.done.value = 1
        cocotb.log.info(f" done :{dut.done.value}")
    else:
        dut.done.value = 0
        cocotb.log.info(f" done :{dut.done.value}")
    # Wait for the final clock cycle to allow for the last shift
    await RisingEdge(dut.clk)

    # Capture the final parallel output
    

    # expected behavior based on shift direction
    if SHIFT_DIRECTION == 1:
        # Shift left, capture parallel_out directly
        expected_output = int("".join(map(str, sin_list_1)), 2)
        cocotb.log.info(f"Shift left mode, Expected output: {expected_output}, Parallel output: {int(parallel_out)}")
    else:
        # Shift right, reverse the bit order of parallel_out
        original_parallel_out = format(int(parallel_out), f'0{DATA_WIDTH}b')  # Convert to binary string
        reversed_parallel_out = int(original_parallel_out[::1], 2)  # Reverse the bit order
        expected_output = int("".join(map(str, sin_list_1[::-1])), 2)
        cocotb.log.info(f" Shift right mode, Expected output: {expected_output}, Reversed parallel output: {reversed_parallel_out}")
    
    # Compare the parallel output with the expected output

    if SHIFT_DIRECTION == 1:
        assert int(parallel_out) == expected_output, f"Test failed: Expected {expected_output}, got {int(parallel_out)}"
    else:
        assert reversed_parallel_out == expected_output, f"Test failed: Expected {expected_output}, got {reversed_parallel_out}"


    # Final check for done signal - it should be high after the last shift
    assert dut.done.value == 1, "Test failed: 'done' signal was not high after the last bit shift."

    ecc_encoded = int(dut.encoded.value)
    ecc_encoded_1= (dut.encoded.value)
    received_ecc = int(dut.encoded.value)
    error_bit = random.randint(0, DATA_WIDTH + math.ceil(math.log2(DATA_WIDTH)) - 1)
    received_ecc ^= (1 << error_bit)  # Flip the error bit
    dut.received.value = received_ecc
    corrected_data, corrected_ecc, error_detected, error_position = correct_ecc(received_ecc, DATA_WIDTH)
    await RisingEdge(dut.clk)
    cocotb.log.info(f" DUT::parallel_out = {int(parallel_out)}, ecc_encoded = {ecc_encoded_1}, received_ecc ={(dut.received.value)}, data_out = {int(dut.data_out.value)}, error_position from LSB = {error_bit}, error_corrected = {dut.error_corrected.value}, error_detected = {dut.error_detected.value} ")
    cocotb.log.info(f" EXPECTED:: corrected_data = {corrected_data}, corrected_ecc = {corrected_ecc}, error_detected = {int(error_detected)}, error_position from LSB = {error_position} ")
    assert ecc_encoded == corrected_ecc, f" TEST FAILE:: got_ecc_encoded = {ecc_encoded}, expected_corrected_ecc = {corrected_ecc} "
    assert error_detected == dut.error_detected.value, f" expected_error_detected = {error_detected},got_error_detected = {dut.error_detected.value}  "
    if error_detected:
        assert error_position == error_bit, f"expected_error_detected = {error_position}, got_error_detected = {error_bit}"
    print(f"---------------------------------------------------------------------------------------------------------------------------------------------------------")

def correct_ecc(ecc_in, data_wd):
    parity_bits_count = math.ceil(math.log2(data_wd + 1)) + 1
    total_bits = data_wd + parity_bits_count
    ecc_bits = [int(bit) for bit in f"{ecc_in:0{total_bits}b}"[::-1]]

    syndrome = 0
    for i in range(parity_bits_count):
        parity_pos = 2**i
        parity_value = 0
        for j in range(1, total_bits + 1):
            if j & parity_pos:
                parity_value ^= ecc_bits[j - 1]
        syndrome |= (parity_value << i)

    error_detected = syndrome != 0
    error_position = syndrome - 1 if syndrome > 0 else -1

    if error_detected and 0 <= error_position < len(ecc_bits):
        ecc_bits[error_position] ^= 1

    corrected_data_bits = [ecc_bits[i - 1] for i in range(1, total_bits + 1) if not (i & (i - 1)) == 0]
    corrected_data = int("".join(map(str, corrected_data_bits[::-1])), 2)
    corrected_ecc = int("".join(map(str, ecc_bits[::-1])), 2)

    return corrected_data, corrected_ecc, error_detected, error_position