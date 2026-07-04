# Firmware

This folder contains the PwnSat / FlatSat firmware source code used for lab-based satellite cybersecurity analysis.

The firmware is used to understand mission logic, Space Packet Protocol handling, uplink/downlink behavior, USB command handling, and simulated spacecraft subsystems.

---

## Firmware File Index

| File | Purpose |
|---|---|
| `firmware.ino` | Main Arduino/RP2040 firmware entry point. |
| `mission.h` | Mission constants, command definitions, or mission state definitions. |
| `pins.h` | Hardware pin mapping. |
| `spp.cpp` / `spp.h` | Space Packet Protocol parsing, encoding, or packet handling logic. |
| `ruplink.cpp` / `ruplink.h` | Radio uplink handling logic. |
| `rdownlink.cpp` / `rdownlink.h` | Radio downlink handling logic. |
| `usbCDC.cpp` / `usbCDC.h` | USB CDC serial command interface. |
| `sensors.cpp` / `sensors.h` | Sensor simulation or sensor interface logic. |
| `thruster.cpp` / `thruster.h` | Thruster or actuator simulation logic. |
| `worker.cpp` / `worker.h` | Main mission worker or background task logic. |
| `led.cpp` / `led.h` | LED status or hardware feedback logic. |

---

## Thesis Role

This firmware supports:

- protocol analysis,
- firmware architecture understanding,
- command and telemetry behavior analysis,
- vulnerability analysis,
- exploit reliability study,
- defensive engineering and hardening.

---

## Build Artifacts

The `build/` folder may contain generated firmware output such as `.uf2` files.

This should be reviewed later to decide whether build output should remain in the repository, be moved to a release folder, or be ignored by `.gitignore`.

---

## Safety Scope

This firmware is intended for authorized PwnSat / FlatSat lab use only.
