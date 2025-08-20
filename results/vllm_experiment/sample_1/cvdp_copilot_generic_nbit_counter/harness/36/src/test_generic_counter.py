import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles, Timer

# ----------------------------------------
# - Tests
# ----------------------------------------

async def init_dut(dut):

    dut.rst_in.value     = 1
    dut.mode_in.value    = 0
    dut.enable_in.value  = 0
    dut.ref_modulo.value = 0
    await RisingEdge(dut.clk_in)

@cocotb.test()
async def test_reset(dut):
    cocotb.start_soon(Clock(dut.clk_in, 10, units='ns').start())
    await init_dut(dut)

    # ----------------------------------------
    # - Test Reset Functionality
    # ----------------------------------------

    dut.mode_in.value   = 5  # Select Ring counter
    dut.enable_in.value = 1  # Enable the counter

    await RisingEdge(dut.clk_in)
    dut.rst_in.value    = 0  # Deassert reset

    # Count up to a certain value
    for i in range(5):
        await RisingEdge(dut.clk_in)

    # Assert reset
    dut.rst_in.value = 1
    await RisingEdge(dut.clk_in)
    assert dut.o_count.value == 0, "Counter did not reset to 0"

    # Deassert reset and continue counting
    dut.rst_in.value = 0
    await RisingEdge(dut.clk_in)


@cocotb.test()
async def test_ring_counter(dut):

    cocotb.start_soon(Clock(dut.clk_in, 10, units='ns').start())
    await init_dut(dut)

    # ----------------------------------------
    # - Check No Operation
    # ----------------------------------------

    await FallingEdge(dut.clk_in)

    dut.mode_in.value   = 5 # Testing Ring Counter
    dut.enable_in.value = 0 
    
    await RisingEdge(dut.clk_in)
    dut.rst_in.value    = 0

    await FallingEdge(dut.clk_in)
    dut.enable_in.value = 1

    for _ in range(5):
        await FallingEdge(dut.clk_in)

    assert dut.o_count.value == 2 ** 4

@cocotb.test()
async def test_up_counter(dut):

    cocotb.start_soon(Clock(dut.clk_in, 10, units='ns').start())

    # ----------------------------------------
    # - Check No Operation
    # ----------------------------------------

    dut.rst_in.value    = 1
    await FallingEdge(dut.clk_in)

    dut.mode_in.value   = 0 # Testing Up Counter
    dut.enable_in.value = 0 
    
    
    await FallingEdge(dut.clk_in)
    dut.enable_in.value = 1

    await RisingEdge(dut.clk_in) 
    dut.rst_in.value    = 0

    for i in range(256):
        await RisingEdge(dut.clk_in)
        assert dut.o_count.value == i
    
@cocotb.test()
async def test_down_counter(dut):

    cocotb.start_soon(Clock(dut.clk_in, 10, units='ns').start())

    # ----------------------------------------
    # - Check No Operation
    # ----------------------------------------

    dut.rst_in.value    = 1
    await FallingEdge(dut.clk_in)

    dut.mode_in.value   = 1 # Testing down converter
    dut.enable_in.value = 0 # 
    
    
    await FallingEdge(dut.clk_in)
    dut.enable_in.value = 1

    await RisingEdge(dut.clk_in) 
    dut.rst_in.value    = 0


    await RisingEdge(dut.clk_in) 
    for i in range(255, -1, -1):
        await RisingEdge(dut.clk_in)
        assert dut.o_count.value == i

@cocotb.test()
async def test_johnson_counter(dut):

    cocotb.start_soon(Clock(dut.clk_in, 10, units='ns').start())

    # ----------------------------------------
    # - Check No Operation
    # ----------------------------------------

    dut.rst_in.value    = 1
    await FallingEdge(dut.clk_in)

    dut.mode_in.value   = 3 # Testing Johnson Counter
    dut.enable_in.value = 0 # 
    
    
    await FallingEdge(dut.clk_in)
    dut.enable_in.value = 1

    await RisingEdge(dut.clk_in)
    dut.rst_in.value    = 0

    johnson_sequence = [0, 128, 192, 224, 240, 248, 252, 254, 255, 127, 63, 31, 15, 7, 3, 1]
    for i in range(16):
        await RisingEdge(dut.clk_in)
        assert dut.o_count.value == johnson_sequence[i]


def generate_gray_code(n):
    """Generate an n-bit Gray code sequence."""
    gray_code = []
    for i in range(2**n):
        gray_code.append(i ^ (i >> 1))
    return gray_code



@cocotb.test()
async def test_mod_256(dut):

    cocotb.start_soon(Clock(dut.clk_in, 10, units='ns').start())

    # ----------------------------------------
    # - Check No Operation
    # ----------------------------------------

    dut.rst_in.value    = 1
    await FallingEdge(dut.clk_in)

    dut.mode_in.value   = 2 # Testing Up Counter
    dut.ref_modulo.value   = 255 # Testing Up Counter
    dut.enable_in.value = 0 
    
    
    await FallingEdge(dut.clk_in)
    dut.enable_in.value = 1

    await RisingEdge(dut.clk_in) 
    dut.rst_in.value    = 0

    for i in range(256):
        await RisingEdge(dut.clk_in)
        assert dut.o_count.value == i



@cocotb.test()
async def test_gray_counter(dut):
    N = 4  # Bit width
    cocotb.start_soon(Clock(dut.clk_in, 10, units='ns').start())

    # ----------------------------------------
    # - Check No Operation
    # ----------------------------------------

    dut.rst_in.value    = 1
    await FallingEdge(dut.clk_in)

    dut.mode_in.value   = 4  # Testing Gray Counter
    dut.enable_in.value = 0  # 
    
    await FallingEdge(dut.clk_in)
    dut.enable_in.value = 1

    await RisingEdge(dut.clk_in)
    dut.rst_in.value    = 0

    # Generate Gray code sequence for N-bit counter
    gray_sequence = generate_gray_code(N)

    for i in range(2**N):
        await RisingEdge(dut.clk_in)
        assert dut.o_count.value == gray_sequence[i], f"Gray code mismatch at step {i}: expected {gray_sequence[i]}, got {dut.o_count.value}"

@cocotb.test()
async def test_enable(dut):

    cocotb.start_soon(Clock(dut.clk_in, 10, units='ns').start())
    await init_dut(dut)

    # ----------------------------------------
    # - Check No Operation
    # ----------------------------------------

    await FallingEdge(dut.clk_in)

    dut.mode_in.value   = 5 # Testing Ring Counter
    dut.enable_in.value = 0 
    
    await RisingEdge(dut.clk_in)
    dut.rst_in.value    = 0

    await FallingEdge(dut.clk_in)
    dut.enable_in.value = 1

    for _ in range(5):
        await FallingEdge(dut.clk_in)

    assert dut.o_count.value == 2 ** 4
    
    await FallingEdge(dut.clk_in)
    previous_o_count = dut.o_count.value
    dut.enable_in.value = 0 # make enable 0

    await FallingEdge(dut.clk_in)
    await FallingEdge(dut.clk_in) # wait for counter output
    assert dut.o_count.value == previous_o_count, f"Expected o_count to remain {previous_o_count}, but got {dut.o_count.value}"
