import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge,FallingEdge, Timer
import random

import harness_library as hrs_lb

async def wait_for_seconds(dut, num_seconds , clk_freq):
    counter_max = clk_freq
    counter = 0

    for _ in range(num_seconds):
        while counter < counter_max:
            await RisingEdge(dut.clk)
            counter += 1
        counter = 0 
        print(f"Current Time - Hours: {int(dut.hours.value)}, Minutes: {int(dut.minutes.value)}, Seconds: {int(dut.seconds.value)}")

# Test random load values
async def test_random_load(dut):
    for _ in range(2):
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        random_seconds = random.randint(0, 59)

        await RisingEdge(dut.clk)
        dut.load_hours.value = random_hours
        dut.load_minutes.value = random_minutes
        dut.load_seconds.value = random_seconds

        dut.load.value = 1
        await Timer(1, units='ns')
        assert dut.hours.value == random_hours, f"Load error in hours! Expected: {random_hours}, Got: {dut.hours.value}"
        assert dut.minutes.value == random_minutes, f"Load error in minutes! Expected: {random_minutes}, Got: {dut.minutes.value}"
        assert dut.seconds.value == random_seconds, f"Load error in seconds! Expected: {random_seconds}, Got: {dut.seconds.value}"

        await RisingEdge(dut.clk)
        dut.load.value = 0

# Check rollovers for seconds, minutes, and hours
async def check_rollover(dut,clk_freq):

    # Load maximum time to check full rollover
    dut.load.value = 1
    dut.load_hours.value = 23
    dut.load_minutes.value = 59
    dut.load_seconds.value = 59
    await RisingEdge(dut.clk)
    dut.load.value = 0

    # Start the timer
    dut.start_stop.value = 1
    await wait_for_seconds(dut, 1, clk_freq)
    await RisingEdge(dut.clk)

    # Check rollover 
    assert (
        dut.hours.value == 23
        and dut.minutes.value == 59
        and dut.seconds.value == 58
    ), f"Full rollover failed: {dut.hours.value}:{dut.minutes.value}:{dut.seconds.value}"

    # Load minutes rollover 
    dut.load.value = 1
    dut.load_hours.value = 0
    dut.load_minutes.value = 1
    dut.load_seconds.value = 0
    await RisingEdge(dut.clk)
    dut.load.value = 0

    await wait_for_seconds(dut, 60, clk_freq)
    await RisingEdge(dut.clk)
 
    # Check minutes rollover to 00:00:00
    assert (
        dut.hours.value == 0
        and dut.minutes.value == 0
        and dut.seconds.value == 0
    ), f"Minutes rollover failed: {dut.hours.value}:{dut.minutes.value}:{dut.seconds.value}"

    # Load mixed rollover case (01:00:00)
    dut.load.value = 1
    dut.load_hours.value = 1
    dut.load_minutes.value = 0
    dut.load_seconds.value = 0
    await RisingEdge(dut.clk)
    dut.load.value = 0

    await wait_for_seconds(dut, 3600, clk_freq)
    await RisingEdge(dut.clk)

    # Check mixed rollover to 00:00:00
    assert (
        dut.hours.value == 0
        and dut.minutes.value == 0
        and dut.seconds.value == 0
    ), f"Mixed rollover failed: {dut.hours.value}:{dut.minutes.value}:{dut.seconds.value}"

# Verify the timer holds at 00:00:00
async def check_hold_at_zero(dut,clk_freq):
    # Load 00:00:00 and ensure it holds
    dut.load.value = 1
    dut.load_hours.value = 0
    dut.load_minutes.value = 0
    dut.load_seconds.value = 3
    await RisingEdge(dut.clk)
    dut.load.value = 0
    assert (
        dut.hours.value == 0
        and dut.minutes.value == 0
        and dut.seconds.value == 3
    ), f"Timer did not hold at 00:00:00! Got: {dut.hours.value}:{dut.minutes.value}:{dut.seconds.value}"

    # Start the timer
    dut.start_stop.value = 1
    await wait_for_seconds(dut, 20, clk_freq)
    await RisingEdge(dut.clk)
    assert (
        dut.hours.value == 0
        and dut.minutes.value == 0
        and dut.seconds.value == 0
    ), f"Timer did not hold at 00:00:00! Got: {dut.hours.value}:{dut.minutes.value}:{dut.seconds.value}"

    # Stop the timer
    dut.start_stop.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    # Verify the timer is still at 00:00:00
    assert (
        dut.hours.value == 0
        and dut.minutes.value == 0
        and dut.seconds.value == 0
    ), f"Timer changed after stopping at 00:00:00! Got: {dut.hours.value}:{dut.minutes.value}:{dut.seconds.value}"

