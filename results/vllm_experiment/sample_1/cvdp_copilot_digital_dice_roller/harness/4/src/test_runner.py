
import os
from cocotb_tools.runner import get_runner
import pytest

verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = os.getenv("WAVE")

def test_runner(DICE_MAX: int=6, NUM_DICE: int=2 ):
    parameter = {"DICE_MAX":DICE_MAX, "NUM_DICE":NUM_DICE}
    
    # Debug information
    print(f"[DEBUG] Running simulation with DICE_MAX={DICE_MAX}, NUM_DICE={NUM_DICE}")
    print(f"[DEBUG] Parameters: {parameter}")
    
    runner = get_runner(sim)
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        # Arguments
        always=True,
        clean=True,
        waves=True,
        verbose=True,
        parameters=parameter,
        timescale=("1ns", "1ns"),
        log_file="build.log")

    runner.test(hdl_toplevel=toplevel, test_module=module, waves=True)   

# Parametrize test for different WIDTH and WINDOW_SIZE
@pytest.mark.parametrize("DICE_MAX", [6,8])
@pytest.mark.parametrize("NUM_DICE", [2,3])

#@pytest.mark.parametrize("test", range(1))
def test_digital_dice_roller(DICE_MAX, NUM_DICE):
    # Run the simulation with specified parameters
    test_runner(DICE_MAX=DICE_MAX, NUM_DICE=NUM_DICE)
