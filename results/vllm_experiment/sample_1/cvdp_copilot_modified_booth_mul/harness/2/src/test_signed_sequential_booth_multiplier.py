import cocotb
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock
import random


async def signed_binary_to_int(binary_str, width):
    """ Convert binary string to a signed integer based on two's complement. """
    if binary_str[0] == '1':  # If the MSB is 1, it's a negative number
        # Convert binary string of a negative number's two's complement to integer
        return -((1 << width) - int(binary_str, 2))
    else:
        # Positive number, direct conversion
        return int(binary_str, 2)


@cocotb.test()
async def test_signed_sequential_booth_multiplier(dut):
    """
    Testbench for the signed sequential booth multiplier using cocotb.
    """
    WIDTH = int(dut.WIDTH.value)  # Get the WIDTH parameter from the DUT
    clk_period = 10  # Define the clock period (ns)

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    # Reset the device
    dut.rst.value = 1
    dut.start.value = 0
    dut.A.value = 0
    dut.B.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0

    for _ in range(1):
        A = (2**(WIDTH-1)-1)
        B = (2**(WIDTH-1)-1)
        expected_result = A * B

        # Apply inputs
        dut.A.value = A
        dut.B.value = B
        dut.start.value = 1
        await RisingEdge(dut.clk)
        #await RisingEdge(dut.clk)
        dut.start.value = 0

        
        # Calculate latency (number of clock cycles taken)
        latency = 0
        while int(dut.done.value) == 0:
            await RisingEdge(dut.clk)
            latency += 1

        # Read output from DUT as binary string, assuming it's being stored as a string of 2*WIDTH length
        result_binary_str = str(dut.result.value)  # Assuming binstr gives us the binary representation as string
        result_value = await signed_binary_to_int(result_binary_str, 2*WIDTH)

        # Verify latency
        assert latency == WIDTH/2+4, f"Latency FAIL: Expected {WIDTH/2+4}, got {latency}"
        dut._log.info("Latency PASS")


        # Verify result
        assert result_value == expected_result, f"Test failed for A = {A}, B = {B}: Expected = {expected_result}, Got = {result_value}, Latency = {latency} cycles"
        dut._log.info(f"MAX Test passed for A = {A}, B = {B}: Result = {result_value}, Latency = {latency} cycles")

        # Wait before the next test case
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

    dut._log.info("MAX testcase completed.")


    for _ in range(1):
        A = -2**(WIDTH-1)
        B = -2**(WIDTH-1)
        expected_result = A * B

        # Apply inputs
        dut.A.value = A
        dut.B.value = B
        dut.start.value = 1
        await RisingEdge(dut.clk)
        #await RisingEdge(dut.clk)
        dut.start.value = 0

        
        # Calculate latency (number of clock cycles taken)
        latency = 0
        while int(dut.done.value) == 0:
            await RisingEdge(dut.clk)
            latency += 1

        # Read output from DUT as binary string, assuming it's being stored as a string of 2*WIDTH length
        result_binary_str = str(dut.result.value)  # Assuming binstr gives us the binary representation as string
        result_value = await signed_binary_to_int(result_binary_str, 2*WIDTH)

        # Verify latency
        assert latency == WIDTH/2+4, f"Latency FAIL: Expected {WIDTH/2+4}, got {latency}"
        dut._log.info("Latency PASS")


        # Verify result
        assert result_value == expected_result, f"Test failed for A = {A}, B = {B}: Expected = {expected_result}, Got = {result_value}, Latency = {latency} cycles"
        dut._log.info(f"MINI Test passed for A = {A}, B = {B}: Result = {result_value}, Latency = {latency} cycles")

        # Wait before the next test case
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

    dut._log.info("MINI testcase completed.")
    


    for _ in range(1):
        A = 0
        B = 0
        expected_result = A * B

        # Apply inputs
        dut.A.value = A
        dut.B.value = B
        dut.start.value = 1
        await RisingEdge(dut.clk)
        #await RisingEdge(dut.clk)
        dut.start.value = 0

        
        # Calculate latency (number of clock cycles taken)
        latency = 0
        while int(dut.done.value) == 0:
            await RisingEdge(dut.clk)
            latency += 1

        # Read output from DUT as binary string, assuming it's being stored as a string of 2*WIDTH length
        result_binary_str = str(dut.result.value)  # Assuming binstr gives us the binary representation as string
        result_value = await signed_binary_to_int(result_binary_str, 2*WIDTH)

        # Verify latency
        assert latency == WIDTH/2+4, f"Latency FAIL: Expected {WIDTH/2+4}, got {latency}"
        dut._log.info("Latency PASS")


        # Verify result
        assert result_value == expected_result, f"Test failed for A = {A}, B = {B}: Expected = {expected_result}, Got = {result_value}, Latency = {latency} cycles"
        dut._log.info(f"ZERO Test passed for A = {A}, B = {B}: Result = {result_value}, Latency = {latency} cycles")

        # Wait before the next test case
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

    dut._log.info("MINI testcase completed.")    



    for _ in range(20):
        A = random.randint(-2**(WIDTH-1), 2**(WIDTH-1)-1)
        B = random.randint(-2**(WIDTH-1), 2**(WIDTH-1)-1)
        expected_result = A * B

        # Apply inputs
        dut.A.value = A
        dut.B.value = B
        dut.start.value = 1
        await RisingEdge(dut.clk)
        #await RisingEdge(dut.clk)
        dut.start.value = 0

        
        # Calculate latency (number of clock cycles taken)
        latency = 0
        while int(dut.done.value) == 0:
            await RisingEdge(dut.clk)
            latency += 1

        # Read output from DUT as binary string, assuming it's being stored as a string of 2*WIDTH length
        result_binary_str = str(dut.result.value)  # Assuming binstr gives us the binary representation as string
        result_value = await signed_binary_to_int(result_binary_str, 2*WIDTH)

        # Verify latency
        assert latency == WIDTH/2+4, f"Latency FAIL: Expected {WIDTH/2+4}, got {latency}"
        dut._log.info("Latency PASS")


        # Verify result
        assert result_value == expected_result, f"Test failed for A = {A}, B = {B}: Expected = {expected_result}, Got = {result_value}, Latency = {latency} cycles"
        dut._log.info(f"Random Test passed for A = {A}, B = {B}: Result = {result_value}, Latency = {latency} cycles")

        # Wait before the next test case
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

    dut._log.info("All tests completed.")

