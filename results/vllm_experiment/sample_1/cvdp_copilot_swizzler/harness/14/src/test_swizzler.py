import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
from cocotb.result import TestFailure

@cocotb.test()
async def test_tc1_identity_mapping(dut):
    """
    Test Case 1: Identity Mapping (operation_mode=000)
    - data_in = 0xAA (10101010)
    - mapping_in = 0x01234567 (identity mapping for N=8)
    - config_in = 1
    - operation_mode = 0b000 (Swizzle Only)
    - Expected data_out = 0xAA
    - Expected error_flag = 0
    """
    # Initialize inputs
    dut.reset.value = 0  # Ensure reset is not asserted initially
    dut.data_in.value = 0
    dut.mapping_in.value = 0
    dut.config_in.value = 1
    dut.operation_mode.value = 0

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # 100MHz clock

    # Apply reset (active high)
    dut.reset.value = 1  # Assert reset
    await RisingEdge(dut.clk)
    dut.reset.value = 0  # De-assert reset
    dut._log.info("TC1: Reset de-asserted")

    # Apply Test Inputs
    dut.data_in.value = 0xAA  # 0b10101010
    dut.mapping_in.value = 0x01234567  # Identity mapping for N=8
    dut.config_in.value = 1
    dut.operation_mode.value = 0b000

    # Wait for 4 clock cycles to allow data propagation
    for cycle in range(4):
        await RisingEdge(dut.clk)
        dut._log.info(f"TC1 - Cycle {cycle+1}")

    # Verify Output
    data_out = dut.data_out.value.integer
    error_flag = dut.error_flag.value.integer
    assert data_out == 0xAA, f"TC1 FAIL: Expected data_out=0xAA, Got=0x{data_out:02X}"
    assert error_flag == 0, f"TC1 FAIL: Expected error_flag=0, Got={error_flag}"
    dut._log.info("TC1 PASS: Swizzle (Identity Mapping)")

@cocotb.test()
async def test_tc2_reverse_mapping(dut):
    """
    Test Case 2: Reverse Mapping (operation_mode=000)
    - data_in = 0xAA (10101010)
    - mapping_in = 0x76543210 (reverse mapping for N=8)
    - config_in = 1
    - operation_mode = 0b000 (Swizzle Only)
    - Expected data_out = 0x55 (01010101)
    - Expected error_flag = 0
    """
    # Initialize inputs
    dut.reset.value = 0  # Ensure reset is not asserted initially
    dut.data_in.value = 0
    dut.mapping_in.value = 0
    dut.config_in.value = 1
    dut.operation_mode.value = 0

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # 100MHz clock

    # Apply reset (active high)
    dut.reset.value = 1  # Assert reset
    await RisingEdge(dut.clk)
    dut.reset.value = 0  # De-assert reset
    dut._log.info("TC2: Reset de-asserted")

    # Apply Test Inputs
    dut.data_in.value = 0xAA  # 0b10101010
    dut.mapping_in.value = 0x76543210  # Reverse mapping for N=8
    dut.config_in.value = 1
    dut.operation_mode.value = 0b000

    # Wait for 4 clock cycles to allow data propagation
    for cycle in range(4):
        await RisingEdge(dut.clk)
        dut._log.info(f"TC2 - Cycle {cycle+1}")

    # Verify Output
    data_out = dut.data_out.value.integer
    error_flag = dut.error_flag.value.integer
    assert data_out == 0x55, f"TC2 FAIL: Expected data_out=0x55, Got=0x{data_out:02X}"
    assert error_flag == 0, f"TC2 FAIL: Expected error_flag=0, Got={error_flag}"
    dut._log.info("TC2 PASS: Swizzle (Reverse Mapping)")

