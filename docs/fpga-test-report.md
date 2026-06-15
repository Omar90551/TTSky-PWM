# FPGA Testing Procedure — PWM Generator

This document outlines how to test the physical chip after manufacturing to prove it matches all requirements in our specification.

## 1. Pin Assignment Mapping

| Signal Name | Tiny Tapeout Pin | Direction | Description |
|:---|:---|:---|:---|
| `clk` | Clock Pin | Input | 10 MHz system clock |
| `rst_n` | Reset Pin | Input | Active-LOW reset (0 = Reset, 1 = Run) |
| `ena` | Enable Pin | Input | Active-HIGH enable (1 = Enabled, 0 = Disabled) |
| `period_cfg` | `ui_in[0]` to `ui_in[7]` | Input | 8-bit maximum period value |
| `duty_cfg` | `uio_in[0]` to `uio_in[7]` | Input | 8-bit duty cycle (HIGH time) value |
| `pwm_out` | `uo_out[0]` | Output | Dynamic PWM output signal |

## 2. Measurement Setup

1. **Inputs:** Use an external microcontroller, FPGA, or pattern generator to drive the input pins at a 10 MHz clock rate using 1.8V digital logic levels.
2. **Outputs:** Connect an Oscilloscope probe to `uo_out[0]` with its ground clip attached to the test board ground. 
3. **Scope Settings:** Set your oscilloscope to capture voltage signals from 0V to 1.8V with a timebase fast enough to view 100 ns clock cycles.

---

## 3. Targeted Test Vectors

### Test 1 — Asynchronous Reset (REQ-07)
* **Objective:** Pulling `rst_n` LOW must immediately force `pwm_out` to 0, even in the middle of a clock cycle.

| Clock Cycle | `rst_n` | `ena` | `period_cfg` | `duty_cfg` | Expected `pwm_out` | Measured | Pass / Fail |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | 0 | 1 | 0x0A | 0x05 | **0** | | |
| 1 | 1 | 1 | 0x0A | 0x05 | **1** | | |
| 2 (Mid-Cycle) | 0 | 1 | 0x0A | 0x05 | **0** | | |
| 3 | 0 | 1 | 0x0A | 0x05 | **0** | | |

---

### Test 2 — Synchronous Disable (REQ-06)
* **Objective:** Setting `ena` LOW must force `pwm_out` to 0 on the very next rising clock edge.

| Clock Cycle | `rst_n` | `ena` | `period_cfg` | `duty_cfg` | Expected `pwm_out` | Measured | Pass / Fail |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | 1 | 1 | 0x05 | 0x03 | **1** | | |
| 1 | 1 | 0 | 0x05 | 0x03 | **0** | | |
| 2 | 1 | 0 | 0x05 | 0x03 | **0** | | |

---

### Test 3 — Counter Memory Clearance (REQ-06 Corner Case)
* **Objective:** Disabling the chip must completely wipe the internal counter to 0 so it starts completely fresh when re-enabled without any phase shift.

| Clock Cycle | `rst_n` | `ena` | `period_cfg` | `duty_cfg` | Expected `pwm_out` | Measured | Pass / Fail |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | 1 | 1 | 0x03 | 0x02 | **1** | | |
| 1 | 1 | 0 | 0x03 | 0x02 | **0** | | |
| 2 | 1 | 1 | 0x03 | 0x02 | **1** | | |
| 3 | 1 | 1 | 0x03 | 0x02 | **1** | | |

---

### Test 4 — 0% Duty Cycle Floor (REQ-05)
* **Objective:** Setting `duty_cfg = 0` must force the output to stay low continuously.

| Clock Cycle | `rst_n` | `ena` | `period_cfg` | `duty_cfg` | Expected `pwm_out` | Measured | Pass / Fail |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | 1 | 1 | 0x03 | 0x00 | **0** | | |
| 1 | 1 | 1 | 0x03 | 0x00 | **0** | | |
| 2 | 1 | 1 | 0x03 | 0x00 | **0** | | |

---

### Test 5 — 100% Duty Saturation Ceiling (REQ-04)
* **Objective:** If `duty_cfg` is strictly greater than `period_cfg`, the output must saturate and remain high continuously.

| Clock Cycle | `rst_n` | `ena` | `period_cfg` | `duty_cfg` | Expected `pwm_out` | Measured | Pass / Fail |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | 1 | 1 | 0x02 | 0x08 | **1** | | |
| 1 | 1 | 1 | 0x02 | 0x08 | **1** | | |
| 2 | 1 | 1 | 0x02 | 0x08 | **1** | | |

---

### Test 6 — Normal PWM Pulsing (REQ-02 / REQ-03)
* **Objective:** Verify standard PWM generation. With `period_cfg = 4` (5 total cycles per frame) and `duty_cfg = 2`, the output must stay HIGH for 2 cycles, drop LOW for 3 cycles, and repeat.

| Clock Cycle | `rst_n` | `ena` | `period_cfg` | `duty_cfg` | Expected `pwm_out` | Measured | Pass / Fail |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | 1 | 1 | 0x04 | 0x02 | **1** | | |
| 1 | 1 | 1 | 0x04 | 0x02 | **1** | | |
| 2 | 1 | 1 | 0x04 | 0x02 | **0** | | |
| 3 | 1 | 1 | 0x04 | 0x02 | **0** | | |
| 4 | 1 | 1 | 0x04 | 0x02 | **0** | | |
| 5 | 1 | 1 | 0x04 | 0x02 | **1** | | |

---

### Test 7 — Capping Boundary Check (`duty_cfg == period_cfg`)
* **Objective:** When duty equals period, the output must not saturate completely high. Because a frame lasts `period + 1` cycles, the output must stay HIGH for `period` cycles and drop LOW for exactly 1 cycle at the rollover boundary.

| Clock Cycle | `rst_n` | `ena` | `period_cfg` | `duty_cfg` | Expected `pwm_out` | Measured | Pass / Fail |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | 1 | 1 | 0x03 | 0x03 | **1** | | |
| 1 | 1 | 1 | 0x03 | 0x03 | **1** | | |
| 2 | 1 | 1 | 0x03 | 0x03 | **1** | | |
| 3 | 1 | 1 | 0x03 | 0x03 | **0** | | |
| 4 | 1 | 1 | 0x03 | 0x03 | **1** | | |

---

## 4. FPGA Checklist

| Test Item | Feature Verified | Expected Scope Waveform Result | Pass / Fail |
|:---|:---|:---|:---|
| **Test 1** | Asynchronous Reset (REQ-07) | Drops instantly to 0V mid-cycle | [ &nbsp; ] |
| **Test 2** | Synchronous Disable (REQ-06) | Falls to 0V right on the clock edge | [ &nbsp; ] |
| **Test 3** | Counter Clear Recovery | Re-enables smoothly with 0 phase offset | [ &nbsp; ] |
| **Test 4** | 0% Duty Floor (REQ-05) | Constant, straight low line (0V) | [ &nbsp; ] |
| **Test 5** | 100% Saturation Ceiling (REQ-04)| Constant, straight high line (1.8V) | [ &nbsp; ] |
| **Test 6** | Normal PWM Pulsing (REQ-02/03) | Alternating 2-cycle high, 3-cycle low pulse | [ &nbsp; ] |
| **Test 7** | Equal Boundary Check | Stays high with a single brief drop-to-zero | [ &nbsp; ] |

**Final Chip Validation Status: [ PASS / FAIL ]**