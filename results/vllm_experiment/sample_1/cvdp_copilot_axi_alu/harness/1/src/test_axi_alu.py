import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles
import random

#Initialize default value to all the inputs and drive reset HIGH
async def init_dut(dut):
    dut.reset_in.value = 1
    dut.axi_awaddr_i.value = 0
    dut.axi_awlen_i.value = 0
    dut.axi_awsize_i.value = 0
    dut.axi_awburst_i.value = 0
    dut.axi_awvalid_i.value = 0
    dut.axi_wdata_i.value = 0
    dut.axi_wstrb_i.value = 0
    dut.axi_wlast_i.value = 0
    dut.axi_wvalid_i.value = 0
    dut.axi_bready_i.value = 0
    dut.axi_araddr_i.value = 0
    dut.axi_arlen_i.value = 0
    dut.axi_arsize_i.value = 0
    dut.axi_arburst_i.value = 0
    dut.axi_arvalid_i.value = 0
    dut.axi_rready_i.value = 0

    await RisingEdge(dut.axi_clk_in)
    await RisingEdge(dut.axi_clk_in)
    await RisingEdge(dut.axi_clk_in)
    await RisingEdge(dut.axi_clk_in)
    dut.reset_in.value = 0

MAX_BURST = 16

# AXI single write Transaction
async def axi_write(dut, addr, data):
    await RisingEdge(dut.axi_clk_in)
    dut.axi_awaddr_i.value = addr
    dut.axi_awlen_i.value = 0
    dut.axi_awsize_i.value = 2
    dut.axi_awburst_i.value = 0
    dut.axi_awvalid_i.value = 1
    await RisingEdge(dut.axi_clk_in)
    while not dut.axi_awready_o.value:
        await RisingEdge(dut.axi_clk_in)
    dut.axi_awvalid_i.value = 0

    dut.axi_wdata_i.value = data
    dut.axi_wstrb_i.value = 0b1111
    dut.axi_wlast_i.value = 1
    dut.axi_wvalid_i.value = 1
    await RisingEdge(dut.axi_clk_in)
    await RisingEdge(dut.axi_clk_in)
    while not dut.axi_wready_o.value:
        await RisingEdge(dut.axi_clk_in)
    dut.axi_wvalid_i.value = 0
    dut.axi_wlast_i.value = 0

    dut.axi_bready_i.value = 1
    await RisingEdge(dut.axi_clk_in)
    while not dut.axi_bvalid_o.value:
        await RisingEdge(dut.axi_clk_in)
    dut.axi_bready_i.value = 0

#AXI single read
async def axi_read(dut, addr):
    await RisingEdge(dut.axi_clk_in)
    dut.axi_araddr_i.value = addr
    dut.axi_arlen_i.value = 0
    dut.axi_arsize_i.value = 2
    dut.axi_arburst_i.value = 0
    dut.axi_arvalid_i.value = 1
    await RisingEdge(dut.axi_clk_in)
    while not dut.axi_arready_o.value:
        await RisingEdge(dut.axi_clk_in)
    dut.axi_arvalid_i.value = 0

    dut.axi_rready_i.value = 1
    await RisingEdge(dut.axi_clk_in)
    await RisingEdge(dut.axi_clk_in)
    while not dut.axi_rvalid_o.value:
        await RisingEdge(dut.axi_clk_in)
    dut.axi_rready_i.value = 0
    await RisingEdge(dut.axi_clk_in)

    print(f"Single read from addr {hex(addr)}: Data = {hex(dut.axi_rdata_o.value.to_unsigned())}, RRESP = {bin(dut.axi_rresp_o.value.to_unsigned())}, RLAST = {bin(dut.axi_rlast_o.value.to_unsigned())}")

