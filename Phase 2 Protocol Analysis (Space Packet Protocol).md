# Phase 2: Protocol Analysis

## Space Packet Protocol

The Consultative Committee for Space Data Systems, or **CCSDS**, publishes standards and recommended practices used across space missions. One of the most important packet formats is the **Space Packet Protocol**, or **SPP**.

SPP provides a compact packet structure for moving application data between mission components. It is used to identify packet type, route data by Application Process Identifier, track sequence counts, and carry telemetry or telecommand payloads.

The most dangerous part of a standard is often the gap between the document and the implementation. Standards describe what should happen; firmware decides what actually happens when a malformed packet arrives.

## Why Protocol Analysis Matters

In Pwnsat, the packet parser is the bridge between the radio link and the flight software. Any attacker-controlled packet must cross this boundary before it can reach a command handler.

Protocol analysis helps answer:

- Which bytes are trusted?
- How is packet length calculated?
- Which APIDs are accepted?
- Are telemetry and telecommands separated correctly?
- What happens when fields are inconsistent?
- Can malformed packets reach memory-unsafe code?

## Space Packet Layout

An SPP packet has two major parts:

1. **Packet Primary Header:** 6 bytes, mandatory.
2. **Packet Data Field:** 1 to 65,536 bytes, mandatory by the CCSDS model.

```text
|----------------------------- SPACE PACKET -----------------------------|
|  PACKET PRIMARY HEADER  |              PACKET DATA FIELD               |
|  6 octets               |----------------------------------------------|
|                         | Optional Secondary Header | User Data Field |
|                         | Variable                  | Variable        |
```

The primary header is always present and is the first parsing target.

## Packet Primary Header

The 6-byte primary header is divided into three 16-bit fields:

| Field | Size | Offset | Description |
| --- | --- | --- | --- |
| Packet Identification | 2 bytes | `0x00` | Version, packet type, secondary header flag, APID. |
| Packet Sequence Control | 2 bytes | `0x02` | Sequence flags and sequence count. |
| Packet Data Length | 2 bytes | `0x04` | Length of the packet data field minus one. |

The fields are encoded in network byte order, or big endian.

## Bit-Level Header Fields

```text
Packet Identification, 16 bits

bits 15..13   Version
bit  12       Packet Type
bit  11       Secondary Header Flag
bits 10..0    APID

Packet Sequence Control, 16 bits

bits 15..14   Sequence Flags
bits 13..0    Packet Sequence Count

Packet Data Length, 16 bits

bits 15..0    Data field length minus 1
```

## Field Meanings

| Field | Meaning |
| --- | --- |
| Version | CCSDS SPP version. It should be `0b000`. |
| Packet Type | `0` for telemetry/reporting, `1` for telecommand/requesting. |
| Secondary Header Flag | `1` when a secondary header is present, `0` when it is not. |
| APID | Application Process Identifier. Used to route the packet. |
| Sequence Flags | Describes whether the packet is segmented. |
| Sequence Count | 14-bit counter, modulo 16,384. |
| Packet Data Length | Number of bytes in the data field minus one. |

Sequence flag values:

| Value | Meaning |
| --- | --- |
| `0b00` | Continuation segment. |
| `0b01` | First segment. |
| `0b10` | Last segment. |
| `0b11` | Unsegmented data. |

The idle APID is `0x7FF`, represented by eleven `1` bits.

## Length Field Trap

The SPP length field is easy to mishandle. The stored value is not the total packet length. It is not even the raw payload length. It is:

```text
packet_data_length = length_field + 1
total_packet_length = 6 + packet_data_length
```

If the length field is `0x001E`, the packet data field is `31` bytes long, and the total packet should be `37` bytes.

This off-by-one rule is a common source of bugs:

- Allocating `length_field` bytes instead of `length_field + 1`.
- Copying `length_field + 1` bytes into a `length_field`-sized buffer.
- Accepting packets where the captured frame is shorter than the declared data field.
- Treating a zero length field as empty data, even though it means one byte of data.

The current Pwnsat firmware shows that last case in practice: `spp_unpack_packet()` copies payload bytes only when `header.length > 0`. Under a strict SPP interpretation, `header.length == 0` still declares a one-byte data field. For lab commands that need a one-byte payload, the exercises add a padding byte so the implementation copies the intended first data byte.

