import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock

@cocotb.test()
async def test_normal_transfer(dut):
    """Test a normal single block transfer with print statements for debugging."""
    cocotb.log.info("=== Starting test_normal_transfer ===")
    cocotb.start_soon(Clock(dut.i_axi_clk, 10, units="ns").start())

    await reset_dut(dut)

    block_size = 4
    dut.i_block_fifo_rdy.value = 0
    dut.i_block_fifo_size.value = 0
    dut.i_axi_ready.value = 0
    dut.i_pause.value = 0
    dut.i_flush.value = 0
    dut.i_axi_user.value = 0x0


    await Timer(100, units="ns")

    dut.i_block_fifo_size.value = block_size
    dut.i_block_fifo_rdy.value = 1
    cocotb.log.info("FIFO is ready, block_size=%d" % block_size)

    dut.i_axi_ready.value = 1
    cocotb.log.info("AXI is ready for normal_transfer")

    await wait_for_act(dut, "test_normal_transfer")

    fifo_data_words = [0x11, 0x22, 0x33, 0x44]
    await provide_and_check_data(dut, fifo_data_words, "test_normal_transfer")

    cocotb.log.info("=== test_normal_transfer completed successfully ===")


@cocotb.test()
async def test_multiple_blocks(dut):
    """Test handling multiple consecutive blocks."""
    cocotb.log.info("=== Starting test_multiple_blocks ===")
    cocotb.start_soon(Clock(dut.i_axi_clk, 10, units="ns").start())

    await reset_dut(dut)
    dut.i_axi_user.value = 0x0

    # First block
    block_size_1 = 4
    # Second block
    block_size_2 = 4

    dut.i_block_fifo_rdy.value = 1
    dut.i_block_fifo_size.value = block_size_1
    dut.i_axi_ready.value = 1
    dut.i_flush.value = 0
    dut.i_pause.value = 0

    cocotb.log.info("FIFO ready for first block, block_size_1=%d" % block_size_1)
    await wait_for_act(dut, "test_multiple_blocks - first block")

    fifo_data_1 = [0x11, 0x22, 0x33, 0x44]
    await provide_and_check_data(dut, fifo_data_1, "test_multiple_blocks (block1)")

    cocotb.log.info("First block completed, starting second block")

    dut.i_block_fifo_size.value = block_size_2
    await wait_for_act(dut, "test_multiple_blocks - second block")

    fifo_data_2 = [0x55, 0x66, 0x77, 0x88]
    await provide_and_check_data(dut, fifo_data_2, "test_multiple_blocks (block2)")

    cocotb.log.info("=== test_multiple_blocks completed successfully ===")


@cocotb.test()
async def test_flush(dut):
    """Test flushing in the middle of a block."""
    cocotb.log.info("=== Starting test_flush ===")
    cocotb.start_soon(Clock(dut.i_axi_clk, 10, units="ns").start())

    await reset_dut(dut)

    block_size = 5
    dut.i_block_fifo_rdy.value = 1
    dut.i_block_fifo_size.value = block_size
    dut.i_axi_ready.value = 1
    dut.i_pause.value = 0
    dut.i_flush.value = 0
    dut.i_axi_user.value = 0x0


    cocotb.log.info("FIFO ready for flush test, block_size=%d" % block_size)
    await wait_for_act(dut, "test_flush")

    # Provide a couple of words and then flush
    fifo_data = [0x11, 0x22, 0x33, 0x44, 0x55]
    await provide_fifo_data_partial(dut, fifo_data, 2, "test_flush before flush")

    cocotb.log.info("Asserting flush in test_flush")
    dut.i_flush.value = 1
    await RisingEdge(dut.i_axi_clk)
    dut.i_flush.value = 0

    # Check if DUT returns to IDLE
    for _ in range(10):
        await RisingEdge(dut.i_axi_clk)
        if int(dut.o_block_fifo_act.value) == 0:
            cocotb.log.info("DUT returned to IDLE after flush")
            break

    cocotb.log.info("=== test_flush completed successfully ===")


