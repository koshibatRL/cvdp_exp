import os
from cocotb_tools.runner import get_runner

# Get environment variables for Verilog sources, top-level language, and simulation options
verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang = os.getenv("TOPLEVEL_LANG")
sim = os.getenv("SIM", "icarus")
toplevel = os.getenv("TOPLEVEL")
module = os.getenv("MODULE")
wave = os.getenv("WAVE")

# Define row and col parameters from environment variables
row = os.getenv("ROW", "2")
col = os.getenv("COL", "2")  # Default to 2 columns

def test_runner():
    # Set the parameters in the environment for the testbench to access
    os.environ["ROW"] = row
    os.environ["COL"] = col

    runner = get_runner(sim)

    # Build the design with dynamic parameters for row and col
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=toplevel,
        always=True,
        clean=True,
        waves=True,
        verbose=True,
        timescale=("1ns", "1ns"),
        log_file="build.log",
        # Pass parameters dynamically to the simulator
        parameters={
            "row": row,
            "col": col
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
