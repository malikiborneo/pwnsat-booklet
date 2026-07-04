# Technical Audit

This document records technical findings from the PwnSat / FlatSat firmware, scripts, and supporting materials.

The purpose is to preserve thesis evidence in a structured way. Findings should be validated only in an isolated, authorized laboratory environment.

---

## Scope

In scope:

- PwnSat / FlatSat firmware source review,
- USB and RF command ingress paths,
- SPP packet parsing,
- APID command dispatch,
- telemetry generation,
- helper scripts,
- offline fuzzing and local reproduction.

Out of scope:

- real satellites,
- public RF systems,
- third-party ground stations,
- unauthorized transmission,
- operational jamming procedures.

---

## System Summary

The command path can be summarized as:

```text
USB CDC framed input
  -> commandHandler()
  -> spp_unpack_packet()
  -> commandApidHandler()

RF uplink input
  -> uplink receive path
  -> commandHandler()
  -> spp_unpack_packet()
  -> commandApidHandler()
```

The two practical ingress paths converge at the same parser and APID dispatcher. This makes the parser and dispatcher critical trust boundaries.

---

## Finding Summary

| ID | Finding | Class | Thesis Relevance |
|---|---|---|---|
| AUDIT-001 | Unauthenticated command execution path | Missing authentication / authorization | Command authority and rogue ground-station modeling |
| AUDIT-002 | Cleartext telemetry downlink | Missing confidentiality / integrity | Telemetry trust and observability |
| AUDIT-003 | SPP parser length validation weakness | Parser robustness / memory safety | Malformed packet and service-disruption testing |
| AUDIT-004 | Broadcast APID underflow candidate | Handler-level memory corruption | Exploit reliability and defensive hardening |
| AUDIT-005 | Reset command denial of service | Command abuse | Service-disruption modeling |
| AUDIT-006 | Beacon-rate abuse | Logic flaw / traffic flood | Service-degradation experiment |
| AUDIT-007 | Flash-transfer blocking behavior | Command abuse / exfiltration | Telemetry disruption and data exposure |
| AUDIT-008 | Thruster state manipulation | Unauthorized state change | Mission-impact modeling |
| AUDIT-009 | USB frame boundary issue | Local framing DoS | Transport robustness |
| AUDIT-010 | Sensor telemetry trust issue | Internal bus / telemetry trust | I2C-to-telemetry correlation |

---

## AUDIT-001: Unauthenticated Command Execution Path

### Description

The firmware command path accepts command-like traffic from USB and RF before dispatching by APID. No command authentication, sender authorization, anti-replay, or per-APID policy is enforced before command execution.

### Impact

A compatible lab command source can attempt to invoke state-changing handlers such as reset, beacon rate, thruster state, broadcast, and flash transfer.

### Thesis Use

This supports experiments on command authority and defensive controls such as authentication, APID policy, anti-replay, and rate limiting.

### Candidate Controls

- command authentication,
- APID authorization,
- TC/TM direction enforcement,
- anti-replay counter,
- accepted/rejected command telemetry.

---

## AUDIT-002: Cleartext Telemetry Downlink

### Description

Telemetry is built into plaintext SPP packets and transmitted over the downlink path.

### Impact

A compatible receiver in an authorized lab setup can observe telemetry, packet timing, APIDs, and state changes.

### Thesis Use

This supports telemetry trust, observability, and downlink confidentiality discussion.

### Candidate Controls

- telemetry integrity protection,
- authenticated encryption where appropriate,
- sequence counters,
- anomaly flags,
- operator-visible command audit telemetry.

---

## AUDIT-003: SPP Parser Length Validation Weakness

### Description

The SPP parser uses the declared length field when copying packet data. The parser should verify that the received buffer length is sufficient for the declared data size before copying.

### Impact

Malformed or truncated packets may cause out-of-bounds reads, unstable handler behavior, or crash-like behavior in local fuzzing and lab reproduction.

### Thesis Use

This is the strongest parser-hardening finding. It supports experiments comparing baseline parsing with strict length validation.

### Candidate Controls

- validate `buffer != NULL`,
- validate `space_packet != NULL`,
- validate `buffer_len >= SPP_PRIMARY_HEADER_LEN`,
- compute `data_field_size = header.length + 1`,
- require `data_field_size <= SPP_MAX_PAYLOAD_CHUNK`,
- require `buffer_len == SPP_PRIMARY_HEADER_LEN + data_field_size`, or explicitly document trailing-byte handling.