## Reversing Mask Table

Use this table when decoding captured frames.

| Item | Source Field | Mask or Shift |
| --- | --- | --- |
| Version | Packet Identification | `(packet_id >> 13) & 0x7` |
| Packet Type | Packet Identification | `(packet_id >> 12) & 0x1` |
| Secondary Header Flag | Packet Identification | `(packet_id >> 11) & 0x1` |
| APID | Packet Identification | `packet_id & 0x7FF` |
| Sequence Flags | Packet Sequence Control | `(sequence >> 14) & 0x3` |
| Sequence Count | Packet Sequence Control | `sequence & 0x3FFF` |
| Data Length Field | Packet Data Length | `length_field` |
| Data Field Size | Packet Data Length | `length_field + 1` |

## Sample Packet

Captured frame:

```text
00000000  08 07 00 33 00 1E 01 07 00 70 00 8F 00 52 61 62  |...3.....p...Rab|
00000010  69 74 00 00 00 00 00 00 00 00 00 00 00 A7 00 00  |it..............|
00000020  00 01 00 00 60 0A                                |....`.|
```

Raw hex:

```text
08070033001e01070070008f0052616269740000000000000000000000a7000000010000600a
```

Primary header:

| Header Field | Bytes | Value |
| --- | --- | --- |
| Packet Identification | `08 07` | `0x0807` |
| Packet Sequence Control | `00 33` | `0x0033` |
| Packet Data Length | `00 1E` | `30` |

Decoded fields:

| Item | Calculation | Value |
| --- | --- | --- |
| Version | `(0x0807 >> 13) & 0x7` | `0` |
| Packet Type | `(0x0807 >> 12) & 0x1` | `0`, telemetry |
| Secondary Header Flag | `(0x0807 >> 11) & 0x1` | `1` |
| APID | `0x0807 & 0x7FF` | `0x007` |
| Sequence Flags | `(0x0033 >> 14) & 0x3` | `0`, continuation |
| Sequence Count | `0x0033 & 0x3FFF` | `51` |
| Data Length Field | `0x001E` | `30` |
| Data Field Size | `30 + 1` | `31` bytes |

The frame contains 38 bytes in the sample as written. A strict CCSDS interpretation of `0x001E` expects a total length of 37 bytes: 6 header bytes plus 31 data bytes. The extra trailing byte should be investigated as a transport artifact, padding byte, capture boundary issue, or implementation-specific deviation.

This is exactly why protocol analysis must compare the standard, the implementation, and the capture.

## Working Decoder

The following decoder is intentionally small. It validates the primary header, extracts bit fields, computes the expected data length, and reports whether the captured frame has trailing bytes.

```python
#!/usr/bin/env python3
import struct
import string
from dataclasses import dataclass


SEQ_FLAGS = {
    0b00: "Continuation",
    0b01: "First segment",
    0b10: "Last segment",
    0b11: "Unsegmented",
}


def hexdump(data: bytes, width: int = 16) -> str:
    lines = []
    for offset in range(0, len(data), width):
        chunk = data[offset : offset + width]
        hex_bytes = " ".join(f"{byte:02X}" for byte in chunk)
        hex_bytes = hex_bytes.ljust(width * 3)
        ascii_bytes = "".join(
            chr(byte) if chr(byte) in string.printable and byte >= 0x20 else "."
            for byte in chunk
        )
        lines.append(f"{offset:08X}  {hex_bytes}  {ascii_bytes}")
    return "\n".join(lines)


