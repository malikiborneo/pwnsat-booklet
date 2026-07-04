# Thesis Proposal Alignment Review Against `pwnsat-booklet`

Reviewed proposal:

`D:\Monash University\Semester 4\Term 8\ITI5126-ITI5127-ITI5128 Master Thesis\34292020-RezaMalikiAkbar-BayuAnggorojati-LitReviewProposal_rev2.docx`

Reviewed repository:

`malikiborneo/pwnsat-booklet`, local branch `main`, clean against `origin/main`.

## Bottom Line

The proposal is directionally aligned with the repository, but it is not yet scientifically tight enough to defend without revision.

The strongest thesis is not "space-link spoofing in general" and not "SPARTA modelling." The defensible thesis is:

> A controlled, metrics-driven evaluation of command-path hardening against forged CCSDS-style SPP telecommands in the PwnSat FlatSat lab, using USB-first reproducibility and RF/SDR-assisted confirmation where hardware permits.

The current proposal's main weakness is overpromising. It claims a full FlatSat, PlutoSDR, OpenC3 COSMOS, SDR observability, four controls, pairwise combinations, two spoofing scenarios, TTD, TTR, overhead, and N >= 30 trials per cell. That is possible only if the experiment harness, logging, detector, and control modules already exist. They do not currently exist in this repo.

## Extracted Proposal Facts

- Proposal title: "Experimental Evaluation of Anti-Spoofing Controls Against Space-Link Command-Deception in a PWNSAT FlatSat and Software-Defined Radio Testbed."
- Extracted DOCX structure: 139 non-empty paragraphs, 5 tables, about 5,707 words.
- Reference section: 33 reference slots, including one `(reserved)` placeholder.
- Main experimental controls: C1 HMAC-style authentication, C2 command allow-listing/strict typing, C3 length and structural validation, C4 sequence-counter freshness.
- Main metrics: chain completion rate, command acceptance rate, disruption duration, time-to-detect, time-to-recover, false-rejection rate, operational overhead.
- Claimed experiment matrix: baseline + 4 single controls + 6 pairwise combinations + full defense = 12 configurations.
- With S1 and S2 and N >= 30, the proposal commits to at least 720 attack trials before legitimate-command false-rejection tests:

```text
2 scenarios x 12 configurations x 30 repetitions = 720 trials
```

That number is the proposal's biggest feasibility risk.

## Repository Evidence

The repo strongly supports the PwnSat/SPP command-path direction:

- `firmware/mission.h` defines APIDs `0x01` through `0x08`.
- `firmware/spp.cpp` implements CCSDS-style SPP packet build/unpack logic.
- `firmware/worker.cpp` dispatches commands by APID through `commandApidHandler()`.
- `scripts/spp_tools.py` builds and decodes SPP packets.
- `scripts/usb_tc_send.py` builds and sends framed SPP telecommands over the USB command endpoint.
- `Appendix B APID and Packet Reference.md` documents APIDs, SPP header fields, and PwnSat RF parameters.
- `Firmware Vulnerability and Exploitation Draft.md` documents the current architectural weakness: RF and USB command paths converge on `commandHandler()` and `commandApidHandler()` without authentication, authorization, replay protection, or APID direction enforcement.
- `Phase 6 Defensive Engineering and Hardening.md` already names the exact defense families the proposal wants to evaluate: authentication, bounds-checked parsing, APID authorization, anti-replay, rate limits, and telemetry hardening.

The repo does not yet support several proposal claims:

- No implemented HMAC verifier.
- No implemented APID policy table.
- No implemented replay/freshness module.
- No experiment runner for N repeated trials.
- No CSV/JSON evidence schema.
- No automated timing correlation for TTD/TTR.
- No OpenC3 COSMOS target/interface configuration checked into the repo.
- No PlutoSDR/GNU Radio flowgraph or reproducible SDR capture pipeline checked into the repo.

## Brutal Scientific Findings

