# Thesis Repository Map

This document explains how each major part of the repository supports the thesis.

It is different from `REPO_INDEX.md`. The repository index explains **where files are**. This document explains **why those files matter for the research**.

---

## Thesis Direction

The repository supports research on satellite service-disruption risk using a controlled PwnSat / FlatSat laboratory environment.

The intended thesis workflow is:

```text
PwnSat / FlatSat testbed
  -> command and telemetry path analysis
  -> vulnerability and disruption-chain identification
  -> Attack Flow modeling
  -> SPARTA mapping
  -> defensive-control evaluation
  -> measurement and thesis evidence
```

---

## Repository Areas

| Area | Repository Role | Thesis Role |
|---|---|---|
| `firmware/` | PwnSat / FlatSat firmware source and build artifacts. | Evidence for command path, parser behavior, APID dispatch, telemetry generation, and hardening opportunities. |
| `scripts/` | Python helpers for packet building, decoding, USB command delivery, fuzzing support, and I2C parsing. | Supports repeatable experiments, packet analysis, and evidence generation. |
| `sparta/` | Attack Flow Builder artifacts. | Supports SPARTA-mapped attack-chain modeling. |
| `resources/` | Logic analyzer captures and exported analysis files. | Supports reproducibility and hardware-to-telemetry evidence. |
| `static/` | Images, screenshots, diagrams, and figures. | Supports thesis figures, lab evidence, and presentation material. |
| root Markdown chapters | Booklet and methodology narrative. | Provides background, workflow, threat model, technical analysis, and defensive discussion. |
| `Booklet.ipynb` | Hands-on analysis notebook. | Supports offline analysis, repeatable packet exercises, and lab report generation. |

---

## Firmware Folder

Purpose in repository:

- Implements the PwnSat / FlatSat firmware.
- Defines radio configuration, USB command handling, packet parsing, telemetry generation, and command dispatch.

Purpose in thesis:

- Provides source-code evidence for trust-boundary analysis.
- Supports parser robustness experiments.
- Supports APID authorization experiments.
- Supports service-disruption experiments.
- Supports defensive hardening evaluation.

Key thesis files:

- `firmware/spp.h`
- `firmware/spp.cpp`
- `firmware/worker.cpp`
- `firmware/ruplink.cpp`
- `firmware/rdownlink.cpp`
- `firmware/usbCDC.cpp`
- `firmware/mission.h`
- `firmware/sensors.cpp`
- `firmware/thruster.cpp`

---

## Scripts Folder

Purpose in repository:

- Provides analysis and experiment helper scripts.

Purpose in thesis:

- Makes packet construction and decoding repeatable.
- Helps distinguish protocol bugs from transport problems.
- Supports logic-analyzer capture analysis.
- Supports controlled local fuzzing evidence.

Key thesis files:

- `scripts/spp_tools.py`
- `scripts/usb_tc_send.py`
- `scripts/i2c_parser.py`
- `scripts/fuzz_offset.py`
- `scripts/fuzz_exploit.py`

---

## SPARTA Folder

Purpose in repository:

- Stores Attack Flow Builder files for SPARTA mapping.

Purpose in thesis:

- Connects technical findings to a space-domain threat framework.
- Helps show that each lab behavior is part of a broader attack chain.
- Supports structured communication with supervisors, examiners, and readers.

---

## Resources Folder

Purpose in repository:

- Stores raw and exported lab captures.

Purpose in thesis:

- Provides reproducible evidence.
- Supports hardware discovery and telemetry correlation.
- Helps show how physical bus activity maps to mission telemetry.

---

## Static Folder

Purpose in repository:

- Stores screenshots, lab images, diagrams, and figures.

Purpose in thesis:

- Provides visual evidence for lab setup, protocol analysis, SPARTA mapping, fuzzing, and hardware reconnaissance.

---

## Root Markdown Chapters

Purpose in repository:

- Explain the learning path from spacecraft fundamentals to exploitation and defense.

Purpose in thesis:

- Provide raw material for literature/methodology framing.
- Help organize the thesis narrative.
- Support background sections on spacecraft architecture, RF trust boundaries, packet analysis, and defensive engineering.

---

## Notebook

Purpose in repository:

- Provides guided exercises for offline analysis.

Purpose in thesis:

- Can become a reproducible experiment notebook.
- Can generate tables, packet examples, and analysis outputs for the thesis.

---

## Recommended Thesis Use

Use the repository as a controlled testbed, not as a collection of unrelated hacking examples.

The correct research interpretation is:

```text
The repo provides a satellite-like command-and-telemetry environment where attack chains can be modeled, mapped to SPARTA, and used to evaluate defensive controls against service disruption.
```