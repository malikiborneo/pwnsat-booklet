#!/usr/bin/env python3
"""Write pattern bytes to a file"""

from __future__ import annotations

import argparse
from pathlib import Path
from pwn import cyclic

def main() -> None:
  parser = argparse.ArgumentParser(description="Fuzzer Offset")
  parser.add_argument("--path", default="resources/fuzzing/fuzzing/pattern.bin")
  
  args = parser.parse_args()

  pattern = cyclic(300)
  pattern_path = Path(args.path)
  pattern_path.write_bytes(pattern)
  print(f"Wrote {len(pattern)} bytes to {pattern_path}")
  
if __name__ == "__main__":
  main()