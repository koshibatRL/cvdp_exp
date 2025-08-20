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

# Helper function to check seven-segment display output
async def check_seven_segment(dut, expected_floor):
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

    #await RisingEdge(dut.clk)
    actual_seven_seg = int(dut.seven_seg_out.value)
    expected_seven_seg = floor_to_seg_map.get(expected_floor, 0b0000000)
    assert actual_seven_seg == expected_seven_seg, \
        f"Seven-segment mismatch: expected {bin(expected_seven_seg)}, got {bin(actual_seven_seg)}"
    
    dut._log.info("Successfully Matched seven segment output")


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

    if(FLOOR_SIZE == 5):
        dut._log.info("Requesting floor 2,4")
        floor_list = [2,4]
        # Request floors 2, 4, and 6
        await request_floor(dut, 2)
        await request_floor(dut, 4)
    else:
        dut._log.info("Requesting floor 2,4,6")
        floor_list = [2,4,6]
        # Request floors 2, 4, and 6
        await request_floor(dut, 2)
        await request_floor(dut, 4)
        await request_floor(dut, 6)

    # Check if the elevator serves requests in sequence
    for expected_floor in floor_list:
        while dut.current_floor.value != expected_floor:
            await RisingEdge(dut.clk)
        await Timer(30, units="ns")
        assert dut.door_open.value == 1, f"Door did not open at floor {expected_floor}"
        await Timer(10, units="ns")  # Simulate door open delay
        await check_seven_segment(dut, expected_floor)
        dut._log.info(f"Elevator reached floor {expected_floor}")

    dut._log.info("Elevator served multiple requests successfully")

# Test case 3: Emergency stop
async def test_case_3(dut):
    """Test case 3: Emergency stop"""

    # Request floor 5 and activate emergency stop midway
    dut._log.info("Requesting floor 4")
    await request_floor(dut, 4)
    await Timer(30, units="ns")  # Wait for some time during movement

    dut._log.info("Activating emergency stop")
    dut.emergency_stop.value = 1
    await RisingEdge(dut.clk)
    await Timer(40, units="ns")  # Wait for some time during movement
    assert dut.system_status.value == 3, "Elevator did not enter emergency halt state"
    dut._log.info("Elevator entered emergency halt state")

    # Deactivate emergency stop and check if elevator resumes operation
    dut.emergency_stop.value = 0
    await RisingEdge(dut.clk)
    await Timer(10, units="ns")  # Wait for some time during movement    
    assert dut.system_status.value == 0, "Elevator did not return to idle after emergency stop"
    dut._log.info("Emergency stop cleared, elevator resumed operation")

# Test case 4: Reset during operation
async def test_case_4(dut):
    """Test case 4: Reset during operation"""

    # Request floor 4
    await request_floor(dut, 4)
    await Timer(20, units="ns")

    # Apply reset and check if elevator goes to idle
    dut._log.info("Applying reset during operation")
    await reset_dut(dut, 20)
    assert dut.current_floor.value == 0, "Elevator did not reset to ground floor"
    assert dut.system_status.value == 0, "Elevator did not return to idle after reset"
    dut._log.info("Reset applied successfully, elevator returned to idle")

# Test case for overweight condition
async def test_overweight_condition(dut):
    """Test case for overweight condition"""

    dut._log.info("Testing Overweight condition")
    # Request a floor (e.g., floor 3)
    dut._log.info("Requesting floor 3")
    await request_floor(dut, 2)

    # Wait until the elevator reaches the requested floor
    while dut.current_floor.value != 2:
        await RisingEdge(dut.clk)
    await Timer(20, units="ns")

    # Assert that the door is open
    assert dut.door_open.value == 1, "Door did not open at requested floor"
    dut._log.info("Door is open at floor 3")

    # Trigger the overweight condition
    dut.overload_detected.value = 1
    await RisingEdge(dut.clk)
    await Timer(50, units="ns")

    # Verify that the system responds to the overweight condition
    assert dut.system_status.value == 5, "Elevator did not handle overweight condition correctly"
    assert dut.overload_warning.value == 1, "Elevator did not handle overweight condition correctly"
    dut._log.info("Overweight condition handled correctly")

    # Clear the overweight condition
    dut.overload_detected.value = 0
    await RisingEdge(dut.clk)
    await Timer(20, units="ns")

    # Verify that the elevator resumes normal operation
    assert dut.system_status.value == 4, "Elevator did not return to normal operation after overweight condition"
    assert dut.overload_warning.value == 0, "Elevator did not handle overweight condition correctly"
    dut._log.info("Elevator resumed normal operation after overweight condition")

    await wait_door_close(dut)
    await Timer(20, units="ns")

@cocotb.test()
async def test_elevator_control_system(dut):
    """Main test function for elevator control system"""

    # Start the clock
    clock = Clock(dut.clk, 10, units="ns")  # 100 MHz clock
    cocotb.start_soon(clock.start())

    # Initialize all signals to known values
    dut.reset.value = 0
    dut.call_requests.value = 0
    dut.emergency_stop.value = 0

    FLOOR_SIZE = int(FLOOR) - 1
    print("System FLOOR Size: 0 to", FLOOR_SIZE)

    ## Apply reset
    await reset_dut(dut, 30)

    ## Run test cases
    await test_case_1(dut)
    await Timer(20, units="ns")  # Wait before next test

    await test_case_2(dut)
    await Timer(20, units="ns")

    ## Apply reset
    await reset_dut(dut, 30)
    await Timer(20, units="ns")
    await test_overweight_condition(dut)
    await Timer(20, units="ns")

    await test_case_3(dut)
    await Timer(20, units="ns")

    await test_case_4(dut)
