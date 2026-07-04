# Thesis Rescue Plan: July to September

Current date: 2026-07-04.

September poster session is close. If the session is at the start of September, there are about 8 weeks. If it is at the end of September, there are about 12 weeks. The previous plan is too large for that window.

This plan reduces the thesis to one defensible claim, one primary experiment, and a small number of controls.

## Brutal Reality

You do not have enough time to complete all of this:

- full SDR transmit spoofing,
- OpenC3 integration,
- 12 control combinations,
- N >= 30 for every cell,
- TTD and TTR measurement,
- all APIDs,
- fuzzing plus RF spoofing plus defensive engineering,
- full C1-C4 implemented on hardware,
- polished thesis writing from scratch.

Trying to do all of that now will probably produce weak evidence everywhere.

The thesis must become narrower.

## New Core Thesis

Recommended title:

**Experimental Evaluation of Protocol-Level Anti-Spoofing Controls Against Forged Telecommands in a PwnSat FlatSat Testbed**

Defensible thesis claim:

> The PwnSat FlatSat command path accepts forged SPP telecommands without authentication in the baseline configuration. A small set of protocol-level controls can reduce forged-command acceptance and unsafe handler reachability under controlled lab conditions.

This is honest because:

- USB proves packet construction and handler reachability.
- Controlled RF, if completed, proves link-delivered spoofing.
- Controls are evaluated against the same packet format and command path.
- The thesis does not claim real satellite compromise.

## What Counts As Spoofing

USB test:

```text
Terminal B sends forged SPP packet over USBRadioLink.
FlatSat accepts packet.
Handler executes.
```

This proves unauthenticated command-path acceptance. It is not RF spoofing yet.

RF spoofing test:

```text
Attacker-controlled RF transmitter sends forged SPP packet.
FlatSat uplink radio receives it.
commandHandler() parses it.
APID handler executes.
```

This proves controlled FlatSat RF telecommand spoofing.

If RF is not stable by poster time, the honest fallback is:

> The thesis demonstrates unauthenticated command-path acceptance over USB and defines RF spoofing as a planned/partial validation step, with software and firmware evidence showing that the RF path converges on the same command handler.

That fallback is weaker, but still academically salvageable if documented honestly.

## Minimum Viable Research Questions

Use only three questions.

| ID | Question | Evidence |
| --- | --- | --- |
| RQ1 | Can forged SPP telecommands reach PwnSat command handlers without authentication in the baseline FlatSat command path? | USB baseline logs, decoded packets, firmware logs, optional RF logs. |
| RQ2 | Which minimal protocol-level controls reduce forged-command acceptance or unsafe handler reachability? | Before/after results for selected controls. |
| RQ3 | How should the observed command path be mapped to SPARTA and safe FlatSat threat modelling? | SPARTA table and attack-flow explanation. |

Remove TTD and TTR from the core research questions. They are too expensive unless you already have a detector and recovery procedure.

## Minimum Viable Controls

Do not try to implement all C1-C4 fully on hardware before the poster.

Prioritize:

| Priority | Control | Keep? | Reason |
| --- | --- | --- | --- |
| 1 | C2 APID policy / strict typing | Yes | Simple, directly tied to firmware dispatch. |
| 2 | C3 length and structure validation | Yes | Simple, directly tied to `spp_unpack_packet()`. |
| 3 | C1 authentication | Partial or software-first | True anti-spoofing, but may take longer on hardware. |
| 4 | C4 sequence freshness | Optional | Useful for replay, weak against spoofing unless combined with C1. |

Poster-time claim should be:

> C2 and C3 are implemented or evaluated directly. C1 is specified and prototyped if time permits. C4 is treated as replay protection, not standalone anti-spoofing.

## Minimum Viable Experiment Matrix

Do not use N >= 30 for every configuration now.

Use:

| Config | Transport | APID | Trial count | Goal |
| --- | --- | --- | --- | --- |
| B0 baseline | USB | `0x03` SEND_FW | 10 | Confirm forged command acceptance. |
| B0 baseline | USB | `0x05` SET_BEACON_RATE or `0x04` SET_THRUSTER | 10 | Confirm safe state-change command acceptance. |
| B0 baseline | RF, if working | `0x03` SEND_FW | 5 to 10 | Confirm RF-delivered spoofing. |
| C2 policy | USB | same APIDs | 10 | Show unauthorized or disallowed command rejection. |
| C3 validation | USB | malformed length cases | 10 | Show malformed packet rejection. |
| C1 auth prototype | software-first or firmware, if working | `0x03` | 10 | Show no valid tag means reject. |

Minimum useful number:

```text
40 to 60 total trials
```

This is far more realistic than 720+ trials.

Do not claim strong statistics from this. Say:

> Results are reported as repeated controlled observations and acceptance/rejection rates. They are not population-level proof of security.

