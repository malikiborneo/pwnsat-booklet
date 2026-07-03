# Space Fundamentals and System Architecture

Before attacking a satellite-like platform, you need to understand what the platform is trying to imitate. A spacecraft is not just an embedded board in orbit. It is part of a mission system that includes radios, operators, ground stations, packet formats, time constraints, autonomy, sensors, and physical limits.

Pwnsat compresses that environment into a laboratory FlatSat. The board is intentionally accessible, but the security lessons map to real spacecraft engineering patterns: command authority, telemetry trust, bus exposure, safe-mode behavior, packet parsing, and mission operations.

## Orbital Mechanics as an Attack Constraint

Orbital mechanics defines when a spacecraft can communicate, how long a contact window lasts, and what an attacker or operator can realistically do during that window.

| Orbit Type | Altitude Range | Operational Behavior | Security Implication |
| --- | --- | --- | --- |
| LEO, Low Earth Orbit | 160-2,000 km | Short passes over a ground station, often around 10-15 minutes. | Attacks must be prepared before contact and executed quickly. Doppler shift matters for RF work. |
| SSO, Sun-Synchronous Orbit | 600-800 km typical | Predictable passes at similar local solar times. | Predictability helps both operators and adversaries plan observation windows. |
| MEO, Medium Earth Orbit | 2,000-35,786 km | Longer visibility than LEO, higher path loss. | Requires more capable RF infrastructure and planning. |
| GEO, Geostationary Orbit | 35,786 km | Appears fixed relative to Earth. | Persistent visibility can simplify monitoring, jamming, or command attempts. |

Pwnsat does not orbit, but the same concept appears in the lab as **access windows**. You might only have the board powered during a workshop, only have a few minutes of RF capture, or only have one chance to observe boot-time bus traffic. Treat every capture as a pass.

## Mission Segments

A space system is usually described through segments. Each segment introduces different trust boundaries and attack surfaces.

![Space segments](static/Space_Segments.png)

## Space Segment

The space segment contains the spacecraft or satellites that execute the mission. In a constellation, spacecraft may communicate with one another through inter-satellite links, share state, relay telemetry, or coordinate positioning.

In a real mission, the space segment includes:

- The spacecraft bus
- Payloads
- TT&C radios
- On-board computers
- Sensors and actuators
- Flight software
- Inter-satellite links, when present

In Pwnsat, the space segment is represented by the FlatSat board itself: RP2040, radios, sensors, firmware, and packet-processing logic.

> A satellite is a human-made spacecraft intentionally placed into orbit around another body. Every satellite is a spacecraft, but not every spacecraft is a satellite.

## Ground Segment

The ground segment contains the infrastructure used to operate the mission from Earth:

- Mission Operations Center, or MOC
- Ground stations
- Operator consoles
- Data processing systems
- Scheduling systems
- Command generation tools
- Telemetry storage and monitoring

The ground segment is where commands are prepared, validated, transmitted, and audited. It is also where telemetry is received and interpreted. If the ground segment trusts unauthenticated telemetry, an attacker can potentially influence operator decisions without touching the spacecraft directly.

In Pwnsat, a laptop, USB connection, LoRa transceiver, or software command tool can act as a simplified ground segment.

## User Segment

The user segment contains the people, systems, or devices that consume the mission output:

- GNSS receivers
- Satellite phones
- Satellite internet terminals
- Weather data users
- Earth observation processing pipelines
- Science teams

Security failures can cross into the user segment when corrupted telemetry, manipulated payload data, or forged status information reaches downstream users.

## Core Satellite Subsystems

![Space segments](static/Cubesat_subsystems.png)

Most spacecraft can be understood as a collection of subsystems. Pwnsat does not implement every subsystem physically, but it borrows their command and telemetry patterns.

