# Experiment Plan

This document turns the PwnSat / FlatSat repository into a repeatable thesis experiment plan.

All experiments must remain inside an isolated, authorized laboratory environment. USB/local reproduction is preferred before any controlled RF test.

---

## Research Objective

Evaluate how defensive controls reduce satellite service-disruption risk in a controlled PwnSat / FlatSat command-and-telemetry environment.

The experiment workflow is:

```text
baseline behavior
  -> attack or malformed-input condition
  -> defensive control implementation
  -> repeated measurement
  -> SPARTA / Attack Flow interpretation
```

---

## General Safety Boundary

Allowed:

- local PwnSat / FlatSat testing,
- offline packet analysis,
- USB/local reproduction,
- shielded, cabled, or otherwise authorized lab RF,
- passive observation where legal,
- documentation and defensive hardening.

Not allowed:

- real satellite targets,
- public RF systems,
- third-party infrastructure,
- uncontrolled RF fuzzing,
- operational jamming procedures.

---

## Common Test Record

Every experiment should record:

| Field | Description |
|---|---|
| Test ID | Unique experiment identifier. |
| Date | Date and time of test. |
| Firmware build | Commit SHA, build artifact, or version. |
| Transport | Offline, USB framed, RF receive-only, or controlled RF. |
| Packet | Raw bytes and decoded SPP fields. |
| Expected behavior | What should happen. |
| Observed behavior | Logs, LED state, telemetry, reset, crash, or no response. |
| SPARTA mapping | Relevant tactic/technique. |
| Metric result | Timing, rejection count, disruption duration, or other measure. |
| Safety controls | Shielding, low power, cabled setup, or USB-only mode. |
| Interpretation | What the result means for the thesis. |

---

## Experiment Group 1: Command Authority

### Question

Can unauthorized command traffic reach mission-impacting APID handlers?

### Baseline

Send valid commands in the controlled lab environment and confirm expected command behavior.

Candidate APIDs:

- `0x01` PING,
- `0x02` RESETC,
- `0x03` SEND_FW,
- `0x04` SET_THRUSTER,
- `0x05` SET_BEACON_RATE,
- `0x06` BROADCAST_MSG,
- `0x07` FLASH.

### Attack Condition

Send command packets without authentication or authorization and observe whether handlers execute.

### Defensive Condition

Add or simulate:

- command authentication,
- APID authorization policy,
- TC/TM direction enforcement,
- command audit telemetry.

### Metrics

| Metric | Meaning |
|---|---|
| Command acceptance rate | Percentage of test commands accepted. |
| Unauthorized command rejection rate | Percentage of unauthorized commands rejected. |
| State-change success rate | Whether protected state changed. |
| Audit visibility | Whether accepted/rejected commands are visible in telemetry/logs. |

### Expected Thesis Evidence

A table comparing baseline and protected command behavior.

---

## Experiment Group 2: Parser Robustness

### Question

Can malformed SPP packets cause parser instability or unsafe behavior?

### Baseline

Use valid SPP packets and confirm normal parsing.

### Malformed Conditions

Test controlled packet mutations:

- truncated packet,
- declared length larger than received data,
- declared length equal to boundary values,
- unexpected APID,
- invalid version,
- trailing bytes,
- one-byte payload edge cases.

### Defensive Condition

Add or simulate strict parser validation:

```text
buffer != NULL
space_packet != NULL
buffer_len >= SPP_PRIMARY_HEADER_LEN
version == CCSDS_SPP_VERSION
data_field_size = header.length + 1
data_field_size <= SPP_MAX_PAYLOAD_CHUNK
buffer_len == SPP_PRIMARY_HEADER_LEN + data_field_size
```

### Metrics

| Metric | Meaning |
|---|---|
| Malformed rejection rate | Percentage of malformed packets rejected. |
| Parser crash count | Number of crashes or sanitizer findings. |
| Unexpected handler reachability | Whether malformed packets reach APID handlers. |
| False rejection rate | Whether valid packets are rejected. |

### Expected Thesis Evidence

- packet mutation table,
- baseline vs hardened parser result,
- sanitizer or debug evidence where available.

---

## Experiment Group 3: Service Disruption

### Question

Can valid-looking commands degrade availability or telemetry service?

### Test Cases

| Case | APID | Expected Disruption |
|---|---|---|
| Reset loop | `0x02` | Board reset or command-path interruption. |
| Beacon flood | `0x05` | Excessive beacon traffic or telemetry timing disruption. |
| Flash transfer abuse | `0x07` | Blocking transfer and normal telemetry delay. |
| Broadcast misuse | `0x06` | Retune attempt or unsafe handler behavior. |

### Defensive Condition

Add or simulate:

- reset cooldown,
- minimum beacon interval,
- transfer quota,
- command rate limiting,
- mode-gated high-impact commands,
- safe-mode policy.

### Metrics

| Metric | Meaning |
|---|---|
| Disruption duration | Time from disruption start to normal recovery. |
| Telemetry loss interval | Time without normal telemetry. |
| Command response delay | Delay before command processing resumes. |
| Recovery success | Whether normal operation returns automatically. |
| Control effectiveness | Reduction in disruption compared with baseline. |

### Expected Thesis Evidence

A before/after table showing how rate limits and policy reduce disruption.

---

## Experiment Group 4: Telemetry Trust and Observability

### Question

Can telemetry be trusted, and can the lab observe when telemetry is manipulated or disrupted?

### Baseline

Record normal telemetry timing and values.

### Test Conditions

- compare I2C sensor activity with APID `0x08` telemetry,
- observe telemetry during command-induced state changes,
- observe telemetry during service disruption,
- evaluate whether telemetry carries validity or rejection information.

### Defensive Condition

Add or simulate:

- telemetry validity flags,
- range checks,
- sudden-jump detection,
- sequence counters,
- integrity protection,
- accepted/rejected command events.

### Metrics

| Metric | Meaning |
|---|---|
| Telemetry continuity | Whether telemetry remains available. |
| Telemetry correctness | Whether telemetry reflects actual state. |
| Detection time | Time to detect abnormal behavior. |
| Recovery time | Time to return to normal telemetry. |
| Observability coverage | Whether logs/telemetry explain what happened. |

### Expected Thesis Evidence

- telemetry timeline,
- sensor-to-telemetry correlation,
- control comparison table.

---

## Suggested Experiment Sequence

1. Establish USB PING baseline.
2. Decode baseline telemetry.
3. Run parser edge-case tests offline.
4. Reproduce safe malformed-packet behavior through USB.
5. Test service-disruption APIDs locally.
6. Apply defensive controls.
7. Repeat tests with controls enabled.
8. Map each case to SPARTA and Attack Flow.
9. Write results using the evidence log template.

---

## Final Thesis Output

The final thesis should include:

- attack-flow diagrams,
- SPARTA mapping table,
- baseline vs controlled results,
- defensive control effectiveness table,
- discussion of limitations,
- safe-scope statement,
- reproducibility notes.