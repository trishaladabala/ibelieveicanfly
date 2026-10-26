#!/usr/bin/env python3
"""
extract_fb_subgraph.py

Streams the official FlyWire FAFB v783 aggregated connectivity feather file
(proofread_connections_783.feather) to extract the Fan-Shaped Body (FB) subgraph
at threshold w >= 5 (primary) and w >= 3 (sensitivity).

Computes:
1. Whole-brain synapse-weighted consensus neurotransmitter assignments and confidence scores.
2. Filtered FB directed edges, autapse segregation, and mutual dyad extraction.
3. Node covariates: in-degree, out-degree, mutual degree, total degree, synaptic strength.
4. Generates data/fb_node_covariates.json for fast, reproducible downstream analyses.

Verified against Phase 6 authoritative baseline:
- FB w >= 5: 2,465 active nodes, 46,903 directed edges, 5,435 mutual dyads.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import resource
import sys
import time
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PROJECT_ROOT = REPO_ROOT.parent
VENV_PATH = PROJECT_ROOT / ".venv" / "lib" / "python3.12" / "site-packages"
if VENV_PATH.exists():
    sys.path.insert(0, str(VENV_PATH))

import pyarrow.ipc as ipc

FEATHER_FILE = PROJECT_ROOT / "data" / "raw" / "fafb_v783" / "proofread_connections_783.feather"
OUT_CACHE = REPO_ROOT / "data" / "fb_node_covariates.json"

NT_CLASSES = ["ach", "gaba", "glut", "da", "oct", "ser"]
NT_INDEX = {name: i for i, name in enumerate(NT_CLASSES)}


def get_peak_memory_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def extract_fb_data(feather_path: Path, primary_threshold: int = 5) -> dict[str, Any]:
    print(f"Opening {feather_path} ...")
    t0 = time.perf_counter()

    neuron_outputs = defaultdict(lambda: [0.0] * 6)
    fb_edges: dict[tuple[int, int], dict[str, Any]] = {}
    fb_autapses: dict[int, int] = defaultdict(int)

    total_records = 0
    records_with_nt = 0
    total_synapses = 0
    synapses_with_nt = 0

    with open(feather_path, "rb") as f:
        reader = ipc.RecordBatchFileReader(f)
        num_batches = reader.num_record_batches
        print(f"Processing {num_batches} record batches...")

        for b_idx in range(num_batches):
            batch = reader.get_record_batch(b_idx)
            num_rows = batch.num_rows
            total_records += num_rows

            pre_arr = batch.column("pre_pt_root_id")
            post_arr = batch.column("post_pt_root_id")
            syn_arr = batch.column("syn_count")
            np_arr = batch.column("neuropil")
            ach_arr = batch.column("ach_avg")
            gaba_arr = batch.column("gaba_avg")
            glut_arr = batch.column("glut_avg")
            da_arr = batch.column("da_avg")
            oct_arr = batch.column("oct_avg")
            ser_arr = batch.column("ser_avg")

            for r_idx in range(num_rows):
                pre = pre_arr[r_idx].as_py()
                post = post_arr[r_idx].as_py()
                syn = syn_arr[r_idx].as_py()
                total_synapses += syn

                v_ach = ach_arr[r_idx].as_py()
                if v_ach is not None:
                    records_with_nt += 1
                    synapses_with_nt += syn

                    v_gaba = gaba_arr[r_idx].as_py()
                    v_glut = glut_arr[r_idx].as_py()
                    v_da = da_arr[r_idx].as_py()
                    v_oct = oct_arr[r_idx].as_py()
                    v_ser = ser_arr[r_idx].as_py()

                    # Accumulate whole-brain outputs
                    if pre != post:
                        neuron_outputs[pre][0] += syn * v_ach
                        neuron_outputs[pre][1] += syn * v_gaba
                        neuron_outputs[pre][2] += syn * v_glut
                        neuron_outputs[pre][3] += syn * v_da
                        neuron_outputs[pre][4] += syn * v_oct
                        neuron_outputs[pre][5] += syn * v_ser

                    # Check if connection is in FB
                    np_val = np_arr[r_idx].as_py()
                    if np_val == "FB":
                        if pre == post:
                            fb_autapses[pre] += syn
                        else:
                            pair = (pre, post)
                            if pair not in fb_edges:
                                fb_edges[pair] = {
                                    "syn": syn,
                                    "ach": v_ach,
                                    "gaba": v_gaba,
                                    "glut": v_glut,
                                    "da": v_da,
                                    "oct": v_oct,
                                    "ser": v_ser,
                                }
                            else:
                                e = fb_edges[pair]
                                old_syn = e["syn"]
                                new_syn = old_syn + syn
                                e["ach"] = (e["ach"] * old_syn + v_ach * syn) / new_syn
                                e["gaba"] = (e["gaba"] * old_syn + v_gaba * syn) / new_syn
                                e["glut"] = (e["glut"] * old_syn + v_glut * syn) / new_syn
                                e["da"] = (e["da"] * old_syn + v_da * syn) / new_syn
                                e["oct"] = (e["oct"] * old_syn + v_oct * syn) / new_syn
                                e["ser"] = (e["ser"] * old_syn + v_ser * syn) / new_syn
                                e["syn"] = new_syn

    t_ingest = time.perf_counter() - t0
    print(f"Ingestion completed in {t_ingest:.2f}s (RAM: {get_peak_memory_mb():.1f} MB)")
    print(f"Total records: {total_records:,} | Total synapses: {total_synapses:,}")

    # Compute consensus neurotransmitter and confidence
    neuron_consensus: dict[int, int] = {}
    neuron_confidence: dict[int, float] = {}
    for nid, probs in neuron_outputs.items():
        s = sum(probs)
        if s > 0:
            norm = [p / s for p in probs]
            top_p = max(norm)
            neuron_consensus[nid] = int(norm.index(top_p))
            neuron_confidence[nid] = float(top_p)

    print(f"Whole-brain neurons classified: {len(neuron_consensus):,}")

    # Build primary graph at w >= primary_threshold (w >= 5)
    valid_edges = {
        pair: data for pair, data in fb_edges.items()
        if data["syn"] >= primary_threshold and pair[0] in neuron_consensus and pair[1] in neuron_consensus
    }
    active_nodes = sorted(list(set(u for u, v in valid_edges.keys()) | set(v for u, v in valid_edges.keys())))

    # Extract mutual dyads
    mutual_dyads: list[list[int]] = []
    edge_set = set(valid_edges.keys())
    for u, v in valid_edges.keys():
        if u < v and (v, u) in edge_set:
            mutual_dyads.append([u, v])

    # Compute degree covariates
    in_deg = Counter(v for u, v in valid_edges.keys())
    out_deg = Counter(u for u, v in valid_edges.keys())
    syn_in = Counter()
    syn_out = Counter()
    for (u, v), data in valid_edges.items():
        syn_out[u] += data["syn"]
        syn_in[v] += data["syn"]

    m_deg = Counter()
    for u, v in mutual_dyads:
        m_deg[u] += 1
        m_deg[v] += 1

    # Node dictionary
    nodes_info: dict[str, Any] = {}
    for nid in active_nodes:
        c_idx = neuron_consensus[nid]
        nodes_info[str(nid)] = {
            "root_id": nid,
            "nt": c_idx,
            "nt_name": NT_CLASSES[c_idx],
            "conf": round(neuron_confidence[nid], 4),
            "in_deg": in_deg[nid],
            "out_deg": out_deg[nid],
            "tot_deg": in_deg[nid] + out_deg[nid],
            "m_deg": m_deg[nid],
            "syn_in": syn_in[nid],
            "syn_out": syn_out[nid],
        }

    # Format directed edges
    directed_edges_list = [
        [u, v, data["syn"]] for (u, v), data in valid_edges.items()
    ]

    # Verification checks against Phase 6 baseline
    print("\n--- Baseline Audit Verification ---")
    print(f"Active nodes: {len(active_nodes)} (Expected: 2465)")
    print(f"Directed edges (w >= {primary_threshold}): {len(valid_edges)} (Expected: 46903)")
    print(f"Mutual dyads (w >= {primary_threshold}): {len(mutual_dyads)} (Expected: 5435)")
    edge_reciprocity = 2.0 * len(mutual_dyads) / len(valid_edges) * 100.0
    print(f"Edge reciprocity: {edge_reciprocity:.2f}% (Expected: 23.18%)")

    # Dyad transmitter composition
    dyad_transmitters = Counter()
    for u, v in mutual_dyads:
        c1 = neuron_consensus[u]
        c2 = neuron_consensus[v]
        p_name = f"{NT_CLASSES[min(c1, c2)]}_{NT_CLASSES[max(c1, c2)]}"
        dyad_transmitters[p_name] += 1

    print("\nTop Mutual Dyad Transmitter Pairs:")
    for pair_name, count in dyad_transmitters.most_common(8):
        pct = count / len(mutual_dyads) * 100.0
        print(f"  {pair_name:12s}: {count:5d} ({pct:6.2f}%)")

    result = {
        "metadata": {
            "neuropil": "FB",
            "threshold": primary_threshold,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "source_feather": str(feather_path.name),
            "total_records_scanned": total_records,
            "total_synapses_scanned": total_synapses,
            "active_nodes_count": len(active_nodes),
            "directed_edges_count": len(valid_edges),
            "mutual_dyads_count": len(mutual_dyads),
            "edge_reciprocity_pct": round(edge_reciprocity, 4),
            "peak_ram_mb": round(get_peak_memory_mb(), 2),
            "extraction_time_sec": round(t_ingest, 2),
        },
        "active_nodes": active_nodes,
        "nodes": nodes_info,
        "mutual_dyads": mutual_dyads,
        "directed_edges": directed_edges_list,
        "dyad_transmitter_counts": dict(dyad_transmitters),
    }

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Fan-Shaped Body subgraph from FAFB v783 feather.")
    parser.add_argument("--threshold", type=int, default=5, help="Synapse threshold w (default: 5)")
    parser.add_argument("--out", type=str, default=str(OUT_CACHE), help="Output JSON path")
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    data = extract_fb_data(FEATHER_FILE, primary_threshold=args.threshold)

    print(f"\nSaving cached FB covariates to {out_path} ...")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    file_size_mb = out_path.stat().st_size / (1024.0 * 1024.0)
    print(f"Saved {file_size_mb:.2f} MB JSON cache. Extraction complete!")


if __name__ == "__main__":
    main()
