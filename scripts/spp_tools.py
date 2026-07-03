"""Small Space Packet Protocol helpers for the Pwnsat booklet exercises."""

from __future__ import annotations

import struct
from dataclasses import dataclass


APIDS = {
    0x01: "PING",
    0x02: "RESETC",
    0x03: "SEND_FW",
    0x04: "SET_THRUSTER",
    0x05: "SET_BEACON_RATE",
    0x06: "BROADCAST_MSG",
    0x07: "FLASH",
    0x08: "SEND_TM",
    0x7FF: "IDLE",
}


SEQ_FLAGS = {
    0b00: "Continuation",
    0b01: "First segment",
    0b10: "Last segment",
    0b11: "Unsegmented",
}


@dataclass
class DecodedPacket:
    raw: bytes
    version: int
    packet_type: int
    secondary_header: int
    apid: int
    sequence_flags: int
    sequence_count: int
    length_field: int
    data_field_size: int
    data: bytes
    trailing: bytes

    @property
    def packet_type_name(self) -> str:
        return "TM" if self.packet_type == 0 else "TC"

    @property
    def apid_name(self) -> str:
        return APIDS.get(self.apid, "UNKNOWN")


def build_primary_header(
    apid: int,
    packet_type: int = 1,
    sequence_count: int = 0,
    data_len: int = 0,
    sequence_flags: int = 0b11,
    secondary_header: int = 0,
) -> bytes:
    """Build a CCSDS-style SPP primary header.

    `data_len` is the CCSDS length field value, not the raw payload size.
    A value of 0 means the packet declares one byte of data.
    """
    packet_id = 0
    packet_id |= (0 & 0x7) << 13
    packet_id |= (packet_type & 0x1) << 12
    packet_id |= (secondary_header & 0x1) << 11
    packet_id |= apid & 0x7FF

    sequence = 0
    sequence |= (sequence_flags & 0x3) << 14
    sequence |= sequence_count & 0x3FFF

    return struct.pack(">HHH", packet_id, sequence, data_len & 0xFFFF)


def build_tc(apid: int, payload: bytes = b"", sequence_count: int = 1) -> bytes:
    """Build a basic telecommand packet.

    CCSDS stores data field size minus one. Empty payloads are represented by a
    zero-length field in many exercise builders, but strict CCSDS packets have at
    least one data byte. This helper mirrors the lab style and uses max(len-1, 0).
    """
    length_field = max(len(payload) - 1, 0)
    return build_primary_header(
        apid=apid,
        packet_type=1,
        sequence_count=sequence_count,
        data_len=length_field,
    ) + payload

def build_tm(apid: int, payload: bytes = b"", sequence_count: int = 1) -> bytes:
    """Build a basic telemetry packet.

    CCSDS stores data field size minus one. Empty payloads are represented by a
    zero-length field in many exercise builders, but strict CCSDS packets have at
    least one data byte. This helper mirrors the lab style and uses max(len-1, 0).
    """
    length_field = max(len(payload) - 1, 0)
    return build_primary_header(
        apid=apid,
        packet_type=0,
        sequence_count=sequence_count,
        data_len=length_field,
    ) + payload

def decode_packet(raw: bytes) -> DecodedPacket:
    if len(raw) < 6:
        raise ValueError("SPP packet must contain at least a 6-byte primary header")

    packet_id, sequence, length_field = struct.unpack_from(">HHH", raw, 0)
    version = (packet_id >> 13) & 0x7
    packet_type = (packet_id >> 12) & 0x1
    secondary_header = (packet_id >> 11) & 0x1
    apid = packet_id & 0x7FF
    sequence_flags = (sequence >> 14) & 0x3
    sequence_count = sequence & 0x3FFF
    data_field_size = length_field + 1
    expected_total = 6 + data_field_size
    data = raw[6:expected_total]
    trailing = raw[expected_total:]

    return DecodedPacket(
        raw=raw,
        version=version,
        packet_type=packet_type,
        secondary_header=secondary_header,
        apid=apid,
        sequence_flags=sequence_flags,
        sequence_count=sequence_count,
        length_field=length_field,
        data_field_size=data_field_size,
        data=data,
        trailing=trailing,
    )


def hexdump(data: bytes, width: int = 16) -> str:
    lines = []
    for offset in range(0, len(data), width):
        chunk = data[offset : offset + width]
        hex_bytes = " ".join(f"{byte:02X}" for byte in chunk).ljust(width * 3)
        ascii_bytes = "".join(chr(byte) if 32 <= byte <= 126 else "." for byte in chunk)
        lines.append(f"{offset:08X}  {hex_bytes}  {ascii_bytes}")
    return "\n".join(lines)


def print_packet(raw: bytes) -> DecodedPacket:
    packet = decode_packet(raw)
    print("=========== Space Packet ===========")
    print(f"Version:              {packet.version}")
    print(f"Type:                 {packet.packet_type} ({packet.packet_type_name})")
    print(f"Secondary Header:     {packet.secondary_header}")
    print(f"APID:                 0x{packet.apid:03X} ({packet.apid_name})")
    print(
        f"Sequence Flags:       0b{packet.sequence_flags:02b} "
        f"({SEQ_FLAGS.get(packet.sequence_flags, 'Unknown')})"
    )
    print(f"Sequence Count:       {packet.sequence_count}")
    print(f"Length Field:         {packet.length_field}")
    print(f"Data Field Size:      {packet.data_field_size}")
    print(f"Captured Bytes:       {len(raw)}")
    print()
    print("[HEADER]")
    print(hexdump(raw[:6]))
    if packet.data:
        print()
        print("[DATA]")
        print(hexdump(packet.data))
    if packet.trailing:
        print()
        print("[TRAILING]")
        print(hexdump(packet.trailing))
    return packet
