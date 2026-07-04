# Defensive Controls

This document defines the four protocol-level defensive controls used in the latest thesis proposal.

The earlier broad ground-segment controls are now background only. The current thesis evaluates spoofing resilience in the command path.

---

## Latest Control Focus

| Control ID | Control | Main Purpose |
|---|---|---|
| C1 | Cryptographic authentication | Reject forged packets even when syntactically valid. |
| C2 | Command allow-listing and strict typing | Reject unauthorised APID / Packet Type / command combinations. |
| C3 | Length and structural validation | Reject malformed SPP packets before parser/handler misuse. |
| C4 | Sequence-counter freshness / anti-replay | Reject duplicate, stale, or out-of-window command sequences. |

---

## Control Evaluation Model

Each control should be evaluated using the same structure:

```text
baseline forged-command behaviour
  -> enable control
  -> repeat same scenario
  -> measure accepted/rejected commands
  -> record telemetry/log/SDR evidence
  -> compare against baseline
```

---

## C1: Cryptographic Authentication

### Purpose

Ensure that a telecommand is accepted only when it carries a valid authentication tag.

### Candidate Implementation

For thesis scope, a simplified HMAC-based design is enough:

```text
SPP packet fields + payload
  -> HMAC-SHA256 with shared lab key
  -> authentication tag appended or checked before dispatch
```

### Pipeline Insertion Point

```text
Frame Sync
  -> C1 authentication check
  -> SPP Header Parse
```

### Expected Effect

A forged command without a valid tag should be rejected before APID dispatch.

### Metrics

- forged command rejection rate,
- valid command acceptance rate,
- false rejection rate,
- added command latency.

---

## C2: Command Allow-Listing and Strict Typing

### Purpose

Prevent a well-formed packet from reaching a handler unless its APID, Packet Type, command identifier, and expected mode are allowed.

### Candidate Manifest

```json
{
  "commands": [
    {
      "apid": "0x01",
      "packet_type": "TC",
      "name": "PING",
      "min_len": 0,
      "max_len": 0,
      "mode": "any"
    }
  ]
}
```

### Pipeline Insertion Point

```text
SPP Header Parse
  -> APID Dispatch
  -> C2 allow-list / strict type check
  -> Command Handler
```

### Expected Effect

Packets with wrong APID, wrong Packet Type, wrong command ID, unexpected mode, or unexpected payload length should be rejected before handler execution.

### Metrics

- unauthorised command rejection rate,
- wrong Packet Type rejection rate,
- invalid APID rejection rate,
- legitimate command false rejection rate.

---

## C3: Length and Structural Validation

### Purpose

Reject malformed SPP packets before they can affect parser or handler behaviour.

### Required Checks

```text
buffer != NULL
space_packet != NULL
buffer_len >= SPP_PRIMARY_HEADER_LEN
version == expected SPP version
data_field_size = length_field + 1
data_field_size <= maximum supported payload
buffer_len == SPP_PRIMARY_HEADER_LEN + data_field_size
APID-specific length rule passes
secondary-header rule passes, if used
```

### Pipeline Insertion Point

```text
Frame Sync
  -> SPP Header Parse
  -> C3 structural validation
  -> APID Dispatch
```

### Expected Effect

Malformed, truncated, oversized, or structurally inconsistent packets should not reach APID dispatch.

### Metrics

- malformed packet rejection rate,
- unexpected handler reachability,
- parser crash count,
- valid command false rejection rate.

---

## C4: Sequence-Counter Freshness / Anti-Replay

### Purpose

Prevent accepted command traffic from being replayed or accepted with stale sequence values.

### Candidate Implementation

```text
per-APID last accepted sequence count
sliding acceptance window
reject duplicate count
reject backwards count
record rejection reason
```

### Pipeline Insertion Point

```text
SPP Header Parse
  -> C4 freshness check
  -> APID Dispatch
```

### Expected Effect

Reused, duplicate, stale, or implausible sequence values should be rejected before handler execution.

### Metrics

- replay/stale sequence rejection rate,
- false rejection rate under normal sequence gaps,
- command acceptance rate after freshness enforcement.

---

## Full Defence Configuration

The strongest configuration is:

```text
C1 + C2 + C3 + C4
```

Expected chain interruption:

```text
forged packet without valid tag
  -> rejected by C1

well-formed but unauthorised command
  -> rejected by C2

malformed SPP structure
  -> rejected by C3

replayed or stale sequence
  -> rejected by C4
```

---

## Control Matrix

| Configuration | Purpose |
|---|---|
| Baseline | measure unprotected behaviour |
| C1 | authentication-only effectiveness |
| C2 | allow-list-only effectiveness |
| C3 | structural-validation-only effectiveness |
| C4 | freshness-only effectiveness |
| Pairwise combinations | identify useful control interactions |
| C1+C2+C3+C4 | evaluate full defence configuration |

---

## Operational Trade-Offs

Each control may impose cost:

| Control | Possible Cost |
|---|---|
| C1 | added latency, key management complexity, false rejection if tag handling fails |
| C2 | configuration burden, maintenance of allowed command manifest |
| C3 | rejection of edge-case but legitimate packets if rules are too strict |
| C4 | packet-loss tolerance challenge, sequence resynchronisation burden |

The thesis should report these trade-offs, not only security improvement.

---

## Thesis Evaluation Table Template

| Control Config | Forged Acceptance Rate | Chain Completion Rate | TTD | TTR | False Rejection | Overhead | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| Baseline | TBD | TBD | TBD | TBD | TBD | TBD | unprotected behaviour |
| C1 | TBD | TBD | TBD | TBD | TBD | TBD | authentication effect |
| C2 | TBD | TBD | TBD | TBD | TBD | TBD | allow-list effect |
| C3 | TBD | TBD | TBD | TBD | TBD | TBD | structural validation effect |
| C4 | TBD | TBD | TBD | TBD | TBD | TBD | freshness effect |
| Full | TBD | TBD | TBD | TBD | TBD | TBD | combined defence |

---

## Key Principle

A defensive control is thesis-useful only if its effect is measurable.

For each control, record:

1. what chain step it targets,
2. what behaviour should change,
3. what metric proves the change,
4. what operational cost appears,
5. what evidence supports the conclusion.