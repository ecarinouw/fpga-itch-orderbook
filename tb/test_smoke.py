"""Smoke test: one registered stage passes data through with one cycle of latency."""
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.runner import get_runner
from cocotb.triggers import ReadOnly, RisingEdge

ROOT = Path(__file__).resolve().parent.parent


@cocotb.test()
async def passes_data_with_one_cycle_latency(dut):
    cocotb.start_soon(Clock(dut.clk, 6.4, units="ns").start())  # 156.25 MHz
    dut.rst.value = 1
    dut.d.value = 0
    await RisingEdge(dut.clk)
    dut.rst.value = 0

    dut.d.value = 0x0123_4567_89AB_CDEF
    await RisingEdge(dut.clk)
    await ReadOnly()
    assert dut.q.value == 0x0123_4567_89AB_CDEF


def test_smoke():
    runner = get_runner("verilator")
    runner.build(
        sources=[ROOT / "rtl" / "smoke.sv"],
        hdl_toplevel="smoke",
        build_dir=ROOT / "sim_build" / "smoke",
        always=True,
    )
    runner.test(
        hdl_toplevel="smoke",
        test_module="test_smoke",
        test_dir=Path(__file__).resolve().parent,
    )