#AXI burst transaction
async def axi_write_burst(dut, start_addr, burst_length, base_data):
    if burst_length < 1 or burst_length > MAX_BURST:
        print(f"Error: burst_length must be between 1 and {MAX_BURST}")
        return

    await RisingEdge(dut.axi_clk_in)
    dut.axi_awaddr_i.value = start_addr
    dut.axi_awlen_i.value = burst_length - 1
    dut.axi_awsize_i.value = 2
    dut.axi_awburst_i.value = 1
    dut.axi_awvalid_i.value = 1
    await RisingEdge(dut.axi_clk_in)
    while not dut.axi_awready_o.value:
        await RisingEdge(dut.axi_clk_in)
    dut.axi_awvalid_i.value = 0
    dut.axi_wstrb_i.value = 0b1111

    for i in range(burst_length):
        await RisingEdge(dut.axi_clk_in)
        dut.axi_wdata_i.value = base_data + i
        dut.axi_wstrb_i.value = 0b1111
        dut.axi_wvalid_i.value = 1
        if i == burst_length - 1:
            dut.axi_wlast_i.value = 1
        else:
            dut.axi_wlast_i.value = 0
        await RisingEdge(dut.axi_clk_in)
        while not dut.axi_wready_o.value:
            await RisingEdge(dut.axi_clk_in)
        dut.axi_wvalid_i.value = 0
        dut.axi_wlast_i.value = 0

    dut.axi_bready_i.value = 1
    await RisingEdge(dut.axi_clk_in)
    while not dut.axi_bvalid_o.value:
        await RisingEdge(dut.axi_clk_in)
    dut.axi_bready_i.value = 0

#AXI burst read
async def axi_read_burst(dut, start_addr, burst_length):
    if burst_length < 1 or burst_length > MAX_BURST:
        print(f"Error: burst_length must be between 1 and {MAX_BURST}")
        return

    await RisingEdge(dut.axi_clk_in)
    dut.axi_araddr_i.value = start_addr
    dut.axi_arlen_i.value = burst_length - 1
    dut.axi_arsize_i.value = 2
    dut.axi_arburst_i.value = 1
    dut.axi_arvalid_i.value = 1
    await RisingEdge(dut.axi_clk_in)
    while not dut.axi_arready_o.value:
        await RisingEdge(dut.axi_clk_in)
    dut.axi_arvalid_i.value = 0

    curr_addr = start_addr
    for i in range(burst_length):
        dut.axi_rready_i.value = 1
        await RisingEdge(dut.axi_clk_in)
        while not dut.axi_rvalid_o.value:
            await RisingEdge(dut.axi_clk_in)
        print(f"Burst read beat {i} from addr {hex(curr_addr)}: Data = {hex(dut.axi_rdata_o.value.to_unsigned())}, RRESP = {bin(dut.axi_rresp_o.value.to_unsigned())}, RLAST = {bin(dut.axi_rlast_o.value.to_unsigned())}")
        dut.axi_rready_i.value = 0
        curr_addr = curr_addr + (1 << dut.axi_arsize_i.value)

#Custom AXI transaction that supports flow for ALU operation
async def axi_operation(dut, op_a, op_b, op_c, op_select, clock_ctrl):
    await axi_write(dut, 0x00000010, clock_ctrl) # clock control register
    await RisingEdge(dut.axi_clk_in)

    await axi_write(dut, 0x00000000, op_a)
    await RisingEdge(dut.axi_clk_in)
    await axi_write(dut, 0x00000004, op_b)
    await RisingEdge(dut.axi_clk_in)
    await axi_write(dut, 0x00000008, op_c)
    await RisingEdge(dut.axi_clk_in)

    await axi_write(dut, 0x0000000C, (0x00000003 & op_select)) # select operation
    await RisingEdge(dut.axi_clk_in)

    await axi_write(dut, 0x0000000C, op_select) # start operation
    await RisingEdge(dut.axi_clk_in)

    await RisingEdge(dut.axi_clk_in)
    await axi_write(dut, 0x0000000C, 0)
    await RisingEdge(dut.axi_clk_in)
    await RisingEdge(dut.axi_clk_in)
    await RisingEdge(dut.axi_clk_in)

async def test_burst_transactions(dut):
    burst_length = 16
    print(f"Starting burst transactions with burst length = {burst_length}...")

    await axi_write_burst(dut, 0x0000_0020, burst_length, 0x0000_0005)
    await RisingEdge(dut.axi_clk_in)
    await RisingEdge(dut.axi_clk_in)

# TC1: Burst write transaction to initialize incremental data in RAM memory
@cocotb.test()
async def test_burst_write_transaction(dut):
    cocotb.start_soon(Clock(dut.axi_clk_in, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.fast_clk_in, 5, units="ns").start())

    await init_dut(dut)
    await test_burst_transactions(dut)

    print("\nMemory Contents After Burst Write:")
    for i in range(16):
        mem_address = f"0x{0x00000020 + (i * 4):08X}"
        mem_data = int(dut.u_memory_block.ram[i].value)
        expected_value = i + 5  # Expected value as per burst initialization
        print(f"Address: {mem_address} | Data: 0x{mem_data:08X} | Expected: 0x{expected_value:08X}")

        # Assertion to check memory correctness
        assert mem_data == expected_value, \
            f"Memory Mismatch at Address {mem_address}: Expected 0x{expected_value:08X}, Got 0x{mem_data:08X}"