@dataclass
class SpacePacket:
    raw: bytes
    packet_id: int
    sequence: int
    length_field: int
    version: int
    packet_type: int
    secondary_header: int
    apid: int
    sequence_flags: int
    sequence_count: int
    data_field_size: int
    data_field: bytes
    trailing: bytes

    @classmethod
    def decode(cls, raw: bytes) -> "SpacePacket":
        if len(raw) < 7:
            raise ValueError("A CCSDS Space Packet must be at least 7 bytes")

        packet_id, sequence, length_field = struct.unpack_from(">HHH", raw, 0)

        version = (packet_id >> 13) & 0x7
        packet_type = (packet_id >> 12) & 0x1
        secondary_header = (packet_id >> 11) & 0x1
        apid = packet_id & 0x7FF

        sequence_flags = (sequence >> 14) & 0x3
        sequence_count = sequence & 0x3FFF

        data_field_size = length_field + 1
        expected_total = 6 + data_field_size

        if len(raw) < expected_total:
            raise ValueError(
                f"Truncated packet: expected {expected_total} bytes, got {len(raw)}"
            )

        data_field = raw[6:expected_total]
        trailing = raw[expected_total:]

        return cls(
            raw=raw,
            packet_id=packet_id,
            sequence=sequence,
            length_field=length_field,
            version=version,
            packet_type=packet_type,
            secondary_header=secondary_header,
            apid=apid,
            sequence_flags=sequence_flags,
            sequence_count=sequence_count,
            data_field_size=data_field_size,
            data_field=data_field,
            trailing=trailing,
        )

    def print_report(self) -> None:
        packet_type_name = "TM" if self.packet_type == 0 else "TC"
        print("=========== Space Packet ===========")
        print(f"Version:              {self.version}")
        print(f"Type:                 {self.packet_type} ({packet_type_name})")
        print(f"Secondary Header:     {self.secondary_header}")
        print(f"APID:                 0x{self.apid:03X}")
        print(
            f"Sequence Flags:       0b{self.sequence_flags:02b} "
            f"({SEQ_FLAGS[self.sequence_flags]})"
        )
        print(f"Sequence Count:       {self.sequence_count}")
        print(f"Length Field:         {self.length_field}")
        print(f"Data Field Size:      {self.data_field_size} bytes")
        print(f"Captured Bytes:       {len(self.raw)}")
        print()
        print("[HEADER]")
        print(hexdump(self.raw[:6]))
        print()
        print("[DATA FIELD]")
        print(hexdump(self.data_field))
        if self.trailing:
            print()
            print("[TRAILING BYTES]")
            print(hexdump(self.trailing))


if __name__ == "__main__":
    sample = bytes.fromhex(
        "08070033001e01070070008f005261626974"
        "0000000000000000000000a7000000010000600a"
    )
    packet = SpacePacket.decode(sample)
    packet.print_report()
```

Expected output:

```text
=========== Space Packet ===========
Version:              0
Type:                 0 (TM)
Secondary Header:     1
APID:                 0x007
Sequence Flags:       0b00 (Continuation)
Sequence Count:       51
Length Field:         30
Data Field Size:      31 bytes
Captured Bytes:       38

[HEADER]
00000000  08 07 00 33 00 1E                                ...3..

[DATA FIELD]
00000000  01 07 00 70 00 8F 00 52 61 62 69 74 00 00 00 00   ...p...Rabit....
00000010  00 00 00 00 00 00 00 A7 00 00 00 01 00 00 60      ..............`

[TRAILING BYTES]
00000000  0A                                                .
```

## Turning the Decoder Into an Analysis Tool

For reversing, extend the decoder in small steps:

1. Add APID names.
2. Add packet type names.
3. Add command-specific payload parsers.
4. Validate allowed APID/type combinations.
5. Reject impossible length combinations.
6. Log unknown packets as test cases.

Example APID registry:

```python
APIDS = {
    0x01: "PING",
    0x02: "RESET",
    0x04: "THRUSTER",
    0x07: "FLASH",
    0x08: "SEND_TM",
    0x7FF: "IDLE",
}
```

Then the report can include:

```python
print(f"APID Name:            {APIDS.get(self.apid, 'UNKNOWN')}")
```

## Booklet Exercise: Decode and Build SPP Packets

Open [Booklet.ipynb](Booklet.ipynb) and run **Part 2: Space Packet Protocol Exercises**. The helper [scripts/spp_tools.py](scripts/spp_tools.py) provides small packet-building and decoding functions for offline practice.

The notebook walks through:

- Decoding the sample telemetry frame from this chapter.
- Building a safe APID `0x01` PING telecommand.
- Building an APID `0x03` firmware-version request.
- Building an APID `0x04` thruster-state command.
- Inspecting a malformed APID `0x06` broadcast packet as an underflow candidate.

The point is not to transmit. The point is to connect bytes to firmware behavior before moving to USB or RF delivery.

## SpaceCAN Protocol Analysis

