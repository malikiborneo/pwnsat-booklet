# PwnSat Booklet Repository Index

Repository: `malikiborneo/pwnsat-booklet`  
Default branch: `main`  
Purpose: Thesis foundation repository for PwnSat / FlatSat satellite cybersecurity research.

---

## 1. Repository Purpose

This repository supports my Monash Master of Cybersecurity thesis work on satellite cybersecurity using a PwnSat / FlatSat-style lab environment.

The repository contains booklet chapters, firmware source code, Python analysis scripts, protocol notes, SPARTA / Attack Flow artifacts, and lab images used to document and reproduce satellite security analysis.

The main research direction is connected to:

- Satellite service disruption and resilience
- Ground segment and mission operations security
- Space Packet Protocol analysis
- SDR-assisted observability
- PwnSat / FlatSat experimentation
- SPARTA mapping and Attack Flow modeling
- Defensive engineering and hardening

This repo is used as both a technical lab notebook and a reproducibility artifact for the thesis.

---

## 2. Safety and Scope Boundary

All work in this repository is intended for an isolated, authorized lab environment only.

The experiments are focused on:

- Understanding satellite communication and mission system behavior
- Analyzing firmware and protocol logic
- Mapping attack paths to SPARTA techniques
- Testing defensive controls and observability methods
- Improving resilience and reproducibility

This repository must not be used against real satellites, real ground stations, public RF systems, or any system without authorization.

---

## 3. Top-Level Repository Structure

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
