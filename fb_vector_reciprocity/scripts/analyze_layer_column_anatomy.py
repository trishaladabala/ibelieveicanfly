#!/usr/bin/env python3
"""
analyze_layer_column_anatomy.py

Maps all active Fan-Shaped Body (FB) neurons and mutual dyads to official
version-pinned FlyWire v2.1.0 annotations (Supplemental_file1_neuron_annotations.tsv).

Quantifies:
1. Annotation coverage and match rates across all 2,465 active FB neurons.
2. Broad morphological class decomposition:
   - Columnar Input: PFN, PFGs
   - Columnar Output: PFL, PFR
   - Columnar Interneuron: vDelta, hDelta
   - Tangential FB: FB1 through FB9
   - ExR Tangential: ExR
3. Morphology pairing of all 5,435 mutual dyads:
   - Columnar <-> Tangential
   - Columnar <-> Columnar
   - Tangential <-> Tangential
4. The Anatomical Substrate of the 554 ACh <-> GABA Mutual Dyads:
   - Direct test of whether ACh is strictly Columnar and GABA is strictly Tangential.
   - Breakdown by horizontal layers (FB1 to FB9).
   - Top specific cell-type pairs (e.g. vDelta <-> FB6, PFN <-> FB4).

Outputs:
- results/fb_layer_column_anatomy.json
- results/tables/fb_layer_distribution_table.tsv
- results/tables/fb_celltype_pairs_table.tsv
- data/fb_annotation_map.json
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import json
import math
import re
from pathlib import Path
import resource
import sys
import time
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CACHE_FILE = REPO_ROOT / "data" / "fb_node_covariates.json"
if not CACHE_FILE.exists():
    CACHE_FILE = REPO_ROOT.parent / "fb_vector_reciprocity" / "data" / "fb_node_covariates.json"
ANNOT_FILE = REPO_ROOT.parent / "data" / "raw" / "annotations_v2.1.0" / "Supplemental_file1_neuron_annotations.tsv"
if not ANNOT_FILE.exists():
    ANNOT_FILE = REPO_ROOT / "data" / "fb_annotation_map.json"

OUT_JSON = REPO_ROOT / "results" / "fb_layer_column_anatomy.json"
OUT_MAP = REPO_ROOT / "data" / "fb_annotation_map.json"
OUT_LAYER_TSV = REPO_ROOT / "results" / "tables" / "fb_layer_distribution_table.tsv"
OUT_CELLTYPE_TSV = REPO_ROOT / "results" / "tables" / "fb_celltype_pairs_table.tsv"


def get_peak_memory_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def classify_morphology(sub_class: str, hb_type: str, cell_type: str = "") -> tuple[str, str, int | None]:
    """
    Classifies a neuron into morphological family and extracts FB layer if applicable.
    Uses hemibrain_type if available; falls back to cell_type if hemibrain_type is missing.
    Returns: (morphology_family, specific_base_type, layer_num)
    """
    hb = hb_type.strip()
    ct = cell_type.strip()
    sc = sub_class.strip().lower()

    # Determine identifier string to extract type and layer
    target_str = hb
    if not target_str:
        if ct.startswith("CB."):
            target_str = ct[3:]
        else:
            target_str = ct

    # Extract layer number if present (e.g. FB1A -> 1, FB5I2 -> 5, FB3,4L -> 4)
    layer_match = re.search(r"FB([1-9])", target_str)
    if not layer_match and ct:
        layer_match = re.search(r"FB([1-9])", ct)
    layer_num = int(layer_match.group(1)) if layer_match else None

    # Base type
    if hb:
        base_type = hb.split("_")[0] if "_" in hb else hb
        base_type = base_type.split(",")[0] if "," in base_type else base_type
    elif ct:
        ct_clean = ct[3:] if ct.startswith("CB.") else ct
        base_type = ct_clean.split("_")[0] if "_" in ct_clean else ct_clean
        base_type = base_type.split(",")[0] if "," in base_type else base_type
    else:
        base_type = ""

    # Morphology family
    check_str = hb or target_str
    if check_str.startswith("PFN") or check_str.startswith("PFG"):
        family = "columnar_input"
    elif check_str.startswith("PFL") or check_str.startswith("PFR"):
        family = "columnar_output"
    elif check_str.startswith("vDelta") or check_str.startswith("hDelta"):
        family = "columnar_interneuron"
    elif check_str.startswith("FB"):
        family = "tangential_fb"
    elif check_str.startswith("ExR"):
        family = "tangential_exr"
    elif "columnar" in sc:
        family = "columnar_unclassified"
    elif "tangential" in sc:
        family = "tangential_unclassified"
    else:
        family = "unclassified"

    return family, base_type, layer_num


def main() -> None:
    t0 = time.perf_counter()
    print("=" * 80)
    print("FAN-SHAPED BODY (FB) LAYER-COLUMN CELLULAR ANATOMY ANALYSIS")
    print("=" * 80)

    if not CACHE_FILE.exists():
        print(f"Error: cache file {CACHE_FILE} not found.")
        sys.exit(1)
    if not ANNOT_FILE.exists():
        print(f"Error: annotation file {ANNOT_FILE} not found.")
        sys.exit(1)

    print(f"Loading cached FB covariates from {CACHE_FILE} ...")
    with open(CACHE_FILE) as f:
        cache_data = json.load(f)

    active_nodes = cache_data["active_nodes"]
    mutual_dyads = cache_data["mutual_dyads"]
    node_dict = cache_data["nodes"]
    active_set = set(active_nodes)

    # 1. Load FlyWire v2.1.0 annotations
    print(f"Streaming FlyWire v2.1.0 annotations from {ANNOT_FILE} ...")
    node_annotations: dict[int, dict[str, Any]] = {}
    with open(ANNOT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rid_str = row["root_id"]
            if not rid_str:
                continue
            rid = int(rid_str)
            if rid in active_set:
                sc = row.get("cell_sub_class", "")
                hb = row.get("hemibrain_type", "")
                ct = row.get("cell_type", "")
                family, base_type, layer = classify_morphology(sc, hb, ct)

                node_annotations[rid] = {
                    "root_id": rid,
                    "cell_class": row.get("cell_class", ""),
                    "cell_sub_class": sc,
                    "cell_type": ct,
                    "hemibrain_type": hb,
                    "base_type": base_type,
                    "morphology_family": family,
                    "layer": layer,
                    "top_nt": row.get("top_nt", ""),
                    "top_nt_conf": float(row.get("top_nt_conf", 0.0)) if row.get("top_nt_conf") else None,
                    "side": row.get("side", ""),
                }

    coverage_pct = len(node_annotations) / len(active_nodes) * 100.0
    print(f"Active Nodes matched: {len(node_annotations)} / {len(active_nodes)} ({coverage_pct:.2f}%)")

    # Save annotation map
    print(f"Saving node annotation map to {OUT_MAP} ...")
    OUT_MAP.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_MAP, "w") as f:
        json.dump({str(k): v for k, v in node_annotations.items()}, f, indent=2)

    # 2. Analyze Morphology Distribution of Active Neurons
    morphology_counts = Counter(ann["morphology_family"] for ann in node_annotations.values())
    print("\nMorphology Family Census of Active FB Neurons:")
    for fam, cnt in morphology_counts.most_common():
        pct = cnt / len(active_nodes) * 100.0
        print(f"  {fam:22s}: {cnt:4d} ({pct:5.1f}%)")

    # Transmitter by Morphology
    nt_by_family: dict[str, Counter[str]] = defaultdict(Counter)
    for nid, ann in node_annotations.items():
        fam = ann["morphology_family"]
        nt = node_dict[str(nid)]["nt_name"]
        nt_by_family[fam][nt] += 1

    print("\nNeurotransmitter Profiles by Morphology Family:")
    for fam, cnts in sorted(nt_by_family.items(), key=lambda x: -sum(x[1].values())):
        total_f = sum(cnts.values())
        top_nts = ", ".join(f"{nt.upper()}:{c} ({c/total_f*100:.0f}%)" for nt, c in cnts.most_common(3))
        print(f"  {fam:22s} (N={total_f:4d}): {top_nts}")

    # 3. Analyze Mutual Dyad Morphology Pairings (M = 5,435)
    dyad_morphology = Counter()
    dyad_broad_category = Counter()
    all_dyad_layers = Counter()

    # Subsets
    ach_gaba_morphology = Counter()
    ach_gaba_broad = Counter()
    ach_gaba_layers = Counter()
    ach_gaba_cell_pairs = Counter()
    ach_gaba_nt_direction = Counter()  # Columnar-ACh/Tangential-GABA vs vice versa

    for u, v in mutual_dyads:
        ann_u = node_annotations.get(u)
        ann_v = node_annotations.get(v)
        if not ann_u or not ann_v:
            continue

        fam_u = ann_u["morphology_family"]
        fam_v = ann_v["morphology_family"]
        m_pair = f"{min(fam_u, fam_v)}__{max(fam_u, fam_v)}"
        dyad_morphology[m_pair] += 1

        # Layer assignment for all mutual dyads
        layer_u = ann_u["layer"]
        layer_v = ann_v["layer"]
        l_val_all = layer_u if layer_u is not None else layer_v
        if l_val_all is not None:
            all_dyad_layers[f"Layer_{l_val_all}"] += 1
        else:
            all_dyad_layers["Unassigned_Layer"] += 1

        # Broad category: Columnar-Tangential, Columnar-Columnar, Tangential-Tangential
        is_col_u = "columnar" in fam_u
        is_col_v = "columnar" in fam_v
        is_tan_u = "tangential" in fam_u
        is_tan_v = "tangential" in fam_v

        if is_col_u and is_col_v:
            broad = "columnar__columnar"
        elif is_tan_u and is_tan_v:
            broad = "tangential__tangential"
        elif (is_col_u and is_tan_v) or (is_tan_u and is_col_v):
            broad = "columnar__tangential"
        else:
            broad = "other"
        dyad_broad_category[broad] += 1

        # Transmitter pair
        nt_u = node_dict[str(u)]["nt_name"]
        nt_v = node_dict[str(v)]["nt_name"]
        is_ach_gaba = (nt_u == "ach" and nt_v == "gaba") or (nt_u == "gaba" and nt_v == "ach")

        if is_ach_gaba:
            ach_gaba_morphology[m_pair] += 1
            ach_gaba_broad[broad] += 1

            # Directional transmitter assignment by morphology
            if is_col_u and is_tan_v:
                ach_gaba_nt_direction[f"col_{nt_u}__tan_{nt_v}"] += 1
            elif is_tan_u and is_col_v:
                ach_gaba_nt_direction[f"col_{nt_v}__tan_{nt_u}"] += 1

            # Layer assignment
            layer_u = ann_u["layer"]
            layer_v = ann_v["layer"]
            l_val = layer_u if layer_u is not None else layer_v
            if l_val is not None:
                ach_gaba_layers[f"Layer_{l_val}"] += 1
            else:
                ach_gaba_layers["Unassigned_Layer"] += 1

            # Specific cell-type pair
            t_u = ann_u["base_type"] or "Unknown"
            t_v = ann_v["base_type"] or "Unknown"
            cp = f"{min(t_u, t_v)} <-> {max(t_u, t_v)}"
            ach_gaba_cell_pairs[cp] += 1

    total_m = len(mutual_dyads)
    print("\n--- Mutual Dyad Broad Morphology Breakdown (M = 5,435) ---")
    for cat, cnt in dyad_broad_category.most_common():
        pct = cnt / total_m * 100.0
        print(f"  {cat:24s}: {cnt:5d} ({pct:6.2f}%)")

    total_ach_gaba = sum(ach_gaba_broad.values())
    print(f"\n--- ACh <-> GABA Mutual Dyads Breakdown (N = {total_ach_gaba}) ---")
    for cat, cnt in ach_gaba_broad.most_common():
        pct = cnt / total_ach_gaba * 100.0
        print(f"  {cat:24s}: {cnt:5d} ({pct:6.2f}%)")

    print("\nDirectional Chemical Polarity in Columnar-Tangential ACh <-> GABA Dyads:")
    for pol, cnt in ach_gaba_nt_direction.most_common():
        pct = cnt / sum(ach_gaba_nt_direction.values()) * 100.0
        print(f"  {pol:24s}: {cnt:5d} ({pct:6.2f}%)")

    print("\nLayer Distribution of ACh <-> GABA Reciprocal Loops:")
    for lyr, cnt in sorted(ach_gaba_layers.items()):
        pct = cnt / total_ach_gaba * 100.0
        bar = "#" * int(pct // 2)
        print(f"  {lyr:16s}: {cnt:4d} ({pct:5.1f}%) | {bar}")

    print("\nTop 15 Specific Cell-Type Pairs Forming ACh <-> GABA Mutual Dyads:")
    for cp, cnt in ach_gaba_cell_pairs.most_common(15):
        pct = cnt / total_ach_gaba * 100.0
        print(f"  {cp:35s}: {cnt:4d} ({pct:5.2f}%)")

    # 3.5 Layer 4 & 5 Statistical Concentration Test (Fisher's exact test)
    l45_ag = ach_gaba_layers.get("Layer_4", 0) + ach_gaba_layers.get("Layer_5", 0)
    other_ag = total_ach_gaba - l45_ag
    l45_all = all_dyad_layers.get("Layer_4", 0) + all_dyad_layers.get("Layer_5", 0)
    l45_other = l45_all - l45_ag
    other_dyads_total = total_m - total_ach_gaba
    other_other = other_dyads_total - l45_other

    odds_ratio = (l45_ag * other_other) / max(1, other_ag * l45_other)
    K_hyper = l45_all
    N_pop = total_m
    n_sample = total_ach_gaba
    fisher_p = sum(
        math.comb(K_hyper, x) * math.comb(N_pop - K_hyper, n_sample - x) / math.comb(N_pop, n_sample)
        for x in range(l45_ag, n_sample + 1)
    )
    print("\nStatistical Significance of Layer 4 & 5 Concentration:")
    print(f"  ACh-GABA in L4/5: {l45_ag} / {total_ach_gaba} ({l45_ag / total_ach_gaba * 100:.2f}%)")
    print(f"  All dyads in L4/5: {l45_all} / {total_m} ({l45_all / total_m * 100:.2f}%)")
    print(f"  Odds Ratio: {odds_ratio:.2f} | Fisher's Exact p-value: {fisher_p:.2e}")

    # 4. Save Structured Results
    results = {
        "metadata": {
            "neuropil": "FB",
            "active_nodes_count": len(active_nodes),
            "matched_annotations_count": len(node_annotations),
            "coverage_pct": round(coverage_pct, 2),
            "mutual_dyads_count": total_m,
            "ach_gaba_dyads_count": total_ach_gaba,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
        "morphology_census": dict(morphology_counts),
        "dyad_broad_category": dict(dyad_broad_category),
        "dyad_morphology_detailed": dict(dyad_morphology),
        "ach_gaba_broad": dict(ach_gaba_broad),
        "ach_gaba_polarity": dict(ach_gaba_nt_direction),
        "all_dyad_layers": dict(all_dyad_layers),
        "ach_gaba_layers": dict(ach_gaba_layers),
        "layer_4_5_concentration_test": {
            "l45_ach_gaba_count": l45_ag,
            "l45_ach_gaba_pct": round(l45_ag / total_ach_gaba * 100.0, 2),
            "l45_all_dyads_count": l45_all,
            "l45_all_dyads_pct": round(l45_all / total_m * 100.0, 2),
            "odds_ratio": round(odds_ratio, 2),
            "fisher_exact_p_value": fisher_p,
            "is_statistically_significant": fisher_p < 0.001,
        },
        "ach_gaba_top_cell_pairs": dict(ach_gaba_cell_pairs.most_common(30)),
    }

    print(f"\nSaving results to {OUT_JSON} ...")
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)

    # Save Layer TSV Table
    OUT_LAYER_TSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_LAYER_TSV, "w") as f:
        f.write("Layer\tACh_GABA_Dyads\tPct_of_ACh_GABA\n")
        for lyr, cnt in sorted(ach_gaba_layers.items()):
            pct = round(cnt / total_ach_gaba * 100.0, 2)
            f.write(f"{lyr}\t{cnt}\t{pct}\n")

    # Save Cell-Type Pairs TSV Table
    OUT_CELLTYPE_TSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CELLTYPE_TSV, "w") as f:
        f.write("Rank\tCell_Type_Pair\tMutual_Dyads\tPct_of_ACh_GABA\n")
        for rank, (cp, cnt) in enumerate(ach_gaba_cell_pairs.most_common(30), start=1):
            pct = round(cnt / total_ach_gaba * 100.0, 2)
            f.write(f"{rank}\t{cp}\t{cnt}\t{pct}\n")

    print(f"Layer and cell-type tables saved. Analysis complete in {time.perf_counter() - t0:.2f}s!")


if __name__ == "__main__":
    main()
