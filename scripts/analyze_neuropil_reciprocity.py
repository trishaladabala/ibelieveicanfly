#!/usr/bin/env python3
"""
Regional Neuropil Reciprocity Hierarchy Analysis.

Executes Candidate Research Project 1:
Quantifies structural feedback (reciprocity ratio, mutual dyads, synaptic weighting)
across canonical functional tiers:
1. Primary Sensory Neuropils:
   - Antennal Lobe (AL_L, AL_R) - Olfactory
   - Medulla (ME_L, ME_R) - Visual
2. Associative / Learning Neuropils:
   - Mushroom Body Calyx (MB_CA_L, MB_CA_R)
   - Mushroom Body Lobes (MB_ML_R, MB_VL_R)
3. Premotor, Steering, and Navigation Neuropils:
   - Ellipsoid Body (EB) - Ring attractor heading direction
   - Fan-shaped Body (FB) - Spatial orientation & navigation
   - Protocerebral Bridge (PB) - Heading compass
   - Lateral Accessory Lobe (LAL_L, LAL_R) - Motor command routing
   - Anterior Ventrolateral Protocerebrum (AVLP_L, AVLP_R) - Sensorimotor hub

Memory bounded: Streams through the 16.8M Feather file in a single sequential pass.
"""

from __future__ import annotations

import argparse
import json
import resource
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

# Add project root and local venv to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_PATH = PROJECT_ROOT / ".venv" / "lib" / "python3.12" / "site-packages"
if VENV_PATH.exists():
    sys.path.insert(0, str(VENV_PATH))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

try:
    import pyarrow.ipc as ipc
except ImportError:
    ipc = None


def get_peak_memory_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


TARGET_NEUROPILS = {
    # Sensory
    "AL_R": "Primary Sensory (Olfactory)",
    "AL_L": "Primary Sensory (Olfactory)",
    "ME_R": "Primary Sensory (Visual)",
    "ME_L": "Primary Sensory (Visual)",
    # Associative Learning & Memory
    "MB_CA_R": "Associative (Mushroom Body Calyx)",
    "MB_CA_L": "Associative (Mushroom Body Calyx)",
    "MB_ML_R": "Associative (Mushroom Body Medial Lobe)",
    "MB_PED_R": "Associative (Mushroom Body Pedunculus)",
    # Central Navigation / Attractor
    "EB": "Navigation (Ellipsoid Body Ring Attractor)",
    "PB": "Navigation (Protocerebral Bridge Compass)",
    "FB": "Navigation (Fan-shaped Body)",
    # Premotor Steering
    "LAL_R": "Premotor Steering (Lateral Accessory Lobe)",
    "LAL_L": "Premotor Steering (Lateral Accessory Lobe)",
    "AVLP_R": "Premotor Hub (Ant. Ventrolat. Protocerebrum)",
    "AVLP_L": "Premotor Hub (Ant. Ventrolat. Protocerebrum)",
}


