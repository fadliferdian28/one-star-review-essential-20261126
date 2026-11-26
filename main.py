#!/usr/bin/env python3
"""Copy the verified one-star review to the make.fun output directory."""

import hashlib
import os
import shutil
import sys
from pathlib import Path

EXPECTED_SHA256 = "1e5013ef536f4523a38170556223affd9e86f5f164eee161208626a4fce5d9ac"

MIN_CHARS = 1
MAX_CHARS = 160


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    return 1


def main():
    entry_path = Path(__file__).resolve().parent / "entry.txt"

    if not entry_path.is_file():
        return fail(f"entry.txt not found next to main.py ({entry_path})")

    raw = entry_path.read_bytes()

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return fail(f"entry.txt is not valid UTF-8: {exc}")

    char_count = len(text)
    if not MIN_CHARS <= char_count <= MAX_CHARS:
        return fail(
            f"entry.txt has {char_count} characters; must be "
            f"{MIN_CHARS}-{MAX_CHARS}."
        )
    if not text.strip():
        return fail("entry.txt is whitespace-only.")

    actual_sha256 = hashlib.sha256(raw).hexdigest()
    if actual_sha256 != EXPECTED_SHA256:
        return fail(
            "sha256 mismatch: expected "
            f"{EXPECTED_SHA256}, got {actual_sha256}"
        )

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return fail(f"could not create output directory {out_dir}: {exc}")

    if not out_dir.is_dir():
        return fail(f"output path is not a directory: {out_dir}")
    if not os.access(out_dir, os.W_OK):
        return fail(f"output directory is not writable: {out_dir}")

    out_path = out_dir / "entry.txt"

    try:
        shutil.copyfile(entry_path, out_path)
    except shutil.SameFileError:
        print(f"source and destination are the same file; nothing to copy: {out_path}")
    except OSError as exc:
        return fail(f"could not copy to {out_path}: {exc}")

    print(f"characters: {char_count}")
    print(f"sha256: {actual_sha256}")
    print(f"copied to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