SPP describes the packet format used by the command and telemetry path. SpaceCAN describes a different layer of the spacecraft model: the internal controller-to-subsystem bus. In a real small spacecraft, this kind of bus is where the on-board computer talks to power, payload, attitude, radio, and sensor nodes. In this repository, [spacecan_lib](spacecan_lib/README.md) provides a simulated C implementation that lets the reader study that bus without physical CAN hardware.

The reference SpaceCAN standard is published by LibreCube at `https://librecube.gitlab.io/standards/spacecan/`. The design goal is a small, reliable CAN-based bus for control and monitoring between one controller node and multiple responder nodes. It is not intended for high-volume science data. It is intended for commands, status, housekeeping, synchronization, time distribution, and small service packets.

> **Implementation note:** The local `spacecan_lib` README states that version `1.0.0` is not a full implementation of the LibreCube SpaceCAN standard. Treat the library as a research and training model. It implements the pieces needed for bus emulation, request/reply frames, heartbeat/SYNC behavior, fragmentation, sniffing, replay, and injection exercises, but it should not be described as a complete standards-compliant flight implementation.

At a high level, SpaceCAN separates three ideas:

1. **Physical and link layer:** CAN frames with an 11-bit identifier and up to 8 data bytes.
2. **Bus role model:** one controller, usually node ID `0`, and responder nodes, usually node IDs `1` through `127`.
3. **Application meaning:** request, reply, heartbeat, synchronization, time, and optional service protocol data carried inside CAN frames.

The security lesson is that the CAN identifier is not only an address. It is also a priority and message-class field. Lower CAN IDs win arbitration on a real CAN bus, so identifier choice affects timing and authority. A forged low-ID frame can be more than a fake message; it can become a bus-control primitive.

```text
External command path                         Internal bus path

Ground / lab host
  -> RF or USB
  -> SPP parser
  -> APID command handler
  -> controller logic
  -> SpaceCAN request/reply/sync/heartbeat
  -> responder node behavior
```

## SpaceCAN Topology and Roles

LibreCube SpaceCAN uses a controller/responder topology. The controller commands responders and collects status. Responders do not normally talk directly to each other; if data must move between responders, the controller coordinates the exchange. That model matters for security because it creates a clear authority boundary:

| Role | Typical Node ID | Expected Behavior | Security Question |
| --- | --- | --- | --- |
| Controller | `0` | Sends requests, heartbeat, SYNC, and time frames. | Can an attacker impersonate the controller? |
| Responder | `1..127` | Sends replies and housekeeping to the controller. | Can an attacker spoof a responder's telemetry? |
| Passive observer | none | Receives traffic without transmitting. | What can be learned from cadence and payloads? |
| Rogue node | any forged ID | Sends frames not authorized by bus policy. | Do nodes authenticate source or only trust CAN ID? |

The local library models nodes with `spacecan_bus_node_t`. A node stores `node_id`, state, controller flags, heartbeat timing, SYNC timing, and a receive callback. The virtual bus broadcasts frames to connected clients through `/tmp/spacecan.sock`, so the exercises can be performed as Unix processes instead of physical CAN devices.

## SpaceCAN CAN-ID Format

SpaceCAN uses the 11-bit standard CAN identifier. The reference layout follows the ECSS-CAN idea of splitting the identifier into a function/object region and a 7-bit node ID. The local library defines the same practical masks:

```c
#define CAN_FULL_MASK     0x7FF
#define CAN_FUNCTION_MASK 0x780
#define CAN_NODE_MASK     0x07F
```

The current local constants are:

| Object | CAN ID Pattern | Originator in the Model | Meaning |
| --- | --- | --- | --- |
| Heartbeat | `0x700` family | Controller or local simulated node | Node liveness/state signal. |
| SYNC | `0x080` family | Controller or local simulated node | Timing pulse for synchronized behavior. |
| SCET time | `0x180` | Controller | Spacecraft elapsed time distribution. |
| UTC time | `0x200` | Controller | UTC-like time distribution in the local constants. |
| Request | `0x280 + node_id` | Controller | Command or query sent to a responder. |
| Reply | `0x300 + node_id` | Responder | Status, telemetry, or response sent to controller. |

For request and reply traffic, the node ID is recovered from the lower seven bits:

