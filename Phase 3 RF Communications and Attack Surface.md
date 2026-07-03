# Phase 3: RF Communications and Attack Surface

Radio frequency communication is the boundary where a spacecraft becomes reachable without physical access. For satellite security, RF is not just a transport layer. It is part of the command authority model, the telemetry confidentiality model, and the mission availability model.

This phase gives the RF background needed before writing the exploitation chapters. It explains how radio links work, how modulation carries information, why LoRa behaves differently from classic narrowband links, and how common RF attacks such as interception, spoofing, and jamming map to spacecraft security.

All RF exercises in this book assume a controlled lab, shielded or low-power test conditions, and equipment/frequencies that the operator is legally authorized to use. Do not transmit against real spacecraft, public services, or third-party infrastructure.

## RF in a Space System

An RF link carries information by using an electromagnetic wave as a carrier. A transmitter changes some property of that carrier, the wave propagates through space, and a receiver detects those changes and reconstructs the original information.

At a high level:

```text
Application data
  -> packet framing
  -> encoding / whitening / error correction
  -> modulation
  -> RF carrier
  -> antenna
  -> propagation channel
  -> antenna
  -> demodulation
  -> decoding
  -> packet parser
  -> application logic
```

Security controls can exist at several layers. A link may use error correction but no encryption. It may use packet framing but no authentication. It may be resistant to noise but still accept forged packets. These distinctions matter because RF reliability and RF security are different goals.

## Core RF Concepts

| Concept | Meaning | Security Relevance |
| --- | --- | --- |
| Frequency | The carrier's oscillation rate, measured in Hz. | Determines where a receiver must tune and what equipment can observe the signal. |
| Bandwidth | The occupied spectrum around the carrier. | Wider signals may carry more data or spread energy, but use more spectrum. |
| Power | Transmit energy, often measured in dBm or watts. | Affects range, detectability, and interference risk. |
| Noise floor | Background energy in the receiver bandwidth. | A signal must be distinguishable from noise to be decoded. |
| SNR | Signal-to-noise ratio. | Low SNR causes packet loss and may be abused for availability attacks. |
| Antenna gain | Directional or physical ability to focus energy. | Directional antennas can improve reception or localize sources. |
| Polarization | Orientation of the electromagnetic field. | Polarization mismatch can reduce received power. |
| Doppler shift | Apparent frequency shift caused by relative motion. | Important for real satellites, especially LEO. |

For Pwnsat, the firmware configures simple lab links:

| Link | Frequency | Modulation Family | Firmware Parameters |
| --- | --- | --- | --- |
| Uplink | 918 MHz | LoRa CSS | BW 250 kHz, SF7, CR5 |
| Downlink | 916 MHz | LoRa CSS | BW 250 kHz, SF7, CR5 |

The lab board does not need orbital Doppler compensation, but the concept is important for real satellite operations.

## How Modulation Works

A carrier wave by itself carries no useful digital message. Modulation is the process of changing the carrier so that it represents information.

The transmitter can vary:

- Amplitude
- Frequency
- Phase
- A combination of amplitude and phase
- The carrier's spreading pattern over time

The receiver reverses the process by estimating which symbols were transmitted.

## Analog Modulation

Analog modulation varies the carrier continuously.

| Modulation | Carrier Property Changed | Typical Use | Security Notes |
| --- | --- | --- | --- |
| AM, Amplitude Modulation | Amplitude | Broadcast audio, aviation voice variants. | Simple to detect and jam; inefficient under noise. |
| FM, Frequency Modulation | Frequency | Voice, broadcast radio, telemetry variants. | More noise-resistant than AM but still easy to observe. |
| PM, Phase Modulation | Phase | Some telemetry and communication systems. | Phase stability matters for receiver design. |

Analog links can still be security-relevant. Voice channels, unencrypted analog telemetry, and analog control links may leak operational details even when no digital packet parser exists.

## Digital Modulation

Digital modulation maps bits to symbols. A symbol may represent one bit or several bits depending on the modulation.

| Modulation | Idea | Strengths | Weaknesses |
| --- | --- | --- | --- |
| ASK/OOK | Encodes bits by changing amplitude. | Simple, cheap, easy to implement. | Sensitive to fading and amplitude noise. |
| FSK | Encodes bits by shifting frequency. | Robust and common in low-power telemetry. | Occupies frequency deviation around the carrier. |
| GFSK | FSK with Gaussian filtering. | Reduces spectral splatter. | Requires matched receiver settings. |
| PSK | Encodes symbols by shifting phase. | Power efficient and common in space links. | Needs phase recovery. |
| BPSK/QPSK | One or two bits per phase symbol. | Strong performance for telemetry and command links. | Receiver synchronization matters. |
| QAM | Combines amplitude and phase. | High data rate in good SNR. | More sensitive to noise and distortion. |
| OFDM | Splits data across many subcarriers. | Efficient for multipath channels. | Higher complexity and peak-to-average power issues. |
| CSS | Chirp Spread Spectrum. | Robust at low SNR, tolerant of frequency offsets. | Lower data rate; security still depends on higher-layer controls. |

