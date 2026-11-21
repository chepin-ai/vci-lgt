#!/usr/bin/env python3
# CLASSIFY: L1
"""Strict JSON and crash-oriented evidence writes; no platform or credential operations."""
import json
import os
import tempfile
from pathlib import Path


def _unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON object member: {key!r}")
        out[key] = value
    return out


def _reject_nonfinite(constant):
    raise ValueError(f"non-finite JSON number forbidden: {constant}")


def load_json(path):
    return json.loads(
        Path(path).read_text(encoding="utf-8"),
        object_pairs_hook=_unique_object,
        parse_constant=_reject_nonfinite,
    )


def json_text(payload):
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"


def json_bytes(payload):
    return json_text(payload).encode("utf-8")


def write_json_atomic(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # O_EXCL-backed mkstemp avoids PID-only collisions between same-process writers.
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".tmp-", dir=path.parent)
    os.close(fd)
    tmp = Path(tmp_name)
    directory_fd = None
    try:
        # write_text is intentionally used here so fault injection can exercise partial-write cleanup.
        tmp.write_text(json_text(payload), encoding="utf-8")
        with tmp.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        # Persist the rename itself on filesystems that honor directory fsync.
        # This is a syscall-level durability boundary, not a power-loss proof.
        directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        os.fsync(directory_fd)
    finally:
        if directory_fd is not None:
            os.close(directory_fd)
        if tmp.exists():
            tmp.unlink()
