# sim/uvm_env/dut_ref.py
"""
Global DUT handle for pyuvm components.

In test_fifo_uvm.py we do:
    import uvm_env.dut_ref as dut_ref
    dut_ref.set_dut(dut)

Then pyuvm components can do:
    from .dut_ref import get_dut
    self.dut = get_dut()
"""

_dut = None


def set_dut(dut_handle):
    """Store the global DUT handle."""
    global _dut
    _dut = dut_handle


def get_dut():
    """Retrieve the global DUT handle (raises if not set)."""
    if _dut is None:
        raise RuntimeError(
            "Global DUT is not set in dut_ref. "
            "Call dut_ref.set_dut(dut) in the cocotb test before running pyuvm."
        )
    return _dut
