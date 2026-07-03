# Phase 1: Blind Reconnaissance

Black-box reconnaissance assumes that you do not have schematics, source code, firmware, or documentation. Your job is to discover the board's architecture from physical evidence and electrical behavior.

For a satellite-like embedded system, blind reconnaissance should answer five questions:

1. What computes?
2. What communicates?
3. What stores data?
4. What senses or actuates?
5. Where can an operator observe or influence the system?

**Primary SPARTA TTP:** REC-0001.04 Data Bus Information.

## Step 1: Visual Reconnaissance

Visual reconnaissance is not guesswork. Every visible component gives constraints about the system.

## Goals

- Identify processing units.
- Identify external memories.
- Identify communication modules.
- Locate test points and headers.
- Infer possible buses.
- Build a first-pass attack surface map.

## 1.1 Identify the Main MCU or SoC

Look for:

- The largest IC on the board.
- Markings or silkscreen labels.
- A crystal oscillator nearby.
- Dense decoupling capacitors.
- Traces running to radios, sensors, memory, or headers.

Heuristics:

- A nearby crystal often means a timing-sensitive processor or radio.
- Many decoupling capacitors near one IC usually indicate a logic core.
- A nearby flash package suggests external code or data storage.
- Traces from the MCU to test pads may expose SWD, UART, or boot pins.

Expected Pwnsat finding:

| Item | Expected Observation |
| --- | --- |
| Main controller | Raspberry Pi RP2040 or equivalent board controller. |
| Role | Flight software, packet parsing, telemetry generation, command dispatch. |
| Security relevance | The MCU is the target for firmware reversing and memory-corruption testing. |

![Flatsat OBC Identification](static/Flatsat_OBC.png)

## 1.2 Identify External Flash or Memory

Look for:

- 8-pin SOIC or WSON packages.
- Markings such as `25Qxx`, `MX25`, `W25`, or similar SPI flash families.
- Traces to MCU pins that look like CLK, MOSI, MISO, and CS.

Security implications:

- SPI flash can contain firmware or configuration.
- Boot-time SPI traffic can reveal memory layout or firmware reads.
- If write protection is weak, flash may become a persistence target.

![Flatsat Flash Identification](static/Flatsat_Flash.png)

## 1.3 Identify RF Components

Look for:

- Shielded RF modules.
- Antenna connectors or antenna traces.
- Matching networks near RF pins.
- Crystals or TCXOs near radios.
- SPI-like traces between MCU and radio.

Expected Pwnsat finding:

| Item | Expected Observation |
| --- | --- |
| Radio family | SX1262 LoRa-class radios. |
| Radio count | Two radios, commonly used as separate uplink and downlink paths. |
| Security relevance | RF is the remote command and telemetry attack surface. |

![Flatsat Radio Identification](static/Flatsat_Radio.png)

## 1.4 Identify Headers and Test Pads

Headers and test pads are the highest-value targets in blind hardware reconnaissance.

Look for labels such as:

- `TX`, `RX`
- `SWDIO`, `SWCLK`
- `CLK`, `DIO`, `MOSI`, `MISO`, `CS`
- `GND`, `3V3`, `VBUS`
- `BOOT`, `RUN`, `RST`

Possible interfaces:

| Interface | Pins | Value |
| --- | --- | --- |
| UART | TX, RX, GND | Boot logs, debug shell, telemetry text. |
| SWD | SWDIO, SWCLK, GND, VREF | Firmware extraction, breakpoints, memory inspection. |
| SPI | CLK, MOSI, MISO, CS | Flash reads, radio configuration, packet observation. |
| I2C | SDA, SCL, GND | Sensor discovery and telemetry spoofing. |
| GPIO | Digital pins | Reset, boot mode, actuator simulation. |

![Flatsat Test Pads Identification](static/Flatsat_Headers.png)

## Step 2: Power Mapping and Ground Reference

Before probing any signal, establish electrical context.

## 2.1 Find Ground

Use continuity mode to identify ground references:

- USB connector shield.
- Large copper pours.
- Mounting holes.
- Negative side of bulk capacitors.
- Ground pins on headers.

Always connect the logic analyzer ground to the target ground before probing digital channels.

## 2.2 Find Voltage Rails

Use a multimeter to measure likely power pins:

- 3.3 V for MCU logic and sensors.
- 5 V from USB input.
- Lower rails if regulators are present.

Do not inject signals into unknown pins. Classification should start with passive observation.