The modulation only answers "how bits cross the air." It does not automatically provide confidentiality, authentication, replay protection, or command authorization.

## LoRa

LoRa is a physical-layer modulation based on **Chirp Spread Spectrum**, or CSS. Instead of representing data as a simple tone shift or phase shift, LoRa uses chirps: signals whose frequency sweeps over time. Symbols are encoded by shifting the chirp pattern.

LoRa is attractive for embedded and remote systems because it can decode packets at low SNR and operate over long distances at modest data rates.

## LoRa Parameters

| Parameter | Meaning | Effect |
| --- | --- | --- |
| Frequency | Center frequency of the carrier. | Both sides must tune to the same channel. |
| Bandwidth, BW | Width of the chirp sweep. | Wider BW gives higher data rate but less sensitivity. |
| Spreading Factor, SF | Number of chips per symbol, expressed as `SF7` to `SF12` commonly. | Higher SF improves sensitivity but lowers data rate and increases airtime. |
| Coding Rate, CR | Forward error correction overhead. | Higher redundancy improves resilience but increases airtime. |
| Preamble | Known symbols before payload. | Helps receiver detect and synchronize to a packet. |
| Explicit Header | Packet includes length/coding metadata. | More flexible, slightly more overhead. |
| CRC | Link-layer payload integrity check. | Detects accidental errors but is not authentication. |

Pwnsat's uplink code configures:

```text
Frequency:        918 MHz
Bandwidth:        250 kHz
Spreading Factor: SF7
Coding Rate:      5
CRC:              disabled in the current uplink configuration
Header:           explicit
```

The downlink uses:

```text
Frequency:        916 MHz
Bandwidth:        250 kHz
Spreading Factor: SF7
Coding Rate:      5
```

## LoRa Security Reality

LoRa should not be confused with LoRaWAN. LoRa is the modulation. LoRaWAN is a higher-level network protocol that can include device identity, session keys, message integrity, and replay protection.

Pwnsat uses LoRa-style radio links directly. The firmware packets are mission-defined SPP frames, not LoRaWAN frames. Therefore, the board does not inherit LoRaWAN's security model.

Security properties must be provided by the mission protocol:

| Required Property | Where It Must Be Implemented |
| --- | --- |
| Confidentiality | Encrypt command and telemetry payloads. |
| Authentication | Verify sender identity before command dispatch. |
| Integrity | Detect packet modification. |
| Replay protection | Reject reused commands. |
| Authorization | Restrict high-impact APIDs to safe modes or roles. |

In the current Pwnsat firmware, these controls are absent or intentionally weak for training.

## RF Attack Classes

RF attacks can target confidentiality, integrity, authenticity, or availability. Not every RF attack requires a firmware bug.

## Interception

Interception is passive reception of a signal. The attacker does not transmit; they listen.

General workflow:

1. Detect energy near a likely frequency.
2. Identify modulation and bandwidth.
3. Demodulate or record baseband/IQ samples.
4. Recover frames.
5. Parse protocol fields.
6. Reconstruct telemetry, commands, or timing.

Security impact:

- Cleartext telemetry becomes readable.
- Uplink command structure can be learned.
- Packet timing reveals operational rhythms.
- Replays and spoofing become easier after protocol recovery.

SPARTA mapping:

| Activity | Mapping |
| --- | --- |
| Capturing uplink traffic for learning | `REC-0005.01 Uplink Intercept Eavesdropping` |
| Capturing downlink traffic for learning | `REC-0005.02 Downlink Intercept` |
| Reconstructing mission data from captured downlink | `EXF-0003.02 Downlink Exfiltration` |
| Reconstructing command traffic from captured uplink | `EXF-0003.01 Uplink Exfiltration` |

Defensive controls:

- Authenticated encryption.
- Traffic-flow protection where feasible.
- Command counters and anti-replay.
- Monitoring for unauthorized receivers is hard, so assume RF can be heard.

## Spoofing

Spoofing means sending forged data that the receiver treats as legitimate. In RF systems, spoofing can happen at several levels:

| Layer | Spoofing Example |
| --- | --- |
| Signal level | Transmitting a waveform that resembles the expected carrier. |
| Frame level | Sending syntactically valid packets. |
| Protocol level | Reusing valid APIDs, counters, or command formats. |
| Data level | Forging sensor, navigation, timing, or telemetry values. |

For Pwnsat, spoofing becomes command injection when a rogue lab transmitter sends a valid SPP telecommand over the uplink. Because the firmware does not authenticate command origin, the board cannot distinguish an authorized command tool from a compatible transmitter.

SPARTA mapping:

| Activity | Mapping |
| --- | --- |
| Rogue transmitter sends telecommands | `IA-0008.01 Rogue Ground Station` |
| Packet reaches command dispatcher | `EX-0001.01 Command Packets` |
| Forged internal/sensor data is accepted | `EX-0014.02 Bus Traffic Spoofing` or `EX-0014.03 Sensor Data` |

