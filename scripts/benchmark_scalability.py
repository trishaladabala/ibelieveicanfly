#!/usr/bin/env python3
"""
Scalability and Performance Benchmarking for Fly-Brain Connectomics Pipeline.

Evaluates streaming throughput, peak RAM usage, and topological metric scaling
on the resource-constrained Dell Inspiron 5558 across sample sizes:
- 10,000 records
- 50,000 records
- 250,000 records
- 1,000,000 records
- Complete dataset (16,847,997 records)

Strictly respects:
- Single-worker sequential execution.
- Peak resident memory ceiling < 2.5 GiB.
- Low-overhead Disjoint-Set (Union-Find) and 64-bit compact integer edge keys.
"""

from __future__ import annotations

import argparse
import json
import os
import resource
import sys
import time
from collections import Counter
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
    """Return peak resident memory in megabytes."""
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


class DisjointSet:
    """Disjoint Set Union (Union-Find) with path compression and rank optimization."""
    __slots__ = ("parent", "rank")

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        # Path compression
        curr = x
        while curr != root:
            nxt = self.parent[curr]
            self.parent[curr] = root
            curr = nxt
        return root

    def union(self, x: int, y: int) -> None:
        rx = self.find(x)
        ry = self.find(y)
        if rx == ry:
            return
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
        elif self.rank[rx] > self.rank[ry]:
            self.parent[ry] = rx
        else:
            self.parent[ry] = rx
            self.rank[rx] += 1


