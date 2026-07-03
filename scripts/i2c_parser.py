"""I2C logic-analyzer export parser for the Pwnsat booklet exercises.

The parser expects a CSV-style export from a logic analyzer with columns similar
to Saleae's I2C analyzer export:

    Time [s], Packet ID, Address, Read/Write, ACK/NAK, Data

The public exercise repository can provide the raw `.logicdata` capture and an
exported text/CSV file. This module works with the exported text file so readers
without a logic analyzer license or hardware can still complete the exercises.
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()


def extract_hex(value: Any) -> int | None:
    """Extract the first hex value from a table cell."""
    if pd.isna(value):
        return None

    match = re.search(r"0x([0-9A-Fa-f]+)", str(value))
    if match:
        return int(match.group(1), 16)

    return None


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    aliases = {
        "time [s]": "time",
        "time": "time",
        "packet id": "packet_id",
        "packet_id": "packet_id",
        "read/write": "rw",
        "r/w": "rw",
        "rw": "rw",
        "ack/nak": "ack",
        "ack": "ack",
        "address": "address",
        "data": "data",
    }

    df = df.rename(columns={c: aliases.get(c, c) for c in df.columns})

    required = {"time", "packet_id", "address", "rw", "data"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    return df


def load_export(file_path: str | Path) -> pd.DataFrame:
    """Load and normalize a logic-analyzer export file."""
    path = Path(file_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Export file not found: {path}")

    df = pd.read_csv(path)
    df = _normalize_columns(df)

    df["address"] = df["address"].apply(extract_hex)
    df["data"] = df["data"].apply(extract_hex)
    df["rw"] = df["rw"].astype(str).str.strip().str.upper()

    return df


def get_transactions(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Group analyzer rows into I2C transactions."""
    transactions: list[dict[str, Any]] = []

    for packet_id, group in df.groupby("packet_id"):
        group = group.sort_values("time")

        addr = None
        rw = None
        data_bytes: list[int] = []

        for _, row in group.iterrows():
            if addr is None:
                addr = row["address"]
                rw = row["rw"]

            if row["data"] is not None and not pd.isna(row["data"]):
                data_bytes.append(int(row["data"]))

        transactions.append(
            {
                "packet_id": packet_id,
                "address": addr,
                "rw": rw,
                "data": data_bytes,
            }
        )

    return transactions


def get_reads(transactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Infer register reads from WRITE(register) followed by READ(data)."""
    reads: list[dict[str, Any]] = []

    for i in range(len(transactions) - 1):
        t1 = transactions[i]
        t2 = transactions[i + 1]

        if t1["rw"] == "WRITE" and t2["rw"] == "READ":
            if t1["address"] == t2["address"] and len(t1["data"]) >= 1:
                raw_reg = t1["data"][0]
                real_reg = raw_reg & 0x7F if raw_reg & 0x80 else raw_reg

                reads.append(
                    {
                        "device": t1["address"],
                        "register": real_reg,
                        "raw_register": raw_reg,
                        "data": t2["data"],
                    }
                )

    return reads


def filter_reads(
    reads: list[dict[str, Any]],
    address: str | int | None = None,
    register: str | int | None = None,
    transaction: str | None = None,
) -> list[dict[str, Any]]:
    """Filter inferred reads by address, register, or transaction type."""
    filtered = list(reads)

    if address is not None:
        address_int = int(address, 16) if isinstance(address, str) else address
        filtered = [r for r in filtered if r["device"] == address_int]

    if register is not None:
        register_int = int(register, 16) if isinstance(register, str) else register
        filtered = [r for r in filtered if r["register"] == register_int]

    if transaction:
        transaction = transaction.upper()
        if transaction == "R":
            filtered = [r for r in filtered if len(r["data"]) > 0]
        elif transaction == "W":
            filtered = []

    return filtered


def summarize_devices(transactions: list[dict[str, Any]]) -> set[int]:
    return {
        int(t["address"])
        for t in transactions
        if t.get("address") is not None and not pd.isna(t.get("address"))
    }


def build_register_map(reads: list[dict[str, Any]]) -> dict[int, set[int]]:
    register_map: dict[int, set[int]] = defaultdict(set)
    for read in reads:
        register_map[int(read["device"])].add(int(read["register"]))
    return register_map


def print_devices(devices: set[int]) -> None:
    summary = Table(title="Detected Devices", show_lines=True)
    summary.add_column("Device (HEX)", style="cyan")
    summary.add_column("Device (DEC)", style="magenta")

    for device in sorted(devices):
        summary.add_row(f"0x{device:02X}", str(device))

    console.print(summary)
    console.print(f"[bold green]Total devices:[/bold green] {len(devices)}\n")


def print_reads(reads: list[dict[str, Any]], limit: int = 10) -> None:
    table = Table(title="I2C Register Reads", show_lines=True)

    table.add_column("Device", style="cyan", justify="center")
    table.add_column("Register", style="yellow", justify="center")
    table.add_column("Raw Reg", style="dim", justify="center")
    table.add_column("Data", style="green")

    for read in reads[:limit]:
        data_str = " ".join(f"{byte:02X}" for byte in read["data"])
        table.add_row(
            f"0x{read['device']:02X}",
            f"0x{read['register']:02X}",
            f"0x{read['raw_register']:02X}",
            data_str,
        )

    console.print(table)
    console.print(
        f"[bold blue]Total showing {len(reads[:limit])} of:[/bold blue] {len(reads)}\n"
    )


def print_register_map(register_map: dict[int, set[int]]) -> None:
    reg_table = Table(title="Register Map", show_lines=True)
    reg_table.add_column("Device", style="cyan")
    reg_table.add_column("Registers", style="yellow")

    for device, registers in sorted(register_map.items()):
        reg_list = ", ".join(f"0x{reg:02X}" for reg in sorted(registers))
        reg_table.add_row(f"0x{device:02X}", reg_list)

    console.print(reg_table)


def parse_file(
    file_path: str | Path,
    address: str | int | None = None,
    register: str | int | None = None,
    transaction: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Parse a logic analyzer export and print a human-readable summary."""
    console.print(f"[bold cyan]Loading file:[/bold cyan] {file_path}")

    df = load_export(file_path)
    transactions = get_transactions(df)
    reads = get_reads(transactions)
    filtered_reads = filter_reads(reads, address, register, transaction)

    if not address and not register and not transaction:
        print_devices(summarize_devices(transactions))

    print_reads(filtered_reads, limit=limit)

    if not address and not register and not transaction:
        print_register_map(build_register_map(reads))

    return filtered_reads


def main() -> None:
    parser = argparse.ArgumentParser(description="I2C Logic Analyzer Parser")
    parser.add_argument("file_path")
    parser.add_argument("-a", "--address", help="Filter by device address, e.g. 0x19")
    parser.add_argument("-r", "--register", help="Filter by register, e.g. 0x23")
    parser.add_argument(
        "-t", "--transaction", choices=["r", "w"], help="Filter by transaction type"
    )
    parser.add_argument("-l", "--limit", type=int, default=10, help="Rows to display")

    args = parser.parse_args()

    parse_file(
        args.file_path,
        address=args.address,
        register=args.register,
        transaction=args.transaction,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
