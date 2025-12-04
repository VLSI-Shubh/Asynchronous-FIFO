# sim/uvm_env/fifo_driver.py
"""
UVM-style driver for the ASYNC FIFO using pyuvm.

- For WRITE items: use clk_wr, wait for !full, drive data_in + wr pulse
- For READ items:  use clk_rd, wait for !empty, drive rd pulse
"""

from cocotb.triggers import RisingEdge
from pyuvm import uvm_driver

from .fifo_item import FifoItem, FifoOp
from .dut_ref import get_dut


class FifoDriver(uvm_driver):
    """
    Drives FifoItem transactions onto the async FIFO DUT.

    DUT handle is obtained from dut_ref.get_dut(), not from any config DB.
    """

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.dut = None

    def build_phase(self):
        super().build_phase()
        self.dut = get_dut()
        self.logger.info(f"FifoDriver bound to DUT: {self.dut._name}")

    async def run_phase(self):
        self.logger.info("FifoDriver starting run_phase")

        while True:
            # Get next transaction
            item: FifoItem = await self.seq_item_port.get_next_item()
            self.logger.info(f"Driving item: {item}")

            if item.op == FifoOp.WRITE:
                # WRITE domain uses clk_wr and 'full'
                while int(self.dut.full.value) == 1:
                    await RisingEdge(self.dut.clk_wr)

                # Drive write handshake
                self.dut.data_in.value = item.data
                self.dut.wr.value = 1
                await RisingEdge(self.dut.clk_wr)
                self.dut.wr.value = 0

            elif item.op == FifoOp.READ:
                # READ domain uses clk_rd and 'empty'
                while int(self.dut.empty.value) == 1:
                    await RisingEdge(self.dut.clk_rd)

                # Drive read pulse
                self.dut.rd.value = 1
                await RisingEdge(self.dut.clk_rd)
                self.dut.rd.value = 0

            else:
                self.logger.error(f"Unknown operation in FifoItem: {item.op}")

            # Done with this item
            self.seq_item_port.item_done()