```text
request_id(node) = 0x280 + (node_id & 0x7F)
reply_id(node)   = 0x300 + (node_id & 0x7F)
node_id          = can_id & 0x7F
function_class   = can_id & 0x780
```

Example: CAN ID `0x284` is a request to node `0x04`; CAN ID `0x304` is a reply from node `0x04`.

```text
11-bit CAN ID: 0x284

binary: 010 1000 0100
        ^^^ ^^^^ ^^^^
        |   |    |
        |   |    +-- lower 7 bits: node ID 0x04
        +---+------- function/object region: request family 0x280
```

## SpaceCAN Frame Payloads

A normal CAN data frame can carry at most 8 data bytes. SpaceCAN therefore has two useful payload modes:

| Mode | Payload Capacity | Use |
| --- | --- | --- |
| Direct request/reply | `0..8` bytes | Small commands, status values, or housekeeping samples. |
| Packet fragmentation | Up to multiple 6-byte chunks | Larger application packets split over request/reply frames. |

The local direct builders are intentionally simple:

```c
int sc_build_request(spacecan_frame_t *frame, uint8_t node_id,
                     const uint8_t *payload, size_t len);

int sc_build_reply(spacecan_frame_t *frame, uint8_t node_id,
                   const uint8_t *payload, size_t len);
```

Both reject payloads larger than 8 bytes, set the CAN ID from the node ID, set `dlc`, zero the buffer, and copy the payload. There is no authentication, freshness check, or application schema validation at this layer. Those controls would need to be added above the frame builder or enforced by each receiving node.

## SpaceCAN Packet Fragmentation

The reference SpaceCAN packet protocol works around the 8-byte CAN limit by reserving the first two data bytes as a fragmentation header and using the remaining six bytes for packet data. The local implementation follows this shape:

```text
Byte 0: total number of frames minus 1
Byte 1: current frame sequence number, starting at 0
Byte 2..7: up to 6 bytes of packet data
```

A 15-byte packet becomes three CAN frames:

```text
Frame 0: [02 00] [DE AD BE EF 01 02]
Frame 1: [02 01] [03 04 05 06 07 08]
Frame 2: [02 02] [AA BB CC]
```

The local implementation defines:

```c
#define MAX_PACKET_SIZE 256
#define MAX_DATA_LEN 8
#define PAYLOAD_HEADER_LEN 2
#define MAX_CHUNK_LEN 6
#define SC_MAX_FRAGMENTS 43
```

Because each fragment carries six payload bytes, 43 fragments can represent up to 258 fragment bytes, while `MAX_PACKET_SIZE` is 256. The builder rejects input larger than 256 bytes, but protocol analysis should still test reassembly behavior at the boundary because a receiver may see attacker-supplied fragments rather than locally built fragments.

Reassembly stores fragments by sequence number, records per-fragment sizes, and returns a completed packet only after every expected sequence number has arrived. It accepts out-of-order delivery, which is useful for CAN behavior, but it also means the receiver must carefully define duplicate, stale, mixed-CAN-ID, and timeout behavior.

## Heartbeat, SYNC, and Timing Traffic

SpaceCAN heartbeat and SYNC frames are operational signals, not just telemetry.

| Signal | Standard Role | Security-Relevant Abuse |
| --- | --- | --- |
| Heartbeat | Lets nodes determine whether the active bus/controller is alive. | Forged heartbeat can mask failure or influence redundancy decisions. |
| SYNC | Tells responders to perform periodic application behavior. | Forged or high-rate SYNC can alter telemetry cadence or load. |
| Time | Distributes spacecraft time to local time consumers. | Forged time can affect logs, schedules, and freshness checks. |

The local library's heartbeat builder uses a one-byte state payload:

```text
0x00 = INIT
0x01 = OPERATIONAL
0x09 = ERROR
```

That is useful for lab visualization, but it is also a good reminder: once state is represented as unauthenticated bus traffic, a rogue process or node can try to create false health views.

## SpaceCAN Analysis Workflow

Use this workflow when analyzing SpaceCAN traffic:

