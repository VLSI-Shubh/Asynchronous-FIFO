`timescale 1ns/1ns
`include "../src/fifo_async.v"

module fifo_async_tb;

    parameter WIDTH = 8;

    reg clk_rd, clk_wr, rst_rd, rst_wr;
    reg wr, rd;
    reg [WIDTH-1:0] data_in;
    wire [WIDTH-1:0] data_out;
    wire full, empty;


    fifo_async #( .depth(8), .width(WIDTH) ) uut (
    .data_in(data_in),
    .clk_wr(clk_wr),
    .clk_rd(clk_rd),
    .rst_wr(rst_wr),
    .rst_rd(rst_rd),
    .rd(rd),
    .wr(wr),
    .data_out(data_out),
    .full(full),
    .empty(empty)
    );

    // Clock generation
    initial begin
        clk_wr = 0;
        forever #5 clk_wr = ~clk_wr;  // 10ns write clock
    end

    initial begin
        clk_rd = 0;
        forever #7 clk_rd = ~clk_rd;  // 14ns read clock (asynchronous)
    end

    initial begin
        $dumpfile("fifo_async_tb.vcd");
        $dumpvars(0, fifo_async_tb);
    end

    initial begin
        // Step 1: Initialize all inputs
        rst_wr = 1; rst_rd = 1;
        wr = 0; rd = 0;
        data_in = 8'd0;

        // Step 2: Apply reset for both domains
        #13 rst_wr = 0; rst_rd = 0;

        // Step 3: Write 3 values into the FIFO
        #10 wr = 1; data_in = 8'd10;
        #10        data_in = 8'd20;
        #10        data_in = 8'd30;
        #10 wr = 0;                  // Stop writing

        // Step 4: Read 3 values out of the FIFO
        #10 rd = 1;
        #80 rd = 0;                  // Stop reading

        // Step 5: Fill FIFO to test full condition
        #10 wr = 1; data_in = 8'd40;
        #10        data_in = 8'd50;
        #10        data_in = 8'd60;
        #10        data_in = 8'd70;
        #10        data_in = 8'd80;
        #10        data_in = 8'd90;
        #10        data_in = 8'd100;
        #10        data_in = 8'd120;
        #10 wr = 0;

        // Step 6: Empty the FIFO to test empty condition
        #10 rd = 1;
        #10;
        #10;
        #10;
        #10;
        #10 rd = 0;

        // Done
        #20 $finish;
    end


    initial begin
        $monitor("Time=%0t | rst_wr=%b | rst_rd=%b | wr=%b | rd=%b | data_in=%0d | data_out=%0d | full=%b | empty=%b",
                 $time, rst_wr, rst_rd, wr, rd, data_in, data_out, full, empty);
    end

endmodule
