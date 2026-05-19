`default_nettype none

module pwm_comparator (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       enable,
    input  wire [7:0] count_in,
    input  wire [7:0] period_cfg,
    input  wire [7:0] duty_cfg,
    output reg        pwm_out
);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            // REQ-07: Asynchronous Reset forces output low instantly
            pwm_out <= 1'b0;
        end else if (!enable) begin
            // REQ-06: Synchronous Disable forces output low on the clock edge
            pwm_out <= 1'b0;
        end else begin
            // Priority checks for edge cases
            if (duty_cfg == 8'd0) begin
                // REQ-05: 0% Duty Cycle Priority
                pwm_out <= 1'b0;
            end else if (duty_cfg > period_cfg) begin
                // REQ-04: 100% Saturation if duty exceeds period
                pwm_out <= 1'b1;
            end else begin
                // REQ-03: Active Duty Cycle Generation
                if (count_in < duty_cfg) begin
                    pwm_out <= 1'b1; // Output is HIGH while counter is less than duty
                end else begin
                    pwm_out <= 1'b0; // Output drops LOW for the remainder of the period
                end
            end
        end
    end

endmodule