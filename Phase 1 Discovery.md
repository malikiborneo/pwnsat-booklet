# Phase 1: Discovery

Discovery is the first phase of the Pwnsat attack chain. The objective is to build a reliable mental model of the target before sending commands, modifying firmware, or attempting exploitation.

Pwnsat can be studied through two complementary paths:

- **Black-box discovery:** used when schematics, source code, and firmware are unavailable. The operator relies on physical inspection, electrical probing, signal capture, and protocol observation.
- **White-box discovery:** used when public design files, source code, firmware images, blog posts, or conference material are available. The operator uses that information to shorten the reconnaissance phase.

Both paths should lead to the same core outputs:

| Output | Description |
| --- | --- |
| Hardware map | MCU, radios, sensors, memories, connectors, headers, and test pads. |
| Interface map | UART, SPI, I2C, SWD/JTAG, USB CDC, and RF links. |
| Protocol map | Packet format, APIDs, command types, sequence fields, and payload conventions. |
| Command map | Supported telecommands, telemetry frames, high-impact handlers, and reset paths. |
| Attack surface map | Physical, RF, firmware, protocol, and operational entry points. |

In this book, the black-box path is used to teach disciplined hardware reconnaissance. The white-box path shows how open information can transform the same target into a much faster reversing exercise.

Continue with:

- [Phase 1 Blind Reconnaissance](Phase%201%20Blind%20Reconnaissance.md)
- [Phase 1 Assisted Analysis](Phase%201%20Assisted%20Analysis.md)
