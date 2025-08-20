import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles, Timer
import random
import harness_library as hrs_lb
import math

async def reset_dut(dut, duration_ns=10):
  """
    Reset the DUT by setting the synchronous reset signal high for a specified duration
    and then setting it low again.

    During reset, ensure that the DUT's valid_out signal is zero and that no output image 
    data is available.
    
    Args:
        dut: The Design Under Test (DUT).
        duration_ns: The time duration in nanoseconds for which the reset signal will be held high.
    """
  dut.srst.value = 1  # Set reset to active high
  await Timer(duration_ns, units="ns")  # Wait for the specified duration

  # Ensure all outputs are zero
  assert dut.valid_out.value == 0, f"[ERROR] valid_out is not zero after reset: {dut.valid_out.value}"
  assert dut.image_out.value == 0, f"[ERROR] image_out is not zero after reset: {dut.image_out.value}"

  dut.srst.value = 0  # Deactivate reset (set it low)
  await Timer(duration_ns, units='ns')  # Wait for the reset to stabilize
  dut.srst._log.debug("Reset complete")

# ----------------------------------------
# - Image Rotate Test
# ----------------------------------------
@cocotb.test()
async def verify_image_rotate(dut):
  """
  Verify the DUT's image rotate functionality.

  This test performs the following steps:
  1. Initializes the DUT
  2. Dynamically generates random input images and applies them to the DUT.
  3. Compares the DUT output with the expected rotated image result.

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

  # Retrieve DUT configuration parameters
  rows_in = int(dut.IN_ROW.value)
  cols_in = int(dut.IN_COL.value)
  rows_out = max(rows_in,cols_in)
  cols_out = max(rows_in,cols_in)
  data_width = int(dut.DATA_WIDTH.value)
  num_inputs = 10 # Multiple input sets generated dynamically

  # Print Input Image dimensions for debugging
  print(f"IN_ROW: {rows_in}, IN_COL: {cols_in}")
  print(f"DATA_WIDTH: {data_width}")

  for i in range(num_inputs):
    rotation_angle = random.randint(0, 3) # Random Rotation angle (0-3)

    # Generate a random input image
    image_in = hrs_lb.populate_image(rows_in, cols_in, data_width)
    
    # Flatten the 2D input image to a 1D representation for DUT compatibility
    image_in_flat = hrs_lb.convert_2d_to_flat(image_in, data_width)

    # Apply inputs to DUT
    dut.image_in.value = image_in_flat
    dut.rotation_angle.value = rotation_angle

    # Set valid_in high to indicate valid inputs
    dut.valid_in.value = 1
    await RisingEdge(dut.clk)
    # Set valid_in low
    dut.valid_in.value = 0

    # Calculate expected output
    expected_image_out = hrs_lb.calculate_rotated_image(image_in, rotation_angle, rows_out)

    # Latency measurement: Count the number of clock cycles until valid_out is asserted
    latency = 0
    while (dut.valid_out.value == 0):
      await RisingEdge(dut.clk)
      latency = latency + 1

    # Read the DUT output image in flattened form
    image_out_flat = int(dut.image_out.value)

    # Convert the flattened output back to a 2D image for verification
    image_out = hrs_lb.convert_flat_to_2d(image_out_flat, cols_out, rows_out, data_width)

    # Verify that the DUT output matches the expected rotated image result
    assert image_out == expected_image_out, f"Test {i+1}: Image Out does not match the expected result: {image_out} != {expected_image_out}"

    # Verify that the latency matches the expected value of 7 clock cycles
    assert latency == 7, f"Test {i+1}: Latency {latency} does not match the expected value: 7"

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


