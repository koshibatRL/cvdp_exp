import cocotb
from cocotb.triggers import Timer
import random

# Function to generate random data based on DATA_WIDTH
# Testbench function to test different scenarios
@cocotb.test()
async def test_nbit_sizling(dut):
    """ Test the nbit_sizling module """
    data_wd = int(dut.DATA_WIDTH.value)

    # Corner cases for data_in
    corner_cases = [
        0,  # All bits zero
        (2**data_wd - 1),  # All bits one
        int('10' * (data_wd // 2), 2),  # Alternating 1s and 0s
        int('01' * (data_wd // 2), 2),  # Alternating 0s and 1s
        2**(data_wd - 1),  # High-order bit set
        1  # Low-order bit set
    ]

    # Add single-bit set cases
    #corner_cases += [1 << i for i in range(data_wd)]

    # Test each corner case with a random sel value
    for data_in in corner_cases:
        sel = random.randint(0, 3)  # Randomize sel between 0 to 3

        # Apply inputs to the DUT
        dut.data_in.value = data_in
        dut.sel.value = sel

        await Timer(10, units='ns')

        # Run the actual result calculation in Python for comparison
        expected_data_out, expected_parity = reverse_data_with_parity(data_in, sel, data_wd)

        # Log detailed output
        print(f"DATA_WIDTH = {data_wd}")
        
        print(f"Checking operation for sel={sel}:: data_in = {int(dut.data_in.value)}, "
              f"expected_data_out = {format(expected_data_out, f'0{data_wd}d')}, "  # Format as binary string of width data_wd
              f"data_out = {format(int(dut.data_out.value) & ((1 << data_wd) - 1), f'0{data_wd}d')}, "  # Extract lower data_wd bits
              f"expected_parity = {expected_parity}, "
              f"parity_bit = {(int(dut.data_out.value) >> data_wd) & 1}")  # Extract parity bit

        # Compare the DUT's output with expected value
        assert dut.data_out.value[data_wd-1:0] == expected_data_out, \
            f"Test failed for sel={sel}, data_in={data_in}, expected_data_out={expected_data_out}, " \
            f"but got={dut.data_out.value[data_wd-1:0]}"

        assert dut.data_out.value[data_wd] == expected_parity, \
            f"Parity bit mismatch: expected={expected_parity}, but got={dut.data_out.value[data_wd]}"

    # Random testing for additional scenarios
    for i in range(20):
        # Generate random input data and selection signal
        data_in = random.randint(0, (2**data_wd) - 1)
        sel = random.randint(0, 3)  # Randomize sel between 0 to 3

        # Apply inputs to the DUT
        dut.data_in.value = data_in
        dut.sel.value = sel

        await Timer(10, units='ns')

        # Run the actual result calculation in Python for comparison
        expected_data_out, expected_parity = reverse_data_with_parity(data_in, sel, data_wd)

        # Log detailed output
        print(f"--------------------------------------------------------------------------------------------------")
        print(f"DATA_WIDTH = {data_wd}")
        print(f"Checking operation for sel={sel}:: data_in = {int(dut.data_in.value)}, "
              f"expected_data_out = {format(expected_data_out, f'0{data_wd}d')}, "  # Format as binary string of width data_wd
              f"data_out = {format(int(dut.data_out.value) & ((1 << data_wd) - 1), f'0{data_wd}d')}, "  # Extract lower data_wd bits
              f"expected_parity = {expected_parity}, "
              f"parity_bit = {(int(dut.data_out.value) >> data_wd) & 1}")  # Extract parity bit

        # Compare the DUT's output with expected value
        assert dut.data_out.value[data_wd-1:0] == expected_data_out, \
            f"Test failed for sel={sel}, data_in={data_in}, expected_data_out={expected_data_out}, " \
            f"but got={dut.data_out.value[data_wd-1:0]}"

        assert dut.data_out.value[data_wd] == expected_parity, \
            f"Parity bit mismatch: expected={expected_parity}, but got={dut.data_out.value[data_wd]}"

# Helper function to perform the data reversal and calculate the parity bit
def reverse_data_with_parity(data_in, sel, data_wd):
    # Convert input to binary string of size DATA_WIDTH
    data_in_bits = f'{data_in:0{data_wd}b}'
    
    # Calculate parity bit (XOR of all bits)
    parity_bit = data_in_bits.count('1') % 2  # XOR operation equivalent
    
    if sel == 0:
        # Reverse entire data
        reversed_data = int(data_in_bits[::-1], 2)
    elif sel == 1:
        # Reverse two halves
        half_width = data_wd // 2
        first_half = data_in_bits[:half_width][::-1]
        second_half = data_in_bits[half_width:][::-1]
        reversed_data = int(first_half + second_half, 2)
    elif sel == 2:
        # Reverse four sets
        quarter_width = data_wd // 4
        first_set = data_in_bits[:quarter_width][::-1]
        second_set = data_in_bits[quarter_width:2*quarter_width][::-1]
        third_set = data_in_bits[2*quarter_width:3*quarter_width][::-1]
        fourth_set = data_in_bits[3*quarter_width:][::-1]
        reversed_data = int(first_set + second_set + third_set + fourth_set, 2)
    elif sel == 3:
        # Reverse eight sets
        eighth_width = data_wd // 8
        sets = [data_in_bits[i*eighth_width:(i+1)*eighth_width][::-1] for i in range(8)]
        reversed_data = int(''.join(sets), 2)
    else:
        # Default, just return the input data as-is
        reversed_data = data_in

    return reversed_data, parity_bit
