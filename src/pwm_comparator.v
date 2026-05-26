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
            // REQ-07: Asynchronous Reset
            pwm_out <= 1'b0;
        end else if (!enable) begin
            // REQ-06: Synchronous Disable
            pwm_out <= 1'b0;
        end else begin
            if (duty_cfg == 8'd0) begin
                // REQ-05: 0% duty = always LOW
                pwm_out <= 1'b0;
            end else if (duty_cfg > period_cfg) begin
                // REQ-04: Saturation = always HIGH
                pwm_out <= 1'b1;
            end else begin
                // REQ-03: Normal PWM comparison
                if (count_in < duty_cfg)
                    pwm_out <= 1'b1;
                else
                    pwm_out <= 1'b0;
            end
        end
    end

    `ifdef FORMAL
        reg f_past_valid = 1'b0;
        always @(posedge clk) f_past_valid <= 1'b1;

        // REQ-07: After async reset, output must be 0
        always @(posedge clk) begin
            if (f_past_valid && !$past(rst_n))
                assert(pwm_out == 1'b0);
        end

        // REQ-03/04/05/06: All output logic checks
        always @(posedge clk) begin
            if (f_past_valid && $past(rst_n) && $past(enable)
                             && rst_n && enable) begin
                if ($past(duty_cfg) == 8'd0)
                    assert(pwm_out == 1'b0);
                else if ($past(duty_cfg) > $past(period_cfg))
                    assert(pwm_out == 1'b1);
                else begin
                    if ($past(count_in) < $past(duty_cfg))
                        assert(pwm_out == 1'b1);
                    else
                        assert(pwm_out == 1'b0);
                end
            end
        end

        // COVER: Output can toggle LOW to HIGH
        always @(posedge clk) begin
            if (f_past_valid && $past(rst_n) && $past(enable))
                cover(pwm_out == 1'b1 && $past(pwm_out) == 1'b0);
        end
    `endif

endmodule