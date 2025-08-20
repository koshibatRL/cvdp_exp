import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
import logging

# Constants
APB_ADDRESSES = {
    'ADDRESS_A': 0x00,
    'ADDRESS_B': 0x04,
    'ADDRESS_C': 0x08,
    'ADDRESS_O': 0x0C,
    'ADDRESS_CONTROL': 0x10,
    'ADDRESS_WDATA': 0x14,
    'ADDRESS_SRAM_ADDR': 0x18
}

async def apb_write(dut, address, data):
    """Perform an APB write transaction"""
    # Set APB write signals
    dut.PSEL.value = 1
    dut.PADDR.value = address  # Word address
    dut.PWRITE.value = 1
    dut.PWDATA.value = data
    dut.PENABLE.value = 0

    # Wait for posedge PCLK
    await RisingEdge(dut.PCLK)

    # Enable transfer
    dut.PENABLE.value = 1
    await RisingEdge(dut.PCLK)

    # De-assert PSEL and PENABLE
    dut.PSEL.value = 0
    dut.PENABLE.value = 0

async def apb_read(dut, address):
    """Perform an APB read transaction and return the read data"""
    # Set APB read signals
    dut.PSEL.value = 1
    dut.PADDR.value = address  # Word address
    dut.PWRITE.value = 0
    dut.PENABLE.value = 0

    # Wait for posedge PCLK
    await RisingEdge(dut.PCLK)

    # Enable transfer
    dut.PENABLE.value = 1
    await RisingEdge(dut.PCLK)

    # De-assert PSEL and PENABLE
    dut.PSEL.value = 0
    dut.PENABLE.value = 0
    await RisingEdge(dut.PCLK)

    # Read PRDATA
    read_data = int(dut.PRDATA.value)

    return read_data

def check_condition(condition, fail_msg, pass_msg, test_failures):
    """Helper function to log test results"""
    if not condition:
        logging.getLogger().error(fail_msg)
        test_failures.append(fail_msg)
    else:
        logging.getLogger().info(pass_msg)

@cocotb.test()
async def test1_write_read_addr_a(dut):
    """Test 1: Write and Read ADDRESS_A Register (reg_operand_a)"""

    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 1: Write and Read ADDRESS_A Register")

    # Retrieve ADDR_WIDTH and DATA_WIDTH from DUT parameters
    ADDR_WIDTH = int(dut.ADDR_WIDTH.value)
    DATA_WIDTH = int(dut.DATA_WIDTH.value)

    # Start the clocks
    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_dsp, 1, units="ns").start())

    # Reset
    dut.PRESETn.value = 0
    dut.en_clk_dsp.value = 0
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.PRESETn.value = 1

    # Wait for reset deassertion
    await RisingEdge(dut.PCLK)

    # Perform APB write to ADDRESS_A
    write_data = 0xA5A5A5A5  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_A'], write_data)

    # Perform APB read from ADDRESS_A
    read_data = await apb_read(dut, APB_ADDRESSES['ADDRESS_A'])
    expected_data = write_data
    actual_data = read_data
    
    # Initialize list to collect failures
    test_failures = []

    # Check Data Output Register
    check_condition(
        actual_data == expected_data,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data}, "
        f"Got: 0x{actual_data}",
        f"PASS: Data Output Register value: 0x{actual_data}",
        test_failures
    )

@cocotb.test()
async def test2_write_read_addr_b(dut):
    """Test 2: Write and Read ADDRESS_B Register (reg_operand_b)"""

    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 2: Write and Read ADDRESS_B Register")

    # Retrieve ADDR_WIDTH and DATA_WIDTH from DUT parameters
    ADDR_WIDTH = int(dut.ADDR_WIDTH.value)
    DATA_WIDTH = int(dut.DATA_WIDTH.value)

    # Start the clocks
    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_dsp, 1, units="ns").start())

    # Reset
    dut.PRESETn.value = 0
    dut.en_clk_dsp.value = 0
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.PRESETn.value = 1

    # Wait for reset deassertion
    await RisingEdge(dut.PCLK)

    # Perform APB write to ADDRESS_B
    write_data = 0xA5A5A5A5  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_B'], write_data)

    # Perform APB read from ADDRESS_B
    read_data = await apb_read(dut, APB_ADDRESSES['ADDRESS_B'])
    expected_data = write_data
    actual_data = read_data
    
    # Initialize list to collect failures
    test_failures = []

    # Check Data Output Register
    check_condition(
        actual_data == expected_data,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data}, "
        f"Got: 0x{actual_data}",
        f"PASS: Data Output Register value: 0x{actual_data}",
        test_failures
    )

