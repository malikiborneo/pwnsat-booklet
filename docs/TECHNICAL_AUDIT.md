# Technical Audit

This document records technical findings from the PWNSAT / FlatSat firmware, scripts, and supporting materials.

The audit now supports the revised thesis direction:

```text
Experimental Evaluation of Anti-Spoofing Controls Against Space-Link Command-Deception in a PWNSAT FlatSat and Software-Defined Radio Testbed
```

Findings should be validated only in an isolated, authorised laboratory environment.

---

## Scope

In scope:

- PWNSAT / FlatSat firmware source review,
- CCSDS SPP packet parsing,
- APID dispatch,
- command-handler behaviour,
- telemetry response behaviour,
- USB/local reproduction,
- controlled SDR-assisted observability,
- spoofing-resilience control insertion points.

Out of scope:

- real satellites,
- public RF systems,
- third-party ground stations,
- unauthorised transmission,
- operational jamming,
- GNSS spoofing,
- harmful real-world forged-command instructions.

---

## Revised System Summary

The command acceptance path can be simplified as:

```text
Receiver / local input
  -> frame handling
  -> SPP header parse
  -> APID dispatch
  -> command handler
  -> subsystem state or telemetry response
```

This is the path where the revised thesis evaluates anti-spoofing controls.

---

## Main Control Insertion Points

| Pipeline Stage | Relevant Control |
|---|---|
| Before SPP header parse | Cryptographic authentication / HMAC verification |
| During SPP header parse | Length and structural validation |
| Between parse and dispatch | Sequence-counter freshness / anti-replay |
| Before command handler | Command allow-listing and strict typing |

---

## Finding Summary

| ID | Finding | Class | Thesis Relevance |
|---|---|---|---|
| AUDIT-001 | Command path accepts well-formed SPP/APID traffic before strong source validation | Command authority / spoofing risk | Baseline spoofing susceptibility |
| AUDIT-002 | SPP parser length validation weakness | Parser robustness / structural validation | C3 length-control evaluation |
| AUDIT-003 | APID dispatch exposes mission-impacting handlers | Command authorization | C2 allow-list and strict typing evaluation |
| AUDIT-004 | Sequence fields exist but freshness enforcement is not central in baseline command path | Replay/spoofing resilience | C4 sequence freshness evaluation |
| AUDIT-005 | Reset, beacon, flash, broadcast, and thruster handlers can create visible state/service effects | Mission impact | Safe analogue disruption metrics |
| AUDIT-006 | Telemetry is useful as evidence of command acceptance and state change | Observability | RQ3 log/telemetry correlation |
| AUDIT-007 | USB/local command path enables safe reproduction before RF-backed trials | Reproducibility | Software-first and USB-first methodology |
| AUDIT-008 | SDR/link evidence can complement COSMOS and firmware logs | Measurement fidelity | Time-aligned detection/recovery evidence |

---

## AUDIT-001: Well-Formed Command Traffic Can Reach the Command Path

### Description

The firmware exposes command-like processing through SPP/APID packet handling. In the baseline system, the key question is whether a packet that is syntactically correct is treated as legitimate.

### Thesis Use

This is the baseline condition for the forged-telecommand spoofing experiment.

### Control Relationship

- C1 cryptographic authentication should stop unauthorised packets before parse/dispatch.
- C2 allow-listing should stop unauthorised APID/command combinations before handler execution.

### Metrics

- forged-command acceptance rate,
- chain completion rate,
- false rejection rate for legitimate commands.

---

## AUDIT-002: SPP Parser Length Validation Weakness

### Description

The SPP parser uses packet length fields to determine how much data is copied and interpreted. Any mismatch between declared length and actual packet size is security-relevant.

### Thesis Use

This finding supports the length and structural validation control.

### Control Relationship

C3 should enforce:

```text
buffer != NULL
space_packet != NULL
buffer_len >= SPP_PRIMARY_HEADER_LEN
data_field_size = header.length + 1
data_field_size <= SPP_MAX_PAYLOAD_CHUNK
buffer_len == SPP_PRIMARY_HEADER_LEN + data_field_size
```

### Metrics

