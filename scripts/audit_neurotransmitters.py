#!/usr/bin/env python3
"""
Comprehensive Whole-Brain Neurotransmitter Prediction Audit.

Addresses Phase Four of the Research Protocol:
1. Streams all 16,847,997 records of proofread_connections_783.feather.
2. Evaluates the deep-learning predicted neurotransmitter fields:
   ach_avg, gaba_avg, glut_avg, da_avg, oct_avg, ser_avg.
3. Computes exact synapse-count-weighted probability mass:
   M_k = sum(syn_count_i * probability_{i,k}).
4. Evaluates missingness:
   - Records with missing probabilities per class.
   - Synapses affected by missing data.
   - Complete vs incomplete case analysis.
5. Compares explicit denominator formulations:
   - Formulation 1: Class-specific valid synapse denominator (reproduces preliminary numbers).
   - Formulation 2: Total connectome synapse denominator (54,492,922).
   - Formulation 3: Normalized over total predicted mass sum(M_k).
   - Formulation 4: Complete-case filtered analysis.
6. Evaluates row-level probability sum constraints (sum_k P_{i,k} approx 1.0).
7. Computes regional neurotransmitter compositions across all 79 neuropils.
8. Saves results to results/real_data_pilot/neurotransmitter_audit.json and verified_neurotransmitter_summary.json.
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_PATH = PROJECT_ROOT / ".venv" / "lib" / "python3.12" / "site-packages"
if VENV_PATH.exists():
    sys.path.insert(0, str(VENV_PATH))

import pyarrow.ipc as ipc


def get_peak_memory_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


NT_CLASSES = ["ach", "gaba", "glut", "da", "oct", "ser"]
COL_NAMES = {
    "ach": "ach_avg",
    "gaba": "gaba_avg",
    "glut": "glut_avg",
    "da": "da_avg",
    "oct": "oct_avg",
    "ser": "ser_avg",
}


def audit_neurotransmitters(
    file_path: Path,
    output_audit_json: Path | None = None,
    output_summary_json: Path | None = None,
) -> dict[str, Any]:
    start_time = time.perf_counter()
    if output_audit_json is None:
        output_audit_json = PROJECT_ROOT / "results" / "real_data_pilot" / "neurotransmitter_audit.json"
    if output_summary_json is None:
        output_summary_json = PROJECT_ROOT / "results" / "real_data_pilot" / "verified_neurotransmitter_summary.json"

    output_audit_json.parent.mkdir(parents=True, exist_ok=True)

    print("================================================================================")
    print("PHASE FOUR: WHOLE-BRAIN NEUROTRANSMITTER PREDICTION AUDIT")
    print(f"Dataset: {file_path.name} (16,847,997 records)")
    print("================================================================================\n")

    total_records = 0
    total_synapses = 0

    # Missingness tracking
    missing_records_per_class: Counter[str] = Counter()
    missing_synapses_per_class: Counter[str] = Counter()
    records_with_any_missing = 0
    synapses_with_any_missing = 0

    # Probability mass accumulation
    # All valid records per class
    weighted_mass_all: Counter[str] = Counter()
    valid_synapses_per_class: Counter[str] = Counter()
    valid_records_per_class: Counter[str] = Counter()

    # Complete-case records only
    complete_case_records = 0
    complete_case_synapses = 0
    complete_case_mass: Counter[str] = Counter()

    # Row sum checks on sample
    row_sum_errors = 0
    row_sum_diffs: list[float] = []

    # Regional neuropil tracking
    neuropil_synapses: Counter[str] = Counter()
    neuropil_mass: dict[str, Counter[str]] = defaultdict(Counter)

    with open(file_path, "rb") as f:
        reader = ipc.open_file(f)
        num_batches = reader.num_record_batches

        for b_idx in range(num_batches):
            batch = reader.get_batch(b_idx)
            syn_counts = batch.column("syn_count").to_pylist()
            neuropils = batch.column("neuropil").to_pylist() if "neuropil" in batch.schema.names else [None] * len(syn_counts)

            # Extract class probability vectors
            probs = {nt: batch.column(COL_NAMES[nt]).to_pylist() for nt in NT_CLASSES}

            batch_len = len(syn_counts)
            for i in range(batch_len):
                w = syn_counts[i]
                if w is None or w <= 0:
                    continue

                total_records += 1
                total_synapses += w

                npil = neuropils[i]
                if npil:
                    neuropil_synapses[npil] += w

                # Check missingness for this record
                row_probs = {}
                has_missing = False
                for nt in NT_CLASSES:
                    val = probs[nt][i]
                    if val is None:
                        missing_records_per_class[nt] += 1
                        missing_synapses_per_class[nt] += w
                        has_missing = True
                    else:
                        row_probs[nt] = val
                        weighted_mass_all[nt] += val * w
                        valid_synapses_per_class[nt] += w
                        valid_records_per_class[nt] += 1
                        if npil:
                            neuropil_mass[npil][nt] += val * w

                if has_missing:
                    records_with_any_missing += 1
                    synapses_with_any_missing += w
                else:
                    complete_case_records += 1
                    complete_case_synapses += w
                    for nt, val in row_probs.items():
                        complete_case_mass[nt] += val * w

                    # Check row probability sum
                    if len(row_sum_diffs) < 100000:
                        r_sum = sum(row_probs.values())
                        row_sum_diffs.append(r_sum)
                        if abs(r_sum - 1.0) > 0.05:
                            row_sum_errors += 1

            if (b_idx + 1) % 50 == 0 or (b_idx + 1) == num_batches:
                elapsed = time.perf_counter() - start_time
                print(f"  Processed {b_idx + 1}/{num_batches} batches ({total_records:,} rows) in {elapsed:.1f}s...")

    elapsed_time = time.perf_counter() - start_time
    peak_ram = get_peak_memory_mb()

    # Formulations
    # Formulation 1: Class-specific valid synapse denominator (Preliminary Run Method)
    formulation_1 = {}
    for nt in NT_CLASSES:
        denom = valid_synapses_per_class[nt]
        pct = (weighted_mass_all[nt] / denom * 100.0) if denom > 0 else 0.0
        formulation_1[nt] = round(pct, 2)

    # Formulation 2: Total connectome synapse denominator (54,492,922)
    formulation_2 = {}
    for nt in NT_CLASSES:
        pct = (weighted_mass_all[nt] / total_synapses * 100.0) if total_synapses > 0 else 0.0
        formulation_2[nt] = round(pct, 2)

    # Formulation 3: Normalized over sum of probability mass
    total_mass_sum = sum(weighted_mass_all.values())
    formulation_3 = {}
    for nt in NT_CLASSES:
        pct = (weighted_mass_all[nt] / total_mass_sum * 100.0) if total_mass_sum > 0 else 0.0
        formulation_3[nt] = round(pct, 2)

    # Formulation 4: Complete cases only
    complete_mass_sum = sum(complete_case_mass.values())
    formulation_4 = {}
    for nt in NT_CLASSES:
        pct = (complete_case_mass[nt] / complete_mass_sum * 100.0) if complete_mass_sum > 0 else 0.0
        formulation_4[nt] = round(pct, 2)

    # Row sum statistics on sample
    mean_row_sum = (sum(row_sum_diffs) / len(row_sum_diffs)) if row_sum_diffs else 0.0
    min_row_sum = min(row_sum_diffs) if row_sum_diffs else 0.0
    max_row_sum = max(row_sum_diffs) if row_sum_diffs else 0.0

    # Regional analysis summary
    regional_transmitter_summary = {}
    for npil, syn_count in neuropil_synapses.most_common():
        n_masses = neuropil_mass[npil]
        npil_mass_sum = sum(n_masses.values())
        if npil_mass_sum > 0:
            regional_transmitter_summary[npil] = {
                "total_synapses": syn_count,
                "dominant_transmitter": n_masses.most_common(1)[0][0] if n_masses else "none",
                "ach_pct": round(n_masses["ach"] / npil_mass_sum * 100.0, 2),
                "gaba_pct": round(n_masses["gaba"] / npil_mass_sum * 100.0, 2),
                "glut_pct": round(n_masses["glut"] / npil_mass_sum * 100.0, 2),
                "da_pct": round(n_masses["da"] / npil_mass_sum * 100.0, 2),
                "oct_pct": round(n_masses["oct"] / npil_mass_sum * 100.0, 2),
                "ser_pct": round(n_masses["ser"] / npil_mass_sum * 100.0, 2),
            }

    # Compile Comprehensive Audit Report
    audit_report = {
        "metadata": {
            "execution_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dataset_file": file_path.name,
            "dataset_version": "FlyWire FAFB v783.0",
            "runtime_seconds": round(elapsed_time, 2),
            "peak_ram_mb": round(peak_ram, 1),
            "total_records_processed": total_records,
            "total_synapses_processed": total_synapses,
        },
        "missingness_analysis": {
            "records_with_any_missing_probability": records_with_any_missing,
            "records_missing_fraction_pct": round(records_with_any_missing / total_records * 100.0, 4),
            "synapses_affected_by_missing_data": synapses_with_any_missing,
            "synapses_missing_fraction_pct": round(synapses_with_any_missing / total_synapses * 100.0, 4),
            "complete_case_records": complete_case_records,
            "complete_case_synapses": complete_case_synapses,
            "per_class_missing_records": dict(missing_records_per_class),
            "per_class_missing_synapses": dict(missing_synapses_per_class),
        },
        "row_probability_sum_check": {
            "sample_size_evaluated": len(row_sum_diffs),
            "mean_row_probability_sum": round(mean_row_sum, 4),
            "min_row_probability_sum": round(min_row_sum, 4),
            "max_row_probability_sum": round(max_row_sum, 4),
            "records_deviating_from_unity_gt_5pct": row_sum_errors,
        },
        "probability_mass_raw": {nt: round(weighted_mass_all[nt], 2) for nt in NT_CLASSES},
        "comparative_denominators": {
            "formulation_1_class_specific_valid_synapses_pct": formulation_1,
            "formulation_2_total_connectome_synapses_pct": formulation_2,
            "formulation_3_normalized_over_mass_sum_pct": formulation_3,
            "formulation_4_complete_cases_only_pct": formulation_4,
        },
        "neuropil_regional_transmitter_breakdown": regional_transmitter_summary,
    }

    with output_audit_json.open("w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=2)

    # Simplified summary output for verified reporting
    verified_summary = {
        "metadata": {
            "dataset": file_path.name,
            "scope": "COMPLETE CONNECTOME (16,847,997 records, 54,492,922 synapses)",
            "primary_model": "Eckstein, Bates et al. 2024 Cell deep learning EM predictions",
            "interpretation_warning": "Predicted probabilities, NOT direct biochemical concentrations or physiological conductance",
        },
        "whole_brain_proportions_normalized_pct": formulation_3,
        "whole_brain_proportions_class_specific_pct": formulation_1,
        "complete_case_proportions_pct": formulation_4,
        "raw_probability_mass": {nt: round(weighted_mass_all[nt], 1) for nt in NT_CLASSES},
        "missing_data_fraction_pct": round(synapses_with_any_missing / total_synapses * 100.0, 4),
    }

    with output_summary_json.open("w", encoding="utf-8") as f:
        json.dump(verified_summary, f, indent=2)

    print(f"\nAudit complete in {elapsed_time:.2f}s (Peak RAM: {peak_ram:.1f} MB).")
    print("\n--- COMPARATIVE NEUROTRANSMITTER PERCENTAGES ---")
    print(f"{'Class':10s} | {'Form 1 (Class Valid)':20s} | {'Form 2 (Total Syn)':20s} | {'Form 3 (Norm Mass)':20s} | {'Form 4 (Complete)':20s}")
    print("-" * 100)
    for nt in NT_CLASSES:
        print(f"{nt:10s} | {formulation_1[nt]:18.2f}% | {formulation_2[nt]:18.2f}% | {formulation_3[nt]:18.2f}% | {formulation_4[nt]:18.2f}%")
    print("=" * 100)
    print(f"Missing data affects: {synapses_with_any_missing:,} / {total_synapses:,} synapses ({audit_report['missingness_analysis']['synapses_missing_fraction_pct']}%)")
    print(f"Mean record probability sum: {mean_row_sum:.4f}")
    print(f"Saved full audit to:    {output_audit_json}")
    print(f"Saved verified summary to: {output_summary_json}\n")

    return audit_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run whole-brain neurotransmitter prediction audit.")
    parser.add_argument("--file", type=Path, default=PROJECT_ROOT / "data" / "raw" / "fafb_v783" / "proofread_connections_783.feather")
    args = parser.parse_args()

    audit_neurotransmitters(args.file)
    return 0


if __name__ == "__main__":
    sys.exit(main())