@cocotb.test()
async def test3_write_read_addr_c(dut):
    """Test 3: Write and Read ADDRESS_C Register (reg_operand_c)"""

    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 3: Write and Read ADDRESS_C Register")

    # Retrieve ADDR_WIDTH and DATA_WIDTH from DUT parameters
    ADDR_WIDTH = int(dut.ADDR_WIDTH.value)
    DATA_WIDTH = int(dut.DATA_WIDTH.value)

    # Start the clocks
    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_dsp, 1, units="ns").start())

    # Reset
    dut.PRESETn.value = 0
    dut.en_clk_dsp.value = 0
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.PRESETn.value = 1

    # Wait for reset deassertion
    await RisingEdge(dut.PCLK)

    # Perform APB write to ADDRESS_C
    write_data = 0xA5A5A5A5  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_C'], write_data)

    # Perform APB read from ADDRESS_C
    read_data = await apb_read(dut, APB_ADDRESSES['ADDRESS_C'])
    expected_data = write_data
    actual_data = read_data
    
    # Initialize list to collect failures
    test_failures = []

    # Check Data Output Register
    check_condition(
        actual_data == expected_data,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data}, "
        f"Got: 0x{actual_data}",
        f"PASS: Data Output Register value: 0x{actual_data}",
        test_failures
    )

@cocotb.test()
async def test4_write_read_addr_o(dut):
    """Test 4: Write and Read ADDRESS_O Register (reg_operand_o)"""

    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 4: Write and Read ADDRESS_O Register")

    # Retrieve ADDR_WIDTH and DATA_WIDTH from DUT parameters
    ADDR_WIDTH = int(dut.ADDR_WIDTH.value)
    DATA_WIDTH = int(dut.DATA_WIDTH.value)

    # Start the clocks
    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_dsp, 1, units="ns").start())

    # Reset
    dut.PRESETn.value = 0
    dut.en_clk_dsp.value = 0
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.PRESETn.value = 1

    # Wait for reset deassertion
    await RisingEdge(dut.PCLK)

    # Perform APB write to ADDRESS_O
    write_data = 0xA5A5A5A5  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_O'], write_data)

    # Perform APB read from ADDRESS_O
    read_data = await apb_read(dut, APB_ADDRESSES['ADDRESS_O'])
    expected_data = write_data
    actual_data = read_data
    
    # Initialize list to collect failures
    test_failures = []

    # Check Data Output Register
    check_condition(
        actual_data == expected_data,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data}, "
        f"Got: 0x{actual_data}",
        f"PASS: Data Output Register value: 0x{actual_data}",
        test_failures
    )

@cocotb.test()
async def test5_write_read_addr_control(dut):
    """Test 5: Write and Read ADDRESS_CONTROL Register (reg_control)"""

    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 5: Write and Read ADDRESS_CONTROL Register")

    # Retrieve ADDR_WIDTH and DATA_WIDTH from DUT parameters
    ADDR_WIDTH = int(dut.ADDR_WIDTH.value)
    DATA_WIDTH = int(dut.DATA_WIDTH.value)

    # Start the clocks
    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_dsp, 1, units="ns").start())

    # Reset
    dut.PRESETn.value = 0
    dut.en_clk_dsp.value = 0
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.PRESETn.value = 1

    # Wait for reset deassertion
    await RisingEdge(dut.PCLK)

    # Perform APB write to ADDRESS_CONTROL
    write_data = 0xA5A5A5A5  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], write_data)

    # Perform APB read from ADDRESS_CONTROL
    read_data = await apb_read(dut, APB_ADDRESSES['ADDRESS_CONTROL'])
    expected_data = write_data
    actual_data = read_data
    
    # Initialize list to collect failures
    test_failures = []

    # Check Data Output Register
    check_condition(
        actual_data == expected_data,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data}, "
        f"Got: 0x{actual_data}",
        f"PASS: Data Output Register value: 0x{actual_data}",
        test_failures
    )

