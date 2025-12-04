# sim/uvm_env/fifo_item.py

from enum import Enum
from pyuvm import uvm_sequence_item


class FifoOp(Enum):
    WRITE = 0
    READ = 1


class FifoItem(uvm_sequence_item):
    """
    Transaction representing a single FIFO operation.

    op   : FifoOp.WRITE or FifoOp.READ
    data : data to write (for WRITE)
    """

    def __init__(self, name="fifo_item"):
        super().__init__(name)
        self.op = FifoOp.WRITE
        self.data = 0

    def __str__(self):
        if self.op == FifoOp.WRITE:
            return f"{self.get_name()}: WRITE data=0x{self.data:02x}"
        else:
            return f"{self.get_name()}: READ"
