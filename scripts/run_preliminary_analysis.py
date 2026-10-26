#!/usr/bin/env python3
"""
Preliminary Connectivity Analysis Pipeline for Fly-Brain Connectomics.

Features:
- Streaming CSV ingestion with schema validation and 64-bit ID preservation.
- Directed, weighted graph analysis using sparse Python dictionaries.
- Computes in/out-degree, in/out-strength, reciprocity, autapses, and weakly connected components.
- Zero heavy dependencies (pure Python standard library).
- Generates clean JSON summary results and standalone vector SVG visualizations.
- Explicit labeling of SOFTWARE TEST vs REAL DATA.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import os
import resource
import sys
import time
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Generator, TextIO


def get_peak_memory_mb() -> float:
    """Return peak resident memory in megabytes."""
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def open_file_stream(file_path: Path) -> TextIO:
    if file_path.suffix == ".gz":
        return gzip.open(file_path, "rt", encoding="utf-8", errors="replace")
    return file_path.open("r", encoding="utf-8", errors="replace")


def calculate_distribution_stats(values: list[int | float]) -> dict[str, float | int]:
    """Calculate summary descriptive statistics on a list of numbers."""
    if not values:
        return {"count": 0, "min": 0, "max": 0, "mean": 0.0, "median": 0.0, "q25": 0.0, "q75": 0.0}
    sorted_v = sorted(values)
    n = len(sorted_v)
    mean_val = sum(sorted_v) / n

    def get_percentile(p: float) -> float:
        k = (n - 1) * p
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return float(sorted_v[int(k)])
        return float(sorted_v[int(f)] * (c - k) + sorted_v[int(c)] * (k - f))

    return {
        "count": n,
        "min": sorted_v[0],
        "max": sorted_v[-1],
        "mean": round(mean_val, 2),
        "median": round(get_percentile(0.50), 2),
        "q25": round(get_percentile(0.25), 2),
        "q75": round(get_percentile(0.75), 2),
    }


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


def find_weakly_connected_components(nodes: set[str], adj_undirected: dict[str, set[str]]) -> list[set[str]]:
    """Compute weakly connected components using iterative BFS."""
    visited: set[str] = set()
    components: list[set[str]] = []

    for node in nodes:
        if node not in visited:
            component: set[str] = set()
            queue = deque([node])
            visited.add(node)
            while queue:
                curr = queue.popleft()
                component.add(curr)
                for neighbor in adj_undirected.get(curr, ()):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            components.append(component)

    components.sort(key=len, reverse=True)
    return components


def generate_svg_histogram(
    values: list[int],
    title: str,
    xlabel: str,
    output_path: Path,
    width: int = 640,
    height: int = 360,
    bins: int = 10,
) -> None:
    """Generate a lightweight, dependency-free SVG histogram for distributions."""
    if not values:
        return

    min_v = min(values)
    max_v = max(values)
    if min_v == max_v:
        max_v += 1

    bin_width = (max_v - min_v) / bins
    counts = [0] * bins

    for v in values:
        idx = int((v - min_v) / bin_width)
        if idx >= bins:
            idx = bins - 1
        counts[idx] += 1

    max_count = max(counts) if counts else 1

    pad_left = 60
    pad_right = 30
    pad_top = 40
    pad_bottom = 50
    chart_w = width - pad_left - pad_right
    chart_h = height - pad_top - pad_bottom

    bar_w = chart_w / bins

    svg_elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="background:#ffffff; font-family:sans-serif;">',
        f'  <text x="{width/2}" y="24" text-anchor="middle" font-size="14" font-weight="bold" fill="#1e293b">{title}</text>',
        f'  <text x="{pad_left + chart_w/2}" y="{height - 12}" text-anchor="middle" font-size="12" fill="#475569">{xlabel}</text>',
        f'  <line x1="{pad_left}" y1="{pad_top + chart_h}" x2="{pad_left + chart_w}" y2="{pad_top + chart_h}" stroke="#94a3b8" stroke-width="1.5"/>',
        f'  <line x1="{pad_left}" y1="{pad_top}" x2="{pad_left}" y2="{pad_top + chart_h}" stroke="#94a3b8" stroke-width="1.5"/>',
    ]

    for i, c in enumerate(counts):
        bar_h = (c / max_count) * chart_h
        bx = pad_left + i * bar_w + 2
        by = pad_top + chart_h - bar_h
        bw = max(bar_w - 4, 1)
        b_range_start = min_v + i * bin_width
        svg_elements.append(
            f'  <rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bar_h:.1f}" fill="#3b82f6" opacity="0.85">'
            f'<title>Range: [{b_range_start:.1f}, {b_range_start+bin_width:.1f}] Count: {c}</title></rect>'
        )

    # Y-axis ticks
    for tick_step in [0, 0.5, 1.0]:
        val = int(tick_step * max_count)
        ty = pad_top + chart_h - (tick_step * chart_h)
        svg_elements.append(
            f'  <line x1="{pad_left-4}" y1="{ty:.1f}" x2="{pad_left}" y2="{ty:.1f}" stroke="#64748b"/>'
            f'  <text x="{pad_left-8}" y="{ty+4:.1f}" text-anchor="end" font-size="10" fill="#64748b">{val}</text>'
        )

    svg_elements.append('</svg>')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(svg_elements))

def iter_records(file_path: Path) -> Generator[dict[str, Any], None, None]:
    """Stream connectivity records from either CSV/TSV or Apache Arrow Feather files."""
    if file_path.suffix.lower() == ".feather":
        try:
            import pyarrow.ipc as ipc
        except ImportError:
            venv_path = Path(__file__).resolve().parent.parent / ".venv" / "lib" / "python3.12" / "site-packages"
            if venv_path.exists():
                sys.path.insert(0, str(venv_path))
                import pyarrow.ipc as ipc
            else:
                raise ImportError("pyarrow is required to read .feather files. Install in local .venv.")

        with open(file_path, "rb") as f:
            reader = ipc.open_file(f)
            header = list(reader.schema.names)
            norm_map = {c.lower(): c for c in header}
            pre_col = next((norm_map[c] for c in ["pre_root_id", "pre_pt_root_id", "source", "pre", "bodyid_pre"] if c in norm_map), None)
            post_col = next((norm_map[c] for c in ["post_root_id", "post_pt_root_id", "target", "post", "bodyid_post"] if c in norm_map), None)
            weight_col = next((norm_map[c] for c in ["syn_count", "weight", "count", "num_syn", "synapses"] if c in norm_map), None)
            neuropil_col = next((norm_map[c] for c in ["neuropil", "roi", "region"] if c in norm_map), None)

            for i in range(reader.num_record_batches):
                batch = reader.get_batch(i)
                pre_list = batch.column(pre_col).to_pylist() if pre_col else []
                post_list = batch.column(post_col).to_pylist() if post_col else []
                weight_list = batch.column(weight_col).to_pylist() if weight_col else [1] * len(pre_list)
                neuropil_list = batch.column(neuropil_col).to_pylist() if neuropil_col else [None] * len(pre_list)

                for pre_val, post_val, weight_val, npil_val in zip(pre_list, post_list, weight_list, neuropil_list):
                    yield {
                        "pre": str(pre_val).strip() if pre_val is not None else "",
                        "post": str(post_val).strip() if post_val is not None else "",
                        "weight": weight_val,
                        "neuropil": str(npil_val).strip() if npil_val is not None else None,
                    }
    else:
        with open_file_stream(file_path) as f:
            header: list[str] = []
            delimiter = ","
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                delimiter = "\t" if "\t" in stripped else ","
                header = [c.strip() for c in stripped.split(delimiter)]
                break

            norm_map = {c.lower(): c for c in header}
            pre_col = next((norm_map[c] for c in ["pre_root_id", "pre_pt_root_id", "source", "pre", "bodyid_pre"] if c in norm_map), "pre_root_id")
            post_col = next((norm_map[c] for c in ["post_root_id", "post_pt_root_id", "target", "post", "bodyid_post"] if c in norm_map), "post_root_id")
            weight_col = next((norm_map[c] for c in ["syn_count", "weight", "count", "num_syn", "synapses"] if c in norm_map), "syn_count")
            neuropil_col = next((norm_map[c] for c in ["neuropil", "roi", "region"] if c in norm_map), None)

            reader = csv.DictReader(f, fieldnames=header, delimiter=delimiter)
            for row in reader:
                yield {
                    "pre": row.get(pre_col, "").strip(),
                    "post": row.get(post_col, "").strip(),
                    "weight": row.get(weight_col, "1").strip(),
                    "neuropil": row.get(neuropil_col, "").strip() if (neuropil_col and row.get(neuropil_col)) else None,
                }


def run_pipeline(
    file_path: Path,
    max_records: int = 50000,
    is_software_test: bool = False,
    results_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Run the end-to-end connectivity analysis pipeline.
    """
    start_time = time.perf_counter()

    if results_dir is None:
        project_root = Path(__file__).resolve().parent.parent
        subfolder = "software_test" if is_software_test else "real_data_pilot"
        results_dir = project_root / "results" / subfolder
    results_dir.mkdir(parents=True, exist_ok=True)

    node_to_id: dict[str, int] = {}
    id_to_node: list[str] = []
    edge_weights: dict[int, int] = {}

    neuropil_synapses: Counter[str] = Counter()
    neuropil_connections: Counter[str] = Counter()

    self_connections: list[dict[str, Any]] = []
    duplicate_records_merged = 0
    malformed_rows = 0
    valid_rows_processed = 0
    is_sampled = False

    for record in iter_records(file_path):
        if max_records is not None and max_records >= 0 and valid_rows_processed >= max_records:
            is_sampled = True
            break

        pre = record.get("pre", "").strip()
        post = record.get("post", "").strip()
        weight_raw = record.get("weight", 1)

        if not pre or not post:
            malformed_rows += 1
            continue

        try:
            weight = int(weight_raw)
            if weight <= 0:
                malformed_rows += 1
                continue
        except (ValueError, TypeError):
            malformed_rows += 1
            continue

        valid_rows_processed += 1
        if pre not in node_to_id:
            node_to_id[pre] = len(id_to_node)
            id_to_node.append(pre)
        u = node_to_id[pre]

        if post not in node_to_id:
            node_to_id[post] = len(id_to_node)
            id_to_node.append(post)
        v = node_to_id[post]

        edge_key = (u << 32) | v
        if edge_key in edge_weights:
            duplicate_records_merged += 1
            edge_weights[edge_key] += weight
        else:
            edge_weights[edge_key] = weight

        npil = record.get("neuropil")
        if npil:
            neuropil_synapses[npil] += weight
            neuropil_connections[npil] += 1

        if u == v:
            self_connections.append({"node_id": pre, "syn_count": weight})

    # 2. Graph Metrics Calculation
    N = len(id_to_node)
    total_directed_edges = len(edge_weights)
    out_degrees = [0] * N
    in_degrees = [0] * N
    out_strengths = [0] * N
    in_strengths = [0] * N
    total_weights: list[int] = []

    ds = DisjointSet(N)
    mutual_dyads = 0

    for edge_key, w in edge_weights.items():
        u = edge_key >> 32
        v = edge_key & 0xFFFFFFFF
        total_weights.append(w)
        out_degrees[u] += 1
        in_degrees[v] += 1
        out_strengths[u] += w
        in_strengths[v] += w

        if u != v:
            ds.union(u, v)
            if u < v and ((v << 32) | u) in edge_weights:
                mutual_dyads += 1

    reciprocity_ratio = (2.0 * mutual_dyads / total_directed_edges) if total_directed_edges > 0 else 0.0

    # Connected Components via Disjoint-Set
    comp_counts = Counter(ds.find(i) for i in range(N))
    wcc_sorted = sorted(comp_counts.values(), reverse=True)
    num_components = len(wcc_sorted)
    largest_wcc_size = wcc_sorted[0] if wcc_sorted else 0
    largest_wcc_ratio = (largest_wcc_size / N) if N else 0.0

    # Top Hubs Identification (deterministic secondary sort by string node_id)
    top_out_idx = sorted(range(N), key=lambda i: (-out_degrees[i], id_to_node[i]))[:5]
    top_in_idx = sorted(range(N), key=lambda i: (-in_degrees[i], id_to_node[i]))[:5]
    top_out_str_idx = sorted(range(N), key=lambda i: (-out_strengths[i], id_to_node[i]))[:5]
    top_in_str_idx = sorted(range(N), key=lambda i: (-in_strengths[i], id_to_node[i]))[:5]

    top_out_degree = [(id_to_node[i], out_degrees[i]) for i in top_out_idx]
    top_in_degree = [(id_to_node[i], in_degrees[i]) for i in top_in_idx]
    top_out_strength = [(id_to_node[i], out_strengths[i]) for i in top_out_str_idx]
    top_in_strength = [(id_to_node[i], in_strengths[i]) for i in top_in_str_idx]

    # Distributions
    out_deg_stats = calculate_distribution_stats(out_degrees)
    in_deg_stats = calculate_distribution_stats(in_degrees)
    weight_stats = calculate_distribution_stats(total_weights)

    elapsed_time = time.perf_counter() - start_time
    peak_ram = get_peak_memory_mb()

    # Generate visual artifacts (SVG)
    svg_deg_path = results_dir / "out_degree_distribution.svg"
    svg_weight_path = results_dir / "synapse_weight_distribution.svg"
    generate_svg_histogram(
        out_degrees,
        title=f"Out-Degree Distribution ({'SOFTWARE TEST' if is_software_test else 'Sample'})",
        xlabel="Out-Degree (Postsynaptic Partners)",
        output_path=svg_deg_path,
    )
    generate_svg_histogram(
        total_weights,
        title=f"Synapse Count Distribution ({'SOFTWARE TEST' if is_software_test else 'Sample'})",
        xlabel="Synapse Count per Edge",
        output_path=svg_weight_path,
    )

    summary = {
        "metadata": {
            "is_software_test": is_software_test,
            "file_analyzed": str(file_path.name),
            "is_sampled": is_sampled,
            "max_records_limit": max_records,
            "execution_time_seconds": round(elapsed_time, 4),
            "peak_ram_mb": round(peak_ram, 2),
        },
        "record_validation": {
            "valid_records_processed": valid_rows_processed,
            "malformed_records_excluded": malformed_rows,
            "duplicate_records_aggregated": duplicate_records_merged,
        },
        "network_topology": {
            "total_unique_neurons": N,
            "total_directed_edges": total_directed_edges,
            "total_synapse_count": sum(total_weights),
            "self_connections_count": len(self_connections),
            "mutual_dyads_count": mutual_dyads,
            "reciprocity_ratio": round(reciprocity_ratio, 4),
            "weakly_connected_components_count": num_components,
            "largest_wcc_neuron_count": largest_wcc_size,
            "largest_wcc_coverage_ratio": round(largest_wcc_ratio, 4),
        },
        "degree_and_weight_distributions": {
            "out_degree": out_deg_stats,
            "in_degree": in_deg_stats,
            "edge_synapse_counts": weight_stats,
        },
        "prominent_hubs": {
            "top_out_degree": [{"node_id": nid, "out_degree": deg} for nid, deg in top_out_degree],
            "top_in_degree": [{"node_id": nid, "in_degree": deg} for nid, deg in top_in_degree],
            "top_out_strength": [{"node_id": nid, "out_synapses": st} for nid, st in top_out_strength],
            "top_in_strength": [{"node_id": nid, "in_synapses": st} for nid, st in top_in_strength],
        },
        "regional_breakdown": {
            "neuropils_detected": len(neuropil_synapses),
            "top_neuropils_by_synapses": dict(neuropil_synapses.most_common(10)),
            "top_neuropils_by_connections": dict(neuropil_connections.most_common(10)),
        } if neuropil_synapses else None,
    }

    # Save summary.json
    summary_path = results_dir / "summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run preliminary fly-brain connectivity analysis.")
    parser.add_argument("--file", type=Path, default=None, help="Input CSV/TSV dataset file.")
    parser.add_argument("--max-records", type=int, default=50000, help="Max records to sample (default: 50,000; -1 for unlimited; positive integer for sample size).")
    parser.add_argument("--results-dir", type=Path, default=None, help="Directory to save output results.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    target_file = args.file
    is_software_test = False

    if target_file is None:
        raw_candidates = []
        raw_dir = project_root / "data" / "raw"
        if raw_dir.exists():
            for ext in ("*.feather", "*.csv", "*.tsv", "*.gz"):
                raw_candidates.extend(sorted(raw_dir.rglob(ext)))
        if raw_candidates:
            target_file = raw_candidates[0]
            is_software_test = False
        else:
            target_file = project_root / "data" / "synthetic_connectivity_test.csv"
            is_software_test = True

    if "synthetic" in target_file.name.lower():
        is_software_test = True

    print(f"Running connectivity analysis pipeline on: {target_file}")
    print(f"Status: {'[SOFTWARE TEST]' if is_software_test else '[REAL CONNECTOME EXPERIMENT]'}")

    summary = run_pipeline(
        target_file,
        max_records=args.max_records,
        is_software_test=is_software_test,
        results_dir=args.results_dir,
    )

    print("\n================ PIPELINE EXECUTION SUMMARY ================")
    print(json.dumps(summary, indent=2))
    print("============================================================\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