@cocotb.test()
async def test6_write_read_wdata_sram(dut):
    """Test 6: Write and Read ADDRESS_WDATA Register (reg_wdata_sram)"""

    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 6: Write and Read ADDRESS_WDATA Register")

    # Retrieve ADDR_WIDTH and DATA_WIDTH from DUT parameters
    ADDR_WIDTH = int(dut.ADDR_WIDTH.value)
    DATA_WIDTH = int(dut.DATA_WIDTH.value)

    # Start the clocks
    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_dsp, 1, units="ns").start())

    # Reset
    dut.PRESETn.value = 0
    dut.en_clk_dsp.value = 0
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.PRESETn.value = 1

    # Wait for reset deassertion
    await RisingEdge(dut.PCLK)

    # Perform APB write to ADDRESS_WDATA
    write_data = 0xA5A5A5A5  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_WDATA'], write_data)

    # Perform APB read from ADDRESS_WDATA
    read_data = await apb_read(dut, APB_ADDRESSES['ADDRESS_WDATA'])
    expected_data = write_data
    actual_data = read_data
    
    # Initialize list to collect failures
    test_failures = []

    # Check Data Output Register
    check_condition(
        actual_data == expected_data,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data}, "
        f"Got: 0x{actual_data}",
        f"PASS: Data Output Register value: 0x{actual_data}",
        test_failures
    )

@cocotb.test()
async def test7_write_read_addr_sram(dut):
    """Test 7: Write and Read ADDRESS_SRAM_ADDR Register (reg_addr_sram)"""

    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 7: Write and Read ADDRESS_SRAM_ADDR Register")

    # Retrieve ADDR_WIDTH and DATA_WIDTH from DUT parameters
    ADDR_WIDTH = int(dut.ADDR_WIDTH.value)
    DATA_WIDTH = int(dut.DATA_WIDTH.value)

    # Start the clocks
    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_dsp, 1, units="ns").start())

    # Reset
    dut.PRESETn.value = 0
    dut.en_clk_dsp.value = 0
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.PRESETn.value = 1

    # Wait for reset deassertion
    await RisingEdge(dut.PCLK)

    # Perform APB write to ADDRESS_SRAM_ADDR
    write_data = 0xA5A5A5A5  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], write_data)

    # Perform APB read from ADDRESS_SRAM_ADDR
    read_data = await apb_read(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'])
    expected_data = write_data
    actual_data = read_data
    
    # Initialize list to collect failures
    test_failures = []

    # Check Data Output Register
    check_condition(
        actual_data == expected_data,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data}, "
        f"Got: 0x{actual_data}",
        f"PASS: Data Output Register value: 0x{actual_data}",
        test_failures
    )

@cocotb.test()
async def test8_invalid_address_access(dut):
    """Test 8: Attempt to Access Invalid Address"""

    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 8: Attempt to Access Invalid Address")

    # Retrieve ADDR_WIDTH and DATA_WIDTH from DUT parameters
    ADDR_WIDTH = int(dut.ADDR_WIDTH.value)
    DATA_WIDTH = int(dut.DATA_WIDTH.value)

    # Start the clocks
    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_dsp, 1, units="ns").start())

    # Reset
    dut.PRESETn.value = 0
    dut.en_clk_dsp.value = 0
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.PRESETn.value = 1

    # Wait for reset deassertion
    await RisingEdge(dut.PCLK)

    # Attempt to write to an invalid address (e.g., 0x3F)
    invalid_address = 0x3F
    write_data = 0xDEADBEEF
    await apb_write(dut, invalid_address, write_data)

    await RisingEdge(dut.PCLK)

    received_PSLVERR = dut.PSLVERR
    received_PREADY = dut.PREADY

    # Initialize list to collect failures
    test_failures = []

    # Check that invalid address triggers PSLVERR
    check_condition(
        received_PSLVERR == 1,
        f"FAIL: Invalid address should raise PSLVERR. Expected: {1}, Got: {received_PSLVERR}",
        "PASS: Invalid address access raised PSLVERR as expected",
        test_failures
    )

    # Check that PREADY is asserted
    check_condition(
        received_PREADY == 1,
        f"FAIL: Invalid address should raise PSLVERR. Expected: {1}, Got: {received_PREADY}",
        "PASS: Invalid address access raised PSLVERR as expected",
        test_failures
    )

    # Report failures if any
    if test_failures:
        failure_message = "\n".join(test_failures)
        logger.error(f"Test 8 completed with failures:\n{failure_message}")
        assert False, f"Some test cases failed. Check the log for details:\n{failure_message}"
    else:
        logger.info("Test 8 completed successfully")

