import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly, ClockCycles
import random


async def reset_async_fifo(dut, cycles=4):
    """Reset both write and read domains."""
    dut.rst_wr.value = 1
    dut.rst_rd.value = 1
    dut.wr.value = 0
    dut.rd.value = 0
    dut.data_in.value = 0

    for _ in range(cycles):
        await RisingEdge(dut.clk_wr)
        await RisingEdge(dut.clk_rd)

    dut.rst_wr.value = 0
    dut.rst_rd.value = 0

    for _ in range(4):
        await RisingEdge(dut.clk_wr)
        await RisingEdge(dut.clk_rd)


@cocotb.test()
async def test_basic_write_read(dut):
    """Basic smoke test - write and read a few values."""
    dut._log.info("TEST: Basic Write/Read")

    cocotb.start_soon(Clock(dut.clk_wr, 10, unit="ns").start())
    cocotb.start_soon(Clock(dut.clk_rd, 14, unit="ns").start())

    await reset_async_fifo(dut)

    write_values = [0x11, 0x22, 0x33, 0x44]

    # Write phase
    for idx, value in enumerate(write_values):
        await RisingEdge(dut.clk_wr)
        dut.data_in.value = value
        dut.wr.value = 1
        await RisingEdge(dut.clk_wr)
        dut.wr.value = 0
        dut._log.info(f"  Wrote: 0x{value:02x}")

    # Sync wait
    for _ in range(10):
        await RisingEdge(dut.clk_rd)

    # Read phase
    read_values = []
    for i in range(len(write_values)):
        while int(dut.empty.value) == 1:
            await RisingEdge(dut.clk_rd)

        await RisingEdge(dut.clk_rd)
        dut.rd.value = 1
        await RisingEdge(dut.clk_rd)
        dut.rd.value = 0
        await ReadOnly()
        value = int(dut.data_out.value)
        read_values.append(value)
        dut._log.info(f"  Read:  0x{value:02x}")

    assert read_values == write_values
    dut._log.info("✓ PASS")


@cocotb.test()
async def test_full_fifo(dut):
    """Test FIFO full condition - write until full, verify full flag."""
    dut._log.info("TEST: Full FIFO Condition")

    cocotb.start_soon(Clock(dut.clk_wr, 10, unit="ns").start())
    cocotb.start_soon(Clock(dut.clk_rd, 14, unit="ns").start())

    await reset_async_fifo(dut)

    # Write until full (depth = 8 in your logical model,
    # but we just log how many writes it actually takes).
    write_count = 0
    for i in range(20):  # Try to write more than depth
        await RisingEdge(dut.clk_wr)

        if int(dut.full.value) == 1:
            dut._log.info(f"  FIFO full after {write_count} writes")
            break

        dut.data_in.value = i
        dut.wr.value = 1
        await RisingEdge(dut.clk_wr)
        dut.wr.value = 0
        write_count += 1

    # Verify full flag is set (or at least that we hit the condition)
    await RisingEdge(dut.clk_wr)
    assert int(dut.full.value) == 1, "Full flag should be set"

    # Try writing when full - should be ignored by design
    await RisingEdge(dut.clk_wr)
    dut.data_in.value = 0xFF
    dut.wr.value = 1
    await RisingEdge(dut.clk_wr)
    dut.wr.value = 0

    dut._log.info(f"  Wrote {write_count} items (depth=8 logical)")
    dut._log.info("✓ PASS")


