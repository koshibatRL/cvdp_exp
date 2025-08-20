import cocotb
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb.clock import Clock
import random

def split_bits(value, n, w):
    mask = (1 << w) - 1
    return [(value >> (w * (n - 1 - i))) & mask for i in range(n)]

def row_multiply_mod26(row, vec):
    terms = [((row[j] * vec[j]) % 26) for j in range(3)]
    term_sum = sum(terms)
    term_sum_trunc = term_sum & 0x3F
    residue = term_sum_trunc % 26
    return residue, terms, term_sum, term_sum_trunc

def python_reference_ciphertext(plaintext, key):
    P = split_bits(plaintext, 3, 5)
    K = split_bits(key, 9, 5)
    Kmat = [K[0:3], K[3:6], K[6:9]]
    C  = []
    detailed = []
    for i in range(3):
        c_val, terms, s_raw, s_trunc = row_multiply_mod26(Kmat[i], P)
        C.append(c_val)
        detailed.append(
            {
                "row": i,
                "row_vec": Kmat[i],
                "terms": terms,
                "sum_raw": s_raw,
                "sum_trunc6b": s_trunc,
                "residue": c_val
            }
        )
    ciphertext = (C[0] << 10) | (C[1] << 5) | C[2]
    return ciphertext, P, Kmat, detailed

def rand15():
    return random.randint(0, (1 << 15) - 1)

def rand45():
    return random.randint(0, (1 << 45) - 1)

@cocotb.test()
async def hill_cipher_test(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.reset.value = 1
    dut.start.value = 0
    dut.plaintext.value = 0
    dut.key.value = 0
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.clk)

    test_cases = [
        {'category': 'Normal',  'plaintext': 0b000010000100001, 'key': 0b000010000100001000010000100001000010000100001},
        {'category': 'Maximum', 'plaintext': 0b110101101011010, 'key': 0b111111111111111111111111111111111111111111111},
        {'category': 'Minimum', 'plaintext': 0,                 'key': 0},
        {'category': 'EdgeMod', 'plaintext': 0b001100011000110, 'key': 0b001100011000110001100011000110001100011000110},
        {'category': 'Random1', 'plaintext': rand15(), 'key': rand45()},
        {'category': 'Random2', 'plaintext': rand15(), 'key': rand45()}
    ]

    for idx, case in enumerate(test_cases, start=1):
        dut._log.info(f"===== Test {idx}: {case['category']} =====")
        dut.plaintext.value = case['plaintext']
        dut.key.value = case['key']
        await FallingEdge(dut.clk)
        dut.start.value = 1
        await RisingEdge(dut.clk)
        dut.start.value = 0
        while dut.done.value != 1:
            await RisingEdge(dut.clk)

        exp_cipher, P, Kmat, detail = python_reference_ciphertext(case['plaintext'], case['key'])
        act_cipher = int(dut.ciphertext.value)

        dut._log.info(f"Plaintext (15b): {case['plaintext']:015b}  -> chunks P0..P2 = {P}")
        dut._log.info(f"Key (45b):       {case['key']:045b}")
        for r in range(3):
            dut._log.info(
                f"  Row{r}: K={Kmat[r]}  terms={detail[r]['terms']} "
                f"sum_raw={detail[r]['sum_raw']} sum_trunc6b={detail[r]['sum_trunc6b']} "
                f"residue={detail[r]['residue']}"
            )
        dut._log.info(f"Expected ciphertext: {exp_cipher:015b} ({exp_cipher})")
        dut._log.info(f"Actual   ciphertext: {act_cipher:015b} ({act_cipher})")

        assert act_cipher == exp_cipher, f"Mismatch in {case['category']} (expected {exp_cipher}, got {act_cipher})"

        dut.reset.value = 1
        await RisingEdge(dut.clk)
        dut.reset.value = 0
        await RisingEdge(dut.clk)

@cocotb.test()
async def hill_cipher_clock_latency_test(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    dut.plaintext.value = 0b000010000100001
    dut.key.value = 0b000010000100001000010000100001000010000100001
    await FallingEdge(dut.clk)
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0
    latency = 0
    while dut.done.value != 1:
        await RisingEdge(dut.clk)
        latency += 1
    dut._log.info(f"Measured latency: {latency} cycles")
    assert latency == 3, f"Latency should be 3 cycles but measured {latency}"
