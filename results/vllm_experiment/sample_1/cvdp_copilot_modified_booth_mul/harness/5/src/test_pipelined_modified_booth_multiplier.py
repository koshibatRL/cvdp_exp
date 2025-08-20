import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random

def generate_signed_16_bit():
    value = random.randint(-32768, 32767)
    if value < 0:
        value = (1 << 16) + value  # Convert to two's complement
    return value

def signed_32_bit_result(a, b):
    # Convert back from two's complement if negative
    if a >= 32768:
        a -= 65536
    if b >= 32768:
        b -= 65536
    return a * b

async def reset_dut(dut, duration_ns=10):
    dut.rst.value = 1
    await Timer(duration_ns, units="ns")
    dut.rst.value = 0
    await RisingEdge(dut.clk)
    dut._log.info("Reset complete")

@cocotb.test()
async def test_pipelined_signed_multiplier(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())
    dut.start.value = 0
    dut.X.value = 0
    dut.Y.value = 0
    await reset_dut(dut)
    await RisingEdge(dut.clk)

    num_samples = 100
    test_vectors = [(generate_signed_16_bit(), generate_signed_16_bit()) for _ in range(num_samples)]

    expected_latency = 5
    output_queue = []
    input_queue = []
    latency = 0
    first_time = 1

    for cycle, (a, b) in enumerate(test_vectors):
        dut.X.value = a & 0xFFFF  # Mask to ensure it's treated as 16-bit
        dut.Y.value = b & 0xFFFF  # Mask to ensure it's treated as 16-bit
        input_queue.append((a, b))
        dut.start.value = 1

        expected_result = signed_32_bit_result(a, b)
        output_queue.append(expected_result)

        await RisingEdge(dut.clk)
        if dut.done.value == 0 and first_time == 1:
            latency += 1
            
        dut.start.value = 0
        await RisingEdge(dut.clk)
        
        if dut.done.value == 0 and first_time == 1:
            latency += 1
        elif dut.done.value == 1:
            actual_result = int(dut.result.value.to_signed())
            expected_result = output_queue.pop(0)
            input_a, input_b = input_queue.pop(0)

            assert latency == expected_latency, f"Cycle {cycle}: Expected latency {expected_latency}, got {latency}"
            first_time = 0
            assert actual_result == expected_result, f"Cycle {cycle}: Input A={input_a} ({input_a}), B={input_b} ({input_b}) Expected result {expected_result}, got {actual_result}"
            dut._log.info(f"Cycle {cycle}: Input A={input_a} ({input_a}), B={input_b} ({input_b})")
            dut._log.info(f"Cycle {cycle}: Expected result={expected_result}")
            dut._log.info(f"Cycle {cycle}: Actual result={actual_result}")


@cocotb.test()
async def test_pipelined_signed_multiplier(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())
    dut.start.value = 0
    dut.X.value = 0
    dut.Y.value = 0
    await reset_dut(dut)
    await RisingEdge(dut.clk)

    num_samples = 100
    test_vectors = [(generate_signed_16_bit(), generate_signed_16_bit()) for _ in range(num_samples)]

    expected_latency = 5
    output_queue = []
    input_queue = []
    latency = 0
    first_time = 1

    for cycle, (a, b) in enumerate(test_vectors):
        dut.X.value = a & 0xFFFF  # Mask to ensure it's treated as 16-bit
        dut.Y.value = b & 0xFFFF  # Mask to ensure it's treated as 16-bit
        input_queue.append((a, b))
        dut.start.value = 1

        expected_result = signed_32_bit_result(a, b)
        output_queue.append(expected_result)

        await RisingEdge(dut.clk)
        
        if dut.done.value == 0 and first_time == 1:
            latency += 1
        elif dut.done.value == 1:
            actual_result = int(dut.result.value.to_signed())
            expected_result = output_queue.pop(0)
            input_a, input_b = input_queue.pop(0)

            assert latency == expected_latency, f"Cycle {cycle}: Expected latency {expected_latency}, got {latency}"
            first_time = 0
            assert actual_result == expected_result, f"Cycle {cycle}: Input A={input_a} ({input_a}), B={input_b} ({input_b}) Expected result {expected_result}, got {actual_result}"
            dut._log.info(f"Cycle {cycle}: Input A={input_a} ({input_a}), B={input_b} ({input_b})")
            dut._log.info(f"Cycle {cycle}: Expected result={expected_result}")
            dut._log.info(f"Cycle {cycle}: Actual result={actual_result}")