@cocotb.test()
async def test9_write_read_sram(dut):
    """Test 9: Write and Read from the SRAM"""

    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 9: Write and Read from the SRAM")

    # Retrieve ADDR_WIDTH and DATA_WIDTH from DUT parameters
    ADDR_WIDTH = int(dut.ADDR_WIDTH.value)
    DATA_WIDTH = int(dut.DATA_WIDTH.value)

    # Start the clocks
    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_dsp, 1, units="ns").start())

    # Reset
    dut.PRESETn.value = 0
    dut.en_clk_dsp.value = 0
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.PRESETn.value = 1

    # Wait for reset deassertion
    await RisingEdge(dut.PCLK)

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000008
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)
    
    # Perform APB write to ADDRESS_WDATA
    write_data = 0xA4A4A5A5  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_WDATA'], write_data)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000001  # Write the control mode (1 -> SRAM_WRITE)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000002  # Write the control mode (2 -> SRAM_READ)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)
    
    # Wait for CDC synchronization
    await RisingEdge(dut.PCLK)
    await RisingEdge(dut.PCLK)
    await RisingEdge(dut.PCLK)

    # Perform APB read from ADDRESS_SRAM_ADDR
    read_data = await apb_read(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'])

    await RisingEdge(dut.PCLK)

    expected_data = write_data
    actual_data = read_data
    
    # Initialize list to collect failures
    test_failures = []

    # Check Data Output Register
    check_condition(
        actual_data == expected_data,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data}, "
        f"Got: 0x{actual_data}",
        f"PASS: Data Output Register value: 0x{actual_data}",
        test_failures
    )

@cocotb.test()
async def test10_perform_dsp_op(dut):
    """Test 10: Perform a DSP Operation"""

    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 10: Perform a DSP Operation")

    # Retrieve ADDR_WIDTH and DATA_WIDTH from DUT parameters
    ADDR_WIDTH = int(dut.ADDR_WIDTH.value)
    DATA_WIDTH = int(dut.DATA_WIDTH.value)

    # Start the clocks
    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_dsp, 1, units="ns").start())

    # Reset
    dut.PRESETn.value = 0
    dut.en_clk_dsp.value = 0
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.PRESETn.value = 1

    # Wait for reset deassertion
    await RisingEdge(dut.PCLK)

    # Perform APB write to ADDRESS_A
    write_data = 0x00000002  # Write address for operand A
    await apb_write(dut, APB_ADDRESSES['ADDRESS_A'], write_data)

    # Perform APB write to ADDRESS_B
    write_data = 0x00000004  # Write address for operand B
    await apb_write(dut, APB_ADDRESSES['ADDRESS_B'], write_data)
    
    # Perform APB write to ADDRESS_C
    write_data = 0x00000006  # Write address for operand C
    await apb_write(dut, APB_ADDRESSES['ADDRESS_C'], write_data)
    
    # Perform APB write to ADDRESS_O
    write_data = 0x00000007  # Write address for operand O
    await apb_write(dut, APB_ADDRESSES['ADDRESS_O'], write_data)

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000002
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)
    
    # Perform APB write to ADDRESS_WDATA
    write_data_a = 0x00000005  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_WDATA'], write_data_a)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000001  # Write the control mode (1 -> SRAM_WRITE)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000004
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)
    
    # Perform APB write to ADDRESS_WDATA
    write_data_b = 0x00000008  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_WDATA'], write_data_b)

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000006
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)
    
    # Perform APB write to ADDRESS_WDATA
    write_data_c = 0x00000003  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_WDATA'], write_data_c)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000003  # Write the control mode (3 -> DSP_READ_OP_A)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Wait for DSP operation
    await RisingEdge(dut.PCLK)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000004  # Write the control mode (4 -> DSP_READ_OP_B)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Wait for DSP operation
    await RisingEdge(dut.PCLK)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000005  # Write the control mode (5 -> DSP_READ_OP_C)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Wait for DSP operation
    await RisingEdge(dut.PCLK)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000006  # Write the control mode (6 -> DSP_WRITE_OP_O)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000007
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000002  # Write the control mode (2 -> SRAM_READ)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Wait for CDC synchronization
    await RisingEdge(dut.PCLK)
    await RisingEdge(dut.PCLK)
    await RisingEdge(dut.PCLK)

    # Perform APB read from ADDRESS_SRAM_ADDR
    read_data = await apb_read(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'])

    await RisingEdge(dut.PCLK)

    expected_data = (write_data_a * write_data_b) + write_data_c
    actual_data = read_data

    # Initialize list to collect failures
    test_failures = []

    # Check Data Output Register
    check_condition(
        actual_data == expected_data,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data}, "
        f"Got: 0x{actual_data}",
        f"PASS: Data Output Register value: 0x{actual_data}",
        test_failures
    )

