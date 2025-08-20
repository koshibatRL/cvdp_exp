import cocotb
from cocotb.triggers import FallingEdge, RisingEdge, Timer
from collections import deque

async def dut_init(dut):
    # iterate all the input signals and initialize with 0
    for signal in dut:
        if signal._type == "GPI_NET":
            signal.value = 0

class LineBuffer:
    def __init__(self, ns_row=10, ns_col=8, ns_r_out=4, ns_c_out=3, pad_constant=255, nbw_data=8):
        self.ns_row = ns_row
        self.ns_col = ns_col
        self.ns_r_out = ns_r_out
        self.ns_c_out = ns_c_out
        self.pad_constant = pad_constant
        self.nbw_data = nbw_data
        self.line_buffer = [[0] * ns_col for _ in range(ns_row)]
        self.o_window = [[0] * ns_c_out for _ in range(ns_r_out)]
    
    def reset(self):
        """Resets the line buffer to all zeros."""
        self.line_buffer = [[0] * self.ns_col for _ in range(self.ns_row)]
        self.o_window = [[0] * self.ns_c_out for _ in range(self.ns_r_out)]
    
    def add_line(self, image_row):
        """Adds a new line to the line buffer, shifting previous lines down."""
        line = []
        mask = (1 << self.nbw_data) - 1
        for col in range(self.ns_col):
            extracted_data = (image_row >> ((self.ns_col - col - 1) * self.nbw_data)) & mask
            line.append(extracted_data)
        
        self.line_buffer.pop()
        self.line_buffer.insert(0, line)
    
    def update_inputs(self, window_row, window_col, mode):
        """Updates the output window based on the mode and window start positions."""
        for row in range(self.ns_r_out):
            for col in range(self.ns_c_out):
                r = window_row + row
                c = window_col + col
                
                if mode == 0:  # NO_BOUND_PROCESS
                    if 0 <= r < self.ns_row and 0 <= c < self.ns_col:
                        self.o_window[row][col] = self.line_buffer[r][c]
                    else:
                        self.o_window[row][col] = 0
                elif mode == 1:  # PAD_CONSTANT
                    if 0 <= r < self.ns_row and 0 <= c < self.ns_col:
                        self.o_window[row][col] = self.line_buffer[r][c]
                    else:
                        self.o_window[row][col] = self.pad_constant
                elif mode == 2:  # EXTEND_NEAR
                    r = max(0, min(r, self.ns_row - 1))
                    c = max(0, min(c, self.ns_col - 1))
                    self.o_window[row][col] = self.line_buffer[r][c]
                elif mode == 3:  # MIRROR_BOUND
                    r = self.ns_row - abs(self.ns_row - 1 - abs(r)) if r >= self.ns_row or r < 0 else r
                    c = self.ns_col - abs(self.ns_col - 1 - abs(c)) if c >= self.ns_col or c < 0 else c
                    self.o_window[row][col] = self.line_buffer[r][c]
                elif mode == 4:  # WRAP_AROUND
                    r = r % self.ns_row
                    c = c % self.ns_col
                    self.o_window[row][col] = self.line_buffer[r][c]
                else:
                    self.o_window[row][col] = 0
    
    def get_o_window_flat(self):
        """Returns o_window as a single unpacked integer, reversed in bit order."""
        packed_value = 0
        for row in reversed(range(self.ns_r_out)):
            for col in reversed(range(self.ns_c_out)):
                packed_value = (packed_value << self.nbw_data) | self.o_window[row][col]
        
        return packed_value