@cocotb.test()
async def test_pause(dut):
    """Test pausing in the middle of data sending."""
    cocotb.log.info("=== Starting test_pause ===")
    cocotb.start_soon(Clock(dut.i_axi_clk, 10, units="ns").start())

    await reset_dut(dut)
    dut.i_axi_user.value = 0x0


    block_size = 6
    dut.i_block_fifo_rdy.value = 1
    dut.i_block_fifo_size.value = block_size
    dut.i_axi_ready.value = 1
    dut.i_flush.value = 0
    dut.i_pause.value = 0

    cocotb.log.info("FIFO ready for pause test, block_size=%d" % block_size)
    await wait_for_act(dut, "test_pause")

    # Provide half the data, then pause
    half = block_size // 2
    fifo_data = [0x11, 0x22, 0x33, 0x44, 0x55, 0x66]
    await provide_fifo_data_partial(dut, fifo_data, half, "test_pause - before pause", wait_for_last=False)

    cocotb.log.info("Pausing AXI send in test_pause")
    dut.i_pause.value = 1
    for _ in range(5):
        await RisingEdge(dut.i_axi_clk)
        debug_signals(dut, "test_pause - during pause")
    dut.i_pause.value = 0
    cocotb.log.info("Resumed AXI send in test_pause")

    # Provide remaining data
    await provide_fifo_data_partial(dut, fifo_data[half:], len(fifo_data)-half, "test_pause - after pause")

    cocotb.log.info("=== test_pause completed successfully ===")


@cocotb.test()
async def test_axi_not_ready(dut):
    """Test scenario when AXI not ready for a while."""
    cocotb.log.info("=== Starting test_axi_not_ready ===")
    cocotb.start_soon(Clock(dut.i_axi_clk, 10, units="ns").start())

    await reset_dut(dut)

    dut.i_axi_user.value = 0x0
    block_size = 4
    dut.i_block_fifo_rdy.value = 1
    dut.i_block_fifo_size.value = block_size
    dut.i_flush.value = 0
    dut.i_pause.value = 0
    dut.i_axi_ready.value = 1

    cocotb.log.info("FIFO ready, AXI ready initially for axi_not_ready test, block_size=%d" % block_size)
    await wait_for_act(dut, "test_axi_not_ready")

    half = block_size // 2
    fifo_data = [0x11, 0x22, 0x33, 0x44]
    await provide_fifo_data_partial(dut, fifo_data, half, "test_axi_not_ready - before not ready", wait_for_last=False)

    cocotb.log.info("De-asserting AXI ready for a while in test_axi_not_ready")
    dut.i_axi_ready.value = 0
    for _ in range(10):
        await RisingEdge(dut.i_axi_clk)
        debug_signals(dut, "test_axi_not_ready - AXI not ready")
    dut.i_axi_ready.value = 1
    cocotb.log.info("AXI ready re-asserted in test_axi_not_ready")

    await provide_fifo_data_partial(dut, fifo_data[half:], len(fifo_data)-half, "test_axi_not_ready - after ready")

    cocotb.log.info("=== test_axi_not_ready completed successfully ===")


async def reset_dut(dut):
    cocotb.log.info("Asserting reset")
    dut.rst.value = 1
    dut.i_flush.value = 0
    dut.i_pause.value = 0
    dut.i_block_fifo_rdy.value = 0
    dut.i_block_fifo_size.value = 0
    dut.i_axi_ready.value = 0
    dut.i_block_fifo_data.value = 0


    await Timer(100, units="ns")
    dut.rst.value = 0
    await Timer(100, units="ns")
    cocotb.log.info("DUT reset completed.")
    debug_signals(dut, "After reset")


async def wait_for_act(dut, test_name):
    for i in range(100):
        await RisingEdge(dut.i_axi_clk)
        if int(dut.o_block_fifo_act.value) == 1:
            cocotb.log.info(f"{test_name}: o_block_fifo_act asserted at cycle {i}")
            return
        if i % 10 == 0:
            debug_signals(dut, f"{test_name}: waiting for act at cycle {i}")
    raise cocotb.result.TestFailure(f"{test_name}: DUT did not assert o_block_fifo_act")