@cocotb.test()
async def test11_sram_apb_op(dut):
    """Test 11: Perform a SRAM and APB Operation"""

    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 11: Perform a SRAM and APB Operation")

    # Retrieve ADDR_WIDTH and DATA_WIDTH from DUT parameters
    ADDR_WIDTH = int(dut.ADDR_WIDTH.value)
    DATA_WIDTH = int(dut.DATA_WIDTH.value)

    # Start the clocks
    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_dsp, 1, units="ns").start())

    # Reset
    dut.PRESETn.value = 0
    dut.en_clk_dsp.value = 1
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.PRESETn.value = 1

    # Wait for reset deassertion
    await RisingEdge(dut.PCLK)

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x0000003F
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)
    
    # Perform APB write to ADDRESS_WDATA
    write_data_sram = 0x0F0F0F0F  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_WDATA'], write_data_sram)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000001  # Write the control mode (1 -> SRAM_WRITE)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)
    
    # Perform APB write to ADDRESS_A while SRAM writes the data
    write_data_apb = 0x000FF000  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_A'], write_data_apb)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000002  # Write the control mode (2 -> SRAM_READ)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB read from SRAM address
    read_data_sram = await apb_read(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'])

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000000
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB read from ADDRESS_A
    read_data_apb = await apb_read(dut, APB_ADDRESSES['ADDRESS_A'])

    expected_data_sram = write_data_sram
    actual_data_sram = read_data_sram

    expected_data_apb = write_data_apb
    actual_data_apb = read_data_apb

    await RisingEdge(dut.PCLK)

    # Initialize list to collect failures
    test_failures = []

    # Check Data Read from SRAM
    check_condition(
        actual_data_sram == expected_data_sram,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data_sram}, "
        f"Got: 0x{actual_data_sram}",
        f"PASS: Data Output Register value: 0x{actual_data_sram}",
        test_failures
    )

    # Check Data Read from APB
    check_condition(
        actual_data_apb == expected_data_apb,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data_apb}, "
        f"Got: 0x{actual_data_apb}",
        f"PASS: Data Output Register value: 0x{actual_data_apb}",
        test_failures
    )

    # Report failures if any
    if test_failures:
        failure_message = "\n".join(test_failures)
        logger.error(f"Test 11 completed with failures:\n{failure_message}")
        assert False, f"Some test cases failed. Check the log for details:\n{failure_message}"
    else:
        logger.info("Test 11 completed successfully")