| Severity | Finding | Why it matters | Fix |
| --- | --- | --- | --- |
| High | The experiment matrix is too large for the current repo state. | 720 attack trials plus legitimate-command trials require automation, stable reset/recovery, log capture, and analysis scripts. The repo currently has packet helpers, not a campaign runner. | Define a minimum publishable matrix first, then make the full pairwise matrix optional. |
| High | TTD and TTR are not currently measurable as written. | Time-to-detect requires a detector or a defined operator-observation rule. Time-to-recover requires a repeatable recovery procedure and baseline-restored definition. | Replace vague TTD/TTR with explicit events: `t_inject`, `t_accept`, `t_telemetry_deviation`, `t_alert`, `t_recovered`. |
| High | The proposal overstates SDR/OpenC3 readiness. | The repo shows SPP, USB, firmware, RF parameters, and docs. It does not show OpenC3 config or SDR flowgraphs. | Say "planned evidence streams" unless those artifacts are added. |
| High | "HMAC verified before SPP header parse" is technically imprecise. | If the tag is appended to an SPP packet, the receiver must at least parse minimal framing/length to locate the tag. Full dispatch should wait until authentication succeeds. | Change insertion point to "after minimal frame/header length parse, before APID dispatch and command execution." |
| High | C4 sequence freshness is weak against spoofing if unauthenticated. | A guessed or observed 14-bit sequence count can be forged. Sequence checks mainly help replay unless bound to an authenticated session. | State that C4 alone is expected to reduce naive replay, not cryptographically prevent spoofing. |
| Medium | N >= 30 is not enough to claim elimination. | If 0 successes occur in 30 trials, the rough 95% upper bound is about 10% by the rule of three. | Write "no successes observed; upper 95% bound approximately 3/N" rather than "prevents." |
| Medium | The proposal mixes command-deception, DoS, fuzzing, RF spoofing, and memory corruption. | Too many impact classes can make the thesis look unfocused. | Use forged telecommand acceptance as the primary outcome. Treat fuzzing/memory corruption as background or secondary evidence. |
| Medium | The current title is broader than the repo evidence. | "Software-Defined Radio testbed" makes SDR central. The repo currently centers firmware, SPP, USB tooling, and PwnSat RF parameters. | Retitle around "PwnSat command-path hardening" and make SDR-assisted observability secondary. |
| Medium | The Black Hat Asia 2026 material is not independently reproducible unless cited or archived. | Examiner cannot verify private workshop claims. | Mark it as author-observed training material and back core claims with repo artifacts, CCSDS, NIST, Viasat, SPARTA, and peer-reviewed work. |
| Medium | The proposal needs an explicit dependent-variable table. | Metrics are listed, but not tied to exact log fields or pass/fail rules. | Add a measurement table with event source, timestamp field, unit, and acceptance criterion. |
| Low | The reference list has a `(reserved)` placeholder. | It looks unfinished. | Remove it or fill it before submission. |

## Repository-Aligned Thesis Framing

Use this revised objective:

> This thesis evaluates whether protocol-level command-path controls reduce forged telecommand acceptance and service disruption in the PwnSat FlatSat lab. The experiment uses the existing PwnSat SPP command path as the baseline, validates payload behavior over the deterministic USB command endpoint first, and uses the RF/SDR path as a hardware-backed confirmation and observability layer where available. The evaluated controls are parser length hardening, APID/type policy enforcement, message authentication, and sequence freshness. SPARTA and Attack Flow are used only to describe and interpret the tested chain.

Use this revised contribution statement:

> The contribution is not a new satellite attack. The contribution is a reproducible before/after measurement of how specific defensive controls change command acceptance, telemetry-visible impact, and operational cost in an authorized FlatSat testbed.

## Recommended Research Questions

Replace the current RQs with these tighter versions:

| ID | Revised question | Evidence |
| --- | --- | --- |
| RQ1 | How does the current PwnSat SPP command path accept or reject forged telecommands across selected APIDs under controlled lab delivery? | Baseline packet traces, firmware logs, APID handler outcomes, telemetry effects. |
| RQ2 | How much do parser hardening, APID/type policy, message authentication, and sequence freshness reduce forged-command acceptance and safe-analogue disruption? | Per-control acceptance/rejection rates with confidence intervals across repeated trials. |
| RQ3 | Which evidence streams are sufficient to reconstruct command deception and recovery in the PwnSat lab? | Time-aligned USB/RF packet logs, firmware serial logs, telemetry changes, and analysis notebook outputs. |

