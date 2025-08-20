// Top Module integrating Encoder & decoder
module top_manchester #(
    parameter N = 8  // Default width of input and output data
) (
    input  logic clk_in,          // Clock input
    input  logic rst_in,          // Active high reset input
    // Encoder Signals
    input  logic enc_valid_in,        // Input valid signal
    input  logic [N-1:0] enc_data_in, // N-bit input data
    output logic enc_valid_out,       // output valid signal
    output logic [2*N-1:0] enc_data_out, // 2*N-bit encoder output data
    
    // Decoder Signals
    input  logic dec_valid_in,        // Input valid signal
    input  logic [2*N-1:0] dec_data_in, // 2*N-bit input data
    output logic dec_valid_out,       // Output valid signal
    output logic [N-1:0] dec_data_out // N-bit output decoded data
);

    // Instantiate the Manchester encoder module
    manchester_encoder #(
        .N(N)
    ) encoder_dut (
        .clk_in(clk_in),
        .rst_in(rst_in),
        .enc_valid_in(enc_valid_in),
        .enc_data_in(enc_data_in),
        .enc_valid_out(enc_valid_out),
        .enc_data_out(enc_data_out)
    );

    // Instantiate the Manchester decoder module
    manchester_decoder #(
        .N(N)
    ) decoder_dut (
        .clk_in(clk_in),
        .rst_in(rst_in),
        .dec_valid_in(dec_valid_in),
        .dec_data_in(dec_data_in),
        .dec_valid_out(dec_valid_out),
        .dec_data_out(dec_data_out)
    );

endmodule