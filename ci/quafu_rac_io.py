#!/usr/bin/env python3
# CLASSIFY: L1
"""Strict JSON loading and atomic evidence writes; no platform or credential operations."""
import json
import os
from pathlib import Path


def _unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON object member: {key!r}")
        out[key] = value
    return out


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


def json_text(payload):
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def json_bytes(payload):
    return json_text(payload).encode("utf-8")


def write_json_atomic(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp-{os.getpid()}")
    try:
        # write_text is intentionally used here so fault injection can exercise partial-write cleanup.
        tmp.write_text(json_text(payload), encoding="utf-8")
        with tmp.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()