@cocotb.test()
async def test_tc3_passthrough(dut):
    """
    Test Case 3: Passthrough (operation_mode=001)
    - data_in = 0x55 (01010101)
    - mapping_in = 0x01234567 (identity mapping for N=8)
    - config_in = 1
    - operation_mode = 0b001 (Passthrough)
    - Expected data_out = 0x55
    - Expected error_flag = 0
    """
    # Initialize inputs
    dut.reset.value = 0  # Ensure reset is not asserted initially
    dut.data_in.value = 0
    dut.mapping_in.value = 0
    dut.config_in.value = 1
    dut.operation_mode.value = 0

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # 100MHz clock

    # Apply reset (active high)
    dut.reset.value = 1  # Assert reset
    await RisingEdge(dut.clk)
    dut.reset.value = 0  # De-assert reset
    dut._log.info("TC3: Reset de-asserted")

    # Apply Test Inputs
    dut.data_in.value = 0x55  # 0b01010101
    dut.mapping_in.value = 0x01234567  # Identity mapping for N=8
    dut.config_in.value = 1
    dut.operation_mode.value = 0b001

    # Wait for 4 clock cycles to allow data propagation
    for cycle in range(4):
        await RisingEdge(dut.clk)
        dut._log.info(f"TC3 - Cycle {cycle+1}")

    # Verify Output
    data_out = dut.data_out.value.integer
    error_flag = dut.error_flag.value.integer
    assert data_out == 0x55, f"TC3 FAIL: Expected data_out=0x55, Got=0x{data_out:02X}"
    assert error_flag == 0, f"TC3 FAIL: Expected error_flag=0, Got={error_flag}"
    dut._log.info("TC3 PASS: Passthrough")

@cocotb.test()
async def test_tc4_reverse_data(dut):
    """
    Test Case 4: Reverse Data (operation_mode=010)
    - data_in = 0x55 (01010101)
    - mapping_in = 0x01234567 (identity mapping for N=8)
    - config_in = 1
    - operation_mode = 0b010 (Reverse Data)
    - Expected data_out = 0xAA (10101010)
    - Expected error_flag = 0
    """
    # Initialize inputs
    dut.reset.value = 0  # Ensure reset is not asserted initially
    dut.data_in.value = 0
    dut.mapping_in.value = 0
    dut.config_in.value = 1
    dut.operation_mode.value = 0

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # 100MHz clock

    # Apply reset (active high)
    dut.reset.value = 1  # Assert reset
    await RisingEdge(dut.clk)
    dut.reset.value = 0  # De-assert reset
    dut._log.info("TC4: Reset de-asserted")

    # Apply Test Inputs
    dut.data_in.value = 0x55  # 0b01010101
    dut.mapping_in.value = 0x01234567  # Identity mapping for N=8
    dut.config_in.value = 1
    dut.operation_mode.value = 0b010

    # Wait for 4 clock cycles to allow data propagation
    for cycle in range(4):
        await RisingEdge(dut.clk)
        dut._log.info(f"TC4 - Cycle {cycle+1}")

    # Verify Output
    data_out = dut.data_out.value.integer
    error_flag = dut.error_flag.value.integer
    assert data_out == 0xAA, f"TC4 FAIL: Expected data_out=0xAA, Got=0x{data_out:02X}"
    assert error_flag == 0, f"TC4 FAIL: Expected error_flag=0, Got={error_flag}"
    dut._log.info("TC4 PASS: Reverse Data")

@cocotb.test()
async def test_tc5_swap_halves(dut):
    """
    Test Case 5: Swap Halves (operation_mode=011)
    - data_in = 0xAA (10101010)
    - mapping_in = 0x01234567 (identity mapping for N=8)
    - config_in = 1
    - operation_mode = 0b011 (Swap Halves)
    - Expected data_out = 0xAA (10101010)
    - Expected error_flag = 0
    """
    # Initialize inputs
    dut.reset.value = 0  # Ensure reset is not asserted initially
    dut.data_in.value = 0
    dut.mapping_in.value = 0
    dut.config_in.value = 1
    dut.operation_mode.value = 0

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # 100MHz clock

    # Apply reset (active high)
    dut.reset.value = 1  # Assert reset
    await RisingEdge(dut.clk)
    dut.reset.value = 0  # De-assert reset
    dut._log.info("TC5: Reset de-asserted")

    # Apply Test Inputs
    dut.data_in.value = 0xAA  # 0b10101010
    dut.mapping_in.value = 0x01234567  # Identity mapping for N=8
    dut.config_in.value = 1
    dut.operation_mode.value = 0b011

    # Wait for 4 clock cycles to allow data propagation
    for cycle in range(4):
        await RisingEdge(dut.clk)
        dut._log.info(f"TC5 - Cycle {cycle+1}")

    # Verify Output
    data_out = dut.data_out.value.integer
    error_flag = dut.error_flag.value.integer
    assert data_out == 0xAA, f"TC5 FAIL: Expected data_out=0xAA, Got=0x{data_out:02X}"
    assert error_flag == 0, f"TC5 FAIL: Expected error_flag=0, Got={error_flag}"
    dut._log.info("TC5 PASS: Swap Halves")

