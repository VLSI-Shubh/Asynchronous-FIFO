# sim/uvm_env/fifo_agent.py

from pyuvm import uvm_component, uvm_sequencer

from .fifo_item import FifoItem
from .fifo_driver import FifoDriver
from .fifo_monitor import FifoMonitor


class FifoSequencer(uvm_sequencer):
    """Sequencer for FifoItem transactions."""
    def __init__(self, name, parent):
        super().__init__(name, parent)


class FifoAgent(uvm_component):
    """
    Agent encapsulating:
      - FifoSequencer
      - FifoDriver
      - FifoMonitor
    """

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.sequencer = None
        self.driver = None
        self.monitor = None

    def build_phase(self):
        super().build_phase()
        self.sequencer = FifoSequencer("sequencer", self)
        self.driver = FifoDriver("driver", self)
        self.monitor = FifoMonitor("monitor", self)

    def connect_phase(self):
        super().connect_phase()
        # Connect sequencer to driver
        self.driver.seq_item_port.connect(self.sequencer.seq_item_export)
