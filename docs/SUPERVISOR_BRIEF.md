# Supervisor Brief

## Latest Thesis Direction

**Experimental Evaluation of Anti-Spoofing Controls Against Space-Link Command-Deception in a PWNSAT FlatSat and Software-Defined Radio Testbed**

Student: Reza Maliki Akbar  
Student ID: 34292020  
Supervisory team: Dr. Bayu Anggorojati and Dr. Muhammad Johan Alibasa

This document reflects the revised proposal direction. The earlier Rizka Purwanto / ground-segment-control framing is treated as superseded background, not the current thesis direction.

---

## Plain-Language Summary

The thesis studies a controlled satellite-security problem:

```text
Can a forged telecommand be made to look legitimate to a satellite-like testbed,
and which protocol-level defensive controls stop or detect it?
```

The work uses a PWNSAT FlatSat and SDR-supported lab setup to reproduce a safe, authorised space-link spoofing scenario. The experiment compares baseline behaviour against defensive controls and measures whether forged telecommands are accepted, rejected, detected, or recovered from.

The thesis is **not** about attacking real satellites, public satellite links, GNSS, or third-party ground stations.

---

## What Changed From the Previous Direction

Previous framing:

```text
SPARTA / Attack Flow modeling to evaluate broad ground-segment controls
such as segmentation, container hardening, and log governance.
```

Current refined framing:

```text
Hands-on experimental evaluation of space-link spoofing resilience
in a PWNSAT FlatSat / PlutoSDR-style testbed.
```

SPARTA and Attack Flow are still useful, but they are now the **analysis layer**, not the main contribution.

---

## Core Research Aim

Reproduce a safe, lab-contained space-link spoofing chain and evaluate how four protocol-level controls affect unauthorised telecommand acceptance, telemetry behaviour, detection, and recovery.

The four controls are:

1. cryptographic authentication,
2. command allow-listing and strict typing,
3. length and structural validation,
4. sequence-counter freshness / anti-replay.

---

## Main Research Questions

### RQ1

How can a space-link spoofing chain be safely reproduced in a PWNSAT FlatSat / SDR testbed and mapped to SPARTA and Attack Flow?

### RQ2

How effective are the four controls, individually and in combination, at reducing forged-command acceptance, chain completion, disruption duration, and recovery time?

### RQ3

How can SDR-assisted observability and OpenC3 COSMOS mission-operation logs be combined to improve evidence collection for spoofing detection and chain reconstruction?

---

## Testbed Concept

```text
Ground Station VM / OpenC3 COSMOS
  -> command generation and telemetry logging

Attacker / analysis VM
  -> SDR tools, SPP parsing, forged-frame construction, analysis

PWNSAT FlatSat
  -> satellite-like target with OBC, CCSDS SPP command path, telemetry path

SDR / link observer
  -> controlled lab link evidence and timing correlation
```

Where RF is used, it must remain cabled, attenuated, shielded, or otherwise authorised.

---

## Expected Contribution

The contribution is not a new attack technique and not a real-satellite attack tutorial.

The contribution is experimental evidence:

- a reproducible PWNSAT / SDR testbed configuration,
- a specified forged-telecommand spoofing scenario,
- a control comparison matrix,
- command/telemetry/link evidence,
- before/after results,
- SPARTA-supported interpretation,
- practical recommendations on which controls reduce spoofing-driven disruption risk.

---

## Scope Boundary

In scope:

- PWNSAT FlatSat,
- software-first OBC command pipeline emulator,
- controlled SDR-assisted observability,
- CCSDS SPP telecommand framing,
- OpenC3 COSMOS logs and telemetry,
- defensive control evaluation,
- SPARTA / Attack Flow mapping.

Out of scope:

- real satellite targets,
- public RF links,
- GNSS spoofing,
- operational jamming,
- third-party ground-station interaction,
- uncontrolled RF transmission,
- publishing complete harmful forged-command sequences for operational systems.

---

## Supervisor-Level One-Sentence Summary

This thesis evaluates how protocol-level anti-spoofing controls affect forged telecommand acceptance, detection, and recovery in a safe PWNSAT FlatSat / SDR satellite-security testbed.