## What To Measure

Use simple binary outcomes.

| Field | Meaning |
| --- | --- |
| `packet_hex` | Raw SPP packet sent. |
| `transport` | USB or controlled RF. |
| `apid` | Target APID. |
| `seq` | Sequence count. |
| `accepted` | Did firmware log `[TC - SPP]` and dispatch? |
| `response_seen` | Did expected TM response appear? |
| `state_changed` | Did safe state change occur? |
| `rejected_reason` | Parser, policy, auth, or no response. |
| `notes` | Hardware/log observations. |

Do not measure TTD/TTR unless a detector and recovery script already exist.

## Safe APIDs

Use APIDs that give evidence without creating chaos.

| APID | Use |
| --- | --- |
| `0x01` PING | Basic liveness. |
| `0x03` SEND_FW | Best first case. Gives deterministic telemetry response. |
| `0x04` SET_THRUSTER | Safe state-change analogue, if telemetry confirms state. |
| `0x05` SET_BEACON_RATE | Service-impact analogue, but avoid zero unless lab-safe. |

Avoid as core cases:

| APID | Reason |
| --- | --- |
| `0x02` RESETC | Disruptive and slows repeated testing. |
| `0x06` BROADCAST_MSG | Can drag thesis into memory corruption and RF retune complexity. |
| `0x07` FLASH | Blocking transfer, useful later but time-consuming. |

## Weekly Plan

### Week 1: 2026-07-04 to 2026-07-10

Goal: understand and document the command path.

Deliverables:

- one-page architecture diagram,
- confirm USB command baseline for APID `0x03`,
- record 10 USB trials,
- write the baseline result table.

### Week 2: 2026-07-11 to 2026-07-17

Goal: make evidence repeatable.

Deliverables:

- trial log CSV,
- packet decoding table,
- screenshots or terminal logs,
- APID `0x03` and one safe state-change APID tested over USB.

### Week 3: 2026-07-18 to 2026-07-24

Goal: attempt controlled RF delivery.

Deliverables:

- determine exact RF payload format,
- test whether raw SPP bytes over RF reach `commandHandler()`,
- record success or failure honestly,
- if RF fails, document why and preserve USB plus source-code convergence evidence.

### Week 4: 2026-07-25 to 2026-07-31

Goal: implement or simulate C3 parser validation.

Deliverables:

- before/after malformed length tests,
- rejection evidence,
- code diff or emulator results.

### Week 5: 2026-08-01 to 2026-08-07

Goal: implement or simulate C2 APID/type policy.

Deliverables:

- APID policy table,
- allowed vs disallowed test cases,
- rejection evidence.

### Week 6: 2026-08-08 to 2026-08-14

Goal: C1 authentication decision.

Pick one:

- implement minimal firmware authentication, or
- build software-first authenticated command pipeline and clearly label it as prototype.

Do not get stuck here for more than one week.

### Week 7: 2026-08-15 to 2026-08-21

Goal: analysis and poster figures.

Deliverables:

- baseline vs controls table,
- command path diagram,
- SPARTA mapping,
- limitations slide.

### Week 8: 2026-08-22 to 2026-08-31

Goal: poster-ready package.

Deliverables:

- poster abstract,
- final title,
- final RQs,
- results figure,
- limitations and next steps.

September should be polish, not discovery.

## Poster Story

The poster should tell a simple story:

1. PwnSat FlatSat accepts SPP telecommands by APID.
2. Baseline command path lacks authentication and policy checks.
3. A forged `SEND_FW` telecommand was accepted in the lab.
4. Controlled RF delivery is tested or attempted.
5. C2/C3 controls reduce unsafe command reachability and malformed packet acceptance.
6. C1 is the strongest anti-spoofing control and is either prototyped or specified as the required next hardening step.
7. The contribution is a reproducible measurement workflow, not a new satellite attack.

## Supervisor Update Text

Send something like this:

> I agree that the previous matrix is too broad for the remaining timeline. I have narrowed the thesis to a minimum viable experiment: demonstrate unauthenticated forged SPP telecommand acceptance in the PwnSat FlatSat command path, attempt controlled RF delivery of the same packet, and evaluate a small set of protocol-level controls, prioritising APID/type policy and length validation. I will treat full HMAC authentication and sequence freshness as stretch controls unless implementation stabilises quickly. The poster will focus on command-path evidence, baseline vs defended behavior, and limitations rather than claiming a complete SDR cyber range.

## Final Advice

Do not chase novelty by adding more hardware.

Novelty now comes from:

- clarity,
- repeatability,
- honest limitations,
- before/after control comparison,
- a clean mapping from firmware evidence to thesis claims.

Your strongest thesis is small and sharp:

> A measured FlatSat command-path hardening study against forged telecommands.

