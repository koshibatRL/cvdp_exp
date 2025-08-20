import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
from cocotb.binary import BinaryValue
import logging

# Constants
APB_ADDRESSES = {
    'DATA_IN': 0x00,       # Address 0x00 >> 2 = 0x00
    'DATA_OUT': 0x01,      # Address 0x04 >> 2 = 0x01
    'DATA_OUT_EN': 0x02,   # Address 0x08 >> 2 = 0x02 (Kept for compatibility)
    'INT_ENABLE': 0x03,    # Address 0x0C >> 2 = 0x03
    'INT_TYPE': 0x04,      # Address 0x10 >> 2 = 0x04
    'INT_POLARITY': 0x05,  # Address 0x14 >> 2 = 0x05
    'INT_STATE': 0x06,     # Address 0x18 >> 2 = 0x06
    'DIR_CONTROL': 0x07,   # Address 0x1C >> 2 = 0x07
    'POWER_DOWN': 0x08,    # Address 0x20 >> 2 = 0x08
    'INT_CTRL': 0x09       # Address 0x24 >> 2 = 0x09
}

async def apb_write(dut, address, data):
    """Perform an APB write transaction"""
    # Set APB write signals
    dut.psel.value = 1
    dut.paddr.value = address  # Word address
    dut.pwrite.value = 1
    dut.pwdata.value = data
    dut.penable.value = 0

    # Wait for posedge pclk
    await RisingEdge(dut.pclk)

    # Enable transfer
    dut.penable.value = 1
    await RisingEdge(dut.pclk)

    # De-assert psel and penable
    dut.psel.value = 0
    dut.penable.value = 0

    # Wait for one clock cycle to complete the transaction
    await RisingEdge(dut.pclk)

async def apb_read(dut, address):
    """Perform an APB read transaction and return the read data"""
    # Set APB read signals
    dut.psel.value = 1
    dut.paddr.value = address  # Word address
    dut.pwrite.value = 0
    dut.penable.value = 0

    # Wait for posedge pclk
    await RisingEdge(dut.pclk)

    # Enable transfer
    dut.penable.value = 1
    await RisingEdge(dut.pclk)

    # Read prdata
    read_data_value = dut.prdata.value
    if read_data_value.is_resolvable:
        read_data = int(read_data_value)
    else:
        read_data = 0  # Or handle as per test requirements

    # De-assert psel and penable
    dut.psel.value = 0
    dut.penable.value = 0

    # Wait for one clock cycle to complete the transaction
    await RisingEdge(dut.pclk)

    return read_data

def check_condition(condition, fail_msg, pass_msg, test_failures):
    """Helper function to log test results"""
    if not condition:
        logging.getLogger().error(fail_msg)
        test_failures.append(fail_msg)
    else:
        logging.getLogger().info(pass_msg)