def analyze_regional_reciprocity(
    file_path: Path,
    min_synapse_threshold: int = 1,
) -> dict[str, Any]:
    start_time = time.perf_counter()
    print(f"Streaming {file_path.name} to extract intra-neuropil networks (threshold w >= {min_synapse_threshold})...")

    # Mapping per neuropil: node_to_id, id_to_node, edge_weights
    neuropil_nodes: dict[str, dict[int, int]] = defaultdict(dict)
    neuropil_edges: dict[str, dict[int, int]] = defaultdict(dict)

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
            npils = batch.column(col_npil).to_pylist()

            for p, q, w, npil in zip(pres, posts, weights, npils):
                if not npil or npil not in TARGET_NEUROPILS:
                    continue
                if p is None or q is None or w is None or w < min_synapse_threshold:
                    continue

                nodes_dict = neuropil_nodes[npil]
                if p not in nodes_dict:
                    nodes_dict[p] = len(nodes_dict)
                u = nodes_dict[p]

                if q not in nodes_dict:
                    nodes_dict[q] = len(nodes_dict)
                v = nodes_dict[q]

                edge_key = (u << 32) | v
                edges_dict = neuropil_edges[npil]
                edges_dict[edge_key] = edges_dict.get(edge_key, 0) + w

    ingest_time = time.perf_counter() - start_time
    print(f"Completed streaming in {ingest_time:.2f}s. Computing topological metrics for {len(neuropil_edges)} regions...")

    regional_metrics = []
    for npil, edges_dict in neuropil_edges.items():
        desc = TARGET_NEUROPILS.get(npil, "Unknown Region")
        nodes_dict = neuropil_nodes[npil]
        N = len(nodes_dict)
        E = len(edges_dict)
        total_synapses = sum(edges_dict.values())

        # Reciprocity
        mutual_dyads = 0
        for edge_key, w in edges_dict.items():
            u = edge_key >> 32
            v = edge_key & 0xFFFFFFFF
            if u < v and ((v << 32) | u) in edges_dict:
                mutual_dyads += 1

        reciprocity = (2.0 * mutual_dyads / E) if E > 0 else 0.0
        mean_weight = (total_synapses / E) if E > 0 else 0.0
        density = (E / (N * (N - 1))) if N > 1 else 0.0

        # Expected reciprocity under random Erdős-Rényi graph with equal density:
        er_reciprocity = density
        enrichment_factor = (reciprocity / er_reciprocity) if er_reciprocity > 0 else 0.0

        # Functional tier categorization
        if "Sensory" in desc:
            tier = "Primary Sensory"
        elif "Associative" in desc:
            tier = "Associative Learning"
        elif "Navigation" in desc:
            tier = "Central Navigation / Attractor"
        elif "Premotor" in desc:
            tier = "Premotor Steering"
        else:
            tier = "Other"

        regional_metrics.append({
            "neuropil": npil,
            "description": desc,
            "functional_tier": tier,
            "unique_neurons": N,
            "directed_edges": E,
            "total_synapses": total_synapses,
            "mean_synapses_per_edge": round(mean_weight, 2),
            "network_density": round(density, 6),
            "mutual_dyads": mutual_dyads,
            "reciprocity_ratio": round(reciprocity, 4),
            "reciprocity_percentage": round(reciprocity * 100.0, 2),
            "er_expected_reciprocity_pct": round(er_reciprocity * 100.0, 4),
            "reciprocity_enrichment_fold": round(enrichment_factor, 1),
        })

    # Sort by functional tier and reciprocity
    regional_metrics.sort(key=lambda x: (x["functional_tier"], -x["reciprocity_ratio"]))

    # Tier aggregations
    tier_summary = defaultdict(lambda: {"edges": 0, "mutual_dyads": 0, "synapses": 0, "regions": []})
    for r in regional_metrics:
        t = r["functional_tier"]
        tier_summary[t]["edges"] += r["directed_edges"]
        tier_summary[t]["mutual_dyads"] += r["mutual_dyads"]
        tier_summary[t]["synapses"] += r["total_synapses"]
        tier_summary[t]["regions"].append(r["neuropil"])

    tier_aggregate_report = {}
    for t, vals in tier_summary.items():
        rec = (2.0 * vals["mutual_dyads"] / vals["edges"]) if vals["edges"] > 0 else 0.0
        tier_aggregate_report[t] = {
            "regions_count": len(vals["regions"]),
            "regions_list": vals["regions"],
            "total_directed_edges": vals["edges"],
            "total_mutual_dyads": vals["mutual_dyads"],
            "tier_reciprocity_percentage": round(rec * 100.0, 2),
        }

    total_time = time.perf_counter() - start_time
    peak_ram = get_peak_memory_mb()

    result = {
        "analysis_metadata": {
            "dataset_file": file_path.name,
            "min_synapse_threshold": min_synapse_threshold,
            "execution_time_seconds": round(total_time, 2),
            "peak_ram_mb": round(peak_ram, 1),
        },
        "functional_tier_summary": tier_aggregate_report,
        "neuropil_detailed_metrics": regional_metrics,
    }

    output_path = PROJECT_ROOT / "results" / f"neuropil_reciprocity_w{min_synapse_threshold}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"\nAnalysis complete in {total_time:.2f}s (Peak RAM: {peak_ram:.1f} MB). Saved to: {output_path}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze reciprocity hierarchy across functional neuropils.")
    parser.add_argument("--file", type=Path, default=PROJECT_ROOT / "data" / "raw" / "fafb_v783" / "proofread_connections_783.feather")
    parser.add_argument("--threshold", type=int, default=1, help="Minimum synapse weight threshold (default: 1).")
    args = parser.parse_args()

    res = analyze_regional_reciprocity(args.file, min_synapse_threshold=args.threshold)
    print("\n================ FUNCTIONAL TIER RECIPROCITY SUMMARY ================")
    for tier, data in res["functional_tier_summary"].items():
        print(f"  {tier:35s}: Reciprocity = {data['tier_reciprocity_percentage']:5.2f}% ({data['total_directed_edges']:,} edges)")
    print("=====================================================================\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