Defensive controls:

- Cryptographic command authentication.
- Bidirectional session establishment.
- Anti-replay counters or nonces.
- Strict APID/type authorization.
- Telemetry indicating accepted and rejected commands.

## Jamming

Jamming is an availability attack against a receiver. Instead of trying to parse valid packets, the adversary raises interference or creates signal conditions that prevent the receiver from decoding legitimate traffic.

Conceptual jamming types:

| Type | Concept | Typical Effect |
| --- | --- | --- |
| Broadband noise | Energy spread across a wide frequency range. | Raises the noise floor for many channels. |
| Narrowband tone | Energy concentrated near a carrier or subchannel. | Disrupts receivers sensitive to that frequency. |
| Partial-band interference | Targets only part of the occupied spectrum. | Can degrade specific channels while conserving power. |
| Protocol-aware interference | Times interference around preambles, headers, or expected packet windows. | Can be more efficient than continuous noise. |
| Reactive interference | Transmits only after detecting a target signal. | Harder to notice as a constant emitter. |

This book does not provide operational jamming procedures. The educational point is how availability fails and how defenders detect and design around it.

SPARTA mapping:

| Activity | Mapping |
| --- | --- |
| Preventing telemetry from reaching ground | `DE-0002.02 Jam Link Signal` |
| Preventing command reception | Availability attack against the command link; document as link inhibition and mission impact. |
| Causing operators to lose situational awareness | `IMP-0002 Disruption`, when ground processing or visibility is affected. |

Defensive controls:

- Link-budget margin.
- Directional antennas.
- Frequency agility.
- Spread-spectrum or jam-resistant waveforms.
- Alternate communication paths.
- Telemetry alarms for RSSI/SNR anomalies.
- Operational procedures for degraded communication modes.

## Replay

Replay is the reuse of a previously captured valid message. Replay is not always "spoofing" in the narrow sense because the packet may be authentic, just old.

Replay becomes dangerous when a receiver lacks:

- Sequence enforcement.
- Timestamp validation.
- Nonces.
- Command expiration.
- Session binding.

For Pwnsat, sequence fields exist in the SPP header, but the command path does not enforce anti-replay behavior before dispatch. This means replay should be treated as a likely exploitation technique during later phases.

SPARTA mapping:

| Activity | Mapping |
| --- | --- |
| Capturing a command | `REC-0005.01 Uplink Intercept Eavesdropping` |
| Reusing it through a rogue transmitter | `IA-0008.01 Rogue Ground Station` |
| Causing command execution | `EX-0001.01 Command Packets` |

## Pwnsat RF Attack Surface

The firmware-defined RF surface is compact and very useful for training.

| Surface | Firmware Evidence | Security Question |
| --- | --- | --- |
| Uplink | 918 MHz LoRa, ASCII-hex payload converted to raw SPP bytes. | Can a compatible transmitter inject valid telecommands? |
| Downlink | 916 MHz LoRa, plaintext SPP telemetry. | Can a receiver reconstruct mission state? |
| CRC disabled on uplink | `radio0.setCRC(0)` | How does the system detect accidental corruption or deliberate malformed frames? |
| Explicit header mode | `radio0.explicitHeader()` | Can an observer infer packet length and LoRa framing behavior? |
| Broadcast APID | Packet-controlled frequency in `downlinkRadioTransmitBroadcast()`. | Can a telecommand retune the downlink transmitter in the lab? |
| Beacon-rate APID | Packet-controlled interval. | Can RF commands create excessive traffic? |

## Safe Lab Methodology

Use a staged workflow:

1. **Receive only:** capture downlink and confirm frequency/modulation.
2. **Decode only:** recover packet boundaries and SPP headers.
3. **Replay in a shielded/local lab:** only after confirming authorization and legal RF conditions.
4. **Inject over USB first:** reproduce packet behavior without RF uncertainty.
5. **Transmit over RF last:** port only known-safe lab payloads to the uplink.

This order separates protocol bugs from RF problems. If a packet fails over USB, RF will not make it better. If it works over USB but fails over RF, the issue is likely framing, encoding, radio parameters, airtime, or reception.

## RF Findings to Carry Into Exploitation

| Finding | Exploitation Relevance |
| --- | --- |
| Downlink is cleartext | Enables passive telemetry reconstruction before active attacks. |
| Uplink lacks authentication | Enables rogue lab command injection. |
| LoRa parameters are static | Reduces discovery effort. |
| Uplink accepts ASCII-hex encoded SPP bytes | Adds a transport transformation that exploit builders must handle. |
| CRC is disabled on uplink | Makes malformed packet delivery easier to test in the lab. |
| Broadcast command retunes downlink | Creates an RF behavior change controlled by the command layer. |

The next phase can now move from RF theory into exploitation: command crafting, replay, APID abuse, memory-corruption triggers, and RF delivery of payloads already validated through USB.