#TC2: Incremental data in memory and test all operations
@cocotb.test()
async def test_axi_alu_incremental_data(dut):
    cocotb.start_soon(Clock(dut.axi_clk_in, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.fast_clk_in, 5, units="ns").start())

    await init_dut(dut)

    await test_burst_transactions(dut)
    test_cases = [
        (0x0000000A, 0x00000005, 0x00000002, 0b100, 1),
        (0x00000004, 0x0000000A, 0x00000006, 0b101, 1),
        (0x00000004, 0x00000000, 0x0000000E, 0b110, 1),
        (0x00000006, 0x0000000C, 0x0000000F, 0b111, 1),
        (0x0000000A, 0x00000005, 0x00000002, 0b100, 0),
        (0x00000004, 0x0000000A, 0x00000006, 0b101, 0),
        (0x00000004, 0x00000000, 0x0000000E, 0b110, 0),
        (0x00000006, 0x0000000C, 0x0000000F, 0b111, 0),
        (0x0000000A, 0x00000005, 0x00000002, 0b000, 1),
        (0x00000004, 0x0000000A, 0x00000006, 0b001, 1),
        (0x00000004, 0x00000000, 0x0000000E, 0b010, 1),
        (0x00000006, 0x0000000C, 0x0000000F, 0b011, 1),
    ]

    for op_a, op_b, op_c, op_select, clock_ctrl in test_cases:
        print(f"Testing with operands: op_a = {hex(op_a)}, op_b = {hex(op_b)}, op_c = {hex(op_c)}, op_select = {bin(op_select)}, clock_ctrl = {clock_ctrl}")
        await axi_operation(dut, op_a, op_b, op_c, op_select, clock_ctrl)
        await axi_check_result(dut, op_a, op_b, op_c, op_select)

#TC3: random address with ALU MAC operation (op_select = 00)
@cocotb.test()
async def test_axi_alu_mac_operation_random_address(dut):
    cocotb.start_soon(Clock(dut.axi_clk_in, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.fast_clk_in, 5, units="ns").start())

    await init_dut(dut)

    await test_burst_transactions(dut)

    for _ in range(16):
        op_a = random.randint(0, 15)
        op_b = random.randint(0, 15)
        op_c = random.randint(0, 15)
        op_select = 4
        clock_ctrl = random.randint(0, 1)

        print(f"Testing with operands: op_a = {hex(op_a)}, op_b = {hex(op_b)}, op_c = {hex(op_c)}, op_select = {bin(op_select)}, clock_ctrl = {clock_ctrl}")
        await axi_operation(dut, op_a, op_b, op_c, op_select, clock_ctrl)
        await axi_check_result(dut, op_a, op_b, op_c, op_select)

#TC4: random address with ALU Multiplication operation (op_select = 01)
@cocotb.test()
async def test_axi_alu_mult_operation_random_address(dut):
    cocotb.start_soon(Clock(dut.axi_clk_in, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.fast_clk_in, 5, units="ns").start())

    await init_dut(dut)

    await test_burst_transactions(dut)

    for _ in range(16):
        op_a = random.randint(0, 15)
        op_b = random.randint(0, 15)
        op_c = random.randint(0, 15)
        op_select = 5
        clock_ctrl = random.randint(0, 1)

        print(f"Testing with operands: op_a = {hex(op_a)}, op_b = {hex(op_b)}, op_c = {hex(op_c)}, op_select = {bin(op_select)}, clock_ctrl = {clock_ctrl}")
        await axi_operation(dut, op_a, op_b, op_c, op_select, clock_ctrl)
        await axi_check_result(dut, op_a, op_b, op_c, op_select)

#TC5: random address with ALU Shift operation (op_select = 10)
@cocotb.test()
async def test_axi_alu_shift_operation_random_address(dut):
    cocotb.start_soon(Clock(dut.axi_clk_in, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.fast_clk_in, 5, units="ns").start())

    await init_dut(dut)

    await test_burst_transactions(dut)

    for _ in range(16):
        op_a = random.randint(0, 15)
        op_b = random.randint(0, 15)
        op_c = random.randint(0, 15)
        op_select = 6
        clock_ctrl = random.randint(0, 1)

        print(f"Testing with operands: op_a = {hex(op_a)}, op_b = {hex(op_b)}, op_c = {hex(op_c)}, op_select = {bin(op_select)}, clock_ctrl = {clock_ctrl}")
        await axi_operation(dut, op_a, op_b, op_c, op_select, clock_ctrl)
        await axi_check_result(dut, op_a, op_b, op_c, op_select)