1. Capture raw frames with timestamp, CAN ID, DLC, and data bytes.
2. Classify each CAN ID by function family: heartbeat, SYNC, request, reply, time, or unknown.
3. Extract node ID from the lower seven bits when the frame belongs to a node-addressed family.
4. Build a per-node timeline of requests, replies, heartbeat state, and timing changes.
5. Detect fragmented packets by looking for `data[0] = total_minus_one` and `data[1] = sequence`.
6. Reassemble only frames that share the expected CAN ID, total count, and timing window.
7. Compare observed behavior to the source code and the LibreCube reference.

For each frame, record the following analysis fields:

| Field | Example | Why It Matters |
| --- | --- | --- |
| Timestamp | `1710000000.123` | Reveals cadence, replay timing, and floods. |
| CAN ID | `0x284` | Encodes function class and node. |
| Function | `REQ` | Separates command-like frames from telemetry-like frames. |
| Node ID | `0x04` | Identifies target or source node. |
| DLC | `2` | Detects malformed length for expected command schemas. |
| Data | `01 12` | Application payload. |
| Interpretation | "request to node 4" | Human-readable hypothesis to test. |

## SpaceCAN Security Tests

After decoding the traffic, run malformed and unauthorized cases in the simulator before touching any physical bus:

| Test Case | Purpose |
| --- | --- |
| Forged request to a responder ID | Checks whether command authority is based only on CAN ID. |
| Forged reply from a responder ID | Tests telemetry trust and operator display assumptions. |
| Duplicate heartbeat | Tests state-monitoring ambiguity. |
| High-rate SYNC | Tests timing-driven load and telemetry cadence changes. |
| Fragment sequence gap | Confirms incomplete packets are not delivered upward. |
| Duplicate fragment with different bytes | Tests whether first or last fragment wins. |
| Fragment total-count mismatch | Tests reassembly reset and mixed-packet behavior. |
| Replay file with original timing | Tests whether state transitions are freshness-protected. |

The central question is the same as in SPP analysis: which fields are trusted before they are authenticated, length-checked, and mapped to an explicit state machine?

## Parser Security Tests

Once the valid packet format is understood, test parser behavior with malformed packets in the lab.

| Test Case | Purpose |
| --- | --- |
| Shorter than 6 bytes | Confirms the parser rejects missing headers. |
| Length field larger than captured frame | Tests truncation handling. |
| Length field smaller than captured frame | Tests trailing-byte behavior. |
| Unknown APID | Tests dispatcher default case. |
| TC packet sent to TM-only APID | Tests type enforcement. |
| TM packet sent to TC-only APID | Tests direction enforcement. |
| Idle APID with secondary header flag set | Tests standards compliance. |
| Maximum length field | Tests allocation and copy boundaries. |

Each test should produce one of three outcomes:

- Clean reject.
- Clean accept with documented behavior.
- Crash, reset, memory corruption, or undefined behavior.

The third outcome is a vulnerability candidate.

## Exploitation-Relevant Questions

During protocol analysis, keep a running list of exploitability questions:

- Does the parser validate `length_field + 1` before copying?
- Does it compare declared length to actual received length?
- Are APIDs used as indexes into fixed-size arrays?
- Are command handlers reachable without authentication?
- Are sequence counts enforced or ignored?
- Are duplicate telecommands accepted?
- Does malformed telemetry leak memory?
- Does a reset command require any safety condition?

The answers drive the next phase: controlled command injection and fuzzing.

The malformed packets from this chapter should not be discarded after manual testing. Save them as seed inputs for the fuzzing corpus used in Phase 4. Good corpus entries include a valid PING telecommand, a valid broadcast command, a truncated six-byte header, a packet with a declared length larger than its captured bytes, and a packet with unusual sequence flags. Those files let libFuzzer start near meaningful protocol states instead of wasting time on completely random data.

## Defensive Requirements

The protocol layer should enforce security before dispatch:

- Reject packets shorter than the declared length.
- Decide and document how to handle trailing bytes.
- Enforce APID direction, such as TC-only or TM-only.
- Enforce command authentication before state-changing handlers.
- Add replay protection using sequence counters or authenticated nonces.
- Bounds-check every payload before parsing fields.
- Make parser failures explicit telemetry events rather than silent resets.

Good spacecraft security starts with boring parser correctness. If the packet parser is predictable, bounded, and strict, the rest of the mission software has a much better chance.
