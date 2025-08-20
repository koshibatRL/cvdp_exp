import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
import random

async def init(dut):
    dut.pixel_in.value = 0
    dut.valid_in.value = 0

async def async_rst(dut):   
    dut.rst_n.value = 0  
    await RisingEdge(dut.clk)  
    await Timer(2, units="ns") 
    dut.rst_n.value = 1 

async def sobel_filter_software(image, threshold):
    """Software model for the Sobel filter."""
    Gx_kernel = [[1, 0, -1], [2, 0, -2], [1, 0, -1]]
    Gy_kernel = [[1, 2, 1], [0, 0, 0], [-1, -2, -1]]
    Gx, Gy = 0, 0

    for i in range(3):
        for j in range(3):
            pixel = image[i][j]
            Gx += Gx_kernel[i][j] * pixel
            Gy += Gy_kernel[i][j] * pixel

    abs_Gx = abs(Gx)
    abs_Gy = abs(Gy)
    magnitude = abs_Gx + abs_Gy
    edge_value = 255 if magnitude > threshold else 0
    return edge_value

async def validate_edge(dut, image, threshold, test_name):
    """Validate edge_out value when valid_out is asserted."""
    await RisingEdge(dut.clk)
    if dut.valid_out.value == 1:
        dut_edge_out = int(dut.edge_out.value)
        expected_edge = await sobel_filter_software(image, threshold)
        assert dut_edge_out == expected_edge, f"{test_name} failed at valid_out=1! DUT Output={dut_edge_out}, Expected={expected_edge}"

async def sobel_filter_test(dut, image, threshold, test_name):
    """Run a test case for the Sobel filter."""
    await RisingEdge(dut.clk)
    pixel_stream = [pixel for row in image for pixel in row]  # Flatten 3x3 image to a stream
    dut.valid_in.value = 0  
    dut.pixel_in.value = 0  
    latency = 0

    for pixel in pixel_stream:
        dut.pixel_in.value = pixel
        dut.valid_in.value = 1
        await RisingEdge(dut.clk)  
        if dut.valid_out.value == 0:
            latency += 1
    
    dut.valid_in.value = 0
    dut.pixel_in.value = 0

    expected_latency = 9  
    assert latency == expected_latency, f"{test_name} failed! Measured Latency: {latency}, Expected: {expected_latency}"
    await validate_edge(dut, image, threshold, test_name)

@cocotb.test()
async def sobel_filter_tb(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await init(dut)
    await async_rst(dut)
    threshold = 128
    test_cases = [
        ([[10, 10, 10], [255, 255, 255], [10, 10, 10]], "Horizontal Edge Test"),
        ([[10, 255, 10], [10, 255, 10], [10, 255, 10]], "Vertical Edge Test"),
        ([[128, 128, 128], [128, 128, 128], [128, 128, 128]], "Uniform Input Test"),
        ([[10, 20, 30], [20, 255, 40], [30, 40, 50]], "Edge Detection Test"),
        ([[0, 255, 255], [0, 0, 255], [0, 0, 0]], "Maximum Magnitude Test"),
        ([[0, 0, 0], [0, 255, 0], [0, 0, 0]], "Minimum Magnitude Test"),
    ]

    for image, test_name in test_cases:
        await sobel_filter_test(dut, image, threshold, test_name)
        for _ in range(2):
            await RisingEdge(dut.clk)  

    random_image = [[random.randint(0, 255) for _ in range(3)] for _ in range(3)]
    await sobel_filter_test(dut, random_image, threshold, "Random Input Test")

    for _ in range(5): 
        await RisingEdge(dut.clk)

    cocotb.log.info("All Sobel filter tests passed!")