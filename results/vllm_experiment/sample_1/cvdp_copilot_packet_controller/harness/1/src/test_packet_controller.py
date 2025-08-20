import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random

##################################################################
#  Common Tasks / Utilities
##################################################################

async def init_clock(dut):
    """Initialize a 10ns clock on dut.clk."""
    clock = Clock(dut.clk, 10, units='ns')
    cocotb.start_soon(clock.start())

async def reset_dut(dut):
    """Apply reset for ~50 ns total."""
    dut.rst.value = 1
    # Wait ~30 ns
    await Timer(30, units='ns')
    dut.rst.value = 0
    # Additional ~20 ns settle
    await Timer(20, units='ns')

async def wait_cycles(dut, n):
    """Wait for n rising edges."""
    for _ in range(n):
        await RisingEdge(dut.clk)

async def send_byte(dut, data):
    """Send one byte to the DUT: rx_data_8_i=data for exactly 1 clock."""
    await RisingEdge(dut.clk)
    dut.rx_data_8_i.value = data
    dut.rx_valid_i.value = 1
    await RisingEdge(dut.clk)
    dut.rx_valid_i.value = 0

async def do_tx_done(dut):
    """Pulse tx_done_tick_i for one clock cycle."""
    await RisingEdge(dut.clk)
    dut.tx_done_tick_i.value = 1
    await RisingEdge(dut.clk)
    dut.tx_done_tick_i.value = 0

async def drive_valid_packet(dut, header, num1, num2, opcode):
    """
    Drive 8 bytes:
      header[15:8], header[7:0], num1[15:8], num1[7:0],
      num2[15:8], num2[7:0], opcode, final_cksum
    ensuring sum mod 256 == 0.
    Then wait 10 cycles for the DUT to parse.
    """
    sum_local = ((header >> 8) & 0xFF) + (header & 0xFF) \
              + ((num1 >> 8) & 0xFF) + (num1 & 0xFF) \
              + ((num2 >> 8) & 0xFF) + (num2 & 0xFF) \
              + (opcode & 0xFF)
    sum_local = sum_local % 256
    final_cksum = (0 - sum_local) & 0xFF

    await send_byte(dut, (header >> 8) & 0xFF)
    await send_byte(dut, header & 0xFF)
    await send_byte(dut, (num1 >> 8) & 0xFF)
    await send_byte(dut, num1 & 0xFF)
    await send_byte(dut, (num2 >> 8) & 0xFF)
    await send_byte(dut, num2 & 0xFF)
    await send_byte(dut, opcode)
    await send_byte(dut, final_cksum)

    await wait_cycles(dut, 10)

async def check_5byte_response(dut, expected_result):
    """
    Expect 5 bytes: 0xAB, 0xCD, result_hi, result_lo, xmit_cksum.
    For each byte i2 in 0..4:
      1) Wait up to 50 cycles for tx_start_o=1.
      2) Wait 1 cycle => capture tx_data_8_o.
      3) Pulse do_tx_done(dut).
      4) Wait 1 extra cycle to allow re-assert of tx_start_o for next byte.
    """
    rxed = []
    for i2 in range(5):
        # Step 1) Wait up to 50 cycles for tx_start_o=1
        waitcount = 0
        while (dut.tx_start_o.value == 0) and (waitcount < 50):
            await RisingEdge(dut.clk)
            waitcount += 1
        if dut.tx_start_o.value == 0:
            print(f"ERROR: Timed out waiting for tx_start_o on byte {i2}")
            assert False, f"Tx_start_o not asserted for byte {i2}"

        # Step 2) Wait 1 cycle => read data
        await RisingEdge(dut.clk)
        rxed_byte = int(dut.tx_data_8_o.value)
        rxed.append(rxed_byte)

        # Step 3) do_tx_done => design sees we finished
        await do_tx_done(dut)

        # Step 4) Wait 1 cycle => let design re-assert tx_start_o if needed
        await RisingEdge(dut.clk)

    # Check the 5 bytes
    if rxed[0] != 0xAB:
        print(f"ERROR: Expected 0xAB, got 0x{rxed[0]:02X}")
        assert False
    if rxed[1] != 0xCD:
        print(f"ERROR: Expected 0xCD, got 0x{rxed[1]:02X}")
        assert False

    if rxed[2] != ((expected_result >> 8) & 0xFF):
        print(f"ERROR: result_hi mismatch. Exp=0x{(expected_result>>8)&0xFF:02X}, got=0x{rxed[2]:02X}")
        assert False

    if rxed[3] != (expected_result & 0xFF):
        print(f"ERROR: result_lo mismatch. Exp=0x{expected_result & 0xFF:02X}, got=0x{rxed[3]:02X}")
        assert False

    partial_sum = (rxed[0] + rxed[1] + rxed[2] + rxed[3]) & 0xFF
    exp_cksum = (0 - partial_sum) & 0xFF
    if rxed[4] != exp_cksum:
        print(f"ERROR: xmit_checksum mismatch. Exp=0x{exp_cksum:02X}, got=0x{rxed[4]:02X}")
        assert False

async def check_no_response(dut):
    """Check if we see any tx_start_o for 20 cycles => if yes => error."""
    saw_tx = False
    for _ in range(20):
        await RisingEdge(dut.clk)
        if dut.tx_start_o.value:
            saw_tx = True
    if saw_tx:
        print("ERROR: DUT responded despite invalid packet!")
        assert False

