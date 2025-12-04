# Makefile for async FIFO verification with Verilator + cocotb + pyuvm

# Simulator and DUT info
SIM              = verilator
TOPLEVEL_LANG    = verilog
TOPLEVEL         = fifo_async

# RTL sources
VERILOG_SOURCES  = ../rtl/fifo_async.v

# Default Python test module (can be overridden on the command line)
#   make MODULE=test_fifo_async_smoke
#   make MODULE=test_fifo_uvm
MODULE           ?= test_fifo_async_smoke
COCOTB_TEST_MODULES ?= $(MODULE)

# -------------------------------
# Logging / formatting controls
# -------------------------------

# Overall verbosity
export COCOTB_LOG_LEVEL     ?= INFO
export PYUVM_LOG_LEVEL      ?= INFO

# Use the reduced cocotb format (shorter prefix, closer to “simulator style”)
export COCOTB_REDUCED_LOG_FMT ?= 1

# Optional: custom log format (uncomment if you want something even closer
# to VCS/Questa; this works together with REDUCED_LOG_FMT).
# export COCOTB_LOG_FMT = "%(levelname)-7s %(name)-40s %(message)s"

# Tell Python/cocotb that the terminal is wide, so tables and lines do not wrap
# as early. Adjust 180 to 200/220 if you want even wider.
export COLUMNS ?= 180

# -------------------------------
# Pull in cocotb's generic rules
# -------------------------------
include $(shell cocotb-config --makefiles)/Makefile.sim