def benchmark_stream(
    file_path: Path,
    max_records: int = -1,
    progress_interval_records: int = 2000000,
) -> dict[str, Any]:
    """
    Run an end-to-end streaming connectivity benchmark over the specified dataset.
    """
    start_time = time.perf_counter()
    ram_start = get_peak_memory_mb()

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    node_to_id: dict[int, int] = {}
    id_to_node: list[int] = []
    # Directed edge weights: key = (u_idx << 32) | v_idx -> aggregated syn_count
    edge_weights: dict[int, int] = {}

    neuropil_synapses: Counter[str] = Counter()
    neuropil_records: Counter[str] = Counter()

    nt_weighted_sum: Counter[str] = Counter()
    nt_synapse_total: Counter[str] = Counter()

    total_records_processed = 0
    duplicate_records_aggregated = 0
    malformed_records = 0
    autapse_records = 0

    with open(file_path, "rb") as f:
        reader = ipc.open_file(f)
        total_rows_in_file = reader.count_rows() if hasattr(reader, "count_rows") else sum(reader.get_batch(i).num_rows for i in range(reader.num_record_batches))
        limit = total_rows_in_file if (max_records is None or max_records < 0) else min(max_records, total_rows_in_file)

        col_pre = "pre_pt_root_id"
        col_post = "post_pt_root_id"
        col_weight = "syn_count"
        col_npil = "neuropil"
        nt_cols = [c for c in ["ach_avg", "gaba_avg", "glut_avg", "oct_avg", "ser_avg", "da_avg"] if c in reader.schema.names]

        last_progress_time = start_time

        for batch_idx in range(reader.num_record_batches):
            if total_records_processed >= limit:
                break

            batch = reader.get_batch(batch_idx)
            pres = batch.column(col_pre).to_pylist()
            posts = batch.column(col_post).to_pylist()
            weights = batch.column(col_weight).to_pylist()
            npils = batch.column(col_npil).to_pylist() if col_npil in reader.schema.names else [None] * len(pres)

            nt_data = {nt: batch.column(nt).to_pylist() for nt in nt_cols}

            batch_len = len(pres)
            to_process = min(batch_len, limit - total_records_processed)

            for i in range(to_process):
                p = pres[i]
                q = posts[i]
                w = weights[i]
                npil = npils[i]

                if p is None or q is None or w is None or w <= 0:
                    malformed_records += 1
                    continue

                if p not in node_to_id:
                    node_to_id[p] = len(id_to_node)
                    id_to_node.append(p)
                u = node_to_id[p]

                if q not in node_to_id:
                    node_to_id[q] = len(id_to_node)
                    id_to_node.append(q)
                v = node_to_id[q]

                edge_key = (u << 32) | v
                if edge_key in edge_weights:
                    duplicate_records_aggregated += 1
                    edge_weights[edge_key] += w
                else:
                    edge_weights[edge_key] = w

                if u == v:
                    autapse_records += 1

                if npil:
                    neuropil_synapses[npil] += w
                    neuropil_records[npil] += 1

                for nt, val_list in nt_data.items():
                    val = val_list[i]
                    if val is not None:
                        nt_weighted_sum[nt] += val * w
                        nt_synapse_total[nt] += w

                total_records_processed += 1

            if progress_interval_records > 0 and (total_records_processed % progress_interval_records < batch_len or total_records_processed >= limit):
                now = time.perf_counter()
                elapsed_so_far = now - start_time
                rps = total_records_processed / elapsed_so_far if elapsed_so_far > 0 else 0
                current_ram = get_peak_memory_mb()
                print(
                    f"  [Progress] Processed {total_records_processed:,} / {limit:,} records "
                    f"({total_records_processed/limit*100:.1f}%) | "
                    f"Time: {elapsed_so_far:.2f}s | Throughput: {rps:,.0f} rows/s | RAM: {current_ram:.1f} MB",
                    file=sys.stderr,
                    flush=True,
                )

    ingest_time = time.perf_counter() - start_time

    # Compute Graph Metrics
    t_graph_start = time.perf_counter()
    N = len(id_to_node)
    total_directed_edges = len(edge_weights)
    total_synapses = sum(edge_weights.values())

    out_degrees = [0] * N
    in_degrees = [0] * N
    out_strengths = [0] * N
    in_strengths = [0] * N
    weights_list: list[int] = []

    ds = DisjointSet(N)
    mutual_dyads = 0

    for edge_key, w in edge_weights.items():
        u = edge_key >> 32
        v = edge_key & 0xFFFFFFFF
        weights_list.append(w)
        out_degrees[u] += 1
        in_degrees[v] += 1
        out_strengths[u] += w
        in_strengths[v] += w

        if u != v:
            ds.union(u, v)
            if u < v and ((v << 32) | u) in edge_weights:
                mutual_dyads += 1

    reciprocity_ratio = (2.0 * mutual_dyads / total_directed_edges) if total_directed_edges > 0 else 0.0

    # Weakly connected components calculation
    comp_counts = Counter(ds.find(i) for i in range(N))
    wcc_sorted = sorted(comp_counts.values(), reverse=True)
    num_components = len(wcc_sorted)
    largest_wcc_size = wcc_sorted[0] if wcc_sorted else 0
    largest_wcc_coverage = (largest_wcc_size / N) if N > 0 else 0.0

    # Identify top hubs
    top_out_deg_indices = sorted(range(N), key=lambda i: (-out_degrees[i], str(id_to_node[i])))[:5]
    top_in_deg_indices = sorted(range(N), key=lambda i: (-in_degrees[i], str(id_to_node[i])))[:5]
    top_out_str_indices = sorted(range(N), key=lambda i: (-out_strengths[i], str(id_to_node[i])))[:5]
    top_in_str_indices = sorted(range(N), key=lambda i: (-in_strengths[i], str(id_to_node[i])))[:5]

    top_out_degree = [{"node_id": str(id_to_node[i]), "out_degree": out_degrees[i]} for i in top_out_deg_indices]
    top_in_degree = [{"node_id": str(id_to_node[i]), "in_degree": in_degrees[i]} for i in top_in_deg_indices]
    top_out_strength = [{"node_id": str(id_to_node[i]), "out_synapses": out_strengths[i]} for i in top_out_str_indices]
    top_in_strength = [{"node_id": str(id_to_node[i]), "in_synapses": in_strengths[i]} for i in top_in_str_indices]

    # Summary statistics for distributions
    def calc_stats(vals: list[int]) -> dict[str, Any]:
        if not vals:
            return {"count": 0, "min": 0, "max": 0, "mean": 0.0, "median": 0.0, "q25": 0.0, "q75": 0.0}
        sv = sorted(vals)
        n = len(sv)
        return {
            "count": n,
            "min": sv[0],
            "max": sv[-1],
            "mean": round(sum(sv) / n, 2),
            "median": round(float(sv[n // 2]), 2),
            "q25": round(float(sv[n // 4]), 2),
            "q75": round(float(sv[(3 * n) // 4]), 2),
        }

    out_deg_stats = calc_stats(out_degrees)
    in_deg_stats = calc_stats(in_degrees)
    weight_stats = calc_stats(weights_list)

    # Neurotransmitter global percentage
    nt_fractions = {}
    for nt in nt_cols:
        tot = nt_synapse_total[nt]
        if tot > 0:
            nt_fractions[nt.replace("_avg", "")] = round((nt_weighted_sum[nt] / tot) * 100.0, 2)

    total_time = time.perf_counter() - start_time
    graph_time = time.perf_counter() - t_graph_start
    peak_ram = get_peak_memory_mb()

    return {
        "benchmark_metadata": {
            "dataset_file": file_path.name,
            "max_records_requested": max_records,
            "total_records_processed": total_records_processed,
            "is_full_dataset": total_records_processed == total_rows_in_file,
            "wall_time_seconds": round(total_time, 3),
            "ingestion_time_seconds": round(ingest_time, 3),
            "graph_analysis_time_seconds": round(graph_time, 3),
            "throughput_records_per_second": round(total_records_processed / total_time, 1) if total_time > 0 else 0,
            "peak_ram_mb": round(peak_ram, 1),
            "ram_headroom_mb": round(2560.0 - peak_ram, 1),
        },
        "topology": {
            "unique_neurons": N,
            "unique_directed_edges": total_directed_edges,
            "total_synapse_count": total_synapses,
            "duplicate_records_aggregated": duplicate_records_aggregated,
            "autapse_records": autapse_records,
            "mutual_dyads": mutual_dyads,
            "reciprocity_ratio": round(reciprocity_ratio, 4),
            "connected_components": num_components,
            "largest_component_neurons": largest_wcc_size,
            "largest_component_coverage": round(largest_wcc_coverage, 4),
        },
        "distributions": {
            "out_degree": out_deg_stats,
            "in_degree": in_deg_stats,
            "edge_weights": weight_stats,
        },
        "top_hubs": {
            "top_out_degree": top_out_degree,
            "top_in_degree": top_in_degree,
            "top_out_strength": top_out_strength,
            "top_in_strength": top_in_strength,
        },
        "regional_breakdown": {
            "neuropils_count": len(neuropil_synapses),
            "top_neuropils_by_synapses": dict(neuropil_synapses.most_common(10)),
            "top_neuropils_by_records": dict(neuropil_records.most_common(10)),
        },
        "neurotransmitter_profile_percentage": nt_fractions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run scalability and performance benchmark.")
    parser.add_argument("--file", type=Path, default=PROJECT_ROOT / "data" / "raw" / "fafb_v783" / "proofread_connections_783.feather")
    parser.add_argument("--sizes", nargs="+", type=int, default=[10000, 50000, 250000, 1000000, -1], help="Record sizes to benchmark (-1 for full dataset).")
    parser.add_argument("--output-json", type=Path, default=PROJECT_ROOT / "results" / "scalability_benchmark.json")
    args = parser.parse_args()

    print("================================================================================")
    print("FLY-BRAIN CONNECTOMICS PERFORMANCE & SCALABILITY BENCHMARK")
    print(f"Dataset:  {args.file}")
    print(f"Hardware: Dell Inspiron 5558 (Core i5-4210U @ 1.70GHz, 8 GB RAM, 5400 RPM HDD)")
    print(f"Memory Ceiling: 2.5 GiB (2560 MB)")
    print("================================================================================\n")

    results = []
    for sz in args.sizes:
        label = f"{sz:,} records" if sz > 0 else "FULL DATASET (16,847,997 records)"
        print(f"\n>>> Running Benchmark: {label}...")
        res = benchmark_stream(args.file, max_records=sz)
        meta = res["benchmark_metadata"]
        topo = res["topology"]
        print(
            f"    Result: {meta['total_records_processed']:,} records in {meta['wall_time_seconds']:.2f}s "
            f"({meta['throughput_records_per_second']:,.0f} rec/s) | Peak RAM: {meta['peak_ram_mb']:.1f} MB | "
            f"Headroom: {meta['ram_headroom_mb']:.1f} MB\n"
            f"    Topology: {topo['unique_neurons']:,} neurons, {topo['unique_directed_edges']:,} edges, "
            f"{topo['total_synapse_count']:,} synapses, Reciprocity: {topo['reciprocity_ratio']*100:.2f}%, "
            f"WCC largest component coverage: {topo['largest_component_coverage']*100:.2f}%"
        )
        results.append(res)

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    with args.output_json.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nBenchmark suite completed successfully. Results saved to: {args.output_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

