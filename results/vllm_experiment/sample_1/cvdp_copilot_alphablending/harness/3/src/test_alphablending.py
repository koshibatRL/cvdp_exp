import cocotb
from cocotb.triggers import RisingEdge, Timer
import random


async def reset_dut(dut, duration):
    """Reset the DUT for a given number of clock cycles."""
    dut.reset.value = 1
    for _ in range(duration):
        await RisingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.clk)


async def clock(dut, clk_period):
    """Generate a clock signal with a given period."""
    while True:
        dut.clk.value = 0
        await Timer(clk_period / 2, units='ns')
        dut.clk.value = 1
        await Timer(clk_period / 2, units='ns')


# Function to generate random test inputs
def generate_test_data(H, W):
    """Generate test input values for pixel, alpha, and background pixels."""

    TOTAL_PIXELS = H * W

    pixel_data = []
    alpha_data = []
    bg_pixel_data = []

    for i in range(TOTAL_PIXELS):
        mode = random.randint(0, 3)  # Random mode selection

        if mode == 0:
            pixel_data.append(0x000000)  # Black (0,0,0)
            alpha_data.append(0x00)  # Fully transparent
            bg_pixel_data.append(0xFF0000)  # Red background
        elif mode == 1:
            pixel_data.append(0xFFFFFF)  # White (255,255,255)
            alpha_data.append(0x80)  # 50% alpha
            bg_pixel_data.append(0x00FF00)  # Green background
        elif mode == 2:
            pixel_data.append(0x808080)  # Medium Gray (128,128,128)
            alpha_data.append(0xFF)  # Fully opaque
            bg_pixel_data.append(0x0000FF)  # Blue background
        else:
            pixel_data.append(random.randint(0, 0xFFFFFF))  # Random color
            alpha_data.append(random.randint(0, 255))  # Random alpha
            bg_pixel_data.append(random.randint(0, 0xFFFFFF))  # Random background

    return pixel_data, alpha_data, bg_pixel_data


def compute_expected_output(pixel_data, alpha_data, bg_pixel_data):
    """Compute the reference output using the alpha blending formula."""
    TOTAL_PIXELS = len(pixel_data)
    blended_output = []

    for i in range(TOTAL_PIXELS):
        alpha = alpha_data[i]

        # Extract RGB components
        fg_r = (pixel_data[i] >> 16) & 0xFF
        fg_g = (pixel_data[i] >> 8) & 0xFF
        fg_b = pixel_data[i] & 0xFF

        bg_r = (bg_pixel_data[i] >> 16) & 0xFF
        bg_g = (bg_pixel_data[i] >> 8) & 0xFF
        bg_b = bg_pixel_data[i] & 0xFF

        # Compute blended RGB
        blended_r = (alpha * fg_r + (255 - alpha) * bg_r) // 255
        blended_g = (alpha * fg_g + (255 - alpha) * bg_g) // 255
        blended_b = (alpha * fg_b + (255 - alpha) * bg_b) // 255

        # Pack into 24-bit color
        blended_output.append((blended_r << 16) | (blended_g << 8) | blended_b)

    return blended_output


@cocotb.test()
async def alpha_blending_test(dut):
    """Test alpha blending module with multiple randomized inputs and reference comparison."""

    # Initialize inputs
    dut.clk.value = 0
    dut.reset.value = 1
    dut.start.value = 0
    dut.pixel_in.value = 0
    dut.alpha_in.value = 0
    dut.bg_pixel_in.value = 0

    # Get parameters from the DUT
    H = int(dut.H.value)
    W = int(dut.W.value)
    clk_period = 10  # ns

    random.seed(0)  # For reproducibility

    # Start clock
    cocotb.start_soon(clock(dut, clk_period))

    # Reset the DUT
    await reset_dut(dut, 5)
    dut.start.value = 0

    # Run 4 test cases with different random inputs
    for test_id in range(4):
        # Generate test data
        pixel_data, alpha_data, bg_pixel_data = generate_test_data(H, W)

        # Compute expected output
        expected_output = compute_expected_output(pixel_data, alpha_data, bg_pixel_data)

        # Pack data into a single integer for SystemVerilog compatibility
        pixel_in = sum(pixel_data[i] << (i * 24) for i in range(len(pixel_data)))
        alpha_in = sum(alpha_data[i] << (i * 8) for i in range(len(alpha_data)))
        bg_pixel_in = sum(bg_pixel_data[i] << (i * 24) for i in range(len(bg_pixel_data)))

        # Apply test values
        dut.pixel_in.value = pixel_in
        dut.alpha_in.value = alpha_in
        dut.bg_pixel_in.value = bg_pixel_in
        dut.start.value = 1
        await RisingEdge(dut.clk)
        dut.start.value = 0

        # Wait for done signal
        while dut.done.value == 0:
            await RisingEdge(dut.clk)

        # Get DUT output
        blended_out = int(dut.blended_out.value)

        # Extract DUT output pixels
        dut_output = [(blended_out >> (i * 24)) & 0xFFFFFF for i in range(len(expected_output))]
        
        
        # Compare against expected output
        print(f"\nTest {test_id + 1}:")
        for i in range(len(expected_output)):
            print(f"  MATCH at Pixel {i}: {hex(expected_output[i])}, dut: {dut_output[i]}")
            assert dut_output[i] == expected_output[i], f"  MISMATCH at Pixel {i}: Expected {hex(expected_output[i])}, Got {hex(dut_output[i])}"
            #else:
            #    print(f"  MATCH at Pixel {i}: {hex(expected_output[i])}")

        await Timer(50, units="ns")
