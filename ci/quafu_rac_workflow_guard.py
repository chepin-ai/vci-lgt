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
    fence_path = Path.cwd() / "ci" / "QUAFU-RAC-FIRE-SPENT-LGT-01.json"
    spend = {}
    fence_incorporated = fence_path.exists()
    if fence_incorporated:
        # A missing producer receipt must never erase the no-retry boundary.  Even an
        # unreadable fence is treated conservatively as one uncertain send attempt.
        spend = {
            "send_attempts": 1,
            "new_quantum_jobs_confirmed": 0,
            "new_quantum_jobs_uncertain": True,
            "submission_outcome": "UNCERTAIN_NO_RETRY",
            "spend_fence": {
                "path": "ci/QUAFU-RAC-FIRE-SPENT-LGT-01.json",
                "status": "UNREADABLE_FENCE_FAIL_CLOSED",
                "no_retry": True,
            },
        }
        try:
            fence = load_json(fence_path)
            if fence.get("schema") != "lgt.quafu.rac.fire-spent.v1":
                raise ValueError("invalid spend fence schema")
            if fence.get("experiment_id") != "V147-QUAFU-RAC-PILOT-01":
                raise ValueError("spend fence experiment mismatch")
            status = fence.get("status")
            attempts = fence.get("send_attempts")
            confirmed = fence.get("new_quantum_jobs_confirmed")
            uncertain = fence.get("new_quantum_jobs_uncertain")
            entered = fence.get("send_call_entered")
            if status not in {"SEND_ATTEMPT_FENCED", "UNCERTAIN_NO_RETRY", "CONFIRMED_NO_RETRY"}:
                raise ValueError("invalid spend fence status")
            if type(attempts) is not int or attempts != 1:
                raise ValueError("invalid spend fence send attempts")
            if type(confirmed) is not int or confirmed not in (0, 1):
                raise ValueError("invalid spend fence confirmed counter")
            if type(uncertain) is not bool or type(entered) is not bool:
                raise ValueError("invalid spend fence boolean flags")
            if fence.get("no_retry") is not True:
                raise ValueError("spend fence no_retry must be true")
            task_id = fence.get("task_id")
            if task_id is not None and not isinstance(task_id, str):
                raise ValueError("invalid spend fence task identity")
            if status == "CONFIRMED_NO_RETRY" and (confirmed != 1 or not (isinstance(task_id, str) and task_id.strip())):
                raise ValueError("confirmed fence lacks confirmed job evidence or nonempty task identity")
            if status != "CONFIRMED_NO_RETRY" and confirmed != 0:
                raise ValueError("unconfirmed fence has confirmed job evidence")
            if status == "UNCERTAIN_NO_RETRY" and uncertain is not True:
                raise ValueError("uncertain fence lacks uncertain flag")
            spend.update({
                "send_attempts": attempts,
                "new_quantum_jobs_confirmed": confirmed,
                "new_quantum_jobs_uncertain": uncertain or confirmed == 0,
                "submission_outcome": "CONFIRMED_NO_RETRY" if confirmed else "UNCERTAIN_NO_RETRY",
                "task_id": task_id,
                "spend_fence": {
                    "path": "ci/QUAFU-RAC-FIRE-SPENT-LGT-01.json",
                    "status": status,
                    "no_retry": True,
                },
            })
        except Exception as exc:
            spend["spend_fence"]["error"] = {
                "type": type(exc).__name__, "message": str(exc)[:600],
            }
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
            "spend_fence_incorporated": fence_incorporated,
        },
    }
    payload.update(spend)
    write_json_atomic(path, payload)
    print(json.dumps({"created": True, "path": str(path), "ok": False,
                      "spend_fence_incorporated": fence_incorporated}, ensure_ascii=False))


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
