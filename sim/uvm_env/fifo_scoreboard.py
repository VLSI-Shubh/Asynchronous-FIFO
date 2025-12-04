# sim/uvm_env/fifo_scoreboard.py

from pyuvm import uvm_subscriber
from .fifo_item import FifoOp


class FifoScoreboard(uvm_subscriber):
    """
    Simple reference FIFO model using a Python list.

    In pyuvm 4.x we extend uvm_subscriber, which provides:
      - analysis_export
      - automatic hookup to uvm_analysis_port
    The monitor connects its analysis_port to this analysis_export.
    """

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.ref_model = []  # Python list as reference FIFO

    def write(self, event):
        """Called whenever the monitor sends an event into analysis_export."""
        op = event["op"]
        data = event["data"]

        if op == FifoOp.WRITE:
            self.ref_model.append(data)
            self.logger.info(f"SB: WRITE {hex(data)} (queue={self.ref_model})")

        elif op == FifoOp.READ:
            if not self.ref_model:
                self.logger.error("SB: READ but reference FIFO is empty!")
                return

            expected = self.ref_model.pop(0)

            if expected != data:
                self.logger.error(
                    f"SB MISMATCH: expected {hex(expected)}, got {hex(data)}"
                )
            else:
                self.logger.info(
                    f"SB MATCH: {hex(data)} (remaining queue={self.ref_model})"
                )

        else:
            self.logger.error("SB: Unknown operation type")

    def report_phase(self):
        if self.ref_model:
            self.logger.warning(
                f"SB: Test ended with leftover items: {self.ref_model}"
            )
        else:
            self.logger.info("SB: FIFO empty at end of test")
