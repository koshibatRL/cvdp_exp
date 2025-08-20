import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random

def get_dice_value(dice_values, num_dice, bit_width, index):
    start = (num_dice - index - 1) * bit_width
    end = start + bit_width
    return (dice_values >> start) & ((1 << bit_width) - 1)

def display_dice_values(dut, test_case, num_dice, bit_width):
    print(f"Test Case: {test_case}")
    dice_values = dut.dice_values.value.to_unsigned()
    for i in range(num_dice):
        dice_value = get_dice_value(dice_values, num_dice, bit_width, i)
        print(f"Dice {i + 1} value: {dice_value}")

async def random_delay(min_cycles, max_cycles, clk_period):
    delay_cycles = random.randint(min_cycles, max_cycles)
    await Timer(delay_cycles * clk_period, units="ns")

@cocotb.test()
async def test_digital_dice_roller(dut):

    NUM_DICE = int(dut.NUM_DICE.value)
    DICE_MAX = int(dut.DICE_MAX.value)
    BIT_WIDTH = (DICE_MAX - 1).bit_length() + 1  
    CLK_PERIOD = 10  

    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD, units="ns").start())

    dut.reset.value = 0
    dut.button.value = 0

    print("Test Case 1: Assert asynchronous reset with random delay")
    await Timer(10, units="ns")
    dut.reset.value = 1
    await random_delay(5, 15, CLK_PERIOD)
    display_dice_values(dut, "After Reset", NUM_DICE, BIT_WIDTH)

    print("Test Case 2: Normal rolling behavior with random delay")
    dut.button.value = 1
    await random_delay(10, 20, CLK_PERIOD)
    dut.button.value = 0
    await random_delay(5, 10, CLK_PERIOD)
    display_dice_values(dut, "After Normal Rolling", NUM_DICE, BIT_WIDTH)

    print("Test Case 3: Quick button press with random delay")
    dut.button.value = 1
    await random_delay(1, 5, CLK_PERIOD)
    dut.button.value = 0
    await random_delay(5, 10, CLK_PERIOD)
    display_dice_values(dut, "After Quick Button Press", NUM_DICE, BIT_WIDTH)

    print("Test Case 4: Continuous rolling for random cycles")
    dut.button.value = 1
    await random_delay(15, 30, CLK_PERIOD)
    dut.button.value = 0
    await random_delay(5, 10, CLK_PERIOD)
    display_dice_values(dut, "After Continuous Rolling", NUM_DICE, BIT_WIDTH)

    print("Test Case 5: Reset during rolling with random delay")
    dut.button.value = 1
    await random_delay(5, 10, CLK_PERIOD)
    dut.reset.value = 0
    await random_delay(1, 3, CLK_PERIOD)
    dut.reset.value = 1
    dut.button.value = 0
    await random_delay(5, 10, CLK_PERIOD)
    display_dice_values(dut, "After Reset During Rolling", NUM_DICE, BIT_WIDTH)

    print("All test cases completed.")
