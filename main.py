#!/usr/bin/env python3
"""Entrypoint: verify the bundled entry.png and copy it to the output dir.

Stdlib only (no PIL). Parses the PNG header manually with struct.
Writes ONLY to os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "out"),
"entry.png") -- never next to this file, never inside the repo.
"""
import base64
import hashlib
import os
import struct
import sys
import zlib

EXPECTED_SHA256 = "5b3055d5a91b9f055d5b4921ffec97100c93eed030a9ddacff627739bac9653b"
EXPECTED_SIZE = 151607
MIN_SIZE = 10_000
MAX_SIZE = 1_048_576


def fail(msg):
    print(f"main.py: error: {msg}", file=sys.stderr)
    return 1


def check_png(path):
    """Validate PNG structure; return (size, sha256) or raise ValueError."""
    with open(path, "rb") as fh:
        data = fh.read()
    size = len(data)
    if size < MIN_SIZE:
        raise ValueError(f"too small: {size} bytes")
    if size > MAX_SIZE:
        raise ValueError(f"too big: {size} bytes (limit {MAX_SIZE})")
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("bad PNG signature")
    # first chunk must be IHDR, 13 bytes, 1024x1024, bit depth 8,
    # colour type 2 or 6, compression/filter/interlace 0
    off = 8
    length = struct.unpack(">I", data[off:off + 4])[0]
    ctype = data[off + 4:off + 8]
    if ctype != b"IHDR" or length != 13:
        raise ValueError("first chunk is not a 13-byte IHDR")
    ihdr = data[off + 8:off + 21]
    width, height, depth, ctype_n, comp, filt, inter = struct.unpack(">IIBBBBB", ihdr)
    if (width, height) != (1024, 1024):
        raise ValueError(f"wrong dimensions: {width}x{height}")
    if depth != 8 or ctype_n not in (2, 6):
        raise ValueError(f"unsupported PNG type: depth {depth}, colour {ctype_n}")
    if comp != 0 or filt != 0 or inter != 0:
        raise ValueError("unsupported compression/filter/interlace")
    crc_stored = struct.unpack(">I", data[off + 21:off + 25])[0]
    crc_calc = zlib.crc32(b"IHDR" + ihdr) & 0xFFFFFFFF
    if crc_stored != crc_calc:
        raise ValueError("IHDR CRC mismatch")
    # chunk walk: every chunk CRC, IDAT non-empty, IEND last, no trailing data
    off += 25
    idat_total = 0
    seen_iend = False
    while off < len(data):
        if off + 8 > len(data):
            raise ValueError("truncated chunk header")
        length = struct.unpack(">I", data[off:off + 4])[0]
        ctype = data[off + 4:off + 8]
        if off + 12 + length > len(data):
            raise ValueError(f"truncated chunk {ctype!r}")
        chunk_data = data[off + 8:off + 8 + length]
        crc_stored = struct.unpack(">I", data[off + 8 + length:off + 12 + length])[0]
        if zlib.crc32(ctype + chunk_data) & 0xFFFFFFFF != crc_stored:
            raise ValueError(f"CRC mismatch in chunk {ctype!r}")
        if ctype == b"IDAT":
            if length == 0:
                raise ValueError("empty IDAT chunk")
            idat_total += length
        if ctype == b"IEND":
            if length != 0:
                raise ValueError("IEND must be empty")
            if off + 12 != len(data):
                raise ValueError("trailing data after IEND")
            seen_iend = True
            break
        off += 12 + length
    if not seen_iend:
        raise ValueError("missing IEND chunk")
    if idat_total < 1000:
        raise ValueError(f"IDAT payload too small: {idat_total} bytes")
    sha = hashlib.sha256(data).hexdigest()
    return size, sha


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    if not out_dir:
        return fail("MAKEFUN_OUTPUT_DIR is empty")
    out_dir_abs = os.path.abspath(out_dir)
    here_abs = os.path.abspath(here)
    if out_dir_abs == here_abs or out_dir_abs.startswith(here_abs + os.sep):
        return fail("MAKEFUN_OUTPUT_DIR must not be inside the repo")
    if os.path.isfile(out_dir_abs):
        return fail("MAKEFUN_OUTPUT_DIR is a file, not a directory")
    dst = os.path.join(out_dir_abs, "entry.png")
    if os.path.abspath(dst) == os.path.abspath(src):
        return fail("refusing to overwrite the source entry.png")
    if not os.path.isfile(src):
        return fail(f"source not found: {src}")
    try:
        size, sha = check_png(src)
    except (OSError, ValueError) as exc:
        return fail(str(exc))
    if EXPECTED_SIZE and size != EXPECTED_SIZE:
        return fail(f"size mismatch: got {size}, expected {EXPECTED_SIZE}")
    if EXPECTED_SHA256 != "PLACEHOLDER" and sha != EXPECTED_SHA256:
        return fail(f"sha256 mismatch: got {sha}, expected {EXPECTED_SHA256}")
    os.makedirs(out_dir_abs, exist_ok=True)
    with open(src, "rb") as fh:
        payload = fh.read()
    with open(dst, "wb") as fh:
        fh.write(payload)
    # re-read output to confirm byte-identical
    with open(dst, "rb") as fh:
        out_sha = hashlib.sha256(fh.read()).hexdigest()
    if out_sha != sha:
        return fail("output differs from source")
    print(f"main.py: wrote {dst} ({size} bytes, sha256 {sha})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
