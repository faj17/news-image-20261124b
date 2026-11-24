#!/usr/bin/env python3
"""Validate entry.png and copy it to an output directory.

Stdlib only, no network. Checks: PNG magic, IHDR CRC, 1024x1024
dimensions, size <= 1 MiB, trailing IEND chunk. Copies the file to the
output dir and verifies the copy's SHA-256 matches the source.
"""
import argparse
import hashlib
import os
import shutil
import struct
import sys
import zlib

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1024 * 1024
EXPECTED_W = 1024
EXPECTED_H = 1024


def fail(msg):
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description="Validate entry.png")
    ap.add_argument("--output", default="/output",
                    help="output directory (default /output)")
    ap.add_argument("--verbose", action="store_true",
                    help="print the SHA-256")
    ap.add_argument("--quiet", action="store_true",
                    help="suppress the OK line")
    args = ap.parse_args()

    src = "entry.png"
    if not os.path.isfile(src):
        fail(f"{src} not found")
    size = os.path.getsize(src)
    if size > MAX_BYTES:
        fail(f"{src} is {size} bytes, over the 1 MiB limit")

    with open(src, "rb") as f:
        data = f.read()

    if data[:8] != PNG_MAGIC:
        fail("bad PNG magic")
    if len(data) < 8 + 25:
        fail("file too short for IHDR")

    # IHDR: length (4) + type "IHDR" (4) + data (13) + CRC (4).
    ihdr_len = struct.unpack(">I", data[8:12])[0]
    ihdr_type = data[12:16]
    if ihdr_type != b"IHDR" or ihdr_len != 13:
        fail("first chunk is not a 13-byte IHDR")
    ihdr_data = data[16:29]
    ihdr_crc_stored = struct.unpack(">I", data[29:33])[0]
    ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data) & 0xFFFFFFFF
    if ihdr_crc != ihdr_crc_stored:
        fail("IHDR CRC mismatch")
    width, height = struct.unpack(">II", ihdr_data[:8])
    if (width, height) != (EXPECTED_W, EXPECTED_H):
        fail(f"dimensions {width}x{height}, expected "
             f"{EXPECTED_W}x{EXPECTED_H}")

    # Trailing IEND: last 12 bytes = length 0, type IEND, CRC 0xAE426082.
    if len(data) < 12:
        fail("file too short for IEND")
    tail = data[-12:]
    iend_len, iend_type, iend_crc = struct.unpack(">I4sI", tail)
    if iend_len != 0 or iend_type != b"IEND" or iend_crc != 0xAE426082:
        fail("no trailing IEND chunk")

    digest = sha256_of(src)
    os.makedirs(args.output, exist_ok=True)
    dst = os.path.join(args.output, "entry.png")
    shutil.copyfile(src, dst)
    if sha256_of(dst) != digest:
        fail("copy SHA-256 mismatch")
    if args.verbose:
        print(f"sha256 {digest}")
    if not args.quiet:
        print(f"OK entry.png {width}x{height} {size} bytes -> {dst}")


if __name__ == "__main__":
    main()
