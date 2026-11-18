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

## Market data

Market data is not included in the repository. The project uses two full-day Nasdaq ITCH 5.0 sample files from Nasdaq's public server, [emi.nasdaq.com/ITCH/Nasdaq ITCH](https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH):

| File | Trading day | Size (compressed) | Used for |
| --- | --- | --- | --- |
| `12302019.NASDAQ_ITCH50.gz` | December 30, 2019 | 3.5 GB | Development and regression: a quiet holiday-week day, so replays are fast |
| `S121225-v50.txt.gz` | December 12, 2025 | 12.6 GB | Stress testing: recent message rates, peak bursts, and peak live orders |

Download them into `data/` (ignored by git) and read them compressed; there is no need to unzip them:

```bash
python scripts/itch_stats.py data/12302019.NASDAQ_ITCH50.gz
```

## Specifications

The design follows two Nasdaq specifications. They are not included in the repository; download them into `docs/specs/` (ignored by git):

- [Nasdaq TotalView-ITCH 5.0](https://nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHspecification.pdf): message types and field layouts
- [MoldUDP64](https://m.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/moldudp64.pdf): packet framing, sequence numbers, heartbeats, and end of session

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
