import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_lut_bug_fix(dut):
    """
    Test for LUT-related bugs in the morse_encoder module.
    Verifies the correct Morse code for 'A', 'E', and 'L'.
    """

    # Helper function to drive input and check expected output
    async def drive_and_check(ascii_in, expected_out, expected_length):
        dut.ascii_in.value = ascii_in
        await Timer(1, units="ns")  # Allow some delay for the outputs to stabilize
        assert dut.morse_out.value == expected_out, f"ascii_in={hex(ascii_in)}: Expected morse_out={bin(expected_out)}, got {bin(dut.morse_out.value)}"
        assert dut.morse_length.value == expected_length, f"ascii_in={hex(ascii_in)}: Expected morse_length={expected_length}, got {dut.morse_length.value}"

    # Test cases for previously buggy LUT entries
    # 'A' (8'h41)
    await drive_and_check(0x41, 0b01, 2)  # Correct Morse: .-

    # 'E' (8'h45)
    await drive_and_check(0x45, 0b0, 1)  # Correct Morse: .

    # 'L' (8'h4C)
    await drive_and_check(0x4C, 0b0100, 4)  # Correct Morse: .-..
