#!/bin/bash

set -e

MODE=$1

if [ -z "$MODE" ]; then
    echo "Usage: ./run_sim.sh [rtl|smoke|uvm]"
    exit 1
fi

case "$MODE" in
  rtl)
    echo "[RTL] Running fifo_async_tb with Icarus Verilog"
    iverilog -o tb/fifo_async_tb.vvp tb/fifo_async_tb.v src/fifo_async.v
    vvp tb/fifo_async_tb.vvp
    ;;

  smoke)
    echo "[cocotb] Running smoke tests"
    (cd sim && make MODULE=test_fifo_async_smoke)
    ;;

  uvm)
    echo "[UVM] Running pyuvm environment"
    (cd sim && make MODULE=test_fifo_uvm COCOTB_TEST_MODULES=test_fifo_uvm)
    ;;

  *)
    echo "Invalid mode: $MODE"
    echo "Usage: ./run_sim.sh [rtl|smoke|uvm]"
    exit 1
    ;;
esac
