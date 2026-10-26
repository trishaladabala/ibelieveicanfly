#!/usr/bin/env python3
"""
Controlled Central Complex (EB vs FB vs PB) Reciprocity and Neurotransmitter Motif Analysis
under Directed Degree-Preserving Edge-Swap Null Models (Maslov-Sneppen Rewiring).

Evaluates:
- Ellipsoid Body (EB, compass heading ring attractor)
- Fan-Shaped Body (FB, layered vector navigational integration)
- Protocerebral Bridge (PB, columnar heading relay)

Addresses Phase 5 Research Goals:
1. Keeps individual neuron consensus transmitter phenotypes fixed.
2. Implements directed edge swaps preserving exact in-degree and out-degree sequences.
3. Tests whether reciprocal dyad formation and transmitter pairings deviate from
   in/out-degree expectations within each Central Complex compartment.
4. Generates structured JSON output in results/real_data_pilot/central_complex_degree_preserving_null.json.
"""
from __future__ import annotations

import argparse
import array
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import random
import resource
import sys
import time
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_PATH = PROJECT_ROOT / ".venv" / "lib" / "python3.12" / "site-packages"
if VENV_PATH.exists():
    sys.path.insert(0, str(VENV_PATH))

import pyarrow.ipc as ipc

NT_CLASSES = ["ach", "gaba", "glut", "da", "oct", "ser"]
NT_INDEX = {name: i for i, name in enumerate(NT_CLASSES)}
TARGET_REGIONS = ["EB", "FB", "PB"]


def get_peak_memory_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def format_pair_name(c1: int, c2: int) -> str:
    i1, i2 = min(c1, c2), max(c1, c2)
    return f"{NT_CLASSES[i1]}_{NT_CLASSES[i2]}"


def directed_edge_swap(
    edge_list: list[tuple[int, int]],
    num_swaps: int,
    rng: random.Random,
) -> tuple[list[tuple[int, int]], int, int]:
    """
    Performs directed edge swaps preserving in-degree and out-degree of every node.
    Strictly forbids self-loops (u == v) and multigraph duplicate edges.
    Returns:
        rewired_edges: new list of directed edges
        successful_swaps: count of accepted edge swaps
        attempted_swaps: total attempted swaps
    """
    edge_set = set((u << 32) | v for u, v in edge_list)
    edges = list(edge_list)
    E = len(edges)
    if E < 2:
        return edges, 0, 0

    successful_swaps = 0
    attempted_swaps = 0

    for _ in range(num_swaps):
        attempted_swaps += 1
        i = rng.randrange(E)
        j = rng.randrange(E)
        if i == j:
            continue

        u1, v1 = edges[i]
        u2, v2 = edges[j]

        # Prevent self-loops
        if u1 == v2 or u2 == v1 or u1 == u2 or v1 == v2:
            continue

        k_new1 = (u1 << 32) | v2
        k_new2 = (u2 << 32) | v1

        # Prevent duplicate edges
        if k_new1 in edge_set or k_new2 in edge_set:
            continue

        k_old1 = (u1 << 32) | v1
        k_old2 = (u2 << 32) | v2

        edge_set.remove(k_old1)
        edge_set.remove(k_old2)
        edge_set.add(k_new1)
        edge_set.add(k_new2)

        edges[i] = (u1, v2)
        edges[j] = (u2, v1)
        successful_swaps += 1

    return edges, successful_swaps, attempted_swaps


def count_mutual_motifs(
    edge_list: list[tuple[int, int]],
    neuron_nt: dict[int, int],
) -> tuple[int, Counter[str]]:
    """
    Counts mutual dyads (u <-> v) and categorizes them by unordered transmitter pairing.
    """
    edge_set = set((u << 32) | v for u, v in edge_list)
    mutual_dyads = 0
    pair_counts: Counter[str] = Counter()

    for u, v in edge_list:
        if u < v:
            rev_k = (v << 32) | u
            if rev_k in edge_set:
                nt_u = neuron_nt.get(u, -1)
                nt_v = neuron_nt.get(v, -1)
                if 0 <= nt_u < 6 and 0 <= nt_v < 6:
                    mutual_dyads += 1
                    p_name = format_pair_name(nt_u, nt_v)
                    pair_counts[p_name] += 1

    return mutual_dyads, pair_counts


