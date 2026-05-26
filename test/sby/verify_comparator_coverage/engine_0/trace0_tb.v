`ifndef VERILATOR
module testbench;
  reg [4095:0] vcdfile;
  reg clock;
`else
module testbench(input clock, output reg genclock);
  initial genclock = 1;
`endif
  reg genclock = 1;
  reg [31:0] cycle = 0;
  wire [0:0] PI_clk = clock;
  reg [7:0] PI_count_in;
  reg [7:0] PI_duty_cfg;
  reg [0:0] PI_enable;
  reg [0:0] PI_rst_n;
  reg [7:0] PI_period_cfg;
  pwm_comparator UUT (
    .clk(PI_clk),
    .count_in(PI_count_in),
    .duty_cfg(PI_duty_cfg),
    .enable(PI_enable),
    .rst_n(PI_rst_n),
    .period_cfg(PI_period_cfg)
  );
`ifndef VERILATOR
  initial begin
    if ($value$plusargs("vcd=%s", vcdfile)) begin
      $dumpfile(vcdfile);
      $dumpvars(0, testbench);
    end
    #5 clock = 0;
    while (genclock) begin
      #5 clock = 0;
      #5 clock = 1;
    end
  end
`endif
  initial begin
`ifndef VERILATOR
    #1;
`endif
    // UUT.$auto$async2sync.\cc:107:execute$127  = 1'b0;
    // UUT.$auto$async2sync.\cc:116:execute$131  = 1'b1;
    UUT._witness_.anyinit_procdff_110 = 1'b0;
    UUT._witness_.anyinit_procdff_111 = 1'b0;
    UUT._witness_.anyinit_procdff_112 = 1'b0;
    UUT._witness_.anyinit_procdff_126 = 1'b0;
    UUT.f_past_valid = 1'b0;

    // state 0
    PI_count_in = 8'b00000000;
    PI_duty_cfg = 8'b10000000;
    PI_enable = 1'b1;
    PI_rst_n = 1'b1;
    PI_period_cfg = 8'b00000000;
  end
  always @(posedge clock) begin
    // state 1
    if (cycle == 0) begin
      PI_count_in <= 8'b00000000;
      PI_duty_cfg <= 8'b00000000;
      PI_enable <= 1'b0;
      PI_rst_n <= 1'b1;
      PI_period_cfg <= 8'b00000000;
    end

    // state 2
    if (cycle == 1) begin
      PI_count_in <= 8'b00000000;
      PI_duty_cfg <= 8'b00000000;
      PI_enable <= 1'b0;
      PI_rst_n <= 1'b0;
      PI_period_cfg <= 8'b00000000;
    end

    genclock <= cycle < 2;
    cycle <= cycle + 1;
  end
endmodule
