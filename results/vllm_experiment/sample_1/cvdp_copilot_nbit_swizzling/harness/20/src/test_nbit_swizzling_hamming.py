import cocotb
from cocotb.triggers import Timer
import random
import math

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
        expected_ecc_out = compute_ecc(data_in, data_wd)

                # Capture outputs
        ecc_out = int(dut.ecc_out.value)
        data_out = int(dut.data_out.value)

        # Corrupt a bit randomly in ECC
        corrupted_ecc = ecc_out
        error_bit = random.randint(0, data_wd + math.ceil(math.log2(data_wd)) - 1)
        corrupted_ecc ^= (1 << error_bit)  # Flip the error bit

        # Run ECC correction
        corrected_data, corrected_ecc, error_detected, error_position = correct_ecc(corrupted_ecc, data_wd)

        # Log detailed output
        print(f"--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        print(f"DATA_WIDTH = {data_wd}")
        print(f"Checking operation for sel={sel}:: data_in = {int(dut.data_in.value)},"
              f"expected_data_out = {format(expected_data_out, f'0{data_wd}d')}, "  # Format as binary string of width data_wd
              f"data_out = {format(int(dut.data_out.value) & ((1 << data_wd) - 1), f'0{data_wd}d')}, "  # Extract lower data_wd bits
              f"expected_parity = {expected_parity}, "
              f"parity_bit = {(int(dut.data_out.value) >> data_wd) & 1}")  # Extract parity bit
        print(f" ecc_out = {int(dut.ecc_out.value)}, expected_ecc_out = {(expected_ecc_out)}")
        print(f" ecc_out = {dut.ecc_out.value}, expected_ecc_out = {bin(expected_ecc_out)}")  # ecc encoding logic

                # Log results
        print("-----------------------------------------------------------")
        print(f"Input Data: {int(data_in)}")
        print(f"BIN:: ECC Out: {bin(ecc_out)}, ECC Out: {int(ecc_out)}")
        print(f"BIN:: Corrupted ECC: {bin(corrupted_ecc)}, Corrupted ECC: {int(corrupted_ecc)}")
        print(f"BIN:: Corrected ECC: {bin(corrected_ecc)}, Corrected ECC: {int(corrected_ecc)}")
        print(f"Corrected Data: {int(corrected_data)}")
        print(f"Error Detected: {error_detected}, Error Position from LSB: {error_position}")

        # Compare the DUT's output with expected value
        assert dut.data_out.value[data_wd-1:0] == expected_data_out, \
            f"Test failed for sel={sel}, data_in={data_in}, expected_data_out={expected_data_out}, " \
            f"but got={dut.data_out.value[data_wd-1:0]}"

        assert dut.data_out.value[data_wd] == expected_parity, \
            f"Parity bit mismatch: expected={expected_parity}, but got={dut.data_out.value[data_wd]}"
        
        assert dut.ecc_out.value == expected_ecc_out, \
            f"ECC mismatch: expected={expected_ecc_out}, but got={dut.ecc_out.value}"
        
        assert corrected_data == data_in, "Corrected data does not match the original input data!"
        if error_detected:
            assert error_position == error_bit , "Error position mismatch!"

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
        expected_ecc_out = compute_ecc(data_in, data_wd)

        ecc_out = int(dut.ecc_out.value)
        data_out = int(dut.data_out.value)

        # Corrupt a bit randomly in ECC
        corrupted_ecc = ecc_out
        error_bit = random.randint(0, data_wd + math.ceil(math.log2(data_wd)) - 1)
        corrupted_ecc ^= (1 << error_bit)  # Flip the error bit

        # Run ECC correction
        corrected_data, corrected_ecc, error_detected, error_position = correct_ecc(corrupted_ecc, data_wd)

        # Log detailed output
        print(f"--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        print(f"DATA_WIDTH = {data_wd}")
        print(f"Checking operation for sel={sel}:: data_in = {int(dut.data_in.value)}, "
              f"expected_data_out = {format(expected_data_out, f'0{data_wd}d')}, "  # Format as binary string of width data_wd
              f"data_out = {format(int(dut.data_out.value) & ((1 << data_wd) - 1), f'0{data_wd}d')}, "  # Extract lower data_wd bits
              f"expected_parity = {expected_parity}, "
              f"parity_bit = {(int(dut.data_out.value) >> data_wd) & 1}") # Extract parity bit
        print(f" ecc_out = {int(dut.ecc_out.value)}, expected_ecc_out = {(expected_ecc_out)}")
        print(f" ecc_out = {dut.ecc_out.value}, expected_ecc_out = {bin(expected_ecc_out)}")  # ecc encoding logic

        print("-----------------------------------------------------------")
        print(f"Input Data: {int(data_in)}")
        print(f"BIN:: ECC Out: {bin(ecc_out)}, ECC Out: {int(ecc_out)}")
        print(f"BIN:: Corrupted ECC: {bin(corrupted_ecc)}, Corrupted ECC: {int(corrupted_ecc)}")
        print(f"BIN:: Corrected ECC: {bin(corrected_ecc)}, Corrected ECC: {int(corrected_ecc)}")
        print(f"Corrected Data: {int(corrected_data)}")
        print(f"Error Detected: {error_detected}, Error Position  from LSB: {error_position}")



        # Compare the DUT's output with expected value
        assert dut.data_out.value[data_wd-1:0] == expected_data_out, \
            f"Test failed for sel={sel}, data_in={data_in}, expected_data_out={expected_data_out}, " \
            f"but got={dut.data_out.value[data_wd-1:0]}"

        assert dut.data_out.value[data_wd] == expected_parity, \
            f"Parity bit mismatch: expected={expected_parity}, but got={dut.data_out.value[data_wd]}"
        
        assert corrected_data == data_in, "Corrected data does not match the original input data!"
        assert corrected_ecc == ecc_out, "corrected_ecc does not match the ecc_out"
        if error_detected:
            assert error_position == error_bit, "Error position mismatch!"

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

def compute_ecc(data_in, data_wd):
    # Calculate number of parity bits
    parity_bits_count = math.ceil(math.log2(data_wd + math.ceil(math.log2(data_wd)) + 1))
    total_bits = data_wd + parity_bits_count

    # Prepare the code_temp array with placeholders
    code_temp = [0] * total_bits
    data_bits = list(f"{data_in:0{data_wd}b}"[::-1])  # Reverse the data for insertion

    # Insert data bits at non-power-of-2 positions
    data_idx = 0
    for i in range(1, total_bits + 1):
        if (i & (i - 1)) != 0:  # Not a power of 2
            code_temp[i - 1] = int(data_bits[data_idx])
            data_idx += 1

    # Compute parity bits for power-of-2 positions
    for p in range(parity_bits_count):
        parity_pos = 2**p
        parity_value = 0
        for j in range(1, total_bits + 1):
            if j & parity_pos:
                parity_value ^= code_temp[j - 1]
        code_temp[parity_pos - 1] = parity_value

    # Combine bits back into a single integer
    ecc_value = int("".join(map(str, code_temp[::-1])), 2)
    return ecc_value


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