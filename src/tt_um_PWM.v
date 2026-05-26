`default_nettype none

module tt_um_PWM (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so it can be ignored
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    // Internal wire to connect the counter to the comparator
    wire [7:0] internal_count;
    
    // The output wire from our comparator
    wire pwm_signal;

    // Set up the bidirectional Tiny Tapeout IO pins to be Inputs only
    assign uio_oe  = 8'b0000_0000;
    assign uio_out = 8'b0000_0000;

    // Connect the PWM signal to the first output pin. Ground the rest.
    assign uo_out[0]   = pwm_signal;
    assign uo_out[7:1] = 7'b0000_000;

    // Instantiate the Counter Submodule
    pwm_counter u_counter (
        .clk(clk),
        .rst_n(rst_n),
        .enable(ena),               // Using the Tiny Tapeout enable pin
        .period_cfg(ui_in),         // The 8 dedicated input pins
        .count_out(internal_count)
    );

    // Instantiate the Comparator Submodule
    pwm_comparator u_comparator (
        .clk(clk),
        .rst_n(rst_n),
        .enable(ena),               // Using the Tiny Tapeout enable pin
        .count_in(internal_count),  // Read the value from the counter
        .period_cfg(ui_in),         // The 8 dedicated input pins
        .duty_cfg(uio_in),          // The 8 bidirectional input pins
        .pwm_out(pwm_signal)
    );

endmodule