import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer

@cocotb.test()
async def test_bug_detection(dut):
    """Test the conv3x3 module for bug detection."""

    # Generate clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset the design
    dut.rst_n.value = 0
    await Timer(20, units="ns")
    dut.rst_n.value = 1

    # Initialize inputs
    dut.image_data0.value = 1
    dut.image_data1.value = 1
    dut.image_data2.value = 1
    dut.image_data3.value = 1
    dut.image_data4.value = 1
    dut.image_data5.value = 1
    dut.image_data6.value = 1
    dut.image_data7.value = 1
    dut.image_data8.value = 1

    dut.kernel0.value = 1
    dut.kernel1.value = 1
    dut.kernel2.value = 1
    dut.kernel3.value = 1
    dut.kernel4.value = 1
    dut.kernel5.value = 1
    dut.kernel6.value = 1
    dut.kernel7.value = 1
    dut.kernel8.value = 1

    # Wait for computations to settle
    await Timer(100, units="ns")

    # Calculate expected results
    # Correct row sums
    expected_pipeline_sum_stage10 = 3  # Row 1
    expected_pipeline_sum_stage11 = 3  # Row 2
    expected_pipeline_sum_stage12 = 3  # Row 3

    # Correct total sum
    expected_total_sum = expected_pipeline_sum_stage10 + expected_pipeline_sum_stage11 + expected_pipeline_sum_stage12

    # Correct normalization
    expected_convolved_data = expected_total_sum // 9

    # Check individual row summations
    assert int(dut.pipeline_sum_stage10.value) == expected_pipeline_sum_stage10, "Error in Row 1 summation!"
    assert int(dut.pipeline_sum_stage11.value) == expected_pipeline_sum_stage11, "Error in Row 2 summation!"
    assert int(dut.pipeline_sum_stage12.value) == expected_pipeline_sum_stage12, "Error in Row 3 summation!"

    # Check total sum
    assert int(dut.sum_result.value) == expected_total_sum, "Error in total summation!"

    # Check normalization
    assert int(dut.convolved_data.value) == expected_convolved_data, "Error in normalization: Division should be by 9!"