@cocotb.test()
async def test1_bidirectional_gpio_direction_control(dut):
    """Test 1: Bidirectional GPIOs - Direction Control"""
    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 1: Bidirectional GPIOs - Direction Control")

    # Retrieve GPIO_WIDTH from DUT parameters
    GPIO_WIDTH = int(dut.GPIO_WIDTH.value)

    # Start the clock
    clock = Clock(dut.pclk, 20, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.preset_n.value = 0
    dut.psel.value = 0
    dut.penable.value = 0
    dut.pwrite.value = 0
    dut.pwdata.value = 0
    # Set all GPIOs to 'Z' initially
    for i in range(GPIO_WIDTH):
        dut.gpio[i].value = BinaryValue('Z')
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.preset_n.value = 1

    # Initialize lists to collect failures
    test_failures = []

    # Wait for reset deassertion
    for _ in range(5):
        await RisingEdge(dut.pclk)

    # Configure GPIO[GPIO_WIDTH-1:GPIO_WIDTH-4] as outputs, rest as inputs
    direction_control = ((0xF) << (GPIO_WIDTH - 4)) & ((1 << GPIO_WIDTH) - 1)
    await apb_write(dut, APB_ADDRESSES['DIR_CONTROL'], direction_control)
    read_data = await apb_read(dut, APB_ADDRESSES['DIR_CONTROL'])
    check_condition(
        read_data == direction_control,
        f"FAIL: Direction Control Register mismatch. Expected: 0x{direction_control:0{(GPIO_WIDTH + 3) // 4}X}, Got: 0x{read_data:0{(GPIO_WIDTH + 3) // 4}X}",
        f"PASS: Direction Control Register set to 0x{read_data:0{(GPIO_WIDTH + 3) // 4}X}",
        test_failures
    )

    # Write data to outputs
    data_output = ((0xA) << (GPIO_WIDTH - 4)) & ((1 << GPIO_WIDTH) - 1)
    await apb_write(dut, APB_ADDRESSES['DATA_OUT'], data_output)
    read_data = await apb_read(dut, APB_ADDRESSES['DATA_OUT'])
    check_condition(
        read_data == data_output,
        f"FAIL: Data Output Register mismatch. Expected: 0x{data_output:0{(GPIO_WIDTH + 3) // 4}X}, Got: 0x{read_data:0{(GPIO_WIDTH + 3) // 4}X}",
        f"PASS: Data Output Register value: 0x{read_data:0{(GPIO_WIDTH + 3) // 4}X}",
        test_failures
    )

    # Wait for GPIO outputs to settle
    await Timer(20, units='ns')

    # Verify that GPIO[GPIO_WIDTH-1:GPIO_WIDTH-4] are driven by the DUT
    for i in range(GPIO_WIDTH - 4, GPIO_WIDTH):
        expected_value = (data_output >> i) & 0x1
        actual_value = dut.gpio[i].value
        if actual_value.is_resolvable:
            actual_int = actual_value.integer
            check_condition(
                actual_int == expected_value,
                f"FAIL: GPIO[{i}] output mismatch. Expected: {expected_value}, Got: {actual_int}",
                f"PASS: GPIO[{i}] output matches expected value",
                test_failures
            )
        else:
            test_failures.append(f"FAIL: GPIO[{i}] output is not resolvable")
            logger.error(f"FAIL: GPIO[{i}] output is not resolvable")

    # Drive values on input GPIOs and verify input data
    gpio_input_value = 0xB  # 0b1011

    # Drive the GPIO inputs
    for i in range(GPIO_WIDTH - 4):
        dut.gpio[i].value = (gpio_input_value >> i) & 0x1
    await Timer(1, units='ns')  # Small delay to set values

    # Wait for synchronization (3 clock cycles)
    for _ in range(3):
        await RisingEdge(dut.pclk)

    read_data = await apb_read(dut, APB_ADDRESSES['DATA_IN'])
    expected_data = gpio_input_value & ((1 << (GPIO_WIDTH - 4)) - 1)
    actual_data = read_data & ((1 << (GPIO_WIDTH - 4)) - 1)
    check_condition(
        actual_data == expected_data,
        f"FAIL: GPIO Input Data mismatch on inputs. Expected: 0x{expected_data:X}, Got: 0x{actual_data:X}",
        f"PASS: GPIO Input Data on inputs is 0x{actual_data:X}",
        test_failures
    )

    # Release the drives after the test by setting to 'Z'
    for i in range(GPIO_WIDTH - 4):
        dut.gpio[i].value = BinaryValue('Z')

    # Report failures if any
    if test_failures:
        failure_message = "\n".join(test_failures)
        logger.error(f"Test 1 completed with failures:\n{failure_message}")
        assert False, f"Some test cases failed. Check the log for details:\n{failure_message}"
    else:
        logger.info("Test 1 completed successfully")


@cocotb.test()
async def test2_software_controlled_interrupt_reset(dut):
    """Test 2: Software-Controlled Reset for Interrupts"""
    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 2: Software-Controlled Reset for Interrupts")

    # Retrieve GPIO_WIDTH from DUT parameters
    GPIO_WIDTH = int(dut.GPIO_WIDTH.value)

    # Start the clock
    clock = Clock(dut.pclk, 20, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.preset_n.value = 0
    dut.psel.value = 0
    dut.penable.value = 0
    dut.pwrite.value = 0
    dut.pwdata.value = 0
    # Set all GPIOs to 'Z' initially
    for i in range(GPIO_WIDTH):
        dut.gpio[i].value = BinaryValue('Z')
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.preset_n.value = 1

    # Initialize lists to collect failures
    test_failures = []

    # Wait for reset deassertion
    for _ in range(5):
        await RisingEdge(dut.pclk)

    # Configure GPIO[0] for edge-triggered interrupt
    await apb_write(dut, APB_ADDRESSES['INT_TYPE'], 0x01)     # Edge-triggered on GPIO[0]
    await apb_write(dut, APB_ADDRESSES['INT_POLARITY'], 0x01) # Active high (rising edge)
    await apb_write(dut, APB_ADDRESSES['INT_ENABLE'], 0x01)   # Enable GPIO[0] interrupt
    await apb_write(dut, APB_ADDRESSES['INT_STATE'], 0xFF)    # Clear any pending interrupts

    # Generate a rising edge on GPIO[0]
    dut.gpio[0].value = 0
    await Timer(1, units='ns')
    for _ in range(3):
        await RisingEdge(dut.pclk)
    dut.gpio[0].value = 1
    await Timer(1, units='ns')
    for _ in range(3):
        await RisingEdge(dut.pclk)

    # Check that interrupt is set
    read_data = await apb_read(dut, APB_ADDRESSES['INT_STATE'])
    expected_int_state = 0x01
    actual_int_state = read_data & 0x01
    check_condition(
        actual_int_state == expected_int_state,
        f"FAIL: Interrupt not set on GPIO[0]",
        f"PASS: Interrupt set on GPIO[0] as expected",
        test_failures
    )

    # Use software-controlled reset to clear interrupts
    await apb_write(dut, APB_ADDRESSES['INT_CTRL'], 0x1)
    await Timer(20, units='ns')  # Wait for interrupt reset

    # Verify that interrupt is cleared
    read_data = await apb_read(dut, APB_ADDRESSES['INT_STATE'])
    expected_int_state = 0x00
    actual_int_state = read_data & 0x01
    check_condition(
        actual_int_state == expected_int_state,
        f"FAIL: Interrupt not cleared by software-controlled reset",
        f"PASS: Interrupt cleared by software-controlled reset",
        test_failures
    )

    # Release the drive on GPIO[0] by setting to 'Z'
    dut.gpio[0].value = BinaryValue('Z')

    # Report failures if any
    if test_failures:
        failure_message = "\n".join(test_failures)
        logger.error(f"Test 3 completed with failures:\n{failure_message}")
        assert False, f"Some test cases failed. Check the log for details:\n{failure_message}"
    else:
        logger.info("Test 3 completed successfully")


@cocotb.test()
async def test3_verify_module_power_down_response(dut):
    """Test 3: Verify Module Does Not Respond When Powered Down"""
    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 3: Verify Module Does Not Respond When Powered Down")

    # Retrieve GPIO_WIDTH from DUT parameters
    GPIO_WIDTH = int(dut.GPIO_WIDTH.value)

    # Start the clock
    clock = Clock(dut.pclk, 20, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.preset_n.value = 0
    dut.psel.value = 0
    dut.penable.value = 0
    dut.pwrite.value = 0
    dut.pwdata.value = 0
    # Set all GPIOs to 'Z' initially
    for i in range(GPIO_WIDTH):
        dut.gpio[i].value = BinaryValue('Z')
    await Timer(50, units='ns')
    dut.preset_n.value = 1

    # Initialize lists to collect failures
    test_failures = []

    # Wait for reset deassertion
    for _ in range(5):
        await RisingEdge(dut.pclk)

    # Configure Direction Control Register
    direction_control = ((0xF) << (GPIO_WIDTH - 4)) & ((1 << GPIO_WIDTH) - 1)
    await apb_write(dut, APB_ADDRESSES['DIR_CONTROL'], direction_control)
    await Timer(20, units='ns')

    # Power down the module
    await apb_write(dut, APB_ADDRESSES['POWER_DOWN'], 0x1)
    await Timer(20, units='ns')

    # Try to write to Direction Control Register while powered down
    await apb_write(dut, APB_ADDRESSES['DIR_CONTROL'], 0xFF)
    await Timer(20, units='ns')

    read_data = await apb_read(dut, APB_ADDRESSES['DIR_CONTROL'])
    expected_data = direction_control  # Should not have changed
    actual_data = read_data
    check_condition(
        actual_data == expected_data,
        f"FAIL: Direction Control Register changed during power-down",
        "PASS: Direction Control Register did not change during power-down",
        test_failures
    )

    # Power up the module
    await apb_write(dut, APB_ADDRESSES['POWER_DOWN'], 0x0)
    # Wait for the module to become active
    for _ in range(5):
        await RisingEdge(dut.pclk)

    # Verify that module responds again
    await apb_write(dut, APB_ADDRESSES['DIR_CONTROL'], 0xFF)
    # Wait for the write to take effect
    for _ in range(2):
        await RisingEdge(dut.pclk)
    read_data = await apb_read(dut, APB_ADDRESSES['DIR_CONTROL'])
    expected_data = 0xFF & ((1 << GPIO_WIDTH) - 1)
    actual_data = read_data
    check_condition(
        actual_data == expected_data,
        f"FAIL: Module did not respond after power-up",
        "PASS: Module responds correctly after power-up",
        test_failures
    )

    # Report failures if any
    if test_failures:
        failure_message = "\n".join(test_failures)
        logger.error(f"Test 5 completed with failures:\n{failure_message}")
        assert False, failure_message
    else:
        logger.info("Test 5 completed successfully")

@cocotb.test()
async def test4_verify_interrupts_power_down(dut):
    """Test 4: Verify Interrupts Do Not Occur When Powered Down"""
    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 4: Verify Interrupts Do Not Occur When Powered Down")

    # Retrieve GPIO_WIDTH from DUT parameters
    GPIO_WIDTH = int(dut.GPIO_WIDTH.value)

    # Start the clock
    clock = Clock(dut.pclk, 20, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.preset_n.value = 0
    dut.psel.value = 0
    dut.penable.value = 0
    dut.pwrite.value = 0
    dut.pwdata.value = 0
    # Set all GPIOs to 'Z' initially
    for i in range(GPIO_WIDTH):
        dut.gpio[i].value = BinaryValue('Z')
    await Timer(50, units='ns')
    dut.preset_n.value = 1

    # Initialize lists to collect failures
    test_failures = []

    # Wait for reset deassertion
    for _ in range(5):
        await RisingEdge(dut.pclk)

    # Configure interrupts on GPIO[1]
    await apb_write(dut, APB_ADDRESSES['INT_TYPE'], 0x02)     # Edge-triggered on GPIO[1]
    await apb_write(dut, APB_ADDRESSES['INT_POLARITY'], 0x00) # Active high
    await apb_write(dut, APB_ADDRESSES['INT_ENABLE'], 0x02)   # Enable GPIO[1] interrupt
    await apb_write(dut, APB_ADDRESSES['INT_STATE'], 0xFF)    # Clear any pending interrupts

    # Power down the module
    await apb_write(dut, APB_ADDRESSES['POWER_DOWN'], 0x1)
    await Timer(20, units='ns')

    # Generate an edge on GPIO[1]
    dut.gpio[1].value = 0
    await Timer(1, units='ns')
    for _ in range(3):
        await RisingEdge(dut.pclk)
    dut.gpio[1].value = 1
    await Timer(1, units='ns')
    for _ in range(5):
        await RisingEdge(dut.pclk)

    # Verify that no interrupt is set
    read_data = await apb_read(dut, APB_ADDRESSES['INT_STATE'])
    expected_int_state = 0x00
    actual_int_state = read_data & 0x02
    check_condition(
        actual_int_state == expected_int_state,
        f"FAIL: Interrupt occurred during power-down",
        "PASS: No interrupt occurred during power-down",
        test_failures
    )

    # Power up the module
    await apb_write(dut, APB_ADDRESSES['POWER_DOWN'], 0x0)
    # Wait for the module to become active
    for _ in range(5):
        await RisingEdge(dut.pclk)

    # Generate edge again
    dut.gpio[1].value = 0
    await Timer(1, units='ns')
    for _ in range(3):
        await RisingEdge(dut.pclk)
    dut.gpio[1].value = 1
    await Timer(1, units='ns')
    for _ in range(5):
        await RisingEdge(dut.pclk)

    # Verify that interrupt is now set
    read_data = await apb_read(dut, APB_ADDRESSES['INT_STATE'])
    expected_int_state = 0x02
    actual_int_state = read_data & 0x02
    check_condition(
        actual_int_state == expected_int_state,
        f"FAIL: Interrupt not set after power-up",
        "PASS: Interrupt set after power-up",
        test_failures
    )

    # Release the drive on GPIO[1] by setting to 'Z'
    dut.gpio[1].value = BinaryValue('Z')

    # Report failures if any
    if test_failures:
        failure_message = "\n".join(test_failures)
        logger.error(f"Test 6 completed with failures:\n{failure_message}")
        assert False, failure_message
    else:
        logger.info("Test 6 completed successfully")

@cocotb.test()
async def test5_level_triggered_interrupts(dut):
    """Test 5: Level-Triggered Interrupts"""
    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 5: Level-Triggered Interrupts")

    # Retrieve GPIO_WIDTH from DUT parameters
    GPIO_WIDTH = int(dut.GPIO_WIDTH.value)

    # Start the clock
    clock = Clock(dut.pclk, 20, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.preset_n.value = 0
    dut.psel.value = 0
    dut.penable.value = 0
    dut.pwrite.value = 0
    dut.pwdata.value = 0
    # Set all GPIOs to 'Z' initially
    for i in range(GPIO_WIDTH):
        dut.gpio[i].value = BinaryValue('Z')
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.preset_n.value = 1

    # Wait for reset deassertion
    for _ in range(5):
        await RisingEdge(dut.pclk)

    # Initialize lists to collect failures
    test_failures = []

    # Configure GPIO[0] for level-triggered interrupt
    await apb_write(dut, APB_ADDRESSES['INT_TYPE'], 0x00)     # Level-triggered (INT_TYPE=0)
    await apb_write(dut, APB_ADDRESSES['INT_POLARITY'], 0x01) # Active high (INT_POLARITY=1)
    await apb_write(dut, APB_ADDRESSES['INT_ENABLE'], 0x01)   # Enable GPIO[0] interrupt
    await apb_write(dut, APB_ADDRESSES['INT_STATE'], 0xFF)    # Clear any pending interrupts

    # Set GPIO[0] to high level to trigger interrupt
    dut.gpio[0].value = 1
    await Timer(1, units='ns')
    # Wait for synchronization and interrupt logic update
    for _ in range(5):
        await RisingEdge(dut.pclk)

    # Check that interrupt is set
    read_data = await apb_read(dut, APB_ADDRESSES['INT_STATE'])
    expected_int_state = 0x01
    actual_int_state = read_data & 0x01
    check_condition(
        actual_int_state == expected_int_state,
        f"FAIL: Interrupt not set on GPIO[0] for level-triggered interrupt",
        "PASS: Interrupt set correctly on GPIO[0] for level-triggered interrupt",
        test_failures
    )

    # Now, set GPIO[0] back to low level to clear the interrupt
    dut.gpio[0].value = 0
    await Timer(1, units='ns')
    # Wait for synchronization and interrupt logic update
    for _ in range(5):
        await RisingEdge(dut.pclk)

    # Read INT_STATE again
    read_data = await apb_read(dut, APB_ADDRESSES['INT_STATE'])
    expected_int_state = 0x00
    actual_int_state = read_data & 0x01
    check_condition(
        actual_int_state == expected_int_state,
        f"FAIL: Interrupt not cleared on GPIO[0] when level goes low",
        "PASS: Interrupt cleared correctly on GPIO[0] when level goes low",
        test_failures
    )

    # Release the drive on GPIO[0] by setting to 'Z'
    dut.gpio[0].value = BinaryValue('Z')

    # Report failures if any
    if test_failures:
        failure_message = "\n".join(test_failures)
        logger.error(f"Test 7 completed with failures:\n{failure_message}")
        assert False, failure_message
    else:
        logger.info("Test 7 completed successfully")

@cocotb.test()
async def test6_invalid_apb_addresses(dut):
    """Test 6: Invalid APB Addresses and Error Handling"""
    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 6: Invalid APB Addresses and Error Handling")

    # Retrieve GPIO_WIDTH from DUT parameters
    GPIO_WIDTH = int(dut.GPIO_WIDTH.value)

    # Start the clock
    clock = Clock(dut.pclk, 20, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.preset_n.value = 0
    dut.psel.value = 0
    dut.penable.value = 0
    dut.pwrite.value = 0
    dut.pwdata.value = 0
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.preset_n.value = 1

    # Wait for reset deassertion
    for _ in range(5):
        await RisingEdge(dut.pclk)

    # Initialize lists to collect failures
    test_failures = []

    # Define an invalid address within 6-bit width but outside valid range
    invalid_address = 0x0A  # Next address after valid addresses (assuming valid are 0x00 to 0x09)

    # Attempt to write to invalid address
    await apb_write(dut, invalid_address, 0xDEADBEEF)
    await Timer(10, units='ns')  # Wait for transaction to complete

    # Read from invalid address
    read_data = await apb_read(dut, invalid_address)

    # Read from a valid address to ensure it hasn't been affected
    valid_address = APB_ADDRESSES['DIR_CONTROL']
    expected_data = 0  # After reset, DIR_CONTROL should be 0
    read_data_valid = await apb_read(dut, valid_address)
    check_condition(
        read_data_valid == expected_data,
        f"FAIL: Unexpected data read from valid address 0x{valid_address:X}, expected 0x{expected_data:X}, got 0x{read_data_valid:X}",
        f"PASS: Read expected data 0x{read_data_valid:X} from valid address 0x{valid_address:X}",
        test_failures
    )

    # Now check that reading from invalid address returns zero or default
    check_condition(
        read_data == 0,
        f"FAIL: Read data from invalid address 0x{invalid_address:X} is not zero, got 0x{read_data:X}",
        f"PASS: Read data from invalid address 0x{invalid_address:X} is zero as expected",
        test_failures
    )

    # Ensure module state hasn't changed
    read_data_valid_after = await apb_read(dut, valid_address)
    check_condition(
        read_data_valid_after == expected_data,
        f"FAIL: Module state changed after writing to invalid address",
        f"PASS: Module state unchanged after writing to invalid address",
        test_failures
    )

    # Report failures if any
    if test_failures:
        failure_message = "\n".join(test_failures)
        logger.error(f"Test 8 completed with failures:\n{failure_message}")
        assert False, failure_message
    else:
        logger.info("Test 8 completed successfully")