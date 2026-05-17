# Validation Plan: Configurable Parameter PWM Generator

This document defines the validation items corresponding to the system requirements. Each test scenario provides objective evidence that the implemented design fulfills its specification using `cocotb` and SymbiYosys.

### VAL-01: Configurable Interfaces Test
* **Requirement:** [Verifies REQ-01](specification.md#req-01-configurable-interfaces)
* **Method:** In the Python testbench (`cocotb`), the test shall stimulate `period_cfg`, `duty_cfg`, and `enable` with valid extreme values (`0xFF`, `0xFF`, `1`) and verify that no truncation or missing port errors occur during compilation.

### VAL-02: Variable Period Resolution Test
* **Requirement:** [Verifies REQ-02](specification.md#req-02-variable-period-resolution)
* **Method:** Set `period_cfg` to `8'd99` and `enable` to `1`. The testbench shall track the internal counter reset and assert that the total measured time for one complete cycle is exactly 100 clock cycles.

### VAL-03: Active Duty Cycle Generation Test
* **Requirement:** [Verifies REQ-03](specification.md#req-03-active-duty-cycle-generation)
* **Method:** Set `period_cfg` to `8'd99` and `duty_cfg` to `8'd25`. The testbench shall monitor `pwm_out` over one full period, asserting that it remains `1` for exactly 25 clock cycles and `0` for exactly 75 clock cycles.

### VAL-04: 100% Duty Cycle Saturation Test
* **Requirement:** [Verifies REQ-04](specification.md#req-04-100-duty-cycle-saturation)
* **Method:** Set `period_cfg` to `8'd100` and `duty_cfg` to `8'd150`. Formal Verification (SymbiYosys) will be used to `assert(pwm_out == 1)` continuously, proving the output saturates high when the duty request exceeds the period.

### VAL-05: 0% Duty Cycle Priority Test
* **Requirement:** [Verifies REQ-05](specification.md#req-05-0-duty-cycle-priority)
* **Method:** Set `period_cfg` to `8'd100` and `duty_cfg` to `8'd0`. Formal Verification will be used to `assert(pwm_out == 0)` continuously for at least 300 clock cycles, proving the off-state behaves correctly.

### VAL-06: Synchronous Disable Test
* **Requirement:** [Verifies REQ-06](specification.md#req-06-synchronous-disable)
* **Method:** During active PWM generation where `pwm_out` is `1` and the internal counter is greater than `0`, `enable` shall be driven to `0`. The testbench shall assert that on the next clock edge, `pwm_out` goes to `0` and the internal counter returns to `0`.

### VAL-07: Asynchronous Reset Test
* **Requirement:** [Verifies REQ-07](specification.md#req-07-asynchronous-reset)
* **Method:** During active PWM generation where `pwm_out` is `1`, `rst_n` shall be driven to `0` exactly halfway between clock edges. The testbench shall assert that `pwm_out` drops to `0` instantly, before the next rising edge.