@cocotb.test()
async def test12_dsp_apb_op(dut):
    """Test 12: Perform a DSP and APB Operation"""

    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 12: Perform a DSP and APB Operation")

    # Retrieve ADDR_WIDTH and DATA_WIDTH from DUT parameters
    ADDR_WIDTH = int(dut.ADDR_WIDTH.value)
    DATA_WIDTH = int(dut.DATA_WIDTH.value)

    # Start the clocks
    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_dsp, 1, units="ns").start())

    # Reset
    dut.PRESETn.value = 0
    dut.en_clk_dsp.value = 1
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.PRESETn.value = 1

    # Wait for reset deassertion
    await RisingEdge(dut.PCLK)

    # Perform APB write to ADDRESS_A
    write_data = 0x00000000  # Write address for operand A
    await apb_write(dut, APB_ADDRESSES['ADDRESS_A'], write_data)

    # Perform APB write to ADDRESS_B
    write_data = 0x00000001  # Write address for operand B
    await apb_write(dut, APB_ADDRESSES['ADDRESS_B'], write_data)
    
    # Perform APB write to ADDRESS_C
    write_data = 0x00000002  # Write address for operand C
    await apb_write(dut, APB_ADDRESSES['ADDRESS_C'], write_data)
    
    # Perform APB write to ADDRESS_O
    write_data = 0x0000000F  # Write address for operand O
    await apb_write(dut, APB_ADDRESSES['ADDRESS_O'], write_data)

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000000
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)
    
    # Perform APB write to ADDRESS_WDATA
    write_data_a = 0x0000000A  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_WDATA'], write_data_a)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000001  # Write the control mode (1 -> SRAM_WRITE)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000001
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)
    
    # Perform APB write to ADDRESS_WDATA
    write_data_b = 0x00000011  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_WDATA'], write_data_b)

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000002
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)
    
    # Perform APB write to ADDRESS_WDATA
    write_data_c = 0x00000008  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_WDATA'], write_data_c)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000003  # Write the control mode (3 -> DSP_READ_OP_A)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000004  # Write the control mode (4 -> DSP_READ_OP_B)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000005  # Write the control mode (5 -> DSP_READ_OP_C)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000006  # Write the control mode (6 -> DSP_WRITE_OP_O)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

     # Perform APB write to ADDRESS_C while SRAM writes the data
    write_data_apb = 0x00FFFF00  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_C'], write_data_apb)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000002  # Write the control mode (2 -> SRAM_READ)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x0000000F
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)

    # Perform APB read from SRAM address
    read_data_dsp = await apb_read(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'])

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000000
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB read from ADDRESS_C
    read_data_apb = await apb_read(dut, APB_ADDRESSES['ADDRESS_C'])

    expected_data_dsp = (write_data_a * write_data_b) + write_data_c
    actual_data_dsp = read_data_dsp

    expected_data_apb = write_data_apb
    actual_data_apb = read_data_apb

    await RisingEdge(dut.PCLK)

    # Initialize list to collect failures
    test_failures = []

    # Check Data Read from SRAM
    check_condition(
        actual_data_dsp == expected_data_dsp,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data_dsp}, "
        f"Got: 0x{actual_data_dsp}",
        f"PASS: Data Output Register value: 0x{actual_data_dsp}",
        test_failures
    )

    # Check Data Read from APB
    check_condition(
        actual_data_apb == expected_data_apb,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data_apb}, "
        f"Got: 0x{actual_data_apb}",
        f"PASS: Data Output Register value: 0x{actual_data_apb}",
        test_failures
    )

    # Report failures if any
    if test_failures:
        failure_message = "\n".join(test_failures)
        logger.error(f"Test 12 completed with failures:\n{failure_message}")
        assert False, f"Some test cases failed. Check the log for details:\n{failure_message}"
    else:
        logger.info("Test 12 completed successfully")

@cocotb.test()
async def test13_invalid_sram_address(dut):
    """Test 13: Attempt to Access an Invalid SRAM Address"""

    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 13: Attempt to Access an Invalid SRAM Address")

    # Start the clocks
    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_dsp, 1, units="ns").start())

    # Reset
    dut.PRESETn.value = 0
    dut.en_clk_dsp.value = 0
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.PRESETn.value = 1

    # Wait for reset deassertion
    await RisingEdge(dut.PCLK)

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000040
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)
    
    # Perform APB write to ADDRESS_WDATA
    write_data = 0xDEADBEEF  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_WDATA'], write_data)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000001  # Write the control mode (1 -> SRAM_WRITE)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)
    
    # Wait for CDC synchronization
    await RisingEdge(dut.PCLK)
    dut.PSEL.value = 1
    dut.PENABLE.value = 1

    await RisingEdge(dut.PCLK)
    received_PSLVERR = dut.PSLVERR
    
    # Initialize list to collect failures
    test_failures = []

    # Check that invalid SRAM address triggers PSLVERR
    check_condition(
        received_PSLVERR == 1,
        f"FAIL: Invalid address should raise PSLVERR. Expected: {1}, Got: {received_PSLVERR}",
        "PASS: Invalid address access raised PSLVERR as expected",
        test_failures
    )

