# SPARTA Mapping

This document maps PwnSat / FlatSat technical findings to SPARTA-style space cybersecurity tactics and techniques.

The mapping is used for thesis structure. It should not be treated as proof of impact by itself. Each mapping must be supported by lab evidence, source-code evidence, packet evidence, telemetry evidence, or experiment logs.

---

## Mapping Method

Use this process for each finding:

```text
technical behavior
  -> affected trust boundary
  -> attack-chain step
  -> SPARTA mapping
  -> defensive control
  -> measurable result
```

Example:

```text
Unauthenticated command accepted
  -> command authority boundary crossed
  -> rogue command reaches APID handler
  -> IA-0008.01 / EX-0001.01
  -> command authentication + APID policy
  -> unauthorized command rejection rate
```

---

## Summary Mapping Table

| Finding | Attack-Chain Role | Candidate SPARTA Mapping | Defensive Control |
|---|---|---|---|
| Public firmware and design information | Reconnaissance | REC-0001.01 Software Design; REC-0001.02 Firmware | Secure design review; avoid security by obscurity |
| Hardware and bus discovery | Reconnaissance | REC-0001.04 Data Bus Information | Debug locking; telemetry validation; bus monitoring |
| RF parameter discovery | Reconnaissance | REC-0003.01 Communications Equipment; REC-0003.03 Mission-Specific Channel Scanning | RF monitoring; avoid relying on hidden parameters |
| Cleartext downlink telemetry | Exfiltration / reconnaissance | REC-0005.02 Downlink Intercept; EXF-0003.02 Downlink Exfiltration | Telemetry integrity and encryption |
| Uplink command observation | Reconnaissance / replay preparation | REC-0005.01 Uplink Intercept Eavesdropping; EXF-0003.01 Uplink Exfiltration | Command authentication; anti-replay |
| Rogue command source | Initial access | IA-0008.01 Rogue Ground Station | Authentication and source validation |
| Command reaches APID dispatcher | Execution | EX-0001.01 Command Packets | APID authorization; TC/TM direction enforcement |
| Malformed packet accepted by parser | Execution / erroneous input | EX-0013.02 Erroneous Input | Bounds-checked parsing |
| Reset command abuse | Service disruption | EX-0001.01 Command Packets; DE-0002.03 Inhibit Spacecraft Functionality | Reset authorization and cooldown |
| Beacon-rate abuse | Service degradation | EX-0013.01 Valid Commands; DE-0002.03 Inhibit Spacecraft Functionality | Rate limits; minimum interval |
| Flash-transfer abuse | Exfiltration / service degradation | EXF-0003.02 Downlink Exfiltration; DE-0002.03 Inhibit Spacecraft Functionality | Transfer quota; non-blocking transfer |
| Broadcast command retune | Unauthorized RF reconfiguration | EX-0001.01 Command Packets; IMP-0002 Disruption | Frequency allowlist; mode gate |
| Thruster state manipulation | Mission-state manipulation | EX-0001.01 Command Packets; EX-0012.07 Propulsion Subsystem | Actuator authorization; safe-mode policy |
| Sensor/I2C telemetry manipulation | Internal data trust | REC-0001.04 Data Bus Information; EX-0014.02 Bus Traffic Spoofing; EX-0014.03 Sensor Data | Plausibility checks; validity flags |
| Uplink/downlink availability loss | Denial / impact | DE-0002.02 Jam Link Signal; IMP-0002 Disruption; IMP-0003 Denial | Link monitoring; degraded-mode operations |

---

## Attack Flow 1: Unauthorized Command Execution

```text
Discover command format
  -> build valid SPP telecommand
  -> deliver through USB or controlled lab RF
  -> command reaches parser
  -> APID dispatcher executes handler
  -> mission state changes
```

Candidate SPARTA mapping:

- REC-0003.02 Commanding Details
- IA-0008.01 Rogue Ground Station
- EX-0001.01 Command Packets
- IMP-0002 Disruption, depending on effect

Defensive controls:

- command authentication,
- APID authorization,
- direction enforcement,
- command audit telemetry.

Metrics:

- command acceptance rate,
- unauthorized command rejection rate,
- state-change success or failure,
- audit visibility.

---

## Attack Flow 2: Malformed Packet Parser Failure

```text
Identify SPP header fields
  -> mutate length field
  -> send truncated or inconsistent packet
  -> parser copies based on declared length
  -> crash, unsafe read, or unexpected handler behavior
```

Candidate SPARTA mapping:

- EX-0013.02 Erroneous Input
- EX-0001.01 Command Packets, if command-like packet reaches dispatch
- IMP-0003 Denial, if the effect removes availability

Defensive controls:

- strict packet length validation,
- reject truncated packets,
- reject impossible payload sizes,
- fuzz parser before deployment.

Metrics:

- malformed packet rejection rate,
- crash count,
- handler reachability from malformed packets,
- false rejection rate for valid packets.

---

## Attack Flow 3: Service Disruption Through Valid Commands

```text
Build syntactically valid command
  -> send command to high-impact APID
  -> trigger reset, beacon flood, flash transfer, or broadcast behavior
  -> degrade telemetry or command responsiveness
```

Candidate SPARTA mapping:

- EX-0001.01 Command Packets
- EX-0013.01 Valid Commands
- DE-0002.03 Inhibit Spacecraft Functionality
- IMP-0002 Disruption
- IMP-0003 Denial

Defensive controls:

- rate limiting,
- mode-gated commands,
- reset cooldown,
- transfer quota,
- safe-mode policy.

Metrics:

- disruption duration,
- telemetry loss interval,
- recovery time,
- rejected high-impact command count.

---

## Attack Flow 4: Telemetry Trust and Sensor Data Path

```text
Observe sensor bus
  -> correlate I2C reads with telemetry
  -> change or disrupt sensor data in controlled lab condition
  -> telemetry reflects manipulated or invalid state
  -> operator visibility is affected
```

Candidate SPARTA mapping:

- REC-0001.04 Data Bus Information
- EX-0014.02 Bus Traffic Spoofing
- EX-0014.03 Sensor Data
- IMP-0002 Disruption, if operator decisions are affected

Defensive controls:

- sensor validity flags,
- range checks,
- sudden-jump detection,
- redundant sensing where appropriate,
- telemetry integrity protection.

Metrics:

- detection time,
- invalid telemetry marking rate,
- telemetry correctness,
- operator-visible anomaly coverage.

---

## Claim Discipline

SPARTA mapping does not automatically prove severity. Each mapped item needs evidence.

Use these claim levels:

| Claim | Evidence Needed |
|---|---|
| Mapped risk | Source code, packet format, or architecture supports the path. |
| Reachable behavior | Command or packet reaches the relevant handler. |
| Demonstrated impact | Logs, telemetry, reset, timing disruption, or state change observed. |
| Reliable impact | Repeated successful reproduction across trials. |
| Controlled exploitation | Debugger evidence shows controlled fault or execution influence. |

---

## Thesis Use

This file should support:

- thesis threat model,
- Attack Flow diagrams,
- SPARTA mapping table,
- experiment design,
- result interpretation,
- defensive-control discussion.