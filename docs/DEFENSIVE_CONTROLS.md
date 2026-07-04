# Defensive Controls

This document defines the defensive controls to evaluate in the PwnSat / FlatSat thesis experiments.

The purpose is to convert offensive findings into measurable engineering improvements.

---

## Control Evaluation Model

Each control should be evaluated using the same structure:

```text
baseline weakness
  -> proposed control
  -> implementation or simulation
  -> repeated test
  -> measured result
  -> thesis interpretation
```

---

## Control Summary

| Control ID | Control | Primary Risk Reduced |
|---|---|---|
| CTRL-001 | Command authentication | Unauthorized telecommand execution |
| CTRL-002 | APID authorization | High-impact command misuse |
| CTRL-003 | TC/TM direction enforcement | Confused command/telemetry semantics |
| CTRL-004 | Packet length validation | Parser instability and memory-safety bugs |
| CTRL-005 | Anti-replay counters | Reuse of captured valid commands |
| CTRL-006 | Command rate limits | Reset loops, beacon floods, and transfer abuse |
| CTRL-007 | Safe-mode or maintenance-mode policy | Dangerous commands in unsafe states |
| CTRL-008 | Telemetry integrity | Forged or corrupted telemetry |
| CTRL-009 | Telemetry validity flags | Sensor failure or spoofing invisibility |
| CTRL-010 | Command audit telemetry | Poor operator observability |

---

## CTRL-001: Command Authentication

### Purpose

Verify that the command sender is authorized before command dispatch.

### Applies To

- RESETC,
- SET_THRUSTER,
- SET_BEACON_RATE,
- BROADCAST_MSG,
- FLASH,
- any high-impact APID.

### Evaluation Metric

- unauthorized command rejection rate,
- valid command acceptance rate,
- authentication failure telemetry visibility.

---

## CTRL-002: APID Authorization

### Purpose

Prevent all valid packets from reaching all handlers by default.

### Design Pattern

Use an APID policy table:

| APID | Min Payload | Max Payload | Auth Required | Mode Requirement |
|---|---:|---:|---|---|
| `0x01` PING | 0 | small | optional | any |
| `0x02` RESETC | 0 | 0 | yes | maintenance/safe |
| `0x03` SEND_FW | 0 | 0 | yes | authorized |
| `0x04` SET_THRUSTER | 2 | 2 | yes | simulation/safe |
| `0x05` SET_BEACON_RATE | 1 | 1 | yes | authorized |
| `0x06` BROADCAST_MSG | 2 | bounded | yes | communications maintenance |
| `0x07` FLASH | 0 | bounded | yes | transfer mode |
| `0x08` SEND_TM | fixed | fixed | not TC | telemetry only |

### Evaluation Metric

- protected APID rejection rate,
- invalid APID rejection rate,
- false rejection rate for valid commands.

---

## CTRL-003: TC/TM Direction Enforcement

### Purpose

Ensure that telecommands and telemetry are not treated interchangeably.

### Required Rule

- TC packet type should be required for command handlers.
- TM packet type should not trigger command execution.
- TM-only APIDs should not be accepted as telecommands.

### Evaluation Metric

- direction-confusion packet rejection rate.

---

## CTRL-004: Packet Length Validation

### Purpose

Reject malformed SPP packets before copying payload bytes or dispatching APIDs.

### Required Checks

```text
space_packet != NULL
buffer != NULL
buffer_len >= SPP_PRIMARY_HEADER_LEN
version == CCSDS_SPP_VERSION
data_field_size = header.length + 1
data_field_size <= SPP_MAX_PAYLOAD_CHUNK
buffer_len == SPP_PRIMARY_HEADER_LEN + data_field_size
```

If trailing bytes are allowed, they must be documented and excluded from command dispatch.

### Evaluation Metric

- malformed packet rejection rate,
- parser crash count,
- handler reachability from malformed packets,
- valid packet acceptance rate.

---

## CTRL-005: Anti-Replay Counters

