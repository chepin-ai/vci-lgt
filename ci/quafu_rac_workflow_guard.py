#!/usr/bin/env python3
# CLASSIFY: L1
"""Fail-closed workflow receipt guard. It never contacts a quantum platform."""
import argparse
import datetime
import json
import os
import sys
from pathlib import Path

from quafu_rac_io import load_json, write_json_atomic


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_receipt(path):
    path = Path(path)
    if path.exists():
        print(json.dumps({"created": False, "path": str(path)}, ensure_ascii=False))
        return
    now = utcnow()
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    payload = {
        "schema": "lgt.quafu.rac.receipt.v1",
        "experiment_id": "V147-QUAFU-RAC-PILOT-01",
        "mode": os.environ.get("MODE", "UNKNOWN").upper(),
        "started_utc": now,
        "finished_utc": now,
        "sdk": "pyquafu==0.4.5",
        "new_quantum_jobs_confirmed": 0,
        "send_attempts": 0,
        "new_quantum_jobs_uncertain": False,
        "S_real_pilot": None,
        "task_id": None,
        "ok": False,
        "error": {
            "type": "MissingReceipt",
            "message": "producer created no parseable receipt; workflow guard synthesized failure evidence",
        },
        "workflow_guard": {
            "run_id": int(run_id) if run_id.isdigit() else None,
            "run_attempt": int(os.environ.get("GITHUB_RUN_ATTEMPT", "1")),
            "semantic": "missing producer evidence is a failure, never a green run",
        },
    }
    write_json_atomic(path, payload)
    print(json.dumps({"created": True, "path": str(path), "ok": False}, ensure_ascii=False))


def receipt_ok(path):
    try:
        payload = load_json(path)
        ok = payload.get("ok")
        if type(ok) is not bool:
            raise ValueError("receipt ok must be boolean")
        print("true" if ok else "false")
    except Exception as exc:
        # Keep the raw evidence for commit/artifact; the shell wrapper fails after its bounded push.
        print("invalid")
        print(f"receipt guard: {type(exc).__name__}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["ensure", "ok"])
    parser.add_argument("path")
    args = parser.parse_args()
    if args.command == "ensure":
        ensure_receipt(args.path)
    else:
        receipt_ok(args.path)


if __name__ == "__main__":
    main()
