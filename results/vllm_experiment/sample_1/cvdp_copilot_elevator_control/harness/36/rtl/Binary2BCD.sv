module Binary2BCD(input [7:0] num,output reg [3:0]thousand, output reg [3:0]hundred, output reg [3:0]ten, output reg [3:0]one );
    reg[19:0] shift;
    integer i;
    
    always @(num)
    begin
        shift[19:8] =0;
        shift[7:0]=num;
        
        for(i=0;i<8;i=i+1)
        begin
            if(shift[11:8]>=5)
                shift[11:8]=shift[11:8] +3;
           
            if(shift[15:12]>=5)
                    shift[15:12]=shift[15:12] +3; 

            if(shift[19:16]>=5)
                shift[19:16]=shift[19:16] +3;
            
            shift=shift <<1;                                       
        end
        
        hundred=shift[19:16];
        ten=shift[15:12];
        one=shift[11:8];
        thousand=4'b0000;
        
    end
    
endmodule