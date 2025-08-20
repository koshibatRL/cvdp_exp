# test_caesar_cipher_numeric_key.py
import cocotb
from cocotb.triggers import Timer
import random
import string

def caesar_cipher_sw(input_phrase, numeric_key, decrypt=False):
    """
    Calculate the Caesar Cipher result for a given input and numeric key.
    If decrypt=True, reverse the encryption.
    """
    result = []
    for i in range(len(input_phrase)):
        char = input_phrase[i]
        key = numeric_key[i]

        if decrypt:
            # Reverse the key for decryption
            key = -key

        if "A" <= char <= "Z":
            # Uppercase wrap-around
            shifted_val = (ord(char) - ord("A") + key) % 26
            result.append(chr(shifted_val + ord("A")))
        elif "a" <= char <= "z":
            # Lowercase wrap-around
            shifted_val = (ord(char) - ord("a") + key) % 26
            result.append(chr(shifted_val + ord("a")))
        else:
            # Shift non-alphabetic characters modulo 256
            shifted_char = chr((ord(char) + key) % 256)
            result.append(shifted_char)
    return ''.join(result)


@cocotb.test()
async def test_caesar_cipher_numeric_key(dut):
    """Test Caesar Cipher RTL module with numeric key (random tests)"""
    PHRASE_WIDTH = int(dut.PHRASE_WIDTH.value)
    PHRASE_LEN = PHRASE_WIDTH // 8

    # Initialize the DUT inputs
    dut.input_phrase.value = 0
    dut.key_phrase.value = 0
    dut.decrypt.value = 0  # Encryption mode

    await Timer(2, units="ns")

    # Run multiple random tests
    for _ in range(3):
        # Generate random phrase & keys
        input_phrase = ''.join(random.choices(string.ascii_letters + " ", k=PHRASE_LEN))
        numeric_key = [random.randint(0, 25) for _ in range(PHRASE_LEN)]

        # Convert to bit vectors
        input_phrase_bits = int.from_bytes(input_phrase.encode(), 'big')
        numeric_key_bits = 0
        for i, key_val in enumerate(numeric_key):
            shift_amount = 5 * (PHRASE_LEN - 1 - i)
            numeric_key_bits |= (key_val << shift_amount)

        # Drive DUT inputs
        dut.input_phrase.value = input_phrase_bits
        dut.key_phrase.value = numeric_key_bits

        await Timer(2, units="ns")  # Allow time for processing

        # DUT output
        dut_output = dut.output_phrase.value.to_unsigned().to_bytes(PHRASE_LEN, 'big').decode(errors="ignore")

        # Expected result (SW model)
        expected_output = caesar_cipher_sw(input_phrase, numeric_key)

        # Print results (with expected output)
        cocotb.log.info(
            f"Numeric Key Test:\n"
            f"  Input Phrase: {input_phrase}\n"
            f"  Key Phrase: {numeric_key}\n"
            f"  Expected: {expected_output}\n"
            f"  DUT Output: {dut_output}"
        )

        # Check
        assert dut_output == expected_output, (
            f"Test failed for input={input_phrase}, key={numeric_key}. "
            f"Expected: {expected_output}, Got: {dut_output}"
        )
        cocotb.log.info(f"Test passed for input={input_phrase}, key={numeric_key}.")


@cocotb.test()
async def test_caesar_cipher_special_characters(dut):
    """Test Caesar Cipher RTL module with special characters in the input"""
    PHRASE_WIDTH = int(dut.PHRASE_WIDTH.value)
    PHRASE_LEN = PHRASE_WIDTH // 8

    # Initialize the DUT inputs
    dut.input_phrase.value = 0
    dut.key_phrase.value = 0
    dut.decrypt.value = 0  # Encryption mode

    await Timer(2, units="ns")

    # Prepare special characters input (truncated to PHRASE_LEN if needed)
    input_phrase = "!@#$%^&*()"[:PHRASE_LEN]
    numeric_key = [random.randint(0, 25) for _ in range(PHRASE_LEN)]

    # Convert to bit vectors
    input_phrase_bits = int.from_bytes(input_phrase.encode(), 'big')
    numeric_key_bits = 0
    for i, key_val in enumerate(numeric_key):
        shift_amount = 5 * (PHRASE_LEN - 1 - i)
        numeric_key_bits |= (key_val << shift_amount)

    # Drive DUT inputs
    dut.input_phrase.value = input_phrase_bits
    dut.key_phrase.value = numeric_key_bits

    await Timer(2, units="ns")

    # DUT output
    dut_output = dut.output_phrase.value.to_unsigned().to_bytes(PHRASE_LEN, 'big').decode(errors="ignore")

    # Expected result
    expected_output = caesar_cipher_sw(input_phrase, numeric_key)

    cocotb.log.info(
        f"Special Characters Test:\n"
        f"  Input Phrase: {input_phrase}\n"
        f"  Key Phrase: {numeric_key}\n"
        f"  Expected Output: {expected_output}\n"
        f"  DUT Output: {dut_output}"
    )

    assert dut_output == expected_output, (
        f"Test failed for special characters input. "
        f"Got: {dut_output}, Expected: {expected_output}"
    )
    cocotb.log.info("Test passed for special characters input.")