@cocotb.test()
async def test14_multiple_dsp_op(dut):
    """Test 14: Perform Multiple DSP Operations to Check Pipelining Behavior"""

    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 14: Perform Multiple DSP Operations to Check Pipelining Behavior")

    # Start the clocks
    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_dsp, 1, units="ns").start())

    # Reset
    dut.PRESETn.value = 0
    dut.en_clk_dsp.value = 1
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.PRESETn.value = 1

    # Wait for reset deassertion
    await RisingEdge(dut.PCLK)

    # Perform APB write to ADDRESS_A
    write_data = 0x00000000  # Write address for operand A
    await apb_write(dut, APB_ADDRESSES['ADDRESS_A'], write_data)

    # Perform APB write to ADDRESS_B
    write_data = 0x00000001  # Write address for operand B
    await apb_write(dut, APB_ADDRESSES['ADDRESS_B'], write_data)
    
    # Perform APB write to ADDRESS_C
    write_data = 0x00000002  # Write address for operand C
    await apb_write(dut, APB_ADDRESSES['ADDRESS_C'], write_data)
    
    # Perform APB write to ADDRESS_O
    write_data = 0x00000003  # Write address for operand O
    await apb_write(dut, APB_ADDRESSES['ADDRESS_O'], write_data)

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000000
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)
    
    # Perform APB write to ADDRESS_WDATA
    write_data_a = 0x00000004  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_WDATA'], write_data_a)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000001  # Write the control mode (1 -> SRAM_WRITE)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000001
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)
    
    # Perform APB write to ADDRESS_WDATA
    write_data_b = 0x00000004  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_WDATA'], write_data_b)

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000002
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)
    
    # Perform APB write to ADDRESS_WDATA
    write_data_c = 0x00000000  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_WDATA'], write_data_c)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000003  # Write the control mode (3 -> DSP_READ_OP_A)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000004  # Write the control mode (4 -> DSP_READ_OP_B)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000005  # Write the control mode (5 -> DSP_READ_OP_C)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000006  # Write the control mode (6 -> DSP_WRITE_OP_O)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Second DSP Operation

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000002
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)
    
    # Perform APB write to ADDRESS_WDATA
    write_data_c_snd = 0x000000F0  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_WDATA'], write_data_c_snd)
    
    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000001  # Write the control mode (1 -> SRAM_WRITE)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

     # Perform APB write to ADDRESS_O while SRAM writes the data
    write_data_apb = 0x00000004  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_O'], write_data_apb)
    
    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000005  # Write the control mode (5 -> DSP_READ_OP_C)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000006  # Write the control mode (6 -> DSP_WRITE_OP_O)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Third DSP Operation

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000002
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)
    
    # Perform APB write to ADDRESS_WDATA
    write_data_c_trd = 0x00000FF0  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_WDATA'], write_data_c_trd)
    
    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000001  # Write the control mode (1 -> SRAM_WRITE)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

     # Perform APB write to ADDRESS_O while SRAM writes the data
    write_data_apb = 0x00000005  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_O'], write_data_apb)
    
    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000005  # Write the control mode (5 -> DSP_READ_OP_C)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000006  # Write the control mode (6 -> DSP_WRITE_OP_O)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Read first DSP operation

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000002  # Write the control mode (2 -> SRAM_READ)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000003
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)

    # Perform APB read from SRAM address
    read_data_dsp = await apb_read(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'])

    expected_data_fst = (write_data_a * write_data_b) + write_data_c
    actual_data_fst = read_data_dsp

    # Read second DSP operation

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000004
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)

    # Perform APB read from SRAM address
    read_data_dsp = await apb_read(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'])

    expected_data_snd = (write_data_a * write_data_b) + write_data_c_snd
    actual_data_snd = read_data_dsp

    # Read third DSP operation

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000005
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)

    # Perform APB read from SRAM address
    read_data_dsp = await apb_read(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'])

    expected_data_trd = (write_data_a * write_data_b) + write_data_c_trd
    actual_data_trd = read_data_dsp


    await RisingEdge(dut.PCLK)

    # Initialize list to collect failures
    test_failures = []

    # Check Data Read from first DSP operation
    check_condition(
        actual_data_fst == expected_data_fst,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data_fst}, "
        f"Got: 0x{actual_data_fst}",
        f"PASS: Data Output Register value: 0x{actual_data_fst}",
        test_failures
    )

    # Check Data Read from second DSP operation
    check_condition(
        actual_data_snd == expected_data_snd,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data_snd}, "
        f"Got: 0x{actual_data_snd}",
        f"PASS: Data Output Register value: 0x{actual_data_snd}",
        test_failures
    )

    # Check Data Read from third DSP operation
    check_condition(
        actual_data_trd == expected_data_trd,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data_trd}, "
        f"Got: 0x{actual_data_trd}",
        f"PASS: Data Output Register value: 0x{actual_data_trd}",
        test_failures
    )

    # Report failures if any
    if test_failures:
        failure_message = "\n".join(test_failures)
        logger.error(f"Test 14 completed with failures:\n{failure_message}")
        assert False, f"Some test cases failed. Check the log for details:\n{failure_message}"
    else:
        logger.info("Test 14 completed successfully")

