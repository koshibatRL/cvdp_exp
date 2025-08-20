import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles, Timer
import random
import harness_library as hrs_lb
import math

# ----------------------------------------
# - Matrix Multiplication Test
# ----------------------------------------

async def reset_dut(dut, duration_ns=10):
  """
    Reset the DUT by setting the synchronous reset signal high for a specified duration
    and then setting it low again.

    During reset, ensure that the DUT's valid_out signal is zero and that no output matrix 
    data is available.
    
    Args:
        dut: The Design Under Test (DUT).
        duration_ns: The time duration in nanoseconds for which the reset signal will be held high.
    """
  dut.srst.value = 1  # Set reset to active high
  await Timer(duration_ns, units="ns")  # Wait for the specified duration

  # Ensure all outputs are zero
  assert dut.valid_out.value == 0, f"[ERROR] valid_out is not zero after reset: {dut.valid_out.value}"
  assert dut.matrix_c.value == 0, f"[ERROR] matrix_c is not zero after reset: {dut.matrix_c.value}"

  dut.srst.value = 0  # Deactivate reset (set it low)
  await Timer(duration_ns, units='ns')  # Wait for the reset to stabilize
  dut.srst._log.debug("Reset complete")


@cocotb.test()
async def verify_matrix_multiplication(dut):
  """
  Verify matrix multiplication outputs
  This test checks for the following:
  - Proper matrix multiplication with correct output.
  - Output latency should match the expected latency of $clog2(COL_A) + 2 cycles.
  - Reset the DUT before and after the test.
  """

  # Start the clock with a 2ns period
  cocotb.start_soon(Clock(dut.clk, 2, units='ns').start())

  # Initialize DUT inputs
  await hrs_lb.dut_init(dut)

  # Apply reset to DUT
  await reset_dut(dut)

  # Wait for few cycles
  for k in range(10):
    await RisingEdge(dut.clk)

  # Retrieve the rows and columns for matrices
  rows_a = int(dut.ROW_A.value)
  cols_a = int(dut.COL_A.value)
  rows_b = int(dut.ROW_B.value)
  cols_b = int(dut.COL_B.value)
  output_width = int(dut.OUTPUT_DATA_WIDTH.value)

  input_width = int(dut.INPUT_DATA_WIDTH.value)
  input_provided = int(cocotb.plusargs["input_provided"]) # Get the input_provided flag from plusargs
  if input_provided == 1:
    num_inputs = 1 # Single input set provided
  else:
    num_inputs = 10 # Multiple input sets generated dynamically

  # Print matrix dimensions for debugging
  print(f"ROW_A: {rows_a}, COL_A: {cols_a}")
  print(f"ROW_B: {rows_b}, COL_B: {cols_b}")
  print(f"INPUT_DATA_WIDTH: {input_width}")

  for i in range(num_inputs):

    if input_provided == 1:
      # Retrieve matrix_a and matrix_b from plusargs (static input)
      matrix_a_flat = int(cocotb.plusargs["matrix_a"])
      matrix_b_flat = int(cocotb.plusargs["matrix_b"])

      # Convert the flattened matrices back to 2D
      matrix_a = hrs_lb.convert_flat_to_2d(matrix_a_flat, rows_a, cols_a, input_width)
      matrix_b = hrs_lb.convert_flat_to_2d(matrix_b_flat, rows_b, cols_b, input_width)
    else:
      # Dynamically generate matrices (input_provided=0)
      matrix_a = hrs_lb.populate_matrix(rows_a, cols_a, input_width)
      matrix_b = hrs_lb.populate_matrix(rows_b, cols_b, input_width)
      
      # Flatten matrices to pass to the DUT
      matrix_a_flat = hrs_lb.convert_2d_to_flat(matrix_a, input_width)
      matrix_b_flat = hrs_lb.convert_2d_to_flat(matrix_b, input_width)

    # Assign the flattened matrices to DUT inputs
    dut.matrix_a.value = matrix_a_flat
    dut.matrix_b.value = matrix_b_flat
    # Set valid_in high to indicate valid inputs
    dut.valid_in.value = 1
    await RisingEdge(dut.clk)
    # Set valid_in low
    dut.valid_in.value = 0

    # Compute the expected result using the reference implementation
    expected_matrix_c = hrs_lb.matrix_multiply(matrix_a, matrix_b)

    # Latency measurement: Count the number of clock cycles until valid_out is asserted
    latency = 0
    while (dut.valid_out.value == 0):
      await RisingEdge(dut.clk)
      latency = latency + 1

    # Convert the output matrix from the DUT from 1D back to 2D form
    matrix_c_flat = int(dut.matrix_c.value)
    matrix_c = hrs_lb.convert_flat_to_2d(matrix_c_flat, rows_a, cols_b, output_width)

    # Verify that the DUT output matches the expected matrix multiplication result
    assert matrix_c == expected_matrix_c, f"Test {i+1}: Matrix C does not match the expected result: {matrix_c} != {expected_matrix_c}"

    # Verify that the latency matches the expected value of $clog2(COL_A) + 2 clock cycles
    assert latency == (math.ceil(math.log2(cols_a)) + 2), f"Test {i+1}: Latency {latency} does not match the expected value: {(math.ceil(math.log2(cols_a)) + 2)}"

    print(f"Test {i+1} passed")

    # Wait for 2 cycles
    for k in range(2):
      await RisingEdge(dut.clk)

    if (i+1) == num_inputs:
      # Apply reset to DUT
      await reset_dut(dut)

      # Wait for 2 cycles
      for k in range(2):
        await RisingEdge(dut.clk)

