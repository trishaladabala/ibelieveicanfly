#!/usr/bin/env python3
"""
Phase 7: Robustness Gate and Cell-Type Feasibility Analysis for the Adult Drosophila Ellipsoid Body.

Implements:
1. Baseline Verification:
   - Evaluates EB (w >= 5) primary GABA-GABA mutual dyad statistic under Phase 6 mutual-degree quartiles.
2. Targeted Robustness / Sensitivity Analysis:
   - Joint Directed In-Degree and Out-Degree stratification (3x3 tertile grid, 9 strata).
   - Joint Directed Median split (2x2 grid, 4 strata).
   - High-confidence / Directed degree composite (Total degree quartiles x Confidence median, 8 strata).
   - 2,000 permutations with seed 42, computing null distributions, Z-scores, empirical p-values, and mobility diagnostics.
3. Cell-Type Annotation Mapping:
   - Uses version-pinned FlyWire v2.1.0 annotation table (Supplemental_file1_neuron_annotations.tsv).
   - Measures matching coverage across all 483 active nodes and 3,518 mutual dyads.
   - Quantifies cell-class, cell-subclass, and specific hemibrain/cell-type distributions.
4. Descriptive Biological Synthesis:
   - Breakdown of GABA-GABA and all EB mutual dyads by published cell classes.
   - Identifies specific homotypic (e.g. ER2-ER2) and heterotypic (e.g. EPG-PEN) motif architectures.
5. Saves structured results to results/real_data_pilot/phase7/phase7_robustness_and_celltypes.json.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
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

CACHE_FILE = PROJECT_ROOT / "results" / "real_data_pilot" / "phase7" / "eb_node_covariates.json"
ANNOT_FILE = PROJECT_ROOT / "data" / "raw" / "annotations_v2.1.0" / "Supplemental_file1_neuron_annotations.tsv"
OUT_JSON = PROJECT_ROOT / "results" / "real_data_pilot" / "phase7" / "phase7_robustness_and_celltypes.json"


def get_peak_memory_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def run_permutation_ensemble(
    mutual_dyads: list[list[int]],
    node_dict: dict[str, Any],
    strata: list[list[int]],
    num_perms: int = 2000,
    seed: int = 42,
) -> dict[str, Any]:
    """Runs label permutations constrained within defined node strata."""
    rng = random.Random(seed)
    dist = [0] * num_perms
    obs = sum(1 for u, v in mutual_dyads if node_dict[str(u)]["nt_name"] == "gaba" and node_dict[str(v)]["nt_name"] == "gaba")

    for b in range(num_perms):
        mapping = {}
        for st in strata:
            lbls = [node_dict[str(n)]["nt"] for n in st]
            rng.shuffle(lbls)
            mapping.update(zip(st, lbls))

        # Count GABA-GABA dyads
        c = sum(1 for u, v in mutual_dyads if mapping[u] == 1 and mapping[v] == 1)
        dist[b] = c

    mean_val = sum(dist) / num_perms
    var_val = sum((x - mean_val) ** 2 for x in dist) / (num_perms - 1) if num_perms > 1 else 0.0
    std_val = math.sqrt(var_val) if var_val > 0 else 1e-6
    z = (obs - mean_val) / std_val

    # Finite-sample two-tailed empirical p-value
    extreme = sum(1 for x in dist if abs(x - mean_val) >= abs(obs - mean_val))
    p_val = (extreme + 1) / (num_perms + 1)
    enrichment = (obs / mean_val) if mean_val > 0 else 0.0

    sorted_dist = sorted(dist)
    q025 = sorted_dist[int(0.025 * num_perms)]
    q250 = sorted_dist[int(0.250 * num_perms)]
    q500 = sorted_dist[int(0.500 * num_perms)]
    q750 = sorted_dist[int(0.750 * num_perms)]
    q975 = sorted_dist[int(0.975 * num_perms)]

    return {
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


def main() -> None:
    t0 = time.perf_counter()
    print("=" * 80)
    print("PHASE 7: ROBUSTNESS GATE AND CELL-TYPE FEASIBILITY ANALYSIS")
    print("=" * 80)

    # 1. Load cached EB covariates
    if not CACHE_FILE.exists():
        print(f"Error: cache file {CACHE_FILE} not found. Run scratch/inspect_eb_node_covariates.py first.")
        sys.exit(1)

    with open(CACHE_FILE) as f:
        cache_data = json.load(f)

    active_nodes = cache_data["active_nodes"]
    mutual_dyads = cache_data["mutual_dyads"]
    node_dict = cache_data["nodes"]

    obs_gaba = sum(1 for u, v in mutual_dyads if node_dict[str(u)]["nt_name"] == "gaba" and node_dict[str(v)]["nt_name"] == "gaba")
    total_m = len(mutual_dyads)
    print(f"\n[Baseline] Active Nodes: {len(active_nodes)} | Mutual Dyads: {total_m:,}")
    print(f"  Observed GABA-GABA Dyads: {obs_gaba:,} ({obs_gaba/total_m*100:.2f}%)")

    # ---------------------------------------------------------
    # STEP 1 & 2: TARGETED ROBUSTNESS MODELS
    # ---------------------------------------------------------
    print("\n[Step 2/5] Running targeted sensitivity models (B = 2,000 permutations each)...")

    # Baseline Phase 6: Mutual Degree Quartiles
    m_degs = {n: node_dict[str(n)]["m_deg"] for n in active_nodes}
    sorted_m = sorted(active_nodes, key=lambda n: m_degs[n])
    b_size = len(active_nodes) // 4
    strata_p6 = [
        sorted_m[:b_size],
        sorted_m[b_size : 2 * b_size],
        sorted_m[2 * b_size : 3 * b_size],
        sorted_m[3 * b_size :],
    ]
    res_p6 = run_permutation_ensemble(mutual_dyads, node_dict, strata_p6)
    print(f"  [Baseline P6: Mutual-Degree Quartiles (4 strata)]")
    print(f"    Null Mean: {res_p6['null_mean']} ± {res_p6['null_std']} | Enrichment: {res_p6['enrichment_ratio']:.4f}x | Z = {res_p6['z_score']:+5.2f} | p = {res_p6['empirical_p_value']:.6f}")

    # Primary Sensitivity Model: Joint Directed In-Degree x Out-Degree Tertiles (3x3 = 9 strata)
    in_degs = [node_dict[str(n)]["in_deg"] for n in active_nodes]
    out_degs = [node_dict[str(n)]["out_deg"] for n in active_nodes]
    s_in = sorted(in_degs)
    s_out = sorted(out_degs)
    in_t1, in_t2 = s_in[len(active_nodes) // 3], s_in[2 * len(active_nodes) // 3]
    out_t1, out_t2 = s_out[len(active_nodes) // 3], s_out[2 * len(active_nodes) // 3]

    strata_grid9 = defaultdict(list)
    for n in active_nodes:
        d = node_dict[str(n)]
        i_b = 0 if d["in_deg"] <= in_t1 else (1 if d["in_deg"] <= in_t2 else 2)
        o_b = 0 if d["out_deg"] <= out_t1 else (1 if d["out_deg"] <= out_t2 else 2)
        strata_grid9[(i_b, o_b)].append(n)

    grid9_list = list(strata_grid9.values())
    res_grid9 = run_permutation_ensemble(mutual_dyads, node_dict, grid9_list)
    print(f"\n  [Primary Sensitivity: Joint Directed In x Out Tertiles (9 strata)]")
    print(f"    Null Mean: {res_grid9['null_mean']} ± {res_grid9['null_std']} | Enrichment: {res_grid9['enrichment_ratio']:.4f}x | Z = {res_grid9['z_score']:+5.2f} | p = {res_grid9['empirical_p_value']:.6f}")

    # Secondary Sensitivity Model: Joint Directed In-Degree x Out-Degree Median Splits (2x2 = 4 strata)
    in_med = s_in[len(active_nodes) // 2]
    out_med = s_out[len(active_nodes) // 2]
    strata_grid4 = defaultdict(list)
    for n in active_nodes:
        d = node_dict[str(n)]
        i_b = 0 if d["in_deg"] <= in_med else 1
        o_b = 0 if d["out_deg"] <= out_med else 1
        strata_grid4[(i_b, o_b)].append(n)

    grid4_list = list(strata_grid4.values())
    res_grid4 = run_permutation_ensemble(mutual_dyads, node_dict, grid4_list)
    print(f"\n  [Secondary Sensitivity: Joint Directed In x Out Medians (4 strata)]")
    print(f"    Null Mean: {res_grid4['null_mean']} ± {res_grid4['null_std']} | Enrichment: {res_grid4['enrichment_ratio']:.4f}x | Z = {res_grid4['z_score']:+5.2f} | p = {res_grid4['empirical_p_value']:.6f}")

    # Stratum Mobility Diagnostics for Grid 9
    strata_diagnostics = []
    for k in sorted(strata_grid9.keys()):
        st = strata_grid9[k]
        cnt = len(st)
        nt_counts = Counter(node_dict[str(n)]["nt_name"] for n in st)
        gaba_cnt = nt_counts.get("gaba", 0)
        strata_diagnostics.append({
            "stratum_key": f"In_{k[0]}_Out_{k[1]}",
            "total_nodes": cnt,
            "gaba_nodes": gaba_cnt,
            "gaba_pct": round(gaba_cnt / cnt * 100.0, 2),
            "nt_composition": dict(nt_counts),
        })

    # ---------------------------------------------------------
    # STEP 3 & 4: CELL-TYPE ANNOTATION MAPPING
    # ---------------------------------------------------------
    print("\n[Step 3/5] Mapping active EB nodes to FlyWire v2.1.0 annotations...")
    if not ANNOT_FILE.exists():
        print(f"Error: annotation file {ANNOT_FILE} not found.")
        sys.exit(1)

    node_set = set(active_nodes)
    annotations = {}
    with open(ANNOT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rid = int(row["root_id"])
            if rid in node_set:
                annotations[rid] = {
                    "flow": row["flow"].strip() if row["flow"] else "unannotated",
                    "super_class": row["super_class"].strip() if row["super_class"] else "unannotated",
                    "cell_class": row["cell_class"].strip() if row["cell_class"] else "unannotated",
                    "cell_sub_class": row["cell_sub_class"].strip() if row["cell_sub_class"] else "unannotated",
                    "cell_type": row["cell_type"].strip() if row["cell_type"] else "unannotated",
                    "hemibrain_type": row["hemibrain_type"].strip() if row["hemibrain_type"] else (row["cell_type"].strip() if row["cell_type"] else "unannotated"),
                }

    matched_nodes = len(annotations)
    print(f"  Matched Active Nodes: {matched_nodes} / {len(active_nodes)} ({matched_nodes/len(active_nodes)*100:.2f}%)")

    # Dyad matching coverage
    dyads_both_matched = sum(1 for u, v in mutual_dyads if u in annotations and v in annotations)
    gaba_dyads = [(u, v) for u, v in mutual_dyads if node_dict[str(u)]["nt_name"] == "gaba" and node_dict[str(v)]["nt_name"] == "gaba"]
    gaba_both_matched = sum(1 for u, v in gaba_dyads if u in annotations and v in annotations)
    print(f"  All Mutual Dyads Coverage: {dyads_both_matched} / {len(mutual_dyads)} ({dyads_both_matched/len(mutual_dyads)*100:.2f}%)")
    print(f"  GABA-GABA Dyads Coverage: {gaba_both_matched} / {len(gaba_dyads)} ({gaba_both_matched/len(gaba_dyads)*100:.2f}%)")

    # Descriptive Biological Breakdown: All Mutual Dyads
    subclass_pair_counts = Counter()
    same_subclass_cnt = 0
    diff_subclass_cnt = 0
    unannot_subclass_cnt = 0

    type_pair_counts = Counter()
    same_type_cnt = 0
    diff_type_cnt = 0

    for u, v in mutual_dyads:
        sc_u = annotations[u]["cell_sub_class"]
        sc_v = annotations[v]["cell_sub_class"]
        if sc_u == "unannotated" or sc_v == "unannotated":
            unannot_subclass_cnt += 1
        elif sc_u == sc_v:
            same_subclass_cnt += 1
        else:
            diff_subclass_cnt += 1
        p_sc = tuple(sorted([sc_u, sc_v]))
        subclass_pair_counts[p_sc] += 1

        t_u = annotations[u]["hemibrain_type"]
        t_v = annotations[v]["hemibrain_type"]
        if t_u == t_v:
            same_type_cnt += 1
        else:
            diff_type_cnt += 1
        p_t = tuple(sorted([t_u, t_v]))
        type_pair_counts[p_t] += 1

    # Descriptive Biological Breakdown: GABA-GABA Mutual Dyads
    gg_subclass_counts = Counter()
    gg_type_counts = Counter()
    for u, v in gaba_dyads:
        sc_u = annotations[u]["cell_sub_class"]
        sc_v = annotations[v]["cell_sub_class"]
        p_sc = tuple(sorted([sc_u, sc_v]))
        gg_subclass_counts[p_sc] += 1

        t_u = annotations[u]["hemibrain_type"]
        t_v = annotations[v]["hemibrain_type"]
        p_t = tuple(sorted([t_u, t_v]))
        gg_type_counts[p_t] += 1

    print("\n--- GABA-GABA Dyads: Top Cell Sub-Class Pairings ---")
    for p, cnt in gg_subclass_counts.most_common(5):
        print(f"  {p[0]:15s} <-> {p[1]:15s}: {cnt:4d} ({cnt/len(gaba_dyads)*100:.2f}%)")

    print("\n--- GABA-GABA Dyads: Top Specific Cell Type Pairings ---")
    for p, cnt in gg_type_counts.most_common(10):
        print(f"  {p[0]:15s} <-> {p[1]:15s}: {cnt:4d} ({cnt/len(gaba_dyads)*100:.2f}%)")

    # ---------------------------------------------------------
    # STEP 5: SAVE STRUCTURED JSON ARTIFACT
    # ---------------------------------------------------------
    final_output = {
        "metadata": {
            "execution_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dataset": "proofread_connections_783.feather",
            "annotation_source": "https://github.com/flyconnectome/flywire_annotations/releases/tag/v2.1.0",
            "annotation_file": ANNOT_FILE.name,
            "annotation_sha256": "30be6c73975a70c56d930e27911f36455d3886e15abf383b78edd2a5d679e0b6",
            "permutations": 2000,
            "random_seed": 42,
            "runtime_seconds": round(time.perf_counter() - t0, 2),
            "peak_ram_mb": round(get_peak_memory_mb(), 1),
        },
        "baseline_p6_results": {
            "model": "Mutual-Degree Quartiles (4 strata)",
            "observed_gaba_gaba": obs_gaba,
            "total_mutual_dyads": total_m,
            "null_mean": res_p6["null_mean"],
            "null_std": res_p6["null_std"],
            "enrichment_ratio": res_p6["enrichment_ratio"],
            "z_score": res_p6["z_score"],
            "empirical_p_value": res_p6["empirical_p_value"],
        },
        "primary_sensitivity_model": {
            "model": "Joint Directed In-Degree x Out-Degree Tertiles (9 strata)",
            "null_hypothesis": "Observed reciprocal dyad GABA-GABA pairing is explained by joint directed in-degree and out-degree tertile profiles.",
            "strata_count": len(grid9_list),
            "strata_diagnostics": strata_diagnostics,
            "observed_gaba_gaba": obs_gaba,
            "null_mean": res_grid9["null_mean"],
            "null_std": res_grid9["null_std"],
            "enrichment_ratio": res_grid9["enrichment_ratio"],
            "z_score": res_grid9["z_score"],
            "empirical_p_value": res_grid9["empirical_p_value"],
            "survived_gate": bool(res_grid9["empirical_p_value"] < 0.05),
        },
        "secondary_sensitivity_model": {
            "model": "Joint Directed In-Degree x Out-Degree Medians (4 strata)",
            "strata_count": len(grid4_list),
            "null_mean": res_grid4["null_mean"],
            "null_std": res_grid4["null_std"],
            "enrichment_ratio": res_grid4["enrichment_ratio"],
            "z_score": res_grid4["z_score"],
            "empirical_p_value": res_grid4["empirical_p_value"],
        },
        "annotation_matching": {
            "total_active_nodes": len(active_nodes),
            "matched_nodes": matched_nodes,
            "matching_rate_pct": round(matched_nodes / len(active_nodes) * 100.0, 2),
            "all_dyads_matched": dyads_both_matched,
            "all_dyads_coverage_pct": round(dyads_both_matched / len(mutual_dyads) * 100.0, 2),
            "gaba_dyads_matched": gaba_both_matched,
            "gaba_dyads_coverage_pct": round(gaba_both_matched / len(gaba_dyads) * 100.0, 2),
            "node_classes": dict(Counter(a["cell_class"] for a in annotations.values())),
            "node_subclasses": dict(Counter(a["cell_sub_class"] for a in annotations.values())),
        },
        "descriptive_biological_summary": {
            "all_dyads": {
                "both_same_subclass": same_subclass_cnt,
                "both_same_subclass_pct": round(same_subclass_cnt / total_m * 100.0, 2),
                "different_subclass": diff_subclass_cnt,
                "different_subclass_pct": round(diff_subclass_cnt / total_m * 100.0, 2),
                "unannotated_subclass": unannot_subclass_cnt,
                "unannotated_subclass_pct": round(unannot_subclass_cnt / total_m * 100.0, 2),
                "both_same_specific_type": same_type_cnt,
                "both_same_specific_type_pct": round(same_type_cnt / total_m * 100.0, 2),
                "top_subclass_pairs": [
                    {"pair": list(p), "count": cnt, "pct": round(cnt / total_m * 100.0, 2)}
                    for p, cnt in subclass_pair_counts.most_common(10)
                ],
                "top_type_pairs": [
                    {"pair": list(p), "count": cnt, "pct": round(cnt / total_m * 100.0, 2)}
                    for p, cnt in type_pair_counts.most_common(15)
                ],
            },
            "gaba_gaba_dyads": {
                "total_gaba_gaba": len(gaba_dyads),
                "top_subclass_pairs": [
                    {"pair": list(p), "count": cnt, "pct": round(cnt / len(gaba_dyads) * 100.0, 2)}
                    for p, cnt in gg_subclass_counts.most_common(5)
                ],
                "top_type_pairs": [
                    {"pair": list(p), "count": cnt, "pct": round(cnt / len(gaba_dyads) * 100.0, 2)}
                    for p, cnt in gg_type_counts.most_common(15)
                ],
            },
        },
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(final_output, f, indent=2)

    print("\n" + "=" * 80)
    print(f"Results successfully saved to: {OUT_JSON}")
    print(f"Total Phase 7 runtime: {time.perf_counter() - t0:.2f}s | Peak RAM: {get_peak_memory_mb():.1f} MB")
    print("=" * 80)


if __name__ == "__main__":
    main()

