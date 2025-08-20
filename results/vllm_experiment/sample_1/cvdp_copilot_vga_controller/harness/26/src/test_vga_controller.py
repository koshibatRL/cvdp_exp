import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.result import TestSuccess

# Constants for VGA timing (640x480 @ 25 MHz)
TB_H_ACTIVE = 640
TB_H_FRONT  = 16
TB_H_PULSE  = 96
TB_H_BACK   = 48

TB_V_ACTIVE = 480
TB_V_FRONT  = 10
TB_V_PULSE  = 2
TB_V_BACK   = 33

# Clock period (25 MHz)
CLOCK_PERIOD_NS = 40

@cocotb.test()
async def test_vga_controller(dut):
    """VGA Controller Test with hsync and vsync monitoring."""

    # Initialize signals
    dut.clock.value = 0
    dut.reset.value = 0
    dut.color_in.value = 0b11111111  # White color

    # Calculate total cycles (Horizontal cycles * Vertical cycles)
    h_cycles = TB_H_ACTIVE + TB_H_FRONT + TB_H_PULSE + TB_H_BACK
    v_cycles = TB_V_ACTIVE + TB_V_FRONT + TB_V_PULSE + TB_V_BACK
    total_cycles = h_cycles * v_cycles

    # Start clock generation (25 MHz)
    cocotb.start_soon(clock_gen(dut, CLOCK_PERIOD_NS))

    # Apply reset
    dut.reset.value = 1
    await Timer(400, units="ns")
    dut.reset.value = 0
    dut._log.info(f"Reset de-asserted at {cocotb.regression.get_sim_time()} ns")

    # Wait a few clock cycles for the design to initialize
    for _ in range(5):
        await RisingEdge(dut.clock)

    # Wait until hsync and vsync are defined (i.e. not 'X')
    while 'X' in str(dut.hsync.value) or 'X' in str(dut.vsync.value):
        dut._log.info("Waiting for hsync and vsync to be defined...")
        await RisingEdge(dut.clock)

    # Initialize previous values for hsync and vsync
    prev_hsync = int(dut.hsync.value)
    prev_vsync = int(dut.vsync.value)

    # Monitor changes in hsync signal (horizontal timing)
    def monitor_hsync():
        nonlocal prev_hsync
        current = int(dut.hsync.value)
        if current != prev_hsync:
            dut._log.info(f"[TIME {cocotb.regression.get_sim_time()} ns] hsync transition: {prev_hsync} -> {current}")
            prev_hsync = current

    # Monitor changes in vsync signal (vertical timing)
    def monitor_vsync():
        nonlocal prev_vsync
        current = int(dut.vsync.value)
        if current != prev_vsync:
            dut._log.info(f"[TIME {cocotb.regression.get_sim_time()} ns] vsync transition: {prev_vsync} -> {current}")
            prev_vsync = current

    # Run simulation for one complete frame
    for _ in range(total_cycles + 10):
        monitor_hsync()
        monitor_vsync()
        await RisingEdge(dut.clock)

    dut._log.info(f"Simulation complete at {cocotb.regression.get_sim_time()} ns")
    raise TestSuccess("VGA Controller test completed successfully.")

async def clock_gen(dut, period_ns):
    """Clock generation for 25 MHz signal."""
    while True:
        dut.clock.value = 0
        await Timer(period_ns / 2, units="ns")
        dut.clock.value = 1
        await Timer(period_ns / 2, units="ns")