async def check_pause_and_resume(dut,clk_freq):

    dut.load.value = 1
    dut.load_hours.value = 10
    dut.load_minutes.value = 50
    dut.load_seconds.value = 58
    await RisingEdge(dut.clk)
    dut.load.value = 0
    # Test that the stopwatch pauses and resumes correctly.
    dut.start_stop.value = 1
    await wait_for_seconds(dut, 10 , clk_freq)

    # Pause the stopwatch
    dut.start_stop.value = 0
    await RisingEdge(dut.clk)

    paused_seconds = int(dut.seconds.value)
    for _ in range(100):
        await RisingEdge(dut.clk)

    # Wait to ensure the stopwatch remains paused
    await RisingEdge(dut.clk)  
    assert int(dut.seconds.value) == paused_seconds, "Error: Stopwatch did not pause correctly."

    # Resume the stopwatch and check it continues counting from the same value
    dut.start_stop.value = 1
    await wait_for_seconds(dut, 20 , clk_freq)
    assert int(dut.seconds.value) == paused_seconds - 19, "Error: Stopwatch did not resume correctly."

async def pause_at_random_second(dut):

    dut.load.value = 1
    dut.load_hours.value = 2
    dut.load_minutes.value = 5
    dut.load_seconds.value = 40
    await RisingEdge(dut.clk)
    dut.load.value = 0
    dut.start_stop.value = 1

    tb_counter = 0  
    clk_freq = int(dut.CLK_FREQ.value)
    counter_max = clk_freq - 1 

    # Generate a random number of clock cycles to count before pausing
    random_pause_duration = random.randint(1, counter_max-1)

    # Run until reaching the random_pause_duration and keep track with tb_counter
    for _ in range(random_pause_duration):
        await RisingEdge(dut.clk)
        tb_counter += 1

    # Pause the stopwatch
    dut.start_stop.value = 0
    await RisingEdge(dut.clk)
    paused_seconds = int(dut.seconds.value)

    # Ensure the stopwatch remains paused by monitoring tb_counter and checking the seconds in the DUT
    for _ in range(100):
        await RisingEdge(dut.clk)
        assert int(dut.seconds.value) == paused_seconds, "Error: Stopwatch did not remain paused as expected."

    # Resume the stopwatch and continue tracking
    await RisingEdge(dut.clk)
    dut.start_stop.value = 1

    remaining_ticks = counter_max - tb_counter 
    for _ in range((remaining_ticks + 1)):
         await RisingEdge(dut.clk)

    # Verify stopwatch has advanced after the remaining ticks complete
    await RisingEdge(dut.clk)
    assert int(dut.seconds.value) == paused_seconds - 1 , f"Stopwatch did not resume correctly from paused second. Expected: {paused_seconds - 1}, Got: {dut.seconds.value}"

async def pause_at_random_minute(dut,clk_freq):

    # Set initial state close to rollover
    dut.load.value = 1
    dut.load_hours.value = 0
    dut.load_minutes.value = random.randint(2, 59)
    dut.load_seconds.value = 0
    await RisingEdge(dut.clk)
    dut.load.value = 0

    dut.start_stop.value = 1
    await RisingEdge(dut.clk)
    # Wait until the random minute is reached
    random_minutes = int(dut.load_minutes.value)
    await wait_for_seconds(dut, 60 , clk_freq)

    # Pause the stopwatch
    dut.start_stop.value = 0
    paused_minutes = int(dut.minutes.value)

    # Ensure the stopwatch remains paused
    for _ in range(100):
        await RisingEdge(dut.clk)
        assert int(dut.minutes.value) == paused_minutes, "Error: Stopwatch did not remain paused at the minute."

    # Resume the stopwatch
    dut.start_stop.value = 1
    await wait_for_seconds(dut, 60 , clk_freq)

    # Confirm it continues counting correctly
    assert int(dut.minutes.value) == (paused_minutes - 1), f"Error: Stopwatch did not resume correctly at the minute. Expected: {(paused_minutes - 1)}, Got: {int(dut.minutes.value)}"

async def pause_at_random_hour(dut,clk_freq):

    dut.start_stop.value = 1
    await RisingEdge(dut.clk)

    # Set initial state close to rollover
    random_hour = random.randint(1, 23)
    dut.load.value = 1
    dut.load_hours.value = random_hour
    dut.load_minutes.value = 59
    dut.load_seconds.value = 59
    await RisingEdge(dut.clk)
    dut.load.value = 0

    # Wait until the random hour is reached
    await wait_for_seconds(dut, 60 , clk_freq)

    # Pause the stopwatch
    dut.start_stop.value = 0
    paused_hours = int(dut.hours.value)

    # Ensure the stopwatch remains paused
    for _ in range(100):
        await RisingEdge(dut.clk)
        assert int(dut.hours.value) == paused_hours, "Error: Stopwatch did not remain paused at the hour."

    # Resume the stopwatch
    dut.start_stop.value = 1
    await wait_for_seconds(dut, 3600 , clk_freq)

    # Confirm it continues counting correctly
    assert int(dut.hours.value) == (paused_hours - 1), f"Error: Stopwatch did not resume correctly at the hour. Expected: {(paused_hours - 1)}, Got: {int(dut.hours.value)}"

