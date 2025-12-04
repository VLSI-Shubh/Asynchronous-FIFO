# sim/uvm_env/fifo_monitor.py

import cocotb
from cocotb.triggers import RisingEdge, ReadOnly

from pyuvm import uvm_component, uvm_analysis_port

from .fifo_item import FifoOp
from .dut_ref import get_dut


class FifoMonitor(uvm_component):
    """
    Monitor for the async FIFO interface.

    - Observes WR handshakes on clk_wr, publishes WRITE events.
    - Observes RD handshakes on clk_rd with one-cycle latency, publishes READ events.
    Events are dictionaries:
        { "op": FifoOp.WRITE/READ, "data": <int> }
    The scoreboard uses these to maintain its reference model.
    """

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.ap = uvm_analysis_port("ap", self)
        self.dut = None

    def build_phase(self):
        super().build_phase()
        # Get global DUT handle
        self.dut = get_dut()
        self.logger.info(f"FifoMonitor bound to DUT: {self.dut._name}")

    async def run_phase(self):
        self.logger.info("FifoMonitor running")

        async def monitor_writes():
            """Observe write-side activity on clk_wr."""
            while True:
                await RisingEdge(self.dut.clk_wr)
                await ReadOnly()

                # Ignore during reset
                if int(self.dut.rst_wr.value) == 1:
                    continue

                wr = int(self.dut.wr.value)
                full = int(self.dut.full.value)

                if wr == 1 and full == 0:
                    data = int(self.dut.data_in.value)
                    self.logger.info(
                        f"Monitor observed WRITE data=0x{data:02x}"
                    )
                    evt = {"op": FifoOp.WRITE, "data": data}
                    self.ap.write(evt)

        async def monitor_reads():
            """
            Observe read-side activity on clk_rd.

            Protocol (one-cycle latency):
              - Cycle N: rd asserted, empty == 0 (a read is requested).
              - Cycle N+1: data_out holds the value being read.
            We use prev_rd/prev_empty to line up with the data_out value.
            """
            prev_rd = 0
            prev_empty = 1

            while True:
                await RisingEdge(self.dut.clk_rd)
                await ReadOnly()

                if int(self.dut.rst_rd.value) == 1:
                    prev_rd = 0
                    prev_empty = 1
                    continue

                curr_rd = int(self.dut.rd.value)
                curr_empty = int(self.dut.empty.value)

                # If we requested a read last cycle and FIFO wasn't empty,
                # sample data_out now.
                if prev_rd == 1 and prev_empty == 0:
                    data = int(self.dut.data_out.value)
                    self.logger.info(
                        f"Monitor observed READ data=0x{data:02x}"
                    )
                    evt = {"op": FifoOp.READ, "data": data}
                    self.ap.write(evt)

                prev_rd = curr_rd
                prev_empty = curr_empty

        # Start both monitors
        cocotb.start_soon(monitor_writes())
        cocotb.start_soon(monitor_reads())

        # Keep phase alive
        while True:
            await RisingEdge(self.dut.clk_wr)
