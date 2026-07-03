# SPARTA Framework Mapping

[SPARTA](https://sparta.aerospace.org/) is a space-focused adversary tactics, techniques, and procedures framework. It gives spacecraft operators and security researchers a common vocabulary for describing how a spacecraft or mission system may be compromised through cyber, physical, supply-chain, or counterspace activity.

In this book, SPARTA is used as a map. It does not replace hands-on testing, but it helps connect each Pwnsat weakness to a real spacecraft security concept.

## Why SPARTA Matters for Pwnsat

Pwnsat is intentionally vulnerable, but its design mirrors patterns found in real missions:

- Public design data can reveal system architecture.
- Firmware can expose command handlers and packet formats.
- Cleartext RF links can leak operational details.
- Weak command authentication can permit unauthorized control.
- Unsafe parsing can turn telemetry or telecommands into memory corruption.

Using SPARTA keeps the lab from becoming a collection of isolated tricks. Each exercise becomes part of a larger spacecraft attack chain.

## SPARTA Mapping
![SPARTA General TTPs](static/Pwnsat%20-%20SPARTA%20TTPs.png)

## Vulnerability Assessment

| Asset | Location or Source | Security Weakness |
| --- | --- | --- |
| Hardware design | Public FlatSat design material | Board layout, interfaces, and components can be studied before touching the target. |
| Firmware source | Public firmware repository | Command handlers, APIDs, frequencies, and parsing logic can be reviewed directly. |
| Firmware artifacts | `firmware.elf`, `firmware.bin`, or build outputs | Symbols, memory layout, and functions may simplify reversing. |
| Radio link | Uplink and downlink LoRa channels | No strong authentication or encryption in the lab model. |
| Debug interfaces | Headers, test pads, SWD/UART candidates | Physical access may allow firmware extraction or live debugging. |
| Internal buses | SPI and I2C | Boot traffic, sensors, and radio configuration can be observed. |

## Firmware-Validated Findings

The firmware confirms the major attack surfaces used throughout the book.

| Finding | Firmware Evidence | SPARTA Interpretation |
| --- | --- | --- |
| Fixed uplink parameters | `ruplink.h` defines 918 MHz, 250 kHz bandwidth, SF7, CR5. | Reconnaissance and mission-specific channel scanning. |
| Fixed downlink parameters | `rdownlink.h` defines 916 MHz, 250 kHz bandwidth, SF7, CR5. | Downlink interception and exfiltration. |
| No RF authentication | `uplinkRadioCheckPacketReceived()` forwards decoded bytes directly to `commandHandler()`. | Rogue Ground Station and malicious command packets. |
| No RF encryption | Telemetry packets are built as plaintext SPP frames and sent with `downlinkRadioTransmit*()`. | Downlink intercept and downlink exfiltration. |
| SPP parser trusts declared length | `spp_unpack_packet()` copies `header.length + 1` bytes without verifying `buffer_len >= 6 + length + 1`. | Parser design flaw and memory-corruption primitive. |
| Unauthenticated reset | APID `0x02` calls `watchdog_reboot()`. | Malicious command packet causing denial of service. |
| Beacon-rate abuse | APID `0x05` accepts `0` seconds, creating continuous beacon transmission. | Command abuse and service degradation. |
| Broadcast underflow | APID `0x06` computes `msg_len = payload_total - 2` without first requiring a two-byte frequency field. | Integer underflow leading to unsafe copy and potential control-flow corruption. |
| Arbitrary broadcast frequency attempt | APID `0x06` uses packet-controlled frequency in `downlinkRadioTransmitBroadcast()`. | Unauthorized RF reconfiguration in the lab environment. |
| Sensor telemetry trust | `bmeRead()` and `accelerometerRead()` feed telemetry without plausibility or authenticity checks. | Sensor Data spoofing or Bus Traffic Spoofing through local bus manipulation. |
| Link availability dependency | The mission loop depends on successful RF command and telemetry paths. | Jam Link Signal and downlink disruption scenarios. |

## ST0001 - Reconnaissance

![SPARTA TTPs Reconnaissance](static/Pwnsat%20-%20Assisted%20Analysis.png)

Reconnaissance covers the information-gathering activities that help an operator understand the target before attempting access.

| SPARTA Technique | Pwnsat Example | Objective|
| --- | --- | --- |
| REC-0001.01 Software Design | Reviewing firmware architecture, task layout, and APID dispatch. | Reverse engineer command parsing, locate debug hooks, bypass fault-recovery logic, and build high-fidelity emulators for mission rehearsal. |
| REC-0001.02 Firmware | Studying binaries, ELF symbols, or build artifacts. | Map trust boundaries and hardware choke points (like watchdogs or power controllers) to prepare malicious updates, exploit unsigned images, or force firmware downgrades. |
| REC-0001.04 Data Bus Information | Identifying I2C, SPI, UART, and SWD on the board. | Enumerate bridges and gateways to craft frames that collide with or supersede legitimate traffic, starve health monitoring, or disrupt payload systems. |
| REC-0003.01 Communications Equipment | Identifying radios and modulation. | Characterize signal parameters to build compatible Software Defined Radio (SDR) pipelines and exploit hardware limits (like AGC or power budgets) to induce non-linear disruption. |
| REC-0003.02 Commanding Details | Finding telecommand formats and handlers. | Craft syntactically valid command traffic and time injections to bypass authentication controls or induce counter/timetag desynchronization. |
| REC-0003.03 Mission-Specific Channel Scanning | Determining uplink/downlink frequencies. | Characterize access schemes (TDMA/FDMA/CDMA) and user terminal waveforms to selectively jam, impersonate, or pivot between distinct organizational enclaves. |
| REC-0005.01 Uplink Intercept Eavesdropping | Capturing telecommands. | Capture telecommand framing, authentication fields, emission designators, and preambles to build accurate SDR injection pipelines and map operational maintenance windows. |
| REC-0005.02 Downlink Intercept | Capturing telemetry. | Analyze system states, mode transitions, and operational margins to refine target timing and build mission testbeds, even when primary payload content is encrypted. |
| REC-0006.01 Development Environment | Compile the code. | Identify policy gaps (e.g., unreviewed code paths), embedded secrets, and permissive compiler flags to compromise the build pipeline or reconstruct high-fidelity testbeds using debug metadata. |

## ST0002 - Resource Development

![SPARTA TTPs Resource Development](static/Pwnsat%20-%20SPARTA%20TTPs%20-%20RD.png)

Resource development is the preparation of tools and infrastructure before active operations.

| SPARTA Technique | Pwnsat Example | Objective|
| --- | --- | --- |
| RD-0002.01 Ground Station Equipment | Constructing a rogue, independent RF ground stack. | Replicate mission waveforms and framing to passively collect data, actively probe infrastructure, or execute spoofing attacks against weakly authenticated links. |
| RD-0002.03 Spacecraft | Use the Pwnsat Flatsat. | Conduct short-range spectrum measurements, test spoofing/denial techniques, or exploit weak segmentation in rideshare environments. |


For this book, resource development includes Python decoders, packet builders, RF capture workflows, firmware analysis scripts, and repeatable test harnesses.

## ST0003 - Initial Access

![SPARTA TTPs Initial Access](static/Pwnsat%20-%20SPARTA%20TTPs%20-%20IA.png)

Initial access is the first successful path into the target's operational control surface.

| SPARTA Technique | Pwnsat Example | Objective|
| --- | --- | --- |
| IA-0008.01 Rogue Ground Station | Sending an unauthorized telecommand from lab RF equipment that imitates the expected uplink. | Generate and transmit over-the-air signals that perfectly match the target mission's specific bands, modulation, and framing parameters to execute spoofing or protocol-level manipulation. |
| IA-0007.02 Malicious Command via Ground Station | Sending a malicious command through a legitimate or compromised ground-station path. | Insert malicious scripts or procedures into existing timelines, modify operational limits, and leverage standard downlink channels for data exfiltration, hiding the attack under legitimate command authority. |

On Pwnsat, initial access is often protocol-level rather than shell-level. If the board accepts a forged telecommand, the attacker has crossed the command authority boundary.

## ST0004 - Execution

![SPARTA TTPs Execution](static/Pwnsat%20-%20SPARTA%20TTPs%20-%20EX.png)

Execution covers unauthorized commands or code running on the spacecraft bus.

| SPARTA Technique | Pwnsat Example | Objective|
| --- | --- | --- |
| EX-0001.01 Command Packets | Resending authentic telecommand Protocol Data Units (PDUs) with intact framing, CRCs, counters, or timetags captured from prior exchanges. | Re-trigger specific operational actions (e.g., mode changes), map vehicle reactions at different states, or saturate queues to crowd out legitimate traffic. |
| EX-0001.02 Bus Traffic Replay | Tampering with device firmware, programmable logic (FPGA bitstreams), configuration blobs, or MCU/SoC boot ROM fallbacks. | Consume available bus bandwidth, starve critical publishers, force repetitive subsystem actions, or precisely time injections to collide with and supersede legitimate messages on scheduled buses. |
| EX-0005.02 Malicious Use of Hardware Commands | Issuing low-level device, register, or maintenance commands directly to hardware components over the internal bus. | Bypass high-level command mediation to over-drive mechanisms, disable hardware watchdogs, alter calibration parameters, or manipulate critical power domains. |
| EX-0012.05 Scheduling Algorithm | Tampering with real-time scheduling parameters, task priorities, CPU budgets, deadlines, and clock sources. | Weaponize execution time to introduce high-rate control loop jitter, starve critical command/telemetry handling, and induce hard-to-debug, state-dependent malfunctions. |
| EX-0012.06 Science/Payload Data | Modifying raw detector frames, Level-0 data streams, mass memory file catalogs, or adjacent metadata (timestamps, calibration tables). | Degrade mission value or mislead end-users by forcing ground data pipelines to silently misclassify or discard corrupted scientific payloads. |
| EX-0012.07 Propulsion Subsystem | Editing thruster calibrations, valve timings, inhibit masks, delta-V tables, and tank pressure/temperature safety limits. | Provoke thruster over-correction, waste finite propellant through continuous trims, trigger false autonomous lockouts, or induce off-axis attitude excursions. |
| EX-0012.10 Command & Data Handling Subsystem | Adjusting runtime variables such as opcode-to-handler maps, command queue depths, message routing tables, and event/telemetry filters. | Intercept and reshape logical workflows by dropping or misrouting commands, suppressing vital telemetry, and confusing ground tracking processors. |
| EX-0013.01 Valid Commands | Saturating data paths with an excessive volume of legitimate but low-risk telecommands or bus messages (e.g., no-ops, time queries). | Exhaust CPU cycles, fill command queues, and trigger continuous downstream acknowledgments to delay authentic operations and induce transient loss of control. |
| EX-0013.02 Erroneous Input | Injecting volumetric invalid data—such as wideband noise, malformed packets, or frames with bad CRCs—into receivers and parsers. | Force front-end decoders and parsers into constant validate-and-deny cycles, crowding out real work and driving up system error loads. |
| EX-0014.02 Bus Traffic Spoofing | Emitting forged messages with valid identifiers, addresses, and timing parameters directly onto internal vehicle data paths (MIL-STD-1553, SpaceWire, CAN). | Mask real hardware publishers to make subscribers accept unauthorized actuator setpoints, power toggles, or telemetry states. |
| EX-0016.01 Uplink Jamming | Transmitting RF interference toward the spacecraft's receive antenna to match its frequency, footprint, polarization, and Doppler conditions. | Drive the uplink signal-to-noise ratio below the demodulator threshold to completely block or delay critical telecommands and ranging traffic. |
| EX-0016.02 Downlink Jamming | Creating RF noise in the same frequency band as the satellite's downlink signal, targeting the field of view of ground receiving terminals. | Blind ground users and receivers, often requiring air/space platforms to intercept directional ground stations, or utilizing ground assets to disrupt vulnerable omnidirectional antennas (like GNSS). |

Execution in this lab should always be performed against the local Pwnsat board or emulator, never against third-party radio systems.

## ST0006 - Defense Evasion and Denial

![SPARTA TTPs Defense Evasion and Denial](static/Pwnsat%20-%20SPARTA%20TTPs%20-%20DE.png)

Some Pwnsat behaviors are better described as service degradation than code execution.

| SPARTA Technique | Pwnsat Example | Objective|
| --- | --- | --- |
| DE-0002.02 Jam Link Signal | Overwhelming or jamming the downlink radio frequency signal to block transmitted telemetry from reaching its ground destination. | Leave ground controllers completely unaware of real-time vehicle status, preventing them from deploying critical stability and safety mitigations. |
| DE-0002.03 Inhibit Spacecraft Functionality | Suppressing telemetry directly at the source by manipulating on-board software generation or transmission hardware. | Disable telemetry publishers, mute event channels, or adjust packet filters to hide unauthorized actions while the spacecraft continues operating. |


## ST0008 - Exfiltration

![SPARTA TTPs Defense Evasion and Denial](static/Pwnsat%20-%20SPARTA%20TTPs%20-%20EXF.png)

Exfiltration is the unauthorized removal of mission data.

| SPARTA Technique | Pwnsat Example | Objective|
| --- | --- | --- |
| EXF-0001 Replay | Re-sending previously valid commands or procedures to force the spacecraft to re-transmit recorded data. | Induce legitimate-looking data dumps (recorder playbacks, file directories) timed to align perfectly with actor-controlled reception windows. |
| EXF-0002.01 Power Analysis Attacks | Measuring the instantaneous power consumption of hardware devices like crypto engines or microcontrollers. | Correlate tiny, data-dependent power fluctuations (using SPA/DPA) to map operational sequences or extract cryptographic key bits. |
| EXF-0003.02 Downlink Exfiltration | Capturing cleartext downlink telemetry. | Demonstrates confidentiality failure on the RF link. |
| EXF-0003.01 Uplink Exfiltration | Capturing cleartext uplink telecommands or command-like traffic. | Captured command traffic can support replay, protocol reconstruction, and later intrusion attempts. |
| EXF-0007 Compromised Ground System | Leveraging a foothold within trusted mission ground infrastructure (workstations, control servers, or archive databases) to siphon data. | Mirror real-time streams, export payload products, and harvest command histories silently by abusing authorized data dissemination pathways. |

## ST0009 - Impact

![SPARTA TTPs Defense Evasion and Denial](static/Pwnsat%20-%20SPARTA%20TTPs%20-%20IMP.png)

Threat actor is trying to manipulate, interrupt, or destroy the space system(s) and/or data.

| SPARTA Technique | Pwnsat Example | Objective|
| --- | --- | --- |
| IMP-0002 Disruption | Temporarily impairing, altering, or manipulating communication paths and messages between the spacecraft and ground controllers. | Cause data loss, delay critical operational actions, or corrupt message integrity to jeopardize the spacecraft's immediate purpose. |
| IMP-0003 Denial | Temporarily eliminating complete access, use, or operation of a system without causing permanent physical hardware damage. | Block communications entirely, exhaust processing resources, or degrade subsystems to completely lock ground controllers out of the spacecraft. |

## RF-Specific TTP Notes

The RF chapter introduces attacks that are not always tied to a firmware bug. They map to SPARTA differently depending on the objective:

| RF Activity | Primary SPARTA Mapping | Notes |
| --- | --- | --- |
| Passive downlink capture | `REC-0005.02 Downlink Intercept`, then `EXF-0003.02 Downlink Exfiltration` | Reconnaissance becomes exfiltration when mission data is collected and reconstructed. |
| Passive uplink capture | `REC-0005.01 Uplink Intercept Eavesdropping`, then `EXF-0003.01 Uplink Exfiltration` | Useful for protocol learning, replay analysis, and command cadence study. |
| Rogue command transmission | `IA-0008.01 Rogue Ground Station`, `EX-0001.01 Command Packets` | Applies when the attacker does not control a legitimate ground station. |
| Link jamming | `DE-0002.02 Jam Link Signal` | Availability attack against telemetry or command links. |
| RF spoofing | `IA-0008.01 Rogue Ground Station` or `EX-0014` | Initial-access mapping fits forged command links; spoofing mapping fits forged data treated as truth. |

## Fuzzing-Specific Mapping Notes

Fuzzing is a validation method, not a SPARTA tactic. The technique depends on what the fuzzed input proves.

| Fuzzing Result | Primary SPARTA Mapping | Notes |
| --- | --- | --- |
| Malformed packet stresses parser validation | `EX-0013.02 Erroneous Input` | Use when the input is invalid, malformed, truncated, oversized, or inconsistent. |
| Unauthorized telecommand reaches a handler | `EX-0001.01 Command Packets` | Use when the packet is accepted as a command and causes command-path behavior. |
| Fuzz case causes repeated lockup or reboot | `DE-0002.03 Inhibit Spacecraft Functionality` | Use when the spacecraft-side function is degraded or suppressed. |
| Fuzz case eliminates access or operation in the lab model | `IMP-0003 Denial` | Use for complete loss of availability, not for minor parsing errors. |
| RF delivery of a fuzz-discovered command | `IA-0008.01 Rogue Ground Station` | Use only when the command is transmitted by an unauthorized lab RF stack. |

## Defensive Lessons

Each offensive finding should produce a defensive requirement:

| Finding | Engineering Control |
| --- | --- |
| Cleartext RF traffic | Encrypt sensitive command and telemetry data where mission constraints allow. |
| Unauthenticated commands | Add command authentication, authorization, and replay protection. |
| Unsafe packet lengths | Validate all length fields before allocation, copy, or dispatch. |
| Exposed debug ports | Disable or protect debug access in deployed configurations. |
| Public firmware symbols | Treat public artifacts as adversary-visible and reduce unnecessary leakage. |
| Sensor spoofing | Authenticate critical sensor data where feasible and add plausibility checks. |

SPARTA gives the language; Pwnsat gives the hands-on lab.
