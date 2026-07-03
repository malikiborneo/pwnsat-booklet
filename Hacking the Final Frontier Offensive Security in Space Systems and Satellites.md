# Hacking the Final Frontier

## Offensive Security in Space Systems and Satellites

This book is a practical, technical guide to offensive security research against a vulnerable-by-design FlatSat platform known as **Pwnsat**. The platform models the core parts of a small satellite mission: an on-board computer, radio links, telemetry, telecommands, sensors, packet routing, and mission-specific firmware logic.

The goal is not to teach attacks against operational spacecraft. The goal is to give students, researchers, and engineers a controlled laboratory where they can learn how satellite systems fail, how those failures are discovered, how protocol and firmware weaknesses are exploited, and how the same findings can be translated into better engineering and defensive controls.

## Platform Summary

The Pwnsat/FlatSat board is a vulnerable educational target built around a compact embedded architecture:

| Area | Component | Security Relevance |
| --- | --- | --- |
| On-Board Computer | Raspberry Pi RP2040, dual-core ARM Cortex-M0+ | Runs the flight software and packet-processing logic. |
| Radio Link | Dual SX1262 LoRa radios | Separates uplink telecommands from downlink telemetry. |
| Local Control | USB CDC bridge | Provides a high-speed command and debugging path. |
| Sensors | BME280 and LIS2DH12 | Provide environmental and motion telemetry. |
| Internal Buses | SPI and I2C | Expose useful hardware reconnaissance and spoofing surfaces. |
| Protocol | CCSDS Space Packet Protocol-inspired framing | Routes commands and telemetry by APID. |

## Key Vulnerability Themes

This manuscript treats the board as a complete mission system rather than a single embedded target. The main weakness classes are:

- **Unauthenticated telecommands:** the uplink accepts commands without proving the identity or authority of the sender.
- **Cleartext radio traffic:** telemetry and telecommands can be observed and replayed in a lab RF environment.
- **Protocol parser weaknesses:** malformed Space Packet Protocol frames can stress length parsing, APID dispatch, and payload handling.
- **Unsafe command handlers:** high-impact actions such as reset or actuator simulation are reachable through simple packet construction.
- **Exposed debug and data buses:** UART, SPI, I2C, SWD, and test pads provide hardware-level visibility into the system.
- **Open-source intelligence leakage:** public schematics, firmware, and build artifacts reduce the cost of reversing.

## Reading Path

The book is organized as a progressive attack chain. Each chapter should stand on its own, but the strongest learning path is linear:

1. [Space Fundamentals and System Architecture](Space%20Fundamentals%20and%20System%20Architecture.md)
2. [SPARTA Framework](SPARTA%20Framework.md)
3. [Phase 1 Discovery](Phase%201%20Discovery.md)
4. [Phase 1 Blind Reconnaissance](Phase%201%20Blind%20Reconnaissance.md)
5. [Phase 1 Assisted Analysis](Phase%201%20Assisted%20Analysis.md)
6. [Phase 2 Protocol Analysis: Space Packet Protocol](Phase%202%20Protocol%20Analysis%20%28Space%20Packet%20Protocol%29.md)
7. [Phase 3 RF Communications and Attack Surface](Phase%203%20RF%20Communications%20and%20Attack%20Surface.md)
8. [Phase 4 Exploitation](Phase%204%20Exploitation.md)
9. [Phase 5 Exploit Reliability and Firmware Reversing](Phase%205%20Exploit%20Reliability%20and%20Firmware%20Reversing.md)
10. [Phase 6 Defensive Engineering and Hardening](Phase%206%20Defensive%20Engineering%20and%20Hardening.md)
11. [Conclusion](Conclusion.md)
12. [Appendix A: Lab Setup and Safety](Appendix%20A%20Lab%20Setup%20and%20Safety.md)
13. [Appendix B: APID and Packet Reference](Appendix%20B%20APID%20and%20Packet%20Reference.md)
14. [Appendix C: Glossary](Appendix%20C%20Glossary.md)

## Companion Exercise Booklet

The hands-on exercises are collected in [Booklet.ipynb](Booklet.ipynb). The notebook is designed to work with public example files so readers can practice even without the physical board, a logic analyzer, or RF equipment.

The booklet includes exercises for:

- Parsing exported I2C logic analyzer captures.
- Building I2C register maps.
- Decoding Space Packet Protocol frames.
- Constructing safe telecommand payloads.
- Comparing raw SPP bytes, USB-framed payloads, and RF ASCII-hex payloads.
- Running offline SPP fuzzing exercises with libFuzzer, sanitizers, corpus files, and crash triage.
- Practicing offline SpaceCAN bus decoding, replay reasoning, and fragmentation analysis.
- Mapping firmware findings to SPARTA.

Required notebook dependencies are listed in [requirements-booklet.txt](requirements-booklet.txt). Helper scripts live in [scripts/i2c_parser.py](scripts/i2c_parser.py) and [scripts/spp_tools.py](scripts/spp_tools.py). The fuzzing exercises use the C harnesses under [resources/fuzzing](resources/fuzzing).

## Lab Safety and Scope

All examples in this book assume an isolated educational FlatSat, local hardware access, and frequencies/power levels permitted for the test environment. Do not transmit against real spacecraft, third-party ground stations, public satellite services, or radio systems you do not own or have explicit authorization to test.

The Pwnsat board is intentionally vulnerable so that dangerous patterns can be studied safely before they appear in real systems.
