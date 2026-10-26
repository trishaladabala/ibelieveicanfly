#!/usr/bin/env python3
"""
Directed Degree-Preserving Rewiring (Maslov-Sneppen) Mixing Diagnostics
for the Adult Drosophila Central Complex (EB, FB, PB).

Addresses Phase 3 Requirements:
1. Exact invariant testing on synthetic graphs with known topology.
2. Invariant assertions on real empirical central complex subgraphs.
3. Detailed proposal/acceptance/rejection accounting:
   - Acceptance rate
   - Rejection breakdown: identical index, self-loop, shared nodes, duplicate multigraph edge.
4. Trajectory analysis across swap multipliers (1x, 2x, 5x, 10x, 20x, 30x, 50x, 100x |E|):
   - Rewired edge fraction
   - Mutual dyad count M(t)
   - Primary transmitter motif count (EB: GABA-GABA, FB: ACh-GABA, PB: ACh-ACh)
5. Continuous MCMC chain autocorrelation:
   - Burn-in phase
   - Thinning interval
   - Autocorrelation function (ACF) up to lag 20
   - Integrated autocorrelation time (tau_int) and Effective Sample Size (ESS)
6. Multi-chain convergence & consistency across distinct random seeds (seeds 42, 101, 777, 2026).
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


def directed_edge_swap_instrumented(
    edge_list: list[tuple[int, int]],
    num_swaps: int,
    rng: random.Random,
) -> tuple[list[tuple[int, int]], dict[str, int]]:
    """
    Performs directed edge swaps with detailed accounting of acceptance and rejection reasons.
    Preserves exact directed in-degree and out-degree sequences.
    Strictly forbids self-loops and duplicate edges.
    """
    edge_set = set((u << 32) | v for u, v in edge_list)
    edges = list(edge_list)
    E = len(edges)
    stats = {
        "attempted": num_swaps,
        "accepted": 0,
        "rejected_same_index": 0,
        "rejected_self_loop": 0,
        "rejected_shared_node": 0,
        "rejected_duplicate_edge": 0,
    }
    if E < 2:
        return edges, stats

    for _ in range(num_swaps):
        i = rng.randrange(E)
        j = rng.randrange(E)
        if i == j:
            stats["rejected_same_index"] += 1
            continue

        u1, v1 = edges[i]
        u2, v2 = edges[j]

        # Prevent self-loops
        if u1 == v2 or u2 == v1:
            stats["rejected_self_loop"] += 1
            continue

        # Prevent swaps between edges sharing source or target (shared endpoints)
        if u1 == u2 or v1 == v2:
            stats["rejected_shared_node"] += 1
            continue

        k_new1 = (u1 << 32) | v2
        k_new2 = (u2 << 32) | v1

        # Prevent multigraph duplicate edges
        if k_new1 in edge_set or k_new2 in edge_set:
            stats["rejected_duplicate_edge"] += 1
            continue

        k_old1 = (u1 << 32) | v1
        k_old2 = (u2 << 32) | v2

        edge_set.remove(k_old1)
        edge_set.remove(k_old2)
        edge_set.add(k_new1)
        edge_set.add(k_new2)

        edges[i] = (u1, v2)
        edges[j] = (u2, v1)
        stats["accepted"] += 1

    return edges, stats


def count_mutual_motifs(
    edge_list: list[tuple[int, int]],
    neuron_nt: dict[int, int],
) -> tuple[int, Counter[str]]:
    """Counts mutual dyads and categorizes them by unordered transmitter pairing."""
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


def verify_invariants(
    orig_edges: list[tuple[int, int]],
    rewired_edges: list[tuple[int, int]],
    context: str = "",
) -> None:
    """Rigorous invariant checks for directed degree-preserving rewiring."""
    assert len(rewired_edges) == len(orig_edges), f"{context}: Edge count altered!"
    orig_in = Counter(v for u, v in orig_edges)
    orig_out = Counter(u for u, v in orig_edges)
    rew_in = Counter(v for u, v in rewired_edges)
    rew_out = Counter(u for u, v in rewired_edges)
    assert orig_in == rew_in, f"{context}: In-degree sequence violation!"
    assert orig_out == rew_out, f"{context}: Out-degree sequence violation!"
    for u, v in rewired_edges:
        assert u != v, f"{context}: Self-loop detected ({u} -> {v})!"
    assert len(set(rewired_edges)) == len(rewired_edges), f"{context}: Multigraph duplicate edge detected!"


def test_synthetic_invariants() -> None:
    """Verifies algorithm on synthetic graphs with known topology."""
    print("Running synthetic graph invariant tests...")
    rng = random.Random(42)

    # Synthetic graph 1: 4-node bipartite switch graph (u1->v1, u2->v2, u3->v3, u4->v4)
    # Allows valid edge swaps between independent pairs
    synth1 = [
        (1, 10), (2, 20), (3, 30), (4, 40),
        (10, 1), (20, 2)  # Some mutual dyads
    ]
    rew1, stats1 = directed_edge_swap_instrumented(synth1, 100, rng)
    verify_invariants(synth1, rew1, "Synthetic Graph 1")
    assert stats1["accepted"] > 0, "No swaps accepted on bipartite switch graph!"

    # Synthetic graph 2: Directed cycle C_4 (1->2->3->4->1)
    # Any swap would introduce self-loops or duplicate edges if attempted on adjacent edges
    synth2 = [(1, 2), (2, 3), (3, 4), (4, 1)]
    rew2, stats2 = directed_edge_swap_instrumented(synth2, 50, rng)
    verify_invariants(synth2, rew2, "Synthetic Cycle C_4")

    # Synthetic graph 3: Disconnected components (1->2, 2->1, 3->4, 4->3)
    synth3 = [(1, 2), (2, 1), (3, 4), (4, 3)]
    rew3, stats3 = directed_edge_swap_instrumented(synth3, 100, rng)
    verify_invariants(synth3, rew3, "Synthetic Mutual Components")
    print("  All synthetic invariants passed successfully.\n")


def compute_autocorrelation(series: list[float], max_lag: int = 20) -> list[float]:
    """Computes autocorrelation function (ACF) up to max_lag."""
    N = len(series)
    if N < 2:
        return [1.0]
    mean_val = sum(series) / N
    var_val = sum((x - mean_val) ** 2 for x in series) / N
    if var_val == 0:
        return [1.0] * (min(max_lag, N) + 1)

    acf = [1.0]
    for k in range(1, min(max_lag + 1, N)):
        cov_k = sum((series[t] - mean_val) * (series[t + k] - mean_val) for t in range(N - k)) / N
        acf.append(cov_k / var_val)
    return acf


def compute_tau_int_and_ess(acf: list[float], N: int) -> tuple[float, float]:
    """
    Computes integrated autocorrelation time (tau_int) using Geyer's initial positive sequence cutoff
    and effective sample size (ESS).
    """
    tau = 0.5
    for k in range(1, len(acf)):
        if acf[k] <= 0:
            break
        tau += acf[k]
    tau_int = max(0.5, tau)
    ess = N / (2.0 * tau_int)
    return tau_int, min(float(N), ess)


def load_cx_graphs(file_path: Path, eval_thresholds: list[int]) -> tuple[dict[str, dict[int, list[tuple[int, int]]]], dict[int, int]]:
    """Loads central complex directed edge subgraphs and neuron consensus phenotypes."""
    print(f"Loading FAFB v783 dataset from: {file_path}")
    t0 = time.perf_counter()

    neuron_outputs: dict[int, list[float]] = defaultdict(lambda: [0.0] * 6)
    regional_edges: dict[str, dict[tuple[int, int], int]] = {r: defaultdict(int) for r in TARGET_REGIONS}

    with open(file_path, "rb") as f:
        reader = ipc.RecordBatchFileReader(f)
        for i in range(reader.num_record_batches):
            batch = reader.get_record_batch(i)
            pre_arr = batch.column("pre_pt_root_id")
            post_arr = batch.column("post_pt_root_id")
            syn_arr = batch.column("syn_count")
            neuropil_arr = batch.column("neuropil")

            ach_arr = batch.column("ach_avg")
            gaba_arr = batch.column("gaba_avg")
            glut_arr = batch.column("glut_avg")
            da_arr = batch.column("da_avg")
            oct_arr = batch.column("oct_avg")
            ser_arr = batch.column("ser_avg")

            for j in range(batch.num_rows):
                pre = pre_arr[j].as_py()
                post = post_arr[j].as_py()
                syn = syn_arr[j].as_py()
                if pre == post:
                    continue

                # Accumulate weighted probabilities
                v_ach = ach_arr[j].as_py()
                v_gaba = gaba_arr[j].as_py()
                v_glut = glut_arr[j].as_py()
                v_da = da_arr[j].as_py()
                v_oct = oct_arr[j].as_py()
                v_ser = ser_arr[j].as_py()

                if v_ach is not None:
                    neuron_outputs[pre][0] += syn * v_ach
                    neuron_outputs[pre][1] += syn * v_gaba
                    neuron_outputs[pre][2] += syn * v_glut
                    neuron_outputs[pre][3] += syn * v_da
                    neuron_outputs[pre][4] += syn * v_oct
                    neuron_outputs[pre][5] += syn * v_ser

                np_val = neuropil_arr[j].as_py()
                if np_val in TARGET_REGIONS:
                    regional_edges[np_val][(pre, post)] += syn

    # Consensus labels
    neuron_nt: dict[int, int] = {}
    for nid, probs in neuron_outputs.items():
        s = sum(probs)
        if s > 0:
            neuron_nt[nid] = int(probs.index(max(probs)))

    # Filtered regional edge lists at thresholds
    cx_graphs: dict[str, dict[int, list[tuple[int, int]]]] = {r: {} for r in TARGET_REGIONS}
    for r in TARGET_REGIONS:
        for t in eval_thresholds:
            valid_edges = [
                k for k, w in regional_edges[r].items()
                if w >= t and k[0] in neuron_nt and k[1] in neuron_nt
            ]
            cx_graphs[r][t] = valid_edges

    print(f"Data loading complete in {time.perf_counter() - t0:.2f}s (RAM: {get_peak_memory_mb():.1f} MB)")
    return cx_graphs, neuron_nt


def run_mixing_diagnostics(
    cx_graphs: dict[str, dict[int, list[tuple[int, int]]]],
    neuron_nt: dict[int, int],
    output_path: Path,
) -> dict[str, Any]:
    """Runs systematic mixing and autocorrelation diagnostics across Central Complex neuropils."""
    primary_motifs = {
        "EB": "gaba_gaba",
        "FB": "ach_gaba",
        "PB": "ach_ach",
    }
    swap_multipliers = [1, 2, 5, 10, 20, 30, 50, 100]
    multi_seeds = [42, 101, 777, 2026]

    diagnostics_results: dict[str, Any] = {
        "metadata": {
            "execution_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "regions": TARGET_REGIONS,
            "thresholds": [3, 5],
            "swap_multipliers": swap_multipliers,
            "multi_seeds": multi_seeds,
            "chain_samples": 200,
            "burn_in_multiplier": 20,
            "thinning_multiplier": 5,
        },
        "regions": {},
    }

    print("\n" + "=" * 80)
    print("STARTING DIRECTED DEGREE-PRESERVING REWIRING MIXING DIAGNOSTICS")
    print("=" * 80)

    for r in TARGET_REGIONS:
        diagnostics_results["regions"][r] = {}
        target_motif = primary_motifs[r]
        for t in [3, 5]:
            edges = cx_graphs[r][t]
            E = len(edges)
            active_nodes = set(u for u, v in edges) | set(v for u, v in edges)
            V = len(active_nodes)
            obs_m, obs_pairs = count_mutual_motifs(edges, neuron_nt)
            obs_target = obs_pairs.get(target_motif, 0)
            orig_set = set((u << 32) | v for u, v in edges)

            print(f"\n--- Region: {r} | Threshold w >= {t} ---")
            print(f"Nodes: {V:,} | Edges: {E:,} | Obs Mutual Dyads: {obs_m:,} | Obs {target_motif}: {obs_target:,}")

            # 1. Swap Multiplier Trajectory (evaluated from seed graph)
            print("  Evaluating swap multiplier trajectory (1x to 100x |E|)...")
            trajectory: list[dict[str, Any]] = []
            rng_traj = random.Random(42)

            for mult in swap_multipliers:
                num_swaps = mult * E
                rewired, stats = directed_edge_swap_instrumented(edges, num_swaps, rng_traj)
                verify_invariants(edges, rewired, f"{r} w>={t} mult={mult}")

                rew_set = set((u << 32) | v for u, v in rewired)
                retained_edges = len(orig_set & rew_set)
                rewired_fraction = 1.0 - (retained_edges / E)
                acceptance_rate = stats["accepted"] / stats["attempted"] if stats["attempted"] > 0 else 0.0

                m_count, p_counts = count_mutual_motifs(rewired, neuron_nt)
                t_count = p_counts.get(target_motif, 0)

                point = {
                    "multiplier": mult,
                    "attempted": num_swaps,
                    "accepted": stats["accepted"],
                    "acceptance_rate_pct": round(acceptance_rate * 100.0, 2),
                    "rejections": {
                        "same_index": stats["rejected_same_index"],
                        "self_loop": stats["rejected_self_loop"],
                        "shared_node": stats["rejected_shared_node"],
                        "duplicate_edge": stats["rejected_duplicate_edge"],
                    },
                    "rewired_fraction_pct": round(rewired_fraction * 100.0, 2),
                    "mutual_dyads": m_count,
                    "target_motif_count": t_count,
                }
                trajectory.append(point)
                print(f"    {mult:3d}x |E|: Acc = {point['acceptance_rate_pct']:5.2f}% | Rewired = {point['rewired_fraction_pct']:5.2f}% | M = {m_count:4d} | {target_motif} = {t_count:4d}")

            # 2. Continuous MCMC Chain & Autocorrelation Analysis
            print("  Running continuous MCMC chain for autocorrelation analysis (200 samples, thin=5x, burn=20x)...")
            rng_chain = random.Random(42)
            burn_in_swaps = 20 * E
            thin_swaps = 5 * E
            num_chain_samples = 200

            # Burn-in
            current_chain_edges, burn_stats = directed_edge_swap_instrumented(edges, burn_in_swaps, rng_chain)
            verify_invariants(edges, current_chain_edges, f"{r} w>={t} burn-in")

            chain_m_series: list[float] = []
            chain_target_series: list[float] = []
            chain_rewired_fractions: list[float] = []

            for sample_idx in range(num_chain_samples):
                current_chain_edges, _ = directed_edge_swap_instrumented(current_chain_edges, thin_swaps, rng_chain)
                sample_m, sample_pairs = count_mutual_motifs(current_chain_edges, neuron_nt)
                sample_target = float(sample_pairs.get(target_motif, 0))
                chain_m_series.append(float(sample_m))
                chain_target_series.append(sample_target)

                curr_set = set((u << 32) | v for u, v in current_chain_edges)
                chain_rewired_fractions.append(round((1.0 - len(orig_set & curr_set) / E) * 100.0, 2))

            # ACF and ESS
            acf_m = compute_autocorrelation(chain_m_series, max_lag=20)
            tau_m, ess_m = compute_tau_int_and_ess(acf_m, num_chain_samples)

            acf_target = compute_autocorrelation(chain_target_series, max_lag=20)
            tau_target, ess_target = compute_tau_int_and_ess(acf_target, num_chain_samples)

            m_mean = sum(chain_m_series) / num_chain_samples
            m_var = sum((x - m_mean) ** 2 for x in chain_m_series) / (num_chain_samples - 1)
            m_std = math.sqrt(m_var)

            target_mean = sum(chain_target_series) / num_chain_samples
            target_var = sum((x - target_mean) ** 2 for x in chain_target_series) / (num_chain_samples - 1)
            target_std = math.sqrt(target_var)

            chain_diagnostics = {
                "num_samples": num_chain_samples,
                "burn_in_multiplier": 20,
                "thinning_multiplier": 5,
                "mean_rewired_fraction_pct": round(sum(chain_rewired_fractions) / len(chain_rewired_fractions), 2),
                "mutual_dyads": {
                    "mean": round(m_mean, 2),
                    "std": round(m_std, 2),
                    "acf_lags_1_to_5": [round(x, 3) for x in acf_m[1:6]],
                    "acf_lag_10": round(acf_m[10], 3) if len(acf_m) > 10 else None,
                    "tau_int": round(tau_m, 2),
                    "effective_sample_size": round(ess_m, 1),
                },
                "target_motif": {
                    "motif": target_motif,
                    "mean": round(target_mean, 2),
                    "std": round(target_std, 2),
                    "acf_lags_1_to_5": [round(x, 3) for x in acf_target[1:6]],
                    "acf_lag_10": round(acf_target[10], 3) if len(acf_target) > 10 else None,
                    "tau_int": round(tau_target, 2),
                    "effective_sample_size": round(ess_target, 1),
                },
            }
            print(f"    Stationary M: {m_mean:.1f} ± {m_std:.1f} (tau_int = {tau_m:.2f}, ESS = {ess_m:.1f}/{num_chain_samples})")
            print(f"    Stationary {target_motif}: {target_mean:.1f} ± {target_std:.1f} (tau_int = {tau_target:.2f}, ESS = {ess_target:.1f}/{num_chain_samples})")

            # 3. Multi-Chain Consistency (4 distinct random seeds)
            print("  Evaluating multi-chain consistency across 4 independent seeds...")
            seed_comparisons: list[dict[str, Any]] = []
            for seed in multi_seeds:
                rng_s = random.Random(seed)
                # Rewire with 20x |E| swaps
                rew_s, _ = directed_edge_swap_instrumented(edges, 20 * E, rng_s)
                verify_invariants(edges, rew_s, f"{r} w>={t} seed={seed}")
                sm, sp = count_mutual_motifs(rew_s, neuron_nt)
                st = sp.get(target_motif, 0)
                seed_comparisons.append({
                    "seed": seed,
                    "mutual_dyads": sm,
                    "target_motif_count": st,
                })

            diagnostics_results["regions"][r][f"w{t}"] = {
                "threshold": t,
                "nodes": V,
                "edges": E,
                "observed_mutual_dyads": obs_m,
                "observed_target_motif": obs_target,
                "target_motif": target_motif,
                "swap_trajectory": trajectory,
                "continuous_chain": chain_diagnostics,
                "multi_seed_comparison": seed_comparisons,
            }

    # Save to JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(diagnostics_results, f, indent=2)

    print("\n" + "=" * 80)
    print(f"Diagnostics successfully saved to: {output_path}")
    print(f"Total runtime: {time.perf_counter() - t0:.2f}s | Peak RAM: {get_peak_memory_mb():.1f} MB")
    print("=" * 80)
    return diagnostics_results


def main() -> None:
    parser = argparse.ArgumentParser(description="MCMC Rewiring Mixing Diagnostics for Drosophila Central Complex")
    parser.add_argument(
        "--file",
        type=Path,
        default=PROJECT_ROOT / "data" / "raw" / "fafb_v783" / "proofread_connections_783.feather",
        help="Path to proofread connections feather file",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "results" / "real_data_pilot" / "null_model_mixing_diagnostics.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    # Step 1: Synthetic tests
    test_synthetic_invariants()

    # Step 2: Real dataset diagnostics
    cx_graphs, neuron_nt = load_cx_graphs(args.file, eval_thresholds=[3, 5])
    run_mixing_diagnostics(cx_graphs, neuron_nt, args.out)


if __name__ == "__main__":
    t0 = time.perf_counter()
    main()

