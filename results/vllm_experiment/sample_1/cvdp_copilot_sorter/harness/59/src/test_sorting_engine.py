import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import random

async def reset_dut(dut):
    dut.rst.value = 1
    dut.start.value = 0
    dut.in_data.value = 0
    for _ in range(2):
        await RisingEdge(dut.clk)
    dut.rst.value = 0
    await RisingEdge(dut.clk)

def expected_insertion_sort_operations(arr):
    """
    Compute the expected "latency" in terms of operations for an insertion sort on 'arr'.
    We'll count the number of comparisons made during a standard insertion sort.
    """
    # Make a copy to avoid modifying the original array
    data = arr[:]
    operations = 0
    for i in range(1, len(data)):
        operations += 1
        key = data[i]
        j = i - 1

        # In insertion sort, for each element, we compare with previous elements until we find the spot.
        # Count a comparison for each j we test. If we have to move past array[j], that's another comparison.
        while j >= 0 and data[j] > key:
            operations += 1  # comparison
            data[j+1] = data[j]
            j -= 1
        # Even when we break out of loop, we've done one more comparison that fails the condition.
        operations += 1  # comparison to exit the loop
        data[j+1] = key
    operations += (len(data) +2)
    return operations

async def run_sort_test(dut, input_array, N, WIDTH):
    """
    Helper function to run a sort test with a given input_array.
    Returns the number of cycles it took to complete sorting.
    Also compares actual latency with expected operations count.
    """
    # Reset the DUT before each test
    await reset_dut(dut)

    # Pack the input array into a single integer
    in_val = 0
    for i, val in enumerate(input_array):
        in_val |= (val << (i * WIDTH))

    dut._log.info(f"Testing with input: {input_array}")
    dut.in_data.value = in_val

    # Start sorting
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    # Measure how many cycles it takes until done
    cycles = 0
    while True:
        #print("State = ",dut.state.value)
        #print("insert_phase = ",dut.insert_phase.value)
        #print("i = ",dut.i.value)
        #print(*dut.array.value)
        await RisingEdge(dut.clk)
        cycles += 1
        if dut.done.value.to_unsigned() == 1:
            break

    # Once done is high, read out the sorted result
    sorted_val = dut.out_data.value.to_unsigned()
    output_array = []
    for i in range(N):
        chunk = (sorted_val >> (i * WIDTH)) & ((1 << WIDTH) - 1)
        output_array.append(chunk)

    dut._log.info(f"Sorted output after {cycles} cycles: {output_array}")

    # Check correctness
    expected = sorted(input_array)
    assert output_array == expected, f"DUT output {output_array} does not match expected {expected}"
    dut._log.info("Output is correctly sorted.")

    # Compute expected operations for a standard insertion sort on input_array
    exp_ops = expected_insertion_sort_operations(input_array)
    assert exp_ops == cycles, f"Expected latency is not equal to actual latency"

    return cycles

@cocotb.test()
async def test_sorting_engine(dut):
    """Test the insertion sort engine with various cases and compare actual latency to expected operations."""
    # Parameters (these should match the DUT)
    N = int(dut.N.value)
    WIDTH = int(dut.WIDTH.value)

    # Start a clock
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Test cases
    max_val = (1 << WIDTH) - 1

    test_cases = [
        [i for i in range(N)],  # ascending
        [N - 1 - i for i in range(N)],  # descending
        [5] * N,  # all same
        [0] * N,  # all minimum
        [max_val] * N,  # all maximum
        [0, max_val] + [random.randint(0, max_val) for _ in range(N - 2)]  # mixed
    ]

    # Add multiple random tests
    for _ in range(5):
        test_cases.append([random.randint(0, max_val) for _ in range(N)])

    # Run all tests
    for test_input in test_cases:
        await run_sort_test(dut, test_input, N, WIDTH)

    dut._log.info("All tests completed successfully with latency checks against expected insertion sort operations.")