| Subsystem | Purpose | Pwnsat Analogy |
| --- | --- | --- |
| ADCS, Attitude Determination and Control | Determines and controls spacecraft orientation. | Simulated through motion/IMU data and command handlers. |
| C&DH, Command and Data Handling | Processes commands and routes telemetry/payload data. | RP2040 firmware, APID dispatch, USB CDC, packet parser. |
| EPS, Electrical Power System | Generates, stores, and distributes power. | Board power rails, USB power, reset behavior. |
| Propulsion | Performs orbit maintenance or maneuvers. | Simulated thruster APID and actuator-style commands. |
| Structures and Mechanisms | Physical support, deployment, and mechanical systems. | Board layout, connectors, headers, payload interface. |
| TT&C, Telemetry, Tracking, and Command | Sends telemetry and receives commands. | SX1262 uplink/downlink and Space Packet Protocol frames. |
| Thermal Control | Maintains operating temperature. | BME280 environmental telemetry and health monitoring. |

## Attitude Determination and Control

ADCS controls where a spacecraft points. A satellite may need to point solar panels toward the Sun, antennas toward Earth, or payloads toward a target.

Typical ADCS sensors include:

- Star trackers
- Magnetometers
- Gyroscopes
- Sun sensors

Typical actuators include:

- Reaction wheels
- Magnetorquers
- Thrusters

From a security perspective, ADCS is sensitive because false sensor data or unauthorized actuator commands can cause mission degradation even without code execution.

## Command and Data Handling

C&DH is the nervous system of the spacecraft. It receives telecommands, validates them, routes them to subsystems, collects telemetry, and manages payload data.

Common C&DH components include:

- On-board computers
- Microcontrollers
- FPGAs
- Memory devices
- Packet decoders
- Telemetry processors

In Pwnsat, C&DH is the most important offensive target. The RP2040 firmware parses incoming frames, extracts APIDs, dispatches handlers, and produces telemetry. A bug in this layer can turn a malformed packet into a reset, memory corruption, command spoofing, or remote code execution in the lab.

## Electrical Power System

The EPS provides energy to the spacecraft. Real EPS designs include solar panels, batteries, power distribution units, regulators, fuses, and protection circuits.

For security testing, EPS matters because power events often expose behavior that is invisible during normal runtime:

- Boot logs over UART
- Flash reads over SPI
- Sensor initialization over I2C
- Watchdog recovery paths
- Brownout or reset loops

Pwnsat's power-up sequence is therefore a useful reconnaissance moment.

## Propulsion

Propulsion systems change orbit, adjust attitude, perform station keeping, or deorbit a spacecraft. Real systems include tanks, valves, thrusters, pumps, regulators, and safety interlocks.

Pwnsat models propulsion as a commandable subsystem. That makes it a useful training target because the security question is the same: **who is allowed to send a high-impact command, and how does the spacecraft verify that authority?**

## Telemetry, Tracking, and Command

TT&C is the mission's command-and-control channel. It includes uplink commands, downlink telemetry, ranging, tracking, and sometimes emergency recovery.

Pwnsat's TT&C model uses:

- A LoRa uplink for telecommands
- A LoRa downlink for telemetry
- CCSDS-inspired packet framing
- APID-based routing

Because the lab protocol lacks strong authentication and encryption, TT&C becomes the main remote attack surface.

## Thermal Control

Thermal control prevents overheating and freezing. Real spacecraft use radiators, heaters, coatings, heat pipes, thermistors, and thermal straps.

Pwnsat uses environmental telemetry as a simplified model. Temperature, pressure, and humidity readings can be used to teach:

- Sensor trust boundaries
- Telemetry spoofing
- I2C bus analysis
- Health packet parsing

## From Spacecraft Architecture to Attack Surface

The practical lesson is simple: every subsystem creates a trust boundary.

| Trust Boundary | Example Question |
| --- | --- |
| RF link | Can anyone transmit a valid telecommand? |
| Packet parser | What happens when length fields are inconsistent? |
| APID dispatch | Can low-privilege packet types reach high-impact handlers? |
| Sensor bus | Can telemetry be spoofed or replayed? |
| Debug interface | Is firmware extraction or live debugging possible? |
| Reset path | Can an attacker force denial of service? |

The rest of the book follows those boundaries from physical discovery to protocol reversing and exploitation.
