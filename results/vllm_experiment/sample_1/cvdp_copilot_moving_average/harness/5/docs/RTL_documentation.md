# Moving Average Module Documentation

## Module Overview

The `moving_average` module is a hardware implementation designed to compute the moving average of a sequence of 12-bit data inputs with a window width of 8 samples. This module is typically used in digital signal processing (DSP) applications such as noise reduction, data smoothing, and signal conditioning.

## Inputs and Outputs

- **clk (input, wire)**: Clock signal that drives the memory updates and computations within the module.
- **reset (input, wire)**: Synchronous reset signal, which, when high, resets the module
- **data_in (input, wire[11:0])**: 12-bit input data signal.
- **data_out (output, wire[11:0])**: 12-bit output data signal representing the moving average of the last 8 input data values.

## Internal Components and Implementation

### Memory
- **memory[7:0]**: An array of 8 registers, each storing a 12-bit value, used to hold the last 8 input values for averaging.

### Summation Logic
- **sum[14:0]**: A 15-bit register to maintain the running sum of the values stored in the memory. The latest input is added and the oldest input is subtracted to get the current average value.

### Average Logic
-   **data_out[11:0]**: A 12-bit output representing the average value is calculated by using shift operation on **sum[14:0]**. Window size of 8, requires the summation to be divided by 8, which is implemented by shifting the **sum[14:0]** 3 bits to the right.

### Address Management
- **write_address[2:0]**: A 3-bit register pointing to the location that the new input will be written to.
- **next_address[2:0]**: A 3-bit value pointing to the location of the oldest element in the memory.

###