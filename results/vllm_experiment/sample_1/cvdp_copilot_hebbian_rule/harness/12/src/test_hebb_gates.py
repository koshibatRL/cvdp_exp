import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random

@cocotb.test()
async def test_hebb_gates(dut):
    """Test the hebb_gates module with different gate selections and inputs."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    dut.rst.value = 0
    await Timer(10, units="ns")
    dut.rst.value = 1
    dut.start.value = 0
    dut.a.value = 0
    dut.b.value = 0
    dut.gate_select.value = 0
    await RisingEdge(dut.rst)
    await Timer(10, units="ns")

    async def view_signals(duration):
        """Pause for a specified duration and view the values of signals."""
        await Timer(duration, units="ns")
        cocotb.log.info(f"Observing signals after {duration}ns:")
        cocotb.log.info(f"gate_select={dut.gate_select.value}, a={dut.a.value}, b={dut.b.value}, w1={dut.w1.value.to_signed()}, w2={dut.w2.value.to_signed()}, bias={dut.bias.value.to_signed()}, state={bin(dut.present_state.value.to_unsigned())}, test_x1={dut.test_x1.value.to_signed()}, test_x2={dut.test_x2.value.to_signed()}, expected_output={dut.expected_output.value.to_signed()}, test_output={dut.test_output.value.to_signed()}, test_result={dut.test_result.value.to_signed()}, test_done={bin(dut.test_done.value.to_unsigned())}, test_present_state={bin(dut.test_present_state.value.to_unsigned())}, test_index={bin(dut.test_index.value.to_unsigned())}")

    async def apply_stimulus(a, b, gate_select, duration):
        dut.a.value = a
        dut.b.value = b
        dut.gate_select.value = gate_select
        await Timer(duration, units="ns")

    # Directed Test Cases
    dut.gate_select.value = 0b00
    dut.start.value = 1
    cocotb.log.info("Start of AND gate Training and Testing")
    await apply_stimulus(1, 1, 0b00, 60)
    await apply_stimulus(1, -1, 0b00, 60)
    await apply_stimulus(-1, 1, 0b00, 60)
    await apply_stimulus(-1, -1, 0b00, 60)
    # Assert statements for w1, w2, and bias
    assert dut.w1.value.to_signed() == 2, f"Expected w1=2, but got {dut.w1.value}"
    assert dut.w2.value.to_signed() == 2, f"Expected w2=2, but got {dut.w2.value}"
    assert dut.bias.value.to_signed() == -2, f"Expected bias=-2, but got {dut.bias.value}"
    await view_signals(100)
    assert dut.test_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_output.value}"
    await view_signals(75)
    assert dut.test_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_output.value}"
    await view_signals(80)
    assert dut.test_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_output.value}"
    await view_signals(80)
    assert dut.test_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_output.value}"
    
    cocotb.log.info("End of AND gate Training and Testing")
    
    
    dut.gate_select.value = 0b01
    cocotb.log.info("Start of OR gate Training and Testing")
    await apply_stimulus(1, 1, 0b01, 70)
    await apply_stimulus(-1, 1, 0b01, 60)
    await apply_stimulus(1, -1, 0b01, 60)
    await apply_stimulus(-1, -1, 0b01, 70)
    assert dut.w1.value.to_signed() == 2, f"Expected w1=2, but got {dut.w1.value}"
    assert dut.w2.value.to_signed() == 2, f"Expected w2=2, but got {dut.w2.value}"
    assert dut.bias.value.to_signed() ==  2, f"Expected bias= 2, but got {dut.bias.value}"
    await view_signals(80)
    assert dut.test_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_output.value}"
    await view_signals(80)
    assert dut.test_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_output.value}"
    await view_signals(80)
    assert dut.test_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_output.value}"
    await view_signals(80)
    assert dut.test_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_output.value}"
    cocotb.log.info("End of OR gate Training and Testing")

    dut.gate_select.value = 0b10
    cocotb.log.info("Start of NAND gate Training and Testing")
    await apply_stimulus(-1, -1, 0b10, 70)
    await apply_stimulus(-1, 1, 0b10, 60)
    await apply_stimulus(1, -1, 0b10, 60)
    await apply_stimulus(1, 1, 0b10, 70)
    assert dut.w1.value.to_signed() == -2, f"Expected w1=-2, but got {dut.w1.value}"
    assert dut.w2.value.to_signed() == -2, f"Expected w2=-2, but got {dut.w2.value}"
    assert dut.bias.value.to_signed() ==  2, f"Expected bias= 2, but got {dut.bias.value}"
    await view_signals(80)
    assert dut.test_output.value.to_signed() == 1, f"Expected test_output= 1, but got {dut.test_output.value}"
    await view_signals(80)
    assert dut.test_output.value.to_signed() == 1, f"Expected test_output= 1, but got {dut.test_output.value}"
    await view_signals(80)
    assert dut.test_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_output.value}"
    await view_signals(80)
    assert dut.test_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_output.value}"
    cocotb.log.info("End of NAND gate Training and Testing")

    dut.gate_select.value = 0b11
    cocotb.log.info("Start of NOR gate Training and Testing")
    await apply_stimulus(-1, -1, 0b11, 70)
    await apply_stimulus(-1, 1, 0b11, 60)
    await apply_stimulus(1, -1, 0b11, 60)
    await apply_stimulus(1, 1, 0b11, 70)
    assert dut.w1.value.to_signed() == -2, f"Expected w1=-2, but got {dut.w1.value}"
    assert dut.w2.value.to_signed() == -2, f"Expected w2=-2, but got {dut.w2.value}"
    assert dut.bias.value.to_signed() ==  -2, f"Expected bias= -2, but got {dut.bias.value}"
    await view_signals(80)
    assert dut.test_output.value.to_signed() == 1, f"Expected test_output= 1, but got {dut.test_output.value}"
    await view_signals(80)
    assert dut.test_output.value.to_signed() == -1, f"Expected test_output= -1, but got {dut.test_output.value}"
    await view_signals(80)
    assert dut.test_output.value.to_signed() == -1, f"Expected test_output= -1, but got {dut.test_output.value}"
    await view_signals(80)
    assert dut.test_output.value.to_signed() == -1, f"Expected test_output= -1, but got {dut.test_output.value}"
    cocotb.log.info("End of NOR gate Training and Testing")

    # Random Test Cases (with fixed input patterns for each gate)
    num_random_cases = 10
    for i in range(num_random_cases):
        random_gate_select = random.randint(0, 3)
        cocotb.log.info(f"Start of Random Test Case {i+1} for gate_select={bin(random_gate_select)}")
 
        if random_gate_select == 0b00:  # AND gate
            dut.gate_select.value = 0b00
            dut.start.value = 1
            cocotb.log.info("Start of AND gate Training and Testing")
            await apply_stimulus(1, 1, 0b00, 60)
            await apply_stimulus(1, -1, 0b00, 60)
            await apply_stimulus(-1, 1, 0b00, 60)
            await apply_stimulus(-1, -1, 0b00, 60)
            dut.start.value = 0
            assert dut.w1.value.to_signed() == 2, f"Expected w1=2, but got {dut.w1.value}"
            assert dut.w2.value.to_signed() == 2, f"Expected w2=2, but got {dut.w2.value}"
            assert dut.bias.value.to_signed() == -2, f"Expected bias=-2, but got {dut.bias.value}"
            await view_signals(100)
            assert dut.test_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_output.value}"
            await view_signals(75)
            assert dut.test_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_output.value}"
            await view_signals(80)
            assert dut.test_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_output.value}"
            await view_signals(85)
            assert dut.test_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_output.value}"
            cocotb.log.info("End of AND gate Training and Testing")
        
        elif random_gate_select == 0b01:  # OR gate
            dut.gate_select.value = 0b01
            dut.start.value = 1
            cocotb.log.info("Start of OR gate Training and Testing")
            await apply_stimulus(1, 1, 0b01, 70)
            await apply_stimulus(-1, 1, 0b01, 60)
            await apply_stimulus(1, -1, 0b01, 60)
            await apply_stimulus(-1, -1, 0b01, 70)
            dut.start.value = 0
            assert dut.w1.value.to_signed() == 2, f"Expected w1=2, but got {dut.w1.value}"
            assert dut.w2.value.to_signed() == 2, f"Expected w2=2, but got {dut.w2.value}"
            assert dut.bias.value.to_signed() ==  2, f"Expected bias= 2, but got {dut.bias.value}"
            await view_signals(80)
            assert dut.test_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_output.value}"
            await view_signals(80)
            assert dut.test_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_output.value}"
            await view_signals(80)
            assert dut.test_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_output.value}"
            await view_signals(80)
            assert dut.test_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_output.value}"
            cocotb.log.info("End of OR gate Training and Testing")

        elif random_gate_select == 0b10:  # NAND gate
            dut.gate_select.value = 0b10
            dut.start.value = 1
            cocotb.log.info("Start of NAND gate Training and Testing")
            await apply_stimulus(-1, -1, 0b10, 70)
            await apply_stimulus(-1, 1, 0b10, 60)
            await apply_stimulus(1, -1, 0b10, 60)
            await apply_stimulus(1, 1, 0b10, 70)
            dut.start.value = 0
            assert dut.w1.value.to_signed() == -2, f"Expected w1=-2, but got {dut.w1.value}"
            assert dut.w2.value.to_signed() == -2, f"Expected w2=-2, but got {dut.w2.value}"
            assert dut.bias.value.to_signed() ==  2, f"Expected bias= 2, but got {dut.bias.value}"
            await view_signals(80)
            assert dut.test_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_output.value}"
            await view_signals(80)
            assert dut.test_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_output.value}"
            await view_signals(80)
            assert dut.test_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_output.value}"
            await view_signals(80)
            assert dut.test_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_output.value}"
            cocotb.log.info("End of NAND gate Training and Testing")

        elif random_gate_select == 0b11:  # NOR gate
            dut.gate_select.value = 0b11
            dut.start.value = 1
            cocotb.log.info("Start of NOR gate Training and Testing")
            await apply_stimulus(-1, -1, 0b11, 70)
            await apply_stimulus(-1, 1, 0b11, 60)
            await apply_stimulus(1, -1, 0b11, 60)
            await apply_stimulus(1, 1, 0b11, 70)
            dut.start.value = 0
            assert dut.w1.value.to_signed() == -2, f"Expected w1=-2, but got {dut.w1.value}"
            assert dut.w2.value.to_signed() == -2, f"Expected w2=-2, but got {dut.w2.value}"
            assert dut.bias.value.to_signed() ==  -2, f"Expected bias= -2, but got {dut.bias.value}"
            await view_signals(80)
            assert dut.test_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_output.value}"
            await view_signals(80)
            assert dut.test_output.value.to_signed() == -1, f"Expected test_output=1, but got {dut.test_output.value}"
            await view_signals(80)
            assert dut.test_output.value.to_signed() == -1, f"Expected test_output=1, but got {dut.test_output.value}"
            await view_signals(80)
            assert dut.test_output.value.to_signed() == -1, f"Expected test_output=1, but got {dut.test_output.value}"
            cocotb.log.info("End of NOR gate Training and Testing")
    
        cocotb.log.info(f"End of Random Test Case {i+1} for gate_select={bin(random_gate_select)}")

    # Random Invalid Input Test Cases
    num_random_invalid_cases = 5  # Number of random invalid test cases
    for i in range(num_random_invalid_cases):
        random_gate_select = random.randint(0, 3)
        
        # Select the invalid input (either 'a' or 'b') and set it to 0
        invalid_input = random.choice(['a', 'b'])
        
        if random_gate_select == 0b00:  # AND gate
            dut.gate_select.value = 0b00
            dut.start.value = 1
            cocotb.log.info(f"Start of AND gate Training with invalid input on {invalid_input}")
            
            if invalid_input == 'a':
                await apply_stimulus(0, 1, 0b00, 60)
                await apply_stimulus(0, -1, 0b00, 60)
                await apply_stimulus(0, 1, 0b00, 60)
                await apply_stimulus(0, -1, 0b00, 60)
            else:
                await apply_stimulus(1, 0, 0b00, 60)
                await apply_stimulus(-1, 0, 0b00, 60)
                await apply_stimulus(1, 0, 0b00, 60)
                await apply_stimulus(-1, 0, 0b00, 60)

            await view_signals(100)
            await view_signals(75)
            await view_signals(80)
            await view_signals(80)
            cocotb.log.info(f"Output is not expected for invalid input {invalid_input} in AND gate training and testing")
            cocotb.log.info("End of AND gate Training and Testing with invalid input")
        
        elif random_gate_select == 0b01:  # OR gate
            dut.gate_select.value = 0b01
            dut.start.value = 1
            cocotb.log.info(f"Start of OR gate Training with invalid input on {invalid_input}")
            
            if invalid_input == 'a':
                await apply_stimulus(0, 1, 0b01, 60)
                await apply_stimulus(0, -1, 0b01, 60)
                await apply_stimulus(0, 1, 0b01, 60)
                await apply_stimulus(0, -1, 0b01, 60)
            else:
                await apply_stimulus(1, 0, 0b01, 60)
                await apply_stimulus(-1, 0, 0b01, 60)
                await apply_stimulus(1, 0, 0b01, 60)
                await apply_stimulus(-1, 0, 0b01, 60)

            await view_signals(80)
            await view_signals(80)
            await view_signals(80)
            await view_signals(80)
            cocotb.log.info(f"Output is not expected for invalid input {invalid_input} in OR gate training and testing")
            cocotb.log.info("End of OR gate Training and testing with invalid input")

        elif random_gate_select == 0b10:  # NAND gate
            dut.gate_select.value = 0b10
            dut.start.value = 1
            cocotb.log.info(f"Start of NAND gate Training with invalid input on {invalid_input}")
            
            if invalid_input == 'a':
                await apply_stimulus(0, -1, 0b10, 60)
                await apply_stimulus(0, 1, 0b10, 60)
                await apply_stimulus(0, -1, 0b10, 60)
                await apply_stimulus(0, 1, 0b10, 60)
            else:
                await apply_stimulus(-1, 0, 0b10, 60)
                await apply_stimulus(1, 0, 0b10, 60)
                await apply_stimulus(-1, 0, 0b10, 60)
                await apply_stimulus(1, 0, 0b10, 60)

            await view_signals(80)
            await view_signals(80)
            await view_signals(80)
            await view_signals(80)
            cocotb.log.info(f"Output is not expected for invalid input {invalid_input} in NAND gate training and testing")
            cocotb.log.info("End of NAND gate Training with invalid input")
        
        elif random_gate_select == 0b11:  # NOR gate
            dut.gate_select.value = 0b11
            dut.start.value = 1
            cocotb.log.info(f"Start of NOR gate Training with invalid input on {invalid_input}")
            
            if invalid_input == 'a':
                await apply_stimulus(0, -1, 0b11, 60)
                await apply_stimulus(0, 1, 0b11, 60)
                await apply_stimulus(0, -1, 0b11, 60)
                await apply_stimulus(0, 1, 0b11, 60)
            else:
                await apply_stimulus(-1, 0, 0b11, 60)
                await apply_stimulus(1, 0, 0b11, 60)
                await apply_stimulus(-1, 0, 0b11, 60)
                await apply_stimulus(1, 0, 0b11, 60)

            await view_signals(80)
            await view_signals(80)
            await view_signals(80)
            await view_signals(80)
            cocotb.log.info(f"Output is not expected for invalid input {invalid_input} in NOR gate training and testing")
            cocotb.log.info("End of NOR gate Training with invalid input")
    
        cocotb.log.info(f"End of Random Invalid Test Case {i+1} for gate_select={bin(random_gate_select)}")

