#!/usr/bin/env python3
"""Cross-retrieval canonical-counts immutability audit; no platform calls."""
import hashlib, json

BITS=("00","01","10","11")
SCHEMA="lgt.quafu.rac.retrieval-history.v1"

def canonical_counts(counts):
    if counts is None:
        counts={}
    if not isinstance(counts,dict):
        raise ValueError("counts must be a mapping")
    clean={}
    for key,value in counts.items():
        bits=''.join(str(key).split())
        if bits not in BITS:
            raise ValueError("pilot counts require two-bit keys")
        n=int(value)
        if n<0:
            raise ValueError("negative count")
        clean[bits]=clean.get(bits,0)+n
    return {k:clean.get(k,0) for k in BITS}

def counts_sha256(counts):
    canonical=canonical_counts(counts)
    return hashlib.sha256(json.dumps(canonical,sort_keys=True).encode()).hexdigest()

def make_snapshot(run_id,task_id,task_status,counts,receipt_path,receipt_sha256,retrieved_utc):
    if not task_id or not task_status:
        raise ValueError("task id and status required")
    canonical=canonical_counts(counts)
    return {
        "run_id":int(run_id),
        "task_id":str(task_id),
        "task_status":str(task_status),
        "counts":canonical,
        "counts_sha256":counts_sha256(canonical),
        "receipt_path":str(receipt_path),
        "receipt_sha256":str(receipt_sha256),
        "retrieved_utc":str(retrieved_utc),
    }

def audit_history(history):
    if history.get("schema")!=SCHEMA:
        raise ValueError("history schema mismatch")
    snapshots=history.get("snapshots",[])
    if not isinstance(snapshots,list):
        raise ValueError("snapshots must be a list")
    task_id=history.get("task_id")
    for snap in snapshots:
        if snap.get("task_id")!=task_id:
            raise ValueError("cross-task history contamination")
        expected=counts_sha256(snap.get("counts",{}))
        if snap.get("counts_sha256")!=expected:
            raise ValueError("snapshot counts hash mismatch")
    completed=[s for s in snapshots if s.get("task_status")=="Completed"]
    hashes=sorted(set(s["counts_sha256"] for s in completed))
    violation=len(hashes)>1
    if not completed:
        status="NO_COMPLETED"
    elif violation:
        status="IMMUTABLE_VIOLATION"
    elif len(completed)==1:
        status="FIRST_COMPLETED"
    else:
        status="IMMUTABLE_OK"
    return {
        "status":status,
        "snapshots":len(snapshots),
        "completed_snapshots":len(completed),
        "distinct_completed_counts_sha256":hashes,
        "immutable_violation":violation,
        "scoring_allowed":not violation,
        "rule":"Completed canonical counts must be byte-identical across retrieval; never select a preferred result",
    }

def append_snapshot(history,snapshot):
    if history.get("schema")!=SCHEMA or snapshot.get("task_id")!=history.get("task_id"):
        raise ValueError("history or task mismatch")
    snapshots=history.setdefault("snapshots",[])
    duplicate=[s for s in snapshots if s.get("run_id")==snapshot.get("run_id")]
    if duplicate:
        if duplicate[0]!=snapshot:
            raise ValueError("same run id with different snapshot")
    else:
        snapshots.append(snapshot)
    history["audit"]=audit_history(history)
    return history
