#!/usr/bin/env python3
"""
Comprehensive Reciprocal Neurotransmitter Pairing & Circuit Motif Analysis.

Addresses Phase Six & Phase Seven of the Research Protocol:
1. Streams proofread_connections_783.feather (16,847,997 records).
2. Derives presynaptic consensus neurotransmitter assignment for every neuron:
   - T_u = argmax_k sum_j (syn_count_{u,j} * P_{k}(u,j))
   - Confidence metric: C_u = max_k M_{u,k} / sum_k M_{u,k}
   - Whole-brain neuron census by predicted transmitter type.
3. Classifies mutual reciprocal dyads (u <-> v) into pairing motifs:
   - Homotypic: (ach, ach), (gaba, gaba), (glut, glut)
   - Feedback / Heterotypic: (ach, gaba), (ach, glut), (gaba, glut)
   - Modulatory pairings involving da, oct, ser
4. Evaluates pairing across thresholds w >= 1, 3, 5, 10.
5. Implements two rigorous null models:
   - Null Model 1: Analytical Marginal Expectation (multinomial dyad product).
   - Null Model 2: Empirical Degree- & Dyad-Preserving Permutation Null (B = 500 shuffles).
     Preserves exact network topology and node degrees, yielding empirical z-scores and p-values.
6. Evaluates regional motifs:
   - Deep dive into the Ellipsoid Body (EB, Rank #1 reciprocity) to test ring attractor hypotheses.
   - Comparative analysis across EB, FB, AL, MB, and whole brain.
7. Saves full results to results/real_data_pilot/verified_reciprocal_transmitters.json.
"""

from __future__ import annotations

import argparse
import array
import json
import math
import random
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

NT_CLASSES = ["ach", "gaba", "glut", "da", "oct", "ser"]
NT_INDEX = {name: i for i, name in enumerate(NT_CLASSES)}


def get_peak_memory_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def format_pair_name(c1: int, c2: int) -> str:
    if c1 > c2:
        c1, c2 = c2, c1
    return f"{NT_CLASSES[c1]}_{NT_CLASSES[c2]}"


