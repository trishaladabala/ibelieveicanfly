#!/usr/bin/env python3
"""
Comprehensive All-79-Neuropils Reciprocity and Bilateral Symmetry Analysis.

Addresses Phase Five of the Research Protocol:
1. Dynamically detects all neuropils represented in proofread_connections_783.feather (all 79 standard regions).
2. Computes intra-neuropil connectivity across thresholds w >= 1, 3, 5, 10:
   - Input records count
   - Represented neuron count
   - Unique directed edges count
   - Total chemical synapse count
   - Mutual reciprocal dyads (M)
   - Edge reciprocity: R_edge = 2*M / E
   - Dyad reciprocity: R_dyad = M / (U + M)
3. Evaluates whole-brain ranking:
   - Tests whether Ellipsoid Body (EB) is indeed the most reciprocal neuropil across the entire brain.
4. Formal Bilateral Hemisphere Symmetry Analysis:
   - Matches all bilateral pairs (e.g. AL_L vs AL_R, ME_L vs ME_R, MB_CA_L vs MB_CA_R, etc.).
   - Computes Cohen's h effect size for differences between independent proportions.
   - Computes two-proportion z-statistic and p-value.
5. Saves results to results/real_data_pilot/verified_regional_metrics.json.
"""

from __future__ import annotations

import argparse
import json
import math
import resource
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_PATH = PROJECT_ROOT / ".venv" / "lib" / "python3.12" / "site-packages"
if VENV_PATH.exists():
    sys.path.insert(0, str(VENV_PATH))

import pyarrow.ipc as ipc


def get_peak_memory_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def cohens_h(p1: float, p2: float) -> float:
    """Calculate Cohen's h effect size for the difference between two proportions."""
    p1 = max(0.0, min(1.0, p1))
    p2 = max(0.0, min(1.0, p2))
    phi1 = 2.0 * math.asin(math.sqrt(p1))
    phi2 = 2.0 * math.asin(math.sqrt(p2))
    return abs(phi1 - phi2)


def two_proportion_z_test(k1: int, n1: int, k2: int, n2: int) -> tuple[float, float]:
    """Calculate z-statistic and two-tailed p-value for two independent proportions."""
    if n1 <= 0 or n2 <= 0:
        return 0.0, 1.0
    p1 = k1 / n1
    p2 = k2 / n2
    p_pool = (k1 + k2) / (n1 + n2)
    if p_pool <= 0 or p_pool >= 1:
        return 0.0, 1.0
    se = math.sqrt(p_pool * (1.0 - p_pool) * (1.0 / n1 + 1.0 / n2))
    if se == 0:
        return 0.0, 1.0
    z = (p1 - p2) / se
    # Normal CDF approximation via math.erf
    p_value = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(z) / math.sqrt(2.0))))
    return round(z, 4), max(1e-15, min(1.0, p_value))


