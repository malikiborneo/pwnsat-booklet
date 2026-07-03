# Appendix B: APID and Packet Reference

This appendix collects the packet values used throughout the book.

## APID Registry

| APID | Direction | Name | Description |
| --- | --- | --- | --- |
| `0x01` | TC/TM | PING | Liveness and ACK. |
| `0x02` | TC/TM defined, TC used | RESETC | Watchdog reset command and reset telemetry concept. |
| `0x03` | TC/TM | SEND_FW | Firmware version response. |
| `0x04` | TC/TM | SET_THRUSTER | Simulated thruster power control. |
| `0x05` | TC/TM | SET_BEACON_RATE | Beacon interval configuration. |
| `0x06` | TC/TM | BROADCAST_MSG | Broadcast message and frequency control. |
| `0x07` | TC/TM | FLASH | Chunked static data transfer. |
| `0x08` | TM | SEND_TM | Periodic sensor telemetry. |
| `0x7FF` | TM | IDLE | Idle packet APID. |

## SPP Primary Header

| Field | Size | Meaning |
| --- | --- | --- |
| Version | 3 bits | Should be `0`. |
| Packet Type | 1 bit | `0` telemetry, `1` telecommand. |
| Secondary Header Flag | 1 bit | Indicates optional secondary header. |
| APID | 11 bits | Application Process Identifier. |
| Sequence Flags | 2 bits | Segmentation state. |
| Sequence Count | 14 bits | Packet counter. |
| Data Length | 16 bits | Data field size minus one. |

## Bit Masks

```text
version          = (packet_id >> 13) & 0x7
packet_type      = (packet_id >> 12) & 0x1
secondary_header = (packet_id >> 11) & 0x1
apid             = packet_id & 0x7FF
sequence_flags   = (sequence >> 14) & 0x3
sequence_count   = sequence & 0x3FFF
data_size        = length_field + 1
```

## Pwnsat RF Parameters

| Link | Frequency | Bandwidth | Spreading Factor | Coding Rate |
| --- | --- | --- | --- | --- |
| Uplink | 918 MHz | 250 kHz | SF7 | CR5 |
| Downlink | 916 MHz | 250 kHz | SF7 | CR5 |

## Payload Quick Reference

| APID | Payload |
| --- | --- |
| `0x01` PING | Usually empty or small liveness payload. |
| `0x02` RESETC | Empty. |
| `0x03` SEND_FW | Empty request; response includes version. |
| `0x04` SET_THRUSTER | `thruster_id`, `thruster_power`. |
| `0x05` SET_BEACON_RATE | `interval_seconds`. |
| `0x06` BROADCAST_MSG | `frequency_hi`, `frequency_lo`, `message...`. |
| `0x07` FLASH | Empty request; response is chunked. |
| `0x08` SEND_TM | Telemetry response generated periodically. |