@cocotb.test()
async def verify_specific_scenarios(dut):
    """
    Test specific scenarios derived from result tables.
    """
    WIDTH = int(dut.WIDTH.value)  # Get the WIDTH parameter from the DUT
    clk_period = 10  # Define the clock period (ns)

    cocotb.start_soon(Clock(dut.clk, clk_period, units="ns").start())
    
    # Reset the DUT
    dut.rst.value = 1
    dut.start.value = 0
    dut.A.value = 0
    dut.B.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0

    # Define scenarios based on table data
    scenarios1 = [
        {"A": -7, "B": -7, "expected_result": 49, "expected_latency": int(WIDTH/2+4)},
        {"A": -8, "B": -7, "expected_result": 56, "expected_latency": int(WIDTH/2+4)},
        {"A": -7, "B": 2, "expected_result": -14, "expected_latency": int(WIDTH/2+4)},
        {"A": 2, "B": 4, "expected_result": 8, "expected_latency": int(WIDTH/2+4)},
        {"A": -8, "B": -2, "expected_result": 16, "expected_latency": int(WIDTH/2+4)},
        {"A": -1, "B": -4, "expected_result": 4, "expected_latency": int(WIDTH/2+4)},
        {"A": -8, "B": -1, "expected_result": 8, "expected_latency": int(WIDTH/2+4)},
        {"A": 5, "B": -6, "expected_result": -30, "expected_latency": int(WIDTH/2+4)},
        {"A": 1, "B": 4, "expected_result": 4, "expected_latency": int(WIDTH/2+4)},
        {"A": 2, "B": -2, "expected_result": -4, "expected_latency": int(WIDTH/2+4)},
        {"A": -7, "B": 4, "expected_result": -28, "expected_latency": int(WIDTH/2+4)},
    ]

    scenarios2 = [
        {"A": 120, "B": -64, "expected_result": -7680, "expected_latency": int(WIDTH/2+4)},
        {"A": -114, "B": -38, "expected_result": 4332, "expected_latency": int(WIDTH/2+4)},
        {"A": -94, "B": -57, "expected_result": 5358, "expected_latency": int(WIDTH/2+4)},
        {"A": 89, "B": -120, "expected_result": -10680, "expected_latency": int(WIDTH/2+4)},
    ]
    if WIDTH>=8:
        for scenario in scenarios2:
            A = scenario["A"]
            B = scenario["B"]
            expected_result = scenario["expected_result"]
            expected_latency = scenario["expected_latency"]

            # Apply inputs
            dut.A.value = A
            dut.B.value = B
            dut.start.value = 1
            await RisingEdge(dut.clk)
            dut.start.value = 0

            # Wait for the result (track latency)
            latency = 0
            while int(dut.done.value) == 0:
                await RisingEdge(dut.clk)
                latency += 1

            # Retrieve and verify the result
            result_binary_str = str(dut.result.value)
            result_value = await signed_binary_to_int(result_binary_str, 2 * WIDTH)

            # Verify latency
            assert latency == expected_latency, f"Latency FAIL for A={A}, B={B}: Expected {expected_latency}, got {latency}"
            dut._log.info(f"Latency PASS Expected {expected_latency}, got {latency}")

            # Verify result
            assert result_value == expected_result, f"Result FAIL for A={A}, B={B}: Expected {expected_result}, got {result_value}"
            dut._log.info(f"Result PASS for A={A}, B={B}: Expected {expected_result}, got {result_value}")

            # Wait for stabilization
            await RisingEdge(dut.clk)
            await RisingEdge(dut.clk)

        dut._log.info("All scenarios verified.")

    elif WIDTH>=4:
        for scenario in scenarios1:
            A = scenario["A"]
            B = scenario["B"]
            expected_result = scenario["expected_result"]
            expected_latency = scenario["expected_latency"]

            # Apply inputs
            dut.A.value = A
            dut.B.value = B
            dut.start.value = 1
            await RisingEdge(dut.clk)
            dut.start.value = 0

            # Wait for the result (track latency)
            latency = 0
            while int(dut.done.value) == 0:
                await RisingEdge(dut.clk)
                latency += 1

            # Retrieve and verify the result
            result_binary_str = str(dut.result.value)
            result_value = await signed_binary_to_int(result_binary_str, 2 * WIDTH)

            # Verify latency
            assert latency == expected_latency, f"Latency FAIL for A={A}, B={B}: Expected {expected_latency}, got {latency}"
            dut._log.info(f"Latency PASS Expected {expected_latency}, got {latency}")

            # Verify result
            assert result_value == expected_result, f"Result FAIL for A={A}, B={B}: Expected {expected_result}, got {result_value}"
            dut._log.info(f"Result PASS for A={A}, B={B}: Expected {expected_result}, got {result_value}")

            # Wait for stabilization
            await RisingEdge(dut.clk)
            await RisingEdge(dut.clk)

        dut._log.info("All scenarios verified.")
