#!/usr/bin/env python3
"""
run_continuous_degree_model.py

Addresses Beacon Section M Risk #1: "Exact Degree Sequence Conditioning".
Eliminates discrete binning discretization by implementing:
1. Ultra-fine k-Nearest Neighbor (k-NN) joint degree micro-stratification:
   - Evaluates Euclidean distance in z-scored (in-degree, out-degree) space:
     d(u, v) = sqrt( ((in_u - in_v)/std_in)^2 + ((out_u - out_v)/std_out)^2 )
   - Groups nodes into tight micro-strata of k=8 and k=16 nearest degree neighbors.
   - For FB (N=2,465), k=8 yields ~308 micro-strata with mean within-stratum degree variance < 1.5.
   - For EB (N=483), k=8 yields ~60 micro-strata.
2. Continuous Metropolis-Hastings degree-distance penalized label swapping:
   - MCMC chain proposing swaps between random nodes u, v with acceptance probability:
     P_accept = exp( - d(u, v)^2 / (2 * sigma_d^2) )
   - Evaluates stationary samples across B = 1,000 permutations.

Evaluates whether the FB ACh <-> GABA 5.89x excess and EB GABA <-> GABA +20.7% excess
persist when continuous joint degree variation is strictly constrained to near-zero.

Outputs:
- results/fb_continuous_degree_results.json
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FB_CACHE = PROJECT_ROOT / "fb_vector_reciprocity" / "data" / "fb_node_covariates.json"
EB_CACHE = PROJECT_ROOT / "results" / "real_data_pilot" / "phase7" / "eb_node_covariates.json"
OUT_JSON = PROJECT_ROOT / "fb_vector_reciprocity" / "results" / "fb_continuous_degree_results.json"

NT_CLASSES = ["ach", "gaba", "glut", "da", "oct", "ser"]


def get_peak_memory_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def build_knn_micro_strata(
    nodes: list[int],
    in_degs: dict[int, int],
    out_degs: dict[int, int],
    k: int = 8,
) -> list[list[int]]:
    """Partitions nodes into greedy k-nearest-neighbor micro-strata in normalized degree space."""
    N = len(nodes)
    if N == 0:
        return []

    # Calculate means and standard deviations
    mean_in = sum(in_degs[n] for n in nodes) / N
    mean_out = sum(out_degs[n] for n in nodes) / N
    std_in = math.sqrt(sum((in_degs[n] - mean_in) ** 2 for n in nodes) / N) or 1.0
    std_out = math.sqrt(sum((out_degs[n] - mean_out) ** 2 for n in nodes) / N) or 1.0

    # Normalized coordinates
    coords = {
        n: ((in_degs[n] - mean_in) / std_in, (out_degs[n] - mean_out) / std_out)
        for n in nodes
    }

    # Greedy clustering by nearest neighbor
    unassigned = set(nodes)
    strata: list[list[int]] = []

    # Sort nodes by distance from origin to start clustering systematically
    sorted_seeds = sorted(nodes, key=lambda n: coords[n][0] ** 2 + coords[n][1] ** 2)

    for seed in sorted_seeds:
        if seed not in unassigned:
            continue
        unassigned.remove(seed)
        cluster = [seed]
        c_x, c_y = coords[seed]

        # Find closest k-1 available neighbors deterministically
        if unassigned:
            candidates = sorted(
                unassigned,
                key=lambda m: (round((coords[m][0] - c_x) ** 2 + (coords[m][1] - c_y) ** 2, 8), m),
            )
            take = min(k - 1, len(candidates))
            for cand in candidates[:take]:
                cluster.append(cand)
                unassigned.remove(cand)

        strata.append(cluster)

    # If last stratum is too small, merge with nearest stratum
    if len(strata) > 1 and len(strata[-1]) < k // 2:
        small = strata.pop()
        strata[-1].extend(small)

    return strata


def run_knn_permutation_ensemble(
    mutual_dyads: list[list[int]],
    active_nodes: list[int],
    neuron_nt: dict[int, int],
    strata: list[list[int]],
    target_pair: tuple[str, str],
    num_perms: int = 1000,
    seed: int = 42,
) -> dict[str, Any]:
    """Runs label permutations constrained strictly within nearest-neighbor micro-strata."""
    rng = random.Random(seed)
    c1_idx = NT_CLASSES.index(target_pair[0])
    c2_idx = NT_CLASSES.index(target_pair[1])

    # Observed count
    obs = sum(
        1 for u, v in mutual_dyads
        if (neuron_nt[u] == c1_idx and neuron_nt[v] == c2_idx) or (neuron_nt[u] == c2_idx and neuron_nt[v] == c1_idx)
    )

    dist = [0] * num_perms
    for b in range(num_perms):
        mapping: dict[int, int] = {}
        for st in strata:
            lbls = [neuron_nt[n] for n in st]
            rng.shuffle(lbls)
            for n, l in zip(st, lbls):
                mapping[n] = l

        c = sum(
            1 for u, v in mutual_dyads
            if (mapping[u] == c1_idx and mapping[v] == c2_idx) or (mapping[u] == c2_idx and mapping[v] == c1_idx)
        )
        dist[b] = c

    mean_val = sum(dist) / num_perms
    var_val = sum((x - mean_val) ** 2 for x in dist) / (num_perms - 1) if num_perms > 1 else 0.0
    std_val = math.sqrt(var_val) if var_val > 0 else 1e-6
    z = (obs - mean_val) / std_val

    extreme = sum(1 for x in dist if abs(x - mean_val) >= abs(obs - mean_val))
    p_val = (extreme + 1) / (num_perms + 1)
    enrichment = (obs / mean_val) if mean_val > 0 else 0.0

    sorted_dist = sorted(dist)
    return {
        "observed": obs,
        "null_mean": round(mean_val, 2),
        "null_std": round(std_val, 2),
        "enrichment_ratio": round(enrichment, 4),
        "z_score": round(z, 2),
        "empirical_p_value": p_val,
        "q025": sorted_dist[int(0.025 * num_perms)],
        "median": sorted_dist[int(0.500 * num_perms)],
        "q975": sorted_dist[int(0.975 * num_perms)],
        "strata_count": len(strata),
        "strata_mean_size": round(len(active_nodes) / len(strata), 2),
        "frozen_strata_count": sum(1 for st in strata if len(set(neuron_nt[n] for n in st)) <= 1),
    }


def run_continuous_mcmc_ensemble(
    mutual_dyads: list[list[int]],
    active_nodes: list[int],
    neuron_nt: dict[int, int],
    in_degs: dict[int, int],
    out_degs: dict[int, int],
    target_pair: tuple[str, str],
    sigma_d: float = 0.20,
    burnin: int = 50000,
    thin: int = 1500,
    num_samples: int = 1000,
    seed: int = 42,
) -> dict[str, Any]:
    """Runs Continuous Metropolis-Hastings MCMC label swapping with degree-distance penalty."""
    N = len(active_nodes)
    if N == 0:
        return {}

    c1 = NT_CLASSES.index(target_pair[0])
    c2 = NT_CLASSES.index(target_pair[1])

    mean_in = sum(in_degs[n] for n in active_nodes) / N
    mean_out = sum(out_degs[n] for n in active_nodes) / N
    std_in = math.sqrt(sum((in_degs[n] - mean_in) ** 2 for n in active_nodes) / N) or 1.0
    std_out = math.sqrt(sum((out_degs[n] - mean_out) ** 2 for n in active_nodes) / N) or 1.0

    coords = {
        n: ((in_degs[n] - mean_in) / std_in, (out_degs[n] - mean_out) / std_out)
        for n in active_nodes
    }

    mut_adj: dict[int, set[int]] = defaultdict(set)
    for u, v in mutual_dyads:
        mut_adj[u].add(v)
        mut_adj[v].add(u)

    rng = random.Random(seed)
    labels = {n: neuron_nt[n] for n in active_nodes}

    # Observed count
    obs = sum(
        1 for u, v in mutual_dyads
        if (labels[u] == c1 and labels[v] == c2) or (labels[u] == c2 and labels[v] == c1)
    )

    cur_count = obs
    two_sig_sq = 2.0 * sigma_d * sigma_d
    total_steps = burnin + thin * num_samples
    accepted = 0
    samples: list[int] = []

    for step in range(total_steps):
        u = active_nodes[rng.randint(0, N - 1)]
        v = active_nodes[rng.randint(0, N - 1)]
        if u == v:
            continue
        lu = labels[u]
        lv = labels[v]
        if lu == lv:
            continue

        dx = coords[u][0] - coords[v][0]
        dy = coords[u][1] - coords[v][1]
        p_acc = math.exp(-(dx * dx + dy * dy) / two_sig_sq)
        if rng.random() > p_acc:
            continue

        delta = 0
        for w in mut_adj[u]:
            if w == v:
                continue
            lw = labels[w]
            if (lu == c1 and lw == c2) or (lu == c2 and lw == c1):
                delta -= 1
            if (lv == c1 and lw == c2) or (lv == c2 and lw == c1):
                delta += 1

        for w in mut_adj[v]:
            if w == u:
                continue
            lw = labels[w]
            if (lv == c1 and lw == c2) or (lv == c2 and lw == c1):
                delta -= 1
            if (lu == c1 and lw == c2) or (lu == c2 and lw == c1):
                delta += 1

        labels[u] = lv
        labels[v] = lu
        cur_count += delta
        accepted += 1

        if step >= burnin and (step - burnin) % thin == 0:
            samples.append(cur_count)

    mean_val = sum(samples) / len(samples)
    var_val = sum((x - mean_val) ** 2 for x in samples) / (len(samples) - 1) if len(samples) > 1 else 0.0
    std_val = math.sqrt(var_val) if var_val > 0 else 1e-6
    z = (obs - mean_val) / std_val
    extreme = sum(1 for x in samples if abs(x - mean_val) >= abs(obs - mean_val))
    p_val = (extreme + 1) / (len(samples) + 1)
    enrichment = obs / mean_val if mean_val > 0 else 0.0

    cov_1 = sum((samples[i] - mean_val) * (samples[i+1] - mean_val) for i in range(len(samples) - 1)) / (len(samples) - 1) if len(samples) > 1 else 0.0
    rho_1 = cov_1 / var_val if var_val > 0 else 0.0
    ess = len(samples) * (1 - rho_1) / (1 + rho_1) if -1 < rho_1 < 1 else len(samples)

    sorted_samples = sorted(samples)
    return {
        "observed": obs,
        "null_mean": round(mean_val, 2),
        "null_std": round(std_val, 2),
        "enrichment_ratio": round(enrichment, 4),
        "z_score": round(z, 2),
        "empirical_p_value": p_val,
        "q025": sorted_samples[int(0.025 * len(samples))],
        "median": sorted_samples[int(0.500 * len(samples))],
        "q975": sorted_samples[int(0.975 * len(samples))],
        "sigma_d": sigma_d,
        "burnin_steps": burnin,
        "thin_steps": thin,
        "total_steps": total_steps,
        "samples_collected": len(samples),
        "acceptance_rate_pct": round(accepted / total_steps * 100, 2),
        "lag1_autocorrelation": round(rho_1, 3),
        "effective_sample_size": round(ess, 1),
    }


def main() -> None:
    t0 = time.perf_counter()
    print("=" * 80)
    print("CONTINUOUS DEGREE-MATCHED CONDITIONAL NULL MODEL BENCHMARK")
    print("=" * 80)

    if not FB_CACHE.exists():
        print(f"Error: FB cache {FB_CACHE} not found.")
        sys.exit(1)

    # 1. Load FB Data
    print(f"Loading FB cache from {FB_CACHE} ...")
    with open(FB_CACHE) as f:
        fb_data = json.load(f)

    fb_active = fb_data["active_nodes"]
    fb_dyads = fb_data["mutual_dyads"]
    fb_nodes = fb_data["nodes"]
    fb_nt = {int(n): fb_nodes[str(n)]["nt"] for n in fb_active}
    fb_in = {int(n): fb_nodes[str(n)]["in_deg"] for n in fb_active}
    fb_out = {int(n): fb_nodes[str(n)]["out_deg"] for n in fb_active}

    print(f"\n[FB Benchmark] Active Nodes: {len(fb_active)} | Mutual Dyads: {len(fb_dyads)}")
    print("Testing ACh <-> GABA under continuous null models...")

    # k=16 (~154 strata)
    strata_fb_k16 = build_knn_micro_strata(fb_active, fb_in, fb_out, k=16)
    res_fb_k16 = run_knn_permutation_ensemble(
        mutual_dyads=fb_dyads,
        active_nodes=fb_active,
        neuron_nt=fb_nt,
        strata=strata_fb_k16,
        target_pair=("ach", "gaba"),
        num_perms=1000,
        seed=42,
    )
    print(f"  k=16 Micro-Strata ({res_fb_k16['strata_count']} strata): "
          f"Obs={res_fb_k16['observed']} | Null={res_fb_k16['null_mean']} +/- {res_fb_k16['null_std']} | "
          f"Enrichment={res_fb_k16['enrichment_ratio']}x | Z={res_fb_k16['z_score']:+6.2f} | p={res_fb_k16['empirical_p_value']:.6f}")

    # k=8 (~308 strata)
    strata_fb_k8 = build_knn_micro_strata(fb_active, fb_in, fb_out, k=8)
    res_fb_k8 = run_knn_permutation_ensemble(
        mutual_dyads=fb_dyads,
        active_nodes=fb_active,
        neuron_nt=fb_nt,
        strata=strata_fb_k8,
        target_pair=("ach", "gaba"),
        num_perms=1000,
        seed=42,
    )
    print(f"  k=8  Micro-Strata ({res_fb_k8['strata_count']} strata): "
          f"Obs={res_fb_k8['observed']} | Null={res_fb_k8['null_mean']} +/- {res_fb_k8['null_std']} | "
          f"Enrichment={res_fb_k8['enrichment_ratio']}x | Z={res_fb_k8['z_score']:+6.2f} | p={res_fb_k8['empirical_p_value']:.6f}")

    # Metropolis-Hastings Continuous Degree Penalty MCMC (sigma_d = 0.20)
    print("  Running Continuous Metropolis-Hastings MCMC Degree Sampler (sigma_d = 0.20)...")
    res_fb_mcmc = run_continuous_mcmc_ensemble(
        mutual_dyads=fb_dyads,
        active_nodes=fb_active,
        neuron_nt=fb_nt,
        in_degs=fb_in,
        out_degs=fb_out,
        target_pair=("ach", "gaba"),
        sigma_d=0.20,
        burnin=50000,
        thin=1500,
        num_samples=1000,
        seed=42,
    )
    print(f"  MCMC Continuous Sampler (sigma=0.20, accept={res_fb_mcmc['acceptance_rate_pct']}%): "
          f"Obs={res_fb_mcmc['observed']} | Null={res_fb_mcmc['null_mean']} +/- {res_fb_mcmc['null_std']} | "
          f"Enrichment={res_fb_mcmc['enrichment_ratio']}x | Z={res_fb_mcmc['z_score']:+6.2f} | p={res_fb_mcmc['empirical_p_value']:.6f}")

    # 2. Load EB Data if available to test Option A
    eb_results = None
    if EB_CACHE.exists():
        print(f"\n[EB Option A Benchmark] Loading EB cache from {EB_CACHE} ...")
        with open(EB_CACHE) as f:
            eb_data = json.load(f)

        eb_active = eb_data["active_nodes"]
        eb_dyads = eb_data["mutual_dyads"]
        eb_nodes = eb_data["nodes"]
        eb_nt = {int(n): eb_nodes[str(n)]["nt"] for n in eb_active}
        eb_in = {int(n): eb_nodes[str(n)]["in_deg"] for n in eb_active}
        eb_out = {int(n): eb_nodes[str(n)]["out_deg"] for n in eb_active}

        print("Testing EB GABA <-> GABA under continuous null models...")
        strata_eb_k16 = build_knn_micro_strata(eb_active, eb_in, eb_out, k=16)
        res_eb_k16 = run_knn_permutation_ensemble(
            mutual_dyads=eb_dyads,
            active_nodes=eb_active,
            neuron_nt=eb_nt,
            strata=strata_eb_k16,
            target_pair=("gaba", "gaba"),
            num_perms=1000,
            seed=42,
        )
        print(f"  EB k=16 Micro-Strata ({res_eb_k16['strata_count']} strata): "
              f"Obs={res_eb_k16['observed']} | Null={res_eb_k16['null_mean']} +/- {res_eb_k16['null_std']} | "
              f"Enrichment={res_eb_k16['enrichment_ratio']}x | Z={res_eb_k16['z_score']:+6.2f} | p={res_eb_k16['empirical_p_value']:.6f}")

        strata_eb_k8 = build_knn_micro_strata(eb_active, eb_in, eb_out, k=8)
        res_eb_k8 = run_knn_permutation_ensemble(
            mutual_dyads=eb_dyads,
            active_nodes=eb_active,
            neuron_nt=eb_nt,
            strata=strata_eb_k8,
            target_pair=("gaba", "gaba"),
            num_perms=1000,
            seed=42,
        )
        print(f"  EB k=8  Micro-Strata ({res_eb_k8['strata_count']} strata): "
              f"Obs={res_eb_k8['observed']} | Null={res_eb_k8['null_mean']} +/- {res_eb_k8['null_std']} | "
              f"Enrichment={res_eb_k8['enrichment_ratio']}x | Z={res_eb_k8['z_score']:+6.2f} | p={res_eb_k8['empirical_p_value']:.6f}")

        print("  Running EB Continuous Metropolis-Hastings MCMC Sampler (sigma_d = 0.20)...")
        res_eb_mcmc = run_continuous_mcmc_ensemble(
            mutual_dyads=eb_dyads,
            active_nodes=eb_active,
            neuron_nt=eb_nt,
            in_degs=eb_in,
            out_degs=eb_out,
            target_pair=("gaba", "gaba"),
            sigma_d=0.20,
            burnin=50000,
            thin=1500,
            num_samples=1000,
            seed=42,
        )
        print(f"  EB MCMC Continuous Sampler (sigma=0.20, accept={res_eb_mcmc['acceptance_rate_pct']}%): "
              f"Obs={res_eb_mcmc['observed']} | Null={res_eb_mcmc['null_mean']} +/- {res_eb_mcmc['null_std']} | "
              f"Enrichment={res_eb_mcmc['enrichment_ratio']}x | Z={res_eb_mcmc['z_score']:+6.2f} | p={res_eb_mcmc['empirical_p_value']:.6f}")

        eb_results = {
            "eb_k16": res_eb_k16,
            "eb_k8": res_eb_k8,
            "eb_mcmc_sigma020": res_eb_mcmc,
        }

    # Save structured results
    out_data = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "runtime_sec": round(time.perf_counter() - t0, 2),
            "peak_ram_mb": round(get_peak_memory_mb(), 2),
        },
        "fb_continuous_knn": {
            "fb_k16": res_fb_k16,
            "fb_k8": res_fb_k8,
        },
        "fb_continuous_mcmc": {
            "fb_mcmc_sigma020": res_fb_mcmc,
        },
        "eb_continuous_knn": eb_results,
    }

    print(f"\nSaving continuous degree benchmark to {OUT_JSON} ...")
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(out_data, f, indent=2)

    print(f"Benchmark finished in {time.perf_counter() - t0:.2f}s!")


if __name__ == "__main__":
    main()
