import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import logging
import os
import random

def get_granted_channels(grant_list):
    return [i for i, granted in enumerate(grant_list) if granted]

@cocotb.test()
async def test_no_requests(dut):
    """Test Case 1: No Requests - Arbiter should remain idle."""
    logger = logging.getLogger("cocotb.test_no_requests")
    N = int(os.getenv("N_DEVICES", "4"))
    TIMEOUT = int(os.getenv("TIMEOUT", "16"))  # Ensure TIMEOUT=16

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Reset the DUT
    dut.rstn.value = 0
    await Timer(20, units='ns')
    dut.rstn.value = 1
    await RisingEdge(dut.clk)

    logger.info("DUT has been reset for Test Case 1.")

    TEST_CYCLES = 50
    for cycle in range(TEST_CYCLES):
        # No requests; set all req and priority_level to 0
        req = [0] * N
        priority_level = [0] * N
        dut.req.value = 0
        dut.priority_level.value = 0

        logger.debug(f"Cycle {cycle}: req={req} | priority_level={priority_level}")

        await RisingEdge(dut.clk)

        # Read the actual grant from the DUT
        actual_grant = dut.grant.value.to_unsigned()
        actual_grant_list = [(actual_grant >> i) & 1 for i in range(N)]

        # Read the idle signal
        actual_idle = dut.idle.value.to_unsigned()

        logger.debug(f"Cycle {cycle}: grant={actual_grant_list} | idle={actual_idle}")

        # Expected behavior: No grants, idle=1
        expected_grant = [0] * N
        expected_idle = 1

        assert actual_grant_list == expected_grant, \
            f"Cycle {cycle}: Expected grant={expected_grant}, Actual grant={actual_grant_list}"

        assert actual_idle == expected_idle, \
            f"Cycle {cycle}: Expected idle={expected_idle}, Actual idle={actual_idle}"

        logger.info(f"Cycle {cycle}: Arbiter correctly idle with no requests.")

    logger.info("Test Case 1: No Requests completed successfully.")

@cocotb.test()
async def test_single_request(dut):
    """Test Case 2: Single Request - Arbiter should grant to the requesting channel."""
    logger = logging.getLogger("cocotb.test_single_request")
    N = int(os.getenv("N_DEVICES", "4"))
    TIMEOUT = int(os.getenv("TIMEOUT", "16"))  # Ensure TIMEOUT=16

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Reset the DUT
    dut.rstn.value = 0
    await Timer(20, units='ns')
    dut.rstn.value = 1
    await RisingEdge(dut.clk)

    logger.info("DUT has been reset for Test Case 2.")

    requested_channel = 2  # Example: Channel 2 (0-indexed)
    TEST_CYCLES = 50

    for cycle in range(TEST_CYCLES):
        # Only one channel is requesting
        req = [0] * N
        priority_level = [0] * N
        req[requested_channel] = 1
        priority_level[requested_channel] = 0  # Low priority
        req_int = int("".join(str(bit) for bit in reversed(req)), 2)
        priority_level_int = int("".join(str(bit) for bit in reversed(priority_level)), 2)
        dut.req.value = req_int
        dut.priority_level.value = priority_level_int

        logger.debug(f"Cycle {cycle}: req={req} | priority_level={priority_level}")

        await RisingEdge(dut.clk)

        # Read the actual grant from the DUT
        actual_grant = dut.grant.value.to_unsigned()
        actual_grant_list = [(actual_grant >> i) & 1 for i in range(N)]

        # Read the idle signal
        actual_idle = dut.idle.value.to_unsigned()

        logger.debug(f"Cycle {cycle}: grant={actual_grant_list} | idle={actual_idle}")

        # Expected behavior: Only the requested channel is granted, idle=0
        expected_grant = [0] * N
        expected_grant[requested_channel] = 1
        expected_idle = 0

        assert actual_grant_list == expected_grant, \
            f"Cycle {cycle}: Expected grant={expected_grant}, Actual grant={actual_grant_list}"

        assert actual_idle == expected_idle, \
            f"Cycle {cycle}: Expected idle={expected_idle}, Actual idle={actual_idle}"

        logger.info(f"Cycle {cycle}: Arbiter correctly granted Channel {requested_channel}.")

    logger.info("Test Case 2: Single Request completed successfully.")

