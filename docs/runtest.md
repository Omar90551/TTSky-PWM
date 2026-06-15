# Regression Testing Guide: PWM Generator

## 1. Overview
This document describes how to execute the automated `cocotb` regression tests for the PWM generator (`tt_um_PWM`) and how to analyze the resulting waveforms.

## 2. Test Execution
All software verification is fully automated using a Makefile. To execute the regression test suite, navigate to the `/test/` directory and run the following command in the terminal:

`make`

*(Note: Ensure your Python virtual environment is activated and `cocotb` is installed prior to running this command).*

## 3. Interpreting Results
The test outputs are printed directly to the console. 
* **Success:** A successful execution is identified by the `cocotb` summary table at the end of the terminal output displaying **PASS** for all test cases.
* **Failure:** If an assertion fails, the console will throw an `AssertionError` and mark the test as **FAIL**.

## 4. Waveform Inspection
During the test execution, the simulator generates a Variable Change Dump (VCD) file. This file records the state of every signal during the simulation. 

The waveform file is stored at:
`./sim_build/tt_um_PWM.vcd`

To inspect the signals visually, open the waveform in GTKWave using the following command:
`gtkwave sim_build/tt_um_PWM.vcd`