# Appendix A: Lab Setup and Safety

This appendix defines the safe operating assumptions for the book.

## Required Lab Boundaries

- Test only hardware you own or are authorized to assess.
- Keep RF experiments low-power, shielded, or cabled where possible.
- Do not transmit against operational spacecraft, public services, or third-party ground infrastructure.
- Verify local radio regulations before transmitting.
- Prefer USB/local reproduction before RF delivery.

## Recommended Equipment

| Equipment | Use |
| --- | --- |
| Pwnsat/FlatSat board | Target platform. |
| USB cable | Local command and debug path. |
| Logic analyzer | I2C/SPI/UART/SWD discovery. |
| Multimeter | Ground and voltage reference checks. |
| SDR receiver | Passive RF observation where legal. |
| LoRa transceiver | Controlled lab uplink/downlink experiments. |
| SWD debugger | Crash triage and firmware debugging. |
| Faraday bag or shielded setup | RF containment for transmit tests. |

## Software Environment

Useful tools:

- Python 3
- Jupyter
- `pandas`
- `rich`
- `pyserial`
- `pwntools`
- `spacepackets`
- Clang/LLVM with libFuzzer support
- Logic analyzer software
- SDR capture software
- ARM disassembly/debugging tools

The exact RF tooling is intentionally external to this manuscript. The book focuses on firmware behavior, packet construction, and defensive analysis.

## Companion Notebook Setup

The exercise notebook is [Booklet.ipynb](Booklet.ipynb). Install the notebook dependencies with:

```shell
python3 -m pip install -r requirements-booklet.txt
```

The expected public exercise layout is:

```text
.
├── Booklet.ipynb
├── Flatsat_v1_Initial_start_exported.txt
├── Flatsat_v1_Initial_start.logicdata
├── resources
│   └── fuzzing
│       ├── fuzzing
│       ├── include
│       └── src
└── scripts
    ├── i2c_parser.py
    └── spp_tools.py
```

The `.logicdata` file preserves the original capture. The exported `.txt` file lets readers parse the data even if they do not have the original logic analyzer software.

The fuzzing resources are offline harnesses for the SPP library and a deliberately vulnerable local binary. They are not RF transmit tools and should be run before any hardware-facing experiment.

## Experiment Record

For each test, record:

- Date and firmware build.
- Transport: USB, RF receive-only, or RF transmit.
- Raw packet bytes.
- Decoded SPP fields.
- Expected behavior.
- Observed behavior.
- Logs or telemetry captures.
- Safety controls used.

Good notes are part of the exploit. They turn one surprising packet into a reproducible engineering finding.
