/*
 * Floor to Seven-Segment Display Converter
 * 
 * Converts the current floor number (binary) to a seven-segment display output.
 * Supports floors 0 to N-1, with invalid inputs resulting in a blank display.
 */
module floor_to_seven_segment #(
    parameter N = 8 // Number of floors, assumes floors are numbered 0 to N-1
)(
    input wire [$clog2(N)-1:0] floor_display, // Binary floor number input
    output reg [6:0] seven_seg_out // Seven-segment display output: {a, b, c, d, e, f, g}
);

    always @(*) begin
        case (floor_display)
            4'd0: seven_seg_out = 7'b1111110; // 0
            4'd1: seven_seg_out = 7'b0110000; // 1
            4'd2: seven_seg_out = 7'b1101101; // 2
            4'd3: seven_seg_out = 7'b1111001; // 3
            4'd4: seven_seg_out = 7'b0110011; // 4
            4'd5: seven_seg_out = 7'b1011011; // 5
            4'd6: seven_seg_out = 7'b1011111; // 6
            4'd7: seven_seg_out = 7'b1110000; // 7
            4'd8: seven_seg_out = 7'b1111111; // 8
            4'd9: seven_seg_out = 7'b1111011; // 9
            default: seven_seg_out = 7'b0000000; // Blank display for invalid floor numbers
        endcase
    end

endmodule