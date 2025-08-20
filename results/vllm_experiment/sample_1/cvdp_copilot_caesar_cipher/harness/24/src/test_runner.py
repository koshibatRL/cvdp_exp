import os
from cocotb_tools.runner import get_runner

# Get environment variables for Verilog sources, top-level language, and simulation options
verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang = os.getenv("TOPLEVEL_LANG")
sim = os.getenv("SIM", "icarus")
toplevel = os.getenv("TOPLEVEL")
module = os.getenv("MODULE")
wave = os.getenv("WAVE")

# Define PHRASE_WIDTH and PHRASE_LEN parameters from environment variables
PHRASE_WIDTH = os.getenv("PHRASE_WIDTH", "64")  # Default to 8 bits
PHRASE_LEN = os.getenv("PHRASE_LEN", str(int(PHRASE_WIDTH) // 8))  # Default to PHRASE_WIDTH / 8

def test_runner():
    # Set parameters in the environment for the testbench to access
    os.environ["PHRASE_WIDTH"] = PHRASE_WIDTH
    os.environ["PHRASE_LEN"] = PHRASE_LEN

    runner = get_runner(sim)
    
    # Build the design with dynamic parameters for PHRASE_WIDTH and PHRASE_LEN
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        always=True,
        clean=True,
        waves=True,
        verbose=True,
        timescale=("1ns", "1ns"),
        log_file="build.log",
        # Pass PHRASE_WIDTH and PHRASE_LEN as parameters dynamically to the simulator
        parameters={
            "PHRASE_WIDTH": PHRASE_WIDTH,
            "PHRASE_LEN": PHRASE_LEN
        }
    )

    # Run the test
    runner.test(
        hdl_toplevel=toplevel,
        test_module=module,
        waves=True
    )

if __name__ == "__main__":
    test_runner()
