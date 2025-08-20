import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random

# ----------------------------------------
# - Pipelined Adder Test
# ----------------------------------------

async def reset_dut(dut, duration_ns=10):
    dut.reset.value = 1  # Set reset to active high
    await Timer(duration_ns, units="ns")  # Wait for the specified duration
    dut.reset.value = 0  # Deactivate reset (set it low)
    await RisingEdge(dut.clk)
    dut._log.info("Reset complete")

@cocotb.test()
async def test_pipelined_adder_latency(dut):
    """
    Verify the pipelined 32-bit adder for initial latency and subsequent outputs.
    """
    # Start the clock with a 10ns period
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())
    dut.start.value = 0
    dut.A.value = 0
    dut.B.value = 0
    # Apply reset to DUT
    await reset_dut(dut)

    # Wait for a few clock cycles after reset
    await RisingEdge(dut.clk)

    # Generate test input vectors
    num_samples = 100
    test_vectors = [(random.randint(0, 0xFFFFFFFF), random.randint(0, 0xFFFFFFFF)) for _ in range(num_samples)]

    # Known latency of the pipelined adder
    expected_latency = 4
    output_queue = []
    input_queue = []  
    latency = 0

    # Apply inputs every cycle and collect expected outputs
    for cycle, (a, b) in enumerate(test_vectors):
        dut.A.value = a
        dut.B.value = b
        input_queue.append((a, b))
        dut.start.value = 1

        # Compute and store the expected results
        expected_sum = (a + b) & 0xFFFFFFFF
        expected_carry = (a + b) >> 32
        output_queue.append((expected_sum, expected_carry))

        await RisingEdge(dut.clk)
        # dut.start.value = 0

        if dut.done.value == 0:
            latency += 1
        else:
            actual_sum = int(dut.S.value)
            actual_carry = int(dut.Co.value)

            # Retrieve the corresponding inputs and expected outputs
            expected_sum, expected_carry = output_queue.pop(0)
            input_a, input_b = input_queue.pop(0)

            assert latency == expected_latency, f"Cycle {cycle}: Expected latency {expected_latency}, got {latency}"
            assert actual_sum == expected_sum, f"Cycle {cycle}: Expected sum {expected_sum}, got {actual_sum}"
            assert actual_carry == expected_carry, f"Cycle {cycle}: Expected carry {expected_carry}, got {actual_carry}"
            # Print input-output mapping
            print(f"Cycle {cycle}: Input A=0x{input_a:08X}, B=0x{input_b:08X}")
            print(f"Cycle {cycle}: Expected Sum=0x{expected_sum:08X}, Carry={expected_carry}")
            print(f"Cycle {cycle}: Actual Sum=0x{actual_sum:08X}, Carry={actual_carry}")
