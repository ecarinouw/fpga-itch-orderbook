# fpga-itch-orderbook

An FPGA tick-to-trade pipeline in SystemVerilog. It takes Nasdaq ITCH 5.0 market data off a 10G Ethernet stream, maintains an order book in hardware, and emits an order when a configurable trigger condition is met.

> **Status: in progress.** The repository is being built in stages (see [Roadmap](#roadmap)). Results below are filled in only once they've been measured; empty cells mean not yet done.

## Overview

```
 10G Ethernet ──▶ Eth/IP/UDP ──▶ MoldUDP64 ──▶ ITCH 5.0 ──▶ Order ──▶ Trigger ──▶ Risk ──▶ Order
 frame stream     filter         sequencing    parser       book      logic       checks    message
```

- **Input:** 64-bit Ethernet frame stream at 156.25 MHz (10G line rate). Valid-only, no backpressure: the wire does not wait.
- **Parser:** decodes MoldUDP64 packets and splits ITCH messages, including messages that end and begin in the same bus word.
- **Order book:** hashed order table in BRAM, price levels per symbol and side, and best bid and offer tracking with a fixed, documented update latency.
- **Trigger and order path:** a simple runtime-configurable rule, pre-trade risk checks, a kill switch, and an OUCH-format order message.

The trigger rule is a placeholder for a strategy. The point of the project is the latency path around it, not the rule itself.

## Results

All latencies are post-route, on the part listed. Cycle counts are at the stated clock.

| Metric | Value |
| --- | --- |
| Target part | |
| Clock / Fmax | |
| Parser latency (cycles) | |
| Worst-case book update latency (cycles) | |
| Tick-to-trade latency (cycles / ns) | |
| Wire-to-wire latency, min / median / max (ns, measured on hardware) | |
| Resources (LUTs / FFs / BRAMs) | |
| Messages replayed with zero mismatches | |

## Design notes

Longer write-ups go in [`docs/`](docs/):

- `docs/order-book.md`: table structure, collision policy, hazard forwarding, worst-case latency
- `docs/order-table-comparison.md`: two hash-table designs compared on the same real data
- `docs/latency-measurement.md`: how latency is measured, including sub-cycle timestamping on hardware

## Verification

Every RTL block is checked against a Python reference model.

- **Framework:** cocotb tests run on Verilator, driven by pytest, in GitHub Actions CI.
- **Real data:** a full trading day of Nasdaq ITCH 5.0 sample data is wrapped into Ethernet/IP/UDP/MoldUDP64 frames and replayed through the RTL. The scoreboard compares every output event with the reference model.
- **Directed and stress tests:** back-to-back minimum-size messages at line rate, same-order and same-price-level hazards, malformed and truncated packets, and sequence gaps.

## Repository layout

```
rtl/        SystemVerilog source
tb/         cocotb testbenches and scoreboards
model/      Python reference model (parser, book, trigger)
scripts/    data decoding, frame generation, analysis
constr/     timing and placement constraints
docs/       design notes and write-ups
```

## Getting started

Requirements: Python 3.10+, Verilator, cocotb, pytest. Vivado for synthesis and implementation.

```bash
pip install -r requirements.txt
pytest tb/
```

Market data is not included. Download a Nasdaq ITCH 5.0 sample file and point the scripts at it:

```bash
python scripts/itch_stats.py path/to/sample.NASDAQ_ITCH50.gz
```

## Roadmap

- [ ] **Stage 0:** toolchain, CI, data decoding
- [ ] **Stage 1:** framing, parser, and order book in simulation; timing closed post-route
- [ ] **Stage 1e:** comparison of two order-table designs
- [ ] **Stage 2:** trigger, risk checks, and order generation; tick-to-trade in simulation
- [ ] **Stage 3:** 10G board bring-up and measured wire-to-wire latency, with sub-cycle timestamping

## Acknowledgments

Third-party IP used in this project (for example the 10G MAC/PCS) is credited here with its license once added.

## License

MIT
