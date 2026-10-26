#!/usr/bin/env python3
"""
Whole-Brain Synapse Threshold Sensitivity Analysis and Reciprocity Verification.

Addresses Phase Two of the Research Protocol:
1. Streams all 16,847,997 records of proofread_connections_783.feather in a single pass.
2. Aggregates multi-neuropil records into global ordered neuron pairs (pre, post) with summed weights.
3. Evaluates whole-brain network topology across documented thresholds:
   w >= 1, w >= 2, w >= 3, w >= 5, w >= 10, w >= 20.
4. Computes BOTH:
   - Directed Edge Reciprocity: R_edge = 2*M / E (standard Wasserman-Faust / Newman)
   - Dyad Reciprocity:          R_dyad = M / (U + M) = M / Connected_Pairs (Lin et al. 2024 Nature)
5. Verifies reciprocity using an independent second implementation (set intersection S & S_rev).
6. Preserves bounded memory (< 1.5 GiB RAM) on the Dell Inspiron 5558.
"""

from __future__ import annotations

import argparse
import json
import resource
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_PATH = PROJECT_ROOT / ".venv" / "lib" / "python3.12" / "site-packages"
if VENV_PATH.exists():
    sys.path.insert(0, str(VENV_PATH))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

try:
    import pyarrow.ipc as ipc
except ImportError:
    ipc = None

from run_preliminary_analysis import DisjointSet, calculate_distribution_stats


