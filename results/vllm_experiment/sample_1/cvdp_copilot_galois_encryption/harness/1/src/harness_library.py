import cocotb
from cocotb.triggers import FallingEdge, RisingEdge, Timer
import random

async def dut_init(dut):
    # iterate all the input signals and initialize with 0
    for signal in dut:
        if signal._type == "GPI_NET":
            signal.value = 0

# Reset the DUT (design under test)
async def reset_dut(reset_n, duration_ns=10):
    reset_n.value = 1
    await Timer(duration_ns, units="ns")
    reset_n.value = 0
    await Timer(duration_ns, units='ns')
    reset_n._log.debug("Reset complete")   

class GaloisEncryption:
    def __init__(self, key: int, data_bits=128, key_bits=32):
        self.data_bits = data_bits
        self.key_bits = key_bits
        self.key = key & ((1 << key_bits) - 1)  # Ensure key fits in given bits

    def xTIMES02(self, data: int) -> int:
        """Multiply by 02 in GF(2^8) using AES polynomial."""
        return ((data << 1) & 0xFF) ^ (0x1B if data & 0x80 else 0)

    def xTIMES03(self, data: int) -> int:
        """Multiply by 03 in GF(2^8) using AES polynomial."""
        return self.xTIMES02(data) ^ data

    def xTIMES09(self, data: int) -> int:
        """Multiply by 09 in GF(2^8) using AES polynomial."""
        return self.xTIMES02(self.xTIMES02(self.xTIMES02(data))) ^ data

    def xTIMES0B(self, data: int) -> int:
        """Multiply by 0B in GF(2^8) using AES polynomial."""
        return self.xTIMES02(self.xTIMES02(self.xTIMES02(data))) ^ self.xTIMES03(data)

    def xTIMES0D(self, data: int) -> int:
        """Multiply by 0D in GF(2^8) using AES polynomial."""
        return self.xTIMES02(self.xTIMES02(self.xTIMES02(data))) ^ self.xTIMES02(self.xTIMES02(data)) ^ data

    def xTIMES0E(self, data: int) -> int:
        """Multiply by 0E in GF(2^8) using AES polynomial."""
        return self.xTIMES02(self.xTIMES02(self.xTIMES02(data))) ^ self.xTIMES02(self.xTIMES02(data)) ^ self.xTIMES02(data)

    def encrypt(self, data: int) -> int:
        """Encrypt data using a simple Galois field transformation."""
        data = data & ((1 << self.data_bits) - 1)
        encrypted = 0

        # Convert data into 4x4 block matrix (list of lists)
        data_array = [
            [((data >> 120) & 0xFF), ((data >> 88) & 0xFF), ((data >> 56) & 0xFF), ((data >> 24) & 0xFF)],
            [((data >> 112) & 0xFF), ((data >> 80) & 0xFF), ((data >> 48) & 0xFF), ((data >> 16) & 0xFF)],
            [((data >> 104) & 0xFF), ((data >> 72) & 0xFF), ((data >> 40) & 0xFF), ((data >> 8) & 0xFF)],
            [((data >> 96) & 0xFF), ((data >> 64) & 0xFF), ((data >> 32) & 0xFF), ((data) & 0xFF)],
        ]

        enc_array = [row[:] for row in data_array]  # Copy

        for column in range(4):
            enc_array[0][column] = self.xTIMES02(data_array[0][column]) ^ self.xTIMES03(data_array[1][column]) ^ data_array[2][column] ^ data_array[3][column]
            enc_array[1][column] = self.xTIMES02(data_array[1][column]) ^ self.xTIMES03(data_array[2][column]) ^ data_array[3][column] ^ data_array[0][column]
            enc_array[2][column] = self.xTIMES02(data_array[2][column]) ^ self.xTIMES03(data_array[3][column]) ^ data_array[0][column] ^ data_array[1][column]
            enc_array[3][column] = self.xTIMES02(data_array[3][column]) ^ self.xTIMES03(data_array[0][column]) ^ data_array[1][column] ^ data_array[2][column]

            # XOR with key
            enc_array[0][column] ^= (self.key >> 24) & 0xFF
            enc_array[1][column] ^= (self.key >> 16) & 0xFF
            enc_array[2][column] ^= (self.key >> 8) & 0xFF
            enc_array[3][column] ^= (self.key) & 0xFF

        for line in range(4):
            for column in range(4):
                encrypted += enc_array[line][column] << (120 - 8 * line - 32 * column)

        return encrypted

    def decrypt(self, data: int) -> int:
        """Decrypt data using a simple Galois field transformation."""
        data = data & ((1 << self.data_bits) - 1)
        decrypted = 0

        # Convert data into 4x4 block matrix (list of lists)
        data_array = [
            [((data >> 120) & 0xFF), ((data >> 88) & 0xFF), ((data >> 56) & 0xFF), ((data >> 24) & 0xFF)],
            [((data >> 112) & 0xFF), ((data >> 80) & 0xFF), ((data >> 48) & 0xFF), ((data >> 16) & 0xFF)],
            [((data >> 104) & 0xFF), ((data >> 72) & 0xFF), ((data >> 40) & 0xFF), ((data >> 8) & 0xFF)],
            [((data >> 96) & 0xFF), ((data >> 64) & 0xFF), ((data >> 32) & 0xFF), ((data) & 0xFF)],
        ]

        dec_array = [row[:] for row in data_array]  # Copy

        for column in range(4):
            data_array[0][column] ^= (self.key >> 24) & 0xFF
            data_array[1][column] ^= (self.key >> 16) & 0xFF
            data_array[2][column] ^= (self.key >> 8) & 0xFF
            data_array[3][column] ^= (self.key) & 0xFF

            dec_array[0][column] = self.xTIMES0E(data_array[0][column]) ^ self.xTIMES0B(data_array[1][column]) ^ self.xTIMES0D(data_array[2][column]) ^ self.xTIMES09(data_array[3][column])
            dec_array[1][column] = self.xTIMES0E(data_array[1][column]) ^ self.xTIMES0B(data_array[2][column]) ^ self.xTIMES0D(data_array[3][column]) ^ self.xTIMES09(data_array[0][column])
            dec_array[2][column] = self.xTIMES0E(data_array[2][column]) ^ self.xTIMES0B(data_array[3][column]) ^ self.xTIMES0D(data_array[0][column]) ^ self.xTIMES09(data_array[1][column])
            dec_array[3][column] = self.xTIMES0E(data_array[3][column]) ^ self.xTIMES0B(data_array[0][column]) ^ self.xTIMES0D(data_array[1][column]) ^ self.xTIMES09(data_array[2][column])

        for line in range(4):
            for column in range(4):
                decrypted += dec_array[line][column] << (120 - 8 * line - 32 * column)

        return decrypted

    def update_key(self, new_key: int):
        """Update the encryption key."""
        self.key = new_key & ((1 << self.key_bits) - 1)

