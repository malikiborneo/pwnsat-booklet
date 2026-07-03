#!/usr/bin/env python3
"""Send framed Pwnsat SPP telecommands over the USBRadioLink CDC endpoint."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import serial

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from spp_tools import build_tc, print_packet


APID_NAMES = {
    "ping": 0x01,
    "reset": 0x02,
    "fw": 0x03,
    "thruster": 0x04,
    "beacon": 0x05,
    "broadcast": 0x06,
    "flash": 0x07,
}


def parse_hex_bytes(value: str) -> bytes:
    cleaned = value.replace(" ", "").replace(":", "").replace(",", "")
    if len(cleaned) % 2 != 0:
        raise argparse.ArgumentTypeError("hex payload must contain complete bytes")
    try:
        return bytes.fromhex(cleaned)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def frame_usb(raw_spp: bytes) -> bytes:
    return b"\xAA\x55" + len(raw_spp).to_bytes(2, "big") + raw_spp


def build_payload(args: argparse.Namespace) -> bytes:
    if args.payload_hex is not None:
        return args.payload_hex

    if args.command == "thruster":
        return bytes([args.thruster_id, args.power])
    if args.command == "beacon":
        # Current firmware only copies payload when the SPP length field is > 0.
        # Add one padding byte so one-byte handlers still receive data[0].
        return bytes([args.seconds, 0x00])
    if args.command == "broadcast":
        return args.frequency.to_bytes(2, "big") + args.message.encode()

    return b""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and send a framed SPP telecommand over USB."
    )
    parser.add_argument("--port", required=True, help="USBRadioLink serial port")
    parser.add_argument("--baud", type=int, default=921600)
    parser.add_argument(
        "--command",
        choices=sorted(APID_NAMES),
        required=True,
        help="telecommand preset to build",
    )
    parser.add_argument("--payload-hex", type=parse_hex_bytes)
    parser.add_argument("--seq", type=int, default=1)
    parser.add_argument("--thruster-id", type=int, default=0)
    parser.add_argument("--power", type=int, default=80)
    parser.add_argument("--seconds", type=int, default=1)
    parser.add_argument("--frequency", type=lambda x: int(x, 0), default=0x01B8)
    parser.add_argument("--message", default="Pwnsat")
    parser.add_argument("--read-seconds", type=float, default=1.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    raw_spp = build_tc(APID_NAMES[args.command], payload, args.seq)
    framed = frame_usb(raw_spp)

    print("[raw SPP]")
    print(raw_spp.hex())
    print_packet(raw_spp)
    print()
    print("[USB framed]")
    print(framed.hex())

    if args.dry_run:
        return 0

    with serial.Serial(args.port, args.baud, timeout=0.1) as ser:
        time.sleep(0.2)
        ser.write(framed)
        ser.flush()
        deadline = time.time() + args.read_seconds
        received = bytearray()
        while time.time() < deadline:
            chunk = ser.read(4096)
            if chunk:
                received.extend(chunk)

    if received:
        print()
        print("[received bytes]")
        print(received.hex())
    else:
        print()
        print("[received bytes]")
        print("no bytes received before timeout")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
