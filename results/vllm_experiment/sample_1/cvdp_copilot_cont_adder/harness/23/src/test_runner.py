import os
from cocotb.runner import get_runner

# Read environment variables
verilog_sources = os.getenv("VERILOG_SOURCES").split()
toplevel_lang   = os.getenv("TOPLEVEL_LANG")
sim             = os.getenv("SIM", "icarus")
toplevel        = os.getenv("TOPLEVEL")
module          = os.getenv("MODULE")
wave            = os.getenv("WAVE")

def test_runner():
    # Define the parameters to test
    parameters = {
        "DATA_WIDTH": 32,
        "THRESHOLD_VALUE_1": 50,
        "THRESHOLD_VALUE_2": 100,
        "SIGNED_INPUTS": 1,
        "WEIGHT": 2
    }

    # Test both ACCUM_MODEs
    for ACCUM_MODE in [0, 1]:
        parameters["ACCUM_MODE"] = ACCUM_MODE

        # Instantiate the simulator runner
        runner = get_runner(sim)

        # Build the DUT with the specific parameters
        runner.build(
            sources=verilog_sources,
            hdl_toplevel=toplevel,
            parameters=parameters,
            always=True,
            clean=True,
            verbose=True,
            timescale=("1ns", "1ns"),
            # Pass parameter to the simulator (if needed)
            # verilog_compile_args can be used for additional arguments
            # log_file=f"build_{ACCUM_MODE}.log",
        )

        # Run the test with the parameters as environment variables
        env = {f"PARAM_{k}": str(v) for k, v in parameters.items()}
        runner.test(
            hdl_toplevel=toplevel,
            test_module=module,
            waves=(wave == "1"),
            extra_env=env
        )

if __name__ == "__main__":
    test_runner()