- malformed packet rejection rate,
- unexpected handler reachability,
- valid packet false rejection rate.

---

## AUDIT-003: APID Dispatch Is a Command-Authority Boundary

### Description

APID dispatch determines which handler receives a packet. A forged packet with the correct packet type and APID can potentially reach a mission-impacting handler unless command identity and type are checked.

### Thesis Use

This is the main reason command allow-listing and strict typing are included as a control.

### Control Relationship

C2 should enforce a manifest of valid tuples:

```text
APID + Packet Type + Command ID + Expected Length + Required Mode
```

### Metrics

- invalid APID rejection rate,
- wrong Packet Type rejection rate,
- unauthorized command rejection rate,
- valid command acceptance rate.

---

## AUDIT-004: Sequence Freshness Is a Required Anti-Spoofing Layer

### Description

The SPP header contains sequence information, but sequence fields only provide protection if the receiver enforces freshness and rejects stale or duplicate values.

### Thesis Use

This supports Scenario S2, the sequence-aware spoofing variant.

### Control Relationship

C4 should implement per-APID freshness logic:

```text
reject duplicate sequence count
reject backwards sequence count
apply sliding acceptance window
record rejection reason
```

### Metrics

- replayed/duplicate command rejection rate,
- false rejection rate under acceptable packet loss,
- command acceptance rate after sequence enforcement.

---

## AUDIT-005: Command Handlers Create Measurable Safe-Analogue Impact

### Description

Handlers such as reset, beacon-rate change, flash-transfer, broadcast, or thruster-state changes can produce visible state, telemetry, timing, or service-continuity effects.

### Thesis Use

These effects provide measurable lab-safe outcomes for spoofing-driven disruption.

### Safe Measurement Options

- telemetry deviation,
- command ACK / no ACK,
- state variable changed / unchanged,
- recovery time,
- command-path delay,
- operator-visible log event.

### Control Relationship

All controls should reduce unauthorised handler execution.

---

## AUDIT-006: Telemetry Is Evidence, Not Just Output

### Description

Telemetry can show whether a command changed state, whether service continuity was affected, and whether recovery occurred.

### Thesis Use

Telemetry supports RQ3: combining COSMOS logs and SDR/link observations for detection and chain reconstruction.

### Metrics

- telemetry deviation timeline,
- time-to-detect,
- time-to-recover,
- command acceptance/rejection visibility.

---

## AUDIT-007: USB/Software-First Path Supports Safe Reproducibility

### Description

Before using any RF-backed setup, the command path can be exercised locally through software-first or USB-first testing.

### Thesis Use

This protects the timeline and safety posture. The thesis can produce results even if hardware integration is delayed.

### Metrics

- software-first result,
- hardware-backed confirmation result,
- consistency between emulator and FlatSat behaviour.

---

## AUDIT-008: SDR-Assisted Observability Improves Measurement Fidelity

### Description

SDR evidence can help correlate link events with COSMOS logs and telemetry changes. It is not the whole thesis; it is an evidence stream.

### Thesis Use

Supports RQ3 and improves confidence in timing and chain reconstruction.

### Metrics

- event alignment accuracy,
- time-to-detect,
- correlation between link evidence and mission logs.

---

## Claim-Level Guidance

| Claim | Evidence Required |
|---|---|
| Baseline command accepted | Logs, ACK, telemetry response, or state change. |
| Spoofing chain completed | Forged command reaches target handler and produces defined safe effect. |
| Control prevented spoofing | Same command rejected under control-enabled condition. |
| Detection improved | Logs/telemetry/SDR show reduced time-to-detect. |
| Recovery improved | Baseline state restored faster or more consistently. |
| Memory corruption | Crash, sanitizer finding, debugger evidence, or invalid memory access evidence. |

---

## Next Evidence to Collect

- baseline valid PING / status command,
- baseline forged-command acceptance/rejection record,
- C1 HMAC acceptance/rejection result,
- C2 allow-list rejection result,
- C3 length validation rejection result,
- C4 sequence freshness rejection result,
- combined-control matrix result,
- time-aligned COSMOS / telemetry / SDR evidence,
- safe threats-to-validity notes.