def run_reciprocal_transmitter_analysis(
    file_path: Path,
    output_json: Path | None = None,
    num_permutations: int = 500,
    random_seed: int = 42,
) -> dict[str, Any]:
    start_time = time.perf_counter()
    random.seed(random_seed)

    if output_json is None:
        output_json = PROJECT_ROOT / "results" / "real_data_pilot" / "verified_reciprocal_transmitters.json"
    output_json.parent.mkdir(parents=True, exist_ok=True)

    print("================================================================================")
    print("PHASE SIX & SEVEN: RECIPROCAL NEUROTRANSMITTER PAIRING & CIRCUIT MOTIFS")
    print(f"Dataset:      {file_path.name}")
    print(f"Permutations: {num_permutations} (seed={random_seed})")
    print("================================================================================\n")

    # Node mapping
    node_to_id: dict[int, int] = {}
    id_to_node: list[int] = []

    def get_or_create_node(root_id: int) -> int:
        if root_id not in node_to_id:
            idx = len(id_to_node)
            node_to_id[root_id] = idx
            id_to_node.append(root_id)
            return idx
        return node_to_id[root_id]

    # Pre-synaptic transmitter mass: node_id -> [float * 6]
    pre_nt_mass: dict[int, list[float]] = defaultdict(lambda: [0.0] * 6)
    pre_total_synapses: Counter[int] = Counter()

    # Whole-brain edges: 64-bit key (u << 32) | v -> total syn_count
    edge_weights: dict[int, int] = {}

    # Neuropil-specific edges: npil -> dict[64-bit key, syn_count]
    # We track key regions of biological interest: EB, FB, AL_L, AL_R, MB_PED_L
    TARGET_NEUROPILS = {"EB", "FB", "AL_L", "AL_R", "MB_PED_L"}
    neuropil_edges: dict[str, dict[int, int]] = {npil: {} for npil in TARGET_NEUROPILS}

    print(">>> Step 1: Streaming dataset, accumulating presynaptic NT mass & graph edges...")
    total_records = 0
    with open(file_path, "rb") as f:
        reader = ipc.open_file(f)
        num_batches = reader.num_record_batches

        col_pre = "pre_pt_root_id"
        col_post = "post_pt_root_id"
        col_weight = "syn_count"
        col_npil = "neuropil"
        prob_cols = [f"{nt}_avg" for nt in NT_CLASSES]

        for b_idx in range(num_batches):
            batch = reader.get_batch(b_idx)
            pres = batch.column(col_pre).to_pylist()
            posts = batch.column(col_post).to_pylist()
            weights = batch.column(col_weight).to_pylist()
            npils = batch.column(col_npil).to_pylist() if col_npil in batch.schema.names else [None] * len(pres)

            # Extract probability arrays
            p_arrays = [batch.column(col).to_pylist() for col in prob_cols]

            for i in range(len(pres)):
                p = pres[i]
                q = posts[i]
                w = weights[i]
                if p is None or q is None or w is None or w <= 0:
                    continue

                total_records += 1
                u = get_or_create_node(p)
                v = get_or_create_node(q)

                # Accumulate presynaptic neurotransmitter mass
                probs = [p_arrays[c][i] for c in range(6)]
                if all(val is not None for val in probs):
                    mass = pre_nt_mass[u]
                    for c in range(6):
                        mass[c] += w * probs[c]
                    pre_total_synapses[u] += w

                # Whole-brain edge key
                edge_key = (u << 32) | v
                edge_weights[edge_key] = edge_weights.get(edge_key, 0) + w

                # Regional edge key
                npil = npils[i]
                if npil in neuropil_edges:
                    r_edges = neuropil_edges[npil]
                    r_edges[edge_key] = r_edges.get(edge_key, 0) + w

            if (b_idx + 1) % 50 == 0 or (b_idx + 1) == num_batches:
                elapsed = time.perf_counter() - start_time
                ram = get_peak_memory_mb()
                print(f"    Batches: {b_idx + 1:3d}/{num_batches} ({total_records:10,d} rows) | Time: {elapsed:5.1f}s | RAM: {ram:6.1f} MB")

    ingest_time = time.perf_counter() - start_time
    total_nodes = len(id_to_node)
    print(f"\nIngestion complete in {ingest_time:.2f}s.")
    print(f"  Total unique neurons (|V|): {total_nodes:,}")
    print(f"  Total unique directed edges: {len(edge_weights):,}")
    print(f"  Neurons with presynaptic NT predictions: {len(pre_nt_mass):,}\n")

    print(">>> Step 2: Deriving consensus neurotransmitter assignment per neuron...")
    # neuron_nt: array of uint8 class indices (0..5), 255 for unassigned
    # neuron_conf: array of float confidence
    neuron_nt = array.array("B", [255] * total_nodes)
    neuron_conf = array.array("f", [0.0] * total_nodes)

    nt_census = Counter()
    conf_bins = Counter()  # [0.5-0.7), [0.7-0.9), [0.9-1.0]

    for u, mass in pre_nt_mass.items():
        total_m = sum(mass)
        if total_m > 0:
            best_c = 0
            best_m = mass[0]
            for c in range(1, 6):
                if mass[c] > best_m:
                    best_m = mass[c]
                    best_c = c
            conf = best_m / total_m
            neuron_nt[u] = best_c
            neuron_conf[u] = conf

            nt_name = NT_CLASSES[best_c]
            nt_census[nt_name] += 1

            if conf >= 0.9:
                conf_bins[">= 0.90"] += 1
            elif conf >= 0.7:
                conf_bins["0.70 - 0.89"] += 1
            elif conf >= 0.5:
                conf_bins["0.50 - 0.69"] += 1
            else:
                conf_bins["< 0.50 (low confidence)"] += 1

    print("--- NEURON PHENOTYPE CENSUS (Consensus Neurotransmitter) ---")
    assigned_neurons = sum(nt_census.values())
    for nt_name in NT_CLASSES:
        cnt = nt_census[nt_name]
        pct = (cnt / assigned_neurons * 100.0) if assigned_neurons > 0 else 0.0
        print(f"  {nt_name.upper():4s}: {cnt:6,d} neurons ({pct:5.2f}%)")
    print(f"  Total assigned: {assigned_neurons:,} / {total_nodes:,} ({assigned_neurons / total_nodes * 100.0:.2f}%)\n")

    print("--- PREDICTION CONFIDENCE DISTRIBUTION ---")
    for b_label, b_cnt in conf_bins.most_common():
        b_pct = b_cnt / assigned_neurons * 100.0
        print(f"  {b_label:25s}: {b_cnt:6,d} ({b_pct:5.2f}%)")
    print()

    # Function to evaluate reciprocal transmitter motifs on an edge dictionary
    def evaluate_dyad_motifs(
        edges: dict[int, int],
        threshold: int,
        label: str,
        run_permutations: bool = True,
    ) -> dict[str, Any]:
        # Extract mutual dyads (u < v) without allocating a duplicate dictionary
        u_dyads = array.array("I")
        v_dyads = array.array("I")

        for k, w in edges.items():
            if w < threshold:
                continue
            u = k >> 32
            v = k & 0xFFFFFFFF
            if u < v:
                rev_k = (v << 32) | u
                if edges.get(rev_k, 0) >= threshold:
                    # Both neurons must have valid assigned NT
                    nt_u = neuron_nt[u]
                    nt_v = neuron_nt[v]
                    if nt_u < 6 and nt_v < 6:
                        u_dyads.append(u)
                        v_dyads.append(v)

        M = len(u_dyads)
        if M == 0:
            return {"dyad_count": 0, "status": "no_dyads"}

        # Active neurons in reciprocal dyads
        participating_nodes = set(u_dyads) | set(v_dyads)
        N_recip = len(participating_nodes)

        # Marginal transmitter distribution among participating neurons
        recip_nt_counts = Counter(neuron_nt[n] for n in participating_nodes)
        p_marginal = {c: recip_nt_counts[c] / N_recip for c in range(6)}

        # Observed dyad counts
        obs_pairs: Counter[str] = Counter()
        for i in range(M):
            p_name = format_pair_name(neuron_nt[u_dyads[i]], neuron_nt[v_dyads[i]])
            obs_pairs[p_name] += 1

        # All 21 unordered pair names
        pair_types = []
        for c1 in range(6):
            for c2 in range(c1, 6):
                pair_types.append(format_pair_name(c1, c2))

        # 1. Null Model 1: Analytical Marginal Expectation
        analytic_results = {}
        chi2_total = 0.0

        for p_name in pair_types:
            c1_name, c2_name = p_name.split("_")
            c1 = NT_INDEX[c1_name]
            c2 = NT_INDEX[c2_name]
            p1 = p_marginal[c1]
            p2 = p_marginal[c2]

            p_expected = (p1 * p1) if c1 == c2 else (2.0 * p1 * p2)
            exp_count = M * p_expected
            obs_count = obs_pairs.get(p_name, 0)
            ratio = (obs_count / exp_count) if exp_count > 0 else 0.0
            std_residual = ((obs_count - exp_count) / math.sqrt(exp_count)) if exp_count > 0 else 0.0
            chi2_contrib = ((obs_count - exp_count) ** 2 / exp_count) if exp_count > 0 else 0.0
            chi2_total += chi2_contrib

            analytic_results[p_name] = {
                "observed": obs_count,
                "expected": round(exp_count, 1),
                "obs_pct": round(obs_count / M * 100.0, 3),
                "exp_pct": round(p_expected * 100.0, 3),
                "enrichment_ratio": round(ratio, 3),
                "std_residual": round(std_residual, 2),
                "classification": "Enriched" if ratio > 1.15 else ("Depleted" if ratio < 0.85 else "Near Expected"),
            }

        # 2. Null Model 2: Degree-Preserving Permutation Null Model
        perm_results = {}
        if run_permutations and num_permutations > 0:
            part_node_list = list(participating_nodes)
            perm_counts: dict[str, list[int]] = {p_name: [0] * num_permutations for p_name in pair_types}

            # Pre-compute integer lookup matrix for (c1, c2) -> pair_index (0..20)
            pair_lookup = [[0] * 6 for _ in range(6)]
            for p_idx, p_name in enumerate(pair_types):
                c1_name, c2_name = p_name.split("_")
                c1_idx = NT_INDEX[c1_name]
                c2_idx = NT_INDEX[c2_name]
                pair_lookup[c1_idx][c2_idx] = p_idx
                pair_lookup[c2_idx][c1_idx] = p_idx

            # Pre-allocate array for fast permutation indexing
            shuffled_nt = array.array("B", neuron_nt)
            orig_labels = [neuron_nt[n] for n in part_node_list]

            for b in range(num_permutations):
                # Shuffle labels among participating nodes
                permuted_labels = list(orig_labels)
                random.shuffle(permuted_labels)
                for idx, n in enumerate(part_node_list):
                    shuffled_nt[n] = permuted_labels[idx]

                # Fast integer-indexed count under permutation
                counts = [0] * 21
                for i in range(M):
                    counts[pair_lookup[shuffled_nt[u_dyads[i]]][shuffled_nt[v_dyads[i]]]] += 1

                for p_idx, p_name in enumerate(pair_types):
                    perm_counts[p_name][b] = counts[p_idx]

                if (b + 1) % 50 == 0 or (b + 1) == num_permutations:
                    print(f"      [{label}] Permutation {b + 1:3d}/{num_permutations} complete...")

            for p_name in pair_types:
                b_dist = perm_counts[p_name]
                mean_null = sum(b_dist) / num_permutations
                var_null = sum((x - mean_null) ** 2 for x in b_dist) / num_permutations
                std_null = math.sqrt(var_null) if var_null > 0 else 1e-6
                obs = obs_pairs.get(p_name, 0)
                z_score = (obs - mean_null) / std_null

                # Empirical 2-tailed p-value
                extreme_count = sum(1 for x in b_dist if abs(x - mean_null) >= abs(obs - mean_null))
                emp_p = (extreme_count + 1) / (num_permutations + 1)

                perm_results[p_name] = {
                    "mean_null": round(mean_null, 1),
                    "std_null": round(std_null, 2),
                    "z_score": round(z_score, 2),
                    "empirical_p_value": emp_p,
                    "significance": "*** (p < 0.001)" if emp_p < 0.001 else ("** (p < 0.01)" if emp_p < 0.01 else ("* (p < 0.05)" if emp_p < 0.05 else "n.s.")),
                }

        # Higher-level biological circuit categories
        def sum_pairs(pairs_list: list[str]) -> dict[str, Any]:
            obs_s = sum(obs_pairs.get(p, 0) for p in pairs_list)
            exp_s = sum(analytic_results[p]["expected"] for p in pairs_list)
            r_s = (obs_s / exp_s) if exp_s > 0 else 0.0
            return {
                "observed": obs_s,
                "expected": round(exp_s, 1),
                "obs_pct": round(obs_s / M * 100.0, 2),
                "exp_pct": round(exp_s / M * 100.0, 2),
                "enrichment_ratio": round(r_s, 3),
            }

        macro_categories = {
            "recurrent_excitation_ach_ach": sum_pairs(["ach_ach"]),
            "recurrent_inhibition_gaba_gaba": sum_pairs(["gaba_gaba"]),
            "recurrent_glutamatergic_glut_glut": sum_pairs(["glut_glut"]),
            "feedback_inhibition_ach_gaba": sum_pairs(["ach_gaba"]),
            "feedback_glutamatergic_ach_glut": sum_pairs(["ach_glut"]),
            "co_inhibition_gaba_glut": sum_pairs(["gaba_glut"]),
            "all_homotypic_fast": sum_pairs(["ach_ach", "gaba_gaba", "glut_glut"]),
            "all_heterotypic_fast": sum_pairs(["ach_gaba", "ach_glut", "gaba_glut"]),
        }

        return {
            "label": label,
            "threshold": threshold,
            "total_reciprocal_dyads": M,
            "participating_neurons": N_recip,
            "marginal_transmitter_pct": {NT_CLASSES[c]: round(p_marginal[c] * 100.0, 2) for c in range(6)},
            "chi2_total": round(chi2_total, 1),
            "macro_categories": macro_categories,
            "pair_motifs_analytic": analytic_results,
            "pair_motifs_permutation": perm_results,
        }

    print(">>> Step 3: Evaluating Multi-Threshold Reciprocal Dyads on Whole Brain...")
    whole_brain_thresholds = [1, 3, 5, 10]
    whole_brain_results = {}
    for t in whole_brain_thresholds:
        t0 = time.perf_counter()
        # Run permutations for w >= 1 and w >= 5
        do_perm = (t in [1, 5])
        res = evaluate_dyad_motifs(edge_weights, threshold=t, label=f"Whole Brain (w >= {t})", run_permutations=do_perm)
        whole_brain_results[f"w{t}"] = res
        print(f"  Whole Brain w >= {t:2d}: {res['total_reciprocal_dyads']:10,d} mutual dyads evaluated ({time.perf_counter() - t0:.2f}s)")

    print("\n>>> Step 4: Regional Analysis of Reciprocal Motifs (EB, FB, AL_L, MB_PED_L)...")
    regional_results = {}
    for npil in TARGET_NEUROPILS:
        r_edges = neuropil_edges[npil]
        # Evaluate at w >= 1 and w >= 3
        res_w1 = evaluate_dyad_motifs(r_edges, threshold=1, label=f"{npil} (w >= 1)", run_permutations=True)
        res_w3 = evaluate_dyad_motifs(r_edges, threshold=3, label=f"{npil} (w >= 3)", run_permutations=True)
        regional_results[npil] = {"w1": res_w1, "w3": res_w3}
        print(f"  Region {npil:10s} (w>=1): {res_w1['total_reciprocal_dyads']:6,d} dyads | (w>=3): {res_w3['total_reciprocal_dyads']:6,d} dyads")

    total_runtime = time.perf_counter() - start_time
    peak_ram = get_peak_memory_mb()

    # Save complete JSON artifact
    final_artifact = {
        "metadata": {
            "execution_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dataset": file_path.name,
            "runtime_seconds": round(total_runtime, 2),
            "peak_ram_mb": round(peak_ram, 1),
            "permutations": num_permutations,
        },
        "neuron_phenotype_census": {
            "assigned_neurons": assigned_neurons,
            "total_neurons": total_nodes,
            "per_class_counts": dict(nt_census),
            "confidence_distribution": dict(conf_bins),
        },
        "whole_brain_threshold_sensitivity": whole_brain_results,
        "regional_motif_analysis": regional_results,
    }

    with output_json.open("w", encoding="utf-8") as f:
        json.dump(final_artifact, f, indent=2)

    print(f"\nAnalysis complete in {total_runtime:.2f}s (Peak RAM: {peak_ram:.1f} MB).")
    print(f"Results saved to: {output_json}\n")

    # Print Key Publication Tables
    print("==================================================================================================")
    print("WHOLE-BRAIN RECIPROCAL NEUROTRANSMITTER MOTIFS (w >= 5, Lin et al. benchmark)")
    print(f"Total Mutual Dyads: {whole_brain_results['w5']['total_reciprocal_dyads']:,}")
    print("==================================================================================================")
    w5_analytic = whole_brain_results["w5"]["pair_motifs_analytic"]
    w5_perm = whole_brain_results["w5"]["pair_motifs_permutation"]
    print(f"{'Motif':12s} | {'Observed':9s} | {'Expected':9s} | {'Obs %':7s} | {'Exp %':7s} | {'Enrich Ratio':12s} | {'Z-Score (Perm)':14s} | {'Significance'}")
    print("-" * 98)

    # Display major fast neurotransmitter pairings
    key_motifs = ["ach_ach", "gaba_gaba", "glut_glut", "ach_gaba", "ach_glut", "gaba_glut"]
    for m in key_motifs:
        a_data = w5_analytic[m]
        p_data = w5_perm.get(m, {})
        z_str = f"{p_data.get('z_score', 0.0):+8.2f}" if p_data else "N/A"
        sig_str = p_data.get("significance", "N/A") if p_data else "N/A"
        exp_int = int(round(a_data['expected']))
        print(f"{m:12s} | {a_data['observed']:9,d} | {exp_int:9,d} | {a_data['obs_pct']:6.2f}% | {a_data['exp_pct']:6.2f}% | {a_data['enrichment_ratio']:11.3f}x | {z_str:14s} | {sig_str}")
    print("==================================================================================================\n")

    # Print Ellipsoid Body (EB) Table
    print("==================================================================================================")
    print("ELLIPSOID BODY (EB) RECIPROCAL MOTIFS (w >= 1, Ring Attractor Feedback Circuits)")
    print(f"Total Mutual Dyads: {regional_results['EB']['w1']['total_reciprocal_dyads']:,}")
    print("==================================================================================================")
    eb_analytic = regional_results["EB"]["w1"]["pair_motifs_analytic"]
    eb_perm = regional_results["EB"]["w1"]["pair_motifs_permutation"]
    print(f"{'Motif':12s} | {'Observed':9s} | {'Expected':9s} | {'Obs %':7s} | {'Exp %':7s} | {'Enrich Ratio':12s} | {'Z-Score (Perm)':14s} | {'Significance'}")
    print("-" * 98)
    for m in key_motifs:
        a_data = eb_analytic[m]
        p_data = eb_perm.get(m, {})
        z_str = f"{p_data.get('z_score', 0.0):+8.2f}" if p_data else "N/A"
        sig_str = p_data.get("significance", "N/A") if p_data else "N/A"
        exp_int = int(round(a_data['expected']))
        print(f"{m:12s} | {a_data['observed']:9,d} | {exp_int:9,d} | {a_data['obs_pct']:6.2f}% | {a_data['exp_pct']:6.2f}% | {a_data['enrichment_ratio']:11.3f}x | {z_str:14s} | {sig_str}")
    print("==================================================================================================\n")

    return final_artifact


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze reciprocal neurotransmitter pairing and circuit motifs.")
    parser.add_argument("--file", type=Path, default=PROJECT_ROOT / "data" / "raw" / "fafb_v783" / "proofread_connections_783.feather")
    parser.add_argument("--permutations", type=int, default=500, help="Number of permutations for degree-preserving null model.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    args = parser.parse_args()

    run_reciprocal_transmitter_analysis(args.file, num_permutations=args.permutations, random_seed=args.seed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