### Purpose

Prevent old valid commands from being reused.

### Design Options

- maintain last accepted counter per APID,
- reject duplicate counters,
- reject backwards counters,
- bind counters to authentication,
- expire commands after a validity window.

### Evaluation Metric

- replayed command rejection rate,
- accepted duplicate count,
- tolerance to packet loss.

---

## CTRL-006: Command Rate Limits

### Purpose

Reduce command-based denial of service.

### Suggested Limits

| Command | Control |
|---|---|
| RESETC | cooldown, confirmation, authorization |
| SET_BEACON_RATE | minimum interval and change-rate limit |
| FLASH | transfer quota and transfer state |
| BROADCAST_MSG | frequency allowlist and payload limit |
| SET_THRUSTER | mode gate and range limit |

### Evaluation Metric

- disruption duration,
- command rejection count,
- telemetry loss interval,
- recovery time.

---

## CTRL-007: Safe-Mode or Maintenance-Mode Policy

### Purpose

Prevent dangerous commands from running in inappropriate mission states.

### Example Policy

```text
normal mode:
  allow PING, SEND_FW, limited telemetry requests

maintenance mode:
  allow RESETC, FLASH, BROADCAST_MSG with authorization

simulation/safe actuator mode:
  allow SET_THRUSTER with range checks
```

### Evaluation Metric

- dangerous command rejection rate outside allowed mode,
- recovery behavior after mode change.

---

## CTRL-008: Telemetry Integrity

### Purpose

Let operators detect telemetry modification or corruption.

### Design Options

- sequence counters,
- message authentication tag,
- checksum for accidental corruption,
- signed event logs,
- authenticated encryption for sensitive telemetry.

### Evaluation Metric

- corrupted telemetry detection rate,
- missing telemetry detection time,
- sequence gap detection.

---

## CTRL-009: Telemetry Validity Flags

### Purpose

Avoid blindly trusting sensor values when sensors fail or bus data is suspicious.

### Example Flags

```text
sensor_valid
sensor_read_error
out_of_range
sudden_jump_detected
command_recently_changed_state
telemetry_integrity_ok
```

### Evaluation Metric

- invalid telemetry marking rate,
- false alarm rate,
- operator-visible anomaly coverage.

---

## CTRL-010: Command Audit Telemetry

### Purpose

Make command acceptance and rejection visible to operators.

### Recommended Audit Fields

```text
last_command_apid
last_command_status
last_rejection_reason
last_auth_failure_count
last_replay_rejection_count
last_policy_rejection_count
```

### Evaluation Metric

- accepted/rejected command visibility,
- time to detect unauthorized command attempts,
- completeness of event logs.

---

## Recommended Control Bundles

### Minimal Parser Hardening Bundle

- CTRL-004 Packet length validation
- CTRL-003 TC/TM direction enforcement
- CTRL-002 APID payload policy

### Command Authority Bundle

- CTRL-001 Command authentication
- CTRL-002 APID authorization
- CTRL-005 Anti-replay counters
- CTRL-010 Command audit telemetry

### Service-Disruption Bundle

- CTRL-006 Command rate limits
- CTRL-007 Safe-mode policy
- CTRL-010 Command audit telemetry

### Telemetry Trust Bundle

- CTRL-008 Telemetry integrity
- CTRL-009 Telemetry validity flags
- CTRL-010 Command audit telemetry

---

## Thesis Evaluation Table Template

| Control | Baseline Result | Protected Result | Improvement | Notes |
|---|---|---|---|---|
| Packet length validation | TBD | TBD | TBD | Parser robustness |
| APID authorization | TBD | TBD | TBD | Command authority |
| Rate limit | TBD | TBD | TBD | Service disruption |
| Telemetry validity flags | TBD | TBD | TBD | Observability |

---

## Key Principle

A defensive control is useful for the thesis only if it can be measured.

For each control, define:

1. what weakness it targets,
2. what behavior should change,
3. what metric proves the change,
4. what evidence will be saved.