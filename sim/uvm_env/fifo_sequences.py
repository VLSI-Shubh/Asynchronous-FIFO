# sim/uvm_env/fifo_sequences.py

from pyuvm import uvm_sequence

from .fifo_item import FifoItem, FifoOp


class FifoBasicSequence(uvm_sequence):
    """
    Basic sequence:
      - Write a fixed list of values
      - Then read back the same number of items
    """

    def __init__(self, name="fifo_basic_seq"):
        super().__init__(name)

    async def body(self):
        values_to_write = [0x11, 0x22, 0x33, 0x44]

        # Writes
        for val in values_to_write:
            item = FifoItem("write_item")
            item.op = FifoOp.WRITE
            item.data = val

            await self.start_item(item)
            await self.finish_item(item)

        # Reads
        for _ in values_to_write:
            item = FifoItem("read_item")
            item.op = FifoOp.READ

            await self.start_item(item)
            await self.finish_item(item)
