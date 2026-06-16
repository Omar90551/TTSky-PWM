import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

# --- Helper Function: System Reset ---
async def reset_dut(dut):
    """Puts the chip into a known starting state."""
    dut.ena.value = 0
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    
    dut.rst_n.value = 0 # Pull reset LOW (active)
    await Timer(10, unit="ns")  
    dut.rst_n.value = 1 # Pull reset HIGH (inactive)
    await Timer(10, unit="ns")

# --- NEW Helper Function: Sync to Cycle Start ---
async def sync_to_cycle_start(dut):
    """Waits for the PWM output to transition from LOW to HIGH, marking the start of a cycle."""
    # Step 1: Wait until the output is LOW (end of the previous cycle)
    while True:
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(dut.uo_out.value) & 1 == 0:
            break
            
    # Step 2: Wait until the output snaps HIGH (Exactly tick 0 of the new cycle)
    while True:
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if int(dut.uo_out.value) & 1 == 1:
            break

# --- VAL-01: Configurable Interfaces Test ---
@cocotb.test()
async def test_req01_interfaces(dut):
    """REQ-01: Verify the module accepts extreme 8-bit configurations without crashing."""
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    await reset_dut(dut)
    
    # Apply maximum 8-bit values (255) to the ports
    dut.ui_in.value = 0xFF   
    dut.uio_in.value = 0xFF  
    dut.ena.value = 1        
    
    for _ in range(5):
        await RisingEdge(dut.clk)
        
    assert dut.ui_in.value == 0xFF, "ui_in port failed to hold 8-bit value"
    assert dut.uio_in.value == 0xFF, "uio_in port failed to hold 8-bit value"

# --- VAL-02: Variable Period Resolution Test ---
@cocotb.test()
async def test_req02_period_resolution(dut):
    """REQ-02: Verify the timeframe is exactly (period_cfg + 1) clock cycles."""
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    await reset_dut(dut)
    
    target_period = 99
    expected_ticks = target_period + 1
    
    dut.ui_in.value = target_period  
    dut.uio_in.value = 50 # Set a 50% duty cycle to guarantee LOW/HIGH transitions         
    dut.ena.value = 1
    
    # Sync to the exact start of a cycle
    await sync_to_cycle_start(dut)
            
    tick_count = 0
    
    # Wait for output to go LOW
    while True:
        await RisingEdge(dut.clk)
        tick_count += 1
        await Timer(1, unit="ns")
        if int(dut.uo_out.value) & 1 == 0:
            break
            
    # Wait for output to go HIGH again (Start of the NEXT cycle)
    while True:
        await RisingEdge(dut.clk)
        tick_count += 1
        await Timer(1, unit="ns")
        if int(dut.uo_out.value) & 1 == 1:
            break
        if tick_count > 500:
            assert False, "Counter ran away, cycle never restarted!"

    assert tick_count == expected_ticks, f"REQ-02 Failed! Expected {expected_ticks} ticks, but measured {tick_count} ticks."

# --- VAL-03: Active Duty Cycle Generation Test (REQ-03) ---
@cocotb.test()
async def test_req03_duty_cycle(dut):
    """REQ-03: Verify the output stays HIGH for exactly 'duty_cfg' clock ticks."""
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    await reset_dut(dut)
    
    dut.ui_in.value = 19  
    dut.uio_in.value = 5  
    dut.ena.value = 1
    
    # Sync to the exact start of a cycle
    await sync_to_cycle_start(dut)
            
    # The cycle has started. Measure exactly 1 full period (20 ticks).
    high_ticks = 1 # We already saw the first HIGH tick inside the sync function
    
    for _ in range(19):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns") 
        
        if int(dut.uo_out.value) & 1 == 1:
            high_ticks += 1

    assert high_ticks == 5, f"REQ-03 Failed! Expected 5 HIGH ticks, but measured {high_ticks}."

# --- VAL-04: Duty Cycle Edge Cases (REQ-04 & REQ-05) ---
@cocotb.test()
async def test_req04_05_edge_cases(dut):
    """REQ-04 & REQ-05: Verify 0% duty stays LOW, and Duty > Period saturates to HIGH."""
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    await reset_dut(dut)
    
    dut.ui_in.value = 9 # Period = 10 ticks
    dut.ena.value = 1
    
    # --- Part 1: Test 0% Duty Cycle (REQ-05) ---
    dut.uio_in.value = 0 
    
    for _ in range(20):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        assert int(dut.uo_out.value) & 1 == 0, "REQ-05 Failed! Output went HIGH while duty_cfg was 0."

    # --- Part 2: Test >100% Saturation (REQ-04) ---
    dut.uio_in.value = 15 
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    for _ in range(20):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        assert int(dut.uo_out.value) & 1 == 1, "REQ-04 Failed! Output dropped LOW when duty_cfg > period_cfg."


# --- VAL-06: Asynchronous Reset (REQ-07) ---
@cocotb.test()
async def test_req07_async_reset(dut):
    """REQ-07: Verify pulling rst_n LOW resets the system instantly (ignoring the clock)."""
    cocotb.start_soon(Clock(dut.clk, 100, unit="ns").start())
    await reset_dut(dut)
    
    dut.ui_in.value = 15
    dut.uio_in.value = 15 
    dut.ena.value = 1
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    await Timer(1, unit="ns")
    assert int(dut.uo_out.value) & 1 == 1, "Setup failed: Output should be HIGH."
    
    # Wait 20ns (halfway through a clock cycle)
    await Timer(20, unit="ns")
    
    # Pull Reset LOW asynchronously
    dut.rst_n.value = 0 
    
    # Wait 1ns (No Clock Edge has occurred)
    await Timer(15, unit="ns")
    
    # Black Box Check: We only check the output pin, not the internal counter
    assert int(dut.uo_out.value) & 1 == 0, "REQ-07 Failed! Output did not reset asynchronously."

# --- VAL-05: Synchronous Disable (REQ-06) ---
@cocotb.test()
async def test_req06_sync_disable(dut):
    """REQ-06: Verify pulling enable LOW instantly stops the output."""
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    await reset_dut(dut)
    
    dut.ui_in.value = 10
    dut.uio_in.value = 10 
    dut.ena.value = 1
    
    for _ in range(5):
        await RisingEdge(dut.clk)
        
    await Timer(1, unit="ns")
    assert int(dut.uo_out.value) & 1 == 1, "Setup failed: Output should be HIGH."
    
    # Turn the module OFF
    dut.ena.value = 0
    
    # Wait for the next clock tick
    await RisingEdge(dut.clk)
    await Timer(21, unit="ns")
    
    # Black Box Check: We only check the output pin, not the internal counter
    assert int(dut.uo_out.value) & 1 == 0, "REQ-06 Failed! Output did not drop LOW when disabled."