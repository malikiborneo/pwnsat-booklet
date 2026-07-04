# Thesis Repository Map

This document explains how each major part of the repository supports the latest thesis direction.

It is different from `REPO_INDEX.md`. The repository index explains **where files are**. This document explains **why those files matter for the research**.

---

## Latest Thesis Direction

**Experimental Evaluation of Anti-Spoofing Controls Against Space-Link Command-Deception in a PWNSAT FlatSat and Software-Defined Radio Testbed**

The repository now supports this workflow:

```text
PWNSAT / FlatSat testbed
  -> CCSDS SPP telecommand path analysis
  -> controlled forged-telecommand spoofing scenario
  -> anti-spoofing defensive controls
  -> repeated measurement
  -> SPARTA / Attack Flow interpretation
  -> thesis evidence
```

The older ground-segment-control framing remains useful context, but the current contribution is narrower: protocol-level spoofing resilience in a PWNSAT FlatSat / SDR lab.

---

## Repository Areas

| Area | Repository Role | Thesis Role |
|---|---|---|
| `firmware/` | PWNSAT / FlatSat firmware source and build artifacts. | Evidence for OBC command pipeline, SPP parser, APID dispatch, command handlers, telemetry behaviour, and control insertion points. |
| `scripts/` | Python helpers for packet building, decoding, USB delivery, fuzzing support, and I2C parsing. | Supports reproducible SPP packet analysis, command construction, offline testing, and evidence generation. |
| `sparta/` | Attack Flow Builder artifacts. | Supports SPARTA/Attack Flow interpretation of the spoofing chain and defensive breakpoints. |
| `resources/` | Logic analyzer captures and exported data. | Supports lab reproducibility and sensor/telemetry context. |
| `static/` | Images, screenshots, diagrams, and figures. | Supports thesis figures, lab setup explanation, packet analysis, and SPARTA diagrams. |
| root Markdown chapters | Booklet and methodology narrative. | Provides background on space fundamentals, protocol analysis, RF attack surface, exploitation, reliability, and hardening. |
| `Booklet.ipynb` | Hands-on analysis notebook. | Can become a reproducible analysis notebook for SPP decoding, packet comparison, and experiment evidence. |

---

## How Each Folder Supports the Revised Thesis

### `firmware/`

Main thesis use:

- understand the Receiver -> SPP Header Parse -> APID Dispatch -> Command Handler path,
- identify where anti-spoofing controls should be inserted,
- compare baseline acceptance against protected behaviour,
- observe telemetry and state changes after command attempts.

Most relevant files:

- `spp.h` / `spp.cpp` for packet parsing and length handling,
- `mission.h` for APID definitions,
- `worker.cpp` for command dispatch and handlers,
- `ruplink.cpp` / `rdownlink.cpp` for link-facing behaviour,
- `usbCDC.cpp` for local reproducible command delivery,
- `sensors.cpp` and `thruster.cpp` for telemetry/state effects.

### `scripts/`

Main thesis use:

- build and decode SPP packets,
- compare raw SPP, USB-framed, and RF-ready representations,
- generate safe lab inputs,
- parse evidence files.

Most relevant files:

- `spp_tools.py`,
- `usb_tc_send.py`,
- `i2c_parser.py`,
- `fuzz_offset.py`,
- `fuzz_exploit.py`.

### `sparta/`

Main thesis use:

- represent the spoofing chain as Attack Flow,
- map steps to SPARTA techniques,
- document where each defensive control interrupts the chain.

### `resources/`

Main thesis use:

- store raw captures,
- preserve reproducibility evidence,
- support lab traceability.

### `static/`

Main thesis use:

- diagrams for FlatSat architecture,
- screenshots from Black Hat Asia/PWNSAT workflow,
- SPARTA visuals,
- protocol and hardware figures.

---

## Current Research Interpretation

Use the repository as a controlled satellite-like security testbed.

The correct research interpretation is:

```text
The repo provides a PWNSAT/FlatSat command-and-telemetry environment where a safe forged-telecommand spoofing scenario can be reproduced and anti-spoofing controls can be evaluated with repeatable metrics.
```

---

## Do Not Overstate

The repo does not prove real-satellite exploitability.

It supports:

- lab-based spoofing-resilience evaluation,
- protocol-level defensive control testing,
- FlatSat reproducibility,
- SPARTA-supported analysis,
- thesis evidence collection.

It does not support:

- attacks against operational satellites,
- uncontrolled RF transmission,
- broad claims about all spacecraft,
- full operational key-management conclusions,
- real-world jamming or GNSS spoofing claims.