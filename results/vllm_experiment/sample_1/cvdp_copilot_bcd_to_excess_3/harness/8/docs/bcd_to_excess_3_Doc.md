# BCD to Excess-3 Code Converter Documentation
## Overview
This document provides the specifications and details for the Verilog module `bcd_to_excess_3`, which converts a 4-bit Binary-Coded Decimal (BCD) input into its corresponding 4-bit Excess-3 code. The module also includes an error flag to indicate invalid inputs, specifically for non-BCD values.

## Module Details

### Module Name
`bcd_to_excess_3`

### Description
The `bcd_to_excess_3` module takes a 4-bit BCD input and outputs a 4-bit Excess-3 code. For invalid inputs (BCD values outside the range 0000 to 1001), the output is set to `0000`, and an error flag is raised to `1`. This module operates combinationally and updates its output whenever the BCD input changes.

## Interface

### Port Definitions
- **Input**
  - `bcd` (4 bits): A 4-bit input representing a Binary-Coded Decimal (BCD) number. Valid values range from 0000 to 1001.
  
- **Outputs**
  - `excess3` (4 bits): A 4-bit output representing the Excess-3 code equivalent of the input BCD number.
  - `error` (1 bit): A flag that indicates if the input BCD value is invalid. Set to `1` for values outside the valid BCD range.

## Functional Behavior

### Conversion Table
The module maps each valid 4-bit BCD input to its corresponding Excess-3 code as follows:

| BCD Input (bcd) | Excess-3 Output (excess3) |
|-----------------|---------------------------|
| 0000            | 0011                      |
| 0001            | 0100                      |
| 0010            | 0101                      |
| 0011            | 0110                      |
| 0100            | 0111                      |
| 0101            | 1000                      |
| 0110            | 1001                      |
| 0111            | 1010                      |
| 1000            | 1011                      |
| 1001            | 1100                      |

For inputs outside the valid BCD range (1010 to 1111):
- `excess3` output is set to `0000`.
- `error` flag is set to `1` to indicate an invalid input.

### Timing and Sensitivity
This module is purely combinational and updates the output in response to any changes in the `bcd` input. It does not rely on a clock signal.

## Conclusion
The `bcd_to_excess_3` module provides an efficient and reliable way to convert BCD numbers into their Excess-3 representation while handling invalid inputs through an error flag. Designed to operate as a purely combinational module, it instantly reflects any change in the input through the output without the need for a clock signal. This design ensures correct mapping for valid BCD values and robust error handling for out-of-range inputs, making it suitable for applications requiring straightforward BCD-to-Excess-3 conversions.