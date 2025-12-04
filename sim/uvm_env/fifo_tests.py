# sim/uvm_env/fifo_tests.py

import pyuvm
from pyuvm import uvm_test

from .fifo_env import FifoEnv
from .fifo_sequences import FifoBasicSequence


class FifoBasicTest(uvm_test):
    """
    UVM-style test:
      - builds FifoEnv
      - runs FifoBasicSequence on the agent's sequencer
    """

    def __init__(self, name="fifo_basic_test", parent=None):
        super().__init__(name, parent)
        self.env = None

    def build_phase(self):
        super().build_phase()
        self.env = FifoEnv("env", self)

    async def run_phase(self):
        self.raise_objection()
        seq = FifoBasicSequence("basic_seq")
        await seq.start(self.env.agent.sequencer)
        self.drop_objection()
