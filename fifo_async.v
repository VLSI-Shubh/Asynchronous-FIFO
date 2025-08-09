/*
 * Asynchoronus FIFO module with separate read/write clocks, Reset signals.
 *
 * This FIFO module is heavily commented on purpose. Some parts of the code 
 * may look different from common RTL styles, but that decision is  made 
 * intentionally to simplify the design and make it easier to understand — 
 * especially for beginners or for revisiting the logic later.
 *
 * This design uses Gray-coded pointers and double flip-flop synchronizers
 * to safely cross clock domains without metastability.
 *
 * Key features:
 * - Extra MSB in pointers helps differentiate full vs empty conditions.
 * - Full flag is set when write pointer has wrapped and caught up to read pointer.
 * - Empty flag is set when read and write pointers match.
 * - Uses simple register array for storage.
 * 
 */

module fifo_async #(
    parameter depth = 8,
    parameter width = 8
) (
    input [width-1 : 0] data_in,
    input clk_wr, clk_rd, rst_wr, rst_rd,rd, wr,
    output reg [width-1:0] data_out, 
    output full, empty
);
    // Main memory block of the FIFO — it's just a simple register file not the actual module.
    // you can choose to tgive it some other name as well
    // Each entry is 'width' bits wide, and we have 'depth' entries.
    reg [width-1 : 0] fifo [0 : depth-1];

    // This is used for the pointer width just like in synchoronus.
    localparam ptr_depth = $clog2(depth); 

    // We're using one extra bit in the read and write pointers.
    // This helps us distinguish between full and empty states.
    // Without this extra MSB, wr_ptr == rd_ptr would always look like 'empty',
    // but with the extra bit, we can tell when the FIFO has wrapped around. 
    // Binary pointers for write and read positions.
    reg [ptr_depth : 0] wr_ptr_bin,wr_ptr_s1,wr_ptr_s2;
    reg [ptr_depth : 0] rd_ptr_bin,rd_ptr_s1,rd_ptr_s2;

    // Gray-coded pointers derived from binary pointers.
    wire [ptr_depth : 0]wr_ptr_gray,rd_ptr_gray;

    // To keep things clear and avoid confusion while coding, I handled these related parts together:
    // I wrote the binary-to-Gray code conversion for both pointers consecutively,
    // and then the rest of the logic step-by-step.
    // This way, you can easily track both pointers and avoid mistakes,
    // since their operations are complementary to each other.

    // It’s also a personal preference whether you want to do the full and empty condition
    // calculations inside clocked blocks or outside using continuous assignments.
    // I found it more convenient to compute them outside the clock with blocking assignments.

    // Convert binary pointers to Gray code.
    assign wr_ptr_gray = wr_ptr_bin ^ (wr_ptr_bin >> 1);

    assign rd_ptr_gray = rd_ptr_bin ^ (rd_ptr_bin >> 1);

    // Write logic — This logic runs on write clock domain.
    always @(posedge clk_wr or posedge rst_wr) begin
        if (rst_wr) begin
            wr_ptr_bin <= 0;
        end else begin
            if (wr && !full) begin
                fifo[wr_ptr_bin[ptr_depth-1 : 0]] <= data_in;
                wr_ptr_bin <= wr_ptr_bin + 1'b1; // dont forget to increment the pointer
            end 
        end
    end

    // Read logic —This lofic  runs on read clock domain.
    always @(posedge clk_rd or posedge rst_rd) begin
        if (rst_rd) begin
            data_out <= 0;
            rd_ptr_bin <= 0;
        end else begin
            if (rd && !empty) begin
                data_out <= fifo[rd_ptr_bin[ptr_depth-1:0]];
                rd_ptr_bin <= rd_ptr_bin +1'b1; // dont forget to increment the pointer
            end else begin
               if(!rd) begin 
                data_out <= 'bz;
               end 
            end
        end
    end

    //Another important point:
    // The write pointer is synchronized into the read clock domain,
    // and the read pointer is synchronized into the write clock domain.
    // Using Gray code is crucial here because only one bit changes at a time,
    // which helps prevent false full or empty flags due to metastability.
    
    // Synchronize write pointer Gray code into read clock domain.
    // Two flip-flops used to safely cross clock domains.
   always @(posedge clk_rd or posedge rst_rd) begin
        if (rst_rd) begin
            wr_ptr_s1 <= 0;
            wr_ptr_s2 <= 0;
        end else begin
            wr_ptr_s1 <= wr_ptr_gray;
            wr_ptr_s2 <= wr_ptr_s1;
        end
    end
    // Synchronize read pointer Gray code into write clock domain.
    always @(posedge clk_wr or posedge rst_wr) begin
        if (rst_wr) begin
            rd_ptr_s1 <= 0;
            rd_ptr_s2 <= 0;
        end else begin
            rd_ptr_s1 <= rd_ptr_gray;
            rd_ptr_s2 <= rd_ptr_s1;
        end
    end


    // Full flag logic — evaluated in write clock domain.
    // This checks if the write pointer has wrapped around and caught up to the read pointer.
    // We flip the MSB of the write pointer and compare it with the read pointer.

        assign full = {~wr_ptr_gray[ptr_depth], wr_ptr_gray[ptr_depth-1:0]} == rd_ptr_s2;

    // Empty flag logic — evaluated in read clock domain.
    // If the read and write pointers are equal, then the FIFO is empty.

        assign empty = rd_ptr_gray == wr_ptr_s2;


endmodule