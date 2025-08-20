import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random

@cocotb.test()
async def test_perceptron_gates(dut):
    """Testbench for the perceptron_gates module using Cocotb."""

    # Create a 10ns clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset logic
    dut.rst_n.value = 0
    await Timer(10, units="ns")
    dut.rst_n.value = 1

    # Initialize inputs
    dut.x1.value = 0
    dut.x2.value = 0
    dut.learning_rate.value = 1
    dut.threshold.value = 0
    dut.gate_select.value = 0

    await RisingEdge(dut.rst_n)
    await Timer(10, units="ns")

    # Helper function for applying stimulus and logging outputs
    async def apply_stimulus(x1, x2, gate_select, duration):
        dut.x1.value = x1
        dut.x2.value = x2
        dut.gate_select.value = gate_select
        await Timer(duration, units="ns")
        cocotb.log.info(f"gate_select={gate_select}, x1={x1}, x2={x2}, percep_w1={dut.percep_w1.value.to_signed()}, percep_w2={dut.percep_w2.value.to_signed()}, percep_bias={dut.percep_bias.value.to_signed()}, present_addr={bin(dut.present_addr.value.to_unsigned())}, stop={bin(dut.stop.value.to_unsigned())}, input_index={bin(dut.input_index.value.to_unsigned())}, y_in={dut.y_in.value.to_signed()}, y={dut.y.value.to_signed()}, prev_percep_wt_1={dut.prev_percep_wt_1.value.to_signed()}, prev_percep_wt_2={dut.prev_percep_wt_2.value.to_signed()}, prev_percep_bias={dut.prev_percep_bias.value.to_signed()}")
        
    async def view_signals(duration):
        """Pause for a specified duration and view the values of signals."""
        await Timer(duration, units="ns")
        cocotb.log.info(f"Observing signals after {duration}ns:")
        cocotb.log.info(f"gate_select={dut.gate_select.value}, x1={dut.x1.value}, x2={dut.x2.value}, percep_w1={dut.percep_w1.value.to_signed()}, percep_w2={dut.percep_w2.value.to_signed()}, percep_bias={dut.percep_bias.value.to_signed()}, present_addr={bin(dut.present_addr.value.to_unsigned())}, stop={bin(dut.stop.value.to_unsigned())} , test_percep_x1={dut.test_percep_x1.value.to_signed()}, test_percep_x2={dut.test_percep_x2.value.to_signed()}, expected_percep_output={dut.expected_percep_output.value.to_signed()}, test_percep_output={dut.test_percep_output.value.to_signed()}, test_percep_result={dut.test_percep_result.value.to_signed()}, test_percep_done={bin(dut.test_percep_done.value.to_unsigned())}, test_percep_present_state={bin(dut.test_percep_present_state.value.to_unsigned())}, test_percep_index={bin(dut.test_percep_index.value.to_unsigned())}, input_index={bin(dut.input_index.value.to_unsigned())}")

    # Test AND gate targets (gate_select = 2'b00)
    dut.gate_select.value = 0b00
    cocotb.log.info("Start of AND gate Training and Testing")
    await apply_stimulus(1, 1, 0b00, 85)
    await apply_stimulus(1, -1, 0b00, 90)
    await apply_stimulus(-1, 1, 0b00, 100)
    await Timer(25, units="ns")
    await apply_stimulus(-1, -1, 0b00, 75)
    await Timer(5, units="ns")
    await apply_stimulus(1, 1, 0b00, 20)
    await Timer(15, units="ns")
    await apply_stimulus(1, -1, 0b00, 80)
    await apply_stimulus(-1, 1, 0b00, 65)
    await apply_stimulus(-1, -1, 0b00, 15)
    cocotb.log.info(f"Finalized Weights and Bias  are : percep_w1={dut.percep_w1.value.to_signed()},percep_w2={dut.percep_w2.value.to_signed()},percep_bias={dut.percep_bias.value.to_signed()}")
    assert dut.percep_w1.value.to_signed() == 1, f"Expected w1=1, but got {dut.percep_w1.value}"
    assert dut.percep_w2.value.to_signed() == 1, f"Expected w2=1, but got {dut.percep_w2.value}"
    assert dut.percep_bias.value.to_signed() == -1, f"Expected bias=-1, but got {dut.percep_bias.value}"
    await view_signals(80)
    assert dut.test_percep_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_percep_output.value}"
    await view_signals(80)
    assert dut.test_percep_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_percep_output.value}"
    await view_signals(80)
    assert dut.test_percep_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_percep_output.value}"
    await view_signals(70)
    assert dut.test_percep_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_percep_output.value}"
    cocotb.log.info("End of AND gate Training & Testing")

    # Test OR gate targets (gate_select = 2'b01)
    dut.gate_select.value = 0b01
    cocotb.log.info("Start of OR gate Training and Testing")
    await apply_stimulus(1, 1, 0b01, 120)
    await Timer(30, units="ns")
    await apply_stimulus(-1, 1, 0b01, 70)
    await Timer(30, units="ns")
    await apply_stimulus(1, -1, 0b01, 70)
    await Timer(30, units="ns")
    await apply_stimulus(-1, -1, 0b01, 70)
    cocotb.log.info(f"Finalized Weights and Bias  are : percep_w1={dut.percep_w1.value.to_signed()},percep_w2={dut.percep_w2.value.to_signed()},percep_bias={dut.percep_bias.value.to_signed()}")
    assert dut.percep_w1.value.to_signed() == 1, f"Expected w1=1, but got {dut.percep_w1.value}"
    assert dut.percep_w2.value.to_signed() == 1, f"Expected w2=1, but got {dut.percep_w2.value}"
    assert dut.percep_bias.value.to_signed() == 1, f"Expected bias=1, but got {dut.percep_bias.value}"
    await view_signals(80)
    assert dut.test_percep_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_percep_output.value}"
    await view_signals(80)
    assert dut.test_percep_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_percep_output.value}"
    await view_signals(80)
    assert dut.test_percep_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_percep_output.value}"
    await view_signals(70)
    assert dut.test_percep_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_percep_output.value}"
    cocotb.log.info("End of OR gate Training & Testing")

    # Test NAND gate targets (gate_select = 2'b10)
    dut.gate_select.value = 0b10
    cocotb.log.info("Start of NAND gate Training & Testing")
    await apply_stimulus(-1, -1, 0b10, 115)
    await Timer(30, units="ns")
    await apply_stimulus(-1, 1, 0b10, 80)
    await Timer(30, units="ns")
    await apply_stimulus(1, -1, 0b10, 65)
    await Timer(10, units="ns")
    await apply_stimulus(1, 1, 0b10, 70)
    cocotb.log.info(f"Finalized Weights and Bias  are : percep_w1={dut.percep_w1.value.to_signed()},percep_w2={dut.percep_w2.value.to_signed()},percep_bias={dut.percep_bias.value.to_signed()}")
    assert dut.percep_w1.value.to_signed() == -1, f"Expected w1=-1, but got {dut.percep_w1.value}"
    assert dut.percep_w2.value.to_signed() == -1, f"Expected w2=-1, but got {dut.percep_w2.value}"
    assert dut.percep_bias.value.to_signed() == 1, f"Expected bias=1, but got {dut.percep_bias.value}"
    await view_signals(80)
    assert dut.test_percep_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_percep_output.value}"
    await view_signals(80)
    assert dut.test_percep_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_percep_output.value}"
    await view_signals(80)
    assert dut.test_percep_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_percep_output.value}"
    await view_signals(70)
    assert dut.test_percep_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_percep_output.value}"
    cocotb.log.info("End of NAND gate Training & Testing")

    # Test NOR gate targets (gate_select = 2'b11)
    dut.gate_select.value = 0b11
    cocotb.log.info("Start of NOR gate Training")
    await apply_stimulus(-1, -1, 0b11, 120)
    await Timer(20, units="ns")
    await apply_stimulus(-1, 1, 0b11, 80)
    await Timer(20, units="ns")
    await apply_stimulus(1, -1, 0b11, 80)
    await Timer(80, units="ns")
    await apply_stimulus(1, 1, 0b11, 110)
    await Timer(80, units="ns")
    await apply_stimulus(-1, -1, 0b11, 20)
    await Timer(30, units="ns")
    await apply_stimulus(-1, 1, 0b11, 70)
    await Timer(5, units="ns")
    await apply_stimulus(1, -1, 0b11, 10)
    await Timer(25, units="ns")
    await apply_stimulus(1, 1, 0b11, 50)
    cocotb.log.info(f"Finalized Weights and Bias  are : percep_w1={dut.percep_w1.value.to_signed()},percep_w2={dut.percep_w2.value.to_signed()},percep_bias={dut.percep_bias.value.to_signed()}")
    assert dut.percep_w1.value.to_signed() == -1, f"Expected w1=-1, but got {dut.percep_w1.value}"
    assert dut.percep_w2.value.to_signed() == -1, f"Expected w2=-1, but got {dut.percep_w2.value}"
    assert dut.percep_bias.value.to_signed() == -1, f"Expected bias=-1, but got {dut.percep_bias.value}"
    await view_signals(80)
    assert dut.test_percep_output.value.to_signed() == 1, f"Expected test_output=1, but got {dut.test_percep_output.value}"
    await view_signals(80)
    assert dut.test_percep_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_percep_output.value}"
    await view_signals(80)
    assert dut.test_percep_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_percep_output.value}"
    await view_signals(80)
    assert dut.test_percep_output.value.to_signed() == -1, f"Expected test_output=-1, but got {dut.test_percep_output.value}"
    cocotb.log.info("End of NOR gate Training & Testing")
    

    # Random Test Cases (with fixed input patterns for each gate)
    num_random_cases = 10
    for i in range(num_random_cases):
        random_gate_select = random.randint(0, 3)
        cocotb.log.info(f"Start of Random Test Case {i+1} for gate_select={bin(random_gate_select)}")
 
        if random_gate_select == 0b00:  # AND gate
            dut.gate_select.value = 0b00
            cocotb.log.info("Start of AND gate Training and Testing")
            await apply_stimulus(1, 1, 0b00, 85)
            await apply_stimulus(1, -1, 0b00, 90)
            await apply_stimulus(-1, 1, 0b00, 100)
            await Timer(25, units="ns")
            await apply_stimulus(-1, -1, 0b00, 75)
            await Timer(5, units="ns")
            await apply_stimulus(1, 1, 0b00, 20)
            await Timer(15, units="ns")
            await apply_stimulus(1, -1, 0b00, 80)
            await apply_stimulus(-1, 1, 0b00, 65)
            await apply_stimulus(-1, -1, 0b00, 15)
            await view_signals(80)
            await view_signals(80)
            await view_signals(80)
            await view_signals(70)
            cocotb.log.info("End of AND gate Training & Testing")
            
        
        elif random_gate_select == 0b01:  # OR gate
            dut.gate_select.value = 0b01
            cocotb.log.info("Start of OR gate Training and Testing")
            await apply_stimulus(1, 1, 0b01, 120)
            await Timer(30, units="ns")
            await apply_stimulus(-1, 1, 0b01, 70)
            await Timer(30, units="ns")
            await apply_stimulus(1, -1, 0b01, 70)
            await Timer(30, units="ns")
            await apply_stimulus(-1, -1, 0b01, 70)
            await view_signals(80)
            await view_signals(80)
            await view_signals(80)
            await view_signals(70)
            cocotb.log.info("End of OR gate Training & Testing")

        elif random_gate_select == 0b10:  # NAND gate
            dut.gate_select.value = 0b10
            cocotb.log.info("Start of NAND gate Training & Testing")
            await apply_stimulus(-1, -1, 0b10, 115)
            await Timer(30, units="ns")
            await apply_stimulus(-1, 1, 0b10, 80)
            await Timer(30, units="ns")
            await apply_stimulus(1, -1, 0b10, 65)
            await Timer(10, units="ns")
            await apply_stimulus(1, 1, 0b10, 70)
            await view_signals(80)
            await view_signals(80)
            await view_signals(80)
            await view_signals(70)
            cocotb.log.info("End of NAND gate Training & Testing")

        elif random_gate_select == 0b11:  # NOR gate
            dut.gate_select.value = 0b11
            cocotb.log.info("Start of NOR gate Training")
            await apply_stimulus(-1, -1, 0b11, 120)
            await Timer(20, units="ns")
            await apply_stimulus(-1, 1, 0b11, 80)
            await Timer(20, units="ns")
            await apply_stimulus(1, -1, 0b11, 80)
            await Timer(80, units="ns")
            await apply_stimulus(1, 1, 0b11, 110)
            await Timer(80, units="ns")
            await apply_stimulus(-1, -1, 0b11, 20)
            await Timer(30, units="ns")
            await apply_stimulus(-1, 1, 0b11, 70)
            await Timer(5, units="ns")
            await apply_stimulus(1, -1, 0b11, 10)
            await Timer(25, units="ns")
            await apply_stimulus(1, 1, 0b11, 50)
            await view_signals(80)
            await view_signals(80)
            await view_signals(80)
            await view_signals(80)
            cocotb.log.info("End of NOR gate Training & Testing")
    
        cocotb.log.info(f"End of Random Test Case {i+1} for gate_select={bin(random_gate_select)}")

    # Random Invalid Input Test Cases
    num_random_invalid_cases = 5  # Number of random invalid test cases
    for i in range(num_random_invalid_cases):
        random_gate_select = random.randint(0, 3)
        
        # Select the invalid input (either 'a' or 'b') and set it to 0
        invalid_input = random.choice(['x1', 'x2'])
        
        if random_gate_select == 0b00:  # AND gate
            dut.gate_select.value = 0b00
            
            cocotb.log.info(f"Start of AND gate Training with invalid input on {invalid_input}")
            
            if invalid_input == 'x1':
                await apply_stimulus(0, 1, 0b00, 85)
                await apply_stimulus(0, -1, 0b00, 90)
                await apply_stimulus(0, 1, 0b00, 100)
                await Timer(25, units="ns")
                await apply_stimulus(0, -1, 0b00, 75)
                await Timer(5, units="ns")
                await apply_stimulus(0, 1, 0b00, 20)
                await Timer(15, units="ns")
                await apply_stimulus(0, -1, 0b00, 80)
                await apply_stimulus(0, 1, 0b00, 65)
                await apply_stimulus(0, -1, 0b00, 15)
            else:
                await apply_stimulus(1, 0, 0b00, 85)
                await apply_stimulus(1, 0, 0b00, 90)
                await apply_stimulus(-1, 0, 0b00, 100)
                await Timer(25, units="ns")
                await apply_stimulus(-1, 0, 0b00, 75)
                await Timer(5, units="ns")
                await apply_stimulus(1, 0, 0b00, 20)
                await Timer(15, units="ns")
                await apply_stimulus(1, 0, 0b00, 80)
                await apply_stimulus(-1, 0, 0b00, 65)
                await apply_stimulus(-1, 0, 0b00, 15)

            await view_signals(80)
            await view_signals(80)
            await view_signals(80)
            await view_signals(70)
            cocotb.log.info(f"Output is not expected for invalid input {invalid_input} in AND gate training and testing")
            cocotb.log.info("End of AND gate Training and Testing with invalid input")
        
        elif random_gate_select == 0b01:  # OR gate
            dut.gate_select.value = 0b01
            
            cocotb.log.info(f"Start of OR gate Training with invalid input on {invalid_input}")
            
            if invalid_input == 'x1':
                await apply_stimulus(0, 1, 0b01, 120)
                await Timer(30, units="ns")
                await apply_stimulus(0, 1, 0b01, 70)
                await Timer(30, units="ns")
                await apply_stimulus(0, -1, 0b01, 70)
                await Timer(30, units="ns")
                await apply_stimulus(0, -1, 0b01, 70)
            else:
                await apply_stimulus(1, 0, 0b01, 120)
                await Timer(30, units="ns")
                await apply_stimulus(-1, 0, 0b01, 70)
                await Timer(30, units="ns")
                await apply_stimulus(1, 0, 0b01, 70)
                await Timer(30, units="ns")
                await apply_stimulus(-1, 0, 0b01, 70)

            await view_signals(80)
            await view_signals(80)
            await view_signals(80)
            await view_signals(70)
            cocotb.log.info(f"Output is not expected for invalid input {invalid_input} in OR gate training and testing")
            cocotb.log.info("End of OR gate Training and testing with invalid input")

        elif random_gate_select == 0b10:  # NAND gate
            dut.gate_select.value = 0b10
            
            cocotb.log.info(f"Start of NAND gate Training with invalid input on {invalid_input}")
            
            if invalid_input == 'x1':
                await apply_stimulus(0, -1, 0b10, 115)
                await Timer(30, units="ns")
                await apply_stimulus(0, 1, 0b10, 80)
                await Timer(30, units="ns")
                await apply_stimulus(0, -1, 0b10, 65)
                await Timer(10, units="ns")
                await apply_stimulus(0, 1, 0b10, 70)
            else:
                await apply_stimulus(-1, 0, 0b10, 115)
                await Timer(30, units="ns")
                await apply_stimulus(-1, 0, 0b10, 80)
                await Timer(30, units="ns")
                await apply_stimulus(1, 0, 0b10, 65)
                await Timer(10, units="ns")
                await apply_stimulus(1, 0, 0b10, 70)

            await view_signals(80)
            await view_signals(80)
            await view_signals(80)
            await view_signals(70)
            cocotb.log.info(f"Output is not expected for invalid input {invalid_input} in NAND gate training and testing")
            cocotb.log.info("End of NAND gate Training with invalid input")
        
        elif random_gate_select == 0b11:  # NOR gate
            dut.gate_select.value = 0b11
            
            cocotb.log.info(f"Start of NOR gate Training with invalid input on {invalid_input}")
            
            if invalid_input == 'x1':
                await apply_stimulus(0, -1, 0b11, 120)
                await Timer(20, units="ns")
                await apply_stimulus(0, 1, 0b11, 80)
                await Timer(20, units="ns")
                await apply_stimulus(0, -1, 0b11, 80)
                await Timer(80, units="ns")
                await apply_stimulus(0, 1, 0b11, 110)
                await Timer(80, units="ns")
                await apply_stimulus(0, -1, 0b11, 20)
                await Timer(30, units="ns")
                await apply_stimulus(0, 1, 0b11, 70)
                await Timer(5, units="ns")
                await apply_stimulus(0, -1, 0b11, 10)
                await Timer(25, units="ns")
                await apply_stimulus(0, 1, 0b11, 50)
            else:
                await apply_stimulus(-1, 0, 0b11, 120)
                await Timer(20, units="ns")
                await apply_stimulus(-1, 0, 0b11, 80)
                await Timer(20, units="ns")
                await apply_stimulus(1, 0, 0b11, 80)
                await Timer(80, units="ns")
                await apply_stimulus(1, 0, 0b11, 110)
                await Timer(80, units="ns")
                await apply_stimulus(-1, 0, 0b11, 20)
                await Timer(30, units="ns")
                await apply_stimulus(-1, 0, 0b11, 70)
                await Timer(5, units="ns")
                await apply_stimulus(1, 0, 0b11, 10)
                await Timer(25, units="ns")
                await apply_stimulus(1, 0, 0b11, 50)

            await view_signals(80)
            await view_signals(80)
            await view_signals(80)
            await view_signals(80)
            cocotb.log.info(f"Output is not expected for invalid input {invalid_input} in NOR gate training and testing")
            cocotb.log.info("End of NOR gate Training with invalid input")
    
        cocotb.log.info(f"End of Random Invalid Test Case {i+1} for gate_select={bin(random_gate_select)}")

