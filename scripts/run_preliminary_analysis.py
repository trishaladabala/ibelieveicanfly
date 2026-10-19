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
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, TextIO


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
        results_dir = file_path.resolve().parent.parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    # 1. Basic Ingestion and Adjacency Construction
    # Directed sparse adjacency: out_edges[pre][post] = syn_count
    out_edges: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    # Pre-calculated in-edges for rapid degree and strength retrieval: in_edges[post][pre] = syn_count
    in_edges: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    # Undirected neighbor mapping for connected component analysis
    adj_undirected: dict[str, set[str]] = defaultdict(set)

    all_nodes: set[str] = set()
    self_connections: list[dict[str, Any]] = []
    duplicate_records_merged = 0
    malformed_rows = 0
    valid_rows_processed = 0
    is_sampled = False

    header: list[str] = []
    delimiter = ","
    pre_col = "pre_root_id"
    post_col = "post_root_id"
    weight_col = "syn_count"

    with open_file_stream(file_path) as f:
        # Detect header
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            delimiter = "\t" if "\t" in stripped else ","
            header = [c.strip() for c in stripped.split(delimiter)]
            break

        # Map column positions
        norm_map = {c.lower(): c for c in header}
        for cand in ["pre_root_id", "pre_pt_root_id", "source", "pre"]:
            if cand in norm_map:
                pre_col = norm_map[cand]
                break
        for cand in ["post_root_id", "post_pt_root_id", "target", "post"]:
            if cand in norm_map:
                post_col = norm_map[cand]
                break
        for cand in ["syn_count", "weight", "count", "num_syn"]:
            if cand in norm_map:
                weight_col = norm_map[cand]
                break

        reader = csv.DictReader(f, fieldnames=header, delimiter=delimiter)
        for row in reader:
            if max_records > 0 and valid_rows_processed >= max_records:
                is_sampled = True
                break

            pre = row.get(pre_col, "").strip()
            post = row.get(post_col, "").strip()
            weight_str = row.get(weight_col, "1").strip()

            if not pre or not post:
                malformed_rows += 1
                continue

            try:
                weight = int(weight_str)
                if weight <= 0:
                    malformed_rows += 1
                    continue
            except (ValueError, TypeError):
                malformed_rows += 1
                continue

            valid_rows_processed += 1
            all_nodes.add(pre)
            all_nodes.add(post)

            # Check if this edge was already seen in the stream
            if post in out_edges[pre]:
                duplicate_records_merged += 1

            out_edges[pre][post] += weight
            in_edges[post][pre] += weight

            if pre == post:
                self_connections.append({"node_id": pre, "syn_count": weight})
            else:
                adj_undirected[pre].add(post)
                adj_undirected[post].add(pre)

    # 2. Graph Metrics Calculation
    total_directed_edges = sum(len(targets) for targets in out_edges.values())

    out_degrees = {node: len(out_edges.get(node, {})) for node in all_nodes}
    in_degrees = {node: len(in_edges.get(node, {})) for node in all_nodes}
    out_strengths = {node: sum(out_edges.get(node, {}).values()) for node in all_nodes}
    in_strengths = {node: sum(in_edges.get(node, {}).values()) for node in all_nodes}

    # Reciprocity calculation: count mutual dyads (u -> v and v -> u where u != v)
    mutual_dyads = 0
    total_weights: list[int] = []
    for u, targets in out_edges.items():
        for v, w in targets.items():
            total_weights.append(w)
            if u < v and v in out_edges and u in out_edges[v]:
                mutual_dyads += 1

    reciprocity_ratio = (2.0 * mutual_dyads / total_directed_edges) if total_directed_edges > 0 else 0.0

    # Connected Components
    components = find_weakly_connected_components(all_nodes, adj_undirected)
    num_components = len(components)
    largest_wcc_size = len(components[0]) if components else 0
    largest_wcc_ratio = (largest_wcc_size / len(all_nodes)) if all_nodes else 0.0

    # Top Hubs Identification
    top_out_degree = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
    top_in_degree = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
    top_out_strength = sorted(out_strengths.items(), key=lambda x: x[1], reverse=True)[:5]
    top_in_strength = sorted(in_strengths.items(), key=lambda x: x[1], reverse=True)[:5]

    # Distributions
    out_deg_stats = calculate_distribution_stats(list(out_degrees.values()))
    in_deg_stats = calculate_distribution_stats(list(in_degrees.values()))
    weight_stats = calculate_distribution_stats(total_weights)

    elapsed_time = time.perf_counter() - start_time
    peak_ram = get_peak_memory_mb()

    # Generate visual artifacts (SVG)
    svg_deg_path = results_dir / "out_degree_distribution.svg"
    svg_weight_path = results_dir / "synapse_weight_distribution.svg"
    generate_svg_histogram(
        list(out_degrees.values()),
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
            "total_unique_neurons": len(all_nodes),
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
    }

    # Save summary.json
    summary_path = results_dir / "summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run preliminary fly-brain connectivity analysis.")
    parser.add_argument("--file", type=Path, default=None, help="Input CSV/TSV dataset file.")
    parser.add_argument("--max-records", type=int, default=50000, help="Max records to sample (0 for unlimited).")
    parser.add_argument("--results-dir", type=Path, default=None, help="Directory to save output results.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    target_file = args.file
    is_software_test = False

    if target_file is None:
        raw_candidates = list((project_root / "data" / "raw").glob("*.csv")) if (project_root / "data" / "raw").exists() else []
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