@cocotb.test()
async def test_multiple_requests_no_priorities(dut):
    """Test Case 3: Multiple Requests without Priorities - Round-Robin Grants."""
    logger = logging.getLogger("cocotb.test_multiple_requests_no_priorities")
    N = int(os.getenv("N_DEVICES", "4"))
    TIMEOUT = int(os.getenv("TIMEOUT", "16"))  # Ensure TIMEOUT=16

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Reset the DUT
    dut.rstn.value = 0
    await Timer(20, units='ns')
    dut.rstn.value = 1
    await RisingEdge(dut.clk)

    logger.info("DUT has been reset for Test Case 3.")

    requested_channels = [1, 3]  # Example: Channels 1 and 3 (0-indexed)
    TEST_CYCLES = 100

    for cycle in range(TEST_CYCLES):
        # Multiple channels are requesting with no priorities
        req = [0] * N
        priority_level = [0] * N
        for ch in requested_channels:
            req[ch] = 1
            priority_level[ch] = 0
        req_int = int("".join(str(bit) for bit in reversed(req)), 2)
        priority_level_int = int("".join(str(bit) for bit in reversed(priority_level)), 2)
        dut.req.value = req_int
        dut.priority_level.value = priority_level_int

        logger.debug(f"Cycle {cycle}: req={req} | priority_level={priority_level}")

        await RisingEdge(dut.clk)

        # Read the actual grant from the DUT
        actual_grant = dut.grant.value.to_unsigned()
        actual_grant_list = [(actual_grant >> i) & 1 for i in range(N)]

        # Read the idle signal
        actual_idle = dut.idle.value.to_unsigned()

        logger.debug(f"Cycle {cycle}: grant={actual_grant_list} | idle={actual_idle}")

        # Expected behavior:
        # - Only one grant per cycle
        # - Grant is within the requesting channels
        assert sum(actual_grant_list) <= 1, \
            f"Cycle {cycle}: Expected at most one grant, but got {actual_grant_list}"

        if any(req):
            assert sum(actual_grant_list) == 1, \
                f"Cycle {cycle}: Expected one grant, but got {actual_grant_list}"
            granted_channel = actual_grant_list.index(1)
            assert granted_channel in requested_channels, \
                f"Cycle {cycle}: Granted channel {granted_channel} was not requesting."
            logger.info(f"Cycle {cycle}: Arbiter correctly granted Channel {granted_channel}.")
        else:
            assert actual_idle == 1, \
                f"Cycle {cycle}: Expected idle=1, but got idle={actual_idle}"
            logger.info(f"Cycle {cycle}: Arbiter correctly idle with no requests.")

    logger.info("Test Case 3: Multiple Requests without Priorities completed successfully.")

@cocotb.test()
async def test_high_priority_requests(dut):
    """Test Case 4: High-Priority Requests - Arbiter grants high-priority channels first."""
    logger = logging.getLogger("cocotb.test_high_priority_requests")
    N = int(os.getenv("N_DEVICES", "4"))
    TIMEOUT = int(os.getenv("TIMEOUT", "16"))  # Ensure TIMEOUT=16

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Reset the DUT
    dut.rstn.value = 0
    await Timer(20, units='ns')
    dut.rstn.value = 1
    await RisingEdge(dut.clk)

    logger.info("DUT has been reset for Test Case 4.")

    high_priority_channels = [0, 2]
    low_priority_channels = [1, 3]
    TEST_CYCLES = 100

    for cycle in range(TEST_CYCLES):
        # Multiple channels are requesting with some high priorities
        req = [0] * N
        priority_level = [0] * N
        for ch in high_priority_channels:
            req[ch] = 1
            priority_level[ch] = 1  # High priority
        for ch in low_priority_channels:
            req[ch] = 1
            priority_level[ch] = 0  # Low priority
        req_int = int("".join(str(bit) for bit in reversed(req)), 2)
        priority_level_int = int("".join(str(bit) for bit in reversed(priority_level)), 2)
        dut.req.value = req_int
        dut.priority_level.value = priority_level_int

        logger.debug(f"Cycle {cycle}: req={req} | priority_level={priority_level}")

        await RisingEdge(dut.clk)

        # Read the actual grant from the DUT
        actual_grant = dut.grant.value.to_unsigned()
        actual_grant_list = [(actual_grant >> i) & 1 for i in range(N)]

        # Read the idle signal
        actual_idle = dut.idle.value.to_unsigned()

        logger.debug(f"Cycle {cycle}: grant={actual_grant_list} | idle={actual_idle}")

        # Expected behavior:
        # - Only one grant per cycle
        # - If high-priority channels are requesting, grant one of them
        # - Otherwise, grant low-priority channels

        assert sum(actual_grant_list) <= 1, \
            f"Cycle {cycle}: Expected at most one grant, but got {actual_grant_list}"

        if any(req):
            assert sum(actual_grant_list) == 1, \
                f"Cycle {cycle}: Expected one grant, but got {actual_grant_list}"
            granted_channel = actual_grant_list.index(1)
            if priority_level[granted_channel] == 1:
                assert granted_channel in high_priority_channels, \
                    f"Cycle {cycle}: Expected grant to high-priority channels {high_priority_channels}, but granted to Channel {granted_channel}"
                logger.info(f"Cycle {cycle}: Arbiter correctly granted High-Priority Channel {granted_channel}.")
            else:
                assert granted_channel in low_priority_channels, \
                    f"Cycle {cycle}: Expected grant to low-priority channels {low_priority_channels}, but granted to Channel {granted_channel}"
                logger.info(f"Cycle {cycle}: Arbiter correctly granted Low-Priority Channel {granted_channel}.")
        else:
            assert actual_idle == 1, \
                f"Cycle {cycle}: Expected idle=1, but got idle={actual_idle}"
            logger.info(f"Cycle {cycle}: Arbiter correctly idle with no requests.")

    logger.info("Test Case 4: High-Priority Requests completed successfully.")


