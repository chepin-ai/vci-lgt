#!/usr/bin/env python3
"""Rebuild V-150 evidence from raw receipts; never imports production analyzers."""
import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np

W = Path(__file__).resolve().parent
REPO_LAYOUT = W.name == "ci" and (W.parent / "receipts").is_dir()
ROOT = W.parent
BASE = W.parent if REPO_LAYOUT else W
CI = W
BITS = ("00", "01", "10", "11")
TASK_ID = "91C842B01A238734"
SENTINEL = "UNSEALED_CURRENT_RECEIPT"
LATEST_READBACK_SHA256 = "91b0c3d42d78045f9be5d3091367f4afbc738794f025e082880d59e1c8abf5c1"
TS = (W / "TS_PLAN").read_text().strip() if (W / "TS_PLAN").exists() else "2026-11-10T04:18:49Z"


def load(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(raw):
    if raw is None:
        raw = {}
    assert isinstance(raw, dict)
    merged = {k: 0 for k in BITS}
    for key, value in raw.items():
        bits = "".join(str(key).split())
        assert bits in BITS
        assert type(value) is int and value >= 0
        merged[bits] += value
    return merged


def counts_hash(raw):
    clean = canonical(raw)
    payload = json.dumps(clean, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


if REPO_LAYOUT:
    receipt_paths = {rid: BASE / "receipts" / f"quafu-rac-{rid}.json" for rid in [
        "41922417262", "42160979350", "41922704802", "41923004075",
        "41931682046", "42155450189", "42755343750"]}
else:
    receipt_paths = {
        "41922417262": ROOT / "V-147/quafu-rac-41922417262.json",
        "42160979350": W / "quafu-rac-42160979350.json",
        "41922704802": ROOT / "V-147/quafu-rac-41922704802.json",
        "41923004075": ROOT / "V-147/quafu-rac-41923004075.json",
        "41931682046": ROOT / "V-148/quafu-rac-41931682046.json",
        "42155450189": ROOT / "V-149/quafu-rac-42155450189.json",
        "42755343750": W / "quafu-rac-42755343750.json",
    }
receipts = {rid: load(path) for rid, path in receipt_paths.items()}
receipt_hashes = {rid: sha(path) for rid, path in receipt_paths.items()}

# Recompute the preregistration digest from source JSON, independently of production code.
prereg_path = CI / "QUAFU-RAC-PREFLIGHT-LGT-01.json"
prereg = load(prereg_path)
prereg_digest = hashlib.sha256(
    json.dumps(prereg, ensure_ascii=False, sort_keys=True).encode()
).hexdigest()
assert prereg_digest == "563445cc8b420950a42f2aba9e027d367d6568f3888091ded87a7abb9fa10f40"
for rid, receipt in receipts.items():
    assert receipt["schema"] == "lgt.quafu.rac.receipt.v1"
    assert receipt["experiment_id"] == prereg["experiment_id"]
    assert receipt["prereg_sha256"] == prereg_digest
    assert receipt["S_real_pilot"] is None

# Rebuild FIRE identity and QASM hash from the raw FIRE receipt.
fire = receipts["41922704802"]
assert fire["mode"] == "FIRE" and fire["ok"] is True
assert fire["task_id"] == TASK_ID
assert fire["send_attempts"] == 1
assert fire["new_quantum_jobs_confirmed"] == 1
assert fire["new_quantum_jobs_uncertain"] is False
assert fire["selected_backend"]["name"] == prereg["backend_policy"]["selected"] == "ScQ-P5"
qasm = fire["pilot"]["openqasm"]
qasm_digest = hashlib.sha256(qasm.encode()).hexdigest()
assert qasm_digest == fire["pilot"]["qasm_sha256"]
assert qasm_digest == "24aea2fed6cea4bb6aa1532278b7d33984640de8055acdca29462ace0c0921c6"
assert fire["pilot"]["x1"] == fire["pilot"]["x2"] == 1
assert fire["pilot"]["basis"] == "X" and fire["pilot"]["expected_parity"] == 1

# Independent state-vector reconstruction. Index bit order is q0,q1 (q0 leftmost).
H = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
operations = []
for line in qasm.splitlines():
    line = line.strip()
    if line.startswith("h q["):
        operations.append(("h", int(re.search(r"q\[(\d+)\]", line).group(1)), None))
    elif line.startswith("x q["):
        operations.append(("x", int(re.search(r"q\[(\d+)\]", line).group(1)), None))
    elif line.startswith("z q["):
        operations.append(("z", int(re.search(r"q\[(\d+)\]", line).group(1)), None))
    elif line.startswith("cx q["):
        nums = [int(x) for x in re.findall(r"q\[(\d+)\]", line)]
        operations.append(("cx", nums[0], nums[1]))
assert operations[-2:] == [("h", 0, None), ("h", 1, None)]


def apply_one(state, gate, qubit, nqubits=2):
    out = state.copy()
    for index in range(1 << nqubits):
        if ((index >> (nqubits - 1 - qubit)) & 1) == 0:
            other = index | (1 << (nqubits - 1 - qubit))
            a, b = state[index], state[other]
            out[index] = gate[0, 0] * a + gate[0, 1] * b
            out[other] = gate[1, 0] * a + gate[1, 1] * b
    return out


def apply_cx(state, control, target, nqubits=2):
    out = np.zeros_like(state)
    for index, amplitude in enumerate(state):
        c = (index >> (nqubits - 1 - control)) & 1
        t = (index >> (nqubits - 1 - target)) & 1
        destination = index
        if c:
            destination ^= 1 << (nqubits - 1 - target)
        out[destination] += amplitude
    return out


def evolve(ops):
    state = np.array([1, 0, 0, 0], dtype=complex)
    for name, a, b in ops:
        if name == "cx":
            state = apply_cx(state, a, b)
        else:
            state = apply_one(state, {"h": H, "x": X, "z": Z}[name], a)
    return state


pre_basis = evolve(operations[:-2])
psi_minus = np.array([0, 1, -1, 0], dtype=complex) / math.sqrt(2)
fidelity = abs(np.vdot(psi_minus, pre_basis)) ** 2
xx = np.kron(X, X)
xx_expectation = float(np.real(np.vdot(pre_basis, xx @ pre_basis)))
final_state = evolve(operations)
probabilities = {format(i, "02b"): float(abs(a) ** 2) for i, a in enumerate(final_state)}
assert abs(fidelity - 1) < 1e-12
assert abs(xx_expectation + 1) < 1e-12
assert abs(probabilities["01"] - 0.5) < 1e-12
assert abs(probabilities["10"] - 0.5) < 1e-12
assert abs(probabilities["00"]) < 1e-12 and abs(probabilities["11"]) < 1e-12

# Rebuild every retrieval snapshot directly from its raw receipt.
retrieve_ids = ["41923004075", "41931682046", "42155450189", "42755343750"]
history_path = CI / "QUAFU-RAC-RETRIEVAL-HISTORY-LGT-01.json"
history = load(history_path)
assert history["schema"] == "lgt.quafu.rac.retrieval-history.v1"
assert history["task_id"] == TASK_ID
assert len(history["snapshots"]) == len(retrieve_ids)
assert receipt_hashes[retrieve_ids[-1]] == LATEST_READBACK_SHA256
latest_meta = W / "v150_receipt_fetch.json"
latest_fetch = load(latest_meta) if latest_meta.exists() else None
if latest_fetch is not None:
    assert latest_fetch["run_id"] == int(retrieve_ids[-1])
    assert latest_fetch["receipt_sha256"] == receipt_hashes[retrieve_ids[-1]]
rebuilt = []
receipt_hash_checks = []
for rid, stored in zip(retrieve_ids, history["snapshots"]):
    receipt = receipts[rid]
    retrieval = receipt["retrieval"]
    assert receipt["mode"] == "RETRIEVE" and receipt["ok"] is True
    assert receipt["task_id"] == retrieval["task_id"] == TASK_ID
    assert receipt["send_attempts"] == 0
    assert receipt["new_quantum_jobs_confirmed"] == 0
    assert receipt["new_quantum_jobs_uncertain"] is False
    clean = canonical(retrieval["counts"])
    path = f"receipts/quafu-rac-{rid}.json"
    expected_hash = SENTINEL if rid == retrieve_ids[-1] else receipt_hashes[rid]
    snap = {
        "run_id": int(rid),
        "task_id": TASK_ID,
        "task_status": retrieval["task_status"],
        "counts": clean,
        "counts_sha256": counts_hash(clean),
        "receipt_path": path,
        "receipt_sha256": expected_hash,
        "retrieved_utc": receipt["finished_utc"],
    }
    assert stored == snap, (rid, stored, snap)
    if rid == retrieve_ids[-1]:
        closure = "sentinel resolved by independent readback receipt hash"
        if latest_fetch is not None:
            assert latest_fetch["receipt_path"] == path
    else:
        closure = "direct raw-byte SHA-256 equality"
    receipt_hash_checks.append({"run_id": int(rid), "path": path, "actual_sha256": receipt_hashes[rid], "stored_field": expected_hash, "closure": closure})
    rebuilt.append(snap)

# Independent immutable/terminal audit over rebuilt snapshots, without production imports.
completed = [s for s in rebuilt if s["task_status"] == "Completed"]
completed_hashes = sorted({s["counts_sha256"] for s in completed})
counts_violation = len(completed_hashes) > 1
terminal_positions = [i for i, s in enumerate(rebuilt) if s["task_status"] in {"Completed", "Failed", "Canceled"}]
regressions = []
if terminal_positions:
    first_index = terminal_positions[0]
    first = rebuilt[first_index]
    for later in rebuilt[first_index + 1:]:
        if later["task_status"] != first["task_status"]:
            regressions.append({
                "from_run_id": first["run_id"], "from_status": first["task_status"],
                "to_run_id": later["run_id"], "to_status": later["task_status"],
            })
terminal_violation = bool(regressions)
violation = counts_violation or terminal_violation
if violation:
    status = "IMMUTABLE_VIOLATION"
elif not completed:
    status = "NO_COMPLETED"
elif len(completed) == 1:
    status = "FIRST_COMPLETED"
else:
    status = "IMMUTABLE_OK"
audit = {
    "status": status,
    "snapshots": len(rebuilt),
    "completed_snapshots": len(completed),
    "distinct_completed_counts_sha256": completed_hashes,
    "immutable_violation": violation,
    "counts_immutable_violation": counts_violation,
    "terminal_status_violation": terminal_violation,
    "terminal_status_regressions": regressions,
    "scoring_allowed": not violation,
    "rule": "Completed canonical counts and terminal status must be immutable across retrieval; never select a preferred result",
}
assert history["audit"] == audit

# Rebuild the real-job ledger from all raw SIM/FIRE/RETRIEVE receipts.
sim_ids = ["41922417262", "42160979350"]
for rid in sim_ids:
    r = receipts[rid]
    assert r["mode"] == "SIM" and r["ok"] is True
    assert r["task_id"] is None and r["send_attempts"] == 0
    assert r["new_quantum_jobs_confirmed"] == 0 and r["new_quantum_jobs_uncertain"] is False
ledger = {
    "sim_runs": [int(x) for x in sim_ids],
    "fire_runs": [41922704802],
    "retrieve_runs": [int(x) for x in retrieve_ids],
    "fire_send_attempts": sum(receipts[x]["send_attempts"] for x in ["41922704802"]),
    "retrieve_send_attempts": sum(receipts[x]["send_attempts"] for x in retrieve_ids),
    "sim_send_attempts": sum(receipts[x]["send_attempts"] for x in sim_ids),
    "new_quantum_jobs_confirmed": sum(receipts[x]["new_quantum_jobs_confirmed"] for x in receipts),
    "new_quantum_jobs_uncertain_any": any(receipts[x]["new_quantum_jobs_uncertain"] for x in receipts),
    "real_chip_task_ids": [TASK_ID],
    "backend": "ScQ-P5",
    "preregistered_shots": prereg["real_submission"]["shots"],
    "latest_observed_task_status": receipts[retrieve_ids[-1]]["retrieval"]["task_status"],
    "S_real_pilot": None,
    "S_real_eight_cell": None,
    "real_chip_qrand_executed": False,
}
assert ledger["fire_send_attempts"] == 1
assert ledger["retrieve_send_attempts"] == ledger["sim_send_attempts"] == 0
assert ledger["new_quantum_jobs_confirmed"] == 1
assert ledger["new_quantum_jobs_uncertain_any"] is False
assert ledger["latest_observed_task_status"] == "In Queue"

out = {
    "schema": "lgt.quafu.rac.v150-independent-rebuild.v1",
    "beat": "V-150",
    "ts": TS,
    "verdict": "PASS",
    "method": "raw-receipt rebuild; no production analyzer or immutable-module import",
    "source_receipts": [{"run_id": int(rid), "mode": receipts[rid]["mode"], "sha256": receipt_hashes[rid]} for rid in receipt_paths],
    "prereg": {"canonical_sha256": prereg_digest, "all_receipts_match": True},
    "fire": {"run_id": 41922704802, "task_id": TASK_ID, "qasm_sha256": qasm_digest, "send_attempts": 1, "new_quantum_jobs_confirmed": 1},
    "statevector_reconstruction": {"bit_order": "q0 leftmost", "pre_basis_fidelity_to_psi_minus": fidelity, "xx_expectation": xx_expectation, "ideal_measurement_probabilities": probabilities, "odd_parity_probability": probabilities["01"] + probabilities["10"]},
    "history_rebuild": {"snapshots": rebuilt, "audit": audit, "receipt_hash_checks": receipt_hash_checks, "stored_history_sha256": sha(history_path), "exact_snapshot_equality": True, "exact_audit_equality": True},
    "real_job_ledger": ledger,
    "real_platform_calls_by_this_rebuild": 0,
    "real_quantum_jobs_by_this_rebuild": 0,
    "weakening": "All four real retrievals remain In Queue with empty counts. No real counts, S_real_pilot, eight-cell S_real or real-chip QRAND result exists. Ideal state-vector checks are not hardware certification.",
}
(CI / "QUAFU-RAC-V150-INDEPENDENT-REBUILD-LGT-01.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
)
print(json.dumps({
    "verdict": out["verdict"],
    "receipts": len(receipts),
    "snapshots": len(rebuilt),
    "audit": status,
    "ideal_probabilities": probabilities,
    "new_quantum_jobs_confirmed_total": ledger["new_quantum_jobs_confirmed"],
    "latest_task_status": ledger["latest_observed_task_status"],
    "platform_calls": 0,
}, ensure_ascii=False, indent=2))
