`default_nettype none

module pwm_counter (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       enable,
    input  wire [7:0] period_cfg,
    output reg  [7:0] count_out
);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            // REQ-07: Asynchronous Reset
            count_out <= 8'd0;
        end else if (!enable) begin
            // REQ-06: Synchronous Disable resets the counter
            count_out <= 8'd0;
        end else begin
            // REQ-02: Variable Period Resolution
            if (count_out >= period_cfg) begin
                count_out <= 8'd0; // Rollover when we hit the max period
            end else begin
                count_out <= count_out + 8'd1; // Increment normally
            end
        end
    end

endmodule