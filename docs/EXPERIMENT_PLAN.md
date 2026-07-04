# Experiment Plan

This document turns the repository into a repeatable experiment plan for the latest thesis direction.

## Latest Thesis Direction

**Experimental Evaluation of Anti-Spoofing Controls Against Space-Link Command-Deception in a PWNSAT FlatSat and Software-Defined Radio Testbed**

All experiments must remain inside an isolated, authorised laboratory environment. Software-first or USB/local reproduction is preferred before any controlled SDR-backed test.

---

## Research Objective

Reproduce a controlled space-link spoofing scenario in a PWNSAT FlatSat / SDR testbed and evaluate how four protocol-level defensive controls affect unauthorised telecommand acceptance, telemetry behaviour, detection, and recovery.

The four controls are:

- C1: cryptographic authentication,
- C2: command allow-listing and strict typing,
- C3: length and structural validation,
- C4: sequence-counter freshness / anti-replay.

---

## Research Questions

| ID | Question | Expected Evidence |
|---|---|---|
| RQ1 | How can a space-link spoofing chain be safely reproduced in a PWNSAT FlatSat / SDR testbed and mapped to SPARTA and Attack Flow? | Scenario specification, testbed architecture, baseline traces, SPARTA mapping, Attack Flow diagram. |
| RQ2 | How effective are C1-C4, individually and in combination, at reducing command acceptance, chain completion, disruption duration, and recovery time? | Repeated before/after trials, metric tables, false-rejection analysis. |
| RQ3 | How can SDR-assisted observability and OpenC3 COSMOS logs improve evidence collection for spoofing detection and chain reconstruction? | Time-aligned logs, telemetry timelines, packet traces, time-to-detect and time-to-recover. |

---

## Testbed Architecture

```text
Ground Station VM / OpenC3 COSMOS
  -> command generation
  -> telemetry logging
  -> command/telemetry server evidence

Attacker / Analysis VM
  -> SPP decoding and analysis
  -> forged-frame construction for lab testing
  -> SDR/link observation where authorised

PWNSAT FlatSat / OBC emulator
  -> receiver
  -> SPP parse
  -> APID dispatch
  -> command handler
  -> telemetry/state response

SDR / link observer
  -> controlled link evidence
  -> timing correlation
```

---

## Safety Boundary

Allowed:

- software-first emulator testing,
- USB/local reproduction,
- PWNSAT / FlatSat lab testing,
- cabled, attenuated, shielded, or otherwise authorised SDR use,
- defensive control evaluation,
- SPARTA / Attack Flow documentation.

Not allowed:

- real satellite targets,
- public RF links,
- GNSS spoofing,
- operational jamming,
- third-party infrastructure,
- uncontrolled RF transmission,
- publishing operationally harmful forged-command recipes.

---

## Scenario S1: Forged-Telecommand Spoofing

### Goal

Reproduce a safe, authorised forged-telecommand chain in the lab.

### Chain

```text
1. Signal / protocol analysis
2. Command dictionary or APID inference
3. SPP frame forgery
4. Signal or transport impersonation in controlled lab path
5. Command injection into OBC command pipeline
6. Unauthorised command execution attempt
7. Safe analogue mission impact or rejection event
```

### SPARTA Support

Candidate mapping:

- REC-0002 Signal Analysis,
- RE-0001 Reverse Engineering,
- EX-0007 Signal Impersonation,
- EX-0002 Command Injection,
- EX-0001 Unauthorised Command Execution,
- IMP-0005 Denial of Service or safe analogue disruption impact.

---

## Scenario S2: Sequence-Aware Spoof Variant

### Goal

Evaluate whether freshness checking changes the result when an attacker reuses, guesses, or manipulates sequence values.

### Additional Variable

- SPP Sequence Count behaviour.

### Main Control Tested

- C4 sequence-counter freshness / anti-replay.

---

## Control Matrix

Run the same scenario under these configurations:

| Configuration | Controls Enabled |
|---|---|
| Baseline | none |
| C1 | authentication only |
| C2 | allow-list / strict typing only |
| C3 | length / structural validation only |
| C4 | sequence freshness only |
| C1+C2 | authentication + allow-list |
| C1+C3 | authentication + length validation |
| C1+C4 | authentication + freshness |
| C2+C3 | allow-list + length validation |
| C2+C4 | allow-list + freshness |
| C3+C4 | length validation + freshness |
| C1+C2+C3+C4 | full control set |

Target: at least `N >= 30` repeated trials per configuration where feasible.

---

## Operational Definitions

### Forged Command Accepted

A forged command is accepted when it reaches the command handler and produces an expected safe effect, acknowledgement, state change, or telemetry event.

### Chain Completion

The chain completes when the forged command reaches the defined safe impact condition.

### Service Disruption / Safe Analogue Impact

A safe analogue impact may include:

- unauthorised state change,
- telemetry deviation,
- command acknowledgement inconsistency,
- command-path delay,
- safe-mode-like state transition in emulator/testbed,
- operator-visible anomaly.

---

## Primary Metrics

| Metric | Definition |
|---|---|
| Chain completion rate | Percentage of trials reaching the defined impact condition. |
| Command acceptance rate | Percentage of forged telecommands accepted for execution. |
| Command rejection rate | Percentage of forged telecommands rejected by a control. |
| Disruption duration | Time service remains below the defined threshold. |
| Time-to-detect | Time from first observable deviation to detection event. |
| Time-to-recover | Time from detection to restored baseline state. |
| False-rejection rate | Percentage of legitimate commands incorrectly rejected. |
| Operational overhead | Added latency, CPU/memory overhead, operator steps, alert burden. |

---

## Evidence Streams

Capture and time-align:

- COSMOS command logs,
- COSMOS telemetry logs,
- raw and decoded SPP packets,
- FlatSat/OBC emulator state changes,
- SDR/link observation where authorised,
- operator workflow timestamps,
- control rejection reasons.

---

## Procedure

1. Establish baseline valid-command behaviour.
2. Establish baseline forged-command behaviour in software-first mode.
3. Record baseline command acceptance/rejection and telemetry response.
4. Enable one control at a time and repeat the scenario.
5. Enable pairwise control combinations and repeat.
6. Enable full C1+C2+C3+C4 configuration and repeat.
7. Confirm key results on FlatSat hardware where feasible.
8. Correlate COSMOS logs, packet traces, telemetry, and SDR observations.
9. Map interrupted chain steps to SPARTA and Attack Flow.
10. Report results with central tendency, worst-case behaviour, and threats to validity.

---

## Analysis

For each configuration, report:

- mean command acceptance rate,
- confidence interval where possible,
- worst-case acceptance/disruption result,
- false-rejection rate,
- overhead,
- which chain step was interrupted,
- whether the result was seen in software-only, hardware-backed, or both.

---

## Final Thesis Artefacts

- testbed architecture diagram,
- spoofing scenario specification,
- control insertion-point diagram,
- experiment matrix,
- results tables,
- SPARTA mapping table,
- Attack Flow diagram,
- evidence log pack,
- threats-to-validity section,
- practical defensive recommendations.