async def provide_and_check_data(dut, fifo_data_words, test_name):
    """Provide the entire block of data and expect last=1 at the end."""
    data_idx = 0
    axi_captured = []

    for cycle in range(1000):
        await RisingEdge(dut.i_axi_clk)

        if cycle % 20 == 0:
            debug_signals(dut, f"{test_name}: Cycle {cycle}")

        if int(dut.o_block_fifo_stb.value) == 1 and data_idx < len(fifo_data_words):
            val = fifo_data_words[data_idx]
            dut.i_block_fifo_data.value = val
            cocotb.log.info(f"{test_name}: Provided FIFO data 0x{val:02x} at data_idx={data_idx}")
            data_idx += 1

        if int(dut.o_axi_valid.value) == 1:
            axi_val = int(dut.o_axi_data.value)
            last = int(dut.o_axi_last.value)

            user_str = dut.o_axi_user.value.binstr
            if 'x' in user_str.lower() or 'z' in user_str.lower():
                cocotb.log.warning(f"{test_name}: o_axi_user has X/Z: {user_str}, printing as string only.")
                user_disp = user_str
            else:
                user_disp = f"0x{int(dut.o_axi_user.value):x}"

            cocotb.log.info(f"{test_name}: AXI OUT data=0x{axi_val:02x}, last={last}, user={user_disp}")
            axi_captured.append(axi_val)
            if last == 1:
                cocotb.log.info(f"{test_name}: Received last=1, block completed.")
                if len(axi_captured) == 0:
                    raise cocotb.result.TestFailure(f"{test_name}: No AXI data received!")
                if int(dut.o_axi_last.value) != 1:
                    raise cocotb.result.TestFailure(f"{test_name}: Did not receive o_axi_last=1 at the end of the block")
                cocotb.log.info(f"{test_name}: test completed successfully")
                return

    # If no last received
    raise cocotb.result.TestFailure(f"{test_name}: Did not receive last=1 after 1000 cycles!")


async def provide_fifo_data_partial(dut, fifo_data_words, count, test_name, wait_for_last=True):
    """Provide a partial set of FIFO words. If wait_for_last=False, we stop after providing the given count of words."""
    data_idx = 0
    axi_captured = []

    for cycle in range(1000):
        await RisingEdge(dut.i_axi_clk)

        if cycle % 20 == 0:
            debug_signals(dut, f"{test_name}: Cycle {cycle}")

        if int(dut.o_block_fifo_stb.value) == 1 and data_idx < count:
            val = fifo_data_words[data_idx]
            dut.i_block_fifo_data.value = val
            cocotb.log.info(f"{test_name}: Provided FIFO data 0x{val:02x} at data_idx={data_idx}")
            data_idx += 1

        if int(dut.o_axi_valid.value) == 1:
            axi_val = int(dut.o_axi_data.value)
            last = int(dut.o_axi_last.value)

            user_str = dut.o_axi_user.value.binstr
            if 'x' in user_str.lower() or 'z' in user_str.lower():
                cocotb.log.warning(f"{test_name}: o_axi_user has X/Z: {user_str}, printing as string only.")
                user_disp = user_str
            else:
                user_disp = f"0x{int(dut.o_axi_user.value):x}"

            cocotb.log.info(f"{test_name}: AXI OUT data=0x{axi_val:02x}, last={last}, user={user_disp}")
            axi_captured.append(axi_val)
            if last == 1 and wait_for_last:
                cocotb.log.info(f"{test_name}: Received last=1, partial test scenario completed.")
                return

        if not wait_for_last and data_idx == count:
            # Provided all requested words, not waiting for last=1
            cocotb.log.info(f"{test_name}: Provided {count} words and not waiting for last, returning.")
            return


def debug_signals(dut, context=""):
    # Convert all signals to int before formatting
    o_act = int(dut.o_block_fifo_act.value)
    o_stb = int(dut.o_block_fifo_stb.value)
    i_rdy = int(dut.i_block_fifo_rdy.value)
    i_size = int(dut.i_block_fifo_size.value)
    o_valid = int(dut.o_axi_valid.value)
    o_last = int(dut.o_axi_last.value)
    i_ready = int(dut.i_axi_ready.value)
    i_flush = int(dut.i_flush.value)
    i_pause = int(dut.i_pause.value)
    o_data = int(dut.o_axi_data.value)

    # Handle o_axi_user
    user_str = dut.o_axi_user.value.binstr
    if 'x' in user_str.lower() or 'z' in user_str.lower():
        o_user_str = user_str
    else:
        o_user = int(dut.o_axi_user.value)
        o_user_str = f"0x{o_user:x}"

    cocotb.log.info(f"{context} Signals: "
                    f"o_block_fifo_act={o_act}, "
                    f"o_block_fifo_stb={o_stb}, "
                    f"i_block_fifo_rdy={i_rdy}, "
                    f"i_block_fifo_size={i_size:024b}, "
                    f"o_axi_valid={o_valid}, "
                    f"o_axi_last={o_last}, "
                    f"i_axi_ready={i_ready}, "
                    f"i_flush={i_flush}, "
                    f"i_pause={i_pause}, "
                    f"o_axi_data=0x{o_data:08x}, "
                    f"o_axi_user={o_user_str}")