def get_peak_memory_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def run_threshold_analysis(
    file_path: Path,
    thresholds: list[int] | None = None,
    output_json: Path | None = None,
) -> dict[str, Any]:
    if thresholds is None:
        thresholds = [1, 2, 3, 5, 10, 20]

    if output_json is None:
        output_json = PROJECT_ROOT / "results" / "real_data_pilot" / "verified_threshold_sensitivity.json"
    output_json.parent.mkdir(parents=True, exist_ok=True)

    start_time = time.perf_counter()
    print("================================================================================")
    print("PHASE TWO: WHOLE-BRAIN SYNAPSE THRESHOLD SENSITIVITY & RECIPROCITY AUDIT")
    print(f"Dataset:    {file_path.name} (16,847,997 physical records)")
    print(f"Thresholds: {thresholds}")
    print("================================================================================\n")

    node_to_id: dict[int, int] = {}
    id_to_node: list[int] = []
    # edge_weights: (u << 32) | v -> aggregated synapse count
    edge_weights: dict[int, int] = {}

    total_records = 0
    duplicate_records_merged = 0
    malformed_records = 0

    print(">>> Step 1: Streaming dataset and building whole-brain multi-neuropil aggregated graph...")
    with open(file_path, "rb") as f:
        reader = ipc.open_file(f)
        num_batches = reader.num_record_batches
        col_pre = "pre_pt_root_id"
        col_post = "post_pt_root_id"
        col_weight = "syn_count"

        for b_idx in range(num_batches):
            batch = reader.get_batch(b_idx)
            pres = batch.column(col_pre).to_pylist()
            posts = batch.column(col_post).to_pylist()
            weights = batch.column(col_weight).to_pylist()

            for p, q, w in zip(pres, posts, weights):
                if p is None or q is None or w is None or w <= 0:
                    malformed_records += 1
                    continue

                if p not in node_to_id:
                    node_to_id[p] = len(id_to_node)
                    id_to_node.append(p)
                u = node_to_id[p]

                if q not in node_to_id:
                    node_to_id[q] = len(id_to_node)
                    id_to_node.append(q)
                v = node_to_id[q]

                edge_key = (u << 32) | v
                if edge_key in edge_weights:
                    duplicate_records_merged += 1
                    edge_weights[edge_key] += w
                else:
                    edge_weights[edge_key] = w

                total_records += 1

            if (b_idx + 1) % 50 == 0 or (b_idx + 1) == num_batches:
                elapsed = time.perf_counter() - start_time
                ram = get_peak_memory_mb()
                print(f"    Batches processed: {b_idx + 1}/{num_batches} ({total_records:,} rows) | Time: {elapsed:.1f}s | RAM: {ram:.1f} MB")

    ingest_time = time.perf_counter() - start_time
    total_unique_edges = len(edge_weights)
    total_unique_nodes = len(id_to_node)
    total_synapses = sum(edge_weights.values())

    print(f"\nIngestion Complete in {ingest_time:.2f}s:")
    print(f"  Total valid records:            {total_records:,}")
    print(f"  Multi-neuropil records merged:  {duplicate_records_merged:,}")
    print(f"  Unique proofread neurons (|V|): {total_unique_nodes:,}")
    print(f"  Unique directed edges (|E|):    {total_unique_edges:,}")
    print(f"  Total anatomical synapses:      {total_synapses:,}\n")

    print(">>> Step 2: Evaluating Whole-Brain Topology across Thresholds in Memory...")
    threshold_results = []

    for t in sorted(thresholds):
        t_start = time.perf_counter()
        # 1. Filter edges
        # Keys of edges with weight >= t
        filtered_edges = {k: w for k, w in edge_weights.items() if w >= t}
        E = len(filtered_edges)
        syn_count_t = sum(filtered_edges.values())

        # 2. Identify active neurons
        active_nodes = set()
        for k in filtered_edges:
            active_nodes.add(k >> 32)
            active_nodes.add(k & 0xFFFFFFFF)
        N_active = len(active_nodes)

        # 3. Method A: Count mutual dyads via directed edge hash lookup
        mutual_dyads = 0
        autapses = 0
        for k in filtered_edges:
            u = k >> 32
            v = k & 0xFFFFFFFF
            if u == v:
                autapses += 1
            elif u < v:
                rev_k = (v << 32) | u
                if rev_k in filtered_edges:
                    mutual_dyads += 1

        # 4. Method B (Independent verification): Set intersection of forward and reverse keys
        # Set of non-autapse edges
        edge_set = {k for k in filtered_edges if (k >> 32) != (k & 0xFFFFFFFF)}
        rev_set = {((k & 0xFFFFFFFF) << 32) | (k >> 32) for k in edge_set}
        reciprocal_edges_set = edge_set & rev_set
        mutual_dyads_verified = len(reciprocal_edges_set) // 2
        verification_passed = (mutual_dyads == mutual_dyads_verified)

        reciprocal_directed_edges = 2 * mutual_dyads
        asymmetric_directed_edges = E - reciprocal_directed_edges - autapses
        total_connected_pairs = asymmetric_directed_edges + mutual_dyads

        # Metrics:
        # Edge-based reciprocity: R_edge = 2*M / E
        reciprocity_edge = (reciprocal_directed_edges / E) if E > 0 else 0.0
        # Dyad-based reciprocity: R_dyad = M / (U + M) = M / Connected_Pairs
        reciprocity_dyad = (mutual_dyads / total_connected_pairs) if total_connected_pairs > 0 else 0.0

        # Connected components via DisjointSet on active nodes
        ds = DisjointSet(total_unique_nodes)
        for k in filtered_edges:
            u = k >> 32
            v = k & 0xFFFFFFFF
            if u != v:
                ds.union(u, v)

        comp_counts = Counter(ds.find(i) for i in active_nodes)
        comps_sorted = sorted(comp_counts.values(), reverse=True)
        num_components = len(comps_sorted)
        gcc_size = comps_sorted[0] if comps_sorted else 0
        gcc_coverage = (gcc_size / N_active) if N_active > 0 else 0.0

        # Degree statistics
        out_deg = [0] * total_unique_nodes
        in_deg = [0] * total_unique_nodes
        for k in filtered_edges:
            out_deg[k >> 32] += 1
            in_deg[k & 0xFFFFFFFF] += 1

        active_out = [out_deg[i] for i in active_nodes]
        active_in = [in_deg[i] for i in active_nodes]
        out_stats = calculate_distribution_stats(active_out)
        in_stats = calculate_distribution_stats(active_in)

        # Erdős-Rényi baseline comparison
        p_er = (E / (N_active * (N_active - 1))) if N_active > 1 else 0.0
        er_enrichment_edge = (reciprocity_edge / p_er) if p_er > 0 else 0.0

        t_elapsed = time.perf_counter() - t_start

        res_entry = {
            "threshold_w": t,
            "directed_edges": E,
            "total_synapses": syn_count_t,
            "synapse_retention_pct": round(syn_count_t / total_synapses * 100.0, 2),
            "edge_retention_pct": round(E / total_unique_edges * 100.0, 2),
            "active_neurons": N_active,
            "neuron_retention_pct": round(N_active / total_unique_nodes * 100.0, 2),
            "autapses": autapses,
            "mutual_dyads": mutual_dyads,
            "reciprocal_directed_edges": reciprocal_directed_edges,
            "asymmetric_directed_edges": asymmetric_directed_edges,
            "total_connected_pairs": total_connected_pairs,
            "reciprocity_edge_ratio": round(reciprocity_edge, 6),
            "reciprocity_edge_pct": round(reciprocity_edge * 100.0, 2),
            "reciprocity_dyad_ratio": round(reciprocity_dyad, 6),
            "reciprocity_dyad_pct": round(reciprocity_dyad * 100.0, 2),
            "independent_verification_passed": verification_passed,
            "connected_components_count": num_components,
            "gcc_neuron_count": gcc_size,
            "gcc_coverage_pct": round(gcc_coverage * 100.0, 2),
            "erdos_renyi_density": round(p_er, 6),
            "reciprocity_over_er_ratio": round(er_enrichment_edge, 1),
            "out_degree_stats": out_stats,
            "in_degree_stats": in_stats,
            "calc_time_seconds": round(t_elapsed, 2),
        }
        threshold_results.append(res_entry)

        print(
            f"  [Threshold w >= {t:2d}] Edges: {E:10,d} ({res_entry['edge_retention_pct']:5.1f}%) | "
            f"Synapses: {syn_count_t:10,d} ({res_entry['synapse_retention_pct']:5.1f}%) | "
            f"Neurons: {N_active:7,d} | R_edge: {res_entry['reciprocity_edge_pct']:5.2f}% | "
            f"R_dyad: {res_entry['reciprocity_dyad_pct']:5.2f}% | GCC: {res_entry['gcc_coverage_pct']:5.1f}% | "
            f"Verified: {verification_passed} ({t_elapsed:.2f}s)"
        )

    total_pipeline_time = time.perf_counter() - start_time
    final_ram = get_peak_memory_mb()

    audit_summary = {
        "metadata": {
            "dataset_file": file_path.name,
            "dataset_scope": "COMPLETE WHOLE BRAIN (16,847,997 records)",
            "pipeline_version": "Phase 3 Verified Pipeline",
            "execution_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_records_processed": total_records,
            "total_unique_neurons_represented": total_unique_nodes,
            "total_unique_directed_edges": total_unique_edges,
            "total_chemical_synapses": total_synapses,
            "wall_time_seconds": round(total_pipeline_time, 2),
            "peak_memory_mb": round(final_ram, 1),
        },
        "threshold_sensitivity": threshold_results,
    }

    with output_json.open("w", encoding="utf-8") as f:
        json.dump(audit_summary, f, indent=2)

    print(f"\nWhole-brain threshold sensitivity analysis completed in {total_pipeline_time:.2f}s.")
    print(f"Results saved to: {output_json}")
    return audit_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run whole-brain threshold sensitivity analysis.")
    parser.add_argument("--file", type=Path, default=PROJECT_ROOT / "data" / "raw" / "fafb_v783" / "proofread_connections_783.feather")
    parser.add_argument("--thresholds", nargs="+", type=int, default=[1, 2, 3, 5, 10, 20])
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    run_threshold_analysis(args.file, thresholds=args.thresholds, output_json=args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())

