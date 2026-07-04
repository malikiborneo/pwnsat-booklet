# Evidence Log Template

Use this template for every thesis experiment, packet test, crash reproduction, telemetry observation, or defensive-control evaluation.

Good evidence is what turns a lab observation into a thesis result.

---

## Test Record

```text
Test ID:
Date / Time:
Researcher:
Firmware commit or build:
Repository commit:
Hardware setup:
Transport:
Safety controls:
```

---

## Scope

```text
Experiment group:
  Command authority / Parser robustness / Service disruption / Telemetry trust / Other

Objective:

In-scope actions:

Out-of-scope actions:
```

---

## Setup

```text
Board:
Power source:
USB port / serial port:
RF setup, if used:
Shielding or containment:
Logic analyzer, if used:
SDR receiver, if used:
Software tools:
```

---

## Packet or Input

```text
APID:
Packet type:
Sequence flags:
Sequence count:
Length field:
Declared data size:
Actual captured size:
Payload meaning:
Raw SPP bytes:
USB framed bytes, if used:
RF ASCII-hex form, if used:
```

---

## Expected Behavior

```text
Expected parser result:
Expected handler:
Expected telemetry/log output:
Expected LED/board behavior:
Expected safety behavior:
```

---

## Observed Behavior

```text
Observed parser result:
Observed handler behavior:
Observed telemetry/log output:
Observed LED/board behavior:
Observed reset/crash/lockup:
Observed timing:
Unexpected behavior:
```

---

## Metrics

| Metric | Value | Notes |
|---|---:|---|
| Command accepted | TBD | yes/no |
| Command rejected | TBD | yes/no |
| Rejection reason visible | TBD | yes/no |
| Telemetry lost | TBD | seconds |
| Recovery time | TBD | seconds |
| Crash/reset occurred | TBD | yes/no |
| Reproduction count | TBD | successful / total |
| Detection time | TBD | seconds |
| Control improvement | TBD | baseline vs protected |

---

## SPARTA / Attack Flow Mapping

```text
Attack Flow step:
SPARTA tactic:
SPARTA technique:
Affected trust boundary:
Mission impact category:
```

---

## Evidence Files

```text
Serial log:
USB capture:
RF capture:
Logic analyzer capture:
Screenshot:
Notebook output:
Crash artifact:
Telemetry record:
Attack Flow file:
```

---

## Interpretation

```text
What happened?

What does this prove?

What does this not prove?

Is the result reproducible?

Is the claim level source-code evidence, packet evidence, demonstrated impact, memory corruption, control-flow influence, or code execution?
```

---

## Defensive Control Result

```text
Control tested:
Baseline behavior:
Protected behavior:
Improvement observed:
Remaining weakness:
Next hardening step:
```

---

## Claim Level

Select one:

| Claim Level | Evidence Required | Selected? |
|---|---|---|
| Source-code risk | Code path or design shows possible weakness. |  |
| Reachable behavior | Packet reaches parser or handler. |  |
| Demonstrated impact | Logs, telemetry, reset, state change, or timing disruption observed. |  |
| Reproducible impact | Same effect reproduced across repeated trials. |  |
| Memory corruption | Crash, sanitizer result, or fault evidence. |  |
| Control-flow influence | Debugger shows controlled fault or saved-register influence. |  |
| Code execution | Chosen code path executed in target context. |  |

---

## Notes

```text
Open questions:
Limitations:
Follow-up test:
Supervisor discussion point:
```

---

## Short Markdown Result Format

Use this for thesis tables:

```md
### Test ID: <ID>

- **Objective:**
- **Transport:**
- **Packet/APID:**
- **Expected:**
- **Observed:**
- **SPARTA Mapping:**
- **Metric Result:**
- **Interpretation:**
- **Mitigation:**
```

---

## Rule

Do not rely on memory. Save packet bytes, decoded fields, logs, screenshots, and timing results as soon as the test is performed.