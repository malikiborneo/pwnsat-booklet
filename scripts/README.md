# Scripts

This folder contains Python scripts used for PwnSat / FlatSat protocol analysis, packet testing, I2C parsing, and controlled lab fuzzing.

These scripts are intended for an isolated, authorized lab environment only.

---

## Script Index

| Script | Purpose |
|---|---|
| `spp_tools.py` | Space Packet Protocol helper functions for packet parsing, encoding, or decoding. |
| `usb_tc_send.py` | Sends telecommands to the FlatSat firmware through the USB CDC interface. |
| `i2c_parser.py` | Parses exported I2C / logic analyzer capture data. |
| `fuzz_offset.py` | Helps identify offsets or packet fields during controlled fuzzing experiments. |
| `fuzz_exploit.py` | Runs controlled fuzzing or exploit-validation tests against the lab FlatSat target. |

---

## Safety Scope

Do not use these scripts against real satellites, real ground stations, public RF systems, or any system without authorization.

---

## Usage Notes

Detailed command examples should be added after each script is reviewed and tested.