async def random_valid_packets(dut, count):
    """Send 'count' random packets => 0xBACD => random num1/num2 => add/sub => check result."""
    for k in range(count):
        rnd_num1 = random.getrandbits(16)
        rnd_num2 = random.getrandbits(16)
        rnd_opcode = 0x00 if (random.randint(0,1) == 0) else 0x01
        print(f"Random Packet #{k}: opcode=0x{rnd_opcode:X}, num1={rnd_num1}, num2={rnd_num2}")

        await drive_valid_packet(dut, 0xBACD, rnd_num1, rnd_num2, rnd_opcode)
        if rnd_opcode == 0x00:  # add
            expected = (rnd_num1 + rnd_num2) & 0xFFFF
        else:                   # sub
            expected = (rnd_num1 - rnd_num2) & 0xFFFF

        await check_5byte_response(dut, expected)


##################################################################
#  Individual Tests
##################################################################

@cocotb.test()
async def test_add(dut):
    """Test #1: ADD => 16 + 32 = 48 => 0x0030"""
    await init_clock(dut)
    await reset_dut(dut)
    print("Test #1: ADD => 16 + 32 = 48")
    await drive_valid_packet(dut, 0xBACD, 16, 32, 0x00)
    await check_5byte_response(dut, 0x0030)
    print("Test #1 passed.\n")

@cocotb.test()
async def test_sub(dut):
    """Test #2: SUB => 100 - 75 = 25 => 0x0019"""
    await init_clock(dut)
    await reset_dut(dut)
    print("Test #2: SUB => 100 - 75 = 25")
    await drive_valid_packet(dut, 0xBACD, 100, 75, 0x01)
    await check_5byte_response(dut, 0x0019)
    print("Test #2 passed.\n")

@cocotb.test()
async def test_unknown_opcode(dut):
    """Test #3: unknown opcode => 0 result."""
    await init_clock(dut)
    await reset_dut(dut)
    print("Test #3: unknown opcode => result=0")
    await drive_valid_packet(dut, 0xBACD, 10, 20, 0xAB)
    await check_5byte_response(dut, 0x0000)
    print("Test #3 passed.\n")

@cocotb.test()
async def test_invalid_checksum(dut):
    """Test #4: invalid checksum => no response."""
    await init_clock(dut)
    await reset_dut(dut)
    print("Test #4: invalid checksum => no response expected")

    # BA CD 00 10 00 20 00 FF => wait => check no response
    await send_byte(dut, 0xBA)
    await send_byte(dut, 0xCD)
    await send_byte(dut, 0x00)
    await send_byte(dut, 0x10)
    await send_byte(dut, 0x00)
    await send_byte(dut, 0x20)
    await send_byte(dut, 0x00)
    await send_byte(dut, 0xFF)
    await wait_cycles(dut, 10)

    await check_no_response(dut)
    print("Test #4 passed.\n")

@cocotb.test()
async def test_add_zero(dut):
    """Test #5: ADD => 0 + 0 => 0 result."""
    await init_clock(dut)
    await reset_dut(dut)
    print("Test #5: ADD => 0 + 0 = 0")
    await drive_valid_packet(dut, 0xBACD, 0, 0, 0x00)
    await check_5byte_response(dut, 0x0000)
    print("Test #5 passed.\n")

@cocotb.test()
async def test_sub_negative(dut):
    """Test #6: SUB => 50 - 100 => -50 => 0xFFCE (2's complement)."""
    await init_clock(dut)
    await reset_dut(dut)
    print("Test #6: SUB => 50 - 100 => 0xFFCE (assuming wrap).")
    await drive_valid_packet(dut, 0xBACD, 50, 100, 0x01)
    await check_5byte_response(dut, 0xFFCE)
    print("Test #6 passed.\n")

@cocotb.test()
async def test_add_large(dut):
    """Test #7: ADD => 0x8000 + 0x7FFF => 0xFFFF."""
    await init_clock(dut)
    await reset_dut(dut)
    print("Test #7: ADD => 0x8000 + 0x7FFF => 0xFFFF")
    await drive_valid_packet(dut, 0xBACD, 0x8000, 0x7FFF, 0x00)
    await check_5byte_response(dut, 0xFFFF)
    print("Test #7 passed.\n")

@cocotb.test()
async def test_back_to_back(dut):
    """Test #8: Two back-to-back packets => minimal idle time."""
    await init_clock(dut)
    await reset_dut(dut)
    print("Test #8: Two back-to-back => ADD(5+7=12), SUB(20-15=5)")

    # 1) 5+7=12 => 0x000C
    await drive_valid_packet(dut, 0xBACD, 5, 7, 0x00)
    await check_5byte_response(dut, 0x000C)

    # 2) 20-15=5 => 0x0005
    await drive_valid_packet(dut, 0xBACD, 20, 15, 0x01)
    await check_5byte_response(dut, 0x0005)
    print("Test #8 passed.\n")

@cocotb.test()
async def test_random_pkts(dut):
    """Test #9: Random valid packets => 3 times."""
    await init_clock(dut)
    await reset_dut(dut)
    print("Test #9: Random Packets => 3 times")
    await random_valid_packets(dut, 3)
    print("Test #9 passed.\n")

@cocotb.test()
async def test_invalid_header(dut):
    """Test #10: Additional invalid header => no response."""
    await init_clock(dut)
    await reset_dut(dut)
    print("Test #10: Invalid header => no response")

    # 0xDE, 0xAD, plus 6 more zeros
    await send_byte(dut, 0xDE)
    await send_byte(dut, 0xAD)
    for _ in range(6):
        await send_byte(dut, 0x00)
    await wait_cycles(dut, 5)

    await check_no_response(dut)
    print("Test #10 passed.\n")
