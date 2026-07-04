# Evidence Log Template

Use this template for every latest-thesis experiment: spoofing baseline, control-enabled run, packet test, telemetry observation, SDR observation, or recovery measurement.

Good evidence is what turns a lab observation into a thesis result.

---

## Test Record

```text
Test ID:
Date / Time:
Researcher:
Thesis phase: software-first / FlatSat-backed
Firmware commit or build:
Repository commit:
Control configuration:
Scenario: S1 forged telecommand / S2 sequence-aware spoof
Transport: emulator / USB / cabled SDR / shielded SDR / receive-only observation
Safety controls:
```

---

## Research Question Link

```text
Relevant RQ:
  RQ1 scenario reproduction / RQ2 control effectiveness / RQ3 observability

Objective:

Hypothesis:
```

---

## Setup

```text
Ground Station VM:
OpenC3 COSMOS version/config:
Attacker or analysis VM:
PWNSAT FlatSat hardware:
OBC emulator version, if used:
SDR device, if used:
RF containment method:
Clock/time synchronisation method:
Software tools:
```

---

## Control Configuration

Mark enabled controls:

```text
[ ] Baseline, no added controls
[ ] C1 Cryptographic authentication
[ ] C2 Command allow-listing / strict typing
[ ] C3 Length and structural validation
[ ] C4 Sequence-counter freshness / anti-replay
```

Control implementation notes:

```text
C1 details:
C2 manifest/version:
C3 validation rules:
C4 window/counter rule:
```

---

## Packet or Input Record

```text
APID:
Packet Type:
Command ID, if applicable:
Sequence flags:
Sequence count:
Length field:
Declared data size:
Actual captured size:
Payload meaning:
Authentication tag present? yes/no
Authentication valid? yes/no/not applicable
Raw SPP bytes:
USB framed bytes, if used:
RF/link representation, if used:
```

---

## Expected Behaviour

```text
Expected parser result:
Expected control decision:
Expected APID dispatch result:
Expected handler behaviour:
Expected telemetry/log output:
Expected SDR/link observation:
Expected recovery behaviour:
```

---

## Observed Behaviour

```text
Observed parser result:
Observed control decision:
Observed APID dispatch result:
Observed handler behaviour:
Observed telemetry/log output:
Observed SDR/link observation:
Observed state change:
Observed reset/crash/lockup, if any:
Observed recovery behaviour:
Unexpected behaviour:
```

---

## Metrics

| Metric | Value | Notes |
|---|---:|---|
| Forged command accepted | TBD | yes/no |
| Forged command rejected | TBD | yes/no |
| Rejection reason visible | TBD | yes/no |
| Chain completed | TBD | yes/no |
| Safe analogue impact observed | TBD | yes/no |
| Disruption duration | TBD | seconds |
| Time-to-detect | TBD | seconds |
| Time-to-recover | TBD | seconds |
| False rejection of legitimate command | TBD | yes/no |
| Added latency | TBD | ms |
| Reproduction count | TBD | successful / total |

---

## Evidence Streams

```text
COSMOS command log:
COSMOS telemetry log:
Raw packet trace:
Decoded SPP packet output:
OBC emulator log:
FlatSat serial log:
SDR/link capture:
Screenshot:
Notebook output:
Attack Flow artifact:
SPARTA mapping table:
```

---

## SPARTA / Attack Flow Mapping

```text
Attack Flow step reached:
Attack Flow step interrupted:
SPARTA tactic/technique:
Affected trust boundary:
Control responsible for interruption:
```

---

## Interpretation

```text
What happened?

What does this prove?

What does this not prove?

Was the result reproduced?

Does the result support RQ1, RQ2, or RQ3?

What is the control effectiveness conclusion?

What operational trade-off appeared?
```

---

## Claim Level

Select one:

| Claim Level | Evidence Required | Selected? |
|---|---|---|
| Source-code risk | Code path or design shows possible weakness. |  |
| Scenario reproduced | Spoofing chain step is reproduced in authorised lab. |  |
| Command accepted | Forged command reaches handler or produces defined safe effect. |  |
| Command rejected by control | Same packet rejected under control-enabled condition. |  |
| Demonstrated disruption analogue | Telemetry/state/timing deviation observed. |  |
| Detection improvement | TTD improves or rejection becomes visible in logs/telemetry. |  |
| Recovery improvement | TTR improves or baseline state restored more reliably. |  |
| Memory corruption | Crash/sanitizer/debugger evidence exists. |  |

---

## Threats to Validity Notes

```text
Internal validity concern:
External validity concern:
Construct validity concern:
Mitigation applied:
Remaining limitation:
```

---

## Short Markdown Result Format

Use this format in thesis drafts:

```md
### Test ID: <ID>

- **Scenario:** S1 / S2
- **Control configuration:** Baseline / C1 / C2 / C3 / C4 / combination
- **Objective:**
- **Expected:**
- **Observed:**
- **Metric result:**
- **SPARTA / Attack Flow:**
- **Interpretation:**
- **Threats to validity:**
- **Next step:**
```

---

## Rule

Do not rely on memory. Save packet bytes, decoded fields, logs, screenshots, traces, timing values, and control decisions immediately after each test.