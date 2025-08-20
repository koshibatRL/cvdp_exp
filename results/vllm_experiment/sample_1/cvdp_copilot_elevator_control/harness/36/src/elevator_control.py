import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, FallingEdge

FLOOR = cocotb.plusargs.get("N")

# Helper function to reset DUT
async def reset_dut(dut, duration_ns):
    dut.reset.value = 1
    await Timer(duration_ns, units="ns")
    dut.reset.value = 0
    await RisingEdge(dut.clk)

# Helper function to trigger a floor request
async def request_floor(dut, floor):
    #current_requests = int(dut.call_requests.value)  # Convert LogicArray to integer
    dut.call_requests.value =  (1 << floor)  # Perform bitwise OR
    await RisingEdge(dut.clk)
    dut.call_requests.value =  0

# Helper function to clear call requests
async def clear_requests(dut):
    dut.call_requests.value = 0
    await RisingEdge(dut.clk)

#Helper function to wait for door close
async def wait_door_close(dut):
    # Wait until the door closes
    dut._log.info("Waiting for the door to close")
    while dut.door_open.value == 1:
        await RisingEdge(dut.clk)

# Helper function to check seven-segment display output for all places
async def check_seven_segment(dut, expected_floor):
    # Floor-to-segment mappings
    floor_to_seg_map = {
        0: 0b1111110,  # 0
        1: 0b0110000,  # 1
        2: 0b1101101,  # 2
        3: 0b1111001,  # 3
        4: 0b0110011,  # 4
        5: 0b1011011,  # 5
        6: 0b1011111,  # 6
        7: 0b1110000,  # 7
        8: 0b1111111,  # 8
        9: 0b1111011   # 9
    }

    # Convert the expected floor to its BCD representation
    expected_one = expected_floor % 10
    expected_ten = (expected_floor // 10) % 10
    expected_hundred = (expected_floor // 100) % 10

    # Check one's place
    await RisingEdge(dut.clk)

    while dut.seven_seg_out_anode.value != 0b1110:
        await RisingEdge(dut.clk)
    if dut.seven_seg_out_anode.value == 0b1110:
        assert int(dut.seven_seg_out.value) == floor_to_seg_map[expected_one], \
            f"One's place mismatch: Expected {bin(floor_to_seg_map[expected_one])}, got {bin(int(dut.seven_seg_out.value))}"
        dut._log.info(f"One's place matched: {expected_one}")

    # Check ten's place
    await RisingEdge(dut.clk)
    while dut.seven_seg_out_anode.value != 0b1101:
        await RisingEdge(dut.clk)
    if dut.seven_seg_out_anode.value == 0b1101:
        assert int(dut.seven_seg_out.value) == floor_to_seg_map[expected_ten], \
            f"Ten's place mismatch: Expected {bin(floor_to_seg_map[expected_ten])}, got {bin(int(dut.seven_seg_out.value))}"
        dut._log.info(f"Ten's place matched: {expected_ten}")

    # Check hundred's place
    await RisingEdge(dut.clk)
    while dut.seven_seg_out_anode.value != 0b1011:
        await RisingEdge(dut.clk)
    if dut.seven_seg_out_anode.value == 0b1011:
        assert int(dut.seven_seg_out.value) == floor_to_seg_map[expected_hundred], \
            f"Hundred's place mismatch: Expected {bin(floor_to_seg_map[expected_hundred])}, got {bin(int(dut.seven_seg_out.value))}"
        dut._log.info(f"Hundred's place matched: {expected_hundred}")

    dut._log.info("All digit places matched successfully")



# Test case 1: Single floor request
async def test_case_1(dut):
    """Test case 1: Single floor request"""

    # Request floor 3 and check if the elevator reaches it
    dut._log.info("Requesting floor 3")
    await request_floor(dut, 3)

    #print("A Current Floor", dut.current_floor.value)

    # Wait and check if the elevator reaches floor 3
    while dut.current_floor.value != 3:
        await RisingEdge(dut.clk)
        #print("Current Floor", dut.current_floor.value)
    await RisingEdge(dut.clk)
    await Timer(30, units="ns")
    
    assert dut.door_open.value == 1, "Door did not open at requested floor"
    await check_seven_segment(dut, 3)

    dut._log.info("Elevator reached floor 3 successfully")

    await wait_door_close(dut)

    dut._log.info("Door closed successfully after reaching floor")

# Test case 2: Multiple floor requests
async def test_case_2(dut):
    """Test case 2: Multiple floor requests"""

    FLOOR_SIZE = int(FLOOR)

    if(FLOOR_SIZE == 12):
        dut._log.info("Requesting floor 11")
        floor_list = [11]
        # Request floors 11
        await request_floor(dut, 11)
    elif(FLOOR_SIZE == 13 or FLOOR_SIZE == 14 ):
        dut._log.info("Requesting floor 12")
        floor_list = [12]
        # Request floors 11
        await request_floor(dut, 12)
    elif(FLOOR_SIZE == 24):
        dut._log.info("Requesting floor 19")
        floor_list = [19]
        # Request floors 11
        await request_floor(dut, 19)

    # Check if the elevator serves requests in sequence
    for expected_floor in floor_list:
        while dut.current_floor.value != expected_floor:
            await RisingEdge(dut.clk)
        await Timer(30, units="ns")
        assert dut.door_open.value == 1, f"Door did not open at floor {expected_floor}"
        await Timer(40, units="ns")  # Simulate door open delay
        #print(expected_floor, "door value: ", dut.door_open.value)
        await check_seven_segment(dut, expected_floor)
        dut._log.info(f"Elevator reached floor {expected_floor}")

    dut._log.info("Elevator served multiple requests successfully")


# Test case 3: Sparse requests at floors 3 and 7
async def test_case_sparse_requests(dut):
    """Test case 3: Sparse requests at floors 3 and 7"""

    # Apply reset to initialize the DUT
    await reset_dut(dut, 30)
    
    dut._log.info("Testing sparse requests at floors 3 and 7")

    # Request floors 3 and 7
    await request_floor(dut, 3)
    await request_floor(dut, 7)

    print("max_request:", int(dut.max_request.value))
    print("min_request:", int(dut.min_request.value))

    # Expected behavior: The elevator should first serve floor 3, then floor 7
    for expected_floor in [3, 7]:
        print(dut.call_requests_internal.value)
        dut._log.info(f"Waiting for elevator to reach floor {expected_floor}")
        while dut.current_floor.value != expected_floor:
            await RisingEdge(dut.clk)

        # Verify door opens at the correct floor
        await Timer(40, units="ns")  # Allow some time for the system to stabilize
        assert dut.door_open.value == 1, f"Door did not open at floor {expected_floor}"
        dut._log.info(f"Door opened correctly at floor {expected_floor}")

        # Check seven-segment display output for the correct floor
        #await check_seven_segment(dut, expected_floor)

        # Wait for the door to close before moving to the next request
        await wait_door_close(dut)
        dut._log.info(f"Door closed at floor {expected_floor}")

    dut._log.info("Sparse request test passed: Floors 3 and 7 served successfully")

@cocotb.test()
async def test_elevator_sparse_requests(dut):
    """Main test for sparse floor requests to detect max_request and min_request issues"""

    # Start the clock
    clock = Clock(dut.clk, 10, units="ns")  # 100 MHz clock
    cocotb.start_soon(clock.start())

    # Initialize signals
    dut.reset.value = 0
    dut.call_requests.value = 0
    dut.emergency_stop.value = 0

    # Apply reset
    await reset_dut(dut, 30)

    # Run sparse request test case
    await test_case_sparse_requests(dut)
