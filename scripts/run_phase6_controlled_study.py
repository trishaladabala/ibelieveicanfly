#!/usr/bin/env python3
"""
Phase 6: Comprehensive Controlled Central Complex Connectomics Study.

Implements:
1. Transmitter Classification Audit:
   - Synapse-weighted consensus phenotype derivation.
   - Missingness and pure-target census.
   - Confidence score distributions.
   - Connection-level probabilistic mass: P(u->v) * P(v->u).
2. Primary Statistical Analysis (B = 2,000 permutations):
   - Primary Endpoint: EB GABA <-> GABA at w >= 5 under degree-stratified conditional null.
3. Pre-defined Secondary Analyses:
   - FB ACh <-> GABA and PB ACh <-> ACh at w >= 5.
   - Full 21-pair motif inventory across EB, FB, PB with Benjamini-Hochberg FDR correction.
4. Robustness & Sensitivity Checks:
   - Threshold sensitivity: w >= 3 vs w >= 5.
   - High-confidence sensitivity: confidence >= 0.80.
   - Stratification sensitivity: unstratified, tertiles, quartiles, quintiles.
5. Machine-readable JSON output in results/real_data_pilot/phase6/.
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


def partition_into_strata(nodes: list[int], degrees: dict[int, int], n_strata: int) -> list[list[int]]:
    """Partitions nodes into approximately equal-sized strata ordered by degree."""
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


def run_conditional_permutations(
    mutual_dyads: list[tuple[int, int]],
    active_nodes: list[int],
    neuron_nt: dict[int, int],
    strata: list[list[int]],
    num_permutations: int,
    rng: random.Random,
) -> dict[str, Any]:
    """
    Executes degree-stratified label permutations on the fixed reciprocal dyad topology.
    Evaluates all 21 neurotransmitter pairings.
    """
    pair_names = all_pair_names()
    obs_counts: Counter[str] = Counter()
    for u, v in mutual_dyads:
        tu = neuron_nt[u]
        tv = neuron_nt[v]
        p_name = format_pair_name(tu, tv)
        obs_counts[p_name] += 1

    null_distributions: dict[str, list[int]] = {p: [0] * num_permutations for p in pair_names}

    for b in range(num_permutations):
        mapping = {}
        for st in strata:
            lbls = [neuron_nt[n] for n in st]
            rng.shuffle(lbls)
            mapping.update(zip(st, lbls))

        perm_counts: Counter[str] = Counter()
        for u, v in mutual_dyads:
            tu = mapping[u]
            tv = mapping[v]
            p_name = format_pair_name(tu, tv)
            perm_counts[p_name] += 1

        for p in pair_names:
            null_distributions[p][b] = perm_counts[p]

    # Calculate statistics for each pair
    results: dict[str, Any] = {}
    p_vals_raw: list[float] = []
    p_keys: list[str] = []

    for p in pair_names:
        dist = null_distributions[p]
        obs = obs_counts[p]
        mean_val = sum(dist) / num_permutations
        var_val = sum((x - mean_val) ** 2 for x in dist) / (num_permutations - 1) if num_permutations > 1 else 0.0
        std_val = math.sqrt(var_val) if var_val > 0 else 1e-6
        z = (obs - mean_val) / std_val

        # Exact finite-sample two-tailed empirical p-value
        extreme_count = sum(1 for x in dist if abs(x - mean_val) >= abs(obs - mean_val))
        p_val = (extreme_count + 1) / (num_permutations + 1)
        enrichment = (obs / mean_val) if mean_val > 0 else 0.0

        sorted_dist = sorted(dist)
        q025 = sorted_dist[int(0.025 * num_permutations)]
        q250 = sorted_dist[int(0.250 * num_permutations)]
        q500 = sorted_dist[int(0.500 * num_permutations)]
        q750 = sorted_dist[int(0.750 * num_permutations)]
        q975 = sorted_dist[int(0.975 * num_permutations)]

        p_vals_raw.append(p_val)
        p_keys.append(p)

        results[p] = {
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

    # Benjamini-Hochberg FDR
    q_vals = benjamini_hochberg(p_vals_raw)
    for p, q in zip(p_keys, q_vals):
        results[p]["fdr_q_value"] = q
        results[p]["fdr_significant"] = bool(q < 0.05)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 6 Controlled Central Complex Connectomics Study")
    parser.add_argument(
        "--file",
        type=Path,
        default=PROJECT_ROOT / "data" / "raw" / "fafb_v783" / "proofread_connections_783.feather",
        help="Path to proofread connections feather file",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "results" / "real_data_pilot" / "phase6" / "phase6_controlled_study_results.json",
        help="Output JSON path",
    )
    parser.add_argument(
        "--num_perms",
        type=int,
        default=2000,
        help="Number of permutations for primary conditional null",
    )
    args = parser.parse_args()

    t_start = time.perf_counter()
    print("=" * 80)
    print("PHASE 6: CONTROLLED CENTRAL COMPLEX CONNECTOMICS STUDY")
    print(f"Dataset: {args.file}")
    print(f"Permutations: {args.num_perms:,} | Seeds: 42 (primary)")
    print("=" * 80)

    # ---------------------------------------------------------
    # STEP 1: LOAD AND AUDIT TRANSMITTER PREDICTIONS
    # ---------------------------------------------------------
    print("\n[Step 1/5] Ingesting Arrow table and auditing neurotransmitter classifications...")
    neuron_outputs: dict[int, list[float]] = defaultdict(lambda: [0.0] * 6)
    regional_edges: dict[str, dict[tuple[int, int], dict[str, Any]]] = {r: {} for r in TARGET_REGIONS}

    total_records = 0
    records_with_nt = 0
    total_synapses = 0
    synapses_with_nt = 0

    with open(args.file, "rb") as f:
        reader = ipc.RecordBatchFileReader(f)
        for i in range(reader.num_record_batches):
            batch = reader.get_record_batch(i)
            total_records += batch.num_rows

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

            for j in range(batch.num_rows):
                pre = pre_arr[j].as_py()
                post = post_arr[j].as_py()
                syn = syn_arr[j].as_py()
                total_synapses += syn
                if pre == post:
                    continue

                v_ach = ach_arr[j].as_py()
                if v_ach is not None:
                    records_with_nt += 1
                    synapses_with_nt += syn
                    v_gaba = gaba_arr[j].as_py()
                    v_glut = glut_arr[j].as_py()
                    v_da = da_arr[j].as_py()
                    v_oct = oct_arr[j].as_py()
                    v_ser = ser_arr[j].as_py()

                    neuron_outputs[pre][0] += syn * v_ach
                    neuron_outputs[pre][1] += syn * v_gaba
                    neuron_outputs[pre][2] += syn * v_glut
                    neuron_outputs[pre][3] += syn * v_da
                    neuron_outputs[pre][4] += syn * v_oct
                    neuron_outputs[pre][5] += syn * v_ser

                    np_val = np_arr[j].as_py()
                    if np_val in TARGET_REGIONS:
                        pair = (pre, post)
                        if pair not in regional_edges[np_val]:
                            regional_edges[np_val][pair] = {
                                "syn": syn,
                                "ach": v_ach,
                                "gaba": v_gaba,
                                "glut": v_glut,
                                "da": v_da,
                                "oct": v_oct,
                                "ser": v_ser,
                            }
                        else:
                            # Aggregate multiple occurrences in same neuropil
                            e = regional_edges[np_val][pair]
                            old_syn = e["syn"]
                            new_syn = old_syn + syn
                            e["ach"] = (e["ach"] * old_syn + v_ach * syn) / new_syn
                            e["gaba"] = (e["gaba"] * old_syn + v_gaba * syn) / new_syn
                            e["glut"] = (e["glut"] * old_syn + v_glut * syn) / new_syn
                            e["da"] = (e["da"] * old_syn + v_da * syn) / new_syn
                            e["oct"] = (e["oct"] * old_syn + v_oct * syn) / new_syn
                            e["ser"] = (e["ser"] * old_syn + v_ser * syn) / new_syn
                            e["syn"] = new_syn

    # Derive consensus phenotypes and confidence metrics
    neuron_consensus: dict[int, int] = {}
    neuron_confidence: dict[int, float] = {}
    for nid, probs in neuron_outputs.items():
        s = sum(probs)
        if s > 0:
            norm = [p / s for p in probs]
            top_p = max(norm)
            neuron_consensus[nid] = int(norm.index(top_p))
            neuron_confidence[nid] = float(top_p)

    print(f"  Ingestion finished in {time.perf_counter() - t_start:.2f}s")
    print(f"  Total records: {total_records:,} | Records with NT: {records_with_nt:,} (Missing: {total_records - records_with_nt})")
    print(f"  Total synapses: {total_synapses:,} | Synapses with NT: {synapses_with_nt:,} (Missing: {total_synapses - synapses_with_nt})")
    print(f"  Neurons with consensus label: {len(neuron_consensus):,}")

    audit_summary = {
        "total_records": total_records,
        "records_with_nt": records_with_nt,
        "missing_records": total_records - records_with_nt,
        "missing_record_pct": round((total_records - records_with_nt) / total_records * 100.0, 4),
        "total_synapses": total_synapses,
        "synapses_with_nt": synapses_with_nt,
        "missing_synapses": total_synapses - synapses_with_nt,
        "missing_synapse_pct": round((total_synapses - synapses_with_nt) / total_synapses * 100.0, 4),
        "neurons_classified": len(neuron_consensus),
    }

    # ---------------------------------------------------------
    # STEP 2: BUILD REGIONAL RECIPROCAL GRAPHS (w >= 3 and w >= 5)
    # ---------------------------------------------------------
    print("\n[Step 2/5] Building Central Complex graphs and connection-level probabilities...")
    study_data: dict[str, Any] = {}

    for r in TARGET_REGIONS:
        study_data[r] = {}
        for t in [3, 5]:
            reg_dict = regional_edges[r]
            # Filter edges with threshold and classified endpoints
            valid_edges = {
                k: v for k, v in reg_dict.items()
                if v["syn"] >= t and k[0] in neuron_consensus and k[1] in neuron_consensus
            }
            # Active nodes
            active_nodes = sorted(list(set(u for u, v in valid_edges.keys()) | set(v for u, v in valid_edges.keys())))
            # Mutual dyads
            m_dyads = []
            for (u, v) in valid_edges.keys():
                if u < v and (v, u) in valid_edges:
                    m_dyads.append((u, v))

            # Mutual degree sequence
            m_deg = Counter()
            for u, v in m_dyads:
                m_deg[u] += 1
                m_deg[v] += 1

            # Connection-level probabilistic masses
            prob_masses: Counter[str] = Counter()
            for u, v in m_dyads:
                e_uv = valid_edges[(u, v)]
                e_vu = valid_edges[(v, u)]
                for c1_idx, c1_name in enumerate(NT_CLASSES):
                    for c2_idx in range(c1_idx, len(NT_CLASSES)):
                        c2_name = NT_CLASSES[c2_idx]
                        pair_name = f"{c1_name}_{c2_name}"
                        if c1_idx == c2_idx:
                            mass = e_uv[c1_name] * e_vu[c1_name]
                        else:
                            mass = e_uv[c1_name] * e_vu[c2_name] + e_uv[c2_name] * e_vu[c1_name]
                        prob_masses[pair_name] += mass

            # Confidence distribution of active nodes
            confs = [neuron_confidence[n] for n in active_nodes]
            conf_stats = {
                "mean": round(sum(confs) / len(confs), 4) if confs else 0.0,
                "min": round(min(confs), 4) if confs else 0.0,
                "max": round(max(confs), 4) if confs else 0.0,
                "frac_ge_070_pct": round(sum(1 for c in confs if c >= 0.70) / len(confs) * 100.0, 2) if confs else 0.0,
                "frac_ge_080_pct": round(sum(1 for c in confs if c >= 0.80) / len(confs) * 100.0, 2) if confs else 0.0,
                "frac_ge_090_pct": round(sum(1 for c in confs if c >= 0.90) / len(confs) * 100.0, 2) if confs else 0.0,
            }

            study_data[r][f"w{t}"] = {
                "threshold": t,
                "active_nodes": len(active_nodes),
                "directed_edges": len(valid_edges),
                "mutual_dyads": len(m_dyads),
                "reciprocity_edge_pct": round(2 * len(m_dyads) / len(valid_edges) * 100.0, 2) if valid_edges else 0.0,
                "node_list": active_nodes,
                "mutual_dyads_list": m_dyads,
                "mutual_degree_dict": dict(m_deg),
                "confidence_stats": conf_stats,
                "connection_level_prob_masses": {k: round(v, 2) for k, v in prob_masses.items()},
            }
            print(f"  [{r} w >= {t}] Nodes: {len(active_nodes):,} | Edges: {len(valid_edges):,} | Mutual Dyads: {len(m_dyads):,} | Edge Reciprocity: {study_data[r][f'w{t}']['reciprocity_edge_pct']}%")

    # ---------------------------------------------------------
    # STEP 3: EXECUTE PRIMARY AND SECONDARY CONDITIONAL ANALYSES (B = 2,000)
    # ---------------------------------------------------------
    print("\n[Step 3/5] Executing 2,000-permutation degree-stratified conditional null models...")
    rng_perm = random.Random(42)
    statistical_results: dict[str, Any] = {}

    for r in TARGET_REGIONS:
        statistical_results[r] = {}
        for t in [3, 5]:
            d = study_data[r][f"w{t}"]
            nodes = d["node_list"]
            m_dyads = d["mutual_dyads_list"]
            m_deg = d["mutual_degree_dict"]

            # Standard 4 strata (quartiles)
            strata_4 = partition_into_strata(nodes, m_deg, n_strata=4)
            perm_res = run_conditional_permutations(
                mutual_dyads=m_dyads,
                active_nodes=nodes,
                neuron_nt=neuron_consensus,
                strata=strata_4,
                num_permutations=args.num_perms,
                rng=rng_perm,
            )

            statistical_results[r][f"w{t}"] = {
                "threshold": t,
                "active_nodes": len(nodes),
                "directed_edges": d["directed_edges"],
                "mutual_dyads": len(m_dyads),
                "reciprocity_edge_pct": d["reciprocity_edge_pct"],
                "strata_count": 4,
                "strata_sizes": [len(s) for s in strata_4],
                "confidence_stats": d["confidence_stats"],
                "connection_level_prob_masses": d["connection_level_prob_masses"],
                "pair_statistics": perm_res,
            }

            # Print primary and target secondary highlights
            if r == "EB" and t == 5:
                res_gaba = perm_res["gaba_gaba"]
                prob_gaba = d["connection_level_prob_masses"]["gaba_gaba"]
                print(f"\n  *** PRIMARY OUTCOME: EB w >= 5 | GABA <-> GABA ***")
                print(f"    Observed: {res_gaba['observed']} / {len(m_dyads)} ({res_gaba['observed']/len(m_dyads)*100:.2f}%)")
                print(f"    Null Mean (Quartiles): {res_gaba['null_mean']} ± {res_gaba['null_std']}")
                print(f"    Conditional Enrichment: {res_gaba['enrichment_ratio']}x (Z = {res_gaba['z_score']:+.2f}, p = {res_gaba['empirical_p_value']:.6f})")
                print(f"    Connection-Level Prob Mass: {prob_gaba} ({prob_gaba/len(m_dyads)*100:.2f}%)")
            elif r == "FB" and t == 5:
                res_fb = perm_res["ach_gaba"]
                print(f"\n  *** SECONDARY OUTCOME 1: FB w >= 5 | ACh <-> GABA ***")
                print(f"    Observed: {res_fb['observed']} / {len(m_dyads)} ({res_fb['observed']/len(m_dyads)*100:.2f}%)")
                print(f"    Null Mean (Quartiles): {res_fb['null_mean']} ± {res_fb['null_std']}")
                print(f"    Conditional Enrichment: {res_fb['enrichment_ratio']}x (Z = {res_fb['z_score']:+.2f}, p = {res_fb['empirical_p_value']:.6f}, FDR q = {res_fb['fdr_q_value']:.6f})")
            elif r == "PB" and t == 5:
                res_pb = perm_res["ach_ach"]
                print(f"\n  *** SECONDARY OUTCOME 2: PB w >= 5 | ACh <-> ACh ***")
                print(f"    Observed: {res_pb['observed']} / {len(m_dyads)} ({res_pb['observed']/len(m_dyads)*100:.2f}%)")
                print(f"    Null Mean (Quartiles): {res_pb['null_mean']} ± {res_pb['null_std']}")
                print(f"    Conditional Enrichment: {res_pb['enrichment_ratio']}x (Z = {res_pb['z_score']:+.2f}, p = {res_pb['empirical_p_value']:.6f}, FDR q = {res_pb['fdr_q_value']:.6f})")

    # ---------------------------------------------------------
    # STEP 4: TARGETED ROBUSTNESS & SENSITIVITY CHECKS
    # ---------------------------------------------------------
    print("\n[Step 4/5] Running targeted sensitivity checks for EB GABA <-> GABA (w >= 5)...")
    eb_w5 = study_data["EB"]["w5"]
    nodes_eb = eb_w5["node_list"]
    dyads_eb = eb_w5["mutual_dyads_list"]
    deg_eb = eb_w5["mutual_degree_dict"]

    sensitivity_results: dict[str, Any] = {}

    # 4A. Stratification Granularity Sensitivity (Unstratified, 3 Strata, 4 Strata, 5 Strata)
    strat_sensitivity = {}
    for n_st, label in [(1, "unstratified"), (3, "tertiles"), (4, "quartiles"), (5, "quintiles")]:
        st = partition_into_strata(nodes_eb, deg_eb, n_strata=n_st)
        res = run_conditional_permutations(dyads_eb, nodes_eb, neuron_consensus, st, num_permutations=1000, rng=rng_perm)
        strat_sensitivity[label] = {
            "strata_count": n_st,
            "null_mean": res["gaba_gaba"]["null_mean"],
            "null_std": res["gaba_gaba"]["null_std"],
            "enrichment_ratio": res["gaba_gaba"]["enrichment_ratio"],
            "z_score": res["gaba_gaba"]["z_score"],
            "p_value": res["gaba_gaba"]["empirical_p_value"],
        }
        print(f"    Stratification [{label:12s}]: Null Mean = {res['gaba_gaba']['null_mean']:6.1f} | Enrichment = {res['gaba_gaba']['enrichment_ratio']:.2f}x | Z = {res['gaba_gaba']['z_score']:+5.1f}")
    sensitivity_results["stratification_sensitivity"] = strat_sensitivity

    # 4B. High-Confidence Classification Sensitivity (confidence >= 0.80)
    print("  Evaluating high-confidence subset (confidence >= 0.80)...")
    hi_conf_nodes = [n for n in nodes_eb if neuron_confidence[n] >= 0.80]
    hi_conf_node_set = set(hi_conf_nodes)
    hi_conf_dyads = [(u, v) for u, v in dyads_eb if u in hi_conf_node_set and v in hi_conf_node_set]
    hi_deg = Counter()
    for u, v in hi_conf_dyads:
        hi_deg[u] += 1
        hi_deg[v] += 1
    hi_strata = partition_into_strata(hi_conf_nodes, hi_deg, n_strata=4)
    res_hi = run_conditional_permutations(hi_conf_dyads, hi_conf_nodes, neuron_consensus, hi_strata, num_permutations=1000, rng=rng_perm)
    hi_conf_res = {
        "nodes_retained": len(hi_conf_nodes),
        "dyads_retained": len(hi_conf_dyads),
        "observed_gaba_gaba": res_hi["gaba_gaba"]["observed"],
        "observed_pct": round(res_hi["gaba_gaba"]["observed"] / len(hi_conf_dyads) * 100.0, 2) if hi_conf_dyads else 0.0,
        "null_mean": res_hi["gaba_gaba"]["null_mean"],
        "null_std": res_hi["gaba_gaba"]["null_std"],
        "enrichment_ratio": res_hi["gaba_gaba"]["enrichment_ratio"],
        "z_score": res_hi["gaba_gaba"]["z_score"],
        "p_value": res_hi["gaba_gaba"]["empirical_p_value"],
    }
    sensitivity_results["high_confidence_sensitivity"] = hi_conf_res
    print(f"    High-Confidence (>=0.80): Observed = {hi_conf_res['observed_gaba_gaba']}/{hi_conf_res['dyads_retained']} ({hi_conf_res['observed_pct']}%) | Null Mean = {hi_conf_res['null_mean']} | Enrichment = {hi_conf_res['enrichment_ratio']:.2f}x | Z = {hi_conf_res['z_score']:+5.1f}")

    # ---------------------------------------------------------
    # STEP 5: SAVE COMPLETE PUBLICATION-GRADE RESULTS
    # ---------------------------------------------------------
    print("\n[Step 5/5] Compiling and saving final results...")
    final_output = {
        "metadata": {
            "execution_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dataset": str(args.file.name),
            "permutations": args.num_perms,
            "random_seed": 42,
            "runtime_seconds": round(time.perf_counter() - t_start, 2),
            "peak_ram_mb": round(get_peak_memory_mb(), 1),
        },
        "audit_summary": audit_summary,
        "primary_outcome": {
            "region": "EB",
            "threshold": 5,
            "motif": "gaba_gaba",
            "observed_count": statistical_results["EB"]["w5"]["pair_statistics"]["gaba_gaba"]["observed"],
            "total_mutual_dyads": statistical_results["EB"]["w5"]["mutual_dyads"],
            "observed_fraction_pct": round(statistical_results["EB"]["w5"]["pair_statistics"]["gaba_gaba"]["observed"] / statistical_results["EB"]["w5"]["mutual_dyads"] * 100.0, 2),
            "null_mean": statistical_results["EB"]["w5"]["pair_statistics"]["gaba_gaba"]["null_mean"],
            "null_std": statistical_results["EB"]["w5"]["pair_statistics"]["gaba_gaba"]["null_std"],
            "conditional_enrichment_ratio": statistical_results["EB"]["w5"]["pair_statistics"]["gaba_gaba"]["enrichment_ratio"],
            "z_score": statistical_results["EB"]["w5"]["pair_statistics"]["gaba_gaba"]["z_score"],
            "empirical_p_value": statistical_results["EB"]["w5"]["pair_statistics"]["gaba_gaba"]["empirical_p_value"],
            "connection_level_prob_mass": statistical_results["EB"]["w5"]["connection_level_prob_masses"]["gaba_gaba"],
        },
        "regional_statistical_results": statistical_results,
        "sensitivity_checks": sensitivity_results,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(final_output, f, indent=2)

    print("\n" + "=" * 80)
    print(f"Results successfully saved to: {args.out}")
    print(f"Total study runtime: {time.perf_counter() - t_start:.2f}s | Peak RAM: {get_peak_memory_mb():.1f} MB")
    print("=" * 80)


if __name__ == "__main__":
    main()

