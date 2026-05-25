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

# --- VAL-01: Configurable Interfaces Test ---
@cocotb.test()
async def test_req01_interfaces(dut):
    """REQ-01: Verify the module accepts extreme 8-bit configurations without crashing."""
    
    # Start a 50MHz clock (20ns period)
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    await reset_dut(dut)
    
    # Apply maximum 8-bit values (255) to the ports
    dut.ui_in.value = 0xFF   
    dut.uio_in.value = 0xFF  
    dut.ena.value = 1        
    
    # Wait a few clock cycles
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
    dut.uio_in.value = 50            
    dut.ena.value = 1
    
    # Wait for the internal counter to hit exactly 0 (The true start of a cycle)
    while True:
        await RisingEdge(dut.clk)
        if dut.user_project.u_counter.count_out.value == 0:
            break
            
    # Now, count exactly how many clock ticks it takes for the NEXT cycle to start
    tick_count = 0
    
    while True:
        await RisingEdge(dut.clk)
        tick_count += 1
        
        # If the internal counter resets to 0, the cycle has restarted
        if dut.user_project.u_counter.count_out.value == 0:
            break
            
        if tick_count > 500:
            assert False, "Counter ran away, cycle never restarted!"

    # The moment of truth
    assert tick_count == expected_ticks, f"REQ-02 Failed! Expected {expected_ticks} ticks, but measured {tick_count} ticks."

# --- VAL-03: Active Duty Cycle Generation Test (REQ-03) ---
@cocotb.test()
async def test_req03_duty_cycle(dut):
    """REQ-03: Verify the output stays HIGH for exactly 'duty_cfg' clock ticks."""
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    await reset_dut(dut)
    
    # Configuration: Total period = 20 ticks (19 + 1). HIGH time = 5 ticks.
    dut.ui_in.value = 19  
    dut.uio_in.value = 5  
    dut.ena.value = 1
    
    # Wait for the internal counter to hit 0 (Start of cycle)
    while True:
        await RisingEdge(dut.clk)
        if dut.user_project.u_counter.count_out.value == 0:
            break
            
    # The cycle has started. We will measure exactly 1 full period (20 ticks).
    high_ticks = 0
    
    for _ in range(20):
        # Because of the 1-clock pipeline delay in the comparator flip-flop, 
        # the output updates slightly after the clock edge. We wait 1ns to read it.
        await Timer(1, unit="ns") 
        
        if int(dut.uo_out.value) & 1 == 1:
            high_ticks += 1
            
        await RisingEdge(dut.clk)

    # The moment of truth
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
    
    # Run for a few full cycles (20 ticks)
    for _ in range(20):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        assert int(dut.uo_out.value) & 1 == 0, "REQ-05 Failed! Output went HIGH while duty_cfg was 0."

    # --- Part 2: Test >100% Saturation (REQ-04) ---
    # The user enters a duty cycle (15) larger than the period (9)
    dut.uio_in.value = 15 
    
    # Wait 2 clock ticks for the new duty cycle to propagate through the pipeline
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Run for a few full cycles (20 ticks)
    for _ in range(20):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        assert int(dut.uo_out.value) & 1 == 1, "REQ-04 Failed! Output dropped LOW when duty_cfg > period_cfg."


# --- VAL-06: Asynchronous Reset (REQ-07) ---
@cocotb.test()
async def test_req07_async_reset(dut):
    """REQ-07: Verify pulling rst_n LOW resets the system instantly (ignoring the clock)."""
    # Start a SLOW clock so we can easily test between the clock edges
    cocotb.start_soon(Clock(dut.clk, 100, unit="ns").start())
    await reset_dut(dut)
    
    dut.ui_in.value = 15
    dut.uio_in.value = 15 
    dut.ena.value = 1
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Verify it is currently running HIGH
    await Timer(1, unit="ns")
    assert int(dut.uo_out.value) & 1 == 1, "Setup failed: Output should be HIGH."
    
    # The Test: Press the Reset button halfway through a clock cycle
    # We deliberately wait 20ns (not enough for a full 100ns clock tick)
    await Timer(20, unit="ns")
    
    # Pull Reset LOW
    dut.rst_n.value = 0 
    
    # Wait just 1ns (No Clock Edge!)
    await Timer(1, unit="ns")
    
    assert int(dut.uo_out.value) & 1 == 0, "REQ-07 Failed! Output did not reset asynchronously."
    assert dut.user_project.u_counter.count_out.value == 0, "REQ-07 Failed! Counter did not reset asynchronously."

    # --- VAL-05: Synchronous Disable (REQ-06) ---
@cocotb.test()
async def test_req06_sync_disable(dut):
    """REQ-06: Verify pulling enable LOW instantly stops the output and resets the counter."""
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    await reset_dut(dut)
    
    # Set to 100% saturation so the output is constantly HIGH
    dut.ui_in.value = 10
    dut.uio_in.value = 10 
    dut.ena.value = 1
    
    # LET THE CLOCK TICK SO THE HARDWARE UPDATES!
    for _ in range(5):
        await RisingEdge(dut.clk)
        
    # Verify it is currently running HIGH
    await Timer(1, unit="ns")
    assert int(dut.uo_out.value) & 1 == 1, "Setup failed: Output should be HIGH."
    
    # The Test: Turn the module OFF
    dut.ena.value = 0
    
    # Wait for the next clock tick (Synchronous)
    await RisingEdge(dut.clk)
    await Timer(20, unit="ns")
    
    assert int(dut.uo_out.value) & 1 == 0, "REQ-06 Failed! Output did not drop LOW when disabled."
    assert dut.user_project.u_counter.count_out.value == 0, "REQ-06 Failed! Counter did not reset to 0 when disabled."