def analyze_all_neuropils(
    file_path: Path,
    thresholds: list[int] | None = None,
    output_json: Path | None = None,
) -> dict[str, Any]:
    if thresholds is None:
        thresholds = [1, 3, 5, 10]

    if output_json is None:
        output_json = PROJECT_ROOT / "results" / "real_data_pilot" / "verified_regional_metrics.json"
    output_json.parent.mkdir(parents=True, exist_ok=True)

    start_time = time.perf_counter()
    print("================================================================================")
    print("PHASE FIVE: ALL-79 NEUROPILS RECIPROCITY & BILATERAL SYMMETRY ANALYSIS")
    print(f"Dataset:    {file_path.name}")
    print(f"Thresholds: {thresholds}")
    print("================================================================================\n")

    # Neuropil storage: npil -> node_to_id, id_to_node, edge_weights
    neuropil_nodes: dict[str, dict[int, int]] = defaultdict(dict)
    neuropil_edges: dict[str, dict[int, int]] = defaultdict(dict)
    neuropil_records: Counter[str] = Counter()

    print(">>> Step 1: Streaming dataset and grouping intra-neuropil connections across all regions...")
    with open(file_path, "rb") as f:
        reader = ipc.open_file(f)
        num_batches = reader.num_record_batches
        col_pre = "pre_pt_root_id"
        col_post = "post_pt_root_id"
        col_weight = "syn_count"
        col_npil = "neuropil"

        for b_idx in range(num_batches):
            batch = reader.get_batch(b_idx)
            pres = batch.column(col_pre).to_pylist()
            posts = batch.column(col_post).to_pylist()
            weights = batch.column(col_weight).to_pylist()
            npils = batch.column(col_npil).to_pylist() if col_npil in batch.schema.names else [None] * len(pres)

            for p, q, w, npil in zip(pres, posts, weights, npils):
                if not npil or p is None or q is None or w is None or w <= 0:
                    continue

                neuropil_records[npil] += 1
                nodes = neuropil_nodes[npil]
                if p not in nodes:
                    nodes[p] = len(nodes)
                u = nodes[p]

                if q not in nodes:
                    nodes[q] = len(nodes)
                v = nodes[q]

                edge_key = (u << 32) | v
                edges = neuropil_edges[npil]
                edges[edge_key] = edges.get(edge_key, 0) + w

            if (b_idx + 1) % 50 == 0 or (b_idx + 1) == num_batches:
                elapsed = time.perf_counter() - start_time
                print(f"  Processed {b_idx + 1}/{num_batches} batches | Time: {elapsed:.1f}s | Regions detected: {len(neuropil_edges)}")

    print(f"\nIngestion complete in {time.perf_counter() - start_time:.2f}s. Total neuropils detected: {len(neuropil_edges)}\n")

    print(">>> Step 2: Computing Multi-Threshold Metrics for Every Neuropil...")
    neuropil_metrics_table = []

    for npil, edges in neuropil_edges.items():
        nodes = neuropil_nodes[npil]
        N = len(nodes)
        raw_rec_count = neuropil_records[npil]
        total_unique_edges = len(edges)
        total_synapses = sum(edges.values())

        threshold_data = {}
        for t in thresholds:
            t_edges = {k: w for k, w in edges.items() if w >= t}
            E_t = len(t_edges)
            syn_t = sum(t_edges.values())

            # Count mutual dyads and autapses
            mutual_dyads = 0
            autapses = 0
            for k in t_edges:
                u = k >> 32
                v = k & 0xFFFFFFFF
                if u == v:
                    autapses += 1
                elif u < v:
                    rev_k = (v << 32) | u
                    if rev_k in t_edges:
                        mutual_dyads += 1

            r_dir_edges = 2 * mutual_dyads
            asym_edges = E_t - r_dir_edges - autapses
            conn_pairs = asym_edges + mutual_dyads

            r_edge = (r_dir_edges / E_t) if E_t > 0 else 0.0
            r_dyad = (mutual_dyads / conn_pairs) if conn_pairs > 0 else 0.0

            threshold_data[f"w{t}"] = {
                "edges": E_t,
                "synapses": syn_t,
                "autapses": autapses,
                "mutual_dyads": mutual_dyads,
                "reciprocal_directed_edges": r_dir_edges,
                "reciprocity_edge_pct": round(r_edge * 100.0, 2),
                "reciprocity_dyad_pct": round(r_dyad * 100.0, 2),
            }

        neuropil_metrics_table.append({
            "neuropil": npil,
            "input_records": raw_rec_count,
            "represented_neurons": N,
            "total_directed_edges_w1": total_unique_edges,
            "total_synapses_w1": total_synapses,
            "reciprocity_w1_pct": threshold_data["w1"]["reciprocity_edge_pct"],
            "reciprocity_w3_pct": threshold_data.get("w3", {}).get("reciprocity_edge_pct", 0.0),
            "reciprocity_w5_pct": threshold_data.get("w5", {}).get("reciprocity_edge_pct", 0.0),
            "reciprocity_w10_pct": threshold_data.get("w10", {}).get("reciprocity_edge_pct", 0.0),
            "threshold_details": threshold_data,
        })

    # Sort all neuropils by reciprocity at w >= 1 descending
    neuropil_metrics_table.sort(key=lambda x: -x["reciprocity_w1_pct"])

    # Assign ranks
    for rank, entry in enumerate(neuropil_metrics_table, start=1):
        entry["rank_reciprocity_w1"] = rank

    # Re-sort at w >= 3 to get w3 ranks
    w3_sorted = sorted(neuropil_metrics_table, key=lambda x: -x["reciprocity_w3_pct"])
    for rank, entry in enumerate(w3_sorted, start=1):
        entry["rank_reciprocity_w3"] = rank

    print(">>> Step 3: Bilateral Hemisphere Symmetry Analysis...")
    # Find all bilateral pairs: NAME_L and NAME_R
    bilateral_pairs = []
    seen_bases = set()
    npil_lookup = {e["neuropil"]: e for e in neuropil_metrics_table}

    for e in neuropil_metrics_table:
        name = e["neuropil"]
        if name.endswith("_L"):
            base = name[:-2]
            partner = f"{base}_R"
            if partner in npil_lookup and base not in seen_bases:
                seen_bases.add(base)
                left = e
                right = npil_lookup[partner]

                r_left = left["reciprocity_w1_pct"] / 100.0
                r_right = right["reciprocity_w1_pct"] / 100.0
                e_left = left["total_directed_edges_w1"]
                e_right = right["total_directed_edges_w1"]
                m_left = left["threshold_details"]["w1"]["reciprocal_directed_edges"]
                m_right = right["threshold_details"]["w1"]["reciprocal_directed_edges"]

                abs_diff = abs(left["reciprocity_w1_pct"] - right["reciprocity_w1_pct"])
                mean_r = (r_left + r_right) / 2.0
                rel_diff_pct = (abs_diff / (mean_r * 100.0) * 100.0) if mean_r > 0 else 0.0
                h_stat = cohens_h(r_left, r_right)
                z_stat, p_val = two_proportion_z_test(m_left, e_left, m_right, e_right)

                bilateral_pairs.append({
                    "base_neuropil": base,
                    "left_region": f"{base}_L",
                    "right_region": f"{base}_R",
                    "edges_left": e_left,
                    "edges_right": e_right,
                    "synapses_left": left["total_synapses_w1"],
                    "synapses_right": right["total_synapses_w1"],
                    "reciprocity_left_pct": left["reciprocity_w1_pct"],
                    "reciprocity_right_pct": right["reciprocity_w1_pct"],
                    "absolute_diff_pct_points": round(abs_diff, 2),
                    "relative_diff_pct": round(rel_diff_pct, 2),
                    "cohens_h_effect_size": round(h_stat, 4),
                    "effect_size_interpretation": "Negligible (|h| < 0.2)" if h_stat < 0.2 else ("Small (0.2 <= |h| < 0.5)" if h_stat < 0.5 else "Medium/Large"),
                    "two_proportion_z_stat": z_stat,
                    "p_value": p_val,
                })

    bilateral_pairs.sort(key=lambda x: -x["edges_left"] - x["edges_right"])

    total_time = time.perf_counter() - start_time
    peak_ram = get_peak_memory_mb()

    report = {
        "metadata": {
            "execution_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dataset_file": file_path.name,
            "total_neuropils_evaluated": len(neuropil_metrics_table),
            "bilateral_pairs_evaluated": len(bilateral_pairs),
            "runtime_seconds": round(total_time, 2),
            "peak_ram_mb": round(peak_ram, 1),
        },
        "all_neuropils_ranked": neuropil_metrics_table,
        "bilateral_symmetry_audit": bilateral_pairs,
    }

    with output_json.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nAnalysis complete in {total_time:.2f}s (Peak RAM: {peak_ram:.1f} MB).")
    print(f"Results saved to: {output_json}\n")

    # Print Top 10 Reciprocal Neuropils across whole brain
    print("==================================================================================")
    print("TOP 10 MOST RECIPROCAL NEUROPILS ACROSS ENTIRE BRAIN (w >= 1)")
    print("==================================================================================")
    print(f"{'Rank':4s} | {'Neuropil':10s} | {'Edges':10s} | {'Synapses':10s} | {'R_edge (w>=1)':14s} | {'R_edge (w>=3)':14s}")
    print("-" * 80)
    for e in neuropil_metrics_table[:10]:
        print(f"#{e['rank_reciprocity_w1']:<3d} | {e['neuropil']:10s} | {e['total_directed_edges_w1']:10,d} | {e['total_synapses_w1']:10,d} | {e['reciprocity_w1_pct']:12.2f}% | {e['reciprocity_w3_pct']:12.2f}%")
    print("==================================================================================\n")

    # Print Key Bilateral Pairs
    print("==================================================================================")
    print("BILATERAL HEMISPHERIC SYMMETRY AUDIT (Top Neuropil Pairs)")
    print("==================================================================================")
    print(f"{'Base':10s} | {'Recip Left':12s} | {'Recip Right':12s} | {'Abs Diff':10s} | {'Cohen h':10s} | {'Effect Interpretation'}")
    print("-" * 80)
    for p in bilateral_pairs[:10]:
        print(f"{p['base_neuropil']:10s} | {p['reciprocity_left_pct']:10.2f}% | {p['reciprocity_right_pct']:10.2f}% | {p['absolute_diff_pct_points']:8.2f}% | {p['cohens_h_effect_size']:8.4f} | {p['effect_size_interpretation']}")
    print("==================================================================================\n")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze reciprocity and bilateral symmetry across all 79 neuropils.")
    parser.add_argument("--file", type=Path, default=PROJECT_ROOT / "data" / "raw" / "fafb_v783" / "proofread_connections_783.feather")
    args = parser.parse_args()

    analyze_all_neuropils(args.file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
