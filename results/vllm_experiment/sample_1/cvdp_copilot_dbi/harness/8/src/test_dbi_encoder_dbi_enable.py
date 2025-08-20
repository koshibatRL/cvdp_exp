import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles, Timer
import random
import time
import harness_library as hrs_lb

@cocotb.test()
async def test_dbi_encoder_dbi_enable(dut):
    # Seed the random number generator with the current time or another unique value
    random.seed(time.time())
    # Start clock
    cocotb.start_soon(Clock(dut.clk, 100, units='ns').start())
    
    
    # Initialize DUT
    #print(f'data_in before initialization = {dut.data_in.value}') ####need to remove
    await hrs_lb.dut_init(dut) 
    data_in = 0 
    dut.data_in.value = data_in
    await FallingEdge(dut.clk)
    #print(f'data_in after initialization   = {dut.data_in.value}') ####need to remove
    # Apply reset 
    await hrs_lb.reset_dut(dut.rst_n, dut)
    print(f'data_out after reset  = {dut.data_out.value}') ####need to remove


    await FallingEdge(dut.clk)

    prev_dat0 = dut.data_out.value[7:0]
    prev_dat1 = dut.data_out.value[15:8]
    prev_dat2 = dut.data_out.value[23:16]
    prev_dat3 = dut.data_out.value[31:24]
    prev_dat4 = dut.data_out.value[39:32]
    
    #print(f'prev data_out after first data  = {(prev_dat1),(prev_dat0)}')
    data_in = 0xaa_ffff_aaff
    dbi_enable = 0
    dut.dbi_enable.value = dbi_enable
    dut.data_in.value = data_in

    start = 32
    end = 39
    data_in4 = (data_in >> start) & ((1 << (end - start + 1)) - 1)

    start = 24
    end = 31
    data_in3 = (data_in >> start) & ((1 << (end - start + 1)) - 1)

    start = 16
    end = 23
    data_in2 = (data_in >> start) & ((1 << (end - start + 1)) - 1)


    start = 8
    end = 15
    data_in1 = (data_in >> start) & ((1 << (end - start + 1)) - 1)
    
    start = 0
    end = 7
    data_in0 = (data_in >> start) & ((1 << (end - start + 1)) - 1)

    #print(f'data_in after first data  = {bin(data_in1),bin(data_in0)}')
    
    xor_result0 = prev_dat0.integer ^ data_in0
    xor_result1 = prev_dat1.integer ^ data_in1
    xor_result2 = prev_dat2.integer ^ data_in2
    xor_result3 = prev_dat3.integer ^ data_in3
    xor_result4 = prev_dat4.integer ^ data_in4

    count_ones0 = bin(xor_result0).count('1')
    count_ones1 = bin(xor_result1).count('1')
    count_ones2 = bin(xor_result2).count('1')
    count_ones3 = bin(xor_result3).count('1')
    count_ones4 = bin(xor_result4).count('1')

    print(f'count  = {count_ones0,count_ones1,count_ones2,count_ones3,count_ones4}')


    if count_ones0 > 4:  # If the value is greater than 10 
        cntrl0 = 1
        out_data0 = ~data_in0
    else:
        cntrl0 = 0
        out_data0 = data_in0

    if count_ones1 > 4:  # If the value is greater than 10 
        cntrl1 = 1
        out_data1 = ~data_in1
    else:
        cntrl1 = 0
        out_data1 = data_in1

    if count_ones2 > 4:  # If the value is greater than 10 
        cntrl2 = 1
        out_data2 = ~data_in2
    else:
        cntrl2 = 0
        out_data2= data_in2
    
    if count_ones3> 4:  # If the value is greater than 10 
        cntrl3 = 1
        out_data3 = ~data_in3
    else:
        cntrl3 = 0
        out_data3 = data_in3
    
    if count_ones4 > 4:  # If the value is greater than 10 
        cntrl4 = 1
        out_data4 = ~data_in4
    else:
        cntrl4 = 0
        out_data4 = data_in4


    print(f'control outdata = {cntrl0,cntrl1,cntrl2,cntrl3,cntrl4}')
    #print(f'expected outdata = {bin(out_data1),bin(out_data0)}')

    exp_out_data0 = bin(out_data0)[-8:]
    exp_out_data1 = bin(out_data1)[-8:]
    exp_out_data2 = bin(out_data2)[-8:]
    exp_out_data3 = bin(out_data3)[-8:]
    exp_out_data4 = bin(out_data4)[-8:]


    #print(f'expected outdata = {exp_out_data1,exp_out_data0}')
    past_dbi_enable=dbi_enable
    await FallingEdge(dut.clk)
    ##data_out = dut.data_out.value

    pres_dat4 = dut.data_out.value[39:32].binstr
    pres_dat3 = dut.data_out.value[31:24].binstr
    pres_dat2 = dut.data_out.value[23:16].binstr
    pres_dat1 = dut.data_out.value[15:8].binstr
    pres_dat0 = dut.data_out.value[7:0].binstr

    dat_in4 = bin(data_in4)[2:]
    dat_in3 = bin(data_in3)[2:]
    dat_in2 = bin(data_in2)[2:]
    dat_in1 = bin(data_in1)[2:]
    dat_in0 = bin(data_in0)[2:]
    print(f'dut  data_in = {dat_in4,dat_in3,dat_in2,dat_in1,dat_in0}')
    print(f'dut  outdata = {pres_dat4,pres_dat3,pres_dat2,pres_dat1,pres_dat0}')
    print(f'expected  outdata = {exp_out_data4,exp_out_data3,exp_out_data2,exp_out_data1,exp_out_data0}')

    if past_dbi_enable == 0:
        if pres_dat4 == dat_in4 and pres_dat3 == dat_in3 and pres_dat2 == dat_in2 and pres_dat1 == dat_in1 and pres_dat0 == dat_in0:  # If the value is greater than 10 
             print(f"[INFO] Test 'test_dbi_encoder' completed successfully when dbi_enable is zero.")
             assert pres_dat4 == dat_in4 and pres_dat3 == dat_in3 and pres_dat2 == dat_in2 and pres_dat1 == dat_in1 and pres_dat0 == dat_in0, f"[ERROR] data_out output is not matching to expected output: {dut.data_out.value}"
        else:
            print("[INFO] Test 'test_dbi_encoder' failed when dbi_enable is zero.")

    else:
        if pres_dat4 == exp_out_data4 and pres_dat3 == exp_out_data3 and pres_dat2 == exp_out_data2 and pres_dat1 == exp_out_data1 and pres_dat0 == exp_out_data0:  # If the value is greater than 10 
             print(f"[INFO] Test 'test_dbi_encoder' completed successfully.")
             assert pres_dat4 == exp_out_data4 and pres_dat3 == exp_out_data3 and pres_dat2 == exp_out_data2 and pres_dat1 == exp_out_data1 and pres_dat0 == exp_out_data0, f"[ERROR] data_out output is not matching to expected output: {dut.data_out.value}"
        else:
            print("[INFO] Test 'test_dbi_encoder' failed.")

    



    prev_dat0 = dut.data_out.value[7:0]
    prev_dat1 = dut.data_out.value[15:8]
    prev_dat2 = dut.data_out.value[23:16]
    prev_dat3 = dut.data_out.value[31:24]
    prev_dat4 = dut.data_out.value[39:32]
    
    #print(f'prev data_out after first data  = {(prev_dat1),(prev_dat0)}')
    data_in = 0xaa_ffff_aaff
    dbi_enable = 1
    dut.dbi_enable.value = dbi_enable
    dut.data_in.value = data_in

    start = 32
    end = 39
    data_in4 = (data_in >> start) & ((1 << (end - start + 1)) - 1)

    start = 24
    end = 31
    data_in3 = (data_in >> start) & ((1 << (end - start + 1)) - 1)

    start = 16
    end = 23
    data_in2 = (data_in >> start) & ((1 << (end - start + 1)) - 1)


    start = 8
    end = 15
    data_in1 = (data_in >> start) & ((1 << (end - start + 1)) - 1)
    
    start = 0
    end = 7
    data_in0 = (data_in >> start) & ((1 << (end - start + 1)) - 1)

    #print(f'data_in after first data  = {bin(data_in1),bin(data_in0)}')
    
    xor_result0 = prev_dat0.integer ^ data_in0
    xor_result1 = prev_dat1.integer ^ data_in1
    xor_result2 = prev_dat2.integer ^ data_in2
    xor_result3 = prev_dat3.integer ^ data_in3
    xor_result4 = prev_dat4.integer ^ data_in4

    count_ones0 = bin(xor_result0).count('1')
    count_ones1 = bin(xor_result1).count('1')
    count_ones2 = bin(xor_result2).count('1')
    count_ones3 = bin(xor_result3).count('1')
    count_ones4 = bin(xor_result4).count('1')

    print(f'count  = {count_ones0,count_ones1,count_ones2,count_ones3,count_ones4}')

    

    if count_ones0 > 4:  # If the value is greater than 10 
        cntrl0 = 1
        out_data0 = ~data_in0
    else:
        cntrl0 = 0
        out_data0 = data_in0

    if count_ones1 > 4:  # If the value is greater than 10 
        cntrl1 = 1
        out_data1 = ~data_in1
    else:
        cntrl1 = 0
        out_data1 = data_in1

    if count_ones2 > 4:  # If the value is greater than 10 
        cntrl2 = 1
        out_data2 = ~data_in2
    else:
        cntrl2 = 0
        out_data2= data_in2
    
    if count_ones3> 4:  # If the value is greater than 10 
        cntrl3 = 1
        out_data3 = ~data_in3
    else:
        cntrl3 = 0
        out_data3 = data_in3
    
    if count_ones4 > 4:  # If the value is greater than 10 
        cntrl4 = 1
        out_data4 = ~data_in4
    else:
        cntrl4 = 0
        out_data4 = data_in4

    print(f'data_in4  = {data_in0}')
    print(f'out_data4  = {out_data0}')

    print(f'control outdata = {cntrl0,cntrl1,cntrl2,cntrl3,cntrl4}')
    #print(f'expected outdata = {bin(out_data1),bin(out_data0)}')

    exp_out_data0 = bin(out_data0)[-8:]
    exp_out_data1 = bin(out_data1)[-8:]
    exp_out_data2 = bin(out_data2)[-8:]
    exp_out_data3 = bin(out_data3)[-8:]
    exp_out_data4 = bin(out_data4)[-8:]
    print(f'exp_out_data0  = {exp_out_data0}')

    #print(f'expected outdata = {exp_out_data1,exp_out_data0}')
    past_dbi_enable=dbi_enable
    await FallingEdge(dut.clk)
    ##data_out = dut.data_out.value

    pres_dat4 = dut.data_out.value[39:32].binstr
    pres_dat3 = dut.data_out.value[31:24].binstr
    pres_dat2 = dut.data_out.value[23:16].binstr
    pres_dat1 = dut.data_out.value[15:8].binstr
    pres_dat0 = dut.data_out.value[7:0].binstr

    dat_in4 = bin(data_in4)[2:]
    dat_in3 = bin(data_in3)[2:]
    dat_in2 = bin(data_in2)[2:]
    dat_in1 = bin(data_in1)[2:]
    dat_in0 = bin(data_in0)[2:]
    print(f'dut  data_in = {dat_in4,dat_in3,dat_in2,dat_in1,dat_in0}')
    print(f'dut  outdata = {pres_dat4,pres_dat3,pres_dat2,pres_dat1,pres_dat0}')
    print(f'expected  outdata = {exp_out_data4,exp_out_data3,exp_out_data2,exp_out_data1,exp_out_data0}')

    if past_dbi_enable == 0:
        if pres_dat4 == dat_in4 and pres_dat3 == dat_in3 and pres_dat2 == dat_in2 and pres_dat1 == dat_in1 and pres_dat0 == dat_in0:  # If the value is greater than 10 
             print(f"[INFO] Test 'test_dbi_encoder' completed successfully when dbi_enable is zero.")
             assert pres_dat4 == dat_in4 and pres_dat3 == dat_in3 and pres_dat2 == dat_in2 and pres_dat1 == dat_in1 and pres_dat0 == dat_in0, f"[ERROR] data_out output is not matching to expected output: {dut.data_out.value}"
        else:
            print("[INFO] Test 'test_dbi_encoder' failed when dbi_enable is zero.")

    else:
        if pres_dat4 == exp_out_data4 and pres_dat3 == exp_out_data3 and pres_dat2 == exp_out_data2 and pres_dat1 == exp_out_data1 and pres_dat0 == exp_out_data0:  # If the value is greater than 10 
             print(f"[INFO] Test 'test_dbi_encoder' completed successfully.")
             assert pres_dat4 == exp_out_data4 and pres_dat3 == exp_out_data3 and pres_dat2 == exp_out_data2 and pres_dat1 == exp_out_data1 and pres_dat0 == exp_out_data0, f"[ERROR] data_out output is not matching to expected output: {dut.data_out.value}"
        else:
            print("[INFO] Test 'test_dbi_encoder' failed.")
    