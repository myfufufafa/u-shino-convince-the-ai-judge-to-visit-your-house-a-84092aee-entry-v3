#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House — entry program.

Ships a single watercolour invitation letter (letter.jpg, generated for this
entry) as the competition image. The program is deliberately boring on
purpose: it copies the shipped image to /output/entry.png and checks it
against the sealed scorer's gate before it writes anything.

Gate (RULES.txt): /output/entry.png must be a whole PNG or JPEG, at most
1 MiB (1,048,576 bytes) and at most 1024 by 1024 pixels. Anything outside
the gate exits non-zero and writes nothing.
"""

import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "letter.jpg")
OUT_DIR = "/output"
OUT_PATH = os.path.join(OUT_DIR, "entry.png")
MAX_BYTES = 1_048_576
MAX_SIDE = 1024


def jpeg_dimensions(path):
    """Return (width, height) of a JPEG by scanning for its SOF marker."""
    with open(path, "rb") as handle:
        data = handle.read()
    if data[:2] != b"\xff\xd8" or data[-2:] != b"\xff\xd9":
        raise ValueError("not a whole JPEG (missing SOI/EOI markers)")
    pos = 2
    while pos < len(data) - 1:
        if data[pos] != 0xFF:
            pos += 1
            continue
        marker = data[pos + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height = struct.unpack(">H", data[pos + 5:pos + 7])[0]
            width = struct.unpack(">H", data[pos + 7:pos + 9])[0]
            return width, height
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        seg_len = struct.unpack(">H", data[pos + 2:pos + 4])[0]
        pos += 2 + seg_len
    raise ValueError("no SOF marker found in JPEG")


def main():
    size = os.path.getsize(SOURCE)
    if size > MAX_BYTES:
        print(f"FAIL: letter.jpg is {size} bytes, over the 1 MiB cap", file=sys.stderr)
        return 1
    width, height = jpeg_dimensions(SOURCE)
    if width > MAX_SIDE or height > MAX_SIDE:
        print(f"FAIL: letter.jpg is {width}x{height}, over 1024x1024", file=sys.stderr)
        return 1
    os.makedirs(OUT_DIR, exist_ok=True)
    shutil.copyfile(SOURCE, OUT_PATH)
    written = os.path.getsize(OUT_PATH)
    if written != size:
        print(f"FAIL: copy truncated ({written} of {size} bytes)", file=sys.stderr)
        os.remove(OUT_PATH)
        return 1
    print(f"OK: wrote {OUT_PATH} ({written} bytes, {width}x{height} JPEG)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
