
from cocotb.triggers import RisingEdge, Timer
from cocotb.runner import get_runner
import random
import struct
import os
import subprocess
import re

def runner(module, toplevel, src:str, plusargs:list =[], args:tuple = (), parameters:dict={}, wave:bool = False, sim:str = "icarus"):
    runner = get_runner(sim)
    runner.build(
        sources=src,
        hdl_toplevel=toplevel,
        # Arguments
        parameters=parameters,
        # compiler args
        build_args=args,
        always=True,
        clean=True,
        waves=wave,
        verbose=True,
        timescale=("1ns", "1ns"),
        log_file="build.log")
    runner.test(hdl_toplevel=toplevel, test_module=module, waves=wave, plusargs=plusargs, log_file="sim.log")

def xrun_tb(lang:str="sv"):
    VALID_RTYPE = ("sv" , "v")
    if lang not in VALID_RTYPE:
        raise ValueError("Invalid argument for xrun_tb function.")
    
    cmd = f"xrun -coverage all -covoverwrite /code/rtl/*.{lang} /code/verif/*.{lang} {'-sv' if lang == 'sv' else ''} -covtest test -svseed random -logfile simulation.log -work sim_build"
    # print(cmd)
    assert(subprocess.run(cmd, shell=True)), "Simulation didn't ran correctly."
    
def coverage_report(asrt_type:str="all", rtype:str = "text", rname:str = "coverage"):
    VALID_ATYPE = ("all", "code", "fsm", "functional", "block", "expression", "toggle", "statement", "assertion", "covergroup")
    VALID_RTYPE = ("text" , "html")

    if asrt_type not in VALID_ATYPE and rtype not in VALID_RTYPE:
        raise ValueError("Invalid argument for coverage_report function.")
    cmd = f"imc -load /code/rundir/sim_build/cov_work/scope/test -execcmd \"report -metrics {asrt_type} -all -aspect sim -assertionStatus -overwrite -{rtype} -out {rname}\""
    assert(subprocess.run(cmd, shell=True)), "Coverage merge didn't ran correctly."

def covt_report_check(rname:str = "coverage"):

    metrics = {}
    try:
        with open(rname) as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError("Couldn't find the coverage file.")
    # ----------------------------------------
    # - Evaluate Report
    # ----------------------------------------
    column = re.split(r'\s{2,}', lines[0].strip())
    for line in lines[2:]:
        info = re.split(r'\s{2,}', line.strip())
        inst = info[0].lstrip('|-')
        metrics [inst] = {column[i]: info[i].split('%')[0] for i in range(1, len(column))}

    if "Overall Average" in metrics[os.getenv("TOPLEVEL")]:
        assert float(metrics[os.getenv("TOPLEVEL")]["Overall Average"]) >= float(os.getenv("TARGET")), "Didn't achieved the required coverage result."
    elif "Assertion" in metrics[os.getenv("TOPLEVEL")]:
        assert float(metrics[os.getenv("TOPLEVEL")]["Assertion"]) == 100.00, "Didn't achieved the required coverage result."
    elif "Toggle" in metrics[os.getenv("TOPLEVEL")]:
        assert float(metrics[os.getenv("TOPLEVEL")]["Toggle"]) >= float(os.getenv("TARGET")), "Didn't achieved the required coverage result."
    elif "Block" in metrics[os.getenv("TOPLEVEL")]:
        assert float(metrics[os.getenv("TOPLEVEL")]["Block"]) >= float(os.getenv("TARGET")), "Didn't achieved the required coverage result."
    else:
        assert False, "Couldn't find the required coverage result."

def save_vcd(wave:bool, toplevel:str, new_name:str):
    if wave:
        os.makedirs("vcd", exist_ok=True)
        os.rename(f'./sim_build/{toplevel}.fst', f'./vcd/{new_name}.fst')

async def reset_dut(reset_n, duration_ns = 10, active:bool = False):
    # Restart Interface
    reset_n.value = 1 if active else 0
    await Timer(duration_ns, units="ns")
    reset_n.value = 0 if active else 1
    await Timer(duration_ns, units='ns')
    reset_n._log.debug("Reset complete")

async def duty_cycle(pwm_signal, clock, period):
    # 0-> time_period, 1-> high_time, 2-> low_time = full_time = high_time
    pwm = {"time_period": period, "on_time": 0, "off_time": 0}
    pwm_signal._log.debug("Pulse started")
    for i in range(period):
        if pwm_signal.value == 1:
            pwm["on_time"] += 1
        await RisingEdge(clock)

    pwm["off_time"] = pwm["time_period"] - pwm["on_time"]
    pwm_signal._log.debug("Time period completed")
    return pwm

async def dut_init(dut):
    # iterate all the input signals and initialize with 0
    for signal in dut:
        if signal._type == "GPI_NET":
            signal.value = 0

# all the element of array dump in to one verable
def ary_2_int(arry: list, ewdth: int=8) -> int:
    if arry is not None:
        ary = arry.copy()
        ary.reverse()
        ary_byt = int(''.join(format(num, f'0{ewdth}b') for num in ary), 2)
        return ary_byt
    else:
        raise ValueError
    
async def rnd_clk_dly (clock, low: int = 50, high: int = 100):
    for i in range(random.randint(50,100)):
            await RisingEdge(clock)

# converitng floating point number in scientific notation binary format
def float_to_binary(num: float):
    # Convert float to 32-bit binary representation
    packed_num = struct.pack('!f', num)  # Packs the float into 32 bits using IEEE 754
    binary_representation = ''.join(f'{byte:08b}' for byte in packed_num)

    sign = binary_representation[0]
    exponent = binary_representation[1:9]
    mantissa = binary_representation[9:]

    return sign, exponent, mantissa