This is narrower, more measurable, and more aligned with the repository.

## Minimum Publishable Experiment Matrix

Do not start with all 12 combinations. Start with a matrix that can produce defensible results quickly:

| Config | Purpose |
| --- | --- |
| B0 baseline | Current behavior, no added controls. |
| C3 parser hardening | Tests length/structure rejection. |
| C2 APID/type policy | Tests command authorization and direction enforcement. |
| C1 authentication | Tests forged-command rejection. |
| C1+C2+C3 | Tests realistic layered command-path defense. |
| C1+C2+C3+C4 | Tests full proposed defense. |

For one primary scenario:

```text
6 configurations x 30 repetitions = 180 attack trials
```

For two scenarios:

```text
2 scenarios x 6 configurations x 30 repetitions = 360 attack trials
```

That is still serious, but it is much more defensible than 720+ trials before the tooling exists.

Keep the full 12-configuration pairwise matrix as an expansion target only after the harness is stable.

## Recommended Scenario Scope

Use two safe, measurable outcomes:

| Scenario | APID candidate | Impact type | Why |
| --- | --- | --- | --- |
| S1 command acceptance | `0x01` PING or `0x03` SEND_FW | Acceptance/liveness | Low risk, deterministic, good for measuring rejection without state damage. |
| S2 service disruption analogue | `0x05` SET_BEACON_RATE or `0x04` SET_THRUSTER | State change visible in telemetry/logs | Measurable disruption/state manipulation without using destructive real-world commands. |

Keep APID `0x06` BROADCAST_MSG underflow and memory-corruption work out of the main thesis experiment unless you have debugger traces and a stable reproduction. It is valuable, but it drags the thesis into exploit reliability rather than control evaluation.

## Specific Proposal Edits

### Title

Current title:

> Experimental Evaluation of Anti-Spoofing Controls Against Space-Link Command-Deception in a PWNSAT FlatSat and Software-Defined Radio Testbed

Better:

> Metrics-Driven Evaluation of Command-Path Hardening Against Forged SPP Telecommands in a PwnSat FlatSat Lab

Reason: the revised title matches the repository. It does not over-center PlutoSDR or claim a broad space-link spoofing platform before the SDR/COSMOS artifacts are checked in.

### Introduction

Keep Viasat/KA-SAT, but be precise:

- Viasat says the 24 February 2022 KA-SAT incident affected several thousand customers in Ukraine and tens of thousands of fixed broadband customers across Europe.
- Viasat says the incident did not compromise the KA-SAT satellite itself.
- SentinelOne reports spillover affecting remote monitoring/control for 5,800 Enercon wind turbines.
- The EU publicly attributed the KA-SAT cyberattack to Russia on 10 May 2022.

Do not imply that KA-SAT was a satellite command-link spoofing incident. It was mainly a ground/management-network/modem disruption case. Use it only to justify service disruption as a mission-relevant impact.

### Method

Replace:

> HMAC-SHA256 over SPP packet using a shared session key; signature appended as a trailing field; verified before SPP header parse.

With:

> HMAC-SHA256 over dispatch-relevant SPP fields and payload using a shared lab key. The receiver performs minimal length/version parsing to locate the authentication field, then verifies the tag before APID dispatch or command execution. This is an SDLS-inspired educational prototype, not a full implementation of CCSDS SDLS key management.

### Sequence Freshness

Replace any wording that suggests sequence freshness prevents spoofing by itself.

Use:

> Sequence freshness is evaluated primarily as replay resistance. Because the SPP sequence count is only 14 bits and is visible to an observer, freshness without authentication is expected to be bypassable by a sequence-aware forger. Its main value is when bound to C1 authentication and per-APID/session state.

### Metrics

Add this table:

| Event | Source | Field | Unit |
| --- | --- | --- | --- |
| Injection attempt | trial runner | `t_inject` | ms |
| Parser result | firmware/test harness | `parse_status` | enum |
| Auth result | control module | `auth_status` | enum |
| Policy result | control module | `policy_status` | enum |
| Command dispatch | firmware/test harness | `dispatch_apid` | APID |
| Command accepted | firmware/test harness | `accepted` | boolean |
| Telemetry deviation | telemetry parser | `state_delta` | boolean/value |
| Detection event | detector/operator rule | `t_detect` | ms |
| Recovery event | recovery script/operator rule | `t_recovered` | ms |