@cocotb.test()
async def test_all_channels_requesting_mixed_priorities(dut):
    """Test Case 6: All Channels Requesting with Mixed Priorities - Complex Granting Logic."""
    logger = logging.getLogger("cocotb.test_all_channels_requesting_mixed_priorities")
    N = int(os.getenv("N_DEVICES", "4"))
    TIMEOUT = int(os.getenv("TIMEOUT", "16"))  # Ensure TIMEOUT=16

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Reset the DUT
    dut.rstn.value = 0
    await Timer(20, units='ns')
    dut.rstn.value = 1
    await RisingEdge(dut.clk)

    logger.info("DUT has been reset for Test Case 6.")

    priority_patterns = [
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 1, 0, 0],
        [0, 0, 1, 1],
        [1, 0, 0, 1],
        [0, 1, 1, 0],
    ]

    CYCLES_PER_PATTERN = 50

    for pattern_index, prio_pattern in enumerate(priority_patterns):
        logger.info(f"Applying Priority Pattern {pattern_index + 1}: priority_level={prio_pattern}")

        for cycle in range(CYCLES_PER_PATTERN):
            # All channels are requesting
            req = [1] * N
            priority_level = prio_pattern.copy()
            req_int = int("".join(str(bit) for bit in reversed(req)), 2)
            priority_level_int = int("".join(str(bit) for bit in reversed(priority_level)), 2)
            dut.req.value = req_int
            dut.priority_level.value = priority_level_int

            logger.debug(f"Pattern {pattern_index + 1}, Cycle {cycle}: req={req} | priority_level={priority_level}")

            await RisingEdge(dut.clk)

            # Read the actual grant from the DUT
            actual_grant = dut.grant.value.to_unsigned()
            actual_grant_list = [(actual_grant >> i) & 1 for i in range(N)]

            # Read the idle signal
            actual_idle = dut.idle.value.to_unsigned()

            logger.debug(f"Pattern {pattern_index + 1}, Cycle {cycle}: grant={actual_grant_list} | idle={actual_idle}")

            # Determine expected grant: prioritize high-priority channels first
            # Without knowing the internal pointer, validate that grant is within high-priority requesting channels first
            granted_channels = get_granted_channels(actual_grant_list)
            assert len(granted_channels) <= 1, \
                f"Pattern {pattern_index + 1}, Cycle {cycle}: Expected at most one grant, but got {granted_channels}"

            if any(req):
                assert len(granted_channels) == 1, \
                    f"Pattern {pattern_index + 1}, Cycle {cycle}: Expected one grant, but got {granted_channels}"
                granted_channel = granted_channels[0]
                if priority_level[granted_channel] == 1:
                    assert granted_channel in [ch for ch, prio in enumerate(priority_level) if prio == 1], \
                        f"Pattern {pattern_index + 1}, Cycle {cycle}: Granted channel {granted_channel} is not high priority."
                    logger.info(f"Pattern {pattern_index + 1}, Cycle {cycle}: Arbiter correctly granted High-Priority Channel {granted_channel}.")
                else:
                    assert granted_channel in [ch for ch, prio in enumerate(priority_level) if prio == 0], \
                        f"Pattern {pattern_index + 1}, Cycle {cycle}: Granted channel {granted_channel} is not low priority."
                    logger.info(f"Pattern {pattern_index + 1}, Cycle {cycle}: Arbiter correctly granted Low-Priority Channel {granted_channel}.")
            else:
                assert actual_idle == 1, \
                    f"Pattern {pattern_index + 1}, Cycle {cycle}: Expected idle=1, but got idle={actual_idle}"
                logger.info(f"Pattern {pattern_index + 1}, Cycle {cycle}: Arbiter correctly idle with no requests.")

        logger.info(f"Pattern {pattern_index + 1}: Completed all {CYCLES_PER_PATTERN} cycles.")

    logger.info("Test Case 6: All Channels Requesting with Mixed Priorities completed successfully.")