@cocotb.test()
async def test_empty_fifo(dut):
    """Test FIFO empty condition."""
    dut._log.info("TEST: Empty FIFO Condition")

    cocotb.start_soon(Clock(dut.clk_wr, 10, unit="ns").start())
    cocotb.start_soon(Clock(dut.clk_rd, 14, unit="ns").start())

    await reset_async_fifo(dut)

    # Verify empty after reset
    await RisingEdge(dut.clk_rd)
    assert int(dut.empty.value) == 1, "FIFO should be empty after reset"

    # Write one value
    await RisingEdge(dut.clk_wr)
    dut.data_in.value = 0xAA
    dut.wr.value = 1
    await RisingEdge(dut.clk_wr)
    dut.wr.value = 0

    # Wait for sync
    for _ in range(10):
        await RisingEdge(dut.clk_rd)

    # Should not be empty
    assert int(dut.empty.value) == 0, "FIFO should not be empty"

    # Read the value
    await RisingEdge(dut.clk_rd)
    dut.rd.value = 1
    await RisingEdge(dut.clk_rd)
    dut.rd.value = 0

    # Should be empty again after a few cycles
    for _ in range(10):
        await RisingEdge(dut.clk_rd)

    assert int(dut.empty.value) == 1, "FIFO should be empty after reading"

    dut._log.info("✓ PASS")


@cocotb.test()
async def test_alternating_clocks(dut):
    """Test with different clock ratios."""
    dut._log.info("TEST: Alternating Clock Speeds")

    # Fast write, slow read
    cocotb.start_soon(Clock(dut.clk_wr, 8, unit="ns").start())
    cocotb.start_soon(Clock(dut.clk_rd, 20, unit="ns").start())

    await reset_async_fifo(dut)

    test_data = [0x10 + i for i in range(8)]

    # Fast writes
    for value in test_data:
        await RisingEdge(dut.clk_wr)
        while int(dut.full.value) == 1:
            await RisingEdge(dut.clk_wr)
        dut.data_in.value = value
        dut.wr.value = 1
        await RisingEdge(dut.clk_wr)
        dut.wr.value = 0

    # Wait for sync
    for _ in range(15):
        await RisingEdge(dut.clk_rd)

    # Slow reads
    read_data = []
    for _ in range(len(test_data)):
        while int(dut.empty.value) == 1:
            await RisingEdge(dut.clk_rd)
        await RisingEdge(dut.clk_rd)
        dut.rd.value = 1
        await RisingEdge(dut.clk_rd)
        dut.rd.value = 0
        await ReadOnly()
        read_data.append(int(dut.data_out.value))

    assert read_data == test_data
    dut._log.info("✓ PASS")


@cocotb.test()
async def test_simultaneous_rw(dut):
    """Test simultaneous read and write operations."""
    dut._log.info("TEST: Simultaneous Read/Write")

    cocotb.start_soon(Clock(dut.clk_wr, 10, unit="ns").start())
    cocotb.start_soon(Clock(dut.clk_rd, 14, unit="ns").start())

    await reset_async_fifo(dut)

    # Pre-fill FIFO with some data
    prefill = [0xA0 + i for i in range(4)]
    for value in prefill:
        await RisingEdge(dut.clk_wr)
        dut.data_in.value = value
        dut.wr.value = 1
        await RisingEdge(dut.clk_wr)
        dut.wr.value = 0

    # Wait for sync
    for _ in range(10):
        await RisingEdge(dut.clk_rd)

    # Now simultaneously write and read
    new_writes = [0xB0 + i for i in range(4)]
    read_data = []

    async def writer():
        for value in new_writes:
            await RisingEdge(dut.clk_wr)
            while int(dut.full.value) == 1:
                await RisingEdge(dut.clk_wr)
            dut.data_in.value = value
            dut.wr.value = 1
            await RisingEdge(dut.clk_wr)
            dut.wr.value = 0

    async def reader():
        for _ in range(len(prefill)):
            while int(dut.empty.value) == 1:
                await RisingEdge(dut.clk_rd)
            await RisingEdge(dut.clk_rd)
            dut.rd.value = 1
            await RisingEdge(dut.clk_rd)
            dut.rd.value = 0
            await ReadOnly()
            read_data.append(int(dut.data_out.value))

    # Run both concurrently
    await cocotb.start_soon(writer())
    await cocotb.start_soon(reader())

    # Wait for both to complete
    await ClockCycles(dut.clk_rd, 20)

    # Read the newly written data
    for _ in range(len(new_writes)):
        while int(dut.empty.value) == 1:
            await RisingEdge(dut.clk_rd)
        await RisingEdge(dut.clk_rd)
        dut.rd.value = 1
        await RisingEdge(dut.clk_rd)
        dut.rd.value = 0
        await ReadOnly()
        read_data.append(int(dut.data_out.value))

    expected = prefill + new_writes
    assert read_data == expected, f"Expected {expected}, got {read_data}"
    dut._log.info("✓ PASS")


