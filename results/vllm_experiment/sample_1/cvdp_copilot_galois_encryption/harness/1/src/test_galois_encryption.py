import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import harness_library as hrs_lb
import random

@cocotb.test()
async def test_galois_encryption(dut):
    """Test the Galois Encryption module with edge cases and random data."""

    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    model = hrs_lb.GaloisEncryption(0)

    # Retrieve parameters from the DUT
    NBW_DATA = dut.NBW_DATA.value.to_unsigned()
    NBW_KEY = dut.NBW_KEY.value.to_unsigned()

    debug = 0

    # Range for input values
    data_min = 1
    data_max = int(2**NBW_DATA - 1)

    key_min = 1
    key_max = int(2**NBW_KEY - 1)

    resets = 5
    runs = 200

    for k in range(resets):
        # Reset the MODEL
        model.update_key(0)

        # Reset the DUT
        await hrs_lb.dut_init(dut)

        dut.rst_async_n.value = 0
        await Timer(10, units="ns")

        dut_data_out = dut.o_data.value.to_unsigned()
        dut_valid_out = dut.o_valid.value.to_unsigned()
        model_data_out = 0
        model_valid_out = 0
        
        dut.rst_async_n.value = 1
        await Timer(10, units='ns')

        await RisingEdge(dut.clk)
        assert dut_data_out == model_data_out, f"[ERROR] DUT data output does not match model data output: {hex(dut_data_out)} != {hex(model_data_out)}"
        assert dut_valid_out == model_valid_out, f"[ERROR] DUT valid output does not match model valid output: {hex(dut_valid_out)} != {hex(model_valid_out)}"

        # Generate random key
        key = random.randint(key_min, key_max)
        update_key = 1

        dut.i_key.value = key
        dut.i_update_key.value = update_key

        # Update model key
        model.update_key(key)

        await RisingEdge(dut.clk)
        assert dut_data_out == model_data_out, f"[ERROR] DUT data output does not match model data output: {hex(dut_data_out)} != {hex(model_data_out)}"
        assert dut_valid_out == model_valid_out, f"[ERROR] DUT valid output does not match model valid output: {hex(dut_valid_out)} != {hex(model_valid_out)}"

        update_key = 0
        dut.i_update_key.value = update_key

        for i in range(runs):
            # Generate random input data
            in_data = random.randint(data_min, data_max)
            encrypt = random.randint(0,1)

            # Apply inputs to DUT
            dut.i_data.value = in_data
            dut.i_valid.value = 1
            dut.i_encrypt.value = encrypt

            await RisingEdge(dut.clk)
            dut.i_valid.value = 0
            model_data_out = 0
            model_valid_out = 0
            dut_data_out = dut.o_data.value.to_unsigned()
            dut_valid_out = dut.o_valid.value.to_unsigned()
            
            if debug:
                dut_valid_in = dut.i_valid.value
                dut_encrypt_in = dut.i_encrypt.value
                cocotb.log.info(f"\nSET ALL INPUT VALUES")
                cocotb.log.info(f"[INPUTS] in_data: {hex(in_data)}, i_valid: {dut_valid_in}, i_encrypt: {dut_encrypt_in}")
                cocotb.log.info(f"[DUT] data output:    {hex(dut_data_out)}")
                cocotb.log.info(f"[DUT] valid output:   {hex(dut_valid_out)}")
                cocotb.log.info(f"[MODEL] data output:  {hex(model_data_out)}")
                cocotb.log.info(f"[MODEL] valid output: {hex(model_valid_out)}")

            assert dut_data_out == model_data_out, f"[ERROR] DUT data output does not match model data output: {hex(dut_data_out)} != {hex(model_data_out)}"
            assert dut_valid_out == model_valid_out, f"[ERROR] DUT valid output does not match model valid output: {hex(dut_valid_out)} != {hex(model_valid_out)}"

            # Wait for latency
            await RisingEdge(dut.clk)
            dut_data_out = dut.o_data.value.to_unsigned()
            dut_valid_out = dut.o_valid.value.to_unsigned()
            if debug:
                dut_valid_in = dut.i_valid.value
                dut_encrypt_in = dut.i_encrypt.value
                cocotb.log.info(f"\nSET VALID TO 0. Clock 1")
                cocotb.log.info(f"[INPUTS] in_data: {hex(in_data)}, i_valid: {dut_valid_in}, i_encrypt: {dut_encrypt_in}")
                cocotb.log.info(f"[DUT] data output:    {hex(dut_data_out)}")
                cocotb.log.info(f"[DUT] valid output:   {hex(dut_valid_out)}")
                cocotb.log.info(f"[MODEL] data output:  {hex(model_data_out)}")
                cocotb.log.info(f"[MODEL] valid output: {hex(model_valid_out)}")
            assert dut_data_out == model_data_out, f"[ERROR] DUT data output does not match model data output: {hex(dut_data_out)} != {hex(model_data_out)}"
            assert dut_valid_out == model_valid_out, f"[ERROR] DUT valid output does not match model valid output: {hex(dut_valid_out)} != {hex(model_valid_out)}"

            await RisingEdge(dut.clk)
            dut_data_out = dut.o_data.value.to_unsigned()
            dut_valid_out = dut.o_valid.value.to_unsigned()
            if debug:
                dut_valid_in = dut.i_valid.value
                dut_encrypt_in = dut.i_encrypt.value
                cocotb.log.info(f"\nClock 2")
                cocotb.log.info(f"[INPUTS] in_data: {hex(in_data)}, i_valid: {dut_valid_in}, i_encrypt: {dut_encrypt_in}")
                cocotb.log.info(f"[DUT] data output:    {hex(dut_data_out)}")
                cocotb.log.info(f"[DUT] valid output:   {hex(dut_valid_out)}")
                cocotb.log.info(f"[MODEL] data output:  {hex(model_data_out)}")
                cocotb.log.info(f"[MODEL] valid output: {hex(model_valid_out)}")
            assert dut_data_out == model_data_out, f"[ERROR] DUT data output does not match model data output: {hex(dut_data_out)} != {hex(model_data_out)}"
            assert dut_valid_out == model_valid_out, f"[ERROR] DUT valid output does not match model valid output: {hex(dut_valid_out)} != {hex(model_valid_out)}"

            await RisingEdge(dut.clk)
            assert dut_data_out == model_data_out, f"[ERROR] DUT data output does not match model data output: {hex(dut_data_out)} != {hex(model_data_out)}"
            assert dut_valid_out == model_valid_out, f"[ERROR] DUT valid output does not match model valid output: {hex(dut_valid_out)} != {hex(model_valid_out)}"

            dut_data_out = dut.o_data.value.to_unsigned()
            dut_valid_out = dut.o_valid.value.to_unsigned()

            # Process data through the model
            if encrypt:
                model_data_out = model.encrypt(in_data)
            else:
                model_data_out = model.decrypt(in_data)
            model_valid_out = 1
            
            if debug:
                dut_valid_in = dut.i_valid.value
                dut_encrypt_in = dut.i_encrypt.value
                cocotb.log.info(f"\nClock 3. There should be an output here")
                cocotb.log.info(f"[INPUTS] in_data: {hex(in_data)}, i_valid: {dut_valid_in}, i_encrypt: {dut_encrypt_in}")
                cocotb.log.info(f"[DUT] data output:    {hex(dut_data_out)}")
                cocotb.log.info(f"[DUT] valid output:   {hex(dut_valid_out)}")
                cocotb.log.info(f"[MODEL] data output:  {hex(model_data_out)}")
                cocotb.log.info(f"[MODEL] valid output: {hex(model_valid_out)}")

            assert dut_data_out == model_data_out, f"[ERROR] DUT data output does not match model data output: {hex(dut_data_out)} != {hex(model_data_out)}"
            assert dut_valid_out == model_valid_out, f"[ERROR] DUT valid output does not match model valid output: {hex(dut_valid_out)} != {hex(model_valid_out)}"
