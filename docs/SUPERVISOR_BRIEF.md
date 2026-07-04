# Supervisor Brief

## Working Thesis Direction

**Preventing Satellite Service Disruption: Attack Flow Modeling with SPARTA Mapping to Evaluate Ground-Segment and Command-Path Controls Using a PwnSat / FlatSat Laboratory Testbed**

This repository supports a controlled research project on satellite cybersecurity. The work does **not** target real satellites, operational spacecraft, public RF systems, or third-party ground infrastructure.

The research uses PwnSat / FlatSat as a satellite-like laboratory platform to study how command, telemetry, protocol parsing, and service-disruption risks can be modeled and reduced through defensive controls.

---

## Plain-Language Summary

The thesis investigates how satellite service disruption can occur when a spacecraft-like system accepts malformed, replayed, or unauthorized command traffic.

The PwnSat / FlatSat testbed provides a safe environment where the command path, telemetry path, packet parser, RF/USB ingress paths, and simulated subsystem behavior can be inspected end to end.

The research contribution is not simply to demonstrate attacks. The contribution is to build a repeatable method for:

1. modeling attack chains,
2. mapping them to SPARTA,
3. identifying affected trust boundaries,
4. applying defensive controls, and
5. measuring whether those controls reduce disruption risk.

---

## Why This Testbed Is Relevant

PwnSat / FlatSat compresses several spacecraft-relevant concepts into a lab board:

- command authority,
- telemetry trust,
- packet parsing,
- APID-based command dispatch,
- RF uplink and downlink behavior,
- local USB command delivery,
- sensor telemetry,
- firmware-level defensive hardening.

This makes it suitable for controlled cybersecurity experimentation without interacting with real space assets.

---

## Core Research Question

How can SPARTA-mapped Attack Flow modeling be used to evaluate defensive controls that reduce satellite service-disruption risk in a controlled PwnSat / FlatSat command-and-telemetry environment?

---

## Experimental Focus

The thesis should focus on four experiment groups:

1. **Command authority**
   - Can unauthorized command traffic reach mission-impacting handlers?

2. **Parser robustness**
   - Can malformed SPP packets trigger unsafe parser behavior?

3. **Service disruption**
   - Can valid-looking commands degrade availability, telemetry, or command responsiveness?

4. **Telemetry trust and observability**
   - Can telemetry be trusted, and can the lab observe disruption or manipulation effects?

---

## Defensive Controls to Evaluate

The main controls are:

- command authentication,
- APID authorization,
- TC/TM direction enforcement,
- packet length validation,
- anti-replay counters,
- command rate limits,
- safe-mode or maintenance-mode command policy,
- telemetry integrity,
- telemetry validity flags,
- audit telemetry for accepted and rejected commands.

---

## Expected Measurements

Possible thesis metrics include:

- command acceptance rate,
- malformed packet rejection rate,
- crash or reset occurrence,
- telemetry disruption duration,
- time to detect abnormal behavior,
- time to recover normal telemetry,
- number of commands rejected by policy,
- effect of controls on normal command processing.

---

## Scope Boundary

In scope:

- local PwnSat / FlatSat board,
- offline packet analysis,
- USB/local reproduction,
- controlled and authorized lab RF only,
- SPARTA and Attack Flow mapping,
- defensive-control evaluation.

Out of scope:

- real satellite attacks,
- unauthorized RF transmission,
- public ground-station interaction,
- operational jamming procedures,
- uncontrolled RF fuzzing,
- claims of full RF-triggered code execution without debugger evidence.

---

## Supervisor-Level Value

This research is academically useful because it converts a satellite hacking lab into a reproducible control-evaluation framework. The thesis can show how attack modeling, protocol analysis, firmware review, and defensive hardening combine to reduce service-disruption risk in spacecraft-like systems.