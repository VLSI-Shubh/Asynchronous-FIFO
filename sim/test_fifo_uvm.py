# sim/test_fifo_uvm.py

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

from pyuvm import uvm_root

import uvm_env.dut_ref as dut_ref   # global DUT handle
from uvm_env import fifo_tests      # registers FifoBasicTest with pyuvm


async def reset_async_fifo(dut, cycles=4):
    """Asynchronous FIFO reset (both domains)."""
    dut.rst_wr.value = 1
    dut.rst_rd.value = 1
    dut.wr.value = 0
    dut.rd.value = 0
    dut.data_in.value = 0

    # Hold reset for a few cycles on both clocks
    for _ in range(cycles):
        await RisingEdge(dut.clk_wr)
        await RisingEdge(dut.clk_rd)

    dut.rst_wr.value = 0
    dut.rst_rd.value = 0

    # Allow some cycles for pointers/flags to settle
    for _ in range(2):
        await RisingEdge(dut.clk_wr)
        await RisingEdge(dut.clk_rd)


@cocotb.test()
async def run_fifo_basic_uvm_test(dut):
    """
    Top-level cocotb test that launches the pyuvm FifoBasicTest
    on the async FIFO DUT.
    """

    # Start async clocks
    cocotb.start_soon(Clock(dut.clk_wr, 10, unit="ns").start())
    cocotb.start_soon(Clock(dut.clk_rd, 14, unit="ns").start())

    # Reset DUT
    await reset_async_fifo(dut)

    # Publish DUT globally for pyuvm components (no ConfigDB)
    dut_ref.set_dut(dut)

    dut._log.info("Starting async FIFO UVM test (FifoBasicTest via pyuvm)")

    # Run the UVM-style test implemented in uvm_env/fifo_tests.py
    await uvm_root().run_test("FifoBasicTest")

    dut._log.info("Async FIFO UVM test completed")