Then define:

```text
command_acceptance_rate = accepted_forged_commands / total_forged_attempts
false_rejection_rate = rejected_legitimate_commands / total_legitimate_commands
TTD = t_detect - t_inject, only if a detector/operator rule is defined
TTR = t_recovered - t_detect, only if a recovery procedure is defined
```

## Statistical Wording

Use this language:

> Proportions are reported with 95% confidence intervals. For configurations with zero observed forged-command successes, the study reports the upper confidence bound rather than claiming complete prevention. With N = 30 and zero observed successes, the rough rule-of-three upper bound is approximately 10%.

This is brutally important. "0/30" is not "secure." It is "no success observed under these conditions."

## Required Repo Work Before the Proposal Is Fully True

Create or implement these artifacts:

| Artifact | Purpose |
| --- | --- |
| `experiments/run_trials.py` | Repeat trials and write structured results. |
| `experiments/schema.md` | Define event fields, timestamps, metrics, and units. |
| `experiments/results/*.csv` | Store baseline and control-run outputs. |
| `scripts/validate_results.py` | Compute rates, confidence intervals, and summary tables. |
| `firmware` control branch or modules | Implement parser hardening, APID policy, auth, freshness. |
| `docs/thesis_methodology.md` | Keep the thesis method synchronized with repo reality. |
| Optional OpenC3 config folder | Only if COSMOS remains a claimed evidence source. |
| Optional SDR/GNU Radio folder | Only if SDR remains central rather than observational. |

## Examiner Risk Assessment

| Area | Current risk | Reason |
| --- | --- | --- |
| Topic fit | Low | The proposal and repo both center PwnSat, SPP, APIDs, SPARTA, and command-path defense. |
| Scientific feasibility | Medium-high | Too many controls, scenarios, metrics, and toolchains for current implementation state. |
| Novelty | Medium | The novelty is not spoofing itself. The novelty must be reproducible measurement and control comparison in this specific FlatSat lab. |
| Evidence quality | Medium | Strong firmware/docs evidence exists, but repeated-trial evidence does not yet exist. |
| Safety/ethics | Low-medium | Scope is lab-contained, but offensive detail must stay controlled and framed as defense evaluation. |
| Citation risk | Medium | Private workshop material cannot carry core claims unless paired with reproducible repo artifacts and public sources. |

## Practical Revision Plan

1. Retitle and narrow the objective to PwnSat command-path hardening.
2. Replace the full pairwise matrix with a minimum publishable matrix plus optional expansion.
3. Define the exact APIDs used for primary experiments.
4. Define structured event fields and metrics before running tests.
5. Add repo artifacts for trial execution and result analysis.
6. Mark SDR/OpenC3 as "planned/optional" unless reproducible configs are added.
7. Treat SPARTA and Attack Flow as interpretation only, not contribution.
8. Remove the reserved reference placeholder.
9. Be explicit that C4 alone is weak against spoofing and mainly supports replay resistance.
10. Use confidence intervals and avoid prevention claims from small N.

## Final Verdict

This is a viable master's thesis if narrowed.

It is not viable as currently written if the examiner expects all stated infrastructure and metrics to be implemented. The proposal should stop sounding like a complete satellite cyber range and start sounding like a controlled experiment around one command path, four concrete controls, repeatable packet evidence, and honest statistical limits.

The repo already gives you the foundation. The missing piece is not more narrative. The missing piece is measurement discipline.

## External Fact Checks Used

- Viasat KA-SAT incident overview: https://www.viasat.com/perspectives/corporate/2022/ka-sat-network-cyber-attack-overview/
- SentinelOne AcidRain analysis: https://www.sentinelone.com/labs/acidrain-a-modem-wiper-rains-down-on-europe/
- Council of the EU attribution statement, 10 May 2022: https://www.consilium.europa.eu/en/press/press-releases/2022/05/10/russian-cyber-operations-against-ukraine-declaration-by-the-high-representative-on-behalf-of-the-european-union/