@cocotb.test()
async def test_caesar_cipher_key_shorter_than_input(dut):
    """Test Caesar Cipher RTL module with a key shorter than the input phrase"""
    PHRASE_WIDTH = int(dut.PHRASE_WIDTH.value)
    PHRASE_LEN = PHRASE_WIDTH // 8

    # Initialize the DUT inputs
    dut.input_phrase.value = 0
    dut.key_phrase.value = 0
    dut.decrypt.value = 0  # Encryption mode

    await Timer(2, units="ns")

    # Input phrase (truncate if needed), and a shorter key
    input_phrase = "LongerInputPhrase"[:PHRASE_LEN]
    key = [3, 5, 7]  # Short key

    # Extend key cyclically
    extended_key = (key * ((PHRASE_LEN + len(key) - 1) // len(key)))[:PHRASE_LEN]

    # Convert to bit vectors
    input_phrase_bits = int.from_bytes(input_phrase.encode(), 'big')
    key_bits = 0
    for i, key_val in enumerate(extended_key):
        shift_amount = 5 * (PHRASE_LEN - 1 - i)
        key_bits |= (key_val << shift_amount)

    # Drive DUT
    dut.input_phrase.value = input_phrase_bits
    dut.key_phrase.value = key_bits

    await Timer(2, units="ns")

    # DUT output
    dut_output = dut.output_phrase.value.to_unsigned().to_bytes(PHRASE_LEN, 'big').decode(errors="ignore")

    # Expected
    expected_output = caesar_cipher_sw(input_phrase, extended_key)

    cocotb.log.info(
        f"Short-Key Test:\n"
        f"  Input Phrase: {input_phrase}\n"
        f"  Original Key: {key}\n"
        f"  Extended Key: {extended_key}\n"
        f"  Expected Output: {expected_output}\n"
        f"  DUT Output: {dut_output}"
    )

    assert dut_output == expected_output, (
        f"Test failed for key shorter than input phrase. "
        f"Got: {dut_output}, Expected: {expected_output}"
    )
    cocotb.log.info("Test passed for key shorter than input phrase.")


@cocotb.test()
async def test_caesar_cipher_encryption_decryption(dut):
    """Test Caesar Cipher RTL module: encryption followed by decryption"""
    PHRASE_WIDTH = int(dut.PHRASE_WIDTH.value)
    PHRASE_LEN = PHRASE_WIDTH // 8

    # Initialize the DUT inputs
    dut.input_phrase.value = 0
    dut.key_phrase.value = 0
    dut.decrypt.value = 0  # Start in encryption mode

    await Timer(2, units="ns")

    # Generate random input & keys
    input_phrase = ''.join(random.choices(string.ascii_letters + " ", k=PHRASE_LEN))
    numeric_key = [random.randint(0, 25) for _ in range(PHRASE_LEN)]

    # Convert to bit vectors
    input_phrase_bits = int.from_bytes(input_phrase.encode(), 'big')
    numeric_key_bits = 0
    for i, key_val in enumerate(numeric_key):
        shift_amount = 5 * (PHRASE_LEN - 1 - i)
        numeric_key_bits |= (key_val << shift_amount)

    # --------------------------
    # Encryption
    # --------------------------
    dut.input_phrase.value = input_phrase_bits
    dut.key_phrase.value = numeric_key_bits
    dut.decrypt.value = 0  # encryption mode

    await Timer(2, units="ns")

    # Collect encrypted output
    encrypted_output = dut.output_phrase.value.to_unsigned().to_bytes(PHRASE_LEN, 'big').decode(errors="ignore")
    expected_encrypted = caesar_cipher_sw(input_phrase, numeric_key, decrypt=False)

    cocotb.log.info(
        f"Encryption-Decryption Test (Encryption phase):\n"
        f"  Original Input: {input_phrase}\n"
        f"  Numeric Key: {numeric_key}\n"
        f"  Expected Encrypted: {expected_encrypted}\n"
        f"  DUT Encrypted: {encrypted_output}"
    )

    # --------------------------
    # Decryption
    # --------------------------
    dut.input_phrase.value = int.from_bytes(encrypted_output.encode(), 'big')
    dut.key_phrase.value = numeric_key_bits
    dut.decrypt.value = 1  # decryption mode

    await Timer(2, units="ns")

    # Collect decrypted output
    decrypted_output = dut.output_phrase.value.to_unsigned().to_bytes(PHRASE_LEN, 'big').decode(errors="ignore")
    # We expect the decrypted text to match the original input
    expected_decrypted = input_phrase

    cocotb.log.info(
        f"Encryption-Decryption Test (Decryption phase):\n"
        f"  Encrypted Input: {encrypted_output}\n"
        f"  Numeric Key: {numeric_key}\n"
        f"  Expected Decrypted: {expected_decrypted}\n"
        f"  DUT Decrypted: {decrypted_output}"
    )

    assert decrypted_output == input_phrase, (
        f"Decryption failed. Expected: {input_phrase}, Got: {decrypted_output}"
    )

    cocotb.log.info(
        f"Encryption-Decryption Test Passed.\n"
        f"  Original: {input_phrase}\n"
        f"  Encrypted: {encrypted_output}\n"
        f"  Decrypted: {decrypted_output}"
    )
