#!/usr/bin/env python3
"""
Inspect, validate, and audit connectomics dataset files.

Designed for resource-constrained environments:
- Reads sequentially via streaming (O(1) line memory overhead).
- Supports uncompressed (.csv, .tsv) and gzip-compressed (.gz) files.
- Preserves 64-bit unsigned integers without IEEE 754 precision loss.
- Profiles peak memory consumption via resource.getrusage.
- Accurately distinguishes between software tests and real biological data.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import resource
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Generator, TextIO


def get_peak_memory_mb() -> float:
    """Return peak resident set size in megabytes for the current process."""
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # On Linux, ru_maxrss is reported in kilobytes
    return usage / 1024.0


def open_file_stream(file_path: Path) -> TextIO:
    """Open a plain text or gzip-compressed file in text mode."""
    if file_path.suffix == ".gz":
        return gzip.open(file_path, "rt", encoding="utf-8", errors="replace")
    return file_path.open("r", encoding="utf-8", errors="replace")


def detect_file_delimiter(first_line: str) -> str:
    """Detect delimiter from first non-comment line."""
    if "\t" in first_line:
        return "\t"
    return ","


def classify_dataset_schema(header: list[str]) -> tuple[str, dict[str, str]]:
    """
    Classify the file schema based on recognized connectomics column headers.
    Returns (schema_type, column_mapping).
    """
    norm_headers = {col.strip().lower(): col.strip() for col in header}

    # Possible mappings for source neuron ID
    pre_candidates = ["pre_root_id", "pre_pt_root_id", "source", "pre", "bodyid_pre"]
    # Possible mappings for target neuron ID
    post_candidates = ["post_root_id", "post_pt_root_id", "target", "post", "bodyid_post"]
    # Possible mappings for synapse count / weight
    weight_candidates = ["syn_count", "weight", "count", "num_syn", "synapses"]

    col_map = {}

    for cand in pre_candidates:
        if cand in norm_headers:
            col_map["pre"] = norm_headers[cand]
            break

    for cand in post_candidates:
        if cand in norm_headers:
            col_map["post"] = norm_headers[cand]
            break

    for cand in weight_candidates:
        if cand in norm_headers:
            col_map["weight"] = norm_headers[cand]
            break

    if "pre" in col_map and "post" in col_map:
        if "synapse_id" in norm_headers or "pre_pt_x" in norm_headers:
            schema_type = "individual_synapse_records"
        else:
            schema_type = "aggregated_neuron_connections"
    elif "cell_type" in norm_headers or "super_class" in norm_headers:
        schema_type = "cell_metadata_annotations"
    else:
        schema_type = "unknown_format"

    return schema_type, col_map


def audit_dataset_file(
    file_path: Path,
    max_rows: int = 50000,
    is_software_test: bool = False,
) -> dict[str, Any]:
    """
    Audit a connectivity dataset file with streaming, bounded memory processing.
    """
    start_time = time.perf_counter()
    file_size_bytes = file_path.stat().st_size
    file_size_mb = file_size_bytes / (1024 * 1024)

    total_lines = 0
    comment_lines = 0
    header: list[str] = []
    delimiter = ","
    schema_type = "unknown_format"
    col_map: dict[str, str] = {}

    unique_pre: set[str] = set()
    unique_post: set[str] = set()
    seen_edges: set[tuple[str, str]] = set()

    total_valid_records = 0
    malformed_records = 0
    duplicate_edges = 0
    self_connections = 0

    weight_distribution: Counter[int] = Counter()
    total_synapse_count = 0
    min_weight: int | None = None
    max_weight: int | None = None

    is_sampled = False

    with open_file_stream(file_path) as f:
        # Find first non-comment line as header
        for raw_line in f:
            total_lines += 1
            stripped = raw_line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                comment_lines += 1
                continue
            delimiter = detect_file_delimiter(stripped)
            header = [c.strip() for c in stripped.split(delimiter)]
            break

        if not header:
            return {
                "file_path": str(file_path),
                "error": "Empty or comment-only file",
                "is_software_test": is_software_test,
            }

        schema_type, col_map = classify_dataset_schema(header)

        # Process data rows
        reader = csv.DictReader(f, fieldnames=header, delimiter=delimiter)
        for row in reader:
            total_lines += 1

            if max_rows > 0 and total_valid_records + malformed_records >= max_rows:
                is_sampled = True
                break

            # If aggregated connections, validate endpoints and weights
            if "pre" in col_map and "post" in col_map:
                pre_raw = row.get(col_map["pre"], "").strip()
                post_raw = row.get(col_map["post"], "").strip()

                if not pre_raw or not post_raw:
                    malformed_records += 1
                    continue

                weight_raw = row.get(col_map.get("weight", ""), "1").strip()
                try:
                    weight_val = int(weight_raw)
                    if weight_val <= 0:
                        malformed_records += 1
                        continue
                except (ValueError, TypeError):
                    malformed_records += 1
                    continue

                total_valid_records += 1
                unique_pre.add(pre_raw)
                unique_post.add(post_raw)

                edge_key = (pre_raw, post_raw)
                if edge_key in seen_edges:
                    duplicate_edges += 1
                else:
                    seen_edges.add(edge_key)

                if pre_raw == post_raw:
                    self_connections += 1

                weight_distribution[weight_val] += 1
                total_synapse_count += weight_val
                if min_weight is None or weight_val < min_weight:
                    min_weight = weight_val
                if max_weight is None or weight_val > max_weight:
                    max_weight = weight_val
            else:
                total_valid_records += 1

    elapsed_sec = time.perf_counter() - start_time
    peak_ram_mb = get_peak_memory_mb()

    # Calculate summary weight statistics
    mean_weight = (total_synapse_count / total_valid_records) if total_valid_records > 0 else 0.0

    all_neurons = unique_pre.union(unique_post)

    return {
        "file_name": file_path.name,
        "file_path": str(file_path.resolve()),
        "file_size_mb": round(file_size_mb, 4),
        "is_software_test": is_software_test,
        "schema_type": schema_type,
        "detected_columns": header,
        "mapped_columns": col_map,
        "is_sampled": is_sampled,
        "max_rows_limit": max_rows,
        "total_lines_read": total_lines,
        "comment_lines": comment_lines,
        "valid_records": total_valid_records,
        "malformed_records": malformed_records,
        "duplicate_edges": duplicate_edges,
        "self_connections": self_connections,
        "unique_source_neurons": len(unique_pre),
        "unique_target_neurons": len(unique_post),
        "total_unique_neurons": len(all_neurons),
        "total_synapse_count": total_synapse_count,
        "min_synapse_count": min_weight,
        "max_synapse_count": max_weight,
        "mean_synapse_count": round(mean_weight, 2),
        "top_weight_frequencies": dict(weight_distribution.most_common(5)),
        "execution_time_seconds": round(elapsed_sec, 4),
        "peak_ram_mb": round(peak_ram_mb, 2),
    }


def format_audit_report(audit: dict[str, Any]) -> str:
    """Format audit results into readable output."""
    tag = "[SOFTWARE TEST]" if audit.get("is_software_test") else "[REAL DATA AUDIT]"
    lines = [
        "============================================================",
        f"DATASET AUDIT REPORT {tag}",
        "============================================================",
        f"File:            {audit.get('file_name')} ({audit.get('file_size_mb')} MB)",
        f"Classification:  {audit.get('schema_type')}",
        f"Columns:         {audit.get('detected_columns')}",
        f"Column Mapping:  {audit.get('mapped_columns')}",
        f"Sampled Mode:    {audit.get('is_sampled')} (Row limit: {audit.get('max_rows_limit')})",
        "",
        "RECORD INTEGRITY & VALIDATION:",
        f"  Total Valid Records:    {audit.get('valid_records')}",
        f"  Malformed / Skipped:    {audit.get('malformed_records')}",
        f"  Duplicate Edge Pairs:   {audit.get('duplicate_edges')}",
        f"  Self-Loops (Autapses):  {audit.get('self_connections')}",
        "",
        "CONNECTIVITY PROPERTIES:",
        f"  Unique Source Neurons:  {audit.get('unique_source_neurons')}",
        f"  Unique Target Neurons:  {audit.get('unique_target_neurons')}",
        f"  Total Unique Neurons:   {audit.get('total_unique_neurons')}",
        f"  Aggregated Synapses:    {audit.get('total_synapse_count')}",
        f"  Min Synapse Count:      {audit.get('min_synapse_count')}",
        f"  Max Synapse Count:      {audit.get('max_synapse_count')}",
        f"  Mean Synapse Count:     {audit.get('mean_synapse_count')}",
        f"  Top Weight Frequencies: {audit.get('top_weight_frequencies')}",
        "",
        "PERFORMANCE ON DELL INSPIRON 5558:",
        f"  Execution Time:         {audit.get('execution_time_seconds')} s",
        f"  Peak Resident Memory:   {audit.get('peak_ram_mb')} MB",
        "============================================================",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit connectome dataset files.")
    parser.add_argument(
        "--file",
        type=Path,
        default=None,
        help="Path to dataset file to audit (defaults to synthetic test file).",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=50000,
        help="Maximum records to process (default: 50,000; 0 for unlimited).",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Optional path to write audit summary as JSON.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent

    target_file = args.file
    is_software_test = False

    if target_file is None:
        # Check if real data exists in data/raw
        raw_candidates = list((project_root / "data" / "raw").glob("*.csv")) if (project_root / "data" / "raw").exists() else []
        if raw_candidates:
            target_file = raw_candidates[0]
            is_software_test = False
        else:
            target_file = project_root / "data" / "synthetic_connectivity_test.csv"
            is_software_test = True

    if not target_file.exists():
        print(f"Error: Target file {target_file} does not exist.", file=sys.stderr)
        return 1

    if "synthetic" in target_file.name.lower():
        is_software_test = True

    audit = audit_dataset_file(target_file, max_rows=args.max_rows, is_software_test=is_software_test)
    print(format_audit_report(audit))

    if args.json_out:
        with args.json_out.open("w", encoding="utf-8") as f:
            json.dump(audit, f, indent=2)
        print(f"Audit JSON saved to: {args.json_out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
