# PwnSat Booklet

This repository is the technical foundation for my Monash Master of Cybersecurity thesis work on PwnSat / FlatSat satellite cybersecurity.
This is from Kevin.

It contains booklet chapters, firmware source code, Python analysis scripts, protocol notes, SPARTA / Attack Flow artifacts, lab resources, and diagrams used to document and reproduce the research work.

---

## Research Direction

This repository supports thesis work related to:

- Satellite service disruption and resilience
- Ground segment and mission operations security
- Space Packet Protocol analysis
- SDR-assisted observability
- PwnSat / FlatSat experimentation
- SPARTA mapping and Attack Flow modeling
- Defensive engineering and hardening

The repository is used as both a technical lab notebook and a reproducibility artifact.

---

## Repository Structure

See [`REPO_INDEX.md`](REPO_INDEX.md) for the full repository map.

Main folders:

```text
pwnsat-booklet/
├── firmware/       # PwnSat / FlatSat firmware source and build artifacts
├── resources/      # Logic analyzer captures and exported resource files
├── scripts/        # Python tools for parsing, fuzzing, packet sending, and analysis
├── sparta/         # SPARTA / Attack Flow Builder artifacts
├── static/         # Images, diagrams, screenshots, and booklet assets
├── *.md            # Booklet chapters, appendices, and thesis notes
├── Booklet.ipynb   # Notebook-based booklet build / documentation workflow
└── requirements-booklet.txt

```
---

## Safety and Scope

All work in this repository is intended for an isolated, authorized lab environment only.

This repository must not be used against real satellites, real ground stations, public RF systems, or any system without authorization.

---

## Status

This repository is currently under active development as part of thesis preparation and PwnSat / FlatSat lab documentation.
