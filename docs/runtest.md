# Regression Testing Execution Guide

## 1. How to Execute the Tests
The regression test suite is fully automated using a `Makefile`. To run the tests, open a terminal inside the IIC-OSIC-TOOLS Docker container, navigate to this `test` directory, and execute the following command:
`make`

## 2. Where Results are Stored
* **Terminal Output:** A real-time pass/fail matrix is printed directly to the terminal.
* **Log File:** A detailed XML log is generated at `test/results.xml`.
* **Waveforms:** For enabling the inspection of waveforms . The following command should be executed for the test cases . `make WAVES=1` Note that these generated files are excluded from version control via `.gitignore`.

## 3. How to Identify Successful Execution
A successful test run is identified by reading the final table printed in the terminal. The execution is considered a **PASS** only if all individual test cases report a `PASS` status and the final summary reads `FAIL=0`.

## 4. Inspecting Waveforms
To visually inspect the logic, you can open the generated waveform file using GTKWave by executing:
`gtkwave gtkwave tb.fst &`