@cocotb.test()
async def test15_write_sram_while_read(dut):
    """Test 15: Write to SRAM while an ongoing read is in progress"""

    logger = dut._log
    logger.setLevel(logging.INFO)
    logger.info("Test 15: Write to SRAM while an ongoing read is in progress")

    # Start the clocks
    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_dsp, 1, units="ns").start())

    # Reset
    dut.PRESETn.value = 0
    dut.en_clk_dsp.value = 0
    await Timer(50, units='ns')  # Hold reset low for 50 ns
    dut.PRESETn.value = 1

    # Wait for reset deassertion
    await RisingEdge(dut.PCLK)

    # Perform APB write to ADDRESS_SRAM_ADDR
    sram_addr = 0x00000008
    await apb_write(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'], sram_addr)
    
    # Perform APB write to ADDRESS_WDATA
    write_data_1 = 0x00000001  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_WDATA'], write_data_1)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000001  # Write the control mode (1 -> SRAM_WRITE)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000002  # Write the control mode (2 -> SRAM_READ)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)
    
    # Perform APB write to ADDRESS_WDATA (while configured to read first value from SRAM)
    write_data_2 = 0x00000002  # Write a pattern
    await apb_write(dut, APB_ADDRESSES['ADDRESS_WDATA'], write_data_2)

    # Wait for CDC synchronization
    await RisingEdge(dut.PCLK)

    # Perform APB read from ADDRESS_SRAM_ADDR
    read_data = await apb_read(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'])

    expected_data_1 = write_data_1
    actual_data_1 = read_data

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000001  # Write the control mode (1 -> SRAM_WRITE)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)

    # Perform APB write to ADDRESS_CONTROL
    control_mode = 0x00000002  # Write the control mode (2 -> SRAM_READ)
    await apb_write(dut, APB_ADDRESSES['ADDRESS_CONTROL'], control_mode)
    
    # Wait for CDC synchronization
    await RisingEdge(dut.PCLK)
    await RisingEdge(dut.PCLK)
    await RisingEdge(dut.PCLK)

    # Perform APB read from ADDRESS_SRAM_ADDR
    read_data = await apb_read(dut, APB_ADDRESSES['ADDRESS_SRAM_ADDR'])

    expected_data_2 = write_data_2
    actual_data_2 = read_data

    await RisingEdge(dut.PCLK)
    
    # Initialize list to collect failures
    test_failures = []

    # Check Data Output Register 1
    check_condition(
        actual_data_1 == expected_data_1,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data_1}, "
        f"Got: 0x{actual_data_1}",
        f"PASS: Data Output Register value: 0x{actual_data_1}",
        test_failures
    )

    # Check Data Output Register 2
    check_condition(
        actual_data_2 == expected_data_2,
        f"FAIL: Data Output Register mismatch. Expected: 0x{expected_data_2}, "
        f"Got: 0x{actual_data_2}",
        f"PASS: Data Output Register value: 0x{actual_data_2}",
        test_failures
    )

    # Report failures if any
    if test_failures:
        failure_message = "\n".join(test_failures)
        logger.error(f"Test 15 completed with failures:\n{failure_message}")
        assert False, f"Some test cases failed. Check the log for details:\n{failure_message}"
    else:
        logger.info("Test 15 completed successfully")