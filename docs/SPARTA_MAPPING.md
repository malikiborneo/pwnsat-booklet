# SPARTA Mapping

This document maps the latest thesis scenario to SPARTA and Attack Flow.

The revised thesis uses SPARTA and Attack Flow as an **analysis layer**, not as the main contribution. The main contribution is experimental evidence about anti-spoofing controls in a PWNSAT FlatSat / SDR testbed.

---

## Latest Thesis Scenario

```text
Controlled space-link spoofing / command-deception scenario
  -> forged telecommand enters command path
  -> OBC parses SPP header
  -> APID dispatch routes packet
  -> handler executes or rejects command
  -> telemetry/logs/SDR evidence show effect
  -> controls interrupt the chain
```

---

## Attack Flow: Scenario S1

| Step | Description | Candidate SPARTA Mapping | Evidence |
|---|---|---|---|
| 1 | Signal or protocol analysis | REC-0002 Signal Analysis | captured/decoded packet structure, timing, APID observations |
| 2 | Command dictionary / APID inference | RE-0001 Reverse Engineering | decoded SPP fields, APID table, firmware review |
| 3 | SPP frame forgery | Frame forgery / command preparation | constructed lab-safe SPP packet and decoded fields |
| 4 | Signal or transport impersonation | EX-0007 Signal Impersonation | controlled SDR/transport evidence in authorised lab |
| 5 | Command injection into OBC pipeline | EX-0002 Command Injection | packet reaches parser/dispatcher |
| 6 | Unauthorised command execution attempt | EX-0001 Unauthorised Command Execution | ACK/state change/handler log/rejection event |
| 7 | Safe analogue impact or denial | IMP-0005 Denial of Service or analogous disruption impact | telemetry deviation, command delay, state change, recovery record |

---

## Attack Flow: Scenario S2

S2 extends S1 with sequence-counter manipulation or reuse.

| Step | Description | Candidate Mapping | Control Focus |
|---|---|---|---|
| 1 | Observe or infer sequence behaviour | REC-0002 / RE-0001 | identify normal sequence progression |
| 2 | Reuse, guess, or manipulate sequence count | Command deception / replay-adjacent behaviour | C4 sequence freshness |
| 3 | Attempt command acceptance | EX-0002 / EX-0001 | C1, C2, C3, C4 |
| 4 | Observe rejection or impact | IMP-0005 if disruption occurs | telemetry/log evidence |

---

## Control-to-Chain Mapping

| Control | Chain Step Interrupted | Expected Effect |
|---|---|---|
| C1 Cryptographic authentication | before SPP header parse / before command trust decision | forged packet rejected even if well-formed |
| C2 Command allow-listing and strict typing | APID dispatch to command handler | unauthorised APID/type/command tuple rejected |
| C3 Length and structural validation | SPP header parse | malformed or structurally invalid packets rejected before dispatch |
| C4 Sequence-counter freshness | after parse, before dispatch | replayed, duplicate, stale, or out-of-window sequence values rejected |

---

## Finding-to-SPARTA Mapping

| Technical Behaviour | SPARTA / Attack-Chain Interpretation | Defensive Control |
|---|---|---|
| Correct APID causes routing toward command handler | EX-0002 Command Injection / EX-0001 Unauthorised Command Execution | C2 allow-list and strict typing |
| Well-formed forged packet is treated as command-like | EX-0007 Signal Impersonation leading to EX-0002 | C1 authentication |
| Invalid length or malformed packet stresses parser | EX-0009 Exploit Software Vulnerability / erroneous input style behaviour | C3 structural validation |
| Old or duplicated sequence values accepted | replay-adjacent command deception | C4 sequence freshness |
| Command creates telemetry deviation or service delay | IMP-0005 Denial of Service or safe analogue disruption impact | C1-C4 combined controls |
| Logs/telemetry fail to show rejection reason | weak detection and reconstruction | audit telemetry and time-aligned evidence |

---

## How to Use SPARTA in the Thesis

Use SPARTA to answer:

```text
Where does this lab behaviour fit in the space-threat landscape?
```

Do not use SPARTA alone to claim:

```text
This control works.
```

Control effectiveness must come from repeated experiment results.

---

## Experiment Result Annotation Template

For each control configuration, write:

```text
Configuration:
Scenario:
Accepted forged command? yes/no
Interrupted chain step:
Relevant SPARTA mapping:
Evidence stream:
Metric result:
Interpretation:
```

Example:

```text
Configuration: C2 allow-list enabled
Scenario: S1 forged telecommand
Accepted forged command? no
Interrupted chain step: APID dispatch -> command handler
Relevant SPARTA mapping: EX-0002 / EX-0001
Evidence stream: COSMOS log + OBC rejection telemetry
Metric result: command acceptance rate reduced from baseline to protected condition
Interpretation: strict APID/type policy reduced command-deception success in the lab testbed
```

---

## Claim Discipline

| Claim | Required Evidence |
|---|---|
| Mapped risk | source code, packet format, or architecture supports the path |
| Reproduced lab chain | controlled lab packet reaches expected pipeline stage |
| Demonstrated impact | telemetry/log/state/timing evidence shows safe analogue effect |
| Control effectiveness | repeated baseline vs protected comparison |
| Operational trade-off | false rejection, latency, CPU/memory, or operator overhead data |

---

## Thesis Position

SPARTA and Attack Flow help explain the scenario. They are not the thesis result.

The thesis result is the measured effect of anti-spoofing controls against a controlled forged-telecommand chain.