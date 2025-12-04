# sim/uvm_env/fifo_env.py

from pyuvm import uvm_component

from .fifo_agent import FifoAgent
from .fifo_scoreboard import FifoScoreboard


class FifoEnv(uvm_component):
    """
    Environment with:
      - one FifoAgent
      - one FifoScoreboard
    """

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.agent = None
        self.scoreboard = None

    def build_phase(self):
        super().build_phase()
        self.agent = FifoAgent("agent", self)
        self.scoreboard = FifoScoreboard("scoreboard", self)

    def connect_phase(self):
        super().connect_phase()
        # Connect monitor's analysis port to scoreboard's analysis_export
        self.agent.monitor.ap.connect(self.scoreboard.analysis_export)
