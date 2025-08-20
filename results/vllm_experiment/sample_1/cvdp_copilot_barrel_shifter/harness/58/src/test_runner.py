import os
from cocotb_tools.runner import get_runner

# Get environment variables for verilog sources, top-level language, and simulation options
verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang = os.getenv("TOPLEVEL_LANG")
sim = os.getenv("SIM", "icarus")
toplevel = os.getenv("TOPLEVEL")
module = os.getenv("MODULE")
wave = os.getenv("WAVE")

# Define the parameters to test for multiple widths
DATA_WIDTH_LIST = [8, 32]  # List of data widths to test
SHIFT_BITS_WIDTH_LIST = [3, 5 ]  # List of corresponding shift bit widths


def test_runner():
    runner = get_runner(sim)
    
    for data_width, shift_bits_width in zip(DATA_WIDTH_LIST, SHIFT_BITS_WIDTH_LIST):
        print(f"Running tests for DATA_WIDTH={data_width}, SHIFT_BITS_WIDTH={shift_bits_width}")
        
        # Modify the runner to include parameter passing logic for Icarus or your chosen simulator
        runner.build(
            sources=verilog_sources,
            hdl_toplevel=toplevel,
            always=True,
            clean=True,
            waves=True,
            verbose=True,
            timescale=("1ns", "1ns"),
            log_file=f"build_{data_width}x{shift_bits_width}.log",  # Separate log for each configuration
            # Pass parameters dynamically here using +define+ syntax
            parameters={
                "data_width": data_width,
                "shift_bits_width": shift_bits_width
            }
        )

        # Run the tests for this configuration
        runner.test(
            hdl_toplevel=toplevel,
            test_module=module,
            waves=wave == "1",  # Enable waves if WAVE environment variable is set to "1"
        )

if __name__ == "__main__":
    test_runner()
