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
                count_out <= 8'd0;
            end else begin
                count_out <= count_out + 8'd1;
            end
        end
    end

    `ifdef FORMAL
        reg f_past_valid = 1'b0;
        always @(posedge clk) f_past_valid <= 1'b1;

        // REQ-07: After async reset, counter must be 0
        always @(posedge clk) begin
            if (f_past_valid && !$past(rst_n))
                assert(count_out == 8'd0);
        end

        // REQ-06 + REQ-02: Disable and boundary checks
        always @(posedge clk) begin
            if (f_past_valid && $past(rst_n)) begin
                if (!$past(enable))
                    assert(count_out == 8'd0);
                if ($past(enable) && $past(period_cfg) > 0)
                    assert(count_out <= $past(period_cfg));
            end
        end

        // COVER: Counter can actually reach value 10
        always @(posedge clk) begin
            if (rst_n && enable && period_cfg == 8'd10)
                cover(count_out == 8'd10);
        end
    `endif

endmodule