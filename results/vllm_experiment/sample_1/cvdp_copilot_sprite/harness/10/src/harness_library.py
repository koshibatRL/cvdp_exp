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
    reset_n.value = 0
    await Timer(duration_ns, units="ns")
    reset_n.value = 1
    await Timer(duration_ns, units='ns')
    reset_n._log.debug("Reset complete")

class Bitstream:
    IDLE  = 0
    WaitR = 1
    Ready = 2

    def __init__(self):
        self.rst_n = 0
        self.enb = 0
        self.rempty_in = 1
        self.rinc_in = 0
        self.i_byte = 0

        self.o_bit = 0
        self.rempty_out = 1
        self.rinc_out = 0

        self.curr_state = self.IDLE
        self.next_state = self.IDLE

        self.byte_buf = 0
        self.bp = 0

        self.rde = 0

    def reset(self):
        """ Reset the module. """
        self.curr_state = self.IDLE
        self.byte_buf = 0
        self.bp = 0
        self.o_bit = 0
        self.rempty_out = 1
        self.rinc_out = 0

    def update_fsm(self, enb, rempty_in, rinc_in, i_byte):
        """ Update the FSM state based on inputs. """
        self.enb       = enb
        self.rempty_in = rempty_in
        self.rinc_in   = rinc_in
        self.i_byte    = i_byte             
        if self.curr_state == self.IDLE:
            if self.enb:
                self.next_state = self.WaitR
                self.rempty_out = 1
                self.rinc_out = 0
            else:
                self.next_state = self.IDLE
                self.rempty_out = 1
                self.rinc_out = 0

        elif self.curr_state == self.WaitR:
            if self.rempty_in:
                self.next_state = self.WaitR
                self.rempty_out = 1
                self.rinc_out = 0
            else:
                self.next_state = self.Ready
                self.rempty_out = 1
                self.rinc_out = 1

        elif self.curr_state == self.Ready:
            if self.rde:
                if self.rempty_in:
                    self.next_state = self.WaitR
                    self.rempty_out = 1
                    self.rinc_out = 0
                else:
                    self.next_state = self.Ready
                    self.rempty_out = 1
                    self.rinc_out = 1
            else:
                self.next_state = self.Ready
                self.rempty_out = 0
                self.rinc_out = 0

        else:
            self.next_state = self.IDLE
            self.rempty_out = 1
            self.rinc_out = 0

        self.curr_state = self.next_state
        self.update_registers()
        self.rde = (self.bp >> 3) & 1

    def update_registers(self):
        """ Update registers based on FSM output. """
        # Update output bit
        self.o_bit = (self.byte_buf >> (self.bp & 0b111)) & 1
        
        if self.rinc_out:
            self.byte_buf = self.i_byte

        if self.rinc_out:
            self.bp = 0
        elif self.rinc_in and not self.rempty_out:
            self.bp = (self.bp + 1) & 0b1111


    def get_outputs(self):
        """ Get output signals from the module. """
        return {
            "o_bit": self.o_bit,
            "rempty_out": self.rempty_out,
            "rinc_out": self.rinc_out,
        }   