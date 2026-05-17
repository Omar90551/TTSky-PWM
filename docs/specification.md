# System Specification: Configurable Parameter PWM Generator

This document defines the system requirements for a Pulse Width Modulation (PWM) generator with runtime-configurable period and duty cycle parameters. All requirements are formulated according to the SMART criteria.

### REQ-01: Configurable Interfaces
The PWM module shall accept an 8-bit input vector `period_cfg` to define the maximum counter value, an 8-bit input vector `duty_cfg` to define the active high-time, and a 1-bit `enable` signal to control operation.
* **Validation:** [See VAL-01](validation.md#val-01-configurable-interfaces-test)

### REQ-02: Variable Period Resolution
When `enable` is high (1), the module shall generate a repeating timeframe with a total duration of exactly (`period_cfg` + 1) clock cycles.
* **Validation:** [See VAL-02](validation.md#val-02-variable-period-resolution-test)

### REQ-03: Active Duty Cycle Generation
When `enable` is high (1) and `duty_cfg` is less than or equal to `period_cfg`, the output `pwm_out` shall be driven to logic high (1) for exactly `duty_cfg` consecutive clock cycles at the start of the period, and logic low (0) for the remainder of the period.
* **Validation:** [See VAL-03](validation.md#val-03-active-duty-cycle-generation-test)

### REQ-04: 100% Duty Cycle Saturation
If the `duty_cfg` input is configured to a value strictly greater than `period_cfg`, the output `pwm_out` shall remain continuously at logic high (1) with no low-transitions during the period.
* **Validation:** [See VAL-04](validation.md#val-04-100-duty-cycle-saturation-test)

### REQ-05: 0% Duty Cycle Priority
If the `duty_cfg` input is configured to `8'h00`, the output `pwm_out` shall remain continuously at logic low (0) for the entire period, overriding REQ-03.
* **Validation:** [See VAL-05](validation.md#val-05-0-duty-cycle-priority-test)

### REQ-06: Synchronous Disable
When the `enable` input is driven to logic low (0), the `pwm_out` signal shall be driven to logic low (0) on the next rising clock edge, and the internal counter shall be synchronously reset to 0.
* **Validation:** [See VAL-06](validation.md#val-06-synchronous-disable-test)

### REQ-07: Asynchronous Reset
Upon the assertion of an active-low reset signal (`rst_n = 0`), the internal counter shall reset to 0 and the `pwm_out` signal shall immediately drop to logic low (0), independent of the clock edge.
* **Validation:** [See VAL-07](validation.md#val-07-asynchronous-reset-test)