## Step 3: Interface Discovery

Once ground and voltage references are known, classify signals by behavior.

## 3.1 UART Identification

UART is asynchronous serial communication. It usually uses TX, RX, and GND, with no shared clock.

Characteristics:

- Idle high, commonly near 3.3 V.
- Bursts during boot or reset.
- Human-readable ASCII is common in debug builds.
- Common baud rates include 9600, 115200, 230400, and 921600.

Procedure:

1. Connect ground.
2. Probe candidate TX pins.
3. Trigger capture during power-up.
4. Try automatic baud detection or common baud rates.
5. Search decoded output for banners, logs, stack traces, or command prompts.

Security value:

- Boot logs may reveal firmware version, APIDs, frequencies, sensor state, or error paths.
- Debug shells may expose direct command execution in development builds.

## 3.2 SPI Identification

SPI is common for flash memories, radios, displays, and high-speed peripherals.

Characteristics:

- At least four logical signals: CLK, MOSI, MISO, CS.
- Clock only toggles during active transactions.
- Chip-select line usually goes low during a transaction.
- Traffic often appears immediately after reset when flash or radios initialize.

Procedure:

1. Identify candidate pins near flash or radios.
2. Probe four or more channels at once.
3. Trigger on clock activity during reset.
4. Decode as SPI mode 0 or mode 3 first.
5. Compare byte patterns against known flash commands or radio register operations.

Common flash opcodes:

| Opcode | Meaning |
| --- | --- |
| `0x03` | Read data. |
| `0x0B` | Fast read. |
| `0x9F` | Read JEDEC ID. |
| `0x06` | Write enable. |

Security value:

- Flash traffic can reveal firmware access.
- Radio traffic can reveal frequencies, modulation settings, and packet behavior.
- SPI injection can be used in advanced lab scenarios to alter peripheral behavior.

## 3.3 I2C Identification

I2C is common for sensors. It uses two lines: SDA and SCL.

Characteristics:

- Two lines with pull-up resistors.
- Both lines idle high.
- SCL behaves like a clock.
- SDA changes around clock pulses.
- Common speeds are 100 kHz and 400 kHz.

Procedure:

1. Look near sensors or small peripheral ICs.
2. Find two lines that idle high.
3. Capture during boot and normal telemetry generation.
4. Decode with SDA and SCL assigned.
5. Record discovered 7-bit addresses.

Security value:

- Sensor addresses identify onboard components.
- Sensor reads reveal telemetry generation timing.
- Bus injection can be used to spoof health or environment data in a controlled lab.

## 3.4 SWD and JTAG Identification

SWD and JTAG are debug interfaces. ARM Cortex-M targets commonly expose SWD.

Common SWD pins:

- SWDIO
- SWCLK
- GND
- VREF
- RESET, optional

Indicators:

- Small grouped pads near the MCU.
- Labels such as `SWD`, `DIO`, `CLK`, `DBG`.
- One line with clock-like behavior when a debugger attaches.

Security value:

- Full memory inspection.
- Firmware extraction.
- Live debugging.
- Breakpoints in command handlers.

If debug access is enabled on a deployed system, physical access may become full device compromise.

## Step 4: Logic Analyzer Workflow

A logic analyzer turns guesses into evidence. The goal is not just to see signal changes, but to classify interfaces and extract useful protocol information.

## 4.1 Capture Strategy

Start with passive observation:

1. Connect ground.
2. Attach probes to candidate pins.
3. Set the analyzer threshold to match the logic level, usually 3.3 V logic.
4. Capture at a rate at least 4-10 times faster than the expected bus speed.
5. Trigger on reset, power-up, button press, USB connection, or RF activity.

Recommended sample rates:

| Interface | Practical Starting Rate |
| --- | --- |
| UART 115200 | 1-2 MS/s |
| I2C 100 kHz | 1-2 MS/s |
| I2C 400 kHz | 4-8 MS/s |
| SPI 1-8 MHz | 20-50 MS/s |

## 4.2 Signal Classification

Use signal shape before using protocol decoders.

| Signal Behavior | Likely Interface |
| --- | --- |
| One asynchronous line, idle high | UART TX |
| Two idle-high lines, one clock-like | I2C |
| Clock plus MOSI/MISO plus chip select | SPI |
| Short activity only when debugger attaches | SWD/JTAG |
| Constant pulse width pattern | PWM or timing output |
| No activity | Power, ground, reset, unused GPIO, or inactive peripheral |