async def test_out_of_range_values(dut):

    dut.load.value = 1
    dut.load_hours.value = 25  # Out of range, should be clamped to 23
    dut.load_minutes.value = 61  # Out of range, should be clamped to 59
    dut.load_seconds.value = 62  # Out of range, should be clamped to 59


    await Timer(1, units='ns')  
    assert int(dut.hours.value) == 23, f"Error: Hours not clamped to 23! Got: {dut.hours.value}"
    assert int(dut.minutes.value) == 59, f"Error: Minutes not clamped to 59! Got: {dut.minutes.value}"
    assert int(dut.seconds.value) == 59, f"Error: Seconds not clamped to 59! Got: {dut.seconds.value}"
    
    await RisingEdge(dut.clk)
    dut.load.value = 0
# Task to test simultaneous load and start_stop signals
async def test_load_and_start_stop_simultaneously(dut,clk_freq):

    # Load some initial random values
    dut.load.value = 1
    dut.load_hours.value = 5
    dut.load_minutes.value = 30
    dut.load_seconds.value = 15
    
    await Timer(1, units='ns')
    # Verify that the load values are correctly applied
    assert int(dut.hours.value) == 5, f"Load priority failed for hours! Got: {dut.hours.value}"
    assert int(dut.minutes.value) == 30, f"Load priority failed for minutes! Got: {dut.minutes.value}"
    assert int(dut.seconds.value) == 15, f"Load priority failed for seconds! Got: {dut.seconds.value}"
    
    await RisingEdge(dut.clk)
    dut.load.value = 0
    
    dut.start_stop.value = 1

    for _ in range(50):
        await RisingEdge(dut.clk)

    # Assert load and start_stop simultaneously
    dut.load.value = 1
    dut.load_hours.value = 10
    dut.load_minutes.value = 45
    dut.load_seconds.value = 50

    await Timer(1, units='ns')
    # Verify that the load values are correctly applied
    assert int(dut.hours.value) == 10, f"Load priority failed for hours! Got: {dut.hours.value}"
    assert int(dut.minutes.value) == 45, f"Load priority failed for minutes! Got: {dut.minutes.value}"
    assert int(dut.seconds.value) == 50, f"Load priority failed for seconds! Got: {dut.seconds.value}"

    # Deassert load while keeping start_stop active
    dut.load.value = 0
    await RisingEdge(dut.clk)

    # Wait for a few seconds to confirm the timer starts counting down correctly
    await wait_for_seconds(dut, 2, clk_freq)

    assert (
        int(dut.hours.value) == 10 and
        int(dut.minutes.value) == 45 and
        int(dut.seconds.value) == 50-2
    ), f"Timer did not resume correctly! Got: {int(dut.hours.value)}:{int(dut.minutes.value)}:{int(dut.seconds.value)}"
    # Stop the timer
    dut.start_stop.value = 0
    await RisingEdge(dut.clk)

@cocotb.test()
async def test_timer(dut):
    clk_freq = int(dut.CLK_FREQ.value)

    PERIOD = int(1_000_000_000 / clk_freq)  # Calculate clock period in ns
    cocotb.start_soon(Clock(dut.clk, PERIOD // 2, units='ns').start())

    await hrs_lb.dut_init(dut)
    await hrs_lb.reset_dut(dut.reset, duration_ns=PERIOD, active=False)

    assert dut.seconds.value == 0, f"Initial seconds is not 0! Got: {dut.seconds.value}"
    assert dut.minutes.value == 0, f"Initial minutes is not 0! Got: {dut.minutes.value}"
    assert dut.hours.value == 0, f"Initial hours is not 0! Got: {dut.hour.value}"

    await RisingEdge(dut.clk)
    await test_random_load(dut)

     # Start the stopwatch
    dut.start_stop.value = 1
    await wait_for_seconds(dut, 20 , clk_freq)
    initial_seconds = int(dut.seconds.value)

    # Stop the stopwatch  
    dut.start_stop.value = 0
    await RisingEdge(dut.clk)
    stopped_seconds = int(dut.seconds.value)

    await RisingEdge(dut.clk)
    assert int(dut.seconds.value) == stopped_seconds, "Stopwatch did not stop as expected."

    await RisingEdge(dut.clk)
    await check_rollover(dut,clk_freq)

    await RisingEdge(dut.clk)
    await check_hold_at_zero(dut, clk_freq)

    await RisingEdge(dut.clk)
    await check_pause_and_resume(dut, clk_freq)

    dut.reset.value = 1
    await Timer(1, units='ns')

    assert dut.seconds.value == 0, f"Reset failed for seconds! Got: {dut.seconds.value}"
    assert dut.minutes.value == 0, f"Reset failed for minutes! Got: {dut.minutes.value}"
    assert dut.hours.value == 0, f"Reset failed for hours! Got: {dut.hour.value}"
    await RisingEdge(dut.clk)

    dut.reset.value = 0
    await RisingEdge(dut.clk)
    await pause_at_random_second(dut)

    await RisingEdge(dut.clk)
    await pause_at_random_minute(dut,clk_freq)

    await RisingEdge(dut.clk)
    await pause_at_random_hour(dut,clk_freq)

    await RisingEdge(dut.clk)
    await test_out_of_range_values(dut)

    await RisingEdge(dut.clk)
    await test_load_and_start_stop_simultaneously(dut,clk_freq)

    await RisingEdge(dut.clk)