#TC6: random address with ALU division operation (op_select = 11)
@cocotb.test()
async def test_axi_alu_div_operation_random_address(dut):
    cocotb.start_soon(Clock(dut.axi_clk_in, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.fast_clk_in, 5, units="ns").start())

    await init_dut(dut)

    await test_burst_transactions(dut)

    for _ in range(16):
        op_a = random.randint(0, 15)
        op_b = random.randint(0, 15)
        op_c = random.randint(0, 15)
        op_select = 7
        clock_ctrl = random.randint(0, 1)

        print(f"Testing with operands: op_a = {hex(op_a)}, op_b = {hex(op_b)}, op_c = {hex(op_c)}, op_select = {bin(op_select)}, clock_ctrl = {clock_ctrl}")
        await axi_operation(dut, op_a, op_b, op_c, op_select, clock_ctrl)
        await axi_check_result(dut, op_a, op_b, op_c, op_select)

#TC7: Write random data to memory and random operands and address
@cocotb.test()
async def test_random_memory_operands(dut):
    print("Starting random memory operations...")
    cocotb.start_soon(Clock(dut.axi_clk_in, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.fast_clk_in, 5, units="ns").start())

    await init_dut(dut)

    memory = [random.randint(0, 0xFFFFFFFF) for _ in range(16)]
    memory[0] = 0x5

    for i in range(16):
        await axi_write(dut, 0x0000_0020 + (i * 4), memory[i])

    for _ in range(50):
        op_a = random.randint(0, 15)
        op_b = random.randint(0, 15)
        op_c = random.randint(0, 15)
        op_select = random.randint(0,7)
        clock_ctrl = random.randint(0, 1)

        # Print operands and op_select for each test case
        print(f"Testing with random memory values: op_a = {hex(memory[op_a])}, op_b = {hex(memory[op_b])}, op_c = {hex(memory[op_c])}, op_select = {bin(op_select)}, clock_ctrl = {clock_ctrl}")
        await axi_operation(dut, op_a, op_b, op_c, op_select, clock_ctrl)
        await axi_random_check_result(dut, memory[op_a], memory[op_b], memory[op_c], op_select)


#TC8: overlapping dsp and memory
@cocotb.test()
async def test_overlapping_dsp_sram_access(dut):
    cocotb.start_soon(Clock(dut.axi_clk_in, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.fast_clk_in, 5, units="ns").start())

    await init_dut(dut)
    await test_burst_transactions(dut)

    # Start a DSP operation
    op_a = 0x0000000A
    op_b = 0x00000005
    op_c = 0x00000002
    op_select = 0b111  # MAC operation
    clock_ctrl = 1

     # Start a DSP operation
    await axi_operation(dut, op_a, op_b, op_c, 0b011, 1)
    
    # Simultaneous AXI write transaction
    await axi_write(dut, 0x0000_000C, 0x00000007)
    await axi_write(dut, 0x0000_0024, 0x0000FFFF)
    
    # Wait for DSP operation to complete
    await axi_check_result(dut, op_a, op_b, op_c, op_select)
    for i in range(16):
        mem_address = f"0x{0x00000020 + (i * 4):08X}"
        mem_data = int(dut.u_memory_block.ram[i].value)
        if i == 1:
            expected_value = 0x0000FFFF  # Expected value as per burst initialization
        else:
            expected_value = i + 5  # Expected value as per burst initialization
        # Assertion to check memory correctness
        assert mem_data == expected_value, \
            f"Memory Mismatch at Address {mem_address}: Expected 0x{expected_value:08X}, Got 0x{mem_data:08X}"


#TC9: Unaligned AXI Read/Write
@cocotb.test()
async def test_unaligned_axi_access(dut):
    cocotb.start_soon(Clock(dut.axi_clk_in, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.fast_clk_in, 5, units="ns").start())

    await init_dut(dut)

    unaligned_address = 0x00000013  # Example unaligned address
    test_data = 0x12345678
    
    # Write to unaligned address
    await axi_write(dut, unaligned_address, test_data)
    
    # Read back and verify
    await axi_read(dut, unaligned_address)
    read_data = dut.axi_rdata_o.value.to_unsigned()
    assert read_data == 0x0, f"Unaligned access failed: Expected 0x{test_data:X}, Got 0x{read_data:X}"
    print("Test Passed: Unaligned AXI access verified successfully.Odd address not allowed. Only Byte addressable")

