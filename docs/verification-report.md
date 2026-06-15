# Verification Report: PWM Generator

## 1. Overview
This document consolidates all verification evidence for the PWM generator (`tt_um_PWM`) and its submodules. It maps the successful execution of both Formal Verification (mathematical proofs via SymbiYosys) and automated regression tests (software simulation via cocotb) directly to the specified system requirements.

---

## 2. Verification Evidence

### 2.1 Submodule Formal Verification (SymbiYosys)
*These tests mathematically prove that the individual submodules (`pwm_counter` and `pwm_comparator`) operate safely, adhere to all bounds, and can reach their intended operational states.*

| Requirement ID | Description | Target Module | Verification Type | Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-07** | **Counter Async Reset:** Asserts that `count_out` is forced to `8'd0` immediately following an asynchronous reset. | `pwm_counter` | Assert (BMC) | **PASS** |
| **REQ-02, REQ-06** | **Counter Bounds & Sync Disable:** Asserts that the counter resets to `8'd0` upon disable, and never exceeds `period_cfg` during operation. | `pwm_counter` | Assert (BMC) | **PASS** |
| **COVERAGE** | **Counter Reachability:** Proves the counter is physically capable of counting up to a configured value (e.g., `8'd10`). | `pwm_counter` | Cover | **PASS** |
| **REQ-07** | **Comparator Async Reset:** Asserts that `pwm_out` is forced to `1'b0` immediately following an asynchronous reset. | `pwm_comparator`| Assert (BMC) | **PASS** |
| **REQ-03, 04, 05, 06**| **Comparator Output Logic:** Asserts that `pwm_out` strictly obeys 0% duty cycles, 100% saturation, synchronous disables, and normal PWM limit comparisons. | `pwm_comparator`| Assert (BMC) | **PASS** |
| **COVERAGE** | **Output Toggling:** Proves the `pwm_out` signal is physically capable of transitioning from LOW to HIGH under valid operating conditions. | `pwm_comparator`| Cover | **PASS** |

---

### 2.2 Top-Level Regression Testing (cocotb)
*These tests verify the complete, integrated top-level module (`tt_um_PWM`) behavior by applying stimuli over simulated time.*

| Requirement ID | Description | Executed Test Case | Outcome | Relevance to Requirement |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-01** | **8-bit Configuration** | `test_req01_interfaces` | **PASS** | Validates that the module correctly receives and processes 8-bit `ui_in` (period) and `uio_in` (duty cycle) vectors up to their maximum values (255). |
| **REQ-02** | **Period Resolution** | `test_req02_period_resolution` | **PASS** | Confirms that the total duration of one complete PWM cycle exactly matches the requested number of clock cycles based on the input configuration. |
| **REQ-03** | **Duty Cycle Generation** | `test_req03_duty_cycle` | **PASS** | Verifies the accuracy of the HIGH signal duration, ensuring it precisely matches the configured duty cycle input. |
| **REQ-04** | **100% Saturation** | `test_req04_05_edge_cases` | **PASS** | Confirms that if the duty cycle is configured to be equal to or greater than the period, the output remains safely saturated at a constant HIGH (`1`). |
| **REQ-05** | **0% Duty Cycle** | `test_req04_05_edge_cases` | **PASS** | Verifies that configuring a duty cycle of `0` results in a constant LOW (`0`) output, successfully turning off the PWM pulse. |
| **REQ-06** | **Synchronous Enable** | `test_req06_sync_disable` | **PASS** | Validates that deasserting the `ena` pin instantly halts the PWM generation and resets the internal counter, proving synchronous control. |
| **REQ-07** | **Asynchronous Reset** | `test_req07_async_reset` | **PASS** | Validates that dropping the `rst_n` pin immediately drives the output LOW, regardless of the clock state. |

---

## 3. Conclusive Statement
The PWM generator design has been exhaustively verified. The internal arithmetic and logic boundaries of the `pwm_counter` and `pwm_comparator` submodules were mathematically proven using SymbiYosys formal verification (`sby`), ensuring no illegal states or bounding errors can occur. 

The integrated top-level module was subsequently verified through the automated regression test suite implemented via `cocotb`. Every test case passed successfully, generating sufficient, reproducible evidence to prove that all functional requirements specified for this hardware project have been fully met. 

**Overall Verification Status: PASS**