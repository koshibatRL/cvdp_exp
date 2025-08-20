import cocotb
from cocotb.triggers import FallingEdge, RisingEdge, Timer
import random

async def dut_init(dut):
    # iterate all the input signals and initialize with 0
    for signal in dut:
        if signal._type == "GPI_NET":
            signal.value = 0

class OneHotGen:
    def __init__(self, ns_a=8, ns_b=4):
        self.NS_A = ns_a
        self.NS_B = ns_b
        self.state = "IDLE"
        self.region_A = 0
        self.region_B = 0
        self.o_ready = 1
        self.o_address_one_hot = 0
        self.position = 1
        self.config = 0
    
    def reset(self):
        self.state = "IDLE"
        self.region_A = 0
        self.region_B = 0
        self.o_ready = 1
        self.o_address_one_hot = 0
    
    def update(self):
        if self.state == "IDLE":
            if (0b01 & self.config) == 0:  # REGION_A
                self.state = "REGION_A"
                self.region_A = 1
                self.region_B = 0
            else:  # REGION_B
                self.state = "REGION_B"
                self.region_A = 0
                self.region_B = 1
        
        # Update the output one-hot encoding
        if self.state == "REGION_A":
            if self.position <= self.NS_A:
                self.o_address_one_hot = 1 << (self.NS_A + self.NS_B - self.position)
                self.position += 1
            elif self.config == 0b10:
                self.state = "REGION_B"
                self.position = 1
                self.o_address_one_hot = 1 << (self.NS_B - self.position)
                self.position += 1
            else:
                self.position = 1
                self.state = "IDLE"
                self.o_address_one_hot = 0
                
        elif self.state == "REGION_B":
            if self.position <= self.NS_B:
                self.o_address_one_hot = 1 << (self.NS_B - self.position)
                self.position += 1
            elif self.config == 0b11:
                self.state = "REGION_A"
                self.position = 1
                self.o_address_one_hot = 1 << (self.NS_A + self.NS_B - self.position)
                self.position += 1
            else:
                self.position = 1
                self.state = "IDLE"
                self.o_address_one_hot = 0
        
        if self.state == "IDLE":
            self.o_ready = 1
        else:
            self.o_ready = 0

    def get_outputs(self):
        return {
            "o_ready": self.o_ready,
            "o_address_one_hot": self.o_address_one_hot
        }