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
  reg [0:0] PI_enable;
  reg [0:0] PI_rst_n;
  wire [0:0] PI_clk = clock;
  reg [7:0] PI_period_cfg;
  pwm_counter UUT (
    .enable(PI_enable),
    .rst_n(PI_rst_n),
    .clk(PI_clk),
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
    // UUT.$auto$async2sync.\cc:107:execute$70  = 1'b0;
    // UUT.$auto$async2sync.\cc:116:execute$74  = 1'b1;
    UUT._witness_.anyinit_procdff_69 = 8'b00001010;

    // state 0
    PI_enable = 1'b1;
    PI_rst_n = 1'b1;
    PI_period_cfg = 8'b00001010;
  end
  always @(posedge clock) begin
    // state 1
    if (cycle == 0) begin
      PI_enable <= 1'b0;
      PI_rst_n <= 1'b0;
      PI_period_cfg <= 8'b00000000;
    end

    genclock <= cycle < 1;
    cycle <= cycle + 1;
  end
endmodule