---

## AUDIT-004: Broadcast APID Underflow Candidate

### Description

The broadcast handler expects a two-byte frequency field, then computes message length from the declared payload size. If the declared payload size is shorter than required, subtracting two from the payload length can underflow.

### Impact

This is a memory-corruption candidate and should be treated carefully. A full code-execution claim should only be made if debugger evidence proves control of execution.

### Thesis Use

This supports exploit-reliability analysis and safe claim levels.

### Candidate Controls

- require minimum payload length before reading fields,
- require `payload_total >= 2`,
- require `msg_len <= sizeof(buffer_msg)`,
- return structured error telemetry for malformed commands.

---

## AUDIT-005: Reset Command Denial of Service

### Description

The reset APID can trigger a watchdog reset without authentication, confirmation, mode check, or rate limit.

### Impact

Repeated reset commands can degrade availability and prevent stable telemetry or command processing.

### Thesis Use

This is a simple and reliable service-disruption scenario.

### Candidate Controls

- authentication,
- reset cooldown,
- mode restriction,
- command confirmation,
- lockout after repeated reset attempts.

---

## AUDIT-006: Beacon-Rate Abuse

### Description

The beacon-rate APID accepts low interval values, including values that may cause excessive beacon transmission.

### Impact

Beacon flooding can increase traffic and interfere with normal telemetry scheduling.

### Thesis Use

This supports service-degradation experiments with measurable telemetry timing impact.

### Candidate Controls

- minimum interval,
- maximum interval,
- change-rate limit,
- command authorization,
- safe default behavior.

---

## AUDIT-007: Flash-Transfer Blocking Behavior

### Description

The flash-transfer command sends a chunked static blob and blocks normal telemetry while transfer is active.

### Impact

Repeated transfer requests can degrade telemetry availability and expose embedded data.

### Thesis Use

This connects command injection to telemetry disruption and exfiltration-like behavior.

### Candidate Controls

- transfer quota,
- authenticated transfer mode,
- non-blocking transfer state machine,
- telemetry priority preservation,
- rate limiting.

---

## AUDIT-008: Thruster State Manipulation

### Description

The thruster APID changes simulated actuator state using command payload bytes.

### Impact

A command source can alter mission-visible state reflected in telemetry.

### Thesis Use

This is useful for demonstrating mission-impact semantics without physical actuator risk.

### Candidate Controls

- authentication,
- mode gate,
- allowed range checks,
- command audit telemetry,
- safe-state fallback.

---

## AUDIT-009: USB Frame Boundary Issue

### Description

The USB command path accepts framed packets with a two-byte length field. Boundary cases near the maximum frame size should be rejected cleanly and should not stall parser synchronization.

### Impact

Malformed local USB frames may degrade local command handling or force resynchronization.

### Thesis Use

This helps distinguish transport robustness from command/parser vulnerability.

### Candidate Controls

- reject frames where `HEADER_SIZE + len > sizeof(rx_buffer)`,
- add frame timeout,
- add resynchronization policy,
- add per-source rate limiting.

---

## AUDIT-010: Sensor Telemetry Trust Issue

### Description

Sensor readings are placed into telemetry, but status and plausibility are not strongly represented in telemetry output.

### Impact

Manipulated or failed sensor data may be trusted by operators unless telemetry carries validity and anomaly information.

### Thesis Use

This supports telemetry trust and I2C-to-telemetry correlation experiments.

### Candidate Controls

- sensor validity flags,
- range checks,
- jump detection,
- redundant measurements,
- integrity protection,
- command/event audit telemetry.

---

## Claim-Level Guidance

Use careful wording:

| Claim | Required Evidence |
|---|---|
| Command accepted | Logs, ACK, telemetry response, or state change. |
| Service disruption | Reproducible reset, lockup, telemetry loss, or timing degradation. |
| Memory corruption | Crash, sanitizer finding, fault log, or invalid memory access evidence. |
| Control-flow influence | Controlled fault address, saved register corruption, or debugger evidence. |
| Code execution | Controlled execution of chosen code path in target context. |

---

## Next Evidence to Collect

- USB PING baseline.
- USB and RF telemetry baseline.
- RESET service-disruption record.
- BEACON_RATE timing impact record.
- FLASH transfer timing record.
- APID `0x06` malformed packet crash or non-crash record.
- I2C capture to telemetry correlation.
- Baseline vs hardened-firmware comparison.