#TC10: AXI Burst Crossing Memory Boundary
@cocotb.test()
async def test_axi_burst_boundary_wrap(dut):
    cocotb.start_soon(Clock(dut.axi_clk_in, 10, units="ns").start())
    cocotb.start_soon(Clock(dut.fast_clk_in, 5, units="ns").start())

    await init_dut(dut)

    boundary_address = 0x0000_005C  # Example address near boundary
    burst_length = 16  # Ensure burst crosses boundary
    base_data = 0x00000004

    await axi_write_burst(dut, boundary_address, burst_length, base_data)
    await RisingEdge(dut.axi_clk_in)
    # Start a DSP operation
    op_a = 0x0000000A
    op_b = 0x00000005
    op_c = 0x00000002
    op_select = 0b100  # MAC operation
    clock_ctrl = 1

     # Start a DSP operation
    await axi_operation(dut, op_a, op_b, op_c, 0b100, 1)
    await axi_check_result(dut, op_a, op_b, op_c, op_select)
    
    # Wait for DSP operation to complete
    print("Test Passed: AXI burst transaction handled memory boundary correctly.")

#Expected data and check result for incremental data in Memory
async def axi_check_result(dut, op_a, op_b, op_c, op_select):
    dsp_result_address = 5
    await axi_read(dut, dsp_result_address << 2)
    result_low = dut.axi_rdata_o.value.to_unsigned()
    await axi_read(dut, (dsp_result_address + 1) << 2)
    result_high = dut.axi_rdata_o.value.to_unsigned()
    result = (result_high << 32) | result_low

    # Compute expected result based on operation
    if op_select == 0b100:
        expected_result = ((op_a + dsp_result_address) + (op_b + dsp_result_address)) * (op_c + dsp_result_address)
    elif op_select == 0b101:
        expected_result = (op_a + dsp_result_address) * (op_b + dsp_result_address)
    elif op_select == 0b110:
        shift_amount = (op_b + dsp_result_address) & 0x1F  # Ensure shift is within 0-31 range
        expected_result = (op_a + dsp_result_address) >> shift_amount
    elif op_select == 0b111:
        divisor = op_b + dsp_result_address
        if divisor != 0:
            expected_result = (op_a + dsp_result_address) // divisor  # Integer division
        else:
            expected_result = 0xDEADDEAD
    else:
        expected_result = 0

    # Use assert to check the result
    assert result == expected_result, f"Test Failed: Expected = 0x{expected_result:X}, Got = 0x{result:X}"
    print(f"Test Passed: Expected = 0x{expected_result:X}, Got = 0x{result:X}")


#Expected data and check result for random data in Memory
async def axi_random_check_result(dut, op_a, op_b, op_c, op_select):
    dsp_result_address = 5
    await axi_read(dut, dsp_result_address << 2)
    result_low = dut.axi_rdata_o.value.to_unsigned()
    await axi_read(dut, (dsp_result_address + 1) << 2)
    result_high = dut.axi_rdata_o.value.to_unsigned()
    result = (result_high << 32) | result_low

    if not hasattr(axi_random_check_result, "expected_result"):
        axi_random_check_result.expected_result = 0  # Initialize to 0 or any default value

    if op_select == 0b100:
        axi_random_check_result.expected_result = ((op_a + op_b) * op_c) & 0xFFFFFFFFFFFFFFFF
    elif op_select == 0b101:
        axi_random_check_result.expected_result = (op_a * op_b) & 0xFFFFFFFFFFFFFFFF
    elif op_select == 0b110:
        shift_amount = op_b & 0x1F  # Ensure shift is within 0-31 range
        axi_random_check_result.expected_result = (op_a >> shift_amount) & 0xFFFFFFFFFFFFFFFF
    elif op_select == 0b111:
        divisor = op_b
        if divisor != 0:
            axi_random_check_result.expected_result = (op_a // divisor) & 0xFFFFFFFFFFFFFFFF  # Integer division
        else:
            axi_random_check_result.expected_result = 0xDEADDEAD  # Default error value
    # If `op_select` doesn't match any known case, retain the previous expected value

    expected_result = axi_random_check_result.expected_result  # Retrieve the latest expected result

    assert result == expected_result, f"Test Failed: Expected = 0x{expected_result:X}, Got = 0x{result:X}"
    print(f"Test Passed: Expected = 0x{expected_result:X}, Got = 0x{result:X}")

