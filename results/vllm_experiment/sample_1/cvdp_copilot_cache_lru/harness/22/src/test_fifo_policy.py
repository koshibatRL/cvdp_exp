
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
import random
import time
import harness_library as hrs_lb


async def test_fifo_initialization(dut):
    """Test if FIFO counters are correctly initialized to 0 after reset."""
    cocotb.log.info("Starting test_fifo_initialization...")

    nindexes = int(dut.NINDEXES.value)

    await hrs_lb.reset(dut)

    index = 0
    assert dut.fifo_array[index].value == 0, f"Counter for index {index} not initialized to 0."

    index = nindexes - 1
    assert dut.fifo_array[index].value == 0, f"Counter for index {index} not initialized to 0."

    for i in range(4):
        index = random.randint(1, nindexes-2)
        assert dut.fifo_array[index].value == 0, f"Counter for index {index} not initialized to 0."

    cocotb.log.info("test_fifo_initialization passed.")


async def test_fifo_hit_increment(dut):
    """Test a hit does not increment the counter."""
    cocotb.log.info("Starting test_fifo_hit_increment...")

    await hrs_lb.dut_init(dut)
    await hrs_lb.reset(dut)

    nindexes = int(dut.NINDEXES.value)

    target_way = random.randint(0, int(dut.NWAYS.value) - 1)

    for index in [0, nindexes-1]:
        cocotb.log.debug(f"Target index: {index}, Target way: {target_way}")
        await hrs_lb.access_hit(dut, index, target_way)
        assert int(dut.way_replace.value) == 0, "no replace is expected after hit"

    index = random.randint(1, nindexes - 2)
    cocotb.log.debug(f"Target index: {index}, Target way: {target_way}")
    await hrs_lb.access_hit(dut, index, target_way)
    assert int(dut.way_replace.value) == 0, "no replace is expected after hit"

    cocotb.log.info("test_fifo_hit_increment passed.")


async def test_fifo_miss(dut):
    """Test counter behavior in a miss."""
    cocotb.log.info("Starting test_fifo_miss...")

    await hrs_lb.dut_init(dut)
    await hrs_lb.reset(dut)

    nindexes = int(dut.NINDEXES.value)

    for index in [0, nindexes-1]:
        target_way = random.randint(0, int(dut.NWAYS.value) - 1)
        cocotb.log.debug(f"Target index: {index}, Target way: {target_way}")
        await hrs_lb.access_miss(dut, index, target_way)
        assert int(dut.way_replace.value) == 1, "on a miss, the next position is selected for replacement"

    target_way = random.randint(0, int(dut.NWAYS.value) - 1)
    index = random.randint(1, nindexes - 2)
    cocotb.log.debug(f"Target index: {index}, Target way: {target_way}")
    await hrs_lb.access_miss(dut, index, target_way)
    assert int(dut.way_replace.value) == 1, "on a miss, the next position is selected for replacement"

    cocotb.log.info("test_fifo_miss passed.")


async def test_fifo_replacement_order(dut):
    """Test the replacement order."""
    cocotb.log.info("Starting test_fifo_replacement_order...")

    await hrs_lb.dut_init(dut)
    await hrs_lb.reset(dut)

    nindexes = int(dut.NINDEXES.value)
    nways = int(dut.NWAYS.value)

    overflows = 4

    for index in [0, nindexes-1]:
        for i in range(overflows):
            for n in range(nways):
                target_way = n
                cocotb.log.debug(f"Target index: {index}, Target way: {target_way}")
                await hrs_lb.access_miss(dut, index, target_way)
                assert int(dut.way_replace.value) == (n + 1) % nways, "on a miss, the next position is selected for replacement"

    index = random.randint(1, nindexes - 2)
    for i in range(overflows):
        for n in range(nways):
            target_way = n
            cocotb.log.debug(f"Target index: {index}, Target way: {target_way}")
            await hrs_lb.access_miss(dut, index, target_way)
            assert int(dut.way_replace.value) == (n + 1) % nways, "on a miss, the next position is selected for replacement"

    cocotb.log.info("test_fifo_replacement_order passed.")


@cocotb.test()
async def test_policy_working(dut):
    """Main test function to call all tests."""
    cocotb.log.setLevel("DEBUG")
    cocotb.log.info("Starting test_policy_working...")

    clock_period = 10  # ns
    await cocotb.start(Clock(dut.clock, clock_period, units="ns").start())
    await hrs_lb.dut_init(dut)

    nways = int(dut.NWAYS.value)
    nindexes = int(dut.NINDEXES.value)
    cocotb.log.info(f"NWAYS: {nways}  NINDEXES: {nindexes}")

    await test_fifo_initialization(dut)
    cocotb.log.info("Test 1: Initialization passed.")

    await test_fifo_hit_increment(dut)
    cocotb.log.info("Test 2: Hit Increment passed.")

    await test_fifo_miss(dut)
    cocotb.log.info("Test 3: FIFO behavior for miss passed.")

    await test_fifo_replacement_order(dut)
    cocotb.log.info("Test 4: Replacement order passed.")

    cocotb.log.info("All tests passed.")