def run_cx_rewiring_analysis(
    file_path: Path,
    num_permutations: int = 100,
    swap_multiplier: int = 10,
    eval_thresholds: list[int] | None = None,
    output_json: Path | None = None,
    random_seed: int = 42,
) -> dict[str, Any]:
    if eval_thresholds is None:
        eval_thresholds = [3, 5]

    if output_json is None:
        output_json = PROJECT_ROOT / "results" / "real_data_pilot" / "central_complex_degree_preserving_null.json"
    output_json.parent.mkdir(parents=True, exist_ok=True)

    start_time = time.perf_counter()
    rng = random.Random(random_seed)

    print("==================================================================================")
    print("CONTROLLED CENTRAL COMPLEX ANALYSIS: DIRECTED DEGREE-PRESERVING NULL MODELS")
    print(f"Dataset:       {file_path.name}")
    print(f"Regions:       {TARGET_REGIONS}")
    print(f"Thresholds:    w >= {eval_thresholds}")
    print(f"Permutations:  {num_permutations} (swap multiplier: {swap_multiplier}x)")
    print(f"Random Seed:   {random_seed}")
    print("==================================================================================\n")

    # Step 1: Stream dataset, build regional edge dictionaries, derive whole-brain consensus NTs
    print(">>> Step 1: Streaming dataset and accumulating regional edges + presynaptic NT mass...")
    regional_edges: dict[str, dict[tuple[int, int], int]] = {r: defaultdict(int) for r in TARGET_REGIONS}
    neuron_out_mass: dict[int, list[float]] = defaultdict(lambda: [0.0] * 6)
    total_records = 0

    with open(file_path, "rb") as f:
        reader = ipc.open_file(f)
        num_batches = reader.num_record_batches
        prob_cols = [f"{nt}_avg" for nt in NT_CLASSES]

        for b_idx in range(num_batches):
            batch = reader.get_batch(b_idx)
            pres = batch.column("pre_pt_root_id").to_pylist()
            posts = batch.column("post_pt_root_id").to_pylist()
            weights = batch.column("syn_count").to_pylist()
            npils = batch.column("neuropil").to_pylist()

            p_arrays = [batch.column(col).to_pylist() for col in prob_cols]

            for i in range(len(pres)):
                p = pres[i]
                q = posts[i]
                w = weights[i]
                r = npils[i]

                if p is None or q is None or w is None or w <= 0 or p == q:
                    continue

                total_records += 1

                # Regional edges
                if r in regional_edges:
                    regional_edges[r][(p, q)] += w

                # Whole-brain presynaptic probability mass
                probs = [p_arrays[c][i] for c in range(6)]
                if all(val is not None for val in probs):
                    mass = neuron_out_mass[p]
                    for c in range(6):
                        mass[c] += w * probs[c]

            if (b_idx + 1) % 50 == 0 or (b_idx + 1) == num_batches:
                elapsed = time.perf_counter() - start_time
                ram = get_peak_memory_mb()
                print(f"    Batches: {b_idx + 1:3d}/{num_batches} ({total_records:10,d} rows) | Time: {elapsed:5.1f}s | RAM: {ram:6.1f} MB")

    ingest_time = time.perf_counter() - start_time
    print(f"\nIngestion complete in {ingest_time:.2f}s.")

    # Step 2: Assign consensus transmitter per neuron
    neuron_nt: dict[int, int] = {}
    for n, mass in neuron_out_mass.items():
        total_m = sum(mass)
        if total_m > 0:
            best_c = 0
            best_m = mass[0]
            for c in range(1, 6):
                if mass[c] > best_m:
                    best_m = mass[c]
                    best_c = c
            neuron_nt[n] = best_c

    print(f"Assigned consensus neurotransmitter to {len(neuron_nt):,} neurons.")

    # All 21 unordered pair types
    pair_types = []
    for c1 in range(6):
        for c2 in range(c1, 6):
            pair_types.append(format_pair_name(c1, c2))

    # Step 3: Run Regional Rewiring Analysis
    print("\n>>> Step 2: Executing Directed Degree-Preserving Rewiring across EB, FB, and PB...")
    regional_results: dict[str, Any] = {}

    for r in TARGET_REGIONS:
        r_start = time.perf_counter()
        print(f"\n==================================================================================")
        print(f"REGION: {r}")
        print(f"==================================================================================")
        edges_w = regional_edges[r]
        region_dict: dict[str, Any] = {}

        for t in eval_thresholds:
            t_thresh_start = time.perf_counter()
            # Filter edges at threshold with valid transmitter classifications
            raw_edges = [
                k for k, w in edges_w.items()
                if w >= t and k[0] in neuron_nt and k[1] in neuron_nt
            ]
            E = len(raw_edges)
            active_nodes = set(u for u, v in raw_edges) | set(v for u, v in raw_edges)
            V = len(active_nodes)

            if E < 2:
                print(f"  Threshold w >= {t}: Too few edges ({E}) to evaluate.")
                continue

            orig_in = Counter(v for u, v in raw_edges)
            orig_out = Counter(u for u, v in raw_edges)

            # Empirical mutual dyads and motif counts
            obs_m, obs_pairs = count_mutual_motifs(raw_edges, neuron_nt)
            obs_r_edge = (2 * obs_m / E) if E > 0 else 0.0

            # Pre-allocate null distribution containers
            null_m_dist: list[int] = [0] * num_permutations
            null_pair_dist: dict[str, list[int]] = {p: [0] * num_permutations for p in pair_types}
            mixing_fractions: list[float] = [0.0] * num_permutations

            swaps_per_perm = swap_multiplier * E
            print(f"\n  [{r} w >= {t}] Nodes: {V:,} | Directed Edges: {E:,} | Obs Mutual Dyads: {obs_m:,} (R_edge = {obs_r_edge*100:.2f}%)")
            print(f"  Running {num_permutations} permutations ({swaps_per_perm:,} swap attempts/perm)...")

            # Execute Markov Chain
            current_edges = list(raw_edges)
            orig_set = set((u << 32) | v for u, v in raw_edges)

            for b in range(num_permutations):
                # Rewire
                rewired, succ, att = directed_edge_swap(current_edges, swaps_per_perm, rng)
                # Verify exact in-degree & out-degree invariants
                rew_in = Counter(v for u, v in rewired)
                rew_out = Counter(u for u, v in rewired)
                assert orig_in == rew_in, f"[{r} w>={t}] In-degree sequence violation at perm {b}!"
                assert orig_out == rew_out, f"[{r} w>={t}] Out-degree sequence violation at perm {b}!"
                assert len(set(rewired)) == len(rewired), f"[{r} w>={t}] Multigraph duplicate edge detected at perm {b}!"

                # Measure mixing fraction relative to empirical graph
                rew_set = set((u << 32) | v for u, v in rewired)
                retained = len(orig_set & rew_set)
                mix_frac = 1.0 - (retained / E)
                mixing_fractions[b] = mix_frac

                # Evaluate mutual dyads in rewired graph
                rew_m, rew_pairs = count_mutual_motifs(rewired, neuron_nt)
                null_m_dist[b] = rew_m
                for p in pair_types:
                    null_pair_dist[p][b] = rew_pairs.get(p, 0)

                # Reset or continue chain: restarting from empirical graph guarantees independent samples
                current_edges = list(raw_edges)

                if (b + 1) % 25 == 0 or (b + 1) == num_permutations:
                    print(f"    Permutation {b + 1:3d}/{num_permutations} | Avg rewired: {mix_frac*100:.1f}% | Null M: {rew_m:4d}")

            # Statistical Synthesis
            def calc_perm_stats(obs_val: int, dist: list[int]) -> dict[str, Any]:
                mean_val = sum(dist) / len(dist)
                var_val = sum((x - mean_val) ** 2 for x in dist) / (len(dist) - 1) if len(dist) > 1 else 0.0
                std_val = math.sqrt(var_val) if var_val > 0 else 1e-6
                z = (obs_val - mean_val) / std_val
                # Empirical 2-tailed p-value with finite-sample +1 correction
                extreme_count = sum(1 for x in dist if abs(x - mean_val) >= abs(obs_val - mean_val))
                p_val = (extreme_count + 1) / (len(dist) + 1)
                enrichment = (obs_val / mean_val) if mean_val > 0 else 0.0
                return {
                    "observed": obs_val,
                    "null_mean": round(mean_val, 2),
                    "null_std": round(std_val, 2),
                    "z_score": round(z, 2),
                    "empirical_p_value": p_val,
                    "min_resolvable_p_value": round(1.0 / (len(dist) + 1), 6),
                    "enrichment_ratio": round(enrichment, 3),
                    "significant": p_val < 0.05,
                }

            # Reciprocity stats
            m_stats = calc_perm_stats(obs_m, null_m_dist)

            # Motif stats
            motif_stats: dict[str, Any] = {}
            for p in pair_types:
                motif_stats[p] = calc_perm_stats(obs_pairs.get(p, 0), null_pair_dist[p])

            mean_mixing = sum(mixing_fractions) / len(mixing_fractions)

            threshold_entry = {
                "threshold": t,
                "nodes": V,
                "directed_edges": E,
                "mean_rewired_fraction_pct": round(mean_mixing * 100.0, 2),
                "mutual_dyads_observed": obs_m,
                "reciprocity_edge_pct_observed": round(obs_r_edge * 100.0, 2),
                "mutual_dyad_null_stats": m_stats,
                "motifs_null_stats": motif_stats,
                "runtime_seconds": round(time.perf_counter() - t_thresh_start, 2),
            }
            region_dict[f"w{t}"] = threshold_entry

            # Print summary table for key motifs
            print(f"\n  --- Key Motif Results for {r} (w >= {t}) ---")
            print(f"  {'Motif':12s} | {'Observed':9s} | {'Null Mean':9s} | {'Null Std':8s} | {'Enrich':8s} | {'Z-Score':9s} | {'Empirical p':12s}")
            print("  " + "-" * 78)
            key_motifs = ["gaba_gaba", "ach_gaba", "ach_ach", "glut_glut", "gaba_glut"]
            for km in key_motifs:
                ks = motif_stats[km]
                print(f"  {km:12s} | {ks['observed']:9,d} | {ks['null_mean']:9.1f} | {ks['null_std']:8.2f} | {ks['enrichment_ratio']:7.2f}x | {ks['z_score']:+9.2f} | p <= {ks['empirical_p_value']:.4f}")

        regional_results[r] = region_dict

    total_runtime = time.perf_counter() - start_time
    peak_ram = get_peak_memory_mb()

    artifact = {
        "metadata": {
            "execution_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dataset": file_path.name,
            "pipeline": "Controlled Central Complex Directed Degree-Preserving Null Model Analysis",
            "regions_evaluated": TARGET_REGIONS,
            "thresholds_evaluated": eval_thresholds,
            "num_permutations": num_permutations,
            "swap_multiplier": swap_multiplier,
            "random_seed": random_seed,
            "runtime_seconds": round(total_runtime, 2),
            "peak_ram_mb": round(peak_ram, 1),
        },
        "regional_results": regional_results,
    }

    with output_json.open("w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)

    print(f"\nAnalysis complete in {total_runtime:.2f}s (Peak RAM: {peak_ram:.1f} MB).")
    print(f"Results saved to: {output_json}\n")

    return artifact


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze Central Complex under directed degree-preserving edge-swap null models.")
    parser.add_argument("--file", type=Path, default=PROJECT_ROOT / "data" / "raw" / "fafb_v783" / "proofread_connections_783.feather")
    parser.add_argument("--permutations", type=int, default=100)
    parser.add_argument("--multiplier", type=int, default=10)
    parser.add_argument("--thresholds", nargs="+", type=int, default=[3, 5])
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    run_cx_rewiring_analysis(
        file_path=args.file,
        num_permutations=args.permutations,
        swap_multiplier=args.multiplier,
        eval_thresholds=args.thresholds,
        random_seed=args.seed,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

