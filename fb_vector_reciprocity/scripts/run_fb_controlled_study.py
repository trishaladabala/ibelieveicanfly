#!/usr/bin/env python3
"""
run_fb_controlled_study.py

Executes rigorous conditional null models on the Fan-Shaped Body (FB) reciprocal connectome.
Holds the empirical mutual dyad topology (M = 5,435) strictly invariant while permuting
predicted whole-neuron neurotransmitter labels within defined degree strata.

Ensemble Models (B = 2,000 permutations each, seed = 42):
- Model 1: Mutual-Degree Quartiles (4 strata)
- Model 2: Joint Directed In x Out Tertiles (9 strata, 3x3 grid)
- Model 3: Joint Directed In x Out Medians (4 strata, 2x2 grid)
- Model 4: Total Directed Degree Quintiles (5 strata)

Evaluates:
- All 21 neurotransmitter combinations.
- Calibrated Z-scores, empirical p-values with exact finite-sample correction.
- Benjamini-Hochberg FDR adjustments (q < 0.05).
- Stratum mobility diagnostics (verifying zero frozen single-label strata).

Saves results to:
- results/fb_controlled_study_results.json
- results/tables/fb_motif_summary_table.tsv
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import random
import resource
import sys
import time
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CACHE_FILE = REPO_ROOT / "data" / "fb_node_covariates.json"
if not CACHE_FILE.exists():
    CACHE_FILE = REPO_ROOT.parent / "fb_vector_reciprocity" / "data" / "fb_node_covariates.json"
OUT_JSON = REPO_ROOT / "results" / "fb_controlled_study_results.json"
OUT_TSV = REPO_ROOT / "results" / "tables" / "fb_motif_summary_table.tsv"

NT_CLASSES = ["ach", "gaba", "glut", "da", "oct", "ser"]
NT_INDEX = {name: i for i, name in enumerate(NT_CLASSES)}


def get_peak_memory_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def all_pair_names() -> list[str]:
    names = []
    for i in range(len(NT_CLASSES)):
        for j in range(i, len(NT_CLASSES)):
            names.append(f"{NT_CLASSES[i]}_{NT_CLASSES[j]}")
    return names


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    """Applies Benjamini-Hochberg FDR adjustment to a list of p-values."""
    n = len(p_values)
    if n == 0:
        return []
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    q_values = [0.0] * n
    cum_min = 1.0
    for rank_minus_1 in range(n - 1, -1, -1):
        orig_idx, p = indexed[rank_minus_1]
        rank = rank_minus_1 + 1
        q = (p * n) / rank
        cum_min = min(cum_min, q)
        q_values[orig_idx] = min(1.0, cum_min)
    return q_values


def partition_into_strata_1d(nodes: list[int], degrees: dict[int, int], n_strata: int) -> list[list[int]]:
    """Partitions nodes into n equal-sized strata ordered by a single degree covariate."""
    sorted_nodes = sorted(nodes, key=lambda n: degrees.get(n, 0))
    N = len(sorted_nodes)
    if N == 0 or n_strata <= 1:
        return [sorted_nodes]
    bin_size = N // n_strata
    strata = []
    for i in range(n_strata - 1):
        strata.append(sorted_nodes[i * bin_size : (i + 1) * bin_size])
    strata.append(sorted_nodes[(n_strata - 1) * bin_size :])
    return [s for s in strata if len(s) > 0]


def partition_joint_grid(nodes: list[int], in_degs: dict[int, int], out_degs: dict[int, int], n_bins: int) -> list[list[int]]:
    """Partitions nodes into a joint n_bins x n_bins grid based on in- and out-degree quantiles."""
    N = len(nodes)
    if N == 0 or n_bins <= 1:
        return [nodes]

    # Rank nodes by in-degree and out-degree
    sorted_by_in = sorted(nodes, key=lambda n: (in_degs.get(n, 0), n))
    in_bin_size = N // n_bins
    node_in_bin: dict[int, int] = {}
    for b in range(n_bins - 1):
        for n in sorted_by_in[b * in_bin_size : (b + 1) * in_bin_size]:
            node_in_bin[n] = b
    for n in sorted_by_in[(n_bins - 1) * in_bin_size :]:
        node_in_bin[n] = n_bins - 1

    sorted_by_out = sorted(nodes, key=lambda n: (out_degs.get(n, 0), n))
    out_bin_size = N // n_bins
    node_out_bin: dict[int, int] = {}
    for b in range(n_bins - 1):
        for n in sorted_by_out[b * out_bin_size : (b + 1) * out_bin_size]:
            node_out_bin[n] = b
    for n in sorted_by_out[(n_bins - 1) * out_bin_size :]:
        node_out_bin[n] = n_bins - 1

    # Form grid strata
    grid: dict[tuple[int, int], list[int]] = defaultdict(list)
    for n in nodes:
        b_in = node_in_bin[n]
        b_out = node_out_bin[n]
        grid[(b_in, b_out)].append(n)

    return [s for s in grid.values() if len(s) > 0]


def run_permutation_model(
    mutual_dyads: list[list[int]],
    active_nodes: list[int],
    neuron_nt: dict[int, int],
    strata: list[list[int]],
    num_perms: int = 2000,
    seed: int = 42,
) -> dict[str, Any]:
    """Runs conditional label permutations within strata across all 21 transmitter combinations."""
    rng = random.Random(seed)
    pair_names = all_pair_names()

    # Observed counts
    obs_counts: Counter[str] = Counter()
    for u, v in mutual_dyads:
        tu = neuron_nt[u]
        tv = neuron_nt[v]
        p_name = f"{NT_CLASSES[min(tu, tv)]}_{NT_CLASSES[max(tu, tv)]}"
        obs_counts[p_name] += 1

    # Null distribution accumulator
    null_dists: dict[str, list[int]] = {p: [0] * num_perms for p in pair_names}

    for b in range(num_perms):
        mapping: dict[int, int] = {}
        for st in strata:
            lbls = [neuron_nt[n] for n in st]
            rng.shuffle(lbls)
            for n, l in zip(st, lbls):
                mapping[n] = l

        cur_counts: Counter[str] = Counter()
        for u, v in mutual_dyads:
            tu = mapping[u]
            tv = mapping[v]
            p_name = f"{NT_CLASSES[min(tu, tv)]}_{NT_CLASSES[max(tu, tv)]}"
            cur_counts[p_name] += 1

        for p in pair_names:
            null_dists[p][b] = cur_counts[p]

    # Compute statistics for each pair
    pair_stats: dict[str, Any] = {}
    p_values_list: list[float] = []

    for p in pair_names:
        obs = obs_counts[p]
        dist = null_dists[p]
        mean_val = sum(dist) / num_perms
        var_val = sum((x - mean_val) ** 2 for x in dist) / (num_perms - 1) if num_perms > 1 else 0.0
        std_val = math.sqrt(var_val) if var_val > 0 else 1e-6
        z = (obs - mean_val) / std_val

        # Two-tailed empirical p-value
        extreme = sum(1 for x in dist if abs(x - mean_val) >= abs(obs - mean_val))
        p_val = (extreme + 1) / (num_perms + 1)
        enrichment = (obs / mean_val) if mean_val > 0 else 0.0

        sorted_dist = sorted(dist)
        q025 = sorted_dist[int(0.025 * num_perms)]
        q250 = sorted_dist[int(0.250 * num_perms)]
        q500 = sorted_dist[int(0.500 * num_perms)]
        q750 = sorted_dist[int(0.750 * num_perms)]
        q975 = sorted_dist[int(0.975 * num_perms)]

        pair_stats[p] = {
            "observed": obs,
            "null_mean": round(mean_val, 2),
            "null_std": round(std_val, 2),
            "enrichment_ratio": round(enrichment, 4),
            "z_score": round(z, 2),
            "empirical_p_value": p_val,
            "quantiles": {
                "q025": q025,
                "q25": q250,
                "median": q500,
                "q75": q750,
                "q975": q975,
            },
        }
        p_values_list.append(p_val)

    # Benjamini-Hochberg FDR adjustment
    q_values = benjamini_hochberg(p_values_list)
    for idx, p in enumerate(pair_names):
        pair_stats[p]["fdr_q_value"] = q_values[idx]
        pair_stats[p]["fdr_significant"] = q_values[idx] < 0.05

    # Mobility diagnostics
    frozen_strata = sum(1 for st in strata if len(set(neuron_nt[n] for n in st)) <= 1)
    strata_sizes = [len(st) for st in strata]

    return {
        "strata_count": len(strata),
        "strata_sizes": strata_sizes,
        "frozen_strata_count": frozen_strata,
        "mobile_nodes_count": len(active_nodes) if frozen_strata == 0 else sum(len(st) for st in strata if len(set(neuron_nt[n] for n in st)) > 1),
        "pair_statistics": pair_stats,
    }


def main() -> None:
    t0 = time.perf_counter()
    print("=" * 80)
    print("FAN-SHAPED BODY (FB) CONTROLLED RECIPROCAL MOTIF STUDY")
    print("=" * 80)

    if not CACHE_FILE.exists():
        print(f"Error: cache file {CACHE_FILE} not found. Run extract_fb_subgraph.py first.")
        sys.exit(1)

    print(f"Loading cached FB covariates from {CACHE_FILE} ...")
    with open(CACHE_FILE) as f:
        cache_data = json.load(f)

    active_nodes = cache_data["active_nodes"]
    mutual_dyads = cache_data["mutual_dyads"]
    node_dict = cache_data["nodes"]
    metadata = cache_data["metadata"]

    neuron_nt = {int(nid): info["nt"] for nid, info in node_dict.items()}
    in_degs = {int(nid): info["in_deg"] for nid, info in node_dict.items()}
    out_degs = {int(nid): info["out_deg"] for nid, info in node_dict.items()}
    tot_degs = {int(nid): info["tot_deg"] for nid, info in node_dict.items()}
    m_degs = {int(nid): info["m_deg"] for nid, info in node_dict.items()}

    total_m = len(mutual_dyads)
    print(f"Loaded: {len(active_nodes)} active nodes | {total_m:,} mutual dyads")
    print(f"Directed edges: {metadata['directed_edges_count']:,} | Edge Reciprocity: {metadata['edge_reciprocity_pct']}%")

    # Define the 4 degree-stratified models
    print("\nPartitioning strata for 4 null models...")

    # Model 1: Mutual-Degree Quartiles (4 strata)
    strata_m1 = partition_into_strata_1d(active_nodes, m_degs, n_strata=4)

    # Model 2: Joint Directed In x Out Tertiles (9 strata)
    strata_m2 = partition_joint_grid(active_nodes, in_degs, out_degs, n_bins=3)

    # Model 3: Joint Directed In x Out Medians (4 strata)
    strata_m3 = partition_joint_grid(active_nodes, in_degs, out_degs, n_bins=2)

    # Model 4: Total Directed Degree Quintiles (5 strata)
    strata_m4 = partition_into_strata_1d(active_nodes, tot_degs, n_strata=5)

    models_config = [
        ("model1_mutual_quartiles", "Mutual-Degree Quartiles (4 strata)", strata_m1),
        ("model2_joint_in_out_tertiles", "Joint Directed In x Out Tertiles (3x3 grid, 9 strata)", strata_m2),
        ("model3_joint_in_out_medians", "Joint Directed In x Out Medians (2x2 grid, 4 strata)", strata_m3),
        ("model4_total_degree_quintiles", "Total Directed Degree Quintiles (5 strata)", strata_m4),
    ]

    study_results: dict[str, Any] = {
        "metadata": {
            "neuropil": "FB",
            "threshold": metadata["threshold"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "active_nodes_count": len(active_nodes),
            "directed_edges_count": metadata["directed_edges_count"],
            "mutual_dyads_count": total_m,
            "edge_reciprocity_pct": metadata["edge_reciprocity_pct"],
            "permutations_per_model": 2000,
            "seed": 42,
        },
        "models": {},
    }

    print("\nRunning permutation ensembles (B = 2,000 each)...")
    for m_id, m_name, strata in models_config:
        t_m0 = time.perf_counter()
        print(f"\n--- {m_name} ---")
        print(f"  Strata count: {len(strata)} | Sizes: {sorted([len(s) for s in strata])}")
        res = run_permutation_model(
            mutual_dyads=mutual_dyads,
            active_nodes=active_nodes,
            neuron_nt=neuron_nt,
            strata=strata,
            num_perms=2000,
            seed=42,
        )
        t_elapsed = time.perf_counter() - t_m0
        print(f"  Completed in {t_elapsed:.2f}s (RAM: {get_peak_memory_mb():.1f} MB)")

        # Focus on primary endpoints: ach_gaba, ach_glut, ach_ach, gaba_gaba
        p_stats = res["pair_statistics"]
        for target_p in ["ach_gaba", "ach_glut", "ach_ach", "gaba_gaba"]:
            st = p_stats[target_p]
            sig_flag = "***" if st["fdr_significant"] else "n.s."
            print(
                f"    {target_p:10s}: Obs={st['observed']:4d} | Null={st['null_mean']:6.1f} +/- {st['null_std']:4.1f} | "
                f"Ratio={st['enrichment_ratio']:5.2f}x | Z={st['z_score']:+6.2f} | p={st['empirical_p_value']:.6f} | "
                f"FDR q={st['fdr_q_value']:.6f} ({sig_flag})"
            )

        study_results["models"][m_id] = {
            "model_name": m_name,
            "results": res,
        }

    # Save structured JSON
    print(f"\nSaving results to {OUT_JSON} ...")
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(study_results, f, indent=2)

    # Save TSV Summary Table
    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    print(f"Saving summary TSV table to {OUT_TSV} ...")
    with open(OUT_TSV, "w") as f:
        f.write("Model\tPair\tObserved\tObs_Pct\tNull_Mean\tNull_Std\tEnrichment_Ratio\tZ_Score\tEmpirical_P\tFDR_Q\tFDR_Sig\n")
        for m_id, m_name, _ in models_config:
            p_stats = study_results["models"][m_id]["results"]["pair_statistics"]
            for p in all_pair_names():
                st = p_stats[p]
                obs_pct = round(st["observed"] / total_m * 100.0, 2)
                f.write(
                    f"{m_id}\t{p}\t{st['observed']}\t{obs_pct}\t{st['null_mean']}\t{st['null_std']}\t"
                    f"{st['enrichment_ratio']}\t{st['z_score']}\t{st['empirical_p_value']}\t"
                    f"{st['fdr_q_value']}\t{st['fdr_significant']}\n"
                )

    print(f"\nAll 4 controlled models completed successfully in {time.perf_counter() - t0:.2f}s!")


if __name__ == "__main__":
    main()
