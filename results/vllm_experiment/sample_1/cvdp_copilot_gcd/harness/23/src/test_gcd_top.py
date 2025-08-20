import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import random

# Software GCD using Stein’s algorithm for verification
def stein_gcd(a, b):
    if a == 0 and b == 0:
        return 0
    elif a == 0 and b != 0:
        return b
    elif a != 0 and b == 0:
        return a

    # Factor out powers of 2
    shift = 0
    while (((a | b) & 1) == 0):  # both even
        a >>= 1
        b >>= 1
        shift += 1
    # Make sure a is odd
    while ((a & 1) == 0):
        a >>= 1

    # Algorithm loop
    while b != 0:
        while ((b & 1) == 0):
            b >>= 1
        if a > b:
            a, b = b, a
        b = b - a
    # Restore common factors of 2
    return a << shift

def simulate_hw_latency(a, b):
    """
    Simulate the hardware step-by-step latency of Stein’s algorithm.
    This matches the logic in the datapath and controlpath:
    - Start from state S0 (idle), inputs loaded into A_ff, B_ff.
    - Next cycle move to S2 (processing).
    - Each cycle in S2 applies one step of Stein’s algorithm.
    - When A_ff == B_ff (equal), next cycle is S1 (done).
    - We count how many cycles pass from the moment 'go' is deasserted
      and we start checking for done, until done=1.

    Return the total number of cycles (latency) that the hardware
    would take for given inputs A and B.
    """

    # Internal copies representing the hardware registers
    A_ff = a
    B_ff = b
    k_ff = 0

    # The testbench starts counting latency after go=0,
    # at the next cycle the FSM enters S2.
    # Let's count cycles in S2 until done.
    latency = 0

    # The hardware runs until A_ff == B_ff for done signaling
    # On equality, the next cycle goes to S1 (done).
    # So we loop until equal is found.
    while True:
        # Check conditions at the start of each S2 cycle
        a_even = ((A_ff & 1) == 0)
        b_even = ((B_ff & 1) == 0)
        both_even = a_even and b_even
        equal = (A_ff == B_ff)

        if equal:
            # Equal found, next cycle will be done=1.
            # So, one more cycle needed to reach done.
            latency += 1
            break

        # Apply Stein's step for one cycle
        if (A_ff != 0) and (B_ff != 0):
            # Both nonzero
            if both_even:
                A_ff >>= 1
                B_ff >>= 1
                k_ff += 1
            elif a_even and not b_even:
                A_ff >>= 1
            elif b_even and not a_even:
                B_ff >>= 1
            else:
                # Both odd
                if A_ff >= B_ff:
                    diff = A_ff - B_ff
                    A_ff = diff >> 1
                    # B_ff stays the same
                else:
                    diff = B_ff - A_ff
                    B_ff = diff >> 1
                    # A_ff stays the same
        elif A_ff == 0 and B_ff != 0:
            # One zero, one nonzero
            A_ff = B_ff
            B_ff = B_ff
        elif B_ff == 0 and A_ff != 0:
            A_ff = A_ff
            B_ff = A_ff
        # If both zero, they are equal and done next cycle anyway.

        # Completed one processing cycle
        latency += 1

    return latency

# Coroutine to reset the DUT
async def reset_dut(dut):
    dut.rst.value = 1
    dut.go.value  = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.OUT.value == 0, f"Reset Test failed OUT Expected 0, got {int(dut.OUT.value)}"
    assert dut.done.value == 0, f"Reset Test failed done Expected 0, got {int(dut.done.value)}"
    dut.rst.value = 0
    await RisingEdge(dut.clk)
    assert dut.OUT.value == 0, f"Reset Test failed OUT Expected 0, got {int(dut.OUT.value)}"
    assert dut.done.value == 0, f"Reset Test failed done Expected 0, got {int(dut.done.value)}"


async def run_test_case(dut, A, B):
    """Helper function to run a single test case on the DUT and verify results and latency."""
    # Apply inputs
    dut.A.value  = A
    dut.B.value  = B
    dut.go.value = 1

    # Wait one cycle and de-assert go
    await RisingEdge(dut.clk)
    dut.go.value = 0

    # Measure actual latency from this point until done=1
    actual_latency = 0
    while (dut.done.value == 0):
        await RisingEdge(dut.clk)
        actual_latency += 1

    # Compare the result with expected GCD from Stein’s algorithm
    expected_gcd = stein_gcd(A, B)
    got_gcd = int(dut.OUT.value)
    assert got_gcd == expected_gcd, f"GCD mismatch for A={A}, B={B}. Expected {expected_gcd}, got {got_gcd}"

    # Compute expected latency by simulating the hardware steps
    expected_latency = simulate_hw_latency(A, B) + 2

    # Compare actual latency with expected latency
    assert actual_latency == expected_latency, f"Latency mismatch for A={A}, B={B}. Expected {expected_latency}, got {actual_latency}"

    # Print results for debugging
    dut._log.info(f"Testcase A={A}, B={B}, Actual Latency={actual_latency}, Expected Latency={expected_latency}, GCD={got_gcd}")

@cocotb.test()
async def gcd_test(dut):
    """ Test GCD calculation for different combinations of A and B using Stein’s Algorithm """
    # Start the clock with 10ns period
    dut.A.value  = 0
    dut.B.value  = 0
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    width  = int(dut.WIDTH.value)
    max_val = (1 << width) - 1

    # Reset the DUT
    await reset_dut(dut)

    # Pre-defined corner and typical test cases
    test_cases = [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
        (4, 2),
        (6, 3),
        (15, 5),
        (8, 4),
        (9, 6),
        (12, 8),
        (14, 7),
        (max_val, 1),
        (max_val, max_val),
    ]

    # Test all pre-defined test cases
    for A, B in test_cases:
        await run_test_case(dut, A, B)

    # Reset the DUT at the end
    await reset_dut(dut)


@cocotb.test()
async def gcd_stress_test(dut):
    """ Stress test GCD calculation with random values """
    # Start the clock
    dut.A.value  = 0
    dut.B.value  = 0
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset the DUT
    await reset_dut(dut)
    width  = int(dut.WIDTH.value)
    max_val = (1 << width) - 1

    # Random test cases including zeros and max values
    random_cases = [
        (0, random.randint(0, max_val)),
        (random.randint(0, max_val), 0),
        (max_val, random.randint(0, max_val)),
        (random.randint(0, max_val), max_val),
        (max_val, max_val),
        (0, 0)
    ]

    # Add more random pairs
    for _ in range(20):
        A = random.randint(0, max_val)
        B = random.randint(0, max_val)
        random_cases.append((A, B))

    for A, B in random_cases:
        await run_test_case(dut, A, B)

    # Reset at the end
    await reset_dut(dut)


@cocotb.test()
async def gcd_extreme_random_test(dut):
    """ Extensive random tests to ensure broad coverage """
    # Start the clock
    dut.A.value  = 0
    dut.B.value  = 0
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    await reset_dut(dut)
    width  = int(dut.WIDTH.value)
    max_val = (1 << width) - 1

    # Run a large number of random test cases
    for _ in range(100):
        A = random.randint(0, max_val)
        B = random.randint(0, max_val)
        await run_test_case(dut, A, B)

    # Reset at the end
    await reset_dut(dut)
