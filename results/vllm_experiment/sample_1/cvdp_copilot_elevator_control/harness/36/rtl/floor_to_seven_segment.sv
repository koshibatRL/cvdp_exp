/*
 * Floor to Seven-Segment Display Converter
 * 
 * Converts the current floor number (binary) to a seven-segment display output.
 * Supports floors 0 to N-1, with invalid inputs resulting in a blank display.
 */
module floor_to_seven_segment (
    input wire clk, 
    input wire [7:0] floor_display, // Binary floor number input
    output reg [6:0] seven_seg_out, // Seven-segment display output: {a, b, c, d, e, f, g}
    output [3:0]seven_seg_out_anode, ////Signal for switching between ones, tens, hundred, thousand place on seven segment
    output [3:0] thousand, output[3:0] hundred, output [3:0]ten, output [3:0] one
);

    //Internal signals
     reg [6:0]sseg_temp=7'b1111111;
     reg [3:0]an_temp = 4'b1110 ;
     reg [17:0] count=0; //the 18 bit counter which allows us to multiplex at 1000Hz

     always @ (posedge clk)
      begin
        count <= count + 1;
      end

    //code for display multiple digits
always @(*) begin
    case (count[17:16]) // Using only the 2 MSBs of the counter
        2'b00: // When the 2 MSBs are 00, enable the fourth display
        begin
            case (one)
                4'd0: sseg_temp = 7'b1111110; // Display 0
                4'd1: sseg_temp = 7'b0110000; // Display 1
                4'd2: sseg_temp = 7'b1101101; // Display 2
                4'd3: sseg_temp = 7'b1111001; // Display 3
                4'd4: sseg_temp = 7'b0110011; // Display 4
                4'd5: sseg_temp = 7'b1011011; // Display 5
                4'd6: sseg_temp = 7'b1011111; // Display 6
                4'd7: sseg_temp = 7'b1110000; // Display 7
                4'd8: sseg_temp = 7'b1111111; // Display 8
                4'd9: sseg_temp = 7'b1111011; // Display 9
                default: sseg_temp = 7'b0000000; // Blank display
            endcase
            an_temp = 4'b1110; // Enable the fourth display
        end
        
        2'b01: // When the 2 MSBs are 01, enable the third display
        begin
            case (ten)
                4'd0: sseg_temp = 7'b1111110; // Display 0
                4'd1: sseg_temp = 7'b0110000; // Display 1
                4'd2: sseg_temp = 7'b1101101; // Display 2
                4'd3: sseg_temp = 7'b1111001; // Display 3
                4'd4: sseg_temp = 7'b0110011; // Display 4
                4'd5: sseg_temp = 7'b1011011; // Display 5
                4'd6: sseg_temp = 7'b1011111; // Display 6
                4'd7: sseg_temp = 7'b1110000; // Display 7
                4'd8: sseg_temp = 7'b1111111; // Display 8
                4'd9: sseg_temp = 7'b1111011; // Display 9
                default: sseg_temp = 7'b0000000; // Blank display
            endcase
            an_temp = 4'b1101; // Enable the third display
        end

        2'b10: // When the 2 MSBs are 10, enable the second display
        begin
            case (hundred)
                4'd0: sseg_temp = 7'b1111110; // Display 0
                4'd1: sseg_temp = 7'b0110000; // Display 1
                4'd2: sseg_temp = 7'b1101101; // Display 2
                4'd3: sseg_temp = 7'b1111001; // Display 3
                4'd4: sseg_temp = 7'b0110011; // Display 4
                4'd5: sseg_temp = 7'b1011011; // Display 5
                4'd6: sseg_temp = 7'b1011111; // Display 6
                4'd7: sseg_temp = 7'b1110000; // Display 7
                4'd8: sseg_temp = 7'b1111111; // Display 8
                4'd9: sseg_temp = 7'b1111011; // Display 9
                default: sseg_temp = 7'b0000000; // Blank display
            endcase
            an_temp = 4'b1011; // Enable the second display
        end

        2'b11: // When the 2 MSBs are 11, enable the first display
        begin
            case (thousand)
                4'd0: sseg_temp = 7'b1111110; // Display 0
                4'd1: sseg_temp = 7'b0110000; // Display 1
                4'd2: sseg_temp = 7'b1101101; // Display 2
                4'd3: sseg_temp = 7'b1111001; // Display 3
                4'd4: sseg_temp = 7'b0110011; // Display 4
                4'd5: sseg_temp = 7'b1011011; // Display 5
                4'd6: sseg_temp = 7'b1011111; // Display 6
                4'd7: sseg_temp = 7'b1110000; // Display 7
                4'd8: sseg_temp = 7'b1111111; // Display 8
                4'd9: sseg_temp = 7'b1111011; // Display 9
                default: sseg_temp = 7'b0000000; // Blank display
            endcase
            an_temp = 4'b0111; // Enable the first display
        end
    endcase
end

assign seven_seg_out = sseg_temp;
assign seven_seg_out_anode = an_temp;

    //Binary to BCD covertor to receive seprate bits for ones, tens, hundred, thousand places
    Binary2BCD B1(.num(floor_display),.thousand(thousand), .hundred(hundred),.ten(ten),.one(one) );

endmodule