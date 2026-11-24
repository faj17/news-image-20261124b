#!/usr/bin/env python3
"""Entry point for the news-image-20261124 make.fun entry.

Validates the pre-rendered entry.png held in this repository (PNG
magic, IHDR CRC, 1024x1024, at most 1 MiB, trailing IEND chunk), copies
it to the output directory as entry.png, and verifies the copy's
SHA-256 matches the source. Standard library only; no network.

Usage:
    python3 main.py [--output DIR] [--verbose | --quiet]
Default output directory is /output.
"""

import argparse
import hashlib
import shutil
import struct
import sys
import zlib
from pathlib import Path

MAX_BYTES = 1024 * 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def validate(png_bytes):
    if len(png_bytes) > MAX_BYTES:
        fail(f"entry.png is {len(png_bytes)} bytes, over the 1 MiB limit")
    if not png_bytes.startswith(PNG_MAGIC):
        fail("entry.png does not start with the PNG magic bytes")
    if len(png_bytes) < 8 + 25:
        fail("entry.png is too short to hold an IHDR chunk")
    # IHDR chunk: length (4), type (4), data (13), CRC (4).
    length = struct.unpack(">I", png_bytes[8:12])[0]
    ctype = png_bytes[12:16]
    if ctype != b"IHDR" or length != 13:
        fail("entry.png has no valid IHDR chunk first")
    ihdr = png_bytes[16:29]
    width, height = struct.unpack(">II", ihdr[0:8])
    if (width, height) != (1024, 1024):
        fail(f"entry.png is {width}x{height}, expected 1024x1024")
    crc_stored = struct.unpack(">I", png_bytes[29:33])[0]
    crc_actual = zlib.crc32(b"IHDR" + ihdr) & 0xFFFFFFFF
    if crc_stored != crc_actual:
        fail("entry.png IHDR CRC mismatch")
    # Trailing IEND chunk: 12 bytes, length 0, type IEND, CRC of "IEND".
    if len(png_bytes) < 12 or png_bytes[-12:-8] != b"\x00\x00\x00\x00":
        fail("entry.png does not end with a zero-length IEND chunk")
    if png_bytes[-8:-4] != b"IEND":
        fail("entry.png does not end with an IEND chunk")
    iend_crc = struct.unpack(">I", png_bytes[-4:])[0]
    if iend_crc != (zlib.crc32(b"IEND") & 0xFFFFFFFF):
        fail("entry.png IEND CRC mismatch")
    return width, height


def main():
    parser = argparse.ArgumentParser(
        description="Validate and copy entry.png to the output directory.")
    parser.add_argument("--output", default="/output",
                        help="output directory (default: /output)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--verbose", action="store_true",
                       help="print the SHA-256 of the copied image")
    group.add_argument("--quiet", action="store_true",
                       help="print nothing on success")
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    if not source.is_file():
        fail(f"{source} not found")
    png_bytes = source.read_bytes()
    validate(png_bytes)

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "entry.png"
    shutil.copyfile(source, dest)

    digest = hashlib.sha256(dest.read_bytes()).hexdigest()
    expected = hashlib.sha256(png_bytes).hexdigest()
    if digest != expected:
        fail("SHA-256 of the copied entry.png does not match the source")
    if args.verbose:
        print(f"sha256 {digest}")
    elif not args.quiet:
        print(f"wrote {dest}")


if __name__ == "__main__":
    main()
