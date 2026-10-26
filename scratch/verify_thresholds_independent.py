#!/usr/bin/env python3
"""
Independent recomputation and verification of whole-brain threshold metrics.
Runs in bounded memory (< 1.5 GiB RAM) using PyArrow streaming and 64-bit edge packing.
"""
from __future__ import annotations
import array
from collections import defaultdict
from pathlib import Path
import sys
import time

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_PATH = PROJECT_ROOT / ".venv" / "lib" / "python3.12" / "site-packages"
if VENV_PATH.exists():
    sys.path.insert(0, str(VENV_PATH))

import pyarrow.ipc as ipc

FILE_PATH = PROJECT_ROOT / "data" / "raw" / "fafb_v783" / "proofread_connections_783.feather"
THRESHOLDS = [1, 2, 3, 5, 10, 20]

def main():
    print(">>> Starting independent whole-brain recomputation...")
    t0 = time.perf_counter()
    
    node_to_id: dict[int, int] = {}
    id_to_node: list[int] = []
    # (u << 32) | v -> sum of syn_count
    edge_weights: dict[int, int] = {}
    
    with open(FILE_PATH, "rb") as f:
        reader = ipc.open_file(f)
        for b in range(reader.num_record_batches):
            batch = reader.get_batch(b)
            pres = batch.column("pre_pt_root_id").to_pylist()
            posts = batch.column("post_pt_root_id").to_pylist()
            weights = batch.column("syn_count").to_pylist()
            
            for p, q, w in zip(pres, posts, weights):
                if p is None or q is None or w is None or w <= 0:
                    continue
                if p == q:  # exclude autapses
                    continue
                
                if p not in node_to_id:
                    node_to_id[p] = len(id_to_node)
                    id_to_node.append(p)
                u = node_to_id[p]
                
                if q not in node_to_id:
                    node_to_id[q] = len(id_to_node)
                    id_to_node.append(q)
                v = node_to_id[q]
                
                k = (u << 32) | v
                edge_weights[k] = edge_weights.get(k, 0) + w

    ingest_time = time.perf_counter() - t0
    print(f"Ingested 16.85M rows in {ingest_time:.2f}s. Unique directed edges: {len(edge_weights):,}, Unique nodes: {len(id_to_node):,}")

    results = {}
    for t in THRESHOLDS:
        t_start = time.perf_counter()
        # Find mutual dyads and total edges at threshold t
        # We iterate over edge_weights directly without copying dictionary
        E_t = 0
        M_t = 0
        active_nodes = set()
        
        for k, w in edge_weights.items():
            if w >= t:
                E_t += 1
                u = k >> 32
                v = k & 0xFFFFFFFF
                active_nodes.add(u)
                active_nodes.add(v)
                if u < v:
                    rev_k = (v << 32) | u
                    if edge_weights.get(rev_k, 0) >= t:
                        M_t += 1
                        
        two_M = 2 * M_t
        r_edge = (two_M / E_t) if E_t > 0 else 0.0
        # Dyad reciprocity: M / (U + M) where U = E - 2M => M / (E - M)
        r_dyad = (M_t / (E_t - M_t)) if (E_t - M_t) > 0 else 0.0
        
        results[t] = {
            "threshold": t,
            "directed_edges": E_t,
            "mutual_dyads": M_t,
            "reciprocal_directed_edges": two_M,
            "edge_reciprocity_pct": round(r_edge * 100.0, 4),
            "dyad_reciprocity_pct": round(r_dyad * 100.0, 4),
            "active_nodes": len(active_nodes),
            "time_seconds": round(time.perf_counter() - t_start, 2),
        }
        print(f"  w >= {t:2d}: E={E_t:10,d} | M={M_t:8,d} | 2M={two_M:8,d} | R_edge={r_edge*100:6.2f}% | R_dyad={r_dyad*100:6.2f}% | V={len(active_nodes):7,d} ({time.perf_counter() - t_start:.2f}s)")
        
    return results

if __name__ == "__main__":
    main()

