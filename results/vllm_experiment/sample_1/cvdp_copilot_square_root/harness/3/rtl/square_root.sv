module square_root #(parameter WIDTH = 16) (
    input  wire [WIDTH-1:0] num,       
    output reg  [WIDTH/2-1:0] root     
);
    reg [WIDTH-1:0] remainder,square;         
    reg [WIDTH/2-1:0] test_bit, temp_square;        
    integer i,j;

    always @(*) 
    begin
        remainder = num;               
        root = 0;                      
        temp_square = 0;
        
      
        for (i = WIDTH/2-1; i >= 0; i = i - 1) 
        begin
            test_bit = 1'b1 << i;      
            temp_square = (root | test_bit);        
            square = 0; 
            for (j = 0; j < WIDTH; j = j + 1) 
            begin
              if (temp_square[j]) 
              begin 
                  square = square + (temp_square << j); 
              end 
            end
          
            if (square <= remainder) 
            begin
                root = root | test_bit; 
            end
        end
    end
endmodule