@cocotb.test()
async def test_random_pattern(dut):
    """Test with random data patterns."""
    dut._log.info("TEST: Random Data Pattern")

    cocotb.start_soon(Clock(dut.clk_wr, 10, unit="ns").start())
    cocotb.start_soon(Clock(dut.clk_rd, 14, unit="ns").start())

    await reset_async_fifo(dut)

    # Generate random test data
    random.seed(42)
    test_data = [random.randint(0, 255) for _ in range(16)]

    # Write in chunks to avoid overflow
    chunk_size = 4
    all_reads = []

    for chunk_start in range(0, len(test_data), chunk_size):
        chunk = test_data[chunk_start:chunk_start + chunk_size]

        # Write chunk
        for value in chunk:
            await RisingEdge(dut.clk_wr)
            while int(dut.full.value) == 1:
                await RisingEdge(dut.clk_wr)
            dut.data_in.value = value
            dut.wr.value = 1
            await RisingEdge(dut.clk_wr)
            dut.wr.value = 0

        # Wait for sync
        for _ in range(10):
            await RisingEdge(dut.clk_rd)

        # Read chunk
        for _ in range(len(chunk)):
            while int(dut.empty.value) == 1:
                await RisingEdge(dut.clk_rd)
            await RisingEdge(dut.clk_rd)
            dut.rd.value = 1
            await RisingEdge(dut.clk_rd)
            dut.rd.value = 0
            await ReadOnly()
            all_reads.append(int(dut.data_out.value))

    assert all_reads == test_data, f"Expected {test_data}, got {all_reads}"
    dut._log.info("✓ PASS")


@cocotb.test()
async def test_reset_during_operation(dut):
    """Test reset assertion during active operation."""
    dut._log.info("TEST: Reset During Operation")

    cocotb.start_soon(Clock(dut.clk_wr, 10, unit="ns").start())
    cocotb.start_soon(Clock(dut.clk_rd, 14, unit="ns").start())

    await reset_async_fifo(dut)

    # Write some data
    for i in range(4):
        await RisingEdge(dut.clk_wr)
        dut.data_in.value = 0x60 + i
        dut.wr.value = 1
        await RisingEdge(dut.clk_wr)
        dut.wr.value = 0

    # Reset in the middle
    dut._log.info("  Asserting reset mid-operation")
    await reset_async_fifo(dut, cycles=2)

    # Verify empty after reset
    await RisingEdge(dut.clk_rd)
    assert int(dut.empty.value) == 1, "FIFO should be empty after reset"
    assert int(dut.full.value) == 0, "Full flag should be clear after reset"

    # Write and read new data to verify FIFO still works
    await RisingEdge(dut.clk_wr)
    dut.data_in.value = 0xCC
    dut.wr.value = 1
    await RisingEdge(dut.clk_wr)
    dut.wr.value = 0

    for _ in range(10):
        await RisingEdge(dut.clk_rd)

    await RisingEdge(dut.clk_rd)
    dut.rd.value = 1
    await RisingEdge(dut.clk_rd)
    dut.rd.value = 0
    await ReadOnly()
    value = int(dut.data_out.value)

    assert value == 0xCC, f"Expected 0xCC, got 0x{value:02x}"
    dut._log.info("✓ PASS")
