# Phase 6: Defensive Engineering and Hardening

The purpose of offensive testing is not merely to break the board. It is to produce better spacecraft engineering habits. This phase converts the Pwnsat findings into defensive requirements.

Good hardening starts at trust boundaries:

- Who can send a command?
- Which command is allowed in the current mode?
- Is the packet fresh?
- Is the payload length valid?
- Is telemetry trustworthy?
- What happens when a link is unavailable?

## Defensive Priorities

| Priority | Control | Why |
| --- | --- | --- |
| 1 | Command authentication | Prevents rogue transmitters from issuing telecommands. |
| 2 | Bounds-checked parsing | Prevents malformed packets from becoming memory corruption. |
| 3 | APID authorization | Prevents low-risk paths from reaching high-impact handlers. |
| 4 | Anti-replay | Prevents captured commands from being reused. |
| 5 | Telemetry integrity | Prevents operators from trusting forged or corrupted state. |
| 6 | Rate limits | Reduces reset loops, beacon floods, and transfer abuse. |
| 7 | Safe-mode policy | Restricts dangerous commands during anomalous conditions. |

## Parser Hardening

The SPP parser should reject malformed packets before copying payload bytes.

Minimum checks:

```text
buffer != NULL
buffer_len >= SPP_PRIMARY_HEADER_LEN
version == CCSDS_SPP_VERSION
data_field_size = header.length + 1
data_field_size <= SPP_MAX_PAYLOAD_CHUNK
buffer_len == SPP_PRIMARY_HEADER_LEN + data_field_size
```

If trailing bytes are allowed, document the policy explicitly and keep them out of command dispatch.

## APID Policy

Every APID should have a policy table.

| APID | Direction | Minimum Payload | Maximum Payload | Auth Required | Mode Requirement |
| --- | --- | --- | --- | --- | --- |
| `0x01` PING | TC/TM | 0 | Small | Optional or low | Any mode |
| `0x02` RESET | TC | 0 | 0 | Required | Maintenance or safe mode |
| `0x03` SEND_FW | TC/TM | 0 | 0 | Required | Any authorized mode |
| `0x04` SET_THRUSTER | TC | 2 | 2 | Required | Simulation or actuator-safe mode |
| `0x05` SET_BEACON_RATE | TC | 1 | 1 | Required | Any authorized mode |
| `0x06` BROADCAST_MSG | TC/TM | 2 | Bounded | Required | Communications maintenance |
| `0x07` FLASH | TC/TM | 0 | Bounded | Required | Transfer mode |
| `0x08` SEND_TM | TM | Fixed | Fixed | N/A | Any mode |

The dispatcher should check this table before entering a handler.

## Authentication and Integrity

For an educational board, a simple message authentication code is enough to teach the design. For mission systems, key management, operational procedures, and hardware constraints must be engineered carefully.

Required properties:

- The receiver can verify the sender.
- The packet cannot be modified without detection.
- Old packets cannot be replayed.
- High-impact APIDs require stronger authorization.

Possible design pattern:

```text
SPP Primary Header
Command Metadata
  - spacecraft ID
  - command counter
  - timestamp or nonce
  - APID policy flags
Payload
Authentication Tag
```

The authentication tag should cover the header fields that affect dispatch, not only the payload.

## Replay Protection

Sequence counters in the SPP header are not enough unless the firmware enforces them.

Replay defenses:

- Maintain the last accepted command counter per APID or session.
- Reject counters that move backward.
- Reject duplicates.
- Expire commands after a short validity window.
- Bind counters to authenticated sessions.

For intermittent satellite links, replay policy must tolerate packet loss without allowing unlimited reuse.

## Command Rate Limits

Rate limits reduce denial-of-service impact.

| Command | Suggested Control |
| --- | --- |
| RESET | Cooldown, confirmation, and authorization. |
| BEACON_RATE | Minimum interval and change-rate limit. |
| FLASH | Transfer quota and explicit transfer state. |
| BROADCAST_MSG | Frequency allowlist, duration limit, payload limit. |
| SET_THRUSTER | Mode gate, range limit, and command audit. |

Rate limits should fail closed. If the firmware cannot decide whether a command is safe, it should reject it.

## Telemetry Hardening

Telemetry should be trustworthy enough for operators to make decisions.

Controls:

- Add sensor validity flags.
- Report sensor read failures explicitly.
- Clamp impossible values.
- Detect sudden jumps.
- Include sequence counters.
- Add integrity protection.
- Include command acceptance/rejection events.

For Pwnsat, `bmeRead()` and `accelerometerRead()` return status, but the telemetry worker does not use that status to mark telemetry invalid. That is a useful hardening exercise.

## RF Hardening

RF cannot be assumed private.

Controls:

- Encrypt sensitive telemetry.
- Authenticate telecommands.
- Monitor RSSI and SNR anomalies.
- Detect repeated failed command authentication.
- Use directional antennas where appropriate.
- Plan degraded modes for link loss.
- Avoid arbitrary retune commands unless strongly authorized.

Jamming cannot always be prevented, so mission design must include detection and recovery.

## Secure Debug and Build Artifacts

Debug access is valuable in the lab and dangerous in deployment.

Deployment controls:

- Disable or lock debug interfaces.
- Protect firmware readout where supported.
- Avoid shipping unnecessary symbols.
- Sign firmware images.
- Keep build artifacts out of public release packages unless intentionally published.
- Separate educational builds from hardened builds.

Open-source design is compatible with security, but only when the system does not depend on secrecy for command authorization.

## Hardening Checklist

Use this checklist after every vulnerability:

- Is every length checked before copy?
- Is every APID authorized before dispatch?
- Are TC-only and TM-only directions enforced?
- Are reset and actuator commands protected?
- Are command counters enforced?
- Are telemetry values marked valid or invalid?
- Is RF input authenticated?
- Is sensitive telemetry encrypted or integrity-protected?
- Are debug ports locked in deployed configurations?
- Are rate limits present for expensive commands?

Hardening is not a patch at the end. It is the design discipline that keeps small parser mistakes from becoming mission failures.

## Booklet Exercise: Convert Findings Into Controls

Open [Booklet.ipynb](Booklet.ipynb) and complete **Part 4: Firmware Review Exercises**, **Part 5: Fuzzing**, **Part 6: SpaceCAN Bus Offline Exercises**, and **Part 7: Final Lab Report Template**.

For each finding, write:

- The vulnerable firmware function.
- The packet or capture evidence.
- The SPARTA mapping.
- The security impact.
- The recommended mitigation.

This turns the notebook from a parsing exercise into an engineering report.
