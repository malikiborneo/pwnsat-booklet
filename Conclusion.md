# Conclusion

Pwnsat is deliberately small, but the lessons are large. The board compresses a spacecraft-style command link, telemetry path, packet parser, firmware dispatcher, sensors, radios, and debug surfaces into a lab environment that can be understood end to end.

The central lesson is that spacecraft security is systems security. A vulnerable parser matters because it sits behind a radio. A cleartext telemetry stream matters because operators trust it. An unauthenticated reset command matters because availability is a mission property. A sensor bus matters because telemetry is only as trustworthy as the data path that produced it.

The offensive workflow in this book followed a disciplined chain:

1. Understand the mission architecture.
2. Map the target with SPARTA.
3. Discover physical and logical interfaces.
4. Reverse the packet protocol.
5. Understand RF as an attack surface.
6. Validate exploitation locally.
7. Study reliability and firmware behavior.
8. Convert findings into hardening requirements.

That chain is the real tool. Individual vulnerabilities change from firmware to firmware, but the method carries forward.

The safest way to learn spacecraft offensive security is to break a system that was built to be broken, document what happened, and then engineer the fix. Pwnsat gives you that loop.

