import cocotb
from cocotb.triggers import FallingEdge, RisingEdge, Timer
import random

async def dut_init(dut):
    # iterate all the input signals and initialize with 0
    for signal in dut:
        if signal._type == "GPI_NET":
            signal.value = 0

async def extract_signed(signal, width, total_elements):
         signed_values = []
         for i in reversed(range(total_elements)):
             # Extract the unsigned value
             unsigned_value = (signal.value.to_signed() >> (width * i)) & ((1 << width) - 1)
             # Convert to signed
             signed_value = unsigned_value - (1 << width) if unsigned_value & (1 << (width - 1)) else unsigned_value
             signed_values.append(signed_value)
         return signed_values

# Reset the DUT (design under test)
async def reset_dut(reset_n, duration_ns=10):
    reset_n.value = 0
    await Timer(duration_ns, units="ns")
    reset_n.value = 1
    await Timer(duration_ns, units='ns')
    reset_n._log.debug("Reset complete")   

class PRNG:
    def __init__(self):
        self.s0 = 0
        self.s1 = 0
        self.s2 = 0
        self.s0_next = 0
        self.s1_next = 0
        self.s2_next = 0        
        self.u0      = 0

    def reset(self):
        self.s0 = 0
        self.s1 = 0
        self.s2 = 0
    
    def initialize(self, seed0, seed1, seed2):
        self.s0 = seed0
        self.s1 = seed1
        self.s2 = seed2

    def update(self, init, ce, seed0=0, seed1=0, seed2=0):

        self.u0 = self.s0 ^ self.s1 ^ self.s2
        if init:
            self.initialize(seed0, seed1, seed2)
        elif ce:
            self.s0 = self.s0_next
            self.s1 = self.s1_next
            self.s2 = self.s2_next
        self.s0_next = ((((self.s0 >> 1) & 0x7FFFF) << 13) | (((self.s0 >> 6) ^ (self.s0 >> 19)) & 0x1FFF ) ) & 0xFFFFFFFF
        self.s1_next = ((((self.s1 >> 3) & 0x1FFFFFF) << 7) | ((self.s1 >> 23 ^ self.s1 >> 25) & 0x7F ) ) & 0xFFFFFFFF 
        self.s2_next = ((((self.s2 >> 4) & 0x7FF) << 21) | ((self.s2 >> 8 ^ self.s2 >> 11) & 0x1FFFFF ) ) & 0xFFFFFFFF 

        return self.u0