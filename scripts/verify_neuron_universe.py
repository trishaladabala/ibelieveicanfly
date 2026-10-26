#!/usr/bin/env python3
"""
Verify and Reconcile FlyWire Proofread Neuron Universe.

Reconciles the 138,639 unique neuron IDs in proofread_connections_783.feather
against the 139,255 proofread root IDs in proofread_root_ids_783.npy.
"""

from __future__ import annotations

import json
import struct
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_PATH = PROJECT_ROOT / ".venv" / "lib" / "python3.12" / "site-packages"
if VENV_PATH.exists():
    sys.path.insert(0, str(VENV_PATH))

import pyarrow.ipc as ipc


def reconcile_neurons() -> dict:
    start_time = time.perf_counter()
    raw_dir = PROJECT_ROOT / "data" / "raw" / "fafb_v783"
    npy_path = raw_dir / "proofread_root_ids_783.npy"
    feather_path = raw_dir / "proofread_connections_783.feather"

    if not npy_path.exists():
        raise FileNotFoundError(f"Missing {npy_path}")
    if not feather_path.exists():
        raise FileNotFoundError(f"Missing {feather_path}")

    # 1. Read official 139,255 proofread IDs from NPY binary
    with open(npy_path, "rb") as f:
        f.seek(8)
        hlen = int.from_bytes(f.read(2), "little")
        f.seek(10 + hlen)
        raw = f.read()
        num_ids = len(raw) // 8
        proofread_ids = set(struct.unpack(f"<{num_ids}Q", raw))

    # 2. Extract unique presynaptic and postsynaptic IDs from connection table
    pre_ids = set()
    post_ids = set()
    with open(feather_path, "rb") as f:
        reader = ipc.open_file(f)
        for b in range(reader.num_record_batches):
            batch = reader.get_batch(b)
            pre_ids.update(batch.column("pre_pt_root_id").to_pylist())
            post_ids.update(batch.column("post_pt_root_id").to_pylist())

    conn_ids = pre_ids | post_ids
    only_pre = pre_ids - post_ids
    only_post = post_ids - pre_ids
    both_pre_post = pre_ids & post_ids

    missing_from_conn = proofread_ids - conn_ids
    in_conn_not_proofread = conn_ids - proofread_ids

    res = {
        "metadata": {
            "execution_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dataset_version": "FlyWire FAFB v783.0",
            "proofread_array_file": npy_path.name,
            "connections_table_file": feather_path.name,
            "runtime_seconds": round(time.perf_counter() - start_time, 2),
        },
        "population_counts": {
            "official_proofread_neurons_total": len(proofread_ids),
            "represented_in_connections_total": len(conn_ids),
            "presynaptic_active_neurons": len(pre_ids),
            "postsynaptic_active_neurons": len(post_ids),
            "bidirectional_active_neurons": len(both_pre_post),
            "pure_source_neurons_only_pre": len(only_pre),
            "pure_target_neurons_only_post": len(only_post),
            "unconnected_proofread_neurons": len(missing_from_conn),
            "unconnected_percentage_of_reconstruction": round(len(missing_from_conn) / len(proofread_ids) * 100.0, 3),
            "non_proofread_neurons_in_connections": len(in_conn_not_proofread),
        },
        "omitted_neuron_ids_sample": sorted(list(missing_from_conn))[:50],
    }

    out_json = PROJECT_ROOT / "results" / "real_data_pilot" / "neuron_universe_reconciliation.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)

    print(f"Reconciliation completed in {res['metadata']['runtime_seconds']}s. Saved to: {out_json}")
    return res


if __name__ == "__main__":
    reconcile_neurons()