## 4.3 Pwnsat Capture: Initial Bus Discovery

In the current capture, channels 0 and 1 remain static, while channels 2 and 3 show bursts of activity during initialization.

![Initial logic analyzer capture](static/Pasted%20image%2020260511072824.png)

From the waveform:

- Channels 0 and 1 can be deprioritized for this capture.
- Channels 2 and 3 are active.
- Both active lines appear to idle high.
- One active line behaves like a clock.
- The active pair is consistent with I2C.

This is enough to test an I2C decoder.

## 4.4 Decoding as I2C

Add a protocol analyzer with:

| Setting | Value |
| --- | --- |
| Analyzer | I2C |
| SDA | Channel 2 |
| SCL | Channel 3 |
| Address display | 7-bit, address bits only |

![I2C analyzer decode](static/Pasted%20image%2020260511073746.png)

If the decoder produces valid transactions, the hypothesis is confirmed: channels 2 and 3 are an I2C bus.

## 4.5 Interpreting I2C Results

Once the bus is decoded, record:

- Device addresses.
- Read versus write operations.
- Register addresses.
- Transaction timing.
- Whether traffic occurs only at boot or periodically.

Pwnsat's expected I2C devices include:

| Device | Common 7-bit Address | Role |
| --- | --- | --- |
| BME280 | `0x76` or `0x77` | Temperature, pressure, humidity telemetry. |
| LIS2DH12 | `0x18` or `0x19` | Accelerometer/IMU telemetry. |

If the capture shows these addresses, you can link the electrical bus to mission telemetry. That turns a waveform into a subsystem map:

```text
RP2040 -> I2C bus -> BME280 / LIS2DH12 -> telemetry packet builder -> downlink
```

**BME280 0x76 Capture**
![Logic Analyzer sensor capture](static/Logic_I2C_caoture_76.png)

**LIS2DH12 0x19 Capture**
![Logic Analyzer sensor capture](static/Logic_I2C_caoture_19.png)

## Booklet Exercise: Parse an Exported I2C Capture

Open [Booklet.ipynb](Booklet.ipynb) and run **Part 1: Logic Analyzer Export Analysis**. The exercise uses an exported logic analyzer file such as:

```text
Flatsat_v1_Initial_start_exported.txt
```

The helper [scripts/i2c_parser.py](scripts/i2c_parser.py) loads the export, groups rows into I2C transactions, infers register reads, and prints detected devices.

Example notebook workflow:

```python
from i2c_parser import parse_file

parse_file(DATA_FILE, None, None, None)
parse_file(DATA_FILE, "0x19", None, None)
parse_file(DATA_FILE, None, "0x23", None)
parse_file(DATA_FILE, None, None, "r")
```

Use the output to answer:

- Which devices appear on the I2C bus?
- Which registers are touched during startup?
- Which address is most likely the accelerometer?
- Which address is most likely the environmental sensor?
- How would spoofed sensor data affect APID `0x08` telemetry?

## 4.6 What to Extract From the Capture

The immediate deliverable is a bus table:

| Channel | Classification | Evidence | Next Step |
| --- | --- | --- | --- |
| CH0 | Static or unknown | No activity in capture. | Re-test during reset, RF activity, or button press. |
| CH1 | Static or unknown | No activity in capture. | Re-test with different trigger conditions. |
| CH2 | I2C SDA candidate | Idle high, paired with clock line, valid I2C decode. | Confirm by address decode and sensor activity. |
| CH3 | I2C SCL candidate | Clock-like bursts, valid I2C decode. | Measure bus speed and timing. |

Then produce a security interpretation:

- The board exposes sensor traffic on I2C.
- Telemetry can likely be correlated with I2C reads.
- A researcher can test sensor spoofing by controlling the bus in a lab setup.
- Defensive firmware should validate telemetry plausibility rather than blindly trusting every sensor read.

## 4.7 Follow-On Experiments

After identifying I2C, continue with controlled experiments:

1. Capture a full boot sequence and list all I2C addresses.
2. Capture during periodic telemetry downlink and compare timing.
3. Change the physical environment, such as temperature, and observe which bytes change.
4. Match changed bytes to telemetry fields in the downlink packet.
5. If authorized, disconnect or emulate a sensor and observe error handling.

The final goal is to connect physical signals to protocol fields. Once you can say "this I2C transaction becomes this telemetry payload," you are no longer only probing hardware; you are reversing the mission data path.
