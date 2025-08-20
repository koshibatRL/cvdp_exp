import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
import harness_library as hrs_lb
import random

# Helper function to encode a string into RTL-specific encoding
def encode_string(input_string):
    encoded = []
    for char in input_string:
        if '0' <= char <= '9':
            encoded.append(ord(char) - ord('0'))  # Digits
        elif 'A' <= char <= 'Z':
            encoded.append(ord(char) - ord('A') + 10)  # Uppercase letters
        elif 'a' <= char <= 'z':
            encoded.append(ord(char) - ord('a') + 36)  # Lowercase letters
        elif '!' <= char <= '~':
            encoded.append(ord(char) - ord('!') + 62)  # Special characters
        else:
            encoded.append(0)  # Default for unsupported chars
    return encoded

async def reset_dut_with_checkers(dut):


    cocotb.log.info("Applying Reset...")
    await RisingEdge(dut.clk)
    dut.reset.value = 1
    encoded_input = encode_string("Aasdca1@")
    dut.start.value = 1
    await RisingEdge(dut.clk)

    # Check that outputs are reset
    assert dut.valid.value == 0, "Valid should be 0 after reset."
    assert dut.ready.value == 1, "Ready should be 1 after reset."
    for i in range(8):
        assert dut.ascii_out[i].value == 0, f"ascii_out[{i}] should be 0 after reset."
    cocotb.log.info("Reset completed and signal states verified.")

@cocotb.test()
# Cocotb test for the run_length module
async def test_String_to_ASCII_Converter(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Initialize the DUT signals with default 0
    await hrs_lb.dut_init(dut)

    await hrs_lb.reset_dut(dut.reset, duration_ns=5, active=True)
    await RisingEdge(dut.clk)

    for _ in range(10):  # Run 10 random test cases
        # Generate a random string of up to 8 characters
        random_string = ''.join(random.choice(
            '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')
            for _ in range(8))

        # Encode the string
        encoded_input = encode_string(random_string)

        # Apply inputs to DUT
        for i in range(8):
            if i < len(encoded_input):
                dut.char_in[i].value = encoded_input[i]
            else:
                dut.char_in[i].value = 0  # Default for unused indices

        # Start the conversion
        dut.start.value = 1
        await RisingEdge(dut.clk)
        dut.start.value = 0

        # Wait for the valid signal
        valid_seen = False
        while dut.valid.value != 1:
            await RisingEdge(dut.clk)
            if dut.valid.value == 1:
                valid_seen = True
                break
        assert valid_seen, "ERROR: DUT did not assert 'valid' signal."


         # Capture and display results
        ascii_out = []
        for i in range(8):
            ascii_out.append(int(dut.ascii_out[i].value))

        # Display ASCII values for  output
        dut_ascii = ascii_out[:len(random_string)]  # Only relevant outputs

        # Print the results
        cocotb.log.info(f"  Input String     : {random_string}")
        cocotb.log.info(f"  DUT ASCII Output : {dut_ascii}")

        # Validate results
        expected_output = [ord(c) for c in random_string]
        for i in range(len(random_string)):
            assert ascii_out[i] == expected_output[i], (
                f"Mismatch: char_in[{i}] = {random_string[i]} | Expected ASCII = {expected_output[i]} | "
                f"DUT Output = {ascii_out[i]}"
            )

        cocotb.log.info(f"Test passed for random input string: {random_string}")

        # Wait for the ready signal
        while dut.ready.value != 1:
            await RisingEdge(dut.clk)
        # Check if ready signal behaves correctly after valid
        ready_seen = False
        while not ready_seen:
            await RisingEdge(dut.clk)
            if dut.ready.value == 1:
                ready_seen = True

        assert ready_seen, "ERROR: DUT did not assert 'ready' signal after valid."

    cocotb.log.info("All random test cases passed.")

    await reset_dut_with_checkers(dut)
