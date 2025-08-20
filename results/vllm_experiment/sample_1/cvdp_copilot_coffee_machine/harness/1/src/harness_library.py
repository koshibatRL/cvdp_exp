import cocotb
from cocotb.triggers import FallingEdge, RisingEdge, Timer
import random

async def dut_init(dut):
    # iterate all the input signals and initialize with 0
    for signal in dut:
        if signal._type == "GPI_NET":
            signal.value = 0

class CoffeeMachine:
    def __init__(self, operation=0, i_grind_delay=1, i_heat_delay=1, i_pour_delay=1, i_bean_sel=0, num_beans=4):
        self.state = "IDLE"
        self.o_bean_sel = 0
        self.o_grind_beans = 0
        self.o_use_powder = 0
        self.o_heat_water = 0
        self.o_pour_coffee = 0
        self.o_error = 0
        self.i_sensor = 0
        self.operation = operation
        self.step = 0  # Track progress in operation sequence
        self.i_grind_delay = i_grind_delay
        self.i_heat_delay = i_heat_delay
        self.i_pour_delay = i_pour_delay
        self.state_counter = 0  # Counter for state delays
        self.POWDER_DELAY = 2  # Fixed delay for POWDER state
        self.BEAN_SEL_DELAY = 3  # Fixed delay for BEAN_SEL state
        self.i_bean_sel = i_bean_sel
        self.num_beans = num_beans
    
    def reset(self):
        self.state = "IDLE"
        self.reset_outputs()
        
    
    def update_error(self):
        if self.i_sensor & 0b1000:  # Generic error
            self.o_error = 1
        elif self.state == "IDLE":
            if self.i_sensor & 0b0001:  # No water error
                self.o_error = 1
            elif (self.i_sensor & 0b0010) and (self.operation == 0b010 or self.operation == 0b011):  # No beans error
                self.o_error = 1
            elif (self.i_sensor & 0b0100) and (self.operation == 0b100 or self.operation == 0b001):  # No powder error
                self.o_error = 1
            elif self.operation == 0b110 or self.operation == 0b111:
                self.o_error = 1
            else:
                self.o_error = 0
        else:
            self.o_error = 0
    
    def update_state(self, operation, i_sensor, i_grind_delay, i_heat_delay, i_pour_delay, i_bean_sel):
        self.i_sensor = i_sensor
        if self.state == "IDLE":
            self.operation = operation
            self.i_grind_delay = i_grind_delay
            self.i_heat_delay = i_heat_delay
            self.i_pour_delay = i_pour_delay
            self.i_bean_sel = i_bean_sel
            self.step = 0  # Reset step counter
            self.state_counter = 0
        self.update_error()

        steps = {
            0b000: [self.heat, self.pour, self.idle],
            0b001: [self.heat, self.powder, self.pour, self.idle],
            0b010: [self.bean_sel, self.grind, self.heat, self.powder, self.pour, self.idle],
            0b011: [self.bean_sel, self.grind, self.powder, self.pour, self.idle],
            0b100: [self.powder, self.pour, self.idle],
            0b101: [self.pour, self.idle],
        }
        
        if self.o_error:
            current_state = steps[self.operation][self.step]
            current_state()
            self.state = "IDLE"
            return

        
        if self.operation in steps and self.step < len(steps[self.operation]):
            current_state = steps[self.operation][self.step]
            
            if self.state == "BEAN_SEL" and self.state_counter < self.BEAN_SEL_DELAY-1:
                self.state_counter += 1
            elif self.state == "GRIND" and self.state_counter < self.i_grind_delay-1:
                self.state_counter += 1
            elif self.state == "HEAT" and self.state_counter < self.i_heat_delay-1:
                self.state_counter += 1
            elif self.state == "POWDER" and self.state_counter < self.POWDER_DELAY-1:
                self.state_counter += 1
            elif self.state == "POUR" and self.state_counter < self.i_pour_delay-1:
                self.state_counter += 1
            else:
                self.state_counter = 0
                current_state()
                self.step += 1  # Move to next step in the sequence
        
        return 0
    
    def idle(self):
        self.state = "IDLE"
        self.reset_outputs()
    
    def bean_sel(self):
        self.reset_outputs()
        self.state = "BEAN_SEL"
        self.o_bean_sel = 1 << self.i_bean_sel  # One-hot encoding
    
    def grind(self):
        self.reset_outputs()
        self.state = "GRIND"
        self.o_grind_beans = 1
        self.o_bean_sel = 1 << self.i_bean_sel  # Maintain bean selection in one-hot encoding
    
    def powder(self):
        self.reset_outputs()
        self.state = "POWDER"
        self.o_use_powder = 1
    
    def heat(self):
        self.reset_outputs()
        self.state = "HEAT"
        self.o_heat_water = 1
    
    def pour(self):
        self.reset_outputs()
        self.state = "POUR"
        self.o_pour_coffee = 1
    
    def reset_outputs(self):
        self.o_bean_sel = 0
        self.o_grind_beans = 0
        self.o_use_powder = 0
        self.o_heat_water = 0
        self.o_pour_coffee = 0
    
    def get_status(self):
        return {
            "state": self.state,
            "o_bean_sel": self.o_bean_sel,
            "o_grind_beans": self.o_grind_beans,
            "o_use_powder": self.o_use_powder,
            "o_heat_water": self.o_heat_water,
            "o_pour_coffee": self.o_pour_coffee,
            "o_error": self.o_error,
            "step": self.step,
            "state_counter": self.state_counter,
        }