@cocotb.test()
async def test_tc6_bitwise_inversion(dut):
    """
    Test Case 6: Bitwise Inversion (operation_mode=100)
    - data_in = 0xAA (10101010)
    - mapping_in = 0x01234567 (identity mapping for N=8)
    - config_in = 1
    - operation_mode = 0b100 (Bitwise Inversion)
    - Expected data_out = 0x55 (01010101)
    - Expected error_flag = 0
    """
    # Initialize inputs
    dut.reset.value = 0  # Ensure reset is not asserted initially
    dut.data_in.value = 0
    dut.mapping_in.value = 0
    dut.config_in.value = 1
    dut.operation_mode.value = 0

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # 100MHz clock

    # Apply reset (active high)
    dut.reset.value = 1  # Assert reset
    await RisingEdge(dut.clk)
    dut.reset.value = 0  # De-assert reset
    dut._log.info("TC6: Reset de-asserted")

    # Apply Test Inputs
    dut.data_in.value = 0xAA  # 0b10101010
    dut.mapping_in.value = 0x01234567  # Identity mapping for N=8
    dut.config_in.value = 1
    dut.operation_mode.value = 0b100

    # Wait for 4 clock cycles to allow data propagation
    for cycle in range(4):
        await RisingEdge(dut.clk)
        dut._log.info(f"TC6 - Cycle {cycle+1}")

    # Verify Output
    data_out = dut.data_out.value.integer
    error_flag = dut.error_flag.value.integer
    assert data_out == 0x55, f"TC6 FAIL: Expected data_out=0x55, Got=0x{data_out:02X}"
    assert error_flag == 0, f"TC6 FAIL: Expected error_flag=0, Got={error_flag}"
    dut._log.info("TC6 PASS: Bitwise Inversion")

@cocotb.test()
async def test_tc7_circular_left_shift(dut):
    """
    Test Case 7: Circular Left Shift (operation_mode=101)
    - data_in = 0xAA (10101010)
    - mapping_in = 0x01234567 (identity mapping for N=8)
    - config_in = 1
    - operation_mode = 0b101 (Circular Left Shift)
    - Expected data_out = 0x55 (01010101)
    - Expected error_flag = 0
    """
    # Initialize inputs
    dut.reset.value = 0  # Ensure reset is not asserted initially
    dut.data_in.value = 0
    dut.mapping_in.value = 0
    dut.config_in.value = 1
    dut.operation_mode.value = 0

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # 100MHz clock

    # Apply reset (active high)
    dut.reset.value = 1  # Assert reset
    await RisingEdge(dut.clk)
    dut.reset.value = 0  # De-assert reset
    dut._log.info("TC7: Reset de-asserted")

    # Apply Test Inputs
    dut.data_in.value = 0xAA  # 0b10101010
    dut.mapping_in.value = 0x01234567  # Identity mapping for N=8
    dut.config_in.value = 1
    dut.operation_mode.value = 0b101

    # Wait for 4 clock cycles to allow data propagation
    for cycle in range(4):
        await RisingEdge(dut.clk)
        dut._log.info(f"TC7 - Cycle {cycle+1}")

    # Verify Output
    data_out = dut.data_out.value.integer
    error_flag = dut.error_flag.value.integer
    expected = ((0xAA << 1) | (0xAA >> (8-1))) & 0xFF  # Circular left shift by 1
    assert data_out == expected, f"TC7 FAIL: Expected data_out=0x{expected:02X}, Got=0x{data_out:02X}"
    assert error_flag == 0, f"TC7 FAIL: Expected error_flag=0, Got={error_flag}"
    dut._log.info("TC7 PASS: Circular Left Shift")

@cocotb.test()
async def test_tc8_circular_right_shift(dut):
    """
    Test Case 8: Circular Right Shift (operation_mode=110)
    - data_in = 0xAA (10101010)
    - mapping_in = 0x01234567 (identity mapping for N=8)
    - config_in = 1
    - operation_mode = 0b110 (Circular Right Shift)
    - Expected data_out = 0x55 (01010101)
    - Expected error_flag = 0
    """
    # Initialize inputs
    dut.reset.value = 0  # Ensure reset is not asserted initially
    dut.data_in.value = 0
    dut.mapping_in.value = 0
    dut.config_in.value = 1
    dut.operation_mode.value = 0

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # 100MHz clock

    # Apply reset (active high)
    dut.reset.value = 1  # Assert reset
    await RisingEdge(dut.clk)
    dut.reset.value = 0  # De-assert reset
    dut._log.info("TC8: Reset de-asserted")

    # Apply Test Inputs
    dut.data_in.value = 0xAA  # 0b10101010
    dut.mapping_in.value = 0x01234567  # Identity mapping for N=8
    dut.config_in.value = 1
    dut.operation_mode.value = 0b110

    # Wait for 4 clock cycles to allow data propagation
    for cycle in range(4):
        await RisingEdge(dut.clk)
        dut._log.info(f"TC8 - Cycle {cycle+1}")

    # Verify Output
    data_out = dut.data_out.value.integer
    error_flag = dut.error_flag.value.integer
    expected = ((0xAA >> 1) | (0xAA << (8-1))) & 0xFF  # Circular right shift by 1
    assert data_out == expected, f"TC8 FAIL: Expected data_out=0x{expected:02X}, Got=0x{data_out:02X}"
    assert error_flag == 0, f"TC8 FAIL: Expected error_flag=0, Got={error_flag}"
    dut._log.info("TC8 PASS: Circular Right Shift")

@cocotb.test()
async def test_tc9_invalid_mapping(dut):
    """
    Test Case 9: Invalid Mapping
    - data_in = 0xAA (10101010)
    - mapping_in = 0x81234567 (invalid mapping for lane 7: index=8 >= N=8)
    - config_in = 1
    - operation_mode = 0b000 (Swizzle Only)
    - Expected data_out = 0x00 (all zeros due to invalid mapping)
    - Expected error_flag = 1
    """
    # Initialize inputs
    dut.reset.value = 0  # Ensure reset is not asserted initially
    dut.data_in.value = 0
    dut.mapping_in.value = 0
    dut.config_in.value = 1
    dut.operation_mode.value = 0

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # 100MHz clock

    # Apply reset (active high)
    dut.reset.value = 1  # Assert reset
    await RisingEdge(dut.clk)
    dut.reset.value = 0  # De-assert reset
    dut._log.info("TC9: Reset de-asserted")

    # Apply Test Inputs
    dut.data_in.value = 0xAA  # 0b10101010
    dut.mapping_in.value = 0x81234567  # Invalid mapping: lane 7 maps to index=8
    dut.config_in.value = 1
    dut.operation_mode.value = 0b000

    # Wait for 4 clock cycles to allow data propagation
    for cycle in range(4):
        await RisingEdge(dut.clk)
        dut._log.info(f"TC9 - Cycle {cycle+1}")

    # Verify Output
    data_out = dut.data_out.value.integer
    error_flag = dut.error_flag.value.integer
    assert data_out == 0x00, f"TC9 FAIL: Expected data_out=0x00, Got=0x{data_out:02X}"
    assert error_flag == 1, f"TC9 FAIL: Expected error_flag=1, Got={error_flag}"
    dut._log.info("TC9 PASS: Invalid Mapping")
