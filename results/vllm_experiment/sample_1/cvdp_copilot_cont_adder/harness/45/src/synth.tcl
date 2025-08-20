# read verilog
read_verilog -sv /code/rtl/*.sv

# elaborate design hierarchy
hierarchy -check -top cont_adder

# Synthesis check
check -noinit -initdrv -assert

# the high-level stuff
proc; opt; fsm; opt; memory; opt

# mapping to internal cell library
techmap; opt

# generic synthesis
synth -top cont_adder
clean

# write synthetized design
write_verilog -noattr /code